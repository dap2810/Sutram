$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'snapshot.ps1') before
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$src=[IO.Path]::GetFullPath((Join-Path $parent 'Sutram'))
$dst=[IO.Path]::GetFullPath((Join-Path $parent 'Sutram-before-v306'))
if([IO.Path]::GetDirectoryName($src) -ne $parent -or [IO.Path]::GetDirectoryName($dst) -ne $parent -or (Test-Path -LiteralPath $dst)) { throw 'Unexpected backup scope or destination already exists' }
$walk=$src
while($walk) { if((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse ancestor' }; $walk=[IO.Path]::GetDirectoryName($walk) }
if(Get-ChildItem -LiteralPath $src -Recurse -Force | Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1) { throw 'Reparse content' }
$before=Get-Content (Join-Path $PSScriptRoot 'before.json') -Raw|ConvertFrom-Json
Copy-Item -LiteralPath $src -Destination $dst -Recurse
foreach($f in $before.tree) { if((Get-FileHash -LiteralPath (Join-Path $dst $f.path)).Hash -ne $f.sha256) { throw "Backup mismatch: $($f.path)" } }
@{source=$src;backup=$dst;files_verified=$before.tree.Count;reason='Preserve v305 before A3, because same-directory upgrade is permitted by source';status='PASS'}|ConvertTo-Json|Set-Content (Join-Path $PSScriptRoot 'preserve.json') -Encoding UTF8
Write-Host "Preserved $($before.tree.Count) files in $dst"
