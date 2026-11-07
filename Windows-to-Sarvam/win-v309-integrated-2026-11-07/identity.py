from pathlib import Path
import os,subprocess,hashlib,json,winreg,argparse
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--name',default='identity');a=ap.parse_args()
installed=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram'
work=ROOT/'build/native-v309-integrated';parts=[]
for hive,key in [(winreg.HKEY_LOCAL_MACHINE,r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'),(winreg.HKEY_CURRENT_USER,'Environment')]:
    with winreg.OpenKey(hive,key) as k:parts.append(os.path.expandvars(winreg.QueryValueEx(k,'Path')[0]))
env=dict(os.environ,PATH=';'.join(parts));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
def run(cmd):
    p=subprocess.run(cmd,cwd=work,env=env,capture_output=True,timeout=15)
    return dict(command=cmd,exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'))
r=dict(where=run([os.environ['COMSPEC'],'/d','/c','where sutram']),version=run([os.environ['COMSPEC'],'/d','/c','sutram --version']),installed_compiler_sha256=sha(installed/'bin/sutram.exe'),repo_compiler_sha256=sha(ROOT/'win/sutram.exe'),checks=[])
for line in (installed/'payload.manifest.sha256').read_text(encoding='utf-8-sig').splitlines():
    expected,name=line.split(' *',1);actual=sha(installed/name);r['checks'].append(dict(file=name,expected=expected.lower(),actual=actual,pass_=actual==expected.lower()))
with winreg.OpenKey(winreg.HKEY_CURRENT_USER,r'Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram') as k:r['display_version']=winreg.QueryValueEx(k,'DisplayVersion')[0]
r['pending_exists']=(installed/'payload.pending.sha256').exists();r['transaction_exists']=installed.with_name('Sutram.sutram-transaction').exists()
r['manifest_passed']=sum(x['pass_'] for x in r['checks']);r['manifest_total']=len(r['checks'])
r['pass']=r['where']['exit']==0 and r['where']['stdout'].strip().lower()==str(installed/'bin/sutram.exe').lower() and r['version']['exit']==0 and r['version']['stdout'].splitlines()[0]=='Sutram 1.0 (v309) - sampurna sutra' and r['installed_compiler_sha256']==r['repo_compiler_sha256'] and r['manifest_total']==657 and r['manifest_passed']==657 and not r['pending_exists'] and not r['transaction_exists'] and r['display_version']=='1.0.309'
candidate=json.loads((HERE/'candidate.json').read_text(encoding='utf8'))
r['installed_manifest_sha256']=sha(installed/'payload.manifest.sha256')
r['installed_uninstaller_sha256']=sha(installed/'Sutram-Uninstall.exe')
r['candidate_matches']=r['installed_manifest_sha256']==candidate['manifest_sha256'] and r['installed_uninstaller_sha256']==candidate['setup_sha256']
r['pass']=r['pass'] and r['candidate_matches']
(HERE/(a.name+'.json')).write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in r.items() if k!='checks'},indent=2));raise SystemExit(0 if r['pass'] else 1)
