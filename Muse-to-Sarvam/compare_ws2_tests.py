import os, subprocess, glob, json
T296 = "/home/hatch/workspace/r116/tree"
T295 = "/home/hatch/workspace/r116/tree295"
OUT = "/home/hatch/workspace/r116/ws2_out"
def run_one(compiler, workdir, src, tag):
    binp = os.path.join(OUT, tag + ".bin")
    try:
        c = subprocess.run([compiler, src, binp], cwd=workdir, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return {"compile": "TIMEOUT"}
    if c.returncode != 0:
        return {"compile": c.returncode, "compile_err": c.stderr.strip()[:300]}
    try:
        r = subprocess.run([binp], cwd=workdir, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=10)
        return {"compile": 0, "stdout": r.stdout, "stderr": r.stderr, "exit": r.returncode}
    except subprocess.TimeoutExpired:
        return {"compile": 0, "stdout": "", "stderr": "", "exit": "TIMEOUT"}
    finally:
        try: os.remove(binp)
        except OSError: pass
results = {}
files296 = sorted(glob.glob(T296 + "/tests/**/*.sm", recursive=True))
for src296 in files296:
    rel = os.path.relpath(src296, T296)
    src295 = os.path.join(T295, rel)
    if not os.path.exists(src295):
        results[rel] = {"src": "NEW"}
        continue
    if open(src296, 'rb').read() != open(src295, 'rb').read():
        results[rel] = {"src": "CHANGED"}
        continue
    a = run_one(T295 + "/sutram_compiler", T295, src295, "t295")
    b = run_one(T296 + "/sutram_compiler", T296, src296, "t296")
    results[rel] = {"src": "same", "v295": a, "v296": b, "identical": a == b}
same = [v for v in results.values() if v.get("src") == "same"]
diffs = {k: v for k, v in results.items() if v.get("src") == "same" and not v["identical"]}
print(f"tests compared_same_src={len(same)} identical={len([v for v in same if v['identical']])} differing={len(diffs)} new={len([v for v in results.values() if v.get('src')=='NEW'])} changed={len([v for v in results.values() if v.get('src')=='CHANGED'])}")
print("CHANGED:", sorted([k for k, v in results.items() if v.get("src") == "CHANGED"]))
print("NEW:", sorted([k for k, v in results.items() if v.get("src") == "NEW"])[:20])
for k, v in sorted(diffs.items()):
    print(f"--- {k}")
    print(f"  v295: {v['v295']}")
    print(f"  v296: {v['v296']}")
json.dump(results, open(OUT + "/ws2_tests_results.json", "w"), indent=1)
