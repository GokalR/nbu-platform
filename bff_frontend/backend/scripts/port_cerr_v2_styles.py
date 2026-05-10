"""One-shot script: port nbu_platform/styles.css to a scoped cerr-v2-theme.css.

Every CSS selector is prefixed with `.cerr-v2-scope` so the prototype's design
applies only inside the cerr-v2 route wrapper. `:root`, `html`, `body` are
remapped to the scope class. Selectors inside @keyframes and @font-face stay
literal (they are step descriptors, not selectors).
"""
from __future__ import annotations

import re
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parents[3]  # repo root
SRC = ROOT / "nbu_platform" / "styles.css"
DST = ROOT / "bff_frontend" / "frontend" / "src" / "styles" / "cerr-v2-theme.css"

SCOPE = ".cerr-v2-scope"

with SRC.open("r", encoding="utf-8") as f:
    css = f.read()


def prefix_selector_list(sel: str) -> str:
    parts = []
    for raw in sel.split(","):
        s = raw.strip()
        if not s:
            continue
        if s in (":root", "html", "body"):
            parts.append(SCOPE)
            continue
        if s.startswith(":root "):
            parts.append(SCOPE + s[len(":root"):])
            continue
        if s == "html" or s.startswith("html ") or s.startswith("html.") or s.startswith("html["):
            parts.append(s.replace("html", SCOPE, 1))
            continue
        if s == "body" or s.startswith("body ") or s.startswith("body.") or s.startswith("body["):
            parts.append(s.replace("body", SCOPE, 1))
            continue
        parts.append(f"{SCOPE} {s}")
    return ", ".join(parts)


def is_rule_body_for(at_name: str) -> bool:
    name = at_name.lower()
    return name not in (
        "keyframes",
        "-webkit-keyframes",
        "-moz-keyframes",
        "font-face",
        "page",
        "counter-style",
        "property",
    )


def skip_string(s: str, j: int) -> int:
    quote = s[j]
    j += 1
    while j < len(s) and s[j] != quote:
        if s[j] == "\\" and j + 1 < len(s):
            j += 2
        else:
            j += 1
    return j + 1


def skip_comment(s: str, j: int) -> int:
    end = s.find("*/", j + 2)
    return end + 2 if end != -1 else len(s)


i = 0
n = len(css)
out: list[str] = []
atrule_stack: list[bool] = []  # True = body holds CSS rules; False = raw (keyframes etc.)

while i < n:
    c = css[i]
    if c.isspace():
        out.append(c)
        i += 1
        continue
    if c == "/" and i + 1 < n and css[i + 1] == "*":
        end = skip_comment(css, i)
        out.append(css[i:end])
        i = end
        continue
    if c == "}":
        out.append("}")
        i += 1
        if atrule_stack:
            atrule_stack.pop()
        continue
    if c == "@":
        m = re.match(r"@[\w-]+", css[i:])
        if not m:
            out.append(c)
            i += 1
            continue
        name = m.group(0)[1:]
        j = i
        depth_paren = 0
        while j < n:
            ch = css[j]
            if ch in ('"', "'"):
                j = skip_string(css, j)
                continue
            if ch == "(":
                depth_paren += 1
                j += 1
                continue
            if ch == ")":
                depth_paren -= 1
                j += 1
                continue
            if depth_paren == 0 and ch in (";", "{"):
                break
            j += 1
        prelude = css[i:j]
        if j >= n or css[j] == ";":
            out.append(prelude)
            if j < n:
                out.append(css[j])
                i = j + 1
            else:
                i = j
            continue
        out.append(prelude)
        out.append("{")
        i = j + 1
        atrule_stack.append(is_rule_body_for(name))
        continue
    in_raw = bool(atrule_stack) and not atrule_stack[-1]
    if in_raw:
        # @keyframes step rules — keep as-is.
        j = i
        depth_paren = 0
        while j < n:
            ch = css[j]
            if ch == "(":
                depth_paren += 1
                j += 1
                continue
            if ch == ")":
                depth_paren -= 1
                j += 1
                continue
            if depth_paren == 0 and ch == "{":
                break
            j += 1
        out.append(css[i:j])
        out.append("{")
        i = j + 1
        depth = 1
        k = i
        while k < n and depth > 0:
            ch = css[k]
            if ch in ('"', "'"):
                k = skip_string(css, k)
                continue
            if ch == "/" and k + 1 < n and css[k + 1] == "*":
                k = skip_comment(css, k)
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break
            k += 1
        out.append(css[i:k])
        out.append("}")
        i = k + 1
        continue
    # Regular rule: parse selector up to '{', then copy declaration body verbatim
    # until the matching '}'. The prototype CSS uses no nesting, so this is safe.
    j = i
    depth_paren = 0
    while j < n:
        ch = css[j]
        if ch in ('"', "'"):
            j = skip_string(css, j)
            continue
        if ch == "/" and j + 1 < n and css[j + 1] == "*":
            j = skip_comment(css, j)
            continue
        if ch == "(":
            depth_paren += 1
            j += 1
            continue
        if ch == ")":
            depth_paren -= 1
            j += 1
            continue
        if depth_paren == 0 and ch == "{":
            break
        j += 1
    sel_text = css[i:j].strip()
    out.append(prefix_selector_list(sel_text))
    out.append(" {")
    # Copy declaration body verbatim to the matching '}'.
    body_start = j + 1
    depth = 1
    k = body_start
    while k < n and depth > 0:
        ch = css[k]
        if ch in ('"', "'"):
            k = skip_string(css, k)
            continue
        if ch == "/" and k + 1 < n and css[k + 1] == "*":
            k = skip_comment(css, k)
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
        k += 1
    out.append(css[body_start:k])
    out.append("}")
    i = k + 1

result = "".join(out)

header = (
    "/* Ported from nbu_platform/styles.css by app/scripts/port_cerr_v2_styles.py.\n"
    f" * Every selector is prefixed with `{SCOPE}` so the prototype design only\n"
    " * applies inside the cerr-v2 route wrapper. Tokens that were on :root are\n"
    " * now scoped to the wrapper.\n"
    " */\n\n"
)

DST.parent.mkdir(parents=True, exist_ok=True)
DST.write_text(header + result, encoding="utf-8")
print(f"wrote {DST}")
print(f"chars: {len(result)}, lines: {result.count(chr(10))}")
