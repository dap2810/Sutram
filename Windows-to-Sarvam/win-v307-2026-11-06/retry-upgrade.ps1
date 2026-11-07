$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
$old=Get-Content (Join-Path $OutDir 'upgrade.json') -Raw|ConvertFrom-Json
$prep=Get-Content (Join-Path $OutDir 'prepare-upgrade.json') -Raw|ConvertFrom-Json
if(Get-Process -Id $old.child.pid -ErrorAction SilentlyContinue){throw 'Engine still running'}
$wizard=Get-Process -Id $old.pid -ErrorAction SilentlyContinue
if($wizard){if($wizard.StartTime.ToString('o') -ne $old.process_started){throw 'PID identity mismatch'};Stop-Process -Id $wizard.Id -Force}
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$src=Join-Path $parent 'Sutram';$backup=Join-Path $parent 'Sutram-v307-before-upgrade-20261106';$partial=Join-Path $parent 'Sutram-v307-upgrade-first-partial-20261106'
foreach($path in @($src,$backup,$partial)){if([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($path)) -ne $parent){throw 'Unsafe path'};if(Test-Path -LiteralPath $path){$walk=$path;while($walk){if((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'};$walk=[IO.Path]::GetDirectoryName($walk)};if(Get-ChildItem -LiteralPath $path -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1){throw 'Reparse content'}}}
if(Test-Path -LiteralPath $partial){throw 'Partial preservation target exists'}
foreach($file in $prep.files){if((Get-FileHash -LiteralPath (Join-Path $backup $file.relative)).Hash -ne $file.sha256){throw 'Backup mismatch'}}
Copy-Item -LiteralPath $old.engine_log -Destination (Join-Path $OutDir 'upgrade-observer-failed-engine.log')
$record=[ordered]@{at=[DateTime]::Now.ToString('o');status='ERROR_DIALOG';screenshot='upgrade-observer-failed-error.png';note='Observer hit a log sharing error during copy. Its catch also failed while copying the active log. Error dialog was captured after the engine exited. Causality is unproven; retry uses explicit FileShare ReadWrite/Delete and tolerates read errors.';backup=$backup;partial=$partial;pending_before=(Test-Path -LiteralPath (Join-Path $src 'payload.pending.sha256'))}
foreach($name in @('upgrade.json','upgrade-ready.png','upgrade-error.png')){Move-Item -LiteralPath (Join-Path $OutDir $name) -Destination (Join-Path $OutDir ($name.Replace('upgrade','upgrade-observer-failed')))}
Move-Item -LiteralPath $src -Destination $partial
Copy-Item -LiteralPath $backup -Destination $src -Recurse
foreach($file in $prep.files){if((Get-FileHash -LiteralPath (Join-Path $src $file.relative)).Hash -ne $file.sha256){throw 'Restored-file mismatch'}}
$record.restored_files_verified=$prep.files.Count
$record|ConvertTo-Json -Depth 4|Set-Content (Join-Path $OutDir 'upgrade-observer-failed-result.json') -Encoding UTF8
& (Join-Path $OutDir 'install.ps1') -Phase upgrade
