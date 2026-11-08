"""Extract and identify a repository installer without installing it."""
from pathlib import Path
import argparse,subprocess,hashlib,json,sys,datetime,re

ap=argparse.ArgumentParser()
ap.add_argument('--repo',type=Path,default=Path.cwd())
ap.add_argument('--ref',default='origin/main')
a=ap.parse_args();root=a.repo.resolve();here=Path(__file__).resolve().parent
work=root/'build/windows-v313-preflight-current-2026-11-08'
work.mkdir(parents=True,exist_ok=True)
commit=subprocess.check_output(['git','rev-parse',a.ref],cwd=root,text=True).strip()
def blob(path):return subprocess.check_output(['git','show',commit+':'+path],cwd=root)
def sha(data):return hashlib.sha256(data).hexdigest()
sys.path.insert(0,str(root/'tools'))
from check_installer_version import embedded_payload
setup=blob('Sutram-Setup.exe')
declared=blob('Sutram-Setup.sha256').decode('utf8').split()[0]
assert sha(setup)==declared,'Repository setup checksum mismatch'
z=embedded_payload(setup)
names={name.replace('\\','/'):name for name in z.namelist()}
compiler=z.read(names['bin/sutram.exe'])
repo_compiler=blob('win/sutram.exe')
assert compiler==repo_compiler,'Embedded compiler differs from repository compiler'
compiler_path=work/'embedded-sutram.exe'
compiler_path.write_bytes(compiler)
cmd=[str(compiler_path),'--version']
p=subprocess.run(cmd,cwd=work,capture_output=True,timeout=15)
stdout=p.stdout.decode('utf8','replace');stderr=p.stderr.decode('utf8','replace')
m=re.search(r'^Sutram 1\.0 \(v(\d+)\) - sampurna sutra$',stdout,re.M)
version=int(m.group(1)) if m and p.returncode==0 else None
record={'checked_at':datetime.datetime.now().astimezone().isoformat(),'source_commit':commit,'setup_sha256':sha(setup),'declared_setup_sha256':declared,'embedded_compiler_sha256':sha(compiler),'repository_compiler_sha256':sha(repo_compiler),'command':cmd,'cwd':str(work),'exit':p.returncode,'stdout':stdout,'stderr':stderr,'embedded_version_number':version,'required_minimum_version':313,'may_proceed':version is not None and version>=313,'installation_attempted':False,'tasks_A_to_D_run':False}
(here/'preflight.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8',newline='\n')
(here/'version-stdout.txt').write_bytes(p.stdout)
(here/'version-stderr.txt').write_bytes(p.stderr)
print(json.dumps(record,indent=2))
