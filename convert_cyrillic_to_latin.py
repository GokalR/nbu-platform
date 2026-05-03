"""
Convert Cyrillic Uzbek text to Latin Uzbek in all Regional Strategist files.
Only converts text inside uz: { } blocks or uz-keyed values.
"""
import re
import os

# Cyrillic-to-Latin Uzbek mapping
MAPPING = {
    'Ў': "O'", 'ў': "o'",
    'Қ': 'Q', 'қ': 'q',
    'Ғ': "G'", 'ғ': "g'",
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
    'Ъ': "'", 'ъ': "'",
    'Ы': 'I', 'ы': 'i',
    'Ь': '', 'ь': '',
    'Э': 'E', 'э': 'e',
    'Ю': 'Yu', 'ю': 'yu',
    'Я': 'Ya', 'я': 'ya',
}

# Multi-char sequences that need special handling (ш before с, etc.)
# Process longer mappings first
SORTED_KEYS = sorted(MAPPING.keys(), key=len, reverse=True)

def has_cyrillic(text):
    """Check if text contains Cyrillic characters."""
    return bool(re.search(r'[\u0400-\u04FF]', text))

def transliterate(text):
    """Convert Cyrillic Uzbek to Latin Uzbek."""
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

def process_file(filepath):
    """Process a single file, converting Cyrillic Uzbek in uz: sections."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if not has_cyrillic(content):
        return False

    original = content

    # Strategy: find all string literals that contain Cyrillic and are in uz context
    # We'll use a line-by-line approach looking for uz: blocks

    lines = content.split('\n')
    in_uz_block = False
    brace_depth = 0
    new_lines = []
    changed = False

    for line in lines:
        stripped = line.strip()

        # Detect entering a uz: block (various patterns)
        if re.search(r'\buz\s*:', stripped) or re.search(r"'uz'\s*:", stripped) or re.search(r'"uz"\s*:', stripped):
            in_uz_block = True
            # Count braces on this line
            open_b = stripped.count('{') + stripped.count('[')
            close_b = stripped.count('}') + stripped.count(']')
            brace_depth = open_b - close_b

            # If uz value is on the same line (e.g., uz: 'текст')
            if has_cyrillic(line):
                # Find the string values and transliterate them
                new_line = transliterate_strings_in_line(line)
                if new_line != line:
                    changed = True
                    line = new_line

            if brace_depth <= 0:
                in_uz_block = False
                brace_depth = 0
        elif in_uz_block:
            open_b = stripped.count('{') + stripped.count('[')
            close_b = stripped.count('}') + stripped.count(']')
            brace_depth += open_b - close_b

            if has_cyrillic(line):
                new_line = transliterate_strings_in_line(line)
                if new_line != line:
                    changed = True
                    line = new_line

            if brace_depth <= 0:
                in_uz_block = False
                brace_depth = 0

        new_lines.append(line)

    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        return True
    return False

def transliterate_strings_in_line(line):
    """Transliterate Cyrillic text within string literals in a line."""
    # Match strings in single quotes, double quotes, or backticks
    def replace_match(m):
        quote = m.group(1)
        text = m.group(2)
        if has_cyrillic(text):
            return quote + transliterate(text) + quote
        return m.group(0)

    # Handle single-quoted strings
    line = re.sub(r"(')((?:[^'\\]|\\.)*?)(')", lambda m: m.group(1) + (transliterate(m.group(2)) if has_cyrillic(m.group(2)) else m.group(2)) + m.group(3), line)
    # Handle double-quoted strings
    line = re.sub(r'(")((?:[^"\\]|\\.)*?)(")', lambda m: m.group(1) + (transliterate(m.group(2)) if has_cyrillic(m.group(2)) else m.group(2)) + m.group(3), line)
    # Handle backtick strings
    line = re.sub(r'(`)((?:[^`\\]|\\.)*?)(`)', lambda m: m.group(1) + (transliterate(m.group(2)) if has_cyrillic(m.group(2)) else m.group(2)) + m.group(3), line)

    return line


# Files to process
BASE = r'c:\Users\User\Downloads\Projects\NBU-clean\frontend\src'
FILES = [
    # Views
    'views/regionalStrategist/RsHomeView.vue',
    'views/regionalStrategist/RsBusinessTestView.vue',
    'views/regionalStrategist/steps/RsStep0PathSelect.vue',
    'views/regionalStrategist/steps/RsStep1Profile.vue',
    'views/regionalStrategist/steps/RsStep2Finance.vue',
    'views/regionalStrategist/steps/RsStep3Coaching.vue',
    'views/regionalStrategist/steps/RsStep4Analyzing.vue',
    'views/regionalStrategist/steps/RsStep5Results.vue',
    # Components
    'components/regionalStrategist/RsClaudeAnalysis.vue',
    'components/regionalStrategist/RsExcelUpload.vue',
    'components/regionalStrategist/RsFerganaHeatmap.vue',
    'components/regionalStrategist/RsHeader.vue',
    'components/regionalStrategist/RsInputSummary.vue',
    'components/regionalStrategist/RsMargilanHeatmap.vue',
    'components/regionalStrategist/RsRecommendationCard.vue',
    'components/regionalStrategist/RsScoreBreakdown.vue',
    'components/regionalStrategist/RsSelectField.vue',
    # Data
    'data/regionalStrategist/cities.js',
    'data/regionalStrategist/credit-products.js',
    'data/regionalStrategist/demo-seeds.js',
    'data/regionalStrategist/fergana-context.js',
    'data/regionalStrategist/fergana-districts.js',
    'data/regionalStrategist/fergana-enterprises.js',
    'data/regionalStrategist/margilan-paths.js',
    'data/regionalStrategist/regions.js',
    'data/regionalStrategist/scoring.js',
    # I18n
    'views/regionalStrategist/steps/rs-step1-i18n.js',
    'views/regionalStrategist/steps/rs-step2-i18n.js',
    'views/regionalStrategist/steps/rs-step5-i18n.js',
]

processed = 0
for f in FILES:
    path = os.path.join(BASE, f)
    if os.path.exists(path):
        if process_file(path):
            processed += 1
            print(f'  CONVERTED: {f}')
        else:
            print(f'  no change: {f}')
    else:
        print(f'  NOT FOUND: {f}')

print(f'\nDone. {processed} files converted.')
