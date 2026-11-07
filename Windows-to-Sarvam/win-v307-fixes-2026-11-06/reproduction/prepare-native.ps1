$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$out=Join-Path $root 'Windows-to-Sarvam\win-v307-fixes-2026-11-06'
[void](New-Item -ItemType Directory -Force -Path $out)
$prior=Join-Path $root 'Windows-to-Sarvam\win-v307-2026-11-06'
Copy-Item -LiteralPath (Join-Path $prior 'ui-helper.ps1') -Destination $out
$source=[IO.File]::ReadAllText((Join-Path $prior 'install.ps1'))
$pin=(Get-FileHash (Join-Path $root 'Sutram-Setup.exe')).Hash
$source=$source.Replace('CBBFD0A66C0A9728C3FD88096631462430C0185CD8C6738964D5B885253E7481',$pin)
[IO.File]::WriteAllText((Join-Path $out 'install.ps1'),$source,[Text.UTF8Encoding]::new($false))
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs'))
$installed=Join-Path $parent 'Sutram'
$backup=Join-Path $parent 'Sutram-before-review-fixes-20261106'
foreach($p in @($installed,$backup)){if([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($p)) -ne $parent){throw 'Unsafe backup path'}}
if(Test-Path -LiteralPath $backup){throw 'Backup already exists'}
$walk=$installed
while($walk){if((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'};$walk=[IO.Path]::GetDirectoryName($walk)}
if(Get-ChildItem -LiteralPath $installed -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1){throw 'Reparse content'}
$rows=@(Get-ChildItem -LiteralPath $installed -Recurse -File -Force|ForEach-Object {@{relative=$_.FullName.Substring($installed.Length+1);sha256=(Get-FileHash -LiteralPath $_.FullName).Hash}})
Copy-Item -LiteralPath $installed -Destination $backup -Recurse
foreach($row in $rows){if((Get-FileHash -LiteralPath (Join-Path $backup $row.relative)).Hash -ne $row.sha256){throw 'Backup hash mismatch'}}
$result=@{installed=$installed;backup=$backup;files=$rows;file_count=$rows.Count;setup_sha256=$pin;user_path=[Environment]::GetEnvironmentVariable('Path','User');machine_path=[Environment]::GetEnvironmentVariable('Path','Machine');time=[DateTime]::Now.ToString('o')}
[IO.File]::WriteAllText((Join-Path $out 'before.json'),($result|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
Write-Host "Verified backup: $($rows.Count) files. Review setup: $pin"
& (Join-Path $out 'install.ps1') -Phase upgrade
