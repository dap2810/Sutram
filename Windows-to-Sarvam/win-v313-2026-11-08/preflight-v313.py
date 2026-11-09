from pathlib import Path
import subprocess,hashlib,json,sys,shutil,os,datetime
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08'
OUT.mkdir(parents=True,exist_ok=True)
WORK=ROOT/'build/windows-v313-preflight/artifacts';WORK.mkdir(parents=True,exist_ok=True)
ref='108301e2'
def blob(path):return subprocess.check_output(['git','show',ref+':'+path],cwd=ROOT)
def sha(data):return hashlib.sha256(data).hexdigest()
sys.path.insert(0,str(ROOT/'tools'))
from check_installer_version import embedded_payload
data=blob('Sutram-Setup.exe');(WORK/'available-Sutram-Setup.exe').write_bytes(data)
z=embedded_payload(data);names={n.replace('\\','/'):n for n in z.namelist()}
compiler=z.read(names['bin/sutram.exe']);(WORK/'available-sutram.exe').write_bytes(compiler)
p=subprocess.run([str(WORK/'available-sutram.exe'),'--version'],capture_output=True,timeout=15)
installed=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram/bin/sutram.exe'
i=subprocess.run([str(installed),'--version'],capture_output=True,timeout=15)
r={'checked_at':datetime.datetime.now().astimezone().isoformat(),'source_commit':subprocess.check_output(['git','rev-parse',ref],cwd=ROOT,text=True).strip(),'available_setup_sha256':sha(data),'available_compiler_sha256':sha(compiler),'repo_compiler_matches_payload':blob('win/sutram.exe')==compiler,'available_version':{'exit':p.returncode,'stdout':p.stdout.decode('utf8'),'stderr':p.stderr.decode('utf8')},'installed_compiler_sha256':sha(installed.read_bytes()),'installed_version':{'exit':i.returncode,'stdout':i.stdout.decode('utf8'),'stderr':i.stderr.decode('utf8')},'required_version':'Sutram 1.0 (v313) - sampurna sutra','v313_available':b'(v313)' in p.stdout,'installation_attempted':False}
(OUT/'availability.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8',newline='\n')
shutil.copy2('%USERPROFILE%/Downloads/SUTRAM-WINDOWS-V313.md',OUT/'REQUEST.md')
for name in ['ui-helper.ps1','desktop-helper.ps1']:
    shutil.copy2(ROOT/'Windows-to-Sarvam/win-v312-2026-11-08'/name,OUT/name)
shutil.copy2(__file__,OUT/'preflight-v313.py')
print(json.dumps(r,indent=2))
