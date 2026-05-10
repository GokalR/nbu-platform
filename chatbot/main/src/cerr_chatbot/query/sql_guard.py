"""Conservative SQL validator for chatbot-generated read-only SELECTs.

Hard rules:
- exactly one statement
- statement must be SELECT (or WITH ... SELECT)
- only semantic v_* views may appear as table sources
- raw tables, system catalogs, unknown identifiers are rejected
- SELECT * is rejected
- SQL comments are rejected
- LIMIT enforced: append `LIMIT 100` when absent; reject when > 500

We use sqlglot to parse the SQL into an AST. Regex-only validators are easy
to bypass; an AST walk catches most evasions deterministically.

Returns a `ValidatedSql` with the (possibly LIMIT-adjusted) SQL ready for
execution. Raises `SqlGuardError` on rejection.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from sqlglot import exp, parse, parse_one

from cerr_chatbot.query.semantic_catalog import SEMANTIC_CATALOG

DEFAULT_LIMIT = 100
MAX_LIMIT = 500
MAX_JOINS = 4
ALLOWED_VIEWS: frozenset[str] = frozenset(SEMANTIC_CATALOG.keys())

# Allowlist of SQL functions. Class names match sqlglot's exp.* node types
# for builtin aggregates. Anonymous (named) functions are rejected wholesale,
# which excludes pg_sleep, random, load_extension, sqlite_version,
# current_setting, current_user, etc.
ALLOWED_FUNCTION_TYPES: frozenset[str] = frozenset(
    {"Count", "Sum", "Avg", "Min", "Max", "Round", "Cast"}
)

# Surrogate ids are the only columns the chatbot may join on.
SURROGATE_JOIN_KEYS: frozenset[str] = frozenset({"region_id", "district_id", "mahalla_id"})

# Per-view allowlist of column names from the semantic catalog.
ALLOWED_VIEW_COLUMNS: dict[str, frozenset[str]] = {
    name: frozenset(c.name for c in view.columns) for name, view in SEMANTIC_CATALOG.items()
}

# We parse with sqlglot's generic dialect (works for both Postgres and SQLite
# semantic-view DDL we emit). Default reads + writes share the same parser.
_DIALECT = None


class SqlGuardError(ValueError):
    """SQL rejected by the safety guard."""


@dataclass(frozen=True)
class ValidatedSql:
    validated_sql: str
    referenced_views: tuple[str, ...]
    limit_appended: bool


_COMMENT_RE = re.compile(r"--|/\*|\*/")


def validate(sql: str) -> ValidatedSql:
    if not isinstance(sql, str) or not sql.strip():
        raise SqlGuardError("empty SQL")

    if _COMMENT_RE.search(sql):
        raise SqlGuardError("SQL comments are not allowed")

    # Reject more than one statement. parse() returns a list; trailing
    # whitespace / a single optional semicolon is fine because sqlglot returns
    # a single Expression for "SELECT 1;".
    try:
        statements = parse(sql, dialect=_DIALECT)
    except Exception as exc:  # noqa: BLE001 - sqlglot raises generic
        raise SqlGuardError(f"unable to parse SQL: {exc}") from exc

    statements = [s for s in statements if s is not None]
    if not statements:
        raise SqlGuardError("no parseable statement")
    if len(statements) > 1:
        raise SqlGuardError("only one statement allowed")

    tree = statements[0]
    # WITH..SELECT parses as exp.Select with the `with` arg populated, so a
    # single isinstance check is enough. Anything else (Insert, Update, Delete,
    # Create, Drop, Alter, Pragma, Command, etc.) is rejected.
    if not isinstance(tree, exp.Select):
        raise SqlGuardError(f"only SELECT statements allowed (got {type(tree).__name__})")
    select_node: exp.Select = tree

    # Recursive CTE rejected (loop-friendly, expensive, not needed for
    # chatbot read paths).
    with_clause = select_node.args.get("with")
    if with_clause is not None and with_clause.args.get("recursive"):
        raise SqlGuardError("RECURSIVE CTEs are not allowed")

    # JOIN safety: cap count, reject CROSS JOIN and ON-less / comma joins,
    # require surrogate-id-only join keys.
    joins = list(select_node.find_all(exp.Join))
    if len(joins) > MAX_JOINS:
        raise SqlGuardError(f"too many JOINs ({len(joins)} > {MAX_JOINS})")
    for join in joins:
        kind = (join.args.get("kind") or "").upper()
        if kind == "CROSS":
            raise SqlGuardError("CROSS JOIN is not allowed")
        on = join.args.get("on")
        using = join.args.get("using")
        if on is None and using is None:
            raise SqlGuardError("JOIN must have explicit ON or USING (no comma joins)")
        if using is not None:
            for ident in using:
                col_name = ident.name if hasattr(ident, "name") else str(ident)
                if col_name not in SURROGATE_JOIN_KEYS:
                    raise SqlGuardError(
                        f"USING column not allowed: {col_name} (only surrogate ids: "
                        + ", ".join(sorted(SURROGATE_JOIN_KEYS))
                        + ")"
                    )
        if on is not None:
            _validate_join_on(on)

    # Window functions rejected (before function allowlist so the error
    # message stays meaningful even for window-aggregate combos).
    if next(select_node.find_all(exp.Window), None) is not None:
        raise SqlGuardError("window functions are not allowed")

    # Function allowlist. Reject named/Anonymous functions and any unknown
    # builtin not in ALLOWED_FUNCTION_TYPES. COUNT/SUM/AVG/MIN/MAX/ROUND only.
    # Skip operator nodes (And/Or/EQ/GT/etc.) which subclass exp.Func too.
    for func in select_node.find_all(exp.Func):
        if isinstance(func, (exp.Binary, exp.Connector, exp.Predicate, exp.Unary, exp.Paren)):
            continue
        type_name = type(func).__name__
        if type_name == "Anonymous":
            raw_name = func.this if isinstance(func.this, str) else type_name
            raise SqlGuardError(f"function not allowed: {raw_name}")
        if type_name not in ALLOWED_FUNCTION_TYPES:
            raise SqlGuardError(f"function not allowed: {type_name}")

    # SELECT * (anywhere in the tree) is rejected. This covers the top-level
    # projection, CTE projections, and subquery projections.
    for star in select_node.find_all(exp.Star):
        # COUNT(*) parses as a Star inside a Count function -> allow.
        parent = star.parent
        if isinstance(parent, exp.Count):
            continue
        raise SqlGuardError("SELECT * is not allowed; list columns explicitly")

    # Collect all table sources reached via FROM/JOIN/CTE references.
    referenced: list[str] = []
    forbidden: list[str] = []
    for table in select_node.find_all(exp.Table):
        # Skip CTE self-references: sqlglot emits Table nodes for each CTE
        # alias used in the body. The CTE definitions themselves live as
        # exp.CTE wrappers; the actual underlying tables are the Table nodes
        # _inside_ each CTE definition. Detect CTE alias references and skip.
        cte_names = _cte_names(select_node)
        if table.name in cte_names and not table.db:
            continue
        # Schema-qualified or system tables are out of scope here.
        if table.db:
            forbidden.append(f"{table.db}.{table.name}")
            continue
        if table.name not in ALLOWED_VIEWS:
            forbidden.append(table.name)
            continue
        referenced.append(table.name)

    if forbidden:
        raise SqlGuardError(
            "table/view not in allowed semantic catalog: " + ", ".join(sorted(set(forbidden)))
        )
    if not referenced:
        raise SqlGuardError("query references no allowed view")

    # Build alias -> view map for the now-validated allowed tables only, and
    # validate every Column against the catalog. Each scope is validated
    # independently so a CTE body's tables don't pollute outer alias resolution.
    cte_columns = _cte_column_map(select_node)
    _validate_scope(select_node, cte_columns, outer=True)
    with_clause = select_node.args.get("with")
    if with_clause is not None:
        for cte in with_clause.expressions:
            inner = cte.this
            if isinstance(inner, exp.Select):
                _validate_scope(inner, cte_columns, outer=False)

    # LIMIT handling. Walk top-level statement only (subquery limits are fine).
    limit_node = select_node.args.get("limit")
    limit_appended = False
    if limit_node is None:
        select_node.set("limit", exp.Limit(expression=exp.Literal.number(DEFAULT_LIMIT)))
        limit_appended = True
    else:
        n = _limit_value(limit_node)
        if n is None:
            raise SqlGuardError("LIMIT must be a positive integer literal")
        if n > MAX_LIMIT:
            raise SqlGuardError(f"LIMIT {n} exceeds max {MAX_LIMIT}")
        if n <= 0:
            raise SqlGuardError("LIMIT must be > 0")

    rendered = select_node.sql(dialect=_DIALECT)
    return ValidatedSql(
        validated_sql=rendered,
        referenced_views=tuple(sorted(set(referenced))),
        limit_appended=limit_appended,
    )


def _validate_scope(
    select_node: exp.Select,
    cte_columns: dict[str, frozenset[str]],
    *,
    outer: bool,
) -> None:
    """Validate every Column reachable from this scope but not nested in a CTE
    body of its own. CTE column exports are visible only when `outer=True`.
    """
    cte_aliases_visible = set(cte_columns.keys()) if outer else set()
    # Per-alias allowed-column set for this scope. CTE alias maps to its
    # exports; view alias maps to its catalog columns.
    alias_to_columns: dict[str, frozenset[str]] = {}
    alias_to_view_label: dict[str, str] = {}
    for table in select_node.find_all(exp.Table):
        if outer and _is_inside_cte_body_below(table, select_node):
            continue
        alias = table.alias or table.name
        if table.name in cte_aliases_visible and not table.db:
            alias_to_columns[alias] = cte_columns[table.name]
            alias_to_view_label[alias] = table.name
            continue
        alias_to_columns[alias] = ALLOWED_VIEW_COLUMNS.get(table.name, frozenset())
        alias_to_view_label[alias] = table.name

    select_aliases = {a.alias for a in select_node.expressions if isinstance(a, exp.Alias)}

    for col in select_node.find_all(exp.Column):
        if outer and _is_inside_cte_body_below(col, select_node):
            continue
        qualifier = col.table
        name = col.name
        if qualifier:
            allowed = alias_to_columns.get(qualifier)
            if allowed is None:
                raise SqlGuardError(f"unknown table alias: {qualifier}.{name}")
            if name not in allowed:
                src = alias_to_view_label.get(qualifier, qualifier)
                if qualifier in cte_aliases_visible:
                    raise SqlGuardError(
                        f"unknown CTE column: {src}.{name} (exported: {sorted(allowed) or '[]'})"
                    )
                raise SqlGuardError(f"unknown column: {src}.{name}")
            continue
        if name in select_aliases:
            continue
        if len(alias_to_columns) == 1:
            sole_alias = next(iter(alias_to_columns))
            allowed = alias_to_columns[sole_alias]
            if name in allowed:
                continue
            src = alias_to_view_label.get(sole_alias, sole_alias)
            raise SqlGuardError(f"unknown column: {src}.{name}")
        raise SqlGuardError(
            f"unqualified column in multi-view query: {name} (qualify with table alias)"
        )


def _is_inside_cte_body_below(node: exp.Expression, root: exp.Expression) -> bool:
    """True when `node` lives inside an exp.CTE between itself and `root`."""
    parent = node.parent
    while parent is not None and parent is not root:
        if isinstance(parent, exp.CTE):
            return True
        parent = parent.parent
    return False


def _cte_column_map(select_node: exp.Select) -> dict[str, frozenset[str]]:
    """Map each CTE alias to its exported column names.

    Source order:
    1. Explicit `WITH x(a, b) AS (...)` column list, if present.
    2. Otherwise, `alias_or_name` of each projection in the inner SELECT.
    """
    out: dict[str, frozenset[str]] = {}
    with_clause = select_node.args.get("with")
    if with_clause is None:
        return out
    for cte in with_clause.expressions:
        cte_name = cte.alias_or_name
        alias_obj = cte.args.get("alias")
        explicit_cols: list[str] = []
        if alias_obj is not None and alias_obj.columns:
            explicit_cols = [c.name for c in alias_obj.columns]

        if explicit_cols:
            cols = explicit_cols
        else:
            inner = cte.this
            cols = []
            if isinstance(inner, exp.Select):
                for proj in inner.expressions:
                    name = proj.alias_or_name
                    if name:
                        cols.append(name)

        if len(cols) != len(set(cols)):
            seen: set[str] = set()
            dups = [c for c in cols if c in seen or seen.add(c)]  # type: ignore[func-returns-value]
            raise SqlGuardError(
                f"CTE {cte_name} exports duplicate column names: {sorted(set(dups))}"
            )
        out[cte_name] = frozenset(cols)
    return out


def _validate_join_on(on: exp.Expression) -> None:
    """ON clause must be EQ(s) of allowed surrogate columns, AND-chained."""
    for eq in _flatten_and(on):
        if not isinstance(eq, exp.EQ):
            raise SqlGuardError(
                "JOIN ON must be equality of surrogate id columns (AND of equalities allowed)"
            )
        left, right = eq.this, eq.expression
        if not (isinstance(left, exp.Column) and isinstance(right, exp.Column)):
            raise SqlGuardError(
                "JOIN ON predicates must compare two columns, no literals/expressions"
            )
        if left.name not in SURROGATE_JOIN_KEYS or right.name not in SURROGATE_JOIN_KEYS:
            raise SqlGuardError(
                f"JOIN ON column not allowed: {left.name} = {right.name} "
                "(only surrogate ids: " + ", ".join(sorted(SURROGATE_JOIN_KEYS)) + ")"
            )


def _flatten_and(expr: exp.Expression) -> list[exp.Expression]:
    if isinstance(expr, exp.And):
        return _flatten_and(expr.this) + _flatten_and(expr.expression)
    if isinstance(expr, exp.Paren):
        return _flatten_and(expr.this)
    return [expr]


def _cte_names(select_node: exp.Select) -> set[str]:
    with_clause = select_node.args.get("with")
    if with_clause is None:
        return set()
    return {cte.alias_or_name for cte in with_clause.expressions}


def _limit_value(limit_node: exp.Limit) -> int | None:
    expr = limit_node.expression
    if isinstance(expr, exp.Literal) and expr.is_int:
        try:
            return int(expr.this)
        except (TypeError, ValueError):
            return None
    return None


# Re-export parse_one purely so tests can introspect the AST if helpful.
__all__ = [
    "ALLOWED_VIEWS",
    "DEFAULT_LIMIT",
    "MAX_LIMIT",
    "SqlGuardError",
    "ValidatedSql",
    "parse_one",
    "validate",
]
