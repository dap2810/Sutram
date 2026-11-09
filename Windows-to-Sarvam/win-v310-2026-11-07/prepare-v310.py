from pathlib import Path
import shutil
base=Path(__file__).resolve().parent.parent
root=base/'build/windows-v310-acceptance'
out=root/'Windows-to-Sarvam/win-v310-2026-11-07'
out.mkdir(parents=True,exist_ok=True)
work=root/'build/native-v310';work.mkdir(parents=True,exist_ok=True)
old=root/'Windows-to-Sarvam/win-v309-integrated-2026-11-07'
for name in ['ui-helper.ps1','run-install.ps1','preserve.ps1','identity.py','pin-fix-package.py','initial-install.ps1','verify-saved.ps1']:
    text=(old/name).read_text(encoding='utf8').replace('v309-integrated','v310').replace('v309','v310').replace('1.0.309','1.0.310')
    (out/name).write_text(text,encoding='utf8',newline='\n')
shutil.copy2(base/'build/prepare-v310.py',out/'prepare-v310.py')
shutil.copy2(Path('%USERPROFILE%/Downloads/SUTRAM-WINDOWS-V310.md'),out/'REQUEST.md')
print(out)
