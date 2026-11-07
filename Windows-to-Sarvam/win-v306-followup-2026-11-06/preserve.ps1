$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$src=Join-Path $parent 'Sutram';$dst=Join-Path $parent 'Sutram-before-v306-followup-20261106'
if(Test-Path -LiteralPath $dst) { throw 'Follow-up backup already exists; do not overwrite it' }
$walk=$src
while($walk) { if((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse ancestor'};$walk=[IO.Path]::GetDirectoryName($walk) }
if(Get-ChildItem -LiteralPath $src -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1){throw 'Reparse content'}
if((Get-FileHash -LiteralPath (Join-Path $src 'bin\sutram.exe')).Hash -ne 'D3F3DC157BADDEC973947A4D5F5B1760203542B6576B11C15AAB6A757F48DF77'){throw 'Installed compiler is not the tested v306'}
if((Get-FileHash -LiteralPath (Join-Path $root 'Sutram-Setup.exe')).Hash -ne 'E6006CAF2BACEBF378B9D3B8CD4527D63C1DE6AC2E96EFA630E5C268FF852E5F'){throw 'Installer changed'}
$files=@(Get-ChildItem -LiteralPath $src -Recurse -Force -File)
$r=[ordered]@{recorded=[DateTime]::Now.ToString('o');source=$src;backup=$dst;file_count=$files.Count;files=@();version=(& (Join-Path $src 'bin\sutram.exe') --version);user_path=[Environment]::GetEnvironmentVariable('Path','User');machine_path=[Environment]::GetEnvironmentVariable('Path','Machine')}
if($LASTEXITCODE -ne 0 -or $r.version[0] -ne 'Sutram 1.0 (v306) - sampurna sutra'){throw 'Installed CLI identity failed'}
foreach($file in $files){$r.files+=@{relative=$file.FullName.Substring($src.Length+1);bytes=$file.Length;sha256=(Get-FileHash -LiteralPath $file.FullName).Hash}}
Copy-Item -LiteralPath $src -Destination $dst -Recurse
foreach($file in $r.files){if((Get-FileHash -LiteralPath (Join-Path $dst $file.relative)).Hash -ne $file.sha256){throw 'Backup mismatch'}}
$r.verified=$true
$r|ConvertTo-Json -Depth 5|Set-Content (Join-Path $PSScriptRoot 'preserve.json') -Encoding UTF8
Write-Host "Preserved and verified $($files.Count) existing v306 files."
