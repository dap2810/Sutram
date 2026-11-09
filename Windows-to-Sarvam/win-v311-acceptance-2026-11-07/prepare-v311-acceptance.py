from pathlib import Path
import shutil
base=Path(__file__).resolve().parent.parent;root=base/'build/windows-v311-acceptance'
out=root/'Windows-to-Sarvam/win-v311-acceptance-2026-11-07';out.mkdir(parents=True,exist_ok=True)
(root/'build/native-v311-acceptance').mkdir(parents=True,exist_ok=True)
old=root/'Windows-to-Sarvam/win-v311-2026-11-07'
for name in ['ui-helper.ps1','preserve.ps1','pin-fix-package.py','identity.py']:
    text=(old/name).read_text(encoding='utf8').replace('win-v311-2026-11-07','win-v311-acceptance-2026-11-07').replace('native-v311','native-v311-acceptance')
    if name=='preserve.ps1':text=text.replace("'Sutram-v311-'","'Sutram-v311-acceptance-'")
    (out/name).write_text(text,encoding='utf8',newline='\n')
shutil.copy2('%USERPROFILE%/Downloads/SUTRAM-WINDOWS-V311-ACCEPTANCE.md',out/'REQUEST.md')
shutil.copy2(__file__,out/'prepare-v311-acceptance.py')
print(out)
