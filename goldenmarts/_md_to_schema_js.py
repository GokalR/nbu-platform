"""Generate frontend/src/data/goldenMart/citySchema.js from GM_city.md.

The MD is the source of truth (regenerated from the Excel). This script
parses the MD section headers + tables and emits a JS module with:
  - CITY_SECTIONS : 21 sections × N attrs each
  - CITY_TOTAL_FIELDS : sum of attrs
  - CITY_TABS : 6 thematic tab groupings (hand-curated)
  - tabSections() helper

Keys are auto-derived from the Russian label with a deterministic slug.
For readability, we keep `key` short and stable across regenerations.

Usage:  PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_schema_js.py
"""
from __future__ import annotations
import os
import re

HERE = os.path.dirname(__file__)
MD_PATH = os.path.join(HERE, 'GM_city.md')
JS_OUT  = os.path.join(HERE, '..', 'frontend', 'src', 'data', 'goldenMart', 'citySchema.js')

# Hand-mapped icons per section (1-indexed)
SECTION_ICONS = {
    1: 'badge', 2: 'finance', 3: 'account_balance', 4: 'public', 5: 'flag',
    6: 'savings', 7: 'storefront', 8: 'work', 9: 'volunteer_activism',
    10: 'school', 11: 'local_hospital', 12: 'account_balance_wallet',
    13: 'travel_explore', 14: 'home', 15: 'hub', 16: 'route',
    17: 'directions_bus', 18: 'park', 19: 'devices', 20: 'leaderboard',
    21: 'warning',
}

# 6 thematic tabs (mirror of Fergana 6-tab pattern). Section numbers per tab.
TABS = [
    {'id': 'basic',    'num': '01', 'icon': 'badge',                  'label': 'Базовая',         'sections': [1]},
    {'id': 'economy',  'num': '02', 'icon': 'finance',                'label': 'Экономика',       'sections': [2, 3, 4, 5, 6, 7]},
    {'id': 'people',   'num': '03', 'icon': 'groups',                 'label': 'Население',       'sections': [8, 9, 11]},
    {'id': 'social',   'num': '04', 'icon': 'school',                 'label': 'Соц-инфра',       'sections': [10, 14, 15, 16, 17]},
    {'id': 'finance',  'num': '05', 'icon': 'account_balance_wallet', 'label': 'Финансы и цифра', 'sections': [12, 13, 19]},
    {'id': 'mahalla',  'num': '06', 'icon': 'storefront',             'label': 'Махалля и среда', 'sections': [18, 20, 21]},
]


def slug_for(label: str, section_n: int, idx: int) -> str:
    """Position-based stable key: s{section}_{index}. Stable across regenerations
    even if labels are tweaked."""
    return f's{section_n}_{idx}'


def parse_md(md_text: str):
    sections = []
    cur = None
    in_table = False
    seen_header = False
    for line in md_text.splitlines():
        s = line.strip()
        m = re.match(r'^##\s+(\d+)\.\s+(.+)$', s)
        if m:
            n = int(m.group(1))
            title = m.group(2).strip()
            cur = {'n': n, 'title': title, 'attrs': []}
            sections.append(cur)
            in_table = False
            seen_header = False
            continue
        if cur is None:
            continue
        if s.startswith('|---'):
            in_table = True
            seen_header = True
            continue
        if not in_table:
            # header row "| Показатель | Единица | Пример |"
            if s.startswith('| Показатель'):
                continue
            continue
        if not s.startswith('|'):
            in_table = False
            continue
        # data row
        cells = [c.strip() for c in s.strip('|').split('|')]
        if len(cells) < 2:
            continue
        label = cells[0].strip()
        unit  = cells[1].strip() if len(cells) > 1 else ''
        # Skip placeholder header echoes
        if label in ('Показатель', '---'):
            continue
        idx = len(cur['attrs']) + 1
        cur['attrs'].append({
            'label': label,
            'unit': unit,
            'key': slug_for(label, cur['n'], idx),
        })
    return sections


def js_string(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


def emit_js(sections):
    lines = []
    lines.append('/**')
    lines.append(' * Golden Mart — City/Tuman schema (21 sections).')
    lines.append(' *')
    lines.append(' * AUTO-GENERATED from goldenmarts/GM_city.md (which itself is')
    lines.append(' * generated from goldenmarts/golden_mart_city.xlsx via _to_md.py).')
    lines.append(' * Do not hand-edit. To change: edit the Excel, run _to_md.py, then')
    lines.append(' * run goldenmarts/_md_to_schema_js.py.')
    lines.append(' *')
    lines.append(' * Per-city data files (e.g. goldenMart/qoqon.js) reference fields')
    lines.append(' * by `key` (numeric: s{section}_{index}, 1-indexed).')
    lines.append(' */')
    lines.append('')
    lines.append('export const CITY_SECTIONS = [')
    for s in sections:
        icon = SECTION_ICONS.get(s['n'], 'help')
        lines.append('  {')
        lines.append(f'    n: {s["n"]}, title: {js_string(s["title"])}, icon: {js_string(icon)},')
        lines.append('    attrs: [')
        for a in s['attrs']:
            lines.append(
                f'      {{ key: {js_string(a["key"])}, label: {js_string(a["label"])}, unit: {js_string(a["unit"])} }},'
            )
        lines.append('    ],')
        lines.append('  },')
    lines.append(']')
    lines.append('')
    lines.append('export const CITY_TOTAL_FIELDS = CITY_SECTIONS.reduce(')
    lines.append('  (n, s) => n + s.attrs.length,')
    lines.append('  0,')
    lines.append(')')
    lines.append('')
    lines.append('export const CITY_TABS = [')
    for t in TABS:
        sec_list = ', '.join(str(n) for n in t['sections'])
        lines.append(
            f'  {{ id: {js_string(t["id"])}, num: {js_string(t["num"])}, '
            f'icon: {js_string(t["icon"])}, label: {js_string(t["label"])}, '
            f'sections: [{sec_list}] }},'
        )
    lines.append(']')
    lines.append('')
    lines.append('export function tabSections(tabId) {')
    lines.append('  const tab = CITY_TABS.find((t) => t.id === tabId)')
    lines.append('  if (!tab) return []')
    lines.append('  return tab.sections')
    lines.append('    .map((n) => CITY_SECTIONS.find((s) => s.n === n))')
    lines.append('    .filter(Boolean)')
    lines.append('}')
    lines.append('')
    return '\n'.join(lines)


if __name__ == '__main__':
    with open(MD_PATH, encoding='utf-8') as f:
        md = f.read()
    sections = parse_md(md)
    js = emit_js(sections)
    with open(JS_OUT, 'w', encoding='utf-8') as f:
        f.write(js)
    total = sum(len(s['attrs']) for s in sections)
    print(f'  parsed {len(sections)} sections, {total} attributes')
    print(f'  wrote {JS_OUT} ({len(js)} chars)')
