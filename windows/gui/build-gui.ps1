# Pure NASM/native Windows GUI preview build. No elevation, VS/C toolchain, GUI framework.
# Launch PowerShell in the project root or anywhere; relative paths are resolved here.
[CmdletBinding()]
param([switch]$Run)
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$nasm = Get-Command nasm.exe -ErrorAction SilentlyContinue
if (-not $nasm) { throw 'nasm.exe not found. Use your existing Sutram NASM build environment; do not elevate.' }
$ld = Get-Command ld.exe -ErrorAction SilentlyContinue
if (-not $ld) { throw 'ld.exe (PE x86-64 linker) not found in PATH.' }
$src = Join-Path $PSScriptRoot 'sutram_gui.asm'
$obj = Join-Path $env:TEMP ('sutram_gui_' + [guid]::NewGuid().ToString('N') + '.obj')
$exe = Join-Path $root 'sutram-ide-gui.exe'
try {
    & $nasm.Source -f win64 $src -o $obj
    if ($LASTEXITCODE -ne 0) { throw "NASM assembly failed ($LASTEXITCODE)." }
    & $ld.Source -mi386pep --subsystem windows --entry=_start -o $exe $obj
    if ($LASTEXITCODE -ne 0) { throw "Win64 PE link failed ($LASTEXITCODE)." }
    $head = [IO.File]::ReadAllBytes($exe)
    if ($head.Length -lt 512 -or $head[0] -ne 0x4d -or $head[1] -ne 0x5a) {
        throw 'Output is not an MZ Windows executable.'
    }
    $pe = [BitConverter]::ToInt32($head,0x3c)
    if ($pe -le 0 -or $pe + 24 -gt $head.Length -or
        $head[$pe] -ne 0x50 -or $head[$pe+1] -ne 0x45 -or
        [BitConverter]::ToUInt16($head,$pe+4) -ne 0x8664) {
        throw 'PE64 header or AMD64 machine ID missing.'
    }
    Write-Host "Built (format verified only): $exe" -ForegroundColor Green
    Write-Host 'On a real Windows desktop run windows\gui\test-gui.ps1 and the manual checklist.'
    if ($Run) { Start-Process -FilePath $exe -WorkingDirectory $root }
} finally {
    Remove-Item $obj -ErrorAction SilentlyContinue
}
