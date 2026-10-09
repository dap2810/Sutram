$ErrorActionPreference = 'Continue'
Set-StrictMode -Version 2.0

Write-Host 'Sutram Windows build diagnostics' -ForegroundColor Cyan
Write-Host '================================'
Write-Host ("PowerShell: {0}" -f $PSVersionTable.PSVersion)
$osVersion = [Environment]::OSVersion.Version
if ($osVersion.Major -eq 10 -and $osVersion.Build -ge 22000) { $friendlyOs = "Windows 11 (build $($osVersion.Build))" }
elseif ($osVersion.Major -eq 10) { $friendlyOs = "Windows 10 (build $($osVersion.Build))" }
else { $friendlyOs = [Environment]::OSVersion.VersionString }
Write-Host ("OS        : {0}" -f $friendlyOs)
Write-Host ("Kernel    : Windows NT {0}" -f $osVersion)
Write-Host ''

function Resolve-ExistingFile([string[]]$Candidates) {
    foreach ($candidate in $Candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) {
            return (Resolve-Path -LiteralPath $candidate).Path
        }
    }
    return $null
}

function Find-CommandPath([string[]]$Names) {
    foreach ($name in $Names) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) { return $command.Source }
    }
    return $null
}

function Find-Nasm {
    $path = Find-CommandPath @('nasm.exe','nasm')
    if ($path) { return $path }
    $candidates = @(
        'C:\mingw64\bin\nasm.exe',
        'C:\msys64\ucrt64\bin\nasm.exe',
        'C:\msys64\mingw64\bin\nasm.exe',
        (Join-Path $env:ProgramFiles 'NASM\nasm.exe')
    )
    return Resolve-ExistingFile $candidates
}

function Find-MinGwGcc {
    $path = Find-CommandPath @('x86_64-w64-mingw32-gcc.exe','gcc.exe')
    if ($path -and $path -match '(?i)(msys|mingw|ucrt)') { return $path }
    return Resolve-ExistingFile @(
        'C:\msys64\ucrt64\bin\x86_64-w64-mingw32-gcc.exe',
        'C:\msys64\ucrt64\bin\gcc.exe',
        'C:\msys64\mingw64\bin\x86_64-w64-mingw32-gcc.exe',
        'C:\msys64\mingw64\bin\gcc.exe',
        'C:\mingw64\bin\gcc.exe'
    )
}

function Show-Result([string]$Label,[string]$Value) {
    if ($Value) { Write-Host ("{0,-22}: {1}" -f $Label,$Value) -ForegroundColor Green }
    else { Write-Host ("{0,-22}: not found" -f $Label) -ForegroundColor Red }
}

$nasm = Find-Nasm
$gcc = Find-MinGwGcc
Show-Result 'NASM' $nasm
Show-Result 'MinGW GCC' $gcc
Write-Host ('{0,-22}: {1}' -f 'MinGW windres','not required in v11') -ForegroundColor Green
Write-Host ''

if ($nasm -and $gcc) {
    Write-Host 'READY: native compiler + native Win32 wizard installer can be built with NASM + MinGW GCC.' -ForegroundColor Green
    Write-Host 'windres, IExpress, and Inno Setup are not used.' -ForegroundColor Green
    Write-Host 'Run: .\build-windows-setup.ps1' -ForegroundColor Green
    exit 0
}

Write-Host 'NOT READY: install the missing MSYS2/MinGW component shown above.' -ForegroundColor Red
exit 1
