from pathlib import Path
import os,json,hashlib,subprocess,winreg
here=Path(__file__).resolve().parent
install=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram'
c=json.loads((here/'candidate.json').read_text()); before=json.loads((here/'preserve.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
matches={n:sha(install/n)==v for n,v in c['payload'].items()}
def pathval(hive,key):
 with winreg.OpenKey(hive,key) as k:return winreg.QueryValueEx(k,'Path')[0]
user=pathval(winreg.HKEY_CURRENT_USER,'Environment')
machine=pathval(winreg.HKEY_LOCAL_MACHINE,r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment')
env=os.environ.copy();env['PATH']=os.path.expandvars(machine+';'+user)
def run(args):
 p=subprocess.run(args,cwd=here,env=env,capture_output=True,timeout=15)
 return {'argv':args,'exit':p.returncode,'stdout':p.stdout.decode('utf8','replace'),'stderr':p.stderr.decode('utf8','replace')}
r={'payload_files':len(matches),'mismatches':[n for n,v in matches.items() if not v],'compiler_sha256':sha(install/'bin/sutram.exe'),'user_path_unchanged_from_test_baseline':user==before['test_user_path'],'sutram_on_user_path':str(install/'bin').lower() in user.lower(),'normal_cmd':run([os.environ['COMSPEC'],'/d','/c','sutram --version']),'full_path_recovery':run([str(install/'bin/sutram.exe'),'--version']),'book_present':(install/'docs/sutram-book-english.html').is_file()}
(here/'identity.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(r,indent=2))
assert not r['mismatches'] and r['user_path_unchanged_from_test_baseline'] and not r['sutram_on_user_path']
