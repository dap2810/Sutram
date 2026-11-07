"""Build baseline/candidate Linux hosts and compare every emitted ELF fixture."""
from pathlib import Path
import ast, hashlib, json, os, shutil, subprocess, time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = ROOT/'build/oom'
BASE = WORK/'baseline-inputs'

# Only the two Windows runtime files differ in this review. Reconstruct their
# accepted versions explicitly; do not use HEAD, which advances after committing.
for folder in ('src', 'win', 'lang'):
    shutil.copytree(ROOT/folder, BASE/folder, dirs_exist_ok=True)
for name in ('win/winrt_blob.asm', 'win/rtblob.inc'):
    data = subprocess.check_output(['git', 'show', '789181227936714a87e8818065a2ac36352aa81c:'+name], cwd=ROOT)
    (BASE/name).write_bytes(data)

def run(cmd, cwd=ROOT, timeout=90, env=None):
    start=time.perf_counter()
    p=subprocess.run(list(map(str,cmd)),cwd=cwd,capture_output=True,timeout=timeout,env=env)
    row={'command':list(map(str,cmd)), 'cwd':str(cwd),'exit':p.returncode,
         'stdout':p.stdout.decode('utf8','replace'),'stderr':p.stderr.decode('utf8','replace'),
         'elapsed_seconds':round(time.perf_counter()-start,3)}
    return row

builds=[]
for variant, source in [('base',BASE),('patched',ROOT)]:
    dest=WORK/variant
    dest.mkdir(parents=True,exist_ok=True)
    for folder in ('lib','lang'):
        shutil.copytree(ROOT/folder,dest/folder,dirs_exist_ok=True)
    commands=[['nasm','-f','elf64','-I./','src/r68_compiler_entry.asm','-o',str(dest/'linux.o')],
              ['ld','-o',str(dest/'sutram-linux'),str(dest/'linux.o')]]
    for cmd in commands:
        row=run(cmd,cwd=source); builds.append(row)
        if row['exit']:
            (HERE/'linux-build.json').write_text(json.dumps(builds,indent=2)+'\n')
            raise RuntimeError(row)
(HERE/'linux-build.json').write_text(json.dumps(builds,indent=2)+'\n')

module=ast.parse((ROOT/'tests/run_tests.py').read_text())
langs=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign)
           and any(isinstance(t,ast.Name) and t.id=='LANG' for t in n.targets))
rows=[]
out=WORK/'elf-parity'; out.mkdir(exist_ok=True)
for src in sorted((ROOT/'examples').glob('*.sm')):
    results=[]
    for variant in ('base','patched'):
        target=out/(src.stem+'-'+variant+'.bin')
        flags=['--lang',langs[src.stem]] if src.stem in langs else []
        result=run([WORK/variant/'sutram-linux',*flags,src,target],cwd=out if src.stem=='79_ayojan_cwd' else ROOT,timeout=30)
        result['sha256']=hashlib.sha256(target.read_bytes()).hexdigest() if result['exit']==0 else None
        results.append(result)
    a,b=results
    equal=(a['exit'],a['stdout'],a['stderr'],a['sha256'])==(b['exit'],b['stdout'],b['stderr'],b['sha256'])
    rows.append({'case':src.stem,'equal':equal,'baseline':a,'candidate':b})
summary={'cases':len(rows),'identical_binaries':sum(r['equal'] and r['baseline']['exit']==0 for r in rows),
         'identical_refusals':sum(r['equal'] and r['baseline']['exit']!=0 for r in rows),
         'different':[r['case'] for r in rows if not r['equal']]}
(HERE/'linux-parity.json').write_text(json.dumps({'summary':summary,'cases':rows},indent=2)+'\n')
print(json.dumps(summary),flush=True)
env=dict(os.environ,SUTRAM_COMPILER=str(WORK/'patched/sutram-linux'))
suite=run(['python3','tests/run_tests.py'],env=env,timeout=180)
(HERE/'linux-suite.json').write_text(json.dumps(suite,indent=2)+'\n')
print(suite['stdout'],flush=True)
raise SystemExit(int(bool(summary['different']) or suite['exit']!=0))
