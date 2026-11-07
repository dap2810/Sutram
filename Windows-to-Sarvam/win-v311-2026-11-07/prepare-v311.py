from pathlib import Path
import shutil
base=Path(__file__).resolve().parent.parent
old=base/'build/windows-v310-acceptance/Windows-to-Sarvam/win-v310-2026-11-07'
root=base/'build/windows-v311-verification';out=root/'Windows-to-Sarvam/win-v311-2026-11-07'
out.mkdir(parents=True,exist_ok=True);(root/'build/native-v311').mkdir(parents=True,exist_ok=True)
names=['ui-helper.ps1','run-install.ps1','preserve.ps1','identity.py','pin-fix-package.py','initial-install.ps1','verify-saved.ps1','compiler-probes.py','supplemental.py','ownership.py','ownership-controller.ps1']
for name in names:
    text=(old/name).read_text(encoding='utf8').replace('v310','v311').replace('1.0.310','1.0.311')
    if name=='compiler-probes.py':
        text=text.replace("['E_KOSH_GANIT','E_KOSH_DVARA']","['E_KOSH_GANIT','E_KOSH_DVARA','E_VIBHAG_ANKA']")
        text=text.replace("('local-direct',f+'mukhya() { vitti g = make_kosh()\\n likha(g[0]) }\\n','refusal')","('local-direct',f+'mukhya() { vitti g = make_kosh()\\n likha(g[0]) }\\n','7\\n')")
    if name=='supplemental.py':text=text.replace('# A local kosh binding is explicitly supported by r126_ret_kind. The initial\n# optional probe incorrectly expected refusal; execute its already-built output.','# Execute the supported local kosh binding again as a positive control.')
    (out/name).write_text(text,encoding='utf8',newline='\n')
shutil.copy2(base/'build/prepare-v311.py',out/'prepare-v311.py')
shutil.copy2(old/'REQUEST.md',out/'REQUEST.md')
print(out)
