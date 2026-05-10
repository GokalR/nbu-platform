"""Recursive JSON walker.

Emits canonical paths using `[]` notation for arrays.
Aggregates per-path: presence count, null count, observed type set, capped examples.

Geo subtrees are intentionally pruned - geometries are huge and never become
SQL columns; the geometry blob will be stored verbatim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Path suffixes whose subtrees we do NOT recurse into. The path itself is
# still recorded; only its children are skipped.
PRUNE_SUFFIXES: tuple[str, ...] = (".geo", ".region_geo")

EXAMPLE_CAP = 3
EXAMPLE_STR_CAP = 80


@dataclass
class _PathStats:
    presence: int = 0
    null: int = 0
    types: set[str] = field(default_factory=set)
    examples: list[Any] = field(default_factory=list)


Aggregator = dict[str, _PathStats]


def walk(value: Any, root_path: str, agg: Aggregator) -> None:
    _walk(value, root_path, agg)


def _walk(value: Any, path: str, agg: Aggregator) -> None:
    rec = agg.setdefault(path, _PathStats())
    rec.presence += 1

    if value is None:
        rec.null += 1
        rec.types.add("null")
        return

    if isinstance(value, dict):
        rec.types.add("object")
        if _should_prune(path):
            return
        for k, v in value.items():
            _walk(v, f"{path}.{k}", agg)
        return

    if isinstance(value, list):
        rec.types.add("array")
        if _should_prune(path):
            return
        for item in value:
            _walk(item, f"{path}[]", agg)
        return

    # Scalar
    rec.types.add(_scalar_type(value))
    if len(rec.examples) < EXAMPLE_CAP:
        ex = _capped_example(value)
        if ex not in rec.examples:
            rec.examples.append(ex)


def _should_prune(path: str) -> bool:
    return path.endswith(PRUNE_SUFFIXES)


def _scalar_type(value: Any) -> str:
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "string"
    return type(value).__name__


def _capped_example(value: Any) -> Any:
    if isinstance(value, str) and len(value) > EXAMPLE_STR_CAP:
        return value[:EXAMPLE_STR_CAP] + "..."
    return value
