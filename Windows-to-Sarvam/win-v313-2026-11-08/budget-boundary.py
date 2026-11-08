from pathlib import Path
import subprocess,os,hashlib,json,time,ctypes
HERE=Path(__file__).resolve().parent
WORK=HERE.parents[1]/'artifacts/budget';WORK.mkdir(parents=True,exist_ok=True)
COMP=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram/bin/sutram.exe'
availability=json.loads((HERE/'availability.json').read_text())
assert hashlib.sha256(COMP.read_bytes()).hexdigest()==availability['installed_compiler_sha256']
ctypes.windll.kernel32.SetErrorMode(0x8003)
version=subprocess.check_output([str(COMP),'--version']).decode('utf8')
rows={}
def probe(n):
    if n in rows:return rows[n]['status']
    expr='+'.join(['x']*n)
    text=f'mukhya() {{\n    vitti x = 1\n    vitti s = {expr}\n    likha(s)\n}}\n'
    source=HERE/f'boundary-{n}.sm';source.write_text(text,encoding='utf8',newline='\n')
    target=WORK/f'boundary-{n}.exe';assert not target.exists(),'No stale executable allowed'
    cmd=[str(COMP),str(source),str(target)];t=time.perf_counter()
    p=subprocess.run(cmd,capture_output=True,timeout=120)
    message=(p.stdout+p.stderr).decode('utf8','replace')
    status='COMPILES' if p.returncode==0 and target.is_file() else ('WALK_REFUSAL' if p.returncode==1 and not target.exists() and '[E_VAKYA_SEEMA]' in message else 'OTHER')
    r=dict(terms=n,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),command=cmd,exit=p.returncode,seconds=time.perf_counter()-t,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),output_exists=target.exists(),status=status)
    if status=='COMPILES':
        q=subprocess.run([str(target)],capture_output=True,timeout=15)
        r.update(run_exit=q.returncode,run_stdout=q.stdout.decode('utf8','replace'),run_stderr=q.stderr.decode('utf8','replace'))
        assert q.returncode==0 and q.stdout.replace(b'\r\n',b'\n')==f'{n}\n'.encode(),r
    rows[n]=r
    (HERE/'boundary-raw.json').write_text(json.dumps({'version':version,'compiler_sha256':availability['installed_compiler_sha256'],'scope':'PRE-FIX v312 only; v313 unavailable','probes':list(rows.values())},indent=2)+'\n',encoding='utf8',newline='\n')
    print(n,status,flush=True)
    assert status!='OTHER',r
    return status
lo,hi=8200,16400
assert probe(lo)=='COMPILES'
if probe(hi)=='COMPILES':hi=20000;assert probe(hi)=='WALK_REFUSAL'
while hi-lo>1:
    mid=(lo+hi)//2
    if probe(mid)=='COMPILES':lo=mid
    else:hi=mid
r={'version':version,'scope':'PRE-FIX v312 only; v313 unavailable','shape':'local vitti s = x+x+...; x=1; likha(s)','last_compiles':lo,'first_refuses':hi,'tested_probes':len(rows),'full_refusal_message':rows[hi]['stdout']+rows[hi]['stderr'],'all_compiled_outputs_verified':True}
(HERE/'boundary-summary.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps(r,indent=2))
