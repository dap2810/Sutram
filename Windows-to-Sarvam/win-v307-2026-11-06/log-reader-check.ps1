$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$path=Join-Path $root 'build\windows-v307-2026-11-06\log-sharing-fixture.txt'
[IO.File]::WriteAllText($path,"fixture`r`n")
$r=[ordered]@{at=[DateTime]::Now.ToString('o');powershell=$PSVersionTable.PSVersion.ToString();fixture=$path;reader_share='ReadWrite | Delete'}
$f=[IO.File]::Open($path,[IO.FileMode]::Open,[IO.FileAccess]::Read,([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
try{
    try{Add-Content -LiteralPath $path -Value 'while reader open' -Encoding UTF8;$r.add_content_with_reader='PASS'}catch{$r.add_content_with_reader='FAIL';$r.error=$_.Exception.Message}
}finally{$f.Dispose()}
Add-Content -LiteralPath $path -Value 'after reader closed' -Encoding UTF8
$r.add_content_after_reader_closed='PASS'
$r|ConvertTo-Json -Depth 4|Set-Content (Join-Path $PSScriptRoot 'log-reader-check.json') -Encoding UTF8
$r|ConvertTo-Json -Depth 4
