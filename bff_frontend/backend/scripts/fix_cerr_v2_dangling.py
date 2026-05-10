"""Strip dangling declaration blocks from cerr-v2-theme.css.

The prototype source contains stray declaration blocks like:
    }
    height: 26px;
    overflow: hidden;
    }
The CSS porter prefixed these as `.cerr-v2-scope height: 26px;` which is invalid.
We detect them in the ported output and remove the entire fake rule.
"""
from __future__ import annotations
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DST = r"c:\Users\User\Downloads\myfolder\NBU\Projects\nbu_ai_hub\bff_frontend\frontend\src\styles\cerr-v2-theme.css"

with open(DST, "r", encoding="utf-8") as f:
    css = f.read()

n = len(css)
out: list[str] = []
i = 0
depth = 0
removed = 0

BACKSLASH = chr(92)


def skip_string(j: int) -> int:
    q = css[j]
    j += 1
    while j < n and css[j] != q:
        if css[j] == BACKSLASH and j + 1 < n:
            j += 2
        else:
            j += 1
    return j + 1


def skip_comment(j: int) -> int:
    e = css.find("*/", j + 2)
    return e + 2 if e != -1 else n


while i < n:
    c = css[i]
    if c in ('"', "'"):
        end = skip_string(i)
        out.append(css[i:end])
        i = end
        continue
    if c == "/" and i + 1 < n and css[i + 1] == "*":
        end = skip_comment(i)
        out.append(css[i:end])
        i = end
        continue
    if depth == 0 and css[i:i + 15] == ".cerr-v2-scope ":
        # Capture the candidate "selector" until '{' or ';' at depth 0.
        j = i
        while j < n and css[j] != "{" and css[j] != ";":
            if css[j] in ('"', "'"):
                j = skip_string(j); continue
            if css[j] == "/" and j + 1 < n and css[j + 1] == "*":
                j = skip_comment(j); continue
            j += 1
        sel = css[i:j].strip()
        if j < n and css[j] == ";":
            # `.cerr-v2-scope name: value;` — porter mistakenly prefixed a
            # dangling declaration. Skip this stray declaration and continue
            # eating subsequent declarations until the next '}' (which closes
            # the phantom rule body in the source).
            k = j + 1
            while k < n:
                if css[k] in ('"', "'"):
                    k = skip_string(k); continue
                if css[k] == "/" and k + 1 < n and css[k + 1] == "*":
                    k = skip_comment(k); continue
                if css[k] == "}":
                    k += 1
                    break
                k += 1
            i = k
            removed += 1
            continue
        out.append(c)
        i += 1
        continue
    if c == "{":
        depth += 1
    elif c == "}":
        depth -= 1
    out.append(c)
    i += 1

result = "".join(out)
with open(DST, "w", encoding="utf-8") as f:
    f.write(result)
print(f"removed {removed} dangling blocks")
