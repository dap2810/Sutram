"""Sutram real-Windows checks 4-7. Reads the repo, writes only under %TEMP%\\sutram-win."""
import hashlib, json, os, shutil, subprocess, sys, glob

ROOT = sys.argv[1]
OUT = os.path.join(os.environ["TEMP"], "sutram-win")
os.makedirs(OUT, exist_ok=True)
COMP = os.path.join(ROOT, "win", "sutram.exe")
EXPECT = os.path.join(ROOT, "tests", "expect")
EX = os.path.join(ROOT, "examples")
R = {}

def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

def nl(b):
    return b.replace(b"\r\n", b"\n")

# ---- 4 hashes
h = {"win/sutram.exe": sha(os.path.join(ROOT, "win", "sutram.exe")),
     "sutram.exe": sha(os.path.join(ROOT, "sutram.exe")),
     "Sutram-Setup.exe": sha(os.path.join(ROOT, "Sutram-Setup.exe"))}
h["Sutram-Setup.sha256 (recorded)"] = open(os.path.join(ROOT, "Sutram-Setup.sha256")).read().split()[0].lower()
r17 = os.path.join(ROOT, "tests", "negative", "r17")
lines = [l for l in open(os.path.join(r17, "SHA256SUMS"), encoding="utf-8").read().splitlines() if l.strip()]
sums = {"total": len(lines), "ok": 0, "bad": [], "missing": [], "named": {}}
for l in lines:
    want, name = l.split(None, 1)
    name = name.lstrip("*")
    p = os.path.join(r17, name[2:] if name.startswith("./") else name)
    base = os.path.basename(p)
    if not os.path.exists(p):
        sums["missing"].append(base); continue
    got = sha(p)
    if got == want.lower():
        sums["ok"] += 1
    else:
        sums["bad"].append({"file": base, "want": want, "got": got})
    if base in ("mutation-15-27971.sm", "mutation-15-37233.sm", "mutation-15-42057.sm", "mutation-15-574.sm"):
        sums["named"][base] = {"listed": want, "computed": got}
R["hashes"] = h
R["sha256sums_r17"] = sums

# ---- 5 + 7 examples
LANG = {"37_native_gujarati": "gujarati", "38_native_hindi": "hindi", "39_native_tamil": "tamil",
        "218_sanskrit_devanagari": "sanskrit", "219_sanskrit_kosh_aliases": "sanskrit",
        "220_hindi_parse_error": "hindi"}
STDIN = {"23_grahan_input": "5\n", "24_guess_game": "7\n", "26_calculator": "20\n4\n",
         "number_game": "3\n", "46_language_reference": "7\n", "59_windows_grahan_runtime": "42\n"}
CWD = {"79_ayojan_cwd": OUT}
BIN = os.path.join(OUT, "bin"); os.makedirs(BIN, exist_ok=True)

def first_diff(a, b):
    al, bl = a.split(b"\n"), b.split(b"\n")
    for i in range(max(len(al), len(bl))):
        x = al[i] if i < len(al) else None
        y = bl[i] if i < len(bl) else None
        if x != y:
            d = lambda v: "<missing>" if v is None else v.decode("utf-8", "replace")
            return {"line": i + 1, "expected": d(x), "actual": d(y)}
    return None

