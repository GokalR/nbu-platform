"""
Fix ALL Uzbek apostrophes in uz: blocks.

Replace every ASCII apostrophe (U+0027) inside string literals within uz: blocks
with Unicode ʻ (U+02BB). In Uzbek Latin text, the apostrophe is ALWAYS a letter
modifier (oʻ, gʻ, maʻlumot, mablagʻ), never punctuation.

Strategy: find strings in uz: blocks, replace ' with ʻ inside the string content.
"""
import re
import os

UZ_APOST = '\u02bb'  # ʻ

BASE = r'c:\Users\User\Downloads\Projects\NBU-clean\frontend\src'
DIRS = [
    'views/regionalStrategist',
    'components/regionalStrategist',
    'data/regionalStrategist',
]

def replace_apostrophes_in_strings(line):
    """Replace ASCII ' with ʻ inside string literals on this line.
    Handles single-quoted, double-quoted, and backtick strings."""
    result = []
    i = 0
    while i < len(line):
        ch = line[i]
        # Double-quoted or backtick string — replace ' inside
        if ch in ('"', '`'):
            quote = ch
            result.append(ch)
            i += 1
            while i < len(line):
                if line[i] == '\\':
                    result.append(line[i:i+2])
                    i += 2
                    continue
                if line[i] == quote:
                    result.append(line[i])
                    i += 1
                    break
                if line[i] == "'":
                    result.append(UZ_APOST)
                else:
                    result.append(line[i])
                i += 1
        # Single-quoted string — need special handling because ' is both delimiter and content
        elif ch == "'":
            # Collect the full single-quoted string, treating Uzbek apostrophes correctly
            # A Uzbek apostrophe is ' preceded by a letter (part of the word)
            # A string delimiter ' is preceded by: start, comma, space, [, (, :, or other punctuation
            j = i + 1
            content_chars = []
            while j < len(line):
                if line[j] == '\\':
                    content_chars.append(line[j:j+2])
                    j += 2
                    continue
                if line[j] == "'":
                    # Is this the end of the string or a Uzbek apostrophe?
                    # Check: if preceded by a letter AND followed by something that
                    # continues (letter or space+letter within the same string)
                    prev_is_letter = content_chars and content_chars[-1][-1:].isalpha()
                    # Look ahead: what comes after this '?
                    after = line[j+1:j+2]

                    if prev_is_letter and after and after not in (',', ']', ')', '}', ';', '\n', ' ', ':'):
                        # Followed by a letter = definitely Uzbek apostrophe inside string
                        content_chars.append(UZ_APOST)
                        j += 1
                        continue
                    elif prev_is_letter and after == ' ':
                        # Could be end of string or Uzbek apostrophe at end of word
                        # e.g., 'mablag' etishmaydi' — the first ' after mablag is Uzbek
                        # Look further: if after the space there's more text before the next
                        # unescaped ', it's likely still inside the string
                        # Heuristic: look for the next ' and see if the content makes sense
                        rest = line[j+1:]
                        next_quote = rest.find("'")
                        if next_quote > 0:
                            between = rest[:next_quote]
                            # If between contains only normal text (letters, spaces, punctuation)
                            # and ends in a way that looks like end of string, treat this as Uzbek
                            after_next = rest[next_quote+1:next_quote+2]
                            if after_next in (',', ']', ')', '}', '', ';', ' '):
                                # The NEXT quote is the real end delimiter
                                content_chars.append(UZ_APOST)
                                j += 1
                                continue
                        # Otherwise this is the end of the string
                        break
                    else:
                        # End of string
                        break
                else:
                    content_chars.append(line[j])
                    j += 1

            # Build the string with quotes
            content = ''.join(content_chars)
            # Replace any remaining ASCII apostrophes in the content with Unicode
            content = content.replace("'", UZ_APOST)
            result.append("'")
            result.append(content)
            if j < len(line):
                result.append("'")
                i = j + 1
            else:
                # Unclosed string
                i = j
        else:
            result.append(ch)
            i += 1

    return ''.join(result)


def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    new_lines = []
    in_uz_block = False
    brace_depth = 0
    changed = False

    for line in lines:
        stripped = line.strip()

        if re.search(r'\buz\s*:', stripped) or re.search(r"'uz'\s*:", stripped) or re.search(r'"uz"\s*:', stripped):
            in_uz_block = True
            open_b = stripped.count('{') + stripped.count('[')
            close_b = stripped.count('}') + stripped.count(']')
            brace_depth = open_b - close_b

            if "'" in line:
                new_line = replace_apostrophes_in_strings(line)
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

            if "'" in line:
                new_line = replace_apostrophes_in_strings(line)
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


FILES = []
for d in DIRS:
    dirpath = os.path.join(BASE, d)
    for root, dirs, files in os.walk(dirpath):
        for fn in files:
            if fn.endswith(('.vue', '.js')):
                FILES.append(os.path.join(root, fn))

processed = 0
for path in FILES:
    if process_file(path):
        processed += 1
        rel = os.path.relpath(path, BASE)
        print(f'  FIXED: {rel}')
    else:
        rel = os.path.relpath(path, BASE)
        print(f'  no change: {rel}')

print(f'\nDone. {processed} files fixed.')
