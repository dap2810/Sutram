#!/usr/bin/env python3
"""Trap matrix v2: kinds x ops, extended for v287.
Kinds: int, dasham, string, kosh, mala, rachana.
Ops: ==, !=, <, <=, >, >=, +, -, *, /, %.
Usage: python3 trap_matrix_v2.py [compiler]  (default ./sutram_compiler)
Writes trap_matrix_v2.json beside itself. Read-only: never changes the
compiler or the tree."""
import os, subprocess, json, sys, re
C = sys.argv[1] if len(sys.argv) > 1 else "./sutram_compiler"
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "probes_v2")
os.makedirs(D, exist_ok=True)
PRELUDE = {"rachana": "rachana Point = { x, y, z }\n"}
DECLS = {
    "int":   'vitti a = 5',
    "dasham": 'dasham a = 2.5',
    "string": 'vitti a = "ab"',
    "kosh":  'kosh a[2]\n    kosh_push(a, 7)',
    "mala":  'mala a[2]\n    a[0] = 7',
    "rachana": 'vitti a = nirmmita(24)\n    a.x = 10\n    a.y = 20\n    a.z = 30',
}
DECLS_B = {
    "int": 'vitti b = 3',
    "dasham": 'dasham b = 1.5',
    "string": 'vitti b = "cd"',
    "kosh": 'kosh b[2]\n    kosh_push(b, 7)',
    "mala": 'mala b[2]\n    b[0] = 7',
    "rachana": 'vitti b = nirmmita(24)\n    b.x = 10\n    b.y = 20\n    b.z = 30',
}
OPS = ["==", "!=", "<", "<=", ">", ">=", "+", "-", "*", "/", "%"]
OPNAME = {"==": "eq", "!=": "ne", "<": "lt", "<=": "le", ">": "gt",
          ">=": "ge", "+": "plus", "-": "minus", "*": "mul",
          "/": "div", "%": "mod"}
results = []
for ka in ["int", "dasham", "string", "kosh", "mala", "rachana"]:
    for kb in ["int", "dasham", "string", "kosh", "mala", "rachana"]:
        for op in OPS:
            name = f"m_{ka}_{kb}_{OPNAME[op]}"
            pre = PRELUDE.get(ka, "") + (PRELUDE.get(kb, "") if kb != ka else "")
            src = (f"{pre}mukhya() {{\n    {DECLS[ka]}\n    {DECLS_B[kb]}\n"
                   f"    likha(a {op} b)\n}}\n")
            p = f"{D}/{name}.sm"
            open(p, "w").write(src)
            b = f"{D}/{name}.bin"
            if os.path.exists(b):
                os.remove(b)
            cp = subprocess.run([C, p, b], capture_output=True, text=True, timeout=20)
            err = (cp.stderr or "") + (cp.stdout or "")
            if not os.path.exists(b):
                m = re.search(r"\[(E_[A-Z_]+)\]", err)
                results.append({"a": ka, "b": kb, "op": op, "result": "REFUSED",
                                "code": m.group(1) if m else "compile-refused"})
                continue
            rp = subprocess.run(["timeout", "5", b], capture_output=True, text=True, timeout=20)
            out = (rp.stdout or "").strip()
            results.append({"a": ka, "b": kb, "op": op,
                            "result": "CRASH" if rp.returncode not in (0, 1) else out,
                            "exit": rp.returncode})
json.dump(results, open(os.path.join(HERE, "trap_matrix_v2.json"), "w"), indent=1)
print(f"cells: {len(results)}, refused: {sum(1 for r in results if r['result'] == 'REFUSED')}, "
      f"crash: {sum(1 for r in results if r['result'] == 'CRASH')}")
