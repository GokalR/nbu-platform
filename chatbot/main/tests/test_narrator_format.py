"""format_number / format_rows / compute_derived_metrics."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from cerr_chatbot.query.narrator_format import (
    compute_derived_metrics,
    format_cell,
    format_number,
    format_rows,
)

# ---------- format_number ----------


@pytest.mark.parametrize(
    "value,expected",
    [
        (67611.4667952569, "67,611.47"),
        (259153.0518750056, "259,153.05"),
        (1234567, "1,234,567"),
        (1234.5, "1,234.5"),
        (0, "0"),
        (0.0, "0"),
        (-0.0151, "-0.02"),
        (1.0, "1"),
        (4330143.0, "4,330,143"),
    ],
)
def test_format_number_human_readable(value, expected: str) -> None:
    assert format_number(value) == expected


def test_format_number_handles_non_numeric() -> None:
    assert format_number("Андижон") == "Андижон"
    assert format_number(None) == ""


def test_format_cell_passes_strings_through() -> None:
    assert format_cell("Самарқанд") == "Самарқанд"
    assert format_cell(None) is None


def test_format_rows_replaces_only_numeric_cells() -> None:
    rows = (("Андижон", 1234567), ("Фарғона", 999.5))
    out = format_rows(rows)
    assert out == (("Андижон", "1,234,567"), ("Фарғона", "999.5"))


# ---------- compute_derived_metrics ----------


@dataclass
class _Q:
    purpose: str
    columns: tuple[str, ...]
    rows: tuple[tuple, ...]
    row_count: int
    sql: str | None = None
    error: str | None = None


def _primary_top5_population():
    return _Q(
        purpose="primary",
        columns=("region_name_cyr", "population"),
        rows=(
            ("Самарқанд вилояти", 4330143),
            ("Фарғона вилояти", 4204055),
            ("Қашқадарё вилояти", 3591291),
            ("Андижон вилояти", 3479657),
            ("Тошкент шаҳри", 3177589),
        ),
        row_count=5,
    )


def test_metrics_top5_population_has_first_gap_and_share() -> None:
    primary = _primary_top5_population()
    m = compute_derived_metrics(primary, ())
    assert m["shown_count"] == 5
    assert m["first_row_label"] == "Самарқанд вилояти"
    assert m["first_row_value"] == "4,330,143"
    assert m["second_row_value"] == "4,204,055"
    assert m["gap_first_to_second_abs"] == "126,088"
    assert m["sum_shown"] == "18,782,735"
    # Самарқанд / 18.78M ≈ 23.05%
    assert m["share_first_of_shown_pct"].startswith("23")


def test_metrics_with_context_avg_emits_cross_metrics() -> None:
    primary = _primary_top5_population()
    ctx = (
        _Q(
            purpose="average population baseline",
            columns=("avg_pop",),
            rows=((2681526.7,),),
            row_count=1,
        ),
    )
    m = compute_derived_metrics(primary, ctx)
    key = "average_population_baseline"
    assert m[f"context.{key}"] == "2,681,526.7"
    # 4,330,143 / 2,681,526.7 ≈ 1.6147
    assert m[f"first_vs_{key}_ratio"].startswith("1.6")
    # (4,330,143 - 2,681,526.7) / 2,681,526.7 * 100 ≈ 61.5
    assert m[f"first_vs_{key}_pct_diff"].startswith("61.")


def test_metrics_handle_all_zero_values() -> None:
    primary = _Q(
        purpose="primary",
        columns=("region_name_cyr", "rating_score"),
        rows=((f"R{i}", 0.0) for i in range(3)),  # generator on purpose
        row_count=3,
    )
    # Convert generator to tuple for stable iteration since metrics scans twice.
    primary = _Q(
        purpose="primary",
        columns=primary.columns,
        rows=(("R0", 0.0), ("R1", 0.0), ("R2", 0.0)),
        row_count=3,
    )
    m = compute_derived_metrics(primary, ())
    assert m["all_values_equal"] is True
    assert m["first_row_value"] == "0"
    assert m["sum_shown"] == "0"
    # No share because sum is zero — guard prevents divide-by-zero.
    assert "share_first_of_shown_pct" not in m


def test_metrics_handles_null_values() -> None:
    primary = _Q(
        purpose="primary",
        columns=("region_name_cyr", "population"),
        rows=(("A", None), ("B", 100), ("C", 200)),
        row_count=3,
    )
    m = compute_derived_metrics(primary, ())
    assert m["rows_with_null_value"] == 1
    assert m["rows_with_value"] == 2
    # First value is None — function moves on; first_row_value reflects None.
    # Implementation choice: keep the test loose — just verify no crash.
    assert m["first_row_label"] == "B"
    assert m["first_row_value"] == "100"


def test_metrics_skip_context_with_error_or_multi_row() -> None:
    primary = _primary_top5_population()
    ctx = (
        _Q(purpose="bad", columns=("avg",), rows=(), row_count=0, error="sql_guard: blocked"),
        _Q(purpose="multi", columns=("a",), rows=((1,), (2,)), row_count=2),
    )
    m = compute_derived_metrics(primary, ctx)
    # Neither context contributed.
    assert "context.bad" not in m
    assert "context.multi" not in m


def test_metrics_do_not_compute_ratio_against_count_context() -> None:
    primary = _primary_top5_population()
    ctx = (
        _Q(
            purpose="count of rows at floor value",
            columns=("n",),
            rows=((10,),),
            row_count=1,
        ),
    )
    m = compute_derived_metrics(primary, ctx)
    assert m["context.count_of_rows_at_floor_value"] == "10"
    assert "first_vs_count_of_rows_at_floor_value_ratio" not in m
    assert "first_vs_count_of_rows_at_floor_value_pct_diff" not in m


def test_metrics_compute_share_only_against_total_context() -> None:
    primary = _primary_top5_population()
    ctx = (
        _Q(
            purpose="total population",
            columns=("total_population",),
            rows=((37541374,),),
            row_count=1,
        ),
    )
    m = compute_derived_metrics(primary, ctx)
    assert m["context.total_population"] == "37,541,374"
    assert m["share_first_of_total_population_pct"].startswith("11.")
    assert "first_vs_total_population_ratio" not in m
