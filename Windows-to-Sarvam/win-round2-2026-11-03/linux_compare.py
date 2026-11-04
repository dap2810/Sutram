import hashlib,json,os,platform,subprocess,time
from pathlib import Path
h=Path(__file__).resolve().parent
root=h.parents[1]/'build/windows-v297/source'
compiler=root/'sutram_compiler'
def run(args):
    start=time.monotonic()
    try:
        p=subprocess.run([str(a) for a in args],cwd=root,capture_output=True,timeout=5)
        return dict(command=[str(a) for a in args],exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),stdout_hex=p.stdout.hex(),seconds=time.monotonic()-start)
    except (OSError,subprocess.TimeoutExpired) as e:
        return dict(command=[str(a) for a in args],error=str(e),seconds=time.monotonic()-start)
out=dict(host=platform.platform(),uid=os.getuid(),compiler=str(compiler),compiler_sha256=hashlib.sha256(compiler.read_bytes()).hexdigest(),version=run([compiler,'--version']),rows=[])
assert os.getuid()!=0
for name in ('C1','C2'):
    source=h/'programs'/(name+'.sm');binary=h/'programs'/(name+'.bin')
    row=dict(name=name,compile=run([compiler,source,binary]))
    if row['compile'].get('exit')==0:row['run']=run([binary])
    out['rows'].append(row)
(h/'linux-results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps(out,indent=2))
