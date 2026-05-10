"""Dissolve geo_json/regions/{slug}/districts.geojson district MultiPolygons.

Same problem as country regions: each district is built from sub-polygons (likely
mahalla/block-level pieces) so the map looks like a sub-district choropleth.
We dissolve each district to a single clean outline.

Per-region files are in Web Mercator (EPSG:3857), so buffer tolerance is meters.
"""
from __future__ import annotations
import json, sys, io
from pathlib import Path
from shapely.geometry import shape, mapping, MultiPolygon, Polygon
from shapely.ops import unary_union
from shapely.validation import make_valid


def fill_holes(geom):
    """Drop all interior rings (holes), keep just the outer boundary of each polygon."""
    if geom.geom_type == "Polygon":
        return Polygon(geom.exterior)
    if geom.geom_type == "MultiPolygon":
        return MultiPolygon([Polygon(p.exterior) for p in geom.geoms])
    return geom

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT / "geo_json" / "regions"
DST_DIR = ROOT / "bff_frontend" / "backend" / "data" / "geo" / "regions"


def part_count(geom):
    if geom.geom_type == "Polygon": return 1
    if geom.geom_type == "MultiPolygon": return len(geom.geoms)
    if geom.geom_type == "GeometryCollection":
        return sum(part_count(g) for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon"))
    return 0


def keep_polygons(geom):
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    if geom.geom_type == "GeometryCollection":
        polys = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
        if not polys: return None
        return unary_union(polys)
    return None


def dissolve(geom, eps_m=300):
    if not geom.is_valid:
        geom = make_valid(geom)
        geom = keep_polygons(geom) or geom
    out = unary_union(geom)
    out = keep_polygons(out) or out
    if part_count(out) > 5:
        out = out.buffer(eps_m).buffer(-eps_m)
        if not out.is_valid:
            out = make_valid(out)
            out = keep_polygons(out) or out
    if out.geom_type == "MultiPolygon":
        biggest = max(out.geoms, key=lambda p: p.area)
        keep = [p for p in out.geoms if p.area >= biggest.area * 0.001]
        out = MultiPolygon(keep) if len(keep) > 1 else keep[0]
    # Drop interior holes (source data has many small unmapped gaps that
    # render as ugly white pinholes inside each district).
    out = fill_holes(out)
    # Simplify so a district outline is a few dozen points, not thousands.
    # Tolerance is in source CRS units (meters for Mercator-projected files).
    out = out.simplify(150, preserve_topology=True)
    return out


for slug_dir in sorted(SRC_DIR.iterdir()):
    if not slug_dir.is_dir(): continue
    src = slug_dir / "districts.geojson"
    if not src.exists(): continue
    j = json.loads(src.read_text(encoding="utf-8"))
    # Some source files (e.g. fargona-viloyati) have duplicate district_code
    # entries that point at the same geometry with different name labels.
    # Drop later duplicates so each district renders exactly once.
    seen_codes = set()
    deduped_features = []
    for f in j["features"]:
        code = f["properties"].get("district_code")
        if code in seen_codes:
            continue
        seen_codes.add(code)
        deduped_features.append(f)
    if len(deduped_features) != len(j["features"]):
        print(f"    [{slug_dir.name}] deduped {len(j['features']) - len(deduped_features)} duplicate district_code(s)")
    new_features = []
    total_before = total_after = 0
    for f in deduped_features:
        g = shape(f["geometry"])
        before = part_count(g)
        d = dissolve(g, eps_m=300)
        after = part_count(d)
        total_before += before
        total_after += after
        new_features.append({
            "type": "Feature",
            "properties": f["properties"],
            "geometry": mapping(d),
        })
    out = {"type": "FeatureCollection", "features": new_features}
    dst_dir = DST_DIR / slug_dir.name
    dst_dir.mkdir(parents=True, exist_ok=True)
    (dst_dir / "districts.geojson").write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"  {slug_dir.name:35s}  features={len(j['features']):3d}  sub-polys: {total_before:4d} → {total_after:3d}")

print("done")
