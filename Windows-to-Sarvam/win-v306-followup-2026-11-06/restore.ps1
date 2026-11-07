$ErrorActionPreference='Stop'
$report=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'upgrade.json') -Raw|ConvertFrom-Json
$saved=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'preserve.json') -Raw|ConvertFrom-Json
$navigation=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'navigation-attempt.json') -Raw|ConvertFrom-Json
if($report.status -eq 'FINISH'){throw 'Upgrade succeeded; restoration is unnecessary'}
if(-not $report.status -or ([DateTime]::Now-[DateTime]::Parse($report.child_started)).TotalSeconds -lt 935){throw 'Leave the upgrade untouched until the full observation finishes'}
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$src=[IO.Path]::GetFullPath((Join-Path $parent 'Sutram'))
$backup=[IO.Path]::GetFullPath([string]$saved.backup)
$partial=[IO.Path]::GetFullPath((Join-Path $parent 'Sutram-followup-partial-20261106'))
foreach($path in @($src,$backup,$partial)){if([IO.Path]::GetDirectoryName($path) -ne $parent){throw 'Restore paths must be direct children of the approved Programs folder'}}
if($backup -ne (Join-Path $parent 'Sutram-before-v306-followup-20261106') -or (Test-Path -LiteralPath $partial)){throw 'Unexpected backup or existing partial-preservation destination'}
foreach($path in @($src,$backup)){
    $walk=$path
    while($walk){if((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'};$walk=[IO.Path]::GetDirectoryName($walk)}
    if(Get-ChildItem -LiteralPath $path -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1){throw 'Reparse content'}
}
foreach($file in $saved.files){if((Get-FileHash -LiteralPath (Join-Path $backup $file.relative)).Hash -ne $file.sha256){throw 'Backup changed; do not restore'}}
$r=[ordered]@{started=[DateTime]::Now.ToString('o');reason='Restore the verified pre-upgrade installation after the full externally-suspended timeout observation';backup=$backup;partial=$partial;stopped=@();security_settings_changed=$false}
foreach($target in @(@{pid=$report.child.ProcessId;command=$report.child.CommandLine;start=$report.child_started},@{pid=$report.pid;exe=$report.setup;start=$navigation.started})){
    $processId=[int]$target.pid;$actual=Get-CimInstance Win32_Process -Filter "ProcessId = $processId"
    if(-not $actual){continue}
    if($target.command -and $actual.CommandLine -ne $target.command){throw 'Child PID identity changed'}
    if($target.exe -and $actual.ExecutablePath -ne $target.exe){throw 'Wizard PID identity changed'}
    $p=Get-Process -Id $processId
    if([Math]::Abs(($p.StartTime-[DateTime]::Parse($target.start)).TotalSeconds) -gt 2){throw 'Process creation time differs'}
    Stop-Process -InputObject $p -Force
    if(-not $p.WaitForExit(5000)){throw 'Owned process did not stop'}
    $r.stopped+=@{pid=$processId;name=$actual.Name;at=[DateTime]::Now.ToString('o')}
}
$r.partial_file_count=@(Get-ChildItem -LiteralPath $src -Recurse -Force -File).Count
Move-Item -LiteralPath $src -Destination $partial
Copy-Item -LiteralPath $backup -Destination $src -Recurse
$r.files_verified=0
foreach($file in $saved.files){if((Get-FileHash -LiteralPath (Join-Path $src $file.relative)).Hash -ne $file.sha256){throw 'Restored-file mismatch'};$r.files_verified++}
$r.restored_file_count=@(Get-ChildItem -LiteralPath $src -Recurse -Force -File).Count
$r.user_path_unchanged=[Environment]::GetEnvironmentVariable('Path','User') -eq $saved.user_path
$r.machine_path_unchanged=[Environment]::GetEnvironmentVariable('Path','Machine') -eq $saved.machine_path
$r.version=@(& (Join-Path $src 'bin\sutram.exe') --version)
$r.cli_exit=$LASTEXITCODE
$r.pass=$r.files_verified -eq $saved.file_count -and $r.restored_file_count -eq $saved.file_count -and $r.user_path_unchanged -and $r.machine_path_unchanged -and $r.cli_exit -eq 0 -and $r.version[0] -eq 'Sutram 1.0 (v306) - sampurna sutra'
$r|ConvertTo-Json -Depth 5|Set-Content (Join-Path $PSScriptRoot 'restore.json') -Encoding UTF8
Write-Host "Restored $($r.files_verified) original files; PATH unchanged; v306 CLI verified: $($r.pass)"
if(-not $r.pass){throw 'Restoration verification failed'}
