# R153 (ChatGPT R218 follow-up, Sarvam R153 WS1): shortcut ownership, run against real .lnk files with the
# installer's own code - Set-OwnedShortcut and its helpers, the desktop selection statement from install-core.ps1,
# and the shortcut removal statement from uninstall-core.ps1, taken by their syntax trees (as the other fixtures
# here do). Everything happens in a folder under build\; the real desktop and Start menu are not touched.
#
#   1  a user's own "Sutram IDE.lnk" with the IDE's target and their own arguments: install keeps its bytes and makes
#      "Sutram IDE (Sutram).lnk"; uninstall removes that one and keeps the user's, byte for byte (v314 deleted it)
#   2  this installer's link, retargeted by the user, then a reinstall: the changed link is kept byte for byte and a
#      fresh name is used; uninstall keeps it (v314 overwrote it on reinstall)
#   3  both usual names taken: both kept, the installer's is "Sutram IDE (Sutram 2).lnk"
#   4  an empty desktop: "Sutram IDE.lnk" is made and uninstall removes it; the Notepad collision of the v312 run:
#      the user's kept, the installer's made under the second name and removed by uninstall
#   5  a record from before v315 (no hash): never adopted - kept, and a fresh name used - even when the link says
#      exactly what this installer writes, and when only its description or hotkey changed (ChatGPT R220)
#   6  the box unchecked on a reinstall: the installer's unchanged link goes, a changed one stays
#
# Written in the Linux container, where PowerShell could not be run: NOT RUN by its author. For the native run:
#   powershell -NoProfile -ExecutionPolicy Bypass -File tests\windows\test_installer_shortcuts.ps1
$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
function Parse-Engine([string]$Path){$t=$null;$e=$null;$a=[Management.Automation.Language.Parser]::ParseFile($Path,[ref]$t,[ref]$e);if($e.Count){throw ($e|Out-String)};return $a}
$ast=Parse-Engine (Join-Path $root 'windows\native-installer\install-core.ps1')
$uast=Parse-Engine (Join-Path $root 'windows\native-installer\uninstall-core.ps1')
foreach($name in @('Log','Get-Sha','Get-OldShortcutRecord','Test-OwnedShortcut','Set-OwnedShortcut','Remove-OwnedShortcut')){
    $f=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name},$true)
    if(-not $f){throw ('Missing function '+$name)}
    . ([ScriptBlock]::Create($f.Extent.Text))
}
$desk=@($ast.FindAll({param($n) $n -is [Management.Automation.Language.IfStatementAst] -and $n.Extent.Text.StartsWith('if ($DesktopShortcut) {')},$true))
if($desk.Count -ne 1){throw 'Could not identify the desktop selection statement'}
$desk=[ScriptBlock]::Create($desk[0].Extent.Text)
$unlink=@($uast.FindAll({param($n) $n -is [Management.Automation.Language.IfStatementAst] -and $n.Extent.Text.StartsWith("if (`$state.ContainsKey('OwnedShortcuts')) {")},$true))
if($unlink.Count -ne 1){throw 'Could not identify the uninstaller shortcut removal statement'}
$unlink=[ScriptBlock]::Create($unlink[0].Extent.Text)

