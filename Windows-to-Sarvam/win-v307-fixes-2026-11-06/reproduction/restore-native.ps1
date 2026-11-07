param([string]$Phase='upgrade',[switch]$PreserveOnly)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$out=Join-Path $root 'Windows-to-Sarvam\win-v307-fixes-2026-11-06'
$before=Get-Content -LiteralPath (Join-Path $out 'before.json') -Raw|ConvertFrom-Json
$report=Get-Content -LiteralPath (Join-Path $out ($Phase+'.json')) -Raw|ConvertFrom-Json
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs'))
$installed=Join-Path $parent 'Sutram';$backup=[IO.Path]::GetFullPath($before.backup)
$saved=Join-Path $parent ('Sutram-review-'+$Phase+'-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss'))
foreach($p in @($installed,$backup,$saved)){if([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($p)) -ne $parent){throw 'Unsafe restoration path'}}
if(Test-Path -LiteralPath $saved){throw 'Existing destination'}
foreach($p in @($installed,$backup)){
    $walk=$p;while($walk){if((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'};$walk=[IO.Path]::GetDirectoryName($walk)}
    if(Get-ChildItem -LiteralPath $p -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1){throw 'Reparse content'}
}
foreach($f in $before.files){if((Get-FileHash -LiteralPath (Join-Path $backup $f.relative)).Hash -ne $f.sha256){throw 'Backup hash mismatch'}}
$stopped=@()
# Stop only these recorded test processes, including a suspended engine. Never resume it.
foreach($target in @(@{id=$report.child.pid;start=$report.child.started;cmd=$report.child.command},@{id=$report.pid;start=$report.process_started;exe=$report.setup})){
    $actual=Get-CimInstance Win32_Process -Filter "ProcessId = $($target.id)"
    if(-not $actual){continue}
    $p=Get-Process -Id $target.id
    if($p.StartTime.ToString('o') -ne $target.start){throw 'Process identity mismatch'}
    if($target.cmd -and $actual.CommandLine -ne $target.cmd){throw 'Command mismatch'}
    if($target.exe -and $actual.ExecutablePath -ne $target.exe){throw 'Executable mismatch'}
    Stop-Process -InputObject $p -Force
    if(-not $p.WaitForExit(5000)){throw 'Process did not exit'}
    $stopped+=$target.id
}
Start-Sleep -Seconds 8 # let the observer record the owned process exit before preserving evidence
if($report.engine_log -and (Test-Path -LiteralPath $report.engine_log)){Copy-Item -LiteralPath $report.engine_log -Destination (Join-Path $out ($Phase+'-after-stop.log')) -Force}
Move-Item -LiteralPath $installed -Destination $saved
if(-not $PreserveOnly){
    Copy-Item -LiteralPath $backup -Destination $installed -Recurse
    foreach($f in $before.files){if((Get-FileHash -LiteralPath (Join-Path $installed $f.relative)).Hash -ne $f.sha256){throw 'Restoration hash mismatch'}}
}
$result=@{phase=$Phase;time=[DateTime]::Now.ToString('o');stopped=$stopped;preserved=$saved;restored=(-not $PreserveOnly);files_verified=$before.file_count;user_path_unchanged=([Environment]::GetEnvironmentVariable('Path','User') -eq $before.user_path);security_changed=$false}
[IO.File]::WriteAllText((Join-Path $out ('restore-'+$Phase+'.json')),($result|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
$result|ConvertTo-Json
