from pathlib import Path
import hashlib,json,os,subprocess,winreg
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WORK=ROOT/'build/windows-v307-2026-11-06'
WORK.mkdir(parents=True,exist_ok=True)
installed=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
parts=[]
for hive,key in [(winreg.HKEY_LOCAL_MACHINE,r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'),(winreg.HKEY_CURRENT_USER,'Environment')]:
    with winreg.OpenKey(hive,key) as k: parts.append(os.path.expandvars(winreg.QueryValueEx(k,'Path')[0]))
env=os.environ.copy();env['PATH']=';'.join(parts)
def run(cmd):
    p=subprocess.run(list(map(str,cmd)),cwd=WORK,env=env,capture_output=True,timeout=30)
    return dict(command=list(map(str,cmd)),cwd=str(WORK),exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'))
r=dict(commit=run(['git','-C',ROOT,'rev-parse','HEAD'])['stdout'].strip(),setup_sha256=sha(ROOT/'Sutram-Setup.exe'),
       shell_path=env['PATH'],where=run([os.environ['COMSPEC'],'/d','/c','where sutram']),version=run([os.environ['COMSPEC'],'/d','/c','sutram --version']),
       installed_compiler_sha256=sha(installed/'bin/sutram.exe'),repo_compiler_sha256=sha(ROOT/'win/sutram.exe'),
       installed_ide_sha256=sha(installed/'sutram-ide-gui.exe'),checks=[])
manifest=installed/'payload.manifest.sha256'
r['manifest_present']=manifest.is_file()
for line in manifest.read_text(encoding='utf-8-sig').splitlines() if manifest.is_file() else []:
    want,name=line.split(' *',1);p=installed/name;actual=sha(p) if p.is_file() else None
    r['checks'].append(dict(file=name,expected=want.lower(),actual=actual,pass_=actual==want.lower()))
r['identity_pass']=r['where']['exit']==0 and r['where']['stdout'].strip().lower()==str(installed/'bin/sutram.exe').lower() and r['version']['exit']==0 and r['version']['stdout'].splitlines()[:1]==['Sutram 1.0 (v307) - sampurna sutra'] and r['installed_compiler_sha256']==r['repo_compiler_sha256']
r['manifest']=dict(total=len(r['checks']),passed=sum(x['pass_'] for x in r['checks']),failures=[x for x in r['checks'] if not x['pass_']])
(HERE/'identity.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in r.items() if k!='checks'},indent=2))
raise SystemExit(0 if r['identity_pass'] and r['manifest_present'] and not r['manifest']['failures'] else 1)
