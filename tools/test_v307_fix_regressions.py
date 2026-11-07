"""Native regression evidence for the v307 repair candidates (no golden updates)."""
from pathlib import Path
import argparse,ctypes,hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--compiler',required=True);ap.add_argument('--phase',choices=['oom','slice'],required=True);ap.add_argument('--evidence',required=True);ap.add_argument('--baseline',action='store_true');a=ap.parse_args()
compiler=Path(a.compiler).resolve();out=Path(a.evidence).resolve();out.mkdir(parents=True,exist_ok=True)
if os.name=='nt':ctypes.windll.kernel32.SetErrorMode(0x8003)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(compiler=str(compiler),compiler_sha256=sha(compiler),phase=a.phase,baseline=a.baseline,cases=[])
def save():(out/'results.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
def run(cmd,timeout=60):
    start=time.perf_counter()
    try:
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=timeout)
        return dict(command=list(map(str,cmd)),exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),seconds=time.perf_counter()-start)
    except subprocess.TimeoutExpired:return dict(command=list(map(str,cmd)),timeout=True,seconds=time.perf_counter()-start)
if a.phase=='oom':
    assert os.name=='nt','Job Object measurements require native Windows'
    source=ROOT/'Windows-to-Sarvam/win-v307-2026-11-06'
    sys.path.insert(0,str(source));from job_runner import run_limited
    bins={}
    for name in ['B3','A3-mandapa','A3-nirmmita-touch-pages']:
        exe=out/(name+'.exe');c=run([str(compiler),str(source/(name+'.sm')),str(exe)])
        assert c.get('exit')==0,c;bins[name]=exe
    cases=[('B3',cap,n,1) for cap in [448,480,512,544,576,608,640] for n in range(1,4)]
    cases += [('A3-mandapa',64,n,1) for n in range(1,11)]
    cases += [('A3-nirmmita-touch-pages',64,1,1)]
    cases += [('B3',cap,1,1) for cap in [64,128,256]]+[('B3',768,1,0)]
    for name,cap,n,expected in cases:
        label=f'{name}-{cap}-{n}';directory=out/label
        row=run_limited(bins[name],directory,cap)
        raw=(directory/'stderr').read_bytes();stdout=(directory/'stdout').read_bytes()
        row.update(label=label,expected_exit=expected,stderr_hex=raw.hex(),stderr_bytes=len(raw),stdout_hex=stdout.hex(),exit_hex=f"0x{row['exit']:08X}")
        row['pass']=not row['timed_out'] and row['exit']==expected and (raw==b'Sutram truti: smritih na labdha\n' if expected else not raw)
        if expected:row['pass']=row['pass'] and not stdout
        else:row['pass']=row['pass'] and stdout==b'100000000\n'
        r['cases'].append(row);save();print(label,row['exit_hex'],row['pass'],flush=True)
else:
    for src in sorted((ROOT/'Muse-to-Sarvam').glob('r136_ws*.sm')):
        exe=out/(src.stem+('.exe' if os.name=='nt' else '.bin'))
        row=dict(source=str(src.relative_to(ROOT)),sha256=sha(src),compile=run([str(compiler),str(src),str(exe)]))
        c=row['compile'];row['pass']=c.get('exit')==1 and 'E_KOSH_VIBHAG' in (c.get('stdout','')+c.get('stderr',''))
        if c.get('exit')==0:row['run']=run([str(exe)],timeout=15)
        r['cases'].append(row);save();print(src.name,'refused=',row['pass'],flush=True)
    # Typed views must not be laundered through a scalar parameter or storage.
    for name,body in {
        'typed-cell':'mala box[1]\n    box[0] = s',
        'typed-scalar':'likha(s)',
        'typed-return':'nivartanam s',
        'typed-alias':'vitti t = s',
    }.items():
        src=out/(name+'.sm');src.write_text('prakriya f(vibhag s) {\n    '+body+'\n}\nmukhya() {\n    mala m[1]\n    f(m[:])\n}\n')
        c=run([str(compiler),str(src),str(out/(name+'.exe' if os.name=='nt' else name+'.bin'))])
        diagnostic='vibhag prakriyayah na pratyarpaniyah' if name=='typed-return' else 'E_KOSH_VIBHAG'
        row=dict(source=str(src),compile=c,pass_=c.get('exit')==1 and diagnostic in c.get('stdout',''))
        row['pass']=row.pop('pass_');r['cases'].append(row);save()
    for relative in ['examples/248_r23_slices.sm','examples/246_r23_comparator_sort.sm','tests/r133/indirect/safe1.sm']:
        src=ROOT/relative;exe=out/(src.stem+('.exe' if os.name=='nt' else '.bin'))
        c=run([str(compiler),str(src),str(exe)])
        execution=run([str(exe)]) if c.get('exit')==0 else {}
        expected='0\n99\n' if src.stem=='safe1' else (ROOT/'tests/expect'/(src.stem+'.out')).read_text(encoding='utf8')
        row=dict(source=relative,compile=c,run=execution)
        row['pass']=c.get('exit')==0 and execution.get('exit')==0 and execution.get('stdout','').replace('\r\n','\n')==expected
        r['cases'].append(row);save();print(src.name,'positive=',row['pass'],flush=True)
r['summary']=dict(total=len(r['cases']),passed=sum(c['pass'] for c in r['cases']))
save();print(json.dumps(r['summary']))
raise SystemExit(0 if a.baseline or all(c['pass'] for c in r['cases']) else 1)
