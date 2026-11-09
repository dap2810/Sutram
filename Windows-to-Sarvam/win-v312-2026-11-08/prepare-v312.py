from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parent/'windows-v312'
OUT=ROOT/'Windows-to-Sarvam/win-v312-2026-11-08'
OUT.mkdir(parents=True,exist_ok=True)
(ROOT/'build/native-v312').mkdir(parents=True,exist_ok=True)
OLD=ROOT/'Windows-to-Sarvam/win-v311-acceptance-2026-11-07'
for name in ['ui-helper.ps1','desktop-helper.ps1','pin-fix-package.py','identity.py','time-suite.py']:
    text=(OLD/name).read_text(encoding='utf8').replace('win-v311-acceptance-2026-11-07','win-v312-2026-11-08').replace('native-v311-acceptance','native-v312').replace('(v311)','(v312)').replace('1.0.311','1.0.312')
    if name=='time-suite.py':
        text=text.replace('User was invited to exercise Settings uninstall concurrently; this is not a controlled compiler microbenchmark.','Run after reinstall and identity verification, without concurrent installer work; one sample, not a controlled compiler microbenchmark.')
    (OUT/name).write_text(text,encoding='utf8',newline='\n')
text=(OLD/'state.ps1').read_text(encoding='utf8').split("if(Test-Path -LiteralPath (Join-Path $out 'clear-active-state.json'))")[0]
text=text.replace("[ValidateSet('snapshot','clear')]","[ValidateSet('snapshot')]").replace('native-v311-acceptance','native-v312')
(OUT/'state.ps1').write_text(text,encoding='utf8',newline='\n')
shutil.copy2('%USERPROFILE%/Downloads/SUTRAM-WINDOWS-V312.md',OUT/'REQUEST.md')
shutil.copy2(__file__,OUT/'prepare-v312.py')
print(OUT)
