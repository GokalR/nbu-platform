"""Region registry: 14 Uzbekistan viloyats + the path to their .md sources.

The router and ingest both read from this; runtime config (API key, model,
vector store id) lives in app.config.Settings.
"""
from pathlib import Path

RAG_DIR = Path(__file__).resolve().parent / "rag_single"

VILOYATS = [
    {"file": "1703_andijon-viloyati.md",       "name_latin": "Andijon viloyati",            "name_cyrillic": "Андижон вилояти",         "code": "1703"},
    {"file": "1706_buxoro-viloyati.md",        "name_latin": "Buxoro viloyati",             "name_cyrillic": "Бухоро вилояти",          "code": "1706"},
    {"file": "1708_jizzax-viloyati.md",        "name_latin": "Jizzax viloyati",             "name_cyrillic": "Жиззах вилояти",          "code": "1708"},
    {"file": "1710_qashqadaryo-viloyati.md",   "name_latin": "Qashqadaryo viloyati",        "name_cyrillic": "Қашқадарё вилояти",       "code": "1710"},
    {"file": "1712_navoiy-viloyati.md",        "name_latin": "Navoiy viloyati",             "name_cyrillic": "Навоий вилояти",          "code": "1712"},
    {"file": "1714_namangan-viloyati.md",      "name_latin": "Namangan viloyati",           "name_cyrillic": "Наманган вилояти",        "code": "1714"},
    {"file": "1718_samarqand-viloyati.md",     "name_latin": "Samarqand viloyati",          "name_cyrillic": "Самарқанд вилояти",       "code": "1718"},
    {"file": "1722_surxondaryo-viloyati.md",   "name_latin": "Surxondaryo viloyati",        "name_cyrillic": "Сурхондарё вилояти",      "code": "1722"},
    {"file": "1724_сирдарё-вилояти.md",        "name_latin": "Sirdaryo viloyati",           "name_cyrillic": "Сирдарё вилояти",         "code": "1724"},
    {"file": "1726_toshkent-shahri.md",        "name_latin": "Toshkent shahri",             "name_cyrillic": "Тошкент шаҳри",           "code": "1726"},
    {"file": "1727_toshkent-viloyati.md",      "name_latin": "Toshkent viloyati",           "name_cyrillic": "Тошкент вилояти",         "code": "1727"},
    {"file": "1730_fargona-viloyati.md",       "name_latin": "Farg'ona viloyati",           "name_cyrillic": "Фарғона вилояти",         "code": "1730"},
    {"file": "1733_xorazm-viloyati.md",        "name_latin": "Xorazm viloyati",             "name_cyrillic": "Хоразм вилояти",          "code": "1733"},
    {"file": "1735_qoraqalpogiston-respublikasi.md", "name_latin": "Qoraqalpog'iston Respublikasi", "name_cyrillic": "Қорақалпоғистон Республикаси", "code": "1735"},
]
