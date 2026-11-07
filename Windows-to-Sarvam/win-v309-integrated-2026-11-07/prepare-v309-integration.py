from pathlib import Path
import subprocess,hashlib,json
root=Path(__file__).resolve().parents[1]
old=root/'Windows-to-Sarvam/win-v309-final-fixes-2026-11-07'
out=root/'Windows-to-Sarvam/win-v309-integrated-2026-11-07';out.mkdir(exist_ok=True)
(root/'build/native-v309-integrated').mkdir(exist_ok=True)
(out/'.gitattributes').write_text('* -text\n',encoding='utf8')
for name in ['ui-helper.ps1','preserve.ps1','run-install.ps1','identity.py','pin-fix-package.py','initial-install.ps1','verify-saved.ps1','compare-payloads.py']:
    s=(old/name).read_text(encoding='utf8')
    s=s.replace('win-v309-final-fixes-2026-11-07','win-v309-integrated-2026-11-07').replace('native-v309-final-fix','native-v309-integrated').replace('Sutram-v309-final-','Sutram-v309-integrated-')
    s=s.replace('build/linux-payload-final/payload.zip','build/linux-payload-integrated/payload.zip')
    (out/name).write_text(s,encoding='utf8',newline='\n')
equal={}
for name in ['src/sutram_compiler.asm','windows/native-installer/install-core.ps1','windows/native-installer/uninstall-core.ps1','windows/native-installer/sutram_wizard.asm','sutram-ide-gui.exe']:
    before=subprocess.check_output(['git','show','664ff188:'+name],cwd=root)
    after=subprocess.check_output(['git','show','HEAD:'+name],cwd=root)
    equal[name]=dict(identical=before==after,sha256=hashlib.sha256(after).hexdigest())
assert all(v['identical'] for v in equal.values())
assert hashlib.sha256((root/'win/sutram.exe').read_bytes()).hexdigest()=='bcb33e6dbb58c1e8556d29057c2f20128cc00f54e48cf860c7ea5496c0972532'
(out/'unchanged-product-code.json').write_text(json.dumps(equal,indent=2)+'\n',encoding='utf8')
print(out)
