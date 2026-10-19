"""Validate fail-closed preflight on an isolated copy of manifested inputs."""
from pathlib import Path
import subprocess,shutil,uuid
ROOT=Path(__file__).resolve().parents[1]
work=ROOT/'build/windows'/('preflight-'+uuid.uuid4().hex)
manifest=ROOT/'windows/windows-build-integrity.sha256'
for line in manifest.read_text(encoding='utf8').splitlines():
    relative=line.split(' *',1)[1]
    target=work/relative;target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(ROOT/relative,target)
copy=work/'windows/windows-build-integrity.sha256'
shutil.copyfile(manifest,copy)
original=copy.read_bytes()
def check(name,ok,needle=''):
    cmd=['powershell.exe','-NoProfile','-File',str(work/'windows/preflight-windows.ps1')]
    x=subprocess.run(cmd,capture_output=True,timeout=40)
    output=(x.stdout+x.stderr).decode('utf8','replace')
    print('$ '+' '.join(cmd)+'\n'+output+'EXIT '+str(x.returncode),flush=True)
    assert (x.returncode==0)==ok and needle in output,name
    print('PASS '+name,flush=True)
check('clean source copy',True,'PREFLIGHT PASS')
source=work/'win/pe_layout.inc';saved=source.read_bytes()
source.write_bytes(saved+b'\n; modified\n')
check('altered source',False,'Source integrity mismatch')
source.write_bytes(saved)
source.unlink()
check('missing source',False,'Missing source')
source.write_bytes(saved)
copy.write_bytes(original+original.splitlines(keepends=True)[0])
check('duplicate source row',False,'Duplicate source path')
copy.write_text('0'*64+' *../outside.asm\n',encoding='utf8')
check('manifest traversal',False,'Unsafe source path')
copy.write_bytes(original)
extra=work/'lib/unexpected.smlib';extra.write_text('unexpected',encoding='utf8')
check('unmanifested payload input',False,'Unmanifested build/payload input')
print('PREFLIGHT_GUARDS_PASS; isolated fixtures retained at '+str(work))
