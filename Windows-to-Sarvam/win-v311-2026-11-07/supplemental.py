from pathlib import Path
import ctypes,json,subprocess,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];WORK=ROOT/'build/native-v311'
out=HERE/'supplemental';out.mkdir(exist_ok=True);targets=WORK/'supplemental';targets.mkdir(exist_ok=True)
compiler=ROOT/'win/sutram.exe';ctypes.windll.kernel32.SetErrorMode(0x8003)
def run(cmd):
    p=subprocess.run(list(map(str,cmd)),cwd=ROOT,capture_output=True,timeout=15)
    return dict(command=list(map(str,cmd)),exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'))
rows=[]
for name in ['add','xor']:
    src=out/('original-'+name+'.sm');src.write_bytes((ROOT/'Windows-to-Sarvam/win-v307-fixes-2026-11-06/wrapper-comparison'/(name+'.sm')).read_bytes())
    exe=targets/('original-'+name+'.exe');assert not exe.exists()
    c=run([compiler,src,exe]);rows.append(dict(name='original-'+name,compile=c,output_exists=exe.exists(),pass_=c['exit']==1 and not exe.exists() and '[E_VIBHAG_ANKA]' in c['stdout']+c['stderr']))
src=out/'default-argument-untyped.sm';src.write_text('prakriya f(n = 5) { nivartanam n }\nmukhya() { likha(f()) }\n',encoding='utf8')
exe=targets/'default-argument-untyped.exe';assert not exe.exists();c=run([compiler,src,exe]);rows.append(dict(name='default-argument-untyped',compile=c,output_exists=exe.exists()))
# Execute the supported local kosh binding again as a positive control.
rows.append(dict(name='local-kosh-binding-positive',run=run([WORK/'expressions/local-direct.exe'])))
(out/'results.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8');print(json.dumps(rows,indent=2))
