"""Run frozen native goldens with the review compiler, keeping output isolated."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT/'build/oom'
HERE.mkdir(exist_ok=True)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for variant in ('base', 'patched'):
    for folder in ('lib', 'lang'):
        shutil.copytree(ROOT/folder, WORK/variant/folder, dirs_exist_ok=True)

source_file = ROOT/'tools/test_windows_native.py'
source = source_file.read_text(encoding='utf8')
overrides = {"exe=ROOT/'win/sutram.exe'": "exe=ROOT/'build/oom/patched/sutram.exe'",
             "out=ROOT/'build/windows/acceptance'": "out=ROOT/'build/oom/native-suite'"}
for old, new in overrides.items():
    assert source.count(old) == 1
    source = source.replace(old, new)
os.environ['SUTRAM_EVIDENCE'] = str(HERE)
start = time.perf_counter()
code = 0
try:
    exec(compile(source, str(source_file), 'exec'), {'__file__':str(source_file), '__name__':'__main__'})
except SystemExit as e:
    code = int(e.code or 0)
rows = json.loads((HERE/'native-cases.json').read_text())
result = {'compiler_sha256':sha(WORK/'patched/sutram.exe'), 'harness_sha256':sha(source_file),
          'overrides':overrides, 'elapsed_seconds':round(time.perf_counter()-start,3), 'exit':code,
          'counts':{s:sum(r['status']==s for r in rows) for s in sorted({r['status'] for r in rows})},
          'failures':[r['case'] for r in rows if r['status'] in ('FAIL','COMPILE_FAIL','TIMEOUT')]}
(HERE/'native-summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(code)
