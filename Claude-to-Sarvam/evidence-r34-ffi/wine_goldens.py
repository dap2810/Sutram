# The real-Windows harness's check 7 (Windows-to-Sarvam/win-run-2026-10-21/harness-checks-4-5-7.py),
# the same tables, run under Wine with main's win/sutram.exe. For comparison with the real run.
import glob, os, subprocess, sys, json
ROOT, OUT = sys.argv[1], sys.argv[2]
W = ['env', 'DISPLAY=:99', 'WINEDEBUG=-all', f'WINEPREFIX={sys.argv[3]}', '/usr/lib/wine/wine64']
COMP = os.path.join(ROOT, 'win', 'sutram.exe')
EXPECT, EX = os.path.join(ROOT, 'tests', 'expect'), os.path.join(ROOT, 'examples')
LANG = {"37_native_gujarati": "gujarati", "38_native_hindi": "hindi", "39_native_tamil": "tamil",
        "218_sanskrit_devanagari": "sanskrit", "219_sanskrit_kosh_aliases": "sanskrit", "220_hindi_parse_error": "hindi"}
STDIN = {"23_grahan_input": "5\n", "24_guess_game": "7\n", "26_calculator": "20\n4\n",
         "number_game": "3\n", "46_language_reference": "7\n", "59_windows_grahan_runtime": "42\n"}
CWD = {"79_ayojan_cwd": OUT}
os.makedirs(OUT, exist_ok=True)
nl = lambda b: b.replace(b"\r\n", b"\n")
res = {}
names = sorted(os.path.basename(p)[:-3] for p in glob.glob(os.path.join(EX, "*.sm")))
for n in names:
    cf = os.path.exists(os.path.join(EXPECT, n + ".compile_fail"))
    if not cf and not os.path.exists(os.path.join(EXPECT, n + ".out")):
        continue
    exe = os.path.join(OUT, n + ".exe")
    if os.path.exists(exe): os.remove(exe)
    c = subprocess.run(W + [COMP] + (["--lang", LANG[n]] if n in LANG else []) + [os.path.join(EX, n + ".sm"), exe],
                       capture_output=True, timeout=120, cwd=CWD.get(n, ROOT))
    ok_compile = os.path.exists(exe)
    if cf:
        res[n] = 'matched' if not ok_compile else 'differed (compiled)'; continue
    if not ok_compile:
        res[n] = 'failed to compile'; continue
    try:
        r = subprocess.run(W + [exe], input=STDIN.get(n, "").encode(), capture_output=True, timeout=30, cwd=OUT)
    except subprocess.TimeoutExpired:
        res[n] = 'timed out'; continue
    want = nl(open(os.path.join(EXPECT, n + ".out"), "rb").read())
    ef = os.path.join(EXPECT, n + ".exit")
    wcode = int(open(ef).read().strip()) if os.path.exists(ef) else 0
    same = nl(r.stdout) == want
    res[n] = 'matched' if same and r.returncode == wcode else f'differed (exit {r.returncode}, expected {wcode}; stdout {"same" if same else "differs"})'
cnt = {}
for v in res.values():
    k = v.split(' (')[0]; cnt[k] = cnt.get(k, 0) + 1
print(json.dumps(cnt))
for n, v in res.items():
    if v != 'matched': print('NONMATCH', n, v)
