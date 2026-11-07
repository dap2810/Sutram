$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot;. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
$target=Join-Path $env:LOCALAPPDATA 'Programs\Sutram\Sutram-Uninstall.exe'
$r=[ordered]@{started=[DateTime]::Now.ToString('o');method='User invokes uninstall in Settings; observer reads only matching uninstaller/child processes and their visible dialogs.';processes=@();dialogs=@();observations=@()}
$seen=@{};$watch=[Diagnostics.Stopwatch]::StartNew();$known=@();$last=-5
function Save{[IO.File]::WriteAllText((Join-Path $OutDir 'uninstall-observer.json'),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))}
while($watch.Elapsed.TotalSeconds -lt 600){
 $apps=@(Get-CimInstance Win32_Process -Filter "Name = 'Sutram-Uninstall.exe'"|Where-Object {$_.ExecutablePath -eq $target})
 foreach($a in $apps){if(-not $seen.ContainsKey([int]$a.ProcessId)){$p=Get-Process -Id $a.ProcessId -ErrorAction SilentlyContinue;if($p){[void]$p.Handle;$known+=,$p;$seen[[int]$p.Id]=$true;$r.processes+=@{role='uninstaller';pid=$p.Id;started=$p.StartTime.ToString('o');parent=$a.ParentProcessId;command=$a.CommandLine};Save}}}
 foreach($parent in @($r.processes|Where-Object {$_.role -eq 'uninstaller'})){
  foreach($a in @(Get-CimInstance Win32_Process -Filter "ParentProcessId = $($parent.pid)"|Where-Object {$_.Name -eq 'powershell.exe'})){
   if(-not $seen.ContainsKey([int]$a.ProcessId)){$p=Get-Process -Id $a.ProcessId -ErrorAction SilentlyContinue;if($p){[void]$p.Handle;$known+=,$p;$seen[[int]$p.Id]=$true;$r.processes+=@{role='engine';pid=$p.Id;started=$p.StartTime.ToString('o');parent=$a.ParentProcessId;command=$a.CommandLine};$m=[regex]::Match($a.CommandLine,'-LogPath\s+"([^"]+)"');if($m.Success){$r.log_path=$m.Groups[1].Value};Save}}
  }
 }
 foreach($p in @($known)){
  if(-not $p.HasExited){foreach($h in [SutramIde]::WindowsOf($p.Id,'#32770')){if([SutramIde]::IsWindowVisible($h) -and $h.ToInt64() -notin @($r.dialogs|ForEach-Object {$_.handle})){$r.dialogs+=@{time=[DateTime]::Now.ToString('o');pid=$p.Id;handle=$h.ToInt64();text=[AcceptanceWindow]::VisibleTexts($h);screenshot=(Shot $h ('uninstall-dialog-'+$r.dialogs.Count))};Save}}}
 }
 if($watch.Elapsed.TotalSeconds-$last -gt 5){$r.observations+=@{seconds=$watch.Elapsed.TotalSeconds;install_exists=(Test-Path -LiteralPath (Split-Path $target -Parent));uninstall_key_exists=(Test-Path -LiteralPath HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram)};Save;$last=$watch.Elapsed.TotalSeconds}
 if($known.Count -gt 0 -and @($known|Where-Object {-not $_.HasExited}).Count -eq 0){break}
 if(Test-Path (Join-Path $OutDir 'stop-uninstall-observer.flag')){break}
 Start-Sleep -Milliseconds 250
}
$r.ended=[DateTime]::Now.ToString('o');$r.process_results=@($known|ForEach-Object {$p=$_;if($p.HasExited){$p.WaitForExit()};@{pid=$p.Id;exited=$p.HasExited;exit=if($p.HasExited){$p.ExitCode}else{$null}}})
if($r.Contains('log_path') -and (Test-Path -LiteralPath $r.log_path)){Copy-Item -LiteralPath $r.log_path -Destination (Join-Path $OutDir 'uninstall-engine.log')}
$r.capture_warnings=@($script:captureWarnings);Save
Write-Host "Uninstall observer recorded $($r.processes.Count) processes and $($r.dialogs.Count) dialogs; no process was stopped."
