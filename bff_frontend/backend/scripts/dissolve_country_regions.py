"""Dissolve geo_json/regions.geojson MultiPolygons into one clean outline per region.

The source file was built by grouping ADM2 (district) shapes without dissolving,
so each "region" is actually 17-589 separate sub-polygons. Drawn as a choropleth,
this looks like a national-level district map. We dissolve via shapely.unary_union.

Output is written to backend/data/geo/regions.geojson, replacing the noisy file.
"""
from __future__ import annotations
import json, sys, io
from pathlib import Path
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.validation import make_valid


def fill_holes(geom):
    if geom.geom_type == "Polygon":
        return Polygon(geom.exterior)
    if geom.geom_type == "MultiPolygon":
        return MultiPolygon([Polygon(p.exterior) for p in geom.geoms])
    return geom

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "geo_json" / "regions.geojson"
DST = ROOT / "bff_frontend" / "backend" / "data" / "geo" / "regions.geojson"

j = json.loads(SRC.read_text(encoding="utf-8"))

new_features = []
def part_count(geom):
    if geom.geom_type == "Polygon": return 1
    if geom.geom_type == "MultiPolygon": return len(geom.geoms)
    if geom.geom_type == "GeometryCollection":
        return sum(part_count(g) for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon"))
    return 0


def keep_polygons(geom):
    """Keep only Polygon/MultiPolygon parts, drop Lines/Points."""
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    if geom.geom_type == "GeometryCollection":
        polys = [g for g in geom.geoms if g.geom_type in ("Polygon", "MultiPolygon")]
        if not polys: return None
        return unary_union(polys)
    return None


for f in j["features"]:
    g = shape(f["geometry"])
    if not g.is_valid:
        g = make_valid(g)
        g = keep_polygons(g) or g
    dissolved = unary_union(g)
    dissolved = keep_polygons(dissolved) or dissolved
    # Many regions have micro-gaps from district-level source data.
    # Buffer-out + buffer-in merges near-touching pieces.
    if part_count(dissolved) > 5:
        eps = 0.005  # ~500m
        dissolved = dissolved.buffer(eps).buffer(-eps)
        if not dissolved.is_valid:
            dissolved = make_valid(dissolved)
            dissolved = keep_polygons(dissolved) or dissolved
    # Drop slivers (<0.1% of biggest part).
    if dissolved.geom_type == "MultiPolygon":
        biggest = max(dissolved.geoms, key=lambda p: p.area)
        keep = [p for p in dissolved.geoms if p.area >= biggest.area * 0.001]
        dissolved = MultiPolygon(keep) if len(keep) > 1 else keep[0]
    # Drop interior holes (mahalla-level pinholes from the source).
    dissolved = fill_holes(dissolved)
    # Simplify the boundary so we ship dozens of points per region, not thousands.
    # Tolerance is in degrees (WGS84): 0.005° ≈ 500 m at this latitude.
    dissolved = dissolved.simplify(0.005, preserve_topology=True)
    # Keep multi-polygon if region has detached islands (e.g. exclaves), else single polygon.
    new_features.append({
        "type": "Feature",
        "properties": f["properties"],
        "geometry": mapping(dissolved),
    })

out = {"type": "FeatureCollection", "features": new_features}
DST.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")

# Print before/after polygon counts for sanity.
def poly_count(geom):
    t = geom.get("type")
    if t == "Polygon":
        return 1
    if t == "MultiPolygon":
        return len(geom["coordinates"])
    if t == "GeometryCollection":
        return sum(poly_count(g) for g in geom.get("geometries", []))
    return 0

for orig, new in zip(j["features"], new_features):
    name = orig["properties"]["region_name"]
    print(f"  {name:32s}  {poly_count(orig['geometry']):4d} → {poly_count(new['geometry']):3d}")

print(f"\nwrote {DST}")
