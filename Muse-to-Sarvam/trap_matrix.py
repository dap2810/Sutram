#!/usr/bin/env python3
"""Systematic trap finder (prototype): type x operation matrix.
For each (kindA, kindB, op) emit a minimal probe, compile + run on the
v286 compiler, record: refused / crash / output. A cell whose behaviour
is not the type-correct semantics is a trap candidate. Read-only: it
never changes the compiler or the tree."""
import os, subprocess, json
import sys
C = sys.argv[1] if len(sys.argv) > 1 else "./sutram_compiler"
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "probes")
os.makedirs(D, exist_ok=True)
DECLS = {
    "int":   'vitti a = 5',
    "dasham":'dasham a = 2.5',
    "string":'vitti a = "ab"',
    "kosh":  'kosh a[2]\n    kosh_push(a, 7)',
}
DECLS_B = {k: v.replace(" a", " b").replace("(a,", "(b,") for k, v in DECLS.items()}
DECLS_B["string"] = 'vitti b = "cd"'
DECLS_B["dasham"] = 'dasham b = 1.5'
DECLS_B["int"] = 'vitti b = 3'
OPS = ["==", "!=", "<", "+", "-", "*", "/"]
results = []
for ka in ["int", "dasham", "string", "kosh"]:
    for kb in ["int", "dasham", "string", "kosh"]:
        for op in OPS:
            name = f"m_{ka}_{kb}_{op.replace('=','eq').replace('!','ne').replace('<','lt').replace('+','plus').replace('-','minus').replace('*','mul').replace('/','div')}"
            src = f"mukhya() {{\n    {DECLS[ka]}\n    {DECLS_B[kb]}\n    likha(a {op} b)\n}}\n"
            p = f"{D}/{name}.sm"
            open(p, "w").write(src)
            b = f"{D}/{name}.bin"
            if os.path.exists(b): os.remove(b)
            cp = subprocess.run([C, p, b], capture_output=True, text=True, timeout=20)
            err = (cp.stderr or "") + (cp.stdout or "")
            if not os.path.exists(b):
                # refused (or compile error): capture the diagnostic code
                code = ""
                for tok in ["E_VARTANI_TUL", "E_VARTANI_CAT", "E_", "Error"]:
                    if tok in err: code = tok; break
                import re
                m = re.search(r"\[(E_[A-Z_]+)\]", err)
                code = m.group(1) if m else "compile-refused"
                results.append({"a": ka, "b": kb, "op": op, "result": "REFUSED", "code": code})
                continue
            rp = subprocess.run(["timeout", "5", b], capture_output=True, text=True, timeout=20)
            out = (rp.stdout or "").strip()
            results.append({"a": ka, "b": kb, "op": op, "result": "CRASH" if rp.returncode not in (0, 1) else out, "exit": rp.returncode})
json.dump(results, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "trap_matrix.json"), "w"), indent=1)
for r in results:
    if r["result"] not in ("REFUSED",):
        print(f"{r['a']:7} {r['op']:3} {r['b']:7} -> {r['result']} (exit {r.get('exit')})")
print("--- refused cells:")
for r in results:
    if r["result"] == "REFUSED":
        print(f"{r['a']:7} {r['op']:3} {r['b']:7} -> REFUSED {r['code']}")
