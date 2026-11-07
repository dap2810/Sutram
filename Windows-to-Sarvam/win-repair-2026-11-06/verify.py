"""Check the installed package and execute installed samples from unrelated CWD."""
from pathlib import Path
import hashlib,json,os,subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WORK=ROOT/'build/windows-repair-2026-11-06'
WORK.mkdir(parents=True,exist_ok=True)
installed=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=json.loads((HERE/'before.json').read_text(encoding='utf8'))
after=json.loads((HERE/'after.json').read_text(encoding='utf8'))
backup=json.loads((HERE/'backup.json').read_text(encoding='utf8'))
env=os.environ.copy()
env['PATH']=os.path.expandvars(after['machine']['value']+';'+after['user']['value'])
def run(cmd):
    p=subprocess.run(list(map(str,cmd)),cwd=WORK,env=env,capture_output=True,timeout=15)
    return dict(command=list(map(str,cmd)),cwd=str(WORK),exit=p.returncode,
                stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'))
checks=[]
for line in (installed/'payload.manifest.sha256').read_text(encoding='utf-8-sig').splitlines():
    expected,relative=line.split(' *',1)
    path=installed/relative
    actual=sha(path) if path.is_file() else None
    checks.append(dict(path=relative,expected=expected.lower(),actual=actual,pass_=actual==expected.lower()))
samples=[]
for name,want in [('01_hello','Namaste, Sutram!\n'),('02_arith','x + y = 30\n'),('79_ayojan_cwd','81\n')]:
    target=WORK/(name+'.exe')
    c=run([installed/'bin/sutram.exe',installed/'examples'/(name+'.sm'),target])
    r=run([target]) if c['exit']==0 else None
    samples.append(dict(name=name,compile=c,run=r,pass_=bool(r and r['exit']==0 and r['stdout']==want)))
where=run(['where.exe','sutram'])
version=run([os.environ['COMSPEC'],'/d','/c','sutram --version'])
data=dict(package=dict(entries=len(checks),matching=sum(x['pass_'] for x in checks),failures=[x for x in checks if not x['pass_']]),
          compiler_sha256=sha(installed/'bin/sutram.exe'),ide_sha256=sha(installed/'sutram-ide-gui.exe'),
          uninstaller_sha256=sha(installed/'Sutram-Uninstall.exe'),
          backup_intact=all(sha(Path(backup['backup'])/r['path'])==r['sha256'].lower() for r in before['tree']),
          machine_path_unchanged=before['machine']==after['machine'],user_path_unchanged=before['user']==after['user'],
          where=where,version=version,samples=samples,registration=after['registration'],manifest_checks=checks)
data['pass']=all(x['pass_'] for x in checks) and all(x['pass_'] for x in samples) and data['backup_intact'] and version['exit']==0 and where['stdout'].strip().lower()==str(installed/'bin/sutram.exe').lower()
(HERE/'verification.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in data.items() if k not in ['manifest_checks','samples']},indent=2))
raise SystemExit(0 if data['pass'] else 1)
