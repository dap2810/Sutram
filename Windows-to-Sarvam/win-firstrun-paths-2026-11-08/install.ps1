$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
$candidate=Get-Content (Join-Path $OutDir 'candidate.json') -Encoding UTF8 -Raw|ConvertFrom-Json
$setup=Join-Path $OutDir 'Sutram-Setup.exe';$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
if((Get-FileHash -LiteralPath $setup).Hash -ne $candidate.setup_sha256){throw 'Setup hash mismatch'}
if(Test-Path -LiteralPath $install){throw 'Install directory exists'}
$record=Join-Path $OutDir 'install.json';if(Test-Path -LiteralPath $record){throw 'Record exists'}
$r=[ordered]@{time=[DateTime]::Now.ToString('o');setup_sha256=$candidate.setup_sha256;pages=@()}
function Save{[IO.File]::WriteAllText($record,($r|ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false))}
function Click($id){$c=[SutramIde]::GetDlgItem($main,$id);if($c -eq [IntPtr]::Zero){throw "Missing control $id"};[void][SutramIde]::PostMessageW($c,0xF5,[IntPtr]::Zero,[IntPtr]::Zero);Start-Sleep -Milliseconds 300}
function Page($name){Foreground $main;$r.pages+=@{name=$name;text=[AcceptanceWindow]::VisibleTexts($main);screenshot=(Shot $main ('install-'+$name))};Save}
$env:Path=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
$wizard=Start-Process -FilePath $setup -WorkingDirectory $OutDir -WindowStyle Normal -PassThru
$r.pid=$wizard.Id;$r.started=$wizard.StartTime.ToString('o');Save
$main=Wait-Until {[SutramIde]::WindowsOf($wizard.Id,'SutramWizardWindow')|Select-Object -First 1} 15000
if(-not $main){throw 'Wizard absent'};$r.handle=$main.ToInt64();Page 'welcome';Click 2002;Page 'licence'
Click 2010;Click 2002;Page 'location'
if([SutramIde]::Text([SutramIde]::GetDlgItem($main,2020)) -ne $install){throw 'Unexpected location'}
Click 2002
$pathControl=[SutramIde]::GetDlgItem($main,2030);$deskControl=[SutramIde]::GetDlgItem($main,2031)
$r.path_label=[SutramIde]::Text($pathControl);$r.path_default=[SutramIde]::Send($pathControl,0xF0,0,0,3000)
$r.desktop_label=[SutramIde]::Text($deskControl);$r.desktop_default=[SutramIde]::Send($deskControl,0xF0,0,0,3000);Page 'options-default'
if($r.path_default -eq 1){Click 2030};if($r.desktop_default -eq 0){Click 2031}
$r.path_selected=[SutramIde]::Send($pathControl,0xF0,0,0,3000);$r.desktop_selected=[SutramIde]::Send($deskControl,0xF0,0,0,3000)
if($r.path_selected -ne 0 -or $r.desktop_selected -ne 1){throw 'Options not set'};Page 'options-selected';Click 2002;Page 'ready'
$watch=[Diagnostics.Stopwatch]::StartNew();Click 2002;$child=$null
while($watch.Elapsed.TotalSeconds -lt 180){
 if(-not $child){$cp=Get-CimInstance Win32_Process -Filter "ParentProcessId = $($wizard.Id)"|Where-Object {$_.Name -eq 'powershell.exe'}|Select-Object -First 1;if($cp){$child=Get-Process -Id $cp.ProcessId;[void]$child.Handle;$r.child=@{pid=$child.Id;started=$child.StartTime.ToString('o')};Save}}
 $dialogs=@([SutramIde]::WindowsOf($wizard.Id,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)})
 if($dialogs.Count){$r.error_dialog=[AcceptanceWindow]::VisibleTexts($dialogs[0]);Save;throw 'Installer error dialog; left open'}
 if([SutramIde]::Text([SutramIde]::GetDlgItem($main,2002)) -eq 'Finish'){
  $r.seconds=$watch.Elapsed.TotalSeconds;Page 'finish'
  if([SutramIde]::Send([SutramIde]::GetDlgItem($main,2060),0xF0,0,0,3000) -eq 1){Click 2060};Click 2002
  $r.closed=$wizard.WaitForExit(5000);if($child){[void]$child.WaitForExit(5000);$r.child_exit=$child.ExitCode}
  $r.user_path=[Environment]::GetEnvironmentVariable('Path','User');$r.capture_warnings=$script:captureWarnings;Save
  Copy-Item -LiteralPath (Join-Path $install 'install.log') -Destination (Join-Path $OutDir 'install-engine.log')
  if(-not $r.closed -or $r.child_exit -ne 0){throw 'Installation did not complete'}
  Write-Host "Finished in $($r.seconds) seconds; PATH declined, desktop requested.";exit
 }
 Start-Sleep -Milliseconds 200
}
Save;throw 'Installation timed out; left running'
