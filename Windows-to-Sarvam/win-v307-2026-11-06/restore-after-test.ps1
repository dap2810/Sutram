param([ValidateSet('upgrade','recovery')][string]$Phase)
$ErrorActionPreference='Stop'
$report=Get-Content -LiteralPath (Join-Path $PSScriptRoot ($Phase+'.json')) -Raw|ConvertFrom-Json
$prepName=if($Phase -eq 'upgrade'){'upgrade'}else{'interrupt'}
$saved=Get-Content -LiteralPath (Join-Path $PSScriptRoot ('prepare-'+$prepName+'.json')) -Raw|ConvertFrom-Json
if($report.status -eq 'FINISH'){throw 'Successful install does not need restoration'}
if(-not $report.status){throw 'Observer must finish first'}
if($report.status -like 'NO_RESULT*' -and $report.observed_seconds -lt 935){throw 'Observation is incomplete'}
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$src=[IO.Path]::GetFullPath((Join-Path $parent 'Sutram'))
$backup=[IO.Path]::GetFullPath([string]$saved.backup)
$partial=[IO.Path]::GetFullPath((Join-Path $parent ('Sutram-v307-'+$Phase+'-partial-20261106')))
if($Phase -eq 'recovery' -and $backup -eq (Join-Path $parent 'Sutram-v307-before-interruption-repeat-20261106')){$partial=Join-Path $parent 'Sutram-v307-recovery-repeat-partial-20261106'}
foreach($path in @($src,$backup,$partial)){if([IO.Path]::GetDirectoryName($path) -ne $parent){throw 'Unsafe restoration target'}}
$expected=if($Phase -eq 'upgrade'){'Sutram-v307-before-upgrade-20261106'}else{'Sutram-v307-before-interruption-20261106'}
if($Phase -eq 'recovery' -and $backup -eq (Join-Path $parent 'Sutram-v307-before-interruption-repeat-20261106')){$expected='Sutram-v307-before-interruption-repeat-20261106'}
if($backup -ne (Join-Path $parent $expected) -or (Test-Path -LiteralPath $partial)){throw 'Unexpected backup or existing partial destination'}
foreach($path in @($src,$backup)){
    $walk=$path
    while($walk){if((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'};$walk=[IO.Path]::GetDirectoryName($walk)}
    if(Get-ChildItem -LiteralPath $path -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1){throw 'Reparse content'}
}
foreach($file in $saved.files){if((Get-FileHash -LiteralPath (Join-Path $backup $file.relative)).Hash -ne $file.sha256){throw 'Backup mismatch'}}
$r=[ordered]@{phase=$Phase;started=[DateTime]::Now.ToString('o');backup=$backup;partial=$partial;stopped=@();security_settings_changed=$false}
foreach($target in @(@{pid=$report.child.pid;command=$report.child.command;start=$report.child.started},@{pid=$report.pid;exe=$report.setup;start=$report.process_started})){
    $actual=Get-CimInstance Win32_Process -Filter "ProcessId = $($target.pid)"
    if(-not $actual){continue}
    if($target.command -and $actual.CommandLine -ne $target.command){throw 'Child identity changed'}
    if($target.exe -and $actual.ExecutablePath -ne $target.exe){throw 'Wizard identity changed'}
    $p=Get-Process -Id $target.pid
    if($p.StartTime.ToString('o') -ne $target.start){throw 'Process creation time changed'}
    Stop-Process -InputObject $p -Force
    if(-not $p.WaitForExit(5000)){throw 'Owned process did not exit'}
    $r.stopped+=@{pid=$p.Id;name=$actual.Name;at=[DateTime]::Now.ToString('o')}
}
if(Test-Path -LiteralPath $report.engine_log){Copy-Item -LiteralPath $report.engine_log -Destination (Join-Path $PSScriptRoot ($Phase+'-engine.log')) -Force;$r.engine_log_preserved_after_handles_closed=$true}
$r.partial_file_count=@(Get-ChildItem -LiteralPath $src -Recurse -Force -File).Count
Move-Item -LiteralPath $src -Destination $partial
Copy-Item -LiteralPath $backup -Destination $src -Recurse
$r.files_verified=0
foreach($file in $saved.files){if((Get-FileHash -LiteralPath (Join-Path $src $file.relative)).Hash -ne $file.sha256){throw 'Restored file mismatch'};$r.files_verified++}
$r.restored_file_count=@(Get-ChildItem -LiteralPath $src -Recurse -Force -File).Count
$r.user_path_unchanged=[Environment]::GetEnvironmentVariable('Path','User') -eq $saved.user_path_before
$r.machine_path_unchanged=[Environment]::GetEnvironmentVariable('Path','Machine') -eq $saved.machine_path
$r.version=@(& (Join-Path $src 'bin\sutram.exe') --version);$r.cli_exit=$LASTEXITCODE
$r.pass=$r.files_verified -eq $saved.file_count -and $r.restored_file_count -eq $saved.file_count -and $r.user_path_unchanged -and $r.machine_path_unchanged -and $r.cli_exit -eq 0 -and $r.version[0] -eq 'Sutram 1.0 (v307) - sampurna sutra'
$r|ConvertTo-Json -Depth 5|Set-Content (Join-Path $PSScriptRoot ('restore-'+$Phase+'.json')) -Encoding UTF8
Write-Host "Restored $($r.files_verified) files; v307 CLI and PATH verified: $($r.pass)"
if(-not $r.pass){throw 'Restoration verification failed'}
