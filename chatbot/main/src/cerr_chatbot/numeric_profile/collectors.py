"""Walk source data and accumulate raw values into ValueBags / metadata sets.

Row identity rules:
- Region row id   = source file name (one region per file).
- District row id = (file_name, district_index_within_file).
- Mahalla row id  = (file_name, district_index, mahalla_index).

These identities are independent of natural keys (region_code, district code,
mahalla STIR), which are NOT globally unique in source data. Completeness
counts in this module use row ids; natural-key uniqueness is reported
separately as diagnostics.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any

from cerr_chatbot.numeric_profile.stats import ValueBag

RegionRowId = str
DistrictRowId = tuple[str, int]
MahallaRowId = tuple[str, int, int]


@dataclass
class KpiAccumulator:
    value: ValueBag = field(default_factory=ValueBag)
    change_pct: ValueBag = field(default_factory=ValueBag)
    district_avg: ValueBag = field(default_factory=ValueBag)
    seen_row_ids: set[Any] = field(default_factory=set)
    labels: set[str] = field(default_factory=set)
    formats: set[str] = field(default_factory=set)
    directions: set[str] = field(default_factory=set)
    tables: set[str] = field(default_factory=set)
    columns: set[str] = field(default_factory=set)
    scopes: set[Any] = field(default_factory=set)
    provenance: set[str] = field(default_factory=set)


@dataclass
class MacroAccumulator:
    labels: set[str] = field(default_factory=set)
    units: set[str] = field(default_factory=set)
    directions: set[str] = field(default_factory=set)
    seen_district_row_ids: set[DistrictRowId] = field(default_factory=set)
    highlighted_seen_row_ids: set[DistrictRowId] = field(default_factory=set)
    points_per_district: list[int] = field(default_factory=list)
    total_points: int = 0
    highlighted_count: int = 0
    highlighted_value_null_count: int = 0
    all_point_values: ValueBag = field(default_factory=ValueBag)
    highlighted_values: ValueBag = field(default_factory=ValueBag)


@dataclass
class PeerAccumulator:
    this_value: ValueBag = field(default_factory=ValueBag)
    district_avg: ValueBag = field(default_factory=ValueBag)
    percentile: ValueBag = field(default_factory=ValueBag)
    labels: set[str] = field(default_factory=set)
    units: set[str] = field(default_factory=set)
    directions: set[str] = field(default_factory=set)
    peer_ranks: list[int] = field(default_factory=list)
    peer_counts: list[int] = field(default_factory=list)
    rank_exceeds_count: int = 0
    percentile_out_of_range: int = 0


@dataclass
class Collected:
    region_count: int = 0
    district_count: int = 0
    mahalla_count: int = 0
    kpis: dict[tuple[str, str], KpiAccumulator] = field(
        default_factory=lambda: defaultdict(KpiAccumulator)
    )
    macro: dict[str, MacroAccumulator] = field(
        default_factory=lambda: defaultdict(MacroAccumulator)
    )
    macro_district_indicator_count: dict[DistrictRowId, int] = field(default_factory=dict)
    peer: dict[tuple[str, str], PeerAccumulator] = field(
        default_factory=lambda: defaultdict(PeerAccumulator)
    )
    detail_bags: dict[tuple[str, str, str], ValueBag] = field(
        default_factory=lambda: defaultdict(ValueBag)
    )

    # Natural-key collision diagnostics (independent of completeness).
    region_code_counts: Counter[int] = field(default_factory=Counter)
    district_code_counts: Counter[int] = field(default_factory=Counter)
    mahalla_stir_counts: Counter[str] = field(default_factory=Counter)
    mahalla_composite_key_counts: Counter[tuple[Any, Any, str]] = field(default_factory=Counter)


# (group, proposed_column_name, json_subpath_under_mahalla)
DETAIL_FIELDS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    # infra (keys are source-side names, mapped to catalog column names).
    ("mahalla_infrastructure", "road_total_km", ("overview", "detail", "infra", "road_km")),
    ("mahalla_infrastructure", "road_dirt_km", ("overview", "detail", "infra", "road_dirt_km")),
    (
        "mahalla_infrastructure",
        "road_asphalt_km",
        ("overview", "detail", "infra", "road_asphalt_km"),
    ),
    (
        "mahalla_infrastructure",
        "households_without_drinking_water_count",
        ("overview", "detail", "infra", "no_water"),
    ),
    ("mahalla_infrastructure", "power_outage_count", ("overview", "detail", "infra", "power_cuts")),
    (
        "mahalla_infrastructure",
        "medical_facility_distance_km",
        ("overview", "detail", "infra", "medical_km"),
    ),
    ("mahalla_infrastructure", "school_count", ("overview", "detail", "infra", "school")),
    ("mahalla_infrastructure", "sports_facility_count", ("overview", "detail", "infra", "sport")),
    (
        "mahalla_infrastructure",
        "kindergarten_count",
        ("overview", "detail", "infra", "kindergarten"),
    ),
    ("mahalla_infrastructure", "homestead_area_ha", ("overview", "detail", "infra", "tomorqa_ha")),
    # appeals
    ("mahalla_appeals", "crime_appeal_count", ("overview", "appeals", "crime")),
    ("mahalla_appeals", "divorce_appeal_count", ("overview", "appeals", "divorce")),
    ("mahalla_appeals", "social_aid_appeal_count", ("overview", "appeals", "aid")),
    ("mahalla_appeals", "employment_appeal_count", ("overview", "appeals", "employment")),
    ("mahalla_appeals", "gas_appeal_count", ("overview", "appeals", "gas")),
    ("mahalla_appeals", "registry_appeal_count", ("overview", "appeals", "registry")),
    # specialization aggregates (mahalla-level scalars)
    (
        "mahalla_specializations_summary",
        "residual_percent",
        ("overview", "detail", "specialization", "residual_percent"),
    ),
    (
        "mahalla_specializations_summary",
        "total_known_percent",
        ("overview", "detail", "specialization", "total_known_percent"),
    ),
    # crops summary
    (
        "mahalla_crops_summary",
        "total_homestead_area_sotkah",
        ("overview", "detail", "crops", "total_homestead_area_sotikh"),
    ),
)


def _path_get(obj: Any, parts: tuple[str, ...]) -> Any:
    cur: Any = obj
    for p in parts:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def collect(
    payload: dict[str, Any],
    out: Collected,
    *,
    file_name: str = "<unknown>",
) -> None:
    out.region_count += 1
    region_code = payload.get("region_code")
    if isinstance(region_code, int):
        out.region_code_counts[region_code] += 1

    region_row_id: RegionRowId = file_name
    _collect_kpis(payload.get("region_overview"), "region", region_row_id, out)

    districts = payload.get("districts") or []
    if not isinstance(districts, list):
        return
    for d_idx, d in enumerate(districts):
        if not isinstance(d, dict):
            continue
        out.district_count += 1
        district_row_id: DistrictRowId = (file_name, d_idx)
        district_code = d.get("code")
        if isinstance(district_code, int):
            out.district_code_counts[district_code] += 1

        _collect_kpis(d.get("overview"), "district", district_row_id, out)
        _collect_macro(d.get("macro"), district_row_id, out)

        mahallas = d.get("mahallas") or []
        if not isinstance(mahallas, list):
            continue
        for m_idx, m in enumerate(mahallas):
            if not isinstance(m, dict):
                continue
            out.mahalla_count += 1
            mahalla_row_id: MahallaRowId = (file_name, d_idx, m_idx)

            stir = m.get("stir")
            if isinstance(stir, str) and stir:
                out.mahalla_stir_counts[stir] += 1
                out.mahalla_composite_key_counts[(region_code, district_code, stir)] += 1

            _collect_kpis(m.get("overview"), "mahalla", mahalla_row_id, out)
            _collect_peer(m.get("overview"), out)
            _collect_details(m, out)


def _collect_kpis(overview: Any, level: str, row_id: Any, out: Collected) -> None:
    if not isinstance(overview, dict):
        return
    kpis = overview.get("kpis")
    if not isinstance(kpis, list):
        return
    for k in kpis:
        if not isinstance(k, dict):
            continue
        key = k.get("key")
        if not isinstance(key, str):
            continue
        acc = out.kpis[(level, key)]
        acc.seen_row_ids.add(row_id)
        acc.value.add(k.get("value"))
        acc.change_pct.add(k.get("change_pct"))
        acc.district_avg.add(k.get("district_avg"))
        for src_key, sink in (
            ("label", acc.labels),
            ("format", acc.formats),
            ("direction", acc.directions),
            ("table", acc.tables),
            ("column", acc.columns),
            ("provenance", acc.provenance),
        ):
            v = k.get(src_key)
            if isinstance(v, str):
                sink.add(v)
        scope = k.get("compare_scope")
        if scope is not None:
            acc.scopes.add(scope)


def _collect_macro(macro: Any, district_row_id: DistrictRowId, out: Collected) -> None:
    if not isinstance(macro, dict):
        return
    indicators = macro.get("indicators")
    if not isinstance(indicators, list):
        return
    out.macro_district_indicator_count[district_row_id] = out.macro_district_indicator_count.get(
        district_row_id, 0
    ) + sum(1 for x in indicators if isinstance(x, dict))
    for ind in indicators:
        if not isinstance(ind, dict):
            continue
        key = ind.get("key")
        if not isinstance(key, str):
            continue
        acc = out.macro[key]
        acc.seen_district_row_ids.add(district_row_id)
        for src_key, sink in (
            ("label", acc.labels),
            ("unit", acc.units),
            ("direction", acc.directions),
        ):
            v = ind.get(src_key)
            if isinstance(v, str):
                sink.add(v)
        points = ind.get("points")
        if not isinstance(points, list):
            continue
        per_district_points = 0
        for p in points:
            if not isinstance(p, dict):
                continue
            per_district_points += 1
            acc.total_points += 1
            val = p.get("value")
            acc.all_point_values.add(val)
            if p.get("highlighted") is True:
                acc.highlighted_count += 1
                acc.highlighted_seen_row_ids.add(district_row_id)
                if val is None:
                    acc.highlighted_value_null_count += 1
                acc.highlighted_values.add(val)
        if per_district_points > 0:
            acc.points_per_district.append(per_district_points)


def _collect_peer(overview: Any, out: Collected) -> None:
    if not isinstance(overview, dict):
        return
    pp = overview.get("peer_profile")
    if not isinstance(pp, dict):
        return
    for polarity in ("strengths", "weaknesses"):
        items = pp.get(polarity)
        if not isinstance(items, list):
            continue
        for f in items:
            if not isinstance(f, dict):
                continue
            key = f.get("key")
            if not isinstance(key, str):
                continue
            acc = out.peer[(polarity, key)]
            acc.this_value.add(f.get("this_value"))
            acc.district_avg.add(f.get("district_avg"))
            acc.percentile.add(f.get("percentile"))
            for src_key, sink in (
                ("label", acc.labels),
                ("unit", acc.units),
                ("direction", acc.directions),
            ):
                v = f.get(src_key)
                if isinstance(v, str):
                    sink.add(v)
            rank = f.get("peer_rank")
            count = f.get("peer_count")
            if isinstance(rank, int) and not isinstance(rank, bool):
                acc.peer_ranks.append(rank)
            if isinstance(count, int) and not isinstance(count, bool):
                acc.peer_counts.append(count)
            if (
                isinstance(rank, int)
                and isinstance(count, int)
                and not isinstance(rank, bool)
                and not isinstance(count, bool)
                and rank > count
            ):
                acc.rank_exceeds_count += 1
            pct = f.get("percentile")
            if (
                isinstance(pct, (int, float))
                and not isinstance(pct, bool)
                and (pct < 0 or pct > 100)
            ):
                acc.percentile_out_of_range += 1


def _collect_details(mahalla: dict[str, Any], out: Collected) -> None:
    for group, column, parts in DETAIL_FIELDS:
        out.detail_bags[(group, column, ".".join(parts))].add(_path_get(mahalla, parts))

    # specialization items
    items = _path_get(mahalla, ("overview", "detail", "specialization", "items"))
    if isinstance(items, list):
        for it in items:
            if not isinstance(it, dict):
                continue
            for src_key, column in (
                ("households", "household_count"),
                ("population", "population_count"),
                ("percent", "share_percent"),
            ):
                key = ("mahalla_specializations", column, f"items[].{src_key}")
                out.detail_bags[key].add(it.get(src_key))

    # crops seasons
    seasons = _path_get(mahalla, ("overview", "detail", "crops", "seasons"))
    if isinstance(seasons, list):
        for s in seasons:
            if not isinstance(s, dict):
                continue
            for src_key, column in (
                ("total_area_ha", "total_area_ha"),
                ("homestead_area_ha", "homestead_area_ha"),
                ("household_count", "household_count"),
            ):
                key = ("mahalla_crops", column, f"seasons[].{src_key}")
                out.detail_bags[key].add(s.get(src_key))

    # subsidy programs
    programs = _path_get(mahalla, ("overview", "detail", "subsidies", "programs"))
    if isinstance(programs, list):
        for p in programs:
            if not isinstance(p, dict):
                continue
            for src_key, column in (
                ("applications", "application_count"),
                ("required_amount_mln", "required_amount_mln_uzs"),
            ):
                key = ("mahalla_subsidy_programs", column, f"programs[].{src_key}")
                out.detail_bags[key].add(p.get(src_key))
