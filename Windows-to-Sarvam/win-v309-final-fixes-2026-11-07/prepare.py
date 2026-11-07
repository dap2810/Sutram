from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[2]
old=root/'Windows-to-Sarvam/win-v309-fixes-2026-11-07'
out=Path(__file__).resolve().parent
(root/'build/native-v309-final-fix').mkdir(exist_ok=True)
for name in ['ui-helper.ps1','preserve.ps1','run-install.ps1','recovery-tests.ps1','identity.py','verify-saved.ps1','installed-smoke.py','compare-payloads.py','pin-fix-package.py','initial-install.ps1']:
    text=(old/name).read_text(encoding='utf-8-sig')
    text=text.replace('win-v309-fixes-2026-11-07','win-v309-final-fixes-2026-11-07').replace('native-v309-fix','native-v309-final-fix').replace('Sutram-v309-fix-','Sutram-v309-final-')
    text=text.replace('build/linux-payload-fixed/payload.zip','build/linux-payload-final/payload.zip')
    if name=='pin-fix-package.py':
        text=text.replace("=='05b23d56d40aaa4b71c6d67d13996d75da6e4d2e2b2ac47fbf4960a1a52fb481'",'')
    (out/name).write_text(text,encoding='utf8',newline='\n')
# Keep the already proven native Job Object probes with a new output directory and compiler pin.
text=(root/'Windows-to-Sarvam/win-v309-2026-11-07/probes.py').read_text(encoding='utf8')
text=text.replace('Unmodified native v309 compiler','Rebuilt native v309 compiler')
text=text.replace('build/windows-v309-2026-11-07','build/native-v309-final-fix')
text=text.replace("assert sha(compiler)=='05b23d56d40aaa4b71c6d67d13996d75da6e4d2e2b2ac47fbf4960a1a52fb481'", "assert sha(compiler)==json.loads((HERE/'candidate.json').read_text())['compiler_sha256']")
(out/'probes.py').write_text(text,encoding='utf8',newline='\n')
fixture=root/'build/lock-fixture-ed113d00892c4a688ee72076bb21dbdc'
for name in ['results.json','blocked.json','after-owner.json','child.ps1']:
    shutil.copyfile(fixture/name,out/('lock-'+name))
