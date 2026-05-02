"""Generate frontend/src/data/goldenMart/{city|region|country}Schema.js
from the 3 GM MD files (which are themselves regenerated from the Excels).

The MDs are the source of truth; this script parses their section
headers + tables and emits JS modules with:
  - <LEVEL>_SECTIONS — list of sections × attrs
  - <LEVEL>_TOTAL_FIELDS — int sum
  - <LEVEL>_TABS — 6 thematic tab groupings (hand-curated)
  - tabSections(tabId) — helper that returns full section objects

Keys are positional (s{section}_{index}, 1-indexed) — stable across
regenerations. Per-entity data files reference fields by these keys.

Usage:
  PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_schema_js.py
"""
from __future__ import annotations
import json
import os
import re

HERE = os.path.dirname(__file__)

# Russian → Uzbek translations for section titles + field labels.
# Structured as { "_sections": {...}, "_fields": {...} }. Both maps key on
# the Russian label and return the Uzbek translation. When a key is missing,
# we fall back to the Russian label so the UI never goes blank.
TRANSLATIONS_PATH = os.path.join(HERE, '_translations_uz.json')
try:
    with open(TRANSLATIONS_PATH, encoding='utf-8') as _f:
        _UZ = json.load(_f)
    UZ_SECTIONS = _UZ.get('_sections', {})
    UZ_FIELDS   = _UZ.get('_fields', {})
except FileNotFoundError:
    UZ_SECTIONS, UZ_FIELDS = {}, {}

# Hand-mapped icons per section number (consistent across levels).
# Sections that don't exist at a given level are skipped automatically.
SECTION_ICONS = {
    1: 'badge', 2: 'finance', 3: 'account_balance', 4: 'public', 5: 'flag',
    6: 'savings', 7: 'storefront', 8: 'work', 9: 'volunteer_activism',
    10: 'school', 11: 'local_hospital', 12: 'account_balance_wallet',
    13: 'travel_explore', 14: 'home', 15: 'hub', 16: 'route',
    17: 'directions_bus', 18: 'park', 19: 'devices', 20: 'leaderboard',
    21: 'warning',
}

# 6 thematic tabs — same grouping for all levels. Sections missing at a
# given level just resolve to nothing in that tab.
TABS = [
    {'id': 'basic',    'num': '01', 'icon': 'badge',                  'label': 'Базовая',         'sections': [1]},
    {'id': 'economy',  'num': '02', 'icon': 'finance',                'label': 'Экономика',       'sections': [2, 3, 4, 5, 6, 7]},
    {'id': 'people',   'num': '03', 'icon': 'groups',                 'label': 'Население',       'sections': [8, 9, 11]},
    {'id': 'social',   'num': '04', 'icon': 'school',                 'label': 'Соц-инфра',       'sections': [10, 14, 15, 16, 17]},
    {'id': 'finance',  'num': '05', 'icon': 'account_balance_wallet', 'label': 'Финансы и цифра', 'sections': [12, 13, 19, 20]},
    {'id': 'mahalla',  'num': '06', 'icon': 'storefront',             'label': 'Махалля и среда', 'sections': [18, 21]},
]

# Levels we generate
LEVELS = [
    {
        'level': 'city',
        'md_file': 'GM_city.md',
        'js_out': '../frontend/src/data/goldenMart/citySchema.js',
        'prefix': 'CITY',
    },
    {
        'level': 'region',
        'md_file': 'GM_region.md',
        'js_out': '../frontend/src/data/goldenMart/regionSchema.js',
        'prefix': 'REGION',
    },
    {
        'level': 'country',
        'md_file': 'GM_country.md',
        'js_out': '../frontend/src/data/goldenMart/countrySchema.js',
        'prefix': 'COUNTRY',
    },
]