def run_one(name):
    src = os.path.join(EX, name + ".sm")
    exe = os.path.join(BIN, name + ".exe")
    if os.path.exists(exe): os.remove(exe)
    cmd = [COMP] + (["--lang", LANG[name]] if name in LANG else []) + [src, exe]
    c = subprocess.run(cmd, capture_output=True, timeout=60, cwd=CWD.get(name, ROOT))
    cout = c.stdout + c.stderr
    rec = {"name": name, "compile_cmd": " ".join(cmd[1:]), "compile_exit": c.returncode,
           "compile_output": cout.decode("utf-8", "replace")}
    cf = os.path.exists(os.path.join(EXPECT, name + ".compile_fail"))
    if cf:
        rec["expect"] = "compile_fail"
        if c.returncode != 0:
            rec["status"] = "matched"
            # informational: compare diagnostic text, path-normalised, with the Linux golden
            g = os.path.join(EXPECT, name + ".out")
            if os.path.exists(g):
                norm = nl(cout).replace(ROOT.encode(), b"<ROOT>").replace(ROOT.replace("\\", "/").encode(), b"<ROOT>")
                norm = norm.replace(b"<ROOT>\\examples\\", b"<ROOT>/examples/")
                rec["diag_matches_linux_golden"] = norm == nl(open(g, "rb").read())
                if not rec["diag_matches_linux_golden"]:
                    rec["diag_first_diff"] = first_diff(nl(open(g, "rb").read()), norm)
        else:
            rec["status"] = "differed"; rec["detail"] = "expected compilation to FAIL, but it succeeded"
        return rec
    if c.returncode != 0:
        rec["status"] = "failed to compile"; return rec
    try:
        r = subprocess.run([exe], input=STDIN.get(name, "").encode(), capture_output=True, timeout=10, cwd=OUT)
        out, code = r.stdout, r.returncode
    except subprocess.TimeoutExpired as e:
        rec["status"] = "timed out"; rec["stdout_partial"] = (e.stdout or b"").decode("utf-8", "replace"); return rec
    rec["exit"] = code
    rec["stdout"] = out.decode("utf-8", "replace")
    rec["stderr"] = r.stderr.decode("utf-8", "replace")
    if code < 0 or code >= 0xC0000000:
        rec["status"] = "crashed"; rec["detail"] = f"exit 0x{code & 0xFFFFFFFF:08X}"; return rec
    want = nl(open(os.path.join(EXPECT, name + ".out"), "rb").read())
    ef = os.path.join(EXPECT, name + ".exit")
    wcode = int(open(ef).read().strip()) if os.path.exists(ef) else 0
    rec["expected_exit"] = wcode
    same_out = nl(out) == want
    if same_out and code == wcode:
        rec["status"] = "matched"
    else:
        rec["status"] = "differed"
        rec["detail"] = (f"exit {code}, expected {wcode}" if code != wcode else "") + \
                        ("" if same_out else (" ; " if code != wcode else "") + "stdout differs")
        if not same_out: rec["first_diff"] = first_diff(want, nl(out))
    return rec

five = ["246_r23_comparator_sort", "247_r23_methods", "248_r23_slices", "249_r25_phal", "250_r26_dosh_handler"]
R["check5"] = [run_one(n) for n in five]

names = sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(EX, "*.sm")))
sel = [n for n in names if os.path.exists(os.path.join(EXPECT, n + ".out")) or
       os.path.exists(os.path.join(EXPECT, n + ".compile_fail"))]
R["check7_skipped_no_expectation"] = [n for n in names if n not in sel]
res = [run_one(n) for n in sel]
R["check7"] = res
cnt = {}
for x in res: cnt[x["status"]] = cnt.get(x["status"], 0) + 1
R["check7_counts"] = cnt
json.dump(R, open(os.path.join(OUT, "checks-4-5-7.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({"hashes": h, "r17": {k: v for k, v in sums.items() if k != "bad"}, "r17_bad": sums["bad"][:5],
                  "c5": [(x["name"], x["status"], x.get("exit"), x.get("detail")) for x in R["check5"]],
                  "c7": cnt, "c7_total": len(sel), "skipped": R["check7_skipped_no_expectation"]},
                 ensure_ascii=False, indent=1))
for x in res:
    if x["status"] != "matched":
        print("NONMATCH", x["name"], x["status"], x.get("detail"), json.dumps(x.get("first_diff"), ensure_ascii=False),
              x.get("compile_output", "")[:300] if x["status"] == "failed to compile" else "")
for x in res:
    if x.get("expect") == "compile_fail" and not x.get("diag_matches_linux_golden", True):
        print("DIAG", x["name"], json.dumps(x.get("diag_first_diff"), ensure_ascii=False))
