#!/usr/bin/env python3
"""Trap matrix v3: the columns v1/v2 did not cover -- conditions, prints,
stores -- for each value kind. v1/v2 covered binops only; the hand-found
traps (#3 truthiness, #5 likha(kosh), #6 string-into-mala, #8 dasham->mala)
all live in these columns, so v3 is the generator doing that job.
Usage: python3 trap_matrix_v3.py [compiler]  (default ./sutram_compiler)
Writes trap_matrix_v3.json beside itself. Read-only."""
import os, subprocess, json, sys, re
C = sys.argv[1] if len(sys.argv) > 1 else "./sutram_compiler"
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "probes_v3")
os.makedirs(D, exist_ok=True)
PRELUDE = {"rachana": "rachana Point = { x, y, z }\n"}
DECLS = {
    "int": 'vitti a = 5',
    "dasham": 'dasham a = 2.5',
    "string": 'vitti a = "ab"',
    "string_empty": 'vitti a = ""',
    "kosh": 'kosh a[2]\n    kosh_push(a, 7)',
    "mala": 'mala a[2]\n    a[0] = 7',
    "rachana": 'vitti a = nirmmita(24)\n    a.x = 10\n    a.y = 20\n    a.z = 30',
}
KINDS = ["int", "dasham", "string", "string_empty", "kosh", "mala", "rachana"]

def run_probe(name, src):
    p = f"{D}/{name}.sm"
    open(p, "w").write(src)
    b = f"{D}/{name}.bin"
    if os.path.exists(b):
        os.remove(b)
    cp = subprocess.run([C, p, b], capture_output=True, text=True, timeout=20)
    err = (cp.stderr or "") + (cp.stdout or "")
    if not os.path.exists(b):
        m = re.search(r"\[(E_[A-Z_]+)\]", err)
        return {"column": name.split("_")[0], "kind": "_".join(name.split("_")[1:-1]) or name,
                "probe": name, "result": "REFUSED",
                "code": m.group(1) if m else "compile-refused"}
    rp = subprocess.run(["timeout", "5", b], capture_output=True, text=True, timeout=20)
    out = (rp.stdout or "").strip()
    return {"column": name.split("_")[0], "kind": name, "probe": name,
            "result": "CRASH" if rp.returncode not in (0, 1) else out,
            "exit": rp.returncode}

results = []
for k in KINDS:
    pre = PRELUDE.get(k, "")
    # condition column: yadi (a) ? 1 : 0
    src = (f"{pre}mukhya() {{\n    {DECLS[k]}\n    yadi (a) {{\n        likha(1)\n    }} anya {{\n        likha(0)\n    }}\n}}\n")
    r = run_probe(f"cond_{k}", src)
    r["kind"] = k
    results.append(r)
    # print column: likha(a)
    src = f"{pre}mukhya() {{\n    {DECLS[k]}\n    likha(a)\n}}\n"
    r = run_probe(f"print_{k}", src)
    r["kind"] = k
    results.append(r)
    # store column: mala m[2]; m[0] = a; likha(m[0])
    src = (f"{pre}mukhya() {{\n    {DECLS[k]}\n    mala m[2]\n    m[0] = a\n    likha(m[0])\n}}\n")
    r = run_probe(f"store_{k}", src)
    r["kind"] = k
    results.append(r)
json.dump(results, open(os.path.join(HERE, "trap_matrix_v3.json"), "w"), indent=1)
for r in results:
    print(f"{r['column']:6} {r['kind']:13} -> {r['result']}")
