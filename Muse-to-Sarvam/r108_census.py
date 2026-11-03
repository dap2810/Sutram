#!/usr/bin/env python3
"""R96 WS1 memory census scanner: candidates only, hand-reading follows."""
import re, os, json

REPO = os.path.expanduser("~/workspace/r108/tree")
OUT = os.path.expanduser("~/workspace/r108/ws3")

def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()

def has_loop(lines):
    return any(re.search(r"\b(chakra|yavat)\b", ln) and not ln.strip().startswith("#") for ln in lines)

# ---------- examples: file-level flags ----------
ex = {}
for fn in sorted(os.listdir(f"{REPO}/examples")):
    if not fn.endswith(".sm"):
        continue
    lines = read(f"{REPO}/examples/{fn}")
    code = [ln for ln in lines if not ln.strip().startswith("#")]
    text = "\n".join(code)
    ex[fn] = {
        "nirmmita": "nirmmita" in text,
        "kosh_decl": bool(re.search(r"(?m)^[ \t]*kosh[ \t]", text)),
        "mandapa": "mandapa" in text,
        "loop": has_loop(code),
        "push": bool(re.search(r"kosh_push|kosh_enqueue|kosh_kship|kosh_yuj", text)),
        "kosh_param_or_use": "kosh" in text,
    }
with open(f"{OUT}/ex_flags.json", "w") as f:
    json.dump(ex, f, indent=1, sort_keys=True)
print("examples with nirmmita:", sum(1 for v in ex.values() if v["nirmmita"]))
print("examples with kosh_decl:", sum(1 for v in ex.values() if v["kosh_decl"]))
print("examples with mandapa:", sum(1 for v in ex.values() if v["mandapa"]))
print("examples with loop:", sum(1 for v in ex.values() if v["loop"]))
print("examples with push:", sum(1 for v in ex.values() if v["push"]))
print("examples alloc (nirmmita or kosh_decl):", sum(1 for v in ex.values() if v["nirmmita"] or v["kosh_decl"]))
print("examples alloc AND no mandapa:", sum(1 for v in ex.values() if (v["nirmmita"] or v["kosh_decl"]) and not v["mandapa"]))
print("examples alloc AND loop:", sorted(fn for fn, v in ex.items() if (v["nirmmita"] or v["kosh_decl"]) and v["loop"]))
print("examples push AND loop:", sorted(fn for fn, v in ex.items() if v["push"] and v["loop"]))
print("examples push, no loop:", sorted(fn for fn, v in ex.items() if v["push"] and not v["loop"]))

# ---------- lib: function-level flags ----------
# Function = from a prakriya line to the next prakriya line (same file).
FUNC_RE = re.compile(r"^\s*prakriya\s+([A-Za-z_0-9]+)")
lib_funcs = {}  # (module, func) -> dict
for mod in sorted(os.listdir(f"{REPO}/lib")):
    if not mod.endswith(".smlib"):
        continue
    lines = read(f"{REPO}/lib/{mod}")
    cur = None
    body = []
    def flush():
        if cur is None:
            return
        code = [ln for ln in body if not ln.strip().startswith("#")]
        text = "\n".join(code)
        lib_funcs[cur] = {
            "nirmmita": "nirmmita" in text,
            "kosh_decl": bool(re.search(r"(?m)^[ \t]*kosh[ \t]", text)),
            "mandapa": "mandapa" in text,
            "loop": has_loop(code),
            "push": bool(re.search(r"kosh_push|kosh_enqueue|kosh_kship|kosh_yuj", text)),
            "lines": len(body),
        }
    for ln in lines:
        m = FUNC_RE.match(ln)
        if m:
            flush()
            cur = (mod, m.group(1))
            body = [ln]
        elif cur is not None:
            body.append(ln)
    flush()
with open(f"{OUT}/lib_flags.json", "w") as f:
    json.dump({f"{m}::{fn}": v for (m, fn), v in lib_funcs.items()}, f, indent=1, sort_keys=True)
print("\nlib functions total:", len(lib_funcs))
print("lib funcs with nirmmita:", sum(1 for v in lib_funcs.values() if v["nirmmita"]))
print("lib funcs with kosh_decl:", sum(1 for v in lib_funcs.values() if v["kosh_decl"]))
print("lib funcs with mandapa:", sum(1 for v in lib_funcs.values() if v["mandapa"]))
print("lib funcs with loop:", sum(1 for v in lib_funcs.values() if v["loop"]))
print("lib funcs with push:", sum(1 for v in lib_funcs.values() if v["push"]))
print("lib funcs alloc:", sum(1 for v in lib_funcs.values() if v["nirmmita"] or v["kosh_decl"]))
print("lib funcs alloc AND no mandapa:", sum(1 for v in lib_funcs.values() if (v["nirmmita"] or v["kosh_decl"]) and not v["mandapa"]))
print("lib funcs alloc AND loop (Q1a/b candidates):")
for k, v in sorted(lib_funcs.items()):
    if (v["nirmmita"] or v["kosh_decl"]) and v["loop"]:
        print("  ", k, "nirmmita" if v["nirmmita"] else "", "kosh_decl" if v["kosh_decl"] else "", "push" if v["push"] else "")
print("lib funcs push (Q2 candidates):")
for k, v in sorted(lib_funcs.items()):
    if v["push"]:
        print("  ", k, "loop" if v["loop"] else "NOLOOP")
alloc_names = sorted({fn for (m, fn), v in lib_funcs.items() if v["nirmmita"] or v["kosh_decl"]})
with open(f"{OUT}/lib_alloc_names.txt", "w") as f:
    f.write("\n".join(alloc_names) + "\n")
print("\nlib allocating function names (%d):" % len(alloc_names))
print(", ".join(alloc_names))

# R108 addition (same file, appended): old-name population on the same tree.
# Run after scan.py: python3 r108_census.py <tree>  (scan.py itself takes no args
# and uses its REPO/OUT constants; this block runs standalone when invoked with a
# tree path and reproduces the R108 per-name table, code-stripped.)
if __name__ == "__main__" and len(__import__("sys").argv) > 1:
    import sys as _s, glob as _glob
    _tree = _s.argv[1]
    OLD = ["kosh_push","kosh_pop","kosh_len","kosh_cap","kosh_empty","kosh_peek",
           "kosh_clear","kosh_enqueue","kosh_dequeue","pankti_len","netsock",
           "netbind","netlisten","netaccept","char_lower","char_upper","char_from",
           "vartani_cat","lkhb","likha_fmt","sankhya_dot","smaran_cp"]
    _per, _users = {}, set()
    for _f in sorted(_glob.glob(f"{_tree}/examples/*.sm")):
        _t = open(_f, encoding="utf-8", errors="replace").read()
        _t = re.sub(r'"(?:[^"\\]|\\.)*"', '""', _t)
        _code = '\n'.join(_ln.split('#', 1)[0] for _ln in _t.splitlines())
        for _o in OLD:
            if re.search(r'\b' + _o + r'\b', _code):
                _per[_o] = _per.get(_o, 0) + 1
                _users.add(os.path.basename(_f))
    print(f"old-name example users: {len(_users)}")
    for _o in OLD:
        print(f"  {_o}: {_per.get(_o, 0)}")
