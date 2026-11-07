from pathlib import Path
out=Path(__file__).resolve().parent;root=out.parents[1]
s=(root/'Windows-to-Sarvam/win-v306-2026-11-06/ide.ps1').read_text(encoding='utf-8-sig')
s=s.replace("'identity.json'","'initial-identity.json'").replace('$identity.identity_pass','$identity.pass')
s=s.replace('v306','v309-final')
s=s.replace('build\\windows-v309-final-2026-11-06\\ide-save-guard','build\\native-v309-final-fix\\ide-save-guard')
s=s.replace("if((Get-FileHash -LiteralPath $ide).Hash -ne $identity.installed_ide_sha256)","$candidate=Get-Content -LiteralPath (Join-Path $OutDir 'candidate.json') -Raw|ConvertFrom-Json\n$ideHash=($candidate.checks|Where-Object {$_.file -eq 'sutram-ide-gui.exe'}).actual\nif((Get-FileHash -LiteralPath $ide).Hash -ne $ideHash)")
extra='''
    $program="vitti zero = 0`nvitti leaked = make_kosh() + zero`nprakriya make_kosh() { kosh k[1] kosh_kship(k, 7) nivartanam k }`nmukhya() { likha(leaked) }`n"
    [SutramIde]::SetText($editor,$program)
    [void][SutramIde]::Send($main,0x111,2002,0,30000)
    [void][SutramIde]::Send($main,0x111,2010,0,30000)
    $negative=Snapshot 'C3-global-refusal' $true
    $r.c3_pass=$negative.output.Contains('E_KOSH_GANIT') -and -not $negative.output.Contains('Namaste')
'''
s=s.replace('} catch { $r.error=',extra+'} catch { $r.error=')
s=s.replace('$r.c1_pass -and $r.c2_pass -and $r.originals_unchanged','$r.c1_pass -and $r.c2_pass -and $r.c3_pass -and $r.originals_unchanged')
(out/'ide.ps1').write_text(s,encoding='utf8',newline='\n')
