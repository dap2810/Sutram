"""Rebuilt native v309 compiler: requested arithmetic and Job Object checks."""
from pathlib import Path
import argparse,subprocess,json,hashlib,sys,ctypes,time,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];WORK=ROOT/'build/native-v309-final-fix'
ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['arithmetic','oom']);a=ap.parse_args()
compiler=ROOT/'win/sutram.exe';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(compiler)==json.loads((HERE/'candidate.json').read_text())['compiler_sha256']
ctypes.windll.kernel32.SetErrorMode(0x8003)
out=HERE/a.phase;out.mkdir(exist_ok=True);targets=WORK/a.phase;targets.mkdir(exist_ok=True)
r=dict(phase=a.phase,compiler=str(compiler),compiler_sha256=sha(compiler),cases=[])
def save():(out/'results.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
def run(cmd,timeout=30):
    start=time.perf_counter();p=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=timeout)
    return dict(command=list(map(str,cmd)),exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),seconds=time.perf_counter()-start)
if a.phase=='arithmetic':
    for name in ['add','xor']:shutil.copy2(ROOT/'Windows-to-Sarvam/win-v307-fixes-2026-11-06/wrapper-comparison'/(name+'.sm'),out/(name+'.sm'))
    programs={
      'add-literal':'mukhya() { kosh k[1]  kosh_kship(k, 7)  likha(k[0:1] + 0) }\n',
      'condition':'mukhya() { kosh k[1]  kosh_kship(k, 7)  yadi (k[0:1]) { likha(1) } }\n',
      'direct-print':'mukhya() { kosh k[1]  kosh_kship(k, 7)  likha(k[0:1]) }\n',
      'store':'mukhya() { kosh k[1]  kosh_kship(k, 7)  vitti i = k[0:1]  likha(i) }\n',
      'length':'mukhya() {\n    kosh k[1]\n    kosh_kship(k, 1)\n    kosh_kship(k, 2)\n    kosh_kship(k, 3)\n    likha(pankti_gan(k[0:2]))\n}\n'}
    for name,source in programs.items():(out/(name+'.sm')).write_text(source,encoding='utf8',newline='\n')
    for name in ['add','xor',*programs]:
        src=out/(name+'.sm');exe=targets/(name+'.exe')
        if exe.exists():raise RuntimeError('Use a fresh result directory; stale output must not pass')
        c=run([str(compiler),str(src),str(exe)]);message=c['stdout']+c['stderr']
        row=dict(name=name,source_sha256=sha(src),compile=c,output_file_exists=exe.exists())
        if name=='length':
            row['run']=run([str(exe)]) if c['exit']==0 and exe.exists() else {}
            row['pass']=c['exit']==0 and row['run'].get('exit')==0 and row['run'].get('stdout')=='2\n' and not row['run'].get('stderr')
        else:
            row['pass']=c['exit']!=0 and not exe.exists() and 'Sutram truti' in message
            if name in ['add','xor']:row['pass']=row['pass'] and any(x in message for x in ['E_VIBHAG_ANKA','E_KOSH_GANIT'])
            if c['exit']==0 and exe.exists():row['unexpected_run']=run([str(exe)],timeout=10)
        r['cases'].append(row);save();print(name,row['pass'],message.strip(),flush=True)
else:
    sys.path.insert(0,str(ROOT/'tests/windows'));from job_runner import run_limited
    bins={}
    for name in ['B3','A3-mandapa','A3-nirmmita-touch-pages']:
        src=out/(name+'.sm');shutil.copy2(ROOT/'Windows-to-Sarvam/win-v307-2026-11-06'/(name+'.sm'),src)
        exe=targets/(name+'.exe');c=run([str(compiler),str(src),str(exe)])
        if c['exit']!=0:raise RuntimeError(c)
        bins[name]=exe
    cases=[('B3',cap,n) for cap in [448,480,512,544,576,608,640] for n in range(1,4)]
    cases += [('A3-mandapa',64,n) for n in range(1,11)]+[('A3-nirmmita-touch-pages',64,1)]
    for name,cap,n in cases:
        label=f'{name}-{cap}-{n}';folder=out/label
        row=run_limited(bins[name],folder,cap)
        raw=(folder/'stderr').read_bytes();stdout=(folder/'stdout').read_bytes()
        row.update(name=name,limit_mib=cap,repetition=n,stderr_bytes=len(raw),stderr_hex=raw.hex(),ends_lf=raw.endswith(b'\n'),exit_hex=f"0x{row['exit']:08X}")
        row['pass']=not row['timed_out'] and row['exit']==1 and raw==b'Sutram truti: smritih na labdha\n' and not stdout
        r['cases'].append(row);save();print(label,row['exit_hex'],len(raw),row['pass'],flush=True)
r['summary']=dict(total=len(r['cases']),passed=sum(x['pass'] for x in r['cases']))
save();print(json.dumps(r['summary']));raise SystemExit(0 if all(x['pass'] for x in r['cases']) else 1)