$work=Join-Path $root ('build\shortcut-fixture-'+[guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($work)
$LogPath=Join-Path $work 'run.log'
$shell=New-Object -ComObject WScript.Shell
$checks=[ordered]@{}
$notepad=Join-Path $env:WINDIR 'notepad.exe'

function New-Case([string]$Name){
    $c=@{Dir=(Join-Path $work $Name)}
    $c.Install=Join-Path $c.Dir 'Sutram'; $c.Desktop=Join-Path $c.Dir 'Desktop'; $c.Start=Join-Path $c.Dir 'StartMenu\Programs\Sutram'
    foreach($d in @($c.Install,$c.Desktop,$c.Start)){[void][IO.Directory]::CreateDirectory($d)}
    $c.Gui=Join-Path $c.Install 'sutram-ide-gui.exe'; [IO.File]::WriteAllBytes($c.Gui,[byte[]](77,90))
    $c.Icon=Join-Path $c.Install 'assets\sutram.ico'
    $c.State=@{}
    return $c
}
function User-Link([string]$Path,[string]$Target,[string]$Arguments){
    $sc=$shell.CreateShortcut($Path); $sc.TargetPath=$Target; if($Arguments){$sc.Arguments=$Arguments}; $sc.Save()
    return [IO.File]::ReadAllBytes($Path)
}
function Same([string]$Path,[byte[]]$Bytes){ return ([IO.File]::Exists($Path) -and [Convert]::ToBase64String([IO.File]::ReadAllBytes($Path)) -eq [Convert]::ToBase64String($Bytes)) }
# One install's desktop step, as install-core.ps1 runs it, with the variables it gives it; returns the new state.
function Install-Desktop($c,[bool]$Want){
    $oldState=$c.State
    $script:ownedShortcuts=New-Object Collections.Generic.List[string]
    $DesktopShortcut=$Want; $desktopDir=$c.Desktop; $guiInstalled=$c.Gui; $InstallDir=$c.Install; $icon=$c.Icon
    $previousDesktopOwned=($oldState.ContainsKey('DesktopOwned') -and $oldState['DesktopOwned'] -eq '1')
    $previousDesktopName='Sutram IDE.lnk'
    if($oldState.ContainsKey('DesktopLink') -and $oldState['DesktopLink']){$previousDesktopName=$oldState['DesktopLink']}
    $desktopName=''; $desktopOwned=$false
    . $desk
    $c.State=@{OwnedShortcuts=($script:ownedShortcuts.ToArray() -join ','); DesktopOwned=([string][int]$desktopOwned); DesktopLink=$desktopName}
    return $desktopName
}
function Uninstall($c){ $state=$c.State; $startMenu=$c.Start; $desktopDir=$c.Desktop; $InstallDir=$c.Install; . $unlink }

# 1
$c=New-Case 'user-same-target'; $u=Join-Path $c.Desktop 'Sutram IDE.lnk'; $ub=User-Link $u $c.Gui '--my-own-argument'
$made=Install-Desktop $c $true
$checks.c1_install_keeps_user_bytes=(Same $u $ub)
$checks.c1_installer_uses_second_name=($made -eq 'Sutram IDE (Sutram).lnk' -and [IO.File]::Exists((Join-Path $c.Desktop $made)))
$checks.c1_state_does_not_claim_the_user_link=(-not ($c.State['OwnedShortcuts'] -split ',' | Where-Object { $_.StartsWith([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($u))+'|') }))
Uninstall $c
$checks.c1_uninstall_keeps_user_bytes=(Same $u $ub)
$checks.c1_uninstall_removes_its_own=(-not [IO.File]::Exists((Join-Path $c.Desktop 'Sutram IDE (Sutram).lnk')))
# 2
$c=New-Case 'retargeted'; $made=Install-Desktop $c $true
$own=Join-Path $c.Desktop $made; $rb=User-Link $own $notepad ''
$made2=Install-Desktop $c $true
$checks.c2_reinstall_keeps_changed_bytes=(Same $own $rb)
$checks.c2_reinstall_uses_fresh_name=($made -eq 'Sutram IDE.lnk' -and $made2 -eq 'Sutram IDE (Sutram).lnk')
Uninstall $c
$checks.c2_uninstall_keeps_changed_bytes=(Same $own $rb)
# 3
$c=New-Case 'both-taken'; $a=Join-Path $c.Desktop 'Sutram IDE.lnk'; $b=Join-Path $c.Desktop 'Sutram IDE (Sutram).lnk'
$ab=User-Link $a $notepad ''; $bb=User-Link $b $c.Gui ''
$made=Install-Desktop $c $true
$checks.c3_both_kept=((Same $a $ab) -and (Same $b $bb))
$checks.c3_third_name=($made -eq 'Sutram IDE (Sutram 2).lnk')
Uninstall $c
$checks.c3_uninstall_keeps_both=((Same $a $ab) -and (Same $b $bb) -and -not [IO.File]::Exists((Join-Path $c.Desktop $made)))
# 4
$c=New-Case 'empty'; $made=Install-Desktop $c $true
$checks.c4_empty_desktop_made=($made -eq 'Sutram IDE.lnk' -and [IO.File]::Exists((Join-Path $c.Desktop $made)))
Uninstall $c
$checks.c4_empty_desktop_removed=(-not [IO.File]::Exists((Join-Path $c.Desktop 'Sutram IDE.lnk')))
$c=New-Case 'notepad'; $n=Join-Path $c.Desktop 'Sutram IDE.lnk'; $nb=User-Link $n $notepad ''
$made=Install-Desktop $c $true; Uninstall $c
$checks.c4_notepad_kept_ours_removed=((Same $n $nb) -and $made -eq 'Sutram IDE (Sutram).lnk' -and -not [IO.File]::Exists((Join-Path $c.Desktop $made)))
# 5
$c=New-Case 'legacy'; $l=Join-Path $c.Desktop 'Sutram IDE.lnk'
$sc=$shell.CreateShortcut($l); $sc.TargetPath=$c.Gui; $sc.WorkingDirectory=$c.Install; $sc.IconLocation=$c.Icon; $sc.Save(); $lb=[IO.File]::ReadAllBytes($l)
$c.State=@{OwnedShortcuts=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($l)); DesktopOwned='1'; DesktopLink='Sutram IDE.lnk'}
$made=Install-Desktop $c $true
$checks.c5_legacy_template_kept_not_adopted=((Same $l $lb) -and $made -eq 'Sutram IDE (Sutram).lnk')
Uninstall $c
$checks.c5_legacy_template_survives_uninstall=(Same $l $lb)
$c=New-Case 'legacy-description'; $l=Join-Path $c.Desktop 'Sutram IDE.lnk'
$sc=$shell.CreateShortcut($l); $sc.TargetPath=$c.Gui; $sc.WorkingDirectory=$c.Install; $sc.IconLocation=$c.Icon; $sc.Description='my own'; $sc.Hotkey='CTRL+ALT+S'; $sc.Save(); $lb=[IO.File]::ReadAllBytes($l)
$c.State=@{OwnedShortcuts=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($l)); DesktopOwned='1'; DesktopLink='Sutram IDE.lnk'}
[void](Install-Desktop $c $false)
$checks.c5_legacy_description_kept_when_unchecked=(Same $l $lb)
$made=Install-Desktop $c $true; Uninstall $c
$checks.c5_legacy_description_kept_through_reinstall_and_uninstall=((Same $l $lb) -and $made -eq 'Sutram IDE (Sutram).lnk')
# 6
$c=New-Case 'unchecked'; $made=Install-Desktop $c $true; [void](Install-Desktop $c $false)
$checks.c6_unchecked_removes_unchanged=(-not [IO.File]::Exists((Join-Path $c.Desktop $made)))
$c=New-Case 'unchecked-changed'; $made=Install-Desktop $c $true; $own=Join-Path $c.Desktop $made; $cb=User-Link $own $notepad ''
[void](Install-Desktop $c $false)
$checks.c6_unchecked_keeps_changed=(Same $own $cb)

foreach($key in $checks.Keys){Write-Output ((@('FAIL','PASS')[[int][bool]$checks[$key]])+' '+$key)}
[IO.File]::WriteAllText((Join-Path $work 'results.json'),($checks|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
Write-Output ('Evidence: '+$work)
if($checks.Values -contains $false){exit 1}
