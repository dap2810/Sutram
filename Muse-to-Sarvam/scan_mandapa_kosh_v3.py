#!/usr/bin/env python3
"""WS1 scanner v3: like v2, but an alias is any variable whose assignment
RHS (inside the block) mentions the kosh name or an alias anywhere --
covering call-mediated aliases (bahar = rakh(k), 316's form) as well as
bare ones (bahar = k, 287's form)."""
import re, os, sys
TREE = sys.argv[1] if len(sys.argv) > 1 else "/home/hatch/workspace/r104/tree"
EX = os.path.join(TREE, "examples")

def strip_lit(ln):
    return re.sub(r'"(?:[^"\\]|\\.)*"', '""', ln)

def indent_of(ln):
    return len(ln) - len(ln.lstrip(' '))

def find_functions(lines):
    fns = []
    for i, ln in enumerate(lines):
        m = re.match(r"\s*(?:prakriya\s+([A-Za-z_0-9]+)\s*\(|mukhya\s*\()", ln)
        if m:
            fns.append((i, m.group(1) if m.group(1) else "mukhya"))
    return fns

def fn_range(fns, lines, idx):
    start = 0
    for s, _ in fns:
        if s <= idx:
            start = s
        else:
            break
    end = len(lines)
    for s, _ in fns:
        if s > idx:
            end = s
            break
    return start, end

def scan_file(fn):
    raw = open(os.path.join(EX, fn), encoding="utf-8", errors="replace").read().splitlines()
    lines = ["" if ln.strip().startswith("#") else strip_lit(ln) for ln in raw]
    fns = find_functions(lines)
    blocks = []
    for i, ln in enumerate(lines):
        m = re.search(r"\bmandapa\b(?:\s+parimita\s+[A-Za-z_0-9]+)?\s*(\{)?\s*$", ln)
        if not m:
            continue
        if m.group(1) == "{":
            depth = 0
            j = i
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                if j > i and depth <= 0:
                    break
                j += 1
            blocks.append((i, j + 1, "braced"))
        else:
            base = indent_of(ln)
            j = i + 1
            while j < len(lines):
                s = lines[j]
                if s.strip() == "":
                    j += 1
                    continue
                if indent_of(s) > base:
                    j += 1
                else:
                    break
            blocks.append((i, j, "indented"))
    # identity functions: prakriya f(kosh k) { ... nivartanam k ... } (returns
    # its kosh parameter itself, e.g. 316's rakh). A call to one is aliasing;
    # a call to any other function (e.g. padh, returning k[i]) is not.
    identity = set()
    for (fs, _), (fe, _) in zip([(s, None) for s, _ in fns] + [(len(lines), None)],
                                [(s, None) for s, _ in fns][1:] + [(len(lines), None)]):
        pass
    for idx, (fs, fname) in enumerate(fns):
        fe = fns[idx + 1][0] if idx + 1 < len(fns) else len(lines)
        body = lines[fs:fe]
        m = re.search(r"prakriya\s+([A-Za-z_0-9]+)\s*\(\s*kosh\s+([A-Za-z_0-9]+)", lines[fs])
        if m and any(re.search(rf"\bnivartanam\s+{m.group(2)}\s*$", bl) for bl in body):
            identity.add(m.group(1))
    made, hits = [], []
    for (bs, be, kind) in blocks:
        for k in range(bs, be):
            m = re.search(r"\bkosh\s+(?:(?:dasham|vitti)\s+)?([A-Za-z_0-9]+)\s*(?:\[|;|$)", lines[k])
            if not m:
                continue
            name = m.group(1)
            if any(bs2 > bs and bs2 <= k < be2 for (bs2, be2, _) in blocks):
                continue
            made.append((fn, k + 1, name, kind))
            aliases = set()
            changed = True
            while changed:
                changed = False
                for a in range(bs, be):
                    am = re.search(r"\b([A-Za-z_0-9]+)\s*=\s*(.+)$", lines[a])
                    if not am:
                        continue
                    rhs = am.group(2).strip()
                    is_alias_rhs = (
                        re.fullmatch(rf"{name}", rhs) is not None or
                        any(re.fullmatch(rf"{al}", rhs) is not None for al in aliases) or
                        any(re.fullmatch(rf"{f}\((?:{name}|" + "|".join(aliases) + r")(?:\s*,.*)?\)", rhs)
                            is not None for f in identity if aliases or True))
                    if is_alias_rhs and am.group(1) not in aliases and am.group(1) != name:
                        aliases.add(am.group(1))
                        changed = True
            fs, fe = fn_range(fns, lines, k)
            for u in range(be, fe):
                if re.search(rf"\b{name}\b", lines[u]):
                    hits.append((fn, k + 1, name, kind, u + 1, "name", raw[u].strip()[:110]))
            for al in aliases:
                for u in range(be, len(lines)):
                    if re.search(rf"\b{al}\b", lines[u]):
                        hits.append((fn, k + 1, name, kind, u + 1, f"alias:{al}", raw[u].strip()[:110]))
    return made, hits

all_made, all_hits = [], []
for fn in sorted(os.listdir(EX)):
    if not fn.endswith(".sm"):
        continue
    made, hits = scan_file(fn)
    all_made.extend(made)
    all_hits.extend(hits)
print(f"examples making a kosh inside a mandapa: {len(set(m[0] for m in all_made))} "
      f"({len(all_made)} decls)")
for m in all_made:
    print(f"  MADE {m[0]}:{m[1]} {m[2]} ({m[3]})")
print(f"examples USING such a kosh after the block: {len(set(h[0] for h in all_hits))}")
for h in all_hits:
    print(f"  HIT {h[0]} decl@{h[1]} {h[2]} ({h[3]}) used@{h[4]} via {h[5]}: {h[6]}")
