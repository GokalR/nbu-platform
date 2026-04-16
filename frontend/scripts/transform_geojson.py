"""Transform geoBoundaries Uzbekistan ADM1 GeoJSON into our schema.

Input:  any geoBoundaries-style file with `properties.shapeName`
Output: same geometry, but each feature has `properties.key` matching our IDs

Usage:
    python scripts/transform_geojson.py input.geojson public/uzbekistan-regions.geojson
"""

import json
import sys
from pathlib import Path

NAME_TO_KEY = {
    "Andijan Region": "andijan",
    "Bukhara Region": "bukhara",
    "Fergana Region": "fergana",
    "Jizzakh Region": "jizzax",
    "Namangan Region": "namangan",
    "Navoiy Region": "navoiy",
    "Qashqadaryo Region": "qashqadaryo",
    "Republic of Karakalpakstan": "karakalpakstan",
    "Samarqand Region": "samarqand",
    "Sirdaryo Region": "sirdaryo",
    "Surxondaryo Region": "surxondaryo",
    "Tashkent Region": "tashkent_region",
    "Tashkent": "tashkent_city",
    "Xorazm Region": "khorezm",
}


def main(src: str, dst: str) -> None:
    data = json.loads(Path(src).read_text(encoding="utf-8"))
    out_features = []
    for feat in data["features"]:
        name = feat["properties"].get("shapeName")
        key = NAME_TO_KEY.get(name)
        if not key:
            print(f"  skip: unknown region '{name}'", file=sys.stderr)
            continue
        out_features.append({
            "type": "Feature",
            "properties": {"key": key, "name": name},
            "geometry": feat["geometry"],
        })

    out = {
        "type": "FeatureCollection",
        "_source": "geoBoundaries gbOpen ADM1, ODbL 1.0",
        "features": out_features,
    }
    Path(dst).write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {len(out_features)} features to {dst}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
