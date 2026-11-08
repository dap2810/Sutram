from pathlib import Path
import os,subprocess,json,time,hashlib,ctypes
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
WORK=ROOT/'build/native-v312/budget';WORK.mkdir(parents=True,exist_ok=True)
COMP=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram/bin/sutram.exe'
ctypes.windll.kernel32.SetErrorMode(0x8003)
assert hashlib.sha256(COMP.read_bytes()).hexdigest()==json.loads((HERE/'candidate.json').read_text())['compiler_sha256']
rows=[]
for shape in ['literal','variable','global-variable']:
    for count in [10000,20000]:
        term='1' if shape=='literal' else 'z'
        expr='+'.join([term]*count)
        text=f'mukhya() {{\n    likha({expr})\n}}\n' if shape=='literal' else (f'mukhya() {{\n    vitti z = 1\n    likha({expr})\n}}\n' if shape=='variable' else f'vitti z = 1\nvitti g = {expr}\nmukhya() {{\n    likha(g)\n}}\n')
        name=f'{shape}-{count}';source=HERE/(name+'.sm');source.write_text(text,encoding='utf8',newline='\n')
        target=WORK/(name+'.exe');assert not target.exists(),'Never reuse a stale output'
        cmd=[str(COMP),str(source),str(target)];started=time.perf_counter()
        p=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=120)
        r=dict(name=name,terms=count,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),command=cmd,compile_exit=p.returncode,compile_seconds=time.perf_counter()-started,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'),output_exists=target.exists())
        (HERE/(name+'-stdout.txt')).write_bytes(p.stdout);(HERE/(name+'-stderr.txt')).write_bytes(p.stderr)
        if count==10000:
            r['pass']=p.returncode==0 and target.exists()
            if r['pass']:
                run=subprocess.run([str(target)],capture_output=True,timeout=15)
                r.update(run_exit=run.returncode,run_stdout=run.stdout.decode('utf8','replace'),run_stderr=run.stderr.decode('utf8','replace'),output_sha256=hashlib.sha256(target.read_bytes()).hexdigest())
                r['pass']=run.returncode==0 and run.stdout.replace(b'\r\n',b'\n')==b'10000\n'
        else:r['pass']=p.returncode==1 and not target.exists() and '[E_VAKYA_SEEMA]' in r['stderr']+r['stdout'] and '65536' in r['stderr']+r['stdout']
        rows.append(r);print(json.dumps(r),flush=True)
        (HERE/'budget.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8')
raise SystemExit(0 if all(r['pass'] for r in rows) else 1)
