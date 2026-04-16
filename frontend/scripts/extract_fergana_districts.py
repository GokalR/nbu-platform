"""Extract Fergana region ADM2 features and tag with our district keys.

Input:  geoBoundaries ADM2 file (all 199 Uzbekistan districts)
Output: GeoJSON with 19 Fergana region cities+districts
"""

import json
import sys
from pathlib import Path

# shapeName → our district key (matches src/data/districts.js)
FERGANA_MAP = {
    'Fergana city':    ('fargona_city',  'city'),
    'Margilan city':   ('margilon_city', 'city'),
    'Kokand city':     ('qoqon_city',    'city'),
    'Kuvasay city':    ('quvasoy_city',  'city'),
    'Altiarik':        ('oltiariq',      'district'),
    'Bagdad':          ('bogdod',        'district'),
    'Besharik':        ('beshariq',      'district'),
    'Buvayda':         ('buvayda',       'district'),
    'Dangara':         ('dangara',       'district'),
    'Fergana':         ('farhona',       'district'),
    'Furkat':          ('furqat',        'district'),
    'Kushtepa':        ('qoshtepa',      'district'),
    'Kuva':            ('quva',          'district'),
    'Rishtan':         ('rishton',       'district'),
    'Sokh':            ('sox',           'district'),
    'Tashlak':         ('toshloq',       'district'),
    'Uchkuprik':       ('uchkoprik',     'district'),
    'Uzbekistan':      ('ozbekiston',    'district'),
    'Yazyavan':        ('yozyovon',      'district'),
}

def main(src: str, dst: str) -> None:
    data = json.loads(Path(src).read_text(encoding='utf-8'))
    out = []
    for feat in data['features']:
        name = feat['properties'].get('shapeName')
        if name not in FERGANA_MAP:
            continue
        key, kind = FERGANA_MAP[name]
        out.append({
            'type': 'Feature',
            'properties': {'key': key, 'name': name, 'kind': kind},
            'geometry': feat['geometry'],
        })
    result = {
        'type': 'FeatureCollection',
        '_source': 'geoBoundaries gbOpen ADM2, CC BY 3.0 IGO',
        'features': out,
    }
    Path(dst).write_text(json.dumps(result, ensure_ascii=False), encoding='utf-8')
    print(f'wrote {len(out)} features → {dst}')
    print('missing:', sorted(set(FERGANA_MAP.keys()) - {f['properties']['name'] for f in out}))


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
