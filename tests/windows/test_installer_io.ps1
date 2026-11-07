# Native Windows regression: load functions only, never run the installer body.
param([string]$Evidence = (Join-Path $PSScriptRoot '..\..\build\fixes\installer-io.json'))
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$source = Join-Path $root 'windows\native-installer\install-core.ps1'
$tokens=$null; $parseErrors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($source,[ref]$tokens,[ref]$parseErrors)
if($parseErrors.Count){throw $parseErrors[0]}
foreach($name in @('Log','Copy-StagedFiles')) {
    $fn=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name},$true)
    if(-not $fn){throw "Missing function $name"}
    . ([ScriptBlock]::Create($fn.Extent.Text))
}
$work=Join-Path $root ('build\fixes\io-'+[guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory -Path $work,(Join-Path $work 'stage'),(Join-Path $work 'target'))
$LogPath=Join-Path $work 'install.log'
$rows=New-Object Collections.Generic.List[object]
function Check([bool]$Ok,[string]$Name){$rows.Add(@{name=$Name;pass=$Ok});Write-Host "$Name : $Ok"}
Log 'seed'
$reader=[IO.File]::Open($LogPath,[IO.FileMode]::Open,[IO.FileAccess]::Read,([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
try {
    for($i=0;$i -lt 100;$i++){Log "observer write $i"}
    Check (([IO.File]::ReadAllLines($LogPath)).Count -eq 101) '100 appends while shared reader stays open'
} finally {$reader.Dispose()}
$from=Join-Path $work 'stage';$to=Join-Path $work 'target'
[IO.File]::WriteAllText((Join-Path $from 'same.txt'),'identical')
[IO.File]::WriteAllText((Join-Path $to 'same.txt'),'identical')
$oldTime=[DateTime]::UtcNow.AddDays(-2)
[IO.File]::SetLastWriteTimeUtc((Join-Path $to 'same.txt'),$oldTime)
[IO.File]::WriteAllText((Join-Path $from 'changed.txt'),'new bytes')
[IO.File]::WriteAllText((Join-Path $to 'changed.txt'),'old bytes')
[IO.File]::WriteAllText((Join-Path $from 'new.txt'),'new file')
[IO.File]::WriteAllText((Join-Path $from 'payload.manifest.sha256'),'not copied here')
Copy-StagedFiles $from $to
Check ([IO.File]::GetLastWriteTimeUtc((Join-Path $to 'same.txt')) -eq $oldTime) 'identical file timestamp preserved'
Check ([IO.File]::ReadAllText((Join-Path $to 'changed.txt')) -eq 'new bytes') 'changed file replaced'
Check ([IO.File]::ReadAllText((Join-Path $to 'new.txt')) -eq 'new file') 'new file moved into place'
Check (-not [IO.File]::Exists((Join-Path $to 'payload.manifest.sha256'))) 'manifest belongs to transaction completion'
Check (@(Get-ChildItem -LiteralPath $to -Filter '*.sutram-partial').Count -eq 0) 'no partial files after success'
# Failure must propagate and retain the original bytes (no delete fallback).
[IO.File]::WriteAllText((Join-Path $from 'changed.txt'),'third bytes')
$lock=[IO.File]::Open((Join-Path $to 'changed.txt'),[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
$failed=$false
try {try {Copy-StagedFiles $from $to} catch {$failed=$true}} finally {$lock.Dispose()}
Check $failed 'replacement of locked target fails closed'
Check ([IO.File]::ReadAllText((Join-Path $to 'changed.txt')) -eq 'new bytes') 'locked target retained original bytes'
Copy-StagedFiles $from $to
Check ([IO.File]::ReadAllText((Join-Path $to 'changed.txt')) -eq 'third bytes') 'retry completes partial copy'
$result=@{powershell=$PSVersionTable.PSVersion.ToString();source_sha256=(Get-FileHash $source).Hash;work=$work;checks=$rows.ToArray()}
[IO.File]::WriteAllText([IO.Path]::GetFullPath($Evidence),($result|ConvertTo-Json -Depth 6),[Text.UTF8Encoding]::new($false))
if(@($rows|Where-Object {-not $_.pass}).Count){exit 1}
