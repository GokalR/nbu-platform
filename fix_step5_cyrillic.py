"""
Convert Cyrillic Uzbek text to Latin Uzbek in RsStep5Results.vue.
Targets only the 'uz' branches of ternary expressions like:
  L === 'uz' ? 'Cyrillic Uzbek' : 'Russian'
  lang === 'uz' ? 'Cyrillic Uzbek' : 'Russian'

Does NOT touch the ru: section or Russian text.
"""
import re

MAPPING = {
    'Ў': "Oʻ", 'ў': "oʻ",
    'Қ': 'Q', 'қ': 'q',
    'Ғ': "Gʻ", 'ғ': "gʻ",
    'Ҳ': 'H', 'ҳ': 'h',
    'А': 'A', 'а': 'a',
    'Б': 'B', 'б': 'b',
    'В': 'V', 'в': 'v',
    'Г': 'G', 'г': 'g',
    'Д': 'D', 'д': 'd',
    'Ё': 'Yo', 'ё': 'yo',
    'Е': 'E', 'е': 'e',
    'Ж': 'J', 'ж': 'j',
    'З': 'Z', 'з': 'z',
    'И': 'I', 'и': 'i',
    'Й': 'Y', 'й': 'y',
    'К': 'K', 'к': 'k',
    'Л': 'L', 'л': 'l',
    'М': 'M', 'м': 'm',
    'Н': 'N', 'н': 'n',
    'О': 'O', 'о': 'o',
    'П': 'P', 'п': 'p',
    'Р': 'R', 'р': 'r',
    'С': 'S', 'с': 's',
    'Т': 'T', 'т': 't',
    'У': 'U', 'у': 'u',
    'Ф': 'F', 'ф': 'f',
    'Х': 'X', 'х': 'x',
    'Ц': 'Ts', 'ц': 'ts',
    'Ч': 'Ch', 'ч': 'ch',
    'Ш': 'Sh', 'ш': 'sh',
    'Щ': 'Sh', 'щ': 'sh',
    'Ъ': "ʻ", 'ъ': "ʻ",
    'Ы': 'I', 'ы': 'i',
    'Ь': '', 'ь': '',
    'Э': 'E', 'э': 'e',
    'Ю': 'Yu', 'ю': 'yu',
    'Я': 'Ya', 'я': 'ya',
}

SORTED_KEYS = sorted(MAPPING.keys(), key=len, reverse=True)

def has_cyrillic(text):
    return bool(re.search(r'[\u0400-\u04FF]', text))

def transliterate(text):
    result = []
    i = 0
    while i < len(text):
        matched = False
        for key in SORTED_KEYS:
            if text[i:i+len(key)] == key:
                result.append(MAPPING[key])
                i += len(key)
                matched = True
                break
        if not matched:
            result.append(text[i])
            i += 1
    return ''.join(result)

def transliterate_strings_in_line(line):
    """Transliterate Cyrillic in string literals on a single line."""
    def repl(m):
        q1, text, q2 = m.group(1), m.group(2), m.group(3)
        if has_cyrillic(text):
            return q1 + transliterate(text) + q2
        return m.group(0)

    line = re.sub(r"(')((?:[^'\\]|\\.)*?)(')", repl, line)
    line = re.sub(r'(")((?:[^"\\]|\\.)*?)(")', repl, line)
    line = re.sub(r'(`)((?:[^`\\]|\\.)*?)(`)', repl, line)
    return line

filepath = r'c:\Users\User\Downloads\Projects\NBU-clean\frontend\src\views\regionalStrategist\steps\RsStep5Results.vue'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# ── Strategy 1: uz ternaries ──
# Match: (L === 'uz' ? ')(quote)(Cyrillic text)(quote)
def replace_cyrillic_in_uz_ternary(m):
    prefix = m.group(1)
    quote = m.group(2)
    uz_text = m.group(3)
    suffix = m.group(4)
    if has_cyrillic(uz_text):
        uz_text = transliterate(uz_text)
    return prefix + quote + uz_text + suffix

# Single-quoted uz ternary
content = re.sub(
    r"((?:lang|L)\s*===?\s*'uz'\s*\?\s*)(')([^']*?[\u0400-\u04FF][^']*?)(')",
    replace_cyrillic_in_uz_ternary,
    content
)
# Double-quoted uz ternary
content = re.sub(
    r'((?:lang|L)\s*===?\s*\'uz\'\s*\?\s*)(")([^"]*?[\u0400-\u04FF][^"]*?)(")',
    replace_cyrillic_in_uz_ternary,
    content
)
# Backtick uz ternary
content = re.sub(
    r"((?:lang|L)\s*===?\s*'uz'\s*\?\s*)(`)([^`]*?[\u0400-\u04FF][^`]*?)(`)",
    replace_cyrillic_in_uz_ternary,
    content
)

# ── Strategy 2: uz: { ... } section in FERGANA_KINDERGARTEN_OVERRIDE ──
# The uz: section (lines ~95-157) should already be Latin from previous work,
# but let's also handle the top-level data objects if any remain.
lines = content.split('\n')
new_lines = []
in_uz_section = False
brace_depth = 0

for i, line in enumerate(lines):
    stripped = line.strip()

    if re.search(r"^\s*uz:\s*\{", stripped) or re.search(r"^\s*uz:\s*\[", stripped):
        in_uz_section = True
        brace_depth = stripped.count('{') + stripped.count('[') - stripped.count('}') - stripped.count(']')
        if has_cyrillic(line):
            line = transliterate_strings_in_line(line)
        if brace_depth <= 0:
            in_uz_section = False
    elif in_uz_section:
        brace_depth += stripped.count('{') + stripped.count('[') - stripped.count('}') - stripped.count(']')
        if has_cyrillic(line):
            line = transliterate_strings_in_line(line)
        if brace_depth <= 0:
            in_uz_section = False

    new_lines.append(line)

content = '\n'.join(new_lines)

# ── Verify ──
remaining_uz = re.findall(r"(?:lang|L)\s*===?\s*'uz'\s*\?\s*'([^']*[\u0400-\u04FF][^']*)'", content)
if remaining_uz:
    print(f"WARNING: {len(remaining_uz)} remaining Cyrillic strings in uz ternaries:")
    for r in remaining_uz[:10]:
        print(f"  {r[:80]}")

# Count remaining Cyrillic lines (should only be in ru: sections and Russian branches)
remaining_count = 0
for line in content.split('\n'):
    if has_cyrillic(line):
        remaining_count += 1
print(f"Lines still containing Cyrillic (should be ru: sections only): {remaining_count}")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done converting RsStep5Results.vue")
