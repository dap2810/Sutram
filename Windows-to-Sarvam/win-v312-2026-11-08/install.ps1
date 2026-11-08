param([ValidateSet('licence','complete')][string]$Phase='licence',[ValidateSet('initial','capture-retry','reinstall')][string]$Name='initial')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot;$Root=Split-Path (Split-Path $OutDir -Parent) -Parent
. (Join-Path $OutDir 'desktop-helper.ps1')
$script:captureWarnings=@();$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
$setup=Join-Path $Root 'build/native-v312/Sutram-Setup.exe'
$candidate=Get-Content (Join-Path $OutDir 'candidate.json') -Raw|ConvertFrom-Json
if((Get-FileHash -LiteralPath $setup).Hash -ne $candidate.setup_sha256){throw 'Setup hash differs'}
$record=Join-Path $OutDir ($Name+'-install.json')
function Save {[IO.File]::WriteAllText($record,($r|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))}
function Click([int]$Id){$h=[SutramIde]::GetDlgItem($main,$Id);if($h -eq [IntPtr]::Zero){throw "Missing control $Id"};[void][SutramIde]::PostMessageW($h,0xF5,[IntPtr]::Zero,[IntPtr]::Zero);Start-Sleep -Milliseconds 250}
if($Phase -eq 'licence'){
 if(Test-Path -LiteralPath $record){throw 'Record exists; do not overwrite'}
 if(Test-Path -LiteralPath $install){throw 'Expected absent active install'}
 $r=[ordered]@{name=$Name;started=[DateTime]::Now.ToString('o');setup=$setup;setup_sha256=$candidate.setup_sha256;phase='licence';screens=@()}
 $wizard=Start-Process -FilePath $setup -WorkingDirectory $Root -WindowStyle Normal -PassThru
 $r.pid=$wizard.Id;$r.process_started=$wizard.StartTime.ToString('o')
 $main=Wait-Until {[SutramIde]::WindowsOf($wizard.Id,'SutramWizardWindow')|Select-Object -First 1} 15000
 if(-not $main){throw 'No setup window'};$r.handle=$main.ToInt64()
 Click 2002
 $edit=[SutramIde]::GetDlgItem($main,2012)
 $r.licence_text=[SutramIde]::Text($edit)
 [IO.File]::WriteAllText((Join-Path $OutDir ($Name+'-licence.txt')),$r.licence_text,[Text.UTF8Encoding]::new($false))
 $r.display_line_count=[SutramIde]::Send($edit,0xBA,0,0,3000)
 $r.accepted=[SutramIde]::Send([SutramIde]::GetDlgItem($main,2010),0xF0,0,0,3000)
 foreach($position in @('top','middle','sanskrit','bottom')){
   [void][SutramIde]::Send($edit,0xB6,0,-10000,3000)
   if($position -eq 'middle'){[void][SutramIde]::Send($edit,0xB6,0,[int]($r.display_line_count/2)-4,3000)}
   if($position -eq 'sanskrit'){[void][SutramIde]::Send($edit,0xB6,0,32,3000)}
   if($position -eq 'bottom'){[void][SutramIde]::Send($edit,0xB6,0,10000,3000)}
   Start-Sleep -Milliseconds 250;Foreground $main
   if(-not [SutramIde]::IsWindowVisible($edit)){throw 'Licence control no longer visible; page changed'}
   $r.screens+=@{position=$position;first_visible_line=[SutramIde]::Send($edit,0xCE,0,0,3000);file=(Shot $main ($Name+'-licence-'+$position))}
 }
 [void][SutramIde]::Send($edit,0xB6,0,-10000,3000)
 $r.capture_warnings=@($script:captureWarnings);Save
 Write-Host "Stopped at unaccepted licence page; PID $($wizard.Id); $($r.display_line_count) display lines."
 exit
}
$r=Get-Content -LiteralPath $record -Encoding UTF8 -Raw|ConvertFrom-Json
if($r.phase -ne 'licence'){throw 'Installation was already continued'}
$wizard=Get-Process -Id $r.pid
if($wizard.StartTime.ToString('o') -ne $r.process_started){throw 'Process identity changed'}
$main=[IntPtr]$r.handle
$r|Add-Member -NotePropertyName observations -NotePropertyValue @()
$r|Add-Member -NotePropertyName continued -NotePropertyValue ([DateTime]::Now.ToString('o'))
Click 2010;Click 2002
if([SutramIde]::Text([SutramIde]::GetDlgItem($main,2020)) -ne $install){throw 'Unexpected install location'}
Click 2002;Click 2002
$watch=[Diagnostics.Stopwatch]::StartNew();Click 2002;$child=$null;$last=-5
while($watch.Elapsed.TotalSeconds -lt 180){
 if(-not $child){$cp=Get-CimInstance Win32_Process -Filter "ParentProcessId = $($wizard.Id)"|Where-Object {$_.Name -eq 'powershell.exe'}|Select-Object -First 1
  if($cp){$child=Get-Process -Id $cp.ProcessId;[void]$child.Handle;$r|Add-Member -NotePropertyName child -NotePropertyValue @{pid=$child.Id;started=$child.StartTime.ToString('o');command=$cp.CommandLine};Save}}
 $dialogs=@([SutramIde]::WindowsOf($wizard.Id,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)})
 if($dialogs.Count){$r|Add-Member -NotePropertyName error_dialog -NotePropertyValue ([AcceptanceWindow]::VisibleTexts($dialogs[0]));Save;throw 'Installer error dialog; left open'}
 $label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002))
 if($label -eq 'Finish'){
  $r|Add-Member -NotePropertyName finish_seconds -NotePropertyValue $watch.Elapsed.TotalSeconds
  $r|Add-Member -NotePropertyName finish_screenshot -NotePropertyValue (Shot $main ($Name+'-finish'))
  if([SutramIde]::Send([SutramIde]::GetDlgItem($main,2060),0xF0,0,0,3000) -eq 1){Click 2060}
  Click 2002;$r|Add-Member -NotePropertyName closed_after_finish -NotePropertyValue $wizard.WaitForExit(5000)
  if($child){[void]$child.WaitForExit(5000);$r|Add-Member -NotePropertyName child_exit -NotePropertyValue $child.ExitCode}
  $r.phase='finished';Save
  if(-not $r.closed_after_finish -or $r.child_exit -ne 0){throw 'Install did not close successfully'}
  python (Join-Path $OutDir 'identity.py') --name ($Name+'-identity')
  if($LASTEXITCODE){throw 'STOP: installed identity differs from v312'}
  Write-Host "Installed v312; Finish in $($r.finish_seconds) s.";exit
 }
 if($watch.Elapsed.TotalSeconds-$last -ge 5){$r.observations+=@{seconds=$watch.Elapsed.TotalSeconds;next=$label};Save;$last=$watch.Elapsed.TotalSeconds}
 Start-Sleep -Milliseconds 150
}
Save;throw 'Observation timed out; installer left running'
