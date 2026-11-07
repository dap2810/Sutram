from pathlib import Path
import os,subprocess,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
work=ROOT/'build/native-v309-fix/installed-smoke';work.mkdir(exist_ok=True)
source=work/'library.sm';source.write_text('yoj ganit\n\nmukhya() { likha(varg(9)) }\n',encoding='utf8')
installed=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram'
rows=[]
for layout in ['bin','win']:
    target=work/(layout+'.exe')
    command=[str(installed/layout/'sutram.exe'),str(source),str(target)]
    c=subprocess.run(command,cwd=work,capture_output=True,timeout=15)
    r=subprocess.run([str(target)],cwd=work,capture_output=True,timeout=10) if c.returncode==0 else None
    rows.append(dict(layout=layout,compile_command=command,cwd=str(work),compile_exit=c.returncode,compile_stdout=c.stdout.decode(),compile_stderr=c.stderr.decode(),run_exit=r.returncode if r else None,stdout=r.stdout.decode() if r else '',stderr=r.stderr.decode() if r else '',pass_=bool(r and r.returncode==0 and r.stdout==b'81\n' and not r.stderr)))
(HERE/'installed-smoke.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8')
print(json.dumps(rows,indent=2));assert all(r['pass_'] for r in rows)
