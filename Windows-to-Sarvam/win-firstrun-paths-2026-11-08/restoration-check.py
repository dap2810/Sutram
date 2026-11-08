from pathlib import Path
import winreg,json,sys,hashlib,os,subprocess
here=Path(__file__).resolve().parent
before=json.loads((here/'preserve.json').read_text())
def tree(path):
 try:k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,path)
 except FileNotFoundError:return None
 with k:
  values={};i=0
  while True:
   try:n,v,t=winreg.EnumValue(k,i)
   except OSError:break
   values[n]={'type':t,'value':v.hex() if isinstance(v,bytes) else v};i+=1
  children={};i=0
  while True:
   try:n=winreg.EnumKey(k,i)
   except OSError:break
   children[n]=tree(path+'\\'+n);i+=1
 return {'values':values,'children':children}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if sys.argv[1]=='before':
 r={'original_registry':{},'original_shortcuts':{}}
 for k in before['registry']:
  canonical=k['key'].replace('HKCU:\\','');parent=canonical.rsplit('\\',1)[0]
  r['original_registry'][canonical]=tree(parent+'\\'+k['preserved_name']) if k['existed'] else None
 for move in before['moves']:
  p=Path(move['backup'])
  r['original_shortcuts'][move['source']]={str(f.relative_to(p)):sha(f) for f in p.rglob('*') if f.is_file()} if p.is_dir() else {'':sha(p)}
 (here/'restoration-baseline.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
 print('Preserved registry and shortcut baseline recorded.')
else:
 r=json.loads((here/'restoration-baseline.json').read_text());checks={}
 for k,v in r['original_registry'].items():checks['registry:'+k]=tree(k)==v
 for base,files in r['original_shortcuts'].items():
  for rel,h in files.items():checks['shortcut:'+str(Path(base)/rel)]=sha(Path(base)/rel)==h
 for f in before['files']:checks['file:'+f['relative']]=sha(Path(before['install'])/f['relative'])==f['sha256'].lower()
 with winreg.OpenKey(winreg.HKEY_CURRENT_USER,'Environment') as k:user=winreg.QueryValueEx(k,'Path')[0]
 with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment') as k:machine=winreg.QueryValueEx(k,'Path')[0]
 # .NET expands REG_EXPAND_SZ while winreg returns its raw %SystemRoot% text.
 checks['user_path']=user==before['user_path'];checks['machine_path']=os.path.expandvars(machine)==before['machine_path']
 env=os.environ.copy();env['PATH']=os.path.expandvars(machine+';'+user)
 p=subprocess.run([env['COMSPEC'],'/d','/c','where sutram && sutram --version'],cwd=here,env=env,capture_output=True,timeout=10)
 result={'checks':len(checks),'failures':[k for k,v in checks.items() if not v],'fresh_cmd_exit':p.returncode,'fresh_cmd_stdout':p.stdout.decode(),'fresh_cmd_stderr':p.stderr.decode(),'desktop_fixture_removed_by_preservation':not Path(before['desktop']).exists()}
 (here/'restoration-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2));assert not result['failures'] and p.returncode==0
