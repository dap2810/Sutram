$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'restore-after-test.ps1') -Phase recovery
$saved=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'prepare-interrupt.json') -Raw|ConvertFrom-Json
$archive=Join-Path $PSScriptRoot 'reader-interference'
if(Test-Path -LiteralPath $archive){throw 'Archive already exists'}
[void](New-Item -ItemType Directory -Path $archive)
Get-ChildItem -LiteralPath $PSScriptRoot -File|Where-Object {$_.Name -match '^(interrupt|recovery)' -or $_.Name -in @('prepare-interrupt.json','restore-recovery.json')}|ForEach-Object {Move-Item -LiteralPath $_.FullName -Destination (Join-Path $archive $_.Name)}
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$src=Join-Path $parent 'Sutram';$backup=Join-Path $parent 'Sutram-v307-before-interruption-repeat-20261106'
foreach($path in @($src,$backup)){if([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($path)) -ne $parent){throw 'Unsafe path'}}
if(Test-Path -LiteralPath $backup){throw 'Backup already exists'}
$walk=$src
while($walk){if((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'};$walk=[IO.Path]::GetDirectoryName($walk)}
if(Get-ChildItem -LiteralPath $src -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1){throw 'Reparse content'}
Move-Item -LiteralPath $src -Destination $backup
foreach($file in $saved.files){if((Get-FileHash -LiteralPath (Join-Path $backup $file.relative)).Hash -ne $file.sha256){throw 'Backup hash mismatch'}}
$saved.backup=$backup;$saved.at=[DateTime]::Now.ToString('o')
$saved|ConvertTo-Json -Depth 7|Set-Content (Join-Path $PSScriptRoot 'prepare-interrupt.json') -Encoding UTF8
& (Join-Path $PSScriptRoot 'install.ps1') -Phase interrupt
$interrupted=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'interrupt.json') -Raw|ConvertFrom-Json
if($interrupted.status -ne 'INTERRUPTED_AS_REQUESTED' -or -not $interrupted.pending_exists){throw 'No valid partial install'}
Copy-Item -LiteralPath (Join-Path $env:LOCALAPPDATA 'Programs\Sutram\payload.pending.sha256') -Destination (Join-Path $PSScriptRoot 'interrupted-payload.pending.sha256')
& (Join-Path $PSScriptRoot 'install.ps1') -Phase recovery
$recovery=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'recovery.json') -Raw|ConvertFrom-Json
if($recovery.status -ne 'FINISH'){& (Join-Path $PSScriptRoot 'restore-after-test.ps1') -Phase recovery}
python (Join-Path $PSScriptRoot 'identity.py')
if($LASTEXITCODE -ne 0){throw 'Final identity verification failed'}
& (Join-Path $PSScriptRoot 'final-state.ps1')
python (Join-Path $PSScriptRoot 'security-log-read.py')
