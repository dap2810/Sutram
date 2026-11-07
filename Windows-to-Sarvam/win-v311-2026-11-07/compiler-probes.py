"""Native checks requested by REQUEST.md; no compiler/source changes."""
from pathlib import Path
import argparse,ctypes,hashlib,json,subprocess,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];WORK=ROOT/'build/native-v311'
ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['expressions','nesting']);a=ap.parse_args()
compiler=ROOT/'win/sutram.exe'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(compiler)==json.loads((HERE/'candidate.json').read_text())['compiler_sha256']
ctypes.windll.kernel32.SetErrorMode(0x8003)
out=HERE/a.phase;out.mkdir(exist_ok=True);targets=WORK/a.phase;targets.mkdir(exist_ok=True)
def run(cmd):
    t=time.perf_counter()
    try:
        p=subprocess.run(list(map(str,cmd)),cwd=ROOT,capture_output=True,timeout=15)
        return dict(command=list(map(str,cmd)),exit=p.returncode,exit_hex=f'0x{p.returncode&0xffffffff:08X}',stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),seconds=time.perf_counter()-t,timeout=False)
    except subprocess.TimeoutExpired as e:
        return dict(command=list(map(str,cmd)),exit=None,stdout=(e.stdout or b'').decode('utf8','replace'),stderr=(e.stderr or b'').decode('utf8','replace'),seconds=time.perf_counter()-t,timeout=True)
r=dict(compiler_sha256=sha(compiler),version=run([compiler,'--version']),cases=[])
assert r['version']['stdout'].splitlines()[0]=='Sutram 1.0 (v311) - sampurna sutra'
def save():(out/'results.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
def check(name,source,expected):
    src=out/(name+'.sm');src.write_text(source,encoding='utf8',newline='\n');exe=targets/(name+'.exe')
    if exe.exists():raise RuntimeError('Use a fresh target; stale output cannot pass')
    c=run([compiler,src,exe]);row=dict(name=name,source_sha256=sha(src),compile=c,output_file_exists=exe.exists(),expected=expected)
    if expected=='refusal':
        row['pass']=c['exit']==1 and not exe.exists() and any(x in c['stderr']+c['stdout'] for x in ['E_KOSH_GANIT','E_KOSH_DVARA','E_VIBHAG_ANKA'])
    elif expected=='syntax':row['pass']=c['exit']==1 and not exe.exists() and 'Sutram truti' in c['stdout']+c['stderr']
    else:
        row['run']=run([exe]) if c['exit']==0 and exe.exists() else {}
        row['pass']=row['run'].get('stdout')==expected and row['run'].get('exit')==0 and not row['run'].get('stderr')
    r['cases'].append(row);save();return row
if a.phase=='expressions':
    f='prakriya make_kosh() {\n kosh k[1]\n kosh_kship(k, 7)\n nivartanam k\n}\n'
    cases=[('global-direct',f+'vitti g = make_kosh()\nmukhya() { likha(g[0]) }\n','refusal'),
     ('global-add',f+'vitti zero = 0\nvitti leaked = make_kosh() + zero\nmukhya() { likha(leaked) }\n','refusal'),
     ('valid-global','vitti counter = 7\nmukhya() { likha(counter) }\n','7\n'),
     ('two-globals-no-main','vitti a = 1\nvitti b = 2\n','syntax'),
     ('record-literal','rachana Point = { x: 1, y: 2 }\nvitti p = Point\n','syntax'),
     ('default-argument','prakriya f(vitti n = 5) { nivartanam n }\nmukhya() { likha(f()) }\n','syntax'),
     ('two-globals-with-main','vitti a = 1\nvitti b = 2\nmukhya() { likha(a + b) }\n','3\n'),
     ('local-direct',f+'mukhya() { vitti g = make_kosh()\n likha(g[0]) }\n','7\n'),
     ('local-add',f+'mukhya() { vitti zero = 0\n vitti leaked = make_kosh() + zero\n likha(leaked) }\n','refusal')]
    for name,op in [('add','+'),('xor','^')]:
        cases.append((name,'prakriya keep(x) { nivartanam x }\nmukhya() {\n kosh k[1]\n kosh_kship(k, 7)\n vitti zero = 0\n vitti kept = keep(k[0:1] '+op+' zero)\n kosh_kship(k, 8)\n likha(kept)\n}\n','refusal'))
    cases.append(('length','mukhya() {\n kosh k[1]\n kosh_kship(k, 7)\n kosh_kship(k, 8)\n likha(pankti_gan(k[0:2]))\n}\n','2\n'))
    for args in cases:
        row=check(*args);print(row['name'],row['pass'],row['compile']['exit'],row['compile']['stdout'].strip(),row['compile']['stderr'].strip(),flush=True)
else:
    # One more balanced pair per probe; 0 means likha(1) without additional pairs.
    for n in range(0,2049):
        src=out/f'depth-{n:04d}.sm';src.write_text('mukhya() { likha('+'('*n+'1'+')'*n+') }\n',encoding='utf8')
        exe=targets/f'depth-{n:04d}.exe'
        if exe.exists():raise RuntimeError('Stale nesting target')
        c=run([compiler,src,exe]);row=dict(depth=n,source_sha256=sha(src),compile=c,output_file_exists=exe.exists())
        row['status']='TIMEOUT' if c['timeout'] else 'COMPILED' if c['exit']==0 and exe.exists() else 'REFUSED' if c['exit']==1 and not exe.exists() and 'Sutram truti' in c['stdout']+c['stderr'] else 'CRASH_OR_OTHER'
        r['cases'].append(row)
        if n%100==0 or row['status']!='COMPILED':save();print('depth',n,row['status'],flush=True)
        if row['status']!='COMPILED':
            r['boundary']=row
            if n>0:r['last_compiled_run']=run([targets/f'depth-{n-1:04d}.exe'])
            break
    save()
print('Finished',a.phase,len(r['cases']),flush=True)
