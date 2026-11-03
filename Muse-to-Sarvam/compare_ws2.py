import os, subprocess, glob, hashlib, json, sys
T296 = "/home/hatch/workspace/r116/tree"
T295 = "/home/hatch/workspace/r116/tree295"
OUT = "/home/hatch/workspace/r116/ws2_out"
os.makedirs(OUT, exist_ok=True)
def run_one(compiler, workdir, src, tag):
    binp = os.path.join(OUT, tag + ".bin")
    c = subprocess.run([compiler, src, binp], cwd=workdir, capture_output=True, text=True, timeout=30)
    if c.returncode != 0:
        return {"compile": c.returncode, "compile_err": c.stderr.strip()[:300], "run": None}
    try:
        r = subprocess.run([binp], cwd=workdir, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
        return {"compile": 0, "stdout": r.stdout, "stderr": r.stderr, "exit": r.returncode}
    except subprocess.TimeoutExpired:
        return {"compile": 0, "stdout": "", "stderr": "", "exit": "TIMEOUT"}
    finally:
        try: os.remove(binp)
        except OSError: pass
results = {}
files296 = sorted(glob.glob(T296 + "/examples/*.sm"))
for src296 in files296:
    name = os.path.basename(src296)
    src295 = os.path.join(T295, "examples", name)
    same_src = os.path.exists(src295) and open(src296, 'rb').read() == open(src295, 'rb').read()
    if not same_src:
        results[name] = {"src": "CHANGED_OR_NEW"}
        continue
    a = run_one(T295 + "/sutram_compiler", T295, src295, "v295_" + name)
    b = run_one(T296 + "/sutram_compiler", T296, src296, "v296_" + name)
    results[name] = {"src": "same", "v295": a, "v296": b, "identical": a == b}
diffs = {k: v for k, v in results.items() if v.get("src") == "same" and not v["identical"]}
changed = {k: v for k, v in results.items() if v.get("src") != "same"}
print(f"compared_same_src={len([v for v in results.values() if v.get('src')=='same'])} identical={len([v for v in results.values() if v.get('identical')])} differing={len(diffs)} changed_or_new_src={len(changed)}")
print("CHANGED_OR_NEW:", sorted(changed))
print("DIFFERING:")
for k, v in sorted(diffs.items()):
    print(f"--- {k}")
    print(f"  v295: {v['v295']}")
    print(f"  v296: {v['v296']}")
json.dump(results, open(OUT + "/ws2_results.json", "w"), indent=1)
