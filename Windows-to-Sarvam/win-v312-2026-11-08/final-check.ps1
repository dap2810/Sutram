$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'desktop-helper.ps1')
$expected=@()
foreach($file in @('initial-install.json','capture-retry-install.json','reinstall-install.json','observer-process.json')){
 $r=Get-Content -LiteralPath (Join-Path $OutDir $file) -Raw|ConvertFrom-Json
 $expected+=@{file=$file;pid=$r.pid;started=if($r.process_started){$r.process_started}else{$r.started}}
 if($r.child){$expected+=@{file=$file;pid=$r.child.pid;started=$r.child.started}}
}
$obs=Get-Content -LiteralPath (Join-Path $OutDir 'uninstall-observer.json') -Raw|ConvertFrom-Json
foreach($p in $obs.processes){$expected+=@{file='uninstall-observer.json';pid=$p.pid;started=$p.started}}
$rows=@();foreach($e in $expected){$p=Get-Process -Id $e.pid -ErrorAction SilentlyContinue;$rows+=@{evidence=$e.file;pid=$e.pid;expected_start=$e.started;same_process_alive=($p -and $p.StartTime.ToString('o') -eq $e.started)}}
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
$baseline=@([AcceptanceWindow]::All()|Where-Object {$_.handle -in $obs.baseline_console_handles}|ForEach-Object {$p=Get-Process -Id $_.pid -ErrorAction SilentlyContinue;@{handle=$_.handle;pid=$_.pid;class=$_.cls;title=$_.title;path=$p.Path;started=if($p){$p.StartTime.ToString('o')}else{$null}}})
$r=[ordered]@{time=[DateTime]::Now.ToString('o');os=(Get-CimInstance Win32_OperatingSystem|Select-Object Caption,Version,BuildNumber);elevated_admin_token=$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator);processes=$rows;preexisting_console_windows_identified_after_test=$baseline;surviving_sutram_processes=@(Get-Process|Where-Object {$_.ProcessName -match '^Sutram'}|Select-Object Id,ProcessName,Path);temp_residue_still_exists=(Test-Path -LiteralPath '%USERPROFILE%\AppData\Local\Temp\STM7C1C.tmp')}
[IO.File]::WriteAllText((Join-Path $OutDir 'final-check.json'),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
$r|ConvertTo-Json -Depth 8
