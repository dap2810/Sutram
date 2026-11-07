from pathlib import Path
import ctypes,hashlib,json,os,subprocess
from job_runner import run_limited
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
WORK=ROOT/'build/windows-v306-2026-11-06';WORK.mkdir(exist_ok=True)
identity=json.loads((HERE/'identity.json').read_text(encoding='utf8'))
assert identity['identity_pass'],'Stop unless the new shell reports v306'
compiler=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram/bin/sutram.exe'
assert hashlib.sha256(compiler.read_bytes()).hexdigest()==identity['installed_compiler_sha256']
ctypes.windll.kernel32.SetErrorMode(0x8003)
report=dict(compiler=str(compiler),sha256=identity['installed_compiler_sha256'],compilations=[],runs=[])
def save(): (HERE/'oom.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
for name in ['B3','A3-mandapa','A3-nirmmita-touch-pages']:
    cmd=[str(compiler),str(HERE/(name+'.sm')),str(WORK/(name+'.exe'))]
    p=subprocess.run(cmd,cwd=WORK,capture_output=True,timeout=30)
    report['compilations'].append(dict(command=cmd,cwd=str(WORK),exit=p.returncode,stdout=p.stdout.decode(),stderr=p.stderr.decode()))
    save();assert p.returncode==0
for name,cap in [('B3',c) for c in [64,128,256,512,640,768,1024,2048]]+[('A3-mandapa',64),('A3-nirmmita-touch-pages',64)]:
    exe=WORK/(name+'.exe');row=run_limited(exe,WORK/(name+'-'+str(cap)),cap)
    expect_success=name=='B3' and cap>=768
    row.update(probe=name,limit_mib=cap,executable_sha256=hashlib.sha256(exe.read_bytes()).hexdigest())
    row['pass']=not row['timed_out'] and (row['exit'],row['stdout'],row['stderr'])==((0,'100000000\n','') if expect_success else (1,'','Sutram truti: smritih na labdha\n'))
    report['runs'].append(row);save()
    print(f"{name} {cap}MiB exit={row['exit']} stdout={row['stdout']!r} stderr={row['stderr']!r} pass={row['pass']}",flush=True)
report['passed']=sum(r['pass'] for r in report['runs']);report['failed']=len(report['runs'])-report['passed'];save()
raise SystemExit(bool(report['failed']))
