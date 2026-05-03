"""Generate backend/app/models_gm.py from the 3 GM MD files.

Output is a single SQLAlchemy module declaring four tables:
  - gm_entities  (lookup: country/region/city display names + nesting)
  - gm_country   (174 columns)
  - gm_region    (~192 columns)
  - gm_city      (208 columns)

Pipeline:
  golden_mart_*.xlsx
   → goldenmarts/_to_md.py            → GM_*.md
   → goldenmarts/_md_to_schema_js.py  → frontend/src/data/goldenMart/citySchema.js
   → goldenmarts/_md_to_sqlalchemy.py → backend/app/models_gm.py        ← THIS

Whenever admins edit the Excel, run all three. The schema stays consistent
across xlsx, MD, JS and Python.

Column types: numeric units (млрд сум, чел., %, ...) → Numeric;
text-ish units (текст, да/нет, выс/ср/низ) → Text.

Usage: PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_sqlalchemy.py
"""
from __future__ import annotations
import os
import re

HERE = os.path.dirname(__file__)
LEVELS = [
    ('country', os.path.join(HERE, 'GM_country.md'), 'gm_country'),
    ('region',  os.path.join(HERE, 'GM_region.md'),  'gm_region'),
    ('city',    os.path.join(HERE, 'GM_city.md'),    'gm_city'),
]
OUT_PATH = os.path.join(HERE, '..', 'backend', 'app', 'models_gm.py')

TEXT_UNITS = {
    'текст', 'да/нет',
    'высокий/средний/низкий',
    'выс/ср/низ',
}

# Enum fields — stored as language-agnostic codes ('city', 'no', 'high'),
# translated via gmEnum.* i18n keys in the UI. NOT bilingual (one column).
# Must match frontend/src/data/goldenMart/enums.js ENUM_FIELDS.
ENUM_FIELDS = {
    's1_2',                                         # Тип объекта (city|tuman)
    's1_3',                                         # Админ. центр (yes|no)
    's21_2', 's21_5', 's21_8', 's21_11', 's21_14',  # Priority for problems 1..5
}


def parse_md(path: str):
    with open(path, encoding='utf-8') as f:
        md = f.read()
    sections = []
    cur = None
    in_table = False
    for line in md.splitlines():
        s = line.strip()
        m = re.match(r'^##\s+(\d+)\.\s+(.+)$', s)
        if m:
            cur = {'n': int(m.group(1)), 'attrs': []}
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
        if len(cells) < 2 or cells[0] in ('Показатель',):
            continue
        label = cells[0]
        unit  = cells[1] if len(cells) > 1 else ''
        idx = len(cur['attrs']) + 1
        cur['attrs'].append({
            'label': label,
            'unit': unit,
            'key': f's{cur["n"]}_{idx}',
        })
    return sections


def col_type(unit: str) -> str:
    return 'Text' if unit in TEXT_UNITS else 'Numeric'


def emit_class(class_name: str, table_name: str, sections: list, level: str) -> str:
    out = []
    out.append(f'class {class_name}(Base):')
    out.append(f'    """Golden Mart — {level} level. Auto-generated from GM_{level}.md."""')
    out.append(f'    __tablename__ = {table_name!r}')
    out.append('')
    out.append('    entity_key = Column(Text, primary_key=True)')
    out.append('    year = Column(Integer, primary_key=True)')
    if level == 'city':
        out.append('    region_key = Column(Text, nullable=True, index=True)')
    out.append('    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)')
    out.append('    updated_by = Column(UUID(as_uuid=True), nullable=True)')
    out.append('')
    for sec in sections:
        out.append(f'    # ── §{sec["n"]} ({len(sec["attrs"])} fields) ──')
        for attr in sec['attrs']:
            t = col_type(attr['unit'])
            key = attr['key']
            out.append(f'    {key} = Column({t}, nullable=True)  # {attr["label"]} ({attr["unit"]})')
            # Free-form text (unit='текст' AND not an enum field) → bilingual:
            # add a companion `_uz` column. Admin form will render two inputs;
            # detail view picks based on locale.
            if attr['unit'] == 'текст' and key not in ENUM_FIELDS:
                out.append(f'    {key}_uz = Column(Text, nullable=True)  # {attr["label"]} (UZ)')
        out.append('')
    return '\n'.join(out)


def emit_module(by_level):
    out = []
    out.append('"""Golden Mart database models — AUTO-GENERATED.')
    out.append('')
    out.append('Source of truth: goldenmarts/GM_country.md, GM_region.md, GM_city.md')
    out.append('(themselves regenerated from goldenmarts/golden_mart_*.xlsx).')
    out.append('')
    out.append('To regenerate this file:')
    out.append('  PYTHONIOENCODING=utf-8 python goldenmarts/_md_to_sqlalchemy.py')
    out.append('')
    out.append('Tables:')
    out.append('  gm_entities — lookup: which countries / regions / cities exist')
    out.append('  gm_country  — country-level GM data (one row per (entity, year))')
    out.append('  gm_region   — region-level GM data (one row per (entity, year))')
    out.append('  gm_city     — city/tuman-level GM data (one row per (entity, year))')
    out.append('"""')
    out.append('')
    out.append('from datetime import datetime, timezone')
    out.append('')
    out.append('from sqlalchemy import (')
    out.append('    Boolean, Column, DateTime, Integer, Numeric, Text,')
    out.append(')')
    out.append('from sqlalchemy.dialects.postgresql import UUID')
    out.append('')
    out.append('from .db_async import BaseAsync as Base')
    out.append('')
    out.append('')
    out.append('def utcnow():')
    out.append('    return datetime.now(timezone.utc)')
    out.append('')
    out.append('')
    out.append('class GmEntity(Base):')
    out.append('    """Lookup for entity display names + nesting (parent_key)."""')
    out.append("    __tablename__ = 'gm_entities'")
    out.append('')
    out.append('    key = Column(Text, primary_key=True)            # \'qoqon_city\', \'fergana_region\', \'uzbekistan\'')
    out.append("    level = Column(Text, nullable=False)             # 'country' | 'region' | 'city'")
    out.append("    parent_key = Column(Text, nullable=True)         # 'fergana_region' for cities")
    out.append('    name_ru = Column(Text, nullable=False)')
    out.append('    name_uz = Column(Text, nullable=False)')
    out.append("    iso_kind = Column(Text, nullable=True)           # 'shahar' | 'tuman' | 'viloyat'")
    out.append('    active = Column(Boolean, default=True)')
    out.append('    created_at = Column(DateTime(timezone=True), default=utcnow)')
    out.append('')
    out.append('')
    for level, sections in by_level.items():
        class_name = 'Gm' + level.capitalize()
        table_name = f'gm_{level}'
        out.append(emit_class(class_name, table_name, sections, level))
        out.append('')
    return '\n'.join(out)


if __name__ == '__main__':
    by_level = {}
    for level, md_path, _table in LEVELS:
        sections = parse_md(md_path)
        by_level[level] = sections
        n_attrs = sum(len(s['attrs']) for s in sections)
        print(f'  {level}: {len(sections)} sections, {n_attrs} fields')
    src = emit_module(by_level)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write(src)
    print(f'  wrote {OUT_PATH} ({len(src)} chars)')
