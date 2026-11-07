from pathlib import Path
import subprocess,json,os,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];out=HERE/'fixtures';out.mkdir(exist_ok=True)
ps=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe';rows=[]
for name in ['boundaries','reuse','lock']:
    command=[str(ps),'-NoLogo','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(ROOT/'tests/windows'/('test_installer_'+name+'.ps1'))]
    p=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=180,creationflags=subprocess.CREATE_NO_WINDOW)
    (out/(name+'-stdout.txt')).write_bytes(p.stdout);(out/(name+'-stderr.txt')).write_bytes(p.stderr)
    row=dict(name=name,command=command,exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'));rows.append(row)
    print(name,row['exit'],row['stdout'],row['stderr'],flush=True)
(out/'commands.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8')
for prefix in ['boundary-fixture-','reuse-fixture-','lock-fixture-']:
    for folder in (ROOT/'build').glob(prefix+'*'):
        if folder.is_dir():shutil.copytree(folder,out/folder.name)
raise SystemExit(any(r['exit'] for r in rows))
