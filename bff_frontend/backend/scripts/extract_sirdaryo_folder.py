"""Extract cerr_region_1724.json into the per-folder layout the fast CERR
loader expects, so Sirdaryo gets the same per-file slice access pattern as
the other 13 regions.

Output layout:
  cerr_runs/1724_sirdaryo-viloyati/
    region.json
    summary.json
    districts/{district_code}_{slug}/
      district.json
      mahallas.json
      geo.geojson

Then we add 1724 to manifest.json.
"""
from __future__ import annotations
import json, sys, io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

CERR_RUNS = Path(r"c:\Users\User\Downloads\myfolder\NBU\Projects\nbu_ai_hub\region_analytics_platform_template\cerr_runs")

REGION_CODE = 1724
REGION_SLUG = "sirdaryo-viloyati"

src_big = CERR_RUNS / f"cerr_region_{REGION_CODE}.json"
big = json.loads(src_big.read_text(encoding="utf-8"))

region_dir = CERR_RUNS / f"{REGION_CODE}_{REGION_SLUG}"
region_dir.mkdir(exist_ok=True)
districts_dir = region_dir / "districts"
districts_dir.mkdir(exist_ok=True)


# 1. region.json
region_json = {
    "region_code": big["region_code"],
    "region_name": big["region_name"],
    "region_mahalla_count": big.get("region_mahalla_count"),
    "generated_at": big.get("generated_at"),
    "overview": big.get("region_overview"),
}
(region_dir / "region.json").write_text(
    json.dumps(region_json, ensure_ascii=False), encoding="utf-8"
)
print(f"wrote {region_dir / 'region.json'}")


# 2. Per-district artifacts + collect summary list.
summary_districts = []
for d in big.get("districts", []):
    d_code = d["code"]
    # Derive a stable slug from the code only (folder lookup is
    # by_code, not by slug; the label still comes from district.name).
    d_slug = str(d_code)
    folder_name = f"{d_code}_{d_slug}"
    d_dir = districts_dir / folder_name
    d_dir.mkdir(exist_ok=True)

    # district.json
    district_payload = {
        "code": d_code,
        "name": d.get("name"),
        "mahalla_count": d.get("mahalla_count", 0),
        "overview": d.get("overview"),
        "macro": d.get("macro"),
    }
    (d_dir / "district.json").write_text(
        json.dumps(district_payload, ensure_ascii=False), encoding="utf-8"
    )

    # mahallas.json
    mahallas = d.get("mahallas") or []
    mahallas_payload = {
        "district_code": d_code,
        "district_name": d.get("name"),
        "region_code": big["region_code"],
        "region_name": big["region_name"],
        "count": len(mahallas),
        "mahallas": mahallas,
    }
    (d_dir / "mahallas.json").write_text(
        json.dumps(mahallas_payload, ensure_ascii=False), encoding="utf-8"
    )

    # geo.geojson — only write if present.
    geo = d.get("geo")
    if geo:
        (d_dir / "geo.geojson").write_text(
            json.dumps(geo, ensure_ascii=False), encoding="utf-8"
        )

    summary_districts.append({
        "code": d_code,
        "name": d.get("name"),
        "slug": d_slug,
        "mahalla_count": d.get("mahalla_count", 0),
        "mahallas_scraped": len(mahallas),
        "has_macro": bool(d.get("macro")),
        "has_geo": bool(geo),
    })


# 3. summary.json
summary = {
    "generated_at": big.get("generated_at"),
    "region_code": big["region_code"],
    "region_name": big["region_name"],
    "districts_count": len(summary_districts),
    "mahallas_scraped": big.get("mahallas_scraped", 0),
    "mahallas_skipped": big.get("mahallas_skipped", 0),
    "geo_skipped": big.get("geo_skipped", 0),
    "districts": summary_districts,
}
(region_dir / "summary.json").write_text(
    json.dumps(summary, ensure_ascii=False), encoding="utf-8"
)
print(f"wrote {region_dir / 'summary.json'}  ({len(summary_districts)} districts)")


# 4. Add to manifest.json (insert in code order, idempotent).
manifest_path = CERR_RUNS / "manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
existing = {r["code"] for r in manifest["regions"]}
if REGION_CODE not in existing:
    manifest["regions"].append({"code": REGION_CODE, "dir": f"{REGION_CODE}_{REGION_SLUG}"})
    manifest["regions"].sort(key=lambda r: r["code"])
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"added 1724 to manifest.json (total: {len(manifest['regions'])})")
else:
    print("manifest.json already contains 1724")