def parse_md(md_text: str):
    sections = []
    cur = None
    in_table = False
    for line in md_text.splitlines():
        s = line.strip()
        m = re.match(r'^##\s+(\d+)\.\s+(.+)$', s)
        if m:
            n = int(m.group(1))
            title = m.group(2).strip()
            cur = {'n': n, 'title': title, 'attrs': []}
            sections.append(cur)
            in_table = False
            continue
        if cur is None:
            continue
        if s.startswith('|---'):
            in_table = True
            continue
        if not in_table:
            continue
        if not s.startswith('|'):
            in_table = False
            continue
        cells = [c.strip() for c in s.strip('|').split('|')]
        if len(cells) < 2:
            continue
        label = cells[0]
        unit  = cells[1] if len(cells) > 1 else ''
        if label in ('Показатель', '---'):
            continue
        idx = len(cur['attrs']) + 1
        cur['attrs'].append({
            'label': label,
            'unit': unit,
            'key': f's{cur["n"]}_{idx}',
        })
    return sections


def js_string(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def emit_js(prefix: str, level: str, sections: list[dict]) -> str:
    lines = []
    lines.append('/**')
    lines.append(f' * Golden Mart — {level} schema.')
    lines.append(' *')
    lines.append(f' * AUTO-GENERATED from goldenmarts/GM_{level}.md (which itself is')
    lines.append(f' * generated from goldenmarts/golden_mart_{level}.xlsx via _to_md.py).')
    lines.append(' * Do not hand-edit. To change: edit the Excel, run _to_md.py, then')
    lines.append(' * goldenmarts/_md_to_schema_js.py. Bilingual labels come from')
    lines.append(' * goldenmarts/_translations_uz.json — missing keys fall back to RU.')
    lines.append(' *')
    lines.append(f' * Per-entity data files reference fields by `key` (positional s{{section}}_{{index}}).')
    lines.append(' */')
    lines.append('')
    lines.append(f'export const {prefix}_SECTIONS = [')
    for s in sections:
        icon = SECTION_ICONS.get(s['n'], 'help')
        title_uz = UZ_SECTIONS.get(s['title'], s['title'])
        lines.append('  {')
        lines.append(
            f'    n: {s["n"]}, title: {js_string(s["title"])}, '
            f'titleUz: {js_string(title_uz)}, icon: {js_string(icon)},'
        )
        lines.append('    attrs: [')
        for a in s['attrs']:
            label_uz = UZ_FIELDS.get(a['label'], a['label'])
            lines.append(
                f'      {{ key: {js_string(a["key"])}, '
                f'label: {js_string(a["label"])}, '
                f'labelUz: {js_string(label_uz)}, '
                f'unit: {js_string(a["unit"])} }},'
            )
        lines.append('    ],')
        lines.append('  },')
    lines.append(']')
    lines.append('')
    lines.append(f'export const {prefix}_TOTAL_FIELDS = {prefix}_SECTIONS.reduce(')
    lines.append('  (n, s) => n + s.attrs.length,')
    lines.append('  0,')
    lines.append(')')
    lines.append('')
    lines.append(f'export const {prefix}_TABS = [')
    for t in TABS:
        sec_list = ', '.join(str(n) for n in t['sections'])
        lines.append(
            f'  {{ id: {js_string(t["id"])}, num: {js_string(t["num"])}, '
            f'icon: {js_string(t["icon"])}, label: {js_string(t["label"])}, '
            f'sections: [{sec_list}] }},'
        )
    lines.append(']')
    lines.append('')
    lines.append(f'export function tabSections(tabId) {{')
    lines.append(f'  const tab = {prefix}_TABS.find((t) => t.id === tabId)')
    lines.append('  if (!tab) return []')
    lines.append('  return tab.sections')
    lines.append(f'    .map((n) => {prefix}_SECTIONS.find((s) => s.n === n))')
    lines.append('    .filter(Boolean)')
    lines.append('}')
    lines.append('')
    return '\n'.join(lines)


if __name__ == '__main__':
    for cfg in LEVELS:
        md_path = os.path.join(HERE, cfg['md_file'])
        if not os.path.exists(md_path):
            print(f'  SKIP {cfg["level"]}: {md_path} missing')
            continue
        with open(md_path, encoding='utf-8') as f:
            md = f.read()
        sections = parse_md(md)
        js = emit_js(cfg['prefix'], cfg['level'], sections)
        out_path = os.path.normpath(os.path.join(HERE, cfg['js_out']))
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(js)
        total = sum(len(s['attrs']) for s in sections)
        print(f'  {cfg["level"]}: {len(sections)} sections, {total} attrs → {out_path}')
