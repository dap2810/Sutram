#!/usr/bin/env python3
"""Generate the Sutram standard-library reference from module sources.

Reads lib/*.smlib, extracting per module:
  - module name (from filename)
  - header description (leading # comment block)
  - per function: name, signature, one-line description (the # comment
    immediately preceding the prakriya, if any)

Writes docs/sutram-stdlib.html. Re-run after changing lib/.

Usage: python3 tools/gen_stdlib_ref.py (no arguments)
"""

import os
import re
import html

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIBDIR = os.path.join(REPO, "lib")
OUT = os.path.join(REPO, "docs", "sutram-stdlib.html")


def parse_module(path):
    """Return (header_desc, [(name, signature, desc), ...])."""
    with open(path) as f:
        lines = f.read().splitlines()

    header = []
    functions = []
    pending_comment = []
    in_header = True

    for line in lines:
        s = line.strip()
        if s.startswith("#"):
            text = s[1:].strip()
            if in_header:
                header.append(text)
            else:
                pending_comment.append(text)
            continue
        if not s:
            if in_header and header:
                pass  # blank line inside header block is fine
            elif not in_header:
                pending_comment = []
            continue
        in_header = False
        m = re.match(r"prakriya\s+([A-Za-z_][A-Za-z0-9_]*)\s*(\(.*\))?", s)
        if m:
            name = m.group(1)
            sig = name + (m.group(2) or "()")
            desc = " ".join(pending_comment)
            functions.append((name, sig, desc))
        pending_comment = []

    # header: skip filename title lines, keep the descriptive part
    desc_lines = [l for l in header if l and not l.startswith("lib/")]
    return " ".join(desc_lines), functions


def main():
    modules = []
    for fn in sorted(os.listdir(LIBDIR)):
        if not fn.endswith(".smlib"):
            continue
        mod = fn[:-6]
        header, funcs = parse_module(os.path.join(LIBDIR, fn))
        modules.append((mod, header, funcs))

    total = sum(len(f) for _, _, f in modules)

    parts = []
    parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Sutram Standard Library Reference</title>
<style>
body{font-family:Georgia,serif;max-width:900px;margin:2em auto;padding:0 1em;color:#222}
h1{border-bottom:2px solid #333}
h2{margin-top:2em;color:#444;border-bottom:1px solid #ccc}
table{border-collapse:collapse;width:100%;margin:1em 0}
th,td{border:1px solid #ccc;padding:.4em .6em;text-align:left;vertical-align:top}
th{background:#f4f4f4}
code{font-family:Menlo,Consolas,monospace;background:#f6f6f6;padding:0 .2em}
.mod-desc{color:#555;font-style:italic}
footer{margin-top:3em;color:#888;font-size:.9em}
</style>
</head>
<body>
<h1>Sutram Standard Library Reference</h1>
<p>Generated from <code>lib/*.smlib</code> by <code>tools/gen_stdlib_ref.py</code>.
Do not edit by hand.</p>
""")
    # index
    parts.append("<h2>Modules</h2>\n<ul>\n")
    for mod, header, funcs in modules:
        parts.append(
            f'<li><a href="#{mod}"><code>{html.escape(mod)}</code></a>'
            f" — {len(funcs)} functions</li>\n")
    parts.append("</ul>\n")

    for mod, header, funcs in modules:
        parts.append(f'<h2 id="{html.escape(mod)}"><code>{html.escape(mod)}</code></h2>\n')
        if header:
            parts.append(f'<p class="mod-desc">{html.escape(header)}</p>\n')
        parts.append("<table>\n<tr><th>Function</th><th>Description</th></tr>\n")
        for name, sig, desc in funcs:
            parts.append(
                f"<tr><td><code>{html.escape(sig)}</code></td>"
                f"<td>{html.escape(desc)}</td></tr>\n")
        parts.append("</table>\n")

    parts.append(
        f"<footer>{len(modules)} modules, {total} functions. "
        "Generated from library sources.</footer>\n</body>\n</html>\n")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        f.write("".join(parts))
    print(f"Wrote {OUT}: {len(modules)} modules, {total} functions")


if __name__ == "__main__":
    main()
