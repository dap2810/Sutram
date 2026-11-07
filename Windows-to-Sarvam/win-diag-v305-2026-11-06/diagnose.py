"""Native v305 diagnostics only; no product source or installed state is changed."""
from pathlib import Path
import ctypes, hashlib, json, subprocess, time
from job_runner import run_limited

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT/'build/windows-diag-v305-2026-11-06'
WORK.mkdir(parents=True, exist_ok=True)
COMPILER = ROOT/'win/sutram.exe'
B3 = ROOT/'build/windows-v305-2026-11-06/B3.exe'
EXPECTED_COMPILER = 'db5eda53871aafa4749d593ddef2d29e2841e3eb4d3cb7cdf680223fb45a073c'
EXPECTED_B3 = '61c3928c8c34a5612ee5fcb6873f56710b5a92869b6510b0f6062e3913c0dcf2'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(COMPILER) == EXPECTED_COMPILER, 'Use the original v305 compiler'
assert sha(B3) == EXPECTED_B3, 'Use the same previously tested B3 executable'
ctypes.windll.kernel32.SetErrorMode(0x8003)

def command(cmd, cwd=ROOT):
    started = time.perf_counter()
    p = subprocess.run(list(map(str,cmd)),cwd=cwd,capture_output=True,timeout=30)
    return dict(command=list(map(str,cmd)),cwd=str(cwd),exit=p.returncode,
                stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),
                elapsed_seconds=round(time.perf_counter()-started,4))

report = dict(compiler=str(COMPILER),compiler_sha256=sha(COMPILER),
              b3=str(B3),b3_sha256=sha(B3),version=command([COMPILER,'--version']),
              commit=command(['git','rev-parse','HEAD'])['stdout'].strip(),
              compilations=[],runs=[])
def save(): (HERE/'oom.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
def run(name,exe,cap):
    row=run_limited(exe,WORK/(name+'-'+str(cap)+'MiB'),cap)
    row.update(probe=name,limit_mib=cap,exe_sha256=sha(exe))
    report['runs'].append(row); save()
    print(f"{name} {cap} MiB: exit={row['exit']} stdout={row['stdout']!r} stderr={row['stderr']!r}",flush=True)
    return row

probes=['A2-two-million','A3-nirmmita-first-page','A3-mandapa','A3-nirmmita-touch-pages','A3-mandapa-small-budget']
for name in probes:
    exe=WORK/(name+'.exe')
    row=command([COMPILER,HERE/(name+'.sm'),exe]); row['probe']=name
    report['compilations'].append(row); save()
    if row['exit']: raise RuntimeError(row)

# Recheck the three known low limits, then obey the ordered stop-on-success request.
for cap in (64,128,256): run('B3',B3,cap)
first=None
for cap in (384,512,640,768,1024,1536):
    row=run('B3',B3,cap)
    if row['exit']==0:
        first=cap; break
report['first_success_in_requested_sweep_mib']=first
report['prior_2048MiB_control']='../win-v305-2026-11-06/oom-B3-2048MiB.json'
for cap in sorted({64,128,256,*[r['limit_mib'] for r in report['runs']]}):
    run('A2-two-million',WORK/'A2-two-million.exe',cap)
for name in probes[1:]: run(name,WORK/(name+'.exe'),64)
save()

# Exact repository-root relative command and the prior harness's actual CWD.
source=ROOT/'examples/79_ayojan_cwd.sm'
rows=[]
rows.append(command([r'win\sutram.exe',r'examples\79_ayojan_cwd.sm',WORK/'root-relative.exe']))
rows.append(command([COMPILER,source,WORK/'root-absolute.exe']))
rows.append(command([COMPILER,source,WORK/'harness-cwd.exe'],ROOT/'build/windows-v305-2026-11-06/suite'))
bundle=ROOT/'build/windows-v305-2026-11-06/bundle/sutram.exe'
if bundle.exists():
    assert sha(bundle)==EXPECTED_COMPILER
    rows.append(command([bundle,source,WORK/'portable-control.exe'],ROOT/'build/windows-v305-2026-11-06/suite'))
for row in rows:
    if row['exit']==0: row['run']=command([row['command'][-1]],WORK)
(HERE/'harness.json').write_text(json.dumps(dict(compiler_sha256=sha(COMPILER),runs=rows),indent=2)+'\n',encoding='utf8')
print(json.dumps(rows,indent=2))
