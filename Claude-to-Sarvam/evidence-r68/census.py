#!/usr/bin/env python3
"""R68 census: every write into a buffer in lib/*.smlib, by prakriya, with the buffer's origin.

For each prakriya: its signature, the comment block above it (the contract), every
`vitti x = <param>` alias, every own allocation `vitti x = nirmmita(...)`, every declared
`mala x[N]` / `kosh x[N]`, and every write site `x[idx] = ...` or `akshar_rakh(x, idx, ...)`
with the enclosing `yavat`/`yadi` headers (loop bounds) so that a reader can judge the
maximum index against the capacity. Output: one text block per prakriya, to stdout.
"""
import re, sys, glob, os

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/sutram"
FILES = sorted(glob.glob(os.path.join(ROOT, "lib", "*.smlib")))
only = sys.argv[2:]

W_CELL = re.compile(r'^\s*([A-Za-z_]\w*)\[([^\]]+)\]\s*=(?!=)\s*(.*)$')
W_BYTE = re.compile(r'^\s*akshar_rakh\(\s*([A-Za-z_]\w*)\s*,\s*([^,]+),')
# also writes through kosh_push etc. are bounds-checked by the compiler; not listed
ALIAS = re.compile(r'^\s*vitti\s+([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)\s*$')
OWN = re.compile(r'^\s*vitti\s+([A-Za-z_]\w*)\s*=\s*nirmmita\((.*)\)\s*$')
OWN2 = re.compile(r'^\s*([A-Za-z_]\w*)\s*=\s*nirmmita\((.*)\)\s*$')
DECL = re.compile(r'^\s*(mala|kosh)\s+([A-Za-z_]\w*)\[([^\]]*)\]')
HDR = re.compile(r'^\s*(yavat|yadi|anyatha|anya)\b(.*)$')
PRAK = re.compile(r'^prakriya\s+([A-Za-z_]\w*)\s*\(([^)]*)\)')

def strip_comment(line):
    # a '#' inside a string literal is rare in lib; good enough for a census
    q = False; out = []
    for ch in line:
        if ch == '"': q = not q
        if ch == '#' and not q: break
        out.append(ch)
    return "".join(out)

total_sites = 0
total_fn = 0
for f in FILES:
    mod = os.path.basename(f)[:-6]
    if only and mod not in only: continue
    lines = open(f).read().split("\n")
    i = 0
    n = len(lines)
    while i < n:
        m = PRAK.match(lines[i])
        if not m:
            i += 1; continue
        name, params = m.group(1), [p.strip() for p in m.group(2).split(",") if p.strip()]
        # contract: contiguous comment lines right above
        j = i - 1; contract = []
        while j >= 0 and lines[j].startswith("#"):
            contract.append(lines[j]); j -= 1
        contract.reverse()
        # body: until a line that is exactly "}" at column 0
        k = i + 1; body = []
        while k < n and not lines[k].startswith("}"):
            body.append((k + 1, lines[k])); k += 1
        body_end = k
        aliases = {}; owns = {}; decls = {}; sites = []
        stack = []  # (indent, header)
        for ln, raw in body:
            code = strip_comment(raw)
            if not code.strip(): continue
            ind = len(code) - len(code.lstrip())
            while stack and stack[-1][0] >= ind:
                stack.pop()
            h = HDR.match(code)
            if h:
                stack.append((ind, code.strip()))
            a = ALIAS.match(code)
            if a: aliases[a.group(1)] = a.group(2)
            o = OWN.match(code) or OWN2.match(code)
            if o: owns[o.group(1)] = o.group(2)
            d = DECL.match(code)
            if d: decls[d.group(2)] = (d.group(1), d.group(3))
            w = W_CELL.match(code)
            kind = None
            if w:
                kind, buf, idx = "cell", w.group(1), w.group(2).strip()
            else:
                w = W_BYTE.match(code)
                if w:
                    kind, buf, idx = "byte", w.group(1), w.group(2).strip()
            if kind:
                root = buf; seen = set()
                while root in aliases and root not in seen:
                    seen.add(root); root = aliases[root]
                if root in params: origin = "PARAM " + root
                elif root in owns: origin = "OWN nirmmita(" + owns[root] + ")"
                elif root in decls: origin = "DECL %s[%s] (compiler-checked)" % decls[root]
                else: origin = "OTHER " + root
                sites.append((ln, kind, buf, idx, origin, [s[1] for s in stack]))
        if sites or owns:
            total_fn += 1
            total_sites += len(sites)
            print("=" * 78)
            print("%s.smlib:%d  prakriya %s(%s)" % (mod, i + 1, name, ", ".join(params)))
            for c in contract: print("   " + c)
            if owns:
                for v, e in owns.items(): print("   own: %s = nirmmita(%s)" % (v, e))
            if decls:
                for v, (t, e) in decls.items(): print("   decl: %s %s[%s]" % (t, v, e))
            for ln, kind, buf, idx, origin, ctx in sites:
                print("   :%d %s %s[%s]   <- %s" % (ln, kind, buf, idx, origin))
                for c in ctx: print("        in: " + c)
        i = body_end + 1
print("=" * 78)
print("prakriya with writes/allocations: %d, write sites: %d" % (total_fn, total_sites))
