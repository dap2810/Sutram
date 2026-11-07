param([ValidatePattern('^[a-z0-9-]+$')][string]$Name='first-install')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot;$Root=Split-Path (Split-Path $OutDir -Parent) -Parent
. (Join-Path $OutDir 'desktop-helper.ps1')
$setup=Join-Path $Root 'build\native-v311-acceptance\Sutram-Setup.exe';$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
$candidate=Get-Content (Join-Path $OutDir 'candidate.json') -Raw|ConvertFrom-Json
if((Get-FileHash $setup).Hash -ne $candidate.setup_sha256){throw 'Setup hash changed'}
if(Test-Path -LiteralPath $install){throw 'First-install test needs absent active destination'}
$r=[ordered]@{name=$Name;started=[DateTime]::Now.ToString('o');setup=$setup;setup_sha256=$candidate.setup_sha256;pages=@();console_observations=@();observations=@();console_detection='Visible top-level console/Terminal windows sampled during wizard run; sub-sample transients cannot be excluded.'}
$wizard=$null;$child=$null;$launchedIde=$null;$script:captureWarnings=@();$baseline=@([AcceptanceWindow]::All()|Where-Object {$_.cls -match 'Console|CASCADIA'}|ForEach-Object {$_.handle})
function Save{[IO.File]::WriteAllText((Join-Path $OutDir ($Name+'.json')),($r|ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false))}
function Consoles{foreach($w in [AcceptanceWindow]::All()|Where-Object {$_.cls -match 'Console|CASCADIA'}){if($w.handle -notin $baseline -and $w.handle -notin @($r.console_observations|ForEach-Object {$_.handle})){$r.console_observations+=@{time=[DateTime]::Now.ToString('o');handle=$w.handle;pid=$w.pid;class=$w.cls;title=$w.title}}}}
function Click([int]$Id){$h=[SutramIde]::GetDlgItem($main,$Id);if($h -eq [IntPtr]::Zero){throw "Control $Id absent"};[void][SutramIde]::PostMessageW($h,0xF5,[IntPtr]::Zero,[IntPtr]::Zero);Start-Sleep -Milliseconds 180;Consoles}
function Page([string]$Label){$row=[ordered]@{page=$Label;text=[AcceptanceWindow]::VisibleTexts($main);screenshot=(Shot $main ($Name+'-'+$Label))};$r.pages+=,$row;Save}
try{
 $wizard=Start-Process -FilePath $setup -WorkingDirectory $Root -WindowStyle Normal -PassThru;[void]$wizard.Handle;$r.pid=$wizard.Id;$r.process_started=$wizard.StartTime.ToString('o')
 $main=Wait-Until {[SutramIde]::WindowsOf($wizard.Id,'SutramWizardWindow')|Select-Object -First 1} 15000
 if(-not $main){throw 'Wizard did not open'}
 Page 'welcome';Click 2002;Page 'licence'
 $r.licence_initially_accepted=[SutramIde]::Send([SutramIde]::GetDlgItem($main,2010),0xF0,0,0,3000)
 Click 2010;Click 2002;$r.destination=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2020));Page 'location'
 if($r.destination -ne $install){throw 'Unexpected default destination'}
 Click 2002;$r.default_add_path=[SutramIde]::Send([SutramIde]::GetDlgItem($main,2030),0xF0,0,0,3000);$r.default_desktop=[SutramIde]::Send([SutramIde]::GetDlgItem($main,2031),0xF0,0,0,3000);Page 'options'
 Click 2002;Page 'ready';$watch=[Diagnostics.Stopwatch]::StartNew();Click 2002;$lastUI=-1;$lastRecord=-5
 while($watch.Elapsed.TotalSeconds -lt 970){
   Consoles
   if(-not $child){$p=Get-CimInstance Win32_Process -Filter "ParentProcessId = $($wizard.Id)"|Where-Object {$_.Name -eq 'powershell.exe'}|Select-Object -First 1
     if($p){$child=Get-Process -Id $p.ProcessId;[void]$child.Handle;$r.child=@{pid=$child.Id;started=$child.StartTime.ToString('o');command=$p.CommandLine};$m=[regex]::Match($p.CommandLine,'-LogPath\s+"([^"]+)"');if($m.Success){$r.engine_log=$m.Groups[1].Value};Save}}
   if($watch.Elapsed.TotalSeconds-$lastUI -ge .35){
     $dialogs=@([SutramIde]::WindowsOf($wizard.Id,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)})
     if($dialogs.Count){$r.status='ERROR_DIALOG';$r.dialog=[AcceptanceWindow]::VisibleTexts($dialogs[0]);$r.error_screenshot=Shot $dialogs[0] ($Name+'-error');[void][SutramIde]::PostMessageW([SutramIde]::GetDlgItem($dialogs[0],1),0xF5,[IntPtr]::Zero,[IntPtr]::Zero);[void]$wizard.WaitForExit(5000);break}
     try{$label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002))}catch{$label='UI unresponsive'}
     if($label -eq 'Finish'){
       $r.status='FINISH';$r.finish_seconds=$watch.Elapsed.TotalSeconds;$r.launch_ide_default=[SutramIde]::Send([SutramIde]::GetDlgItem($main,2060),0xF0,0,0,3000);Page 'finish'
       Start-Sleep -Milliseconds 1000;$r.closed_before_finish_click=$wizard.HasExited
       $existing=@(Get-Process -Name sutram-ide-gui -ErrorAction SilentlyContinue|ForEach-Object {$_.Id});Click 2002;$r.closed_after_finish_click=$wizard.WaitForExit(5000)
       $launchedIde=Wait-Until {Get-Process -Name sutram-ide-gui -ErrorAction SilentlyContinue|Where-Object {$_.Id -notin $existing -and $_.Path -eq (Join-Path $install 'sutram-ide-gui.exe')}|Select-Object -First 1} 7000
       if($launchedIde){$r.default_launched_ide=@{pid=$launchedIde.Id;started=$launchedIde.StartTime.ToString('o');path=$launchedIde.Path};$ih=Wait-Until {[SutramIde]::WindowsOf($launchedIde.Id,'SutramNativeGUIWindow')|Select-Object -First 1} 5000;if($ih){$r.ide_launch_screenshot=Shot $ih ($Name+'-default-ide');[void][SutramIde]::PostMessageW($ih,0x10,[IntPtr]::Zero,[IntPtr]::Zero)};[void]$launchedIde.WaitForExit(5000)}
       break
     }
     if($watch.Elapsed.TotalSeconds-$lastRecord -ge 5){$r.observations+=@{seconds=$watch.Elapsed.TotalSeconds;label=$label;child_exited=($child -and $child.HasExited)};Save;$lastRecord=$watch.Elapsed.TotalSeconds}
     if($wizard.HasExited){$r.status='EXIT_WITHOUT_FINISH';break};$lastUI=$watch.Elapsed.TotalSeconds
   };Start-Sleep -Milliseconds 100
 }
 if(-not $r.Contains('status')){$r.status='OBSERVER_LIMIT_AFTER_970_SECONDS'}
 $r.total_observed_seconds=$watch.Elapsed.TotalSeconds
}catch{$r.observer_error=$_.Exception.ToString();$r.status='OBSERVER_ERROR';throw}
finally{
 $r.stopped_in_cleanup=@()
 foreach($p in @($launchedIde,$child,$wizard)){if($p -and -not $p.HasExited){$p.Kill();[void]$p.WaitForExit(5000);$r.stopped_in_cleanup+=$p.Id}}
 $r.wizard_exited=($wizard -and $wizard.HasExited);$r.child_exited=($child -and $child.HasExited);if($child -and $child.HasExited){$child.WaitForExit();$r.child_exit=$child.ExitCode}
 $r.default_ide_exited=($launchedIde -and $launchedIde.HasExited)
 $log=Join-Path $install 'install.log';if($r.Contains('engine_log') -and [IO.File]::Exists($r.engine_log)){$log=$r.engine_log}
 if([IO.File]::Exists($log)){[IO.File]::WriteAllBytes((Join-Path $OutDir ($Name+'-engine.log')),[IO.File]::ReadAllBytes($log))}
 $r.capture_warnings=@($script:captureWarnings);$r.ended=[DateTime]::Now.ToString('o');Save
}
Write-Host "$Name $($r.status), engine=$($r.child_exit), Finish=$($r.finish_seconds), consoles=$($r.console_observations.Count)"
if($r.status -ne 'FINISH' -or $r.child_exit -ne 0){throw 'Install did not complete; preserved original remains available'}
python (Join-Path $OutDir 'identity.py') --name ($Name+'-identity')
if($LASTEXITCODE){throw 'STOP: installed v311 identity differs from the expected candidate'}
