# Pure NASM Win64 GUI with a linked scoped-cluster counter. No elevation.
[CmdletBinding()]
param([switch]$Run)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$nasm = Get-Command nasm.exe -ErrorAction SilentlyContinue
$ld = Get-Command ld.exe -ErrorAction SilentlyContinue
if (-not $nasm -or -not $ld) { throw 'Use the existing NASM and PE64 ld toolchain. Do not elevate or install tools automatically.' }
$work = Join-Path $env:TEMP ('sutram_gui_' + [guid]::NewGuid().ToString('N'))
$exe = Join-Path $root 'sutram-ide-gui.exe'
$includeRoot = $root + [IO.Path]::DirectorySeparatorChar
$inputs = @('r67_gui_entry.asm','r66_indic_clusters.asm','r67_cluster_count.asm')
$objects = @()
try {
    [void](New-Item -ItemType Directory -Path $work)
    foreach ($name in $inputs) {
        $source = Join-Path $PSScriptRoot $name
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) { throw "Missing GUI source: $source" }
        $obj = Join-Path $work ([IO.Path]::GetFileNameWithoutExtension($name) + '.obj')
        & $nasm.Source -f win64 -I $includeRoot $source -o $obj
        if ($LASTEXITCODE -ne 0) { throw "NASM assembly failed for $name ($LASTEXITCODE)." }
        $objects += $obj
    }
    $candidate = Join-Path $work 'sutram-ide-gui.exe'
    & $ld.Source -mi386pep --subsystem windows --entry=_start -o $candidate @objects
    if ($LASTEXITCODE -ne 0) { throw "Win64 PE link failed ($LASTEXITCODE)." }
    $head = [IO.File]::ReadAllBytes($candidate)
    if ($head.Length -lt 512 -or $head[0] -ne 0x4d -or $head[1] -ne 0x5a) { throw 'Output is not an MZ executable.' }
    $pe = [BitConverter]::ToInt32($head,0x3c)
    if ($pe -le 0 -or $pe + 26 -gt $head.Length -or
        $head[$pe] -ne 0x50 -or $head[$pe+1] -ne 0x45 -or
        [BitConverter]::ToUInt16($head,$pe+4) -ne 0x8664 -or
        [BitConverter]::ToUInt16($head,$pe+24) -ne 0x20b) { throw 'Invalid PE32+ AMD64 output.' }
    Copy-Item -LiteralPath $candidate -Destination $exe -Force
    Write-Host "Built (format verified only, not GUI-tested): $exe"
    Write-Host 'R66 helper is linked. The title counts scoped clusters; RichEdit still renders and positions the caret.'
    Write-Host 'Run test-gui.ps1 and the real Windows manual checklist before acceptance.'
    if ($Run) { Start-Process -FilePath $exe -WorkingDirectory $root }
} finally {
    if (Test-Path -LiteralPath $work) { Remove-Item -LiteralPath $work -Recurse -Force }
}
