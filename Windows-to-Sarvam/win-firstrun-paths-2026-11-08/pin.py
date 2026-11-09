from pathlib import Path
import subprocess, hashlib, json, sys
root=Path.cwd(); out=root/'build/firstrun-2026-11-08'; out.mkdir(exist_ok=True)
sys.path.insert(0,str(root/'tools'))
from check_installer_version import embedded_payload
def sha(b): return hashlib.sha256(b).hexdigest()
commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
setup=subprocess.check_output(['git','show',commit+':Sutram-Setup.exe'])
assert sha(setup)==subprocess.check_output(['git','show',commit+':Sutram-Setup.sha256']).decode().split()[0]
z=embedded_payload(setup); names={n.replace('\\','/'):n for n in z.namelist()}
compiler=z.read(names['bin/sutram.exe'])
assert compiler==subprocess.check_output(['git','show',commit+':win/sutram.exe'])
(out/'Sutram-Setup.exe').write_bytes(setup)
(out/'embedded-sutram.exe').write_bytes(compiler)
p=subprocess.run([str(out/'embedded-sutram.exe'),'--version'],capture_output=True,timeout=10)
assert p.returncode==0 and b'(v312)' in p.stdout
(out/'version-stdout.txt').write_bytes(p.stdout); (out/'version-stderr.txt').write_bytes(p.stderr)
r={'commit':commit,'setup_sha256':sha(setup),'compiler_sha256':sha(compiler),'version':p.stdout.decode(),'payload':{n:sha(z.read(old)) for n,old in names.items() if not n.endswith('/')}}
(out/'candidate.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
for name in ['ui-helper.ps1','desktop-helper.ps1']:
 (out/name).write_bytes((root/'Windows-to-Sarvam/win-v312-2026-11-08'/name).read_bytes())
(out/'REQUEST.md').write_bytes(Path(r'%USERPROFILE%\Downloads\SUTRAM-WINDOWS-FIRSTRUN.md').read_bytes())
print(json.dumps({k:v for k,v in r.items() if k!='payload'},indent=2))
