$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host 'Sutram Windows preflight' -ForegroundColor Cyan
Write-Host '========================'
Write-Host ("PowerShell: {0}" -f $PSVersionTable.PSVersion)
$osVersion = [Environment]::OSVersion.Version
if ($osVersion.Major -eq 10 -and $osVersion.Build -ge 22000) {
    $friendlyOs = "Windows 11 (build $($osVersion.Build))"
} elseif ($osVersion.Major -eq 10) {
    $friendlyOs = "Windows 10 (build $($osVersion.Build))"
} else {
    $friendlyOs = [Environment]::OSVersion.VersionString
}
Write-Host ("OS        : {0}" -f $friendlyOs)
Write-Host ("Kernel    : Windows NT {0}" -f $osVersion)
if ($PSVersionTable.PSVersion.Major -lt 5) { throw 'Windows PowerShell 5.1 or newer is required.' }
if (-not [Environment]::Is64BitOperatingSystem) { throw 'Sutram Windows native build requires 64-bit Windows.' }

$required = @(
    'src\sutram_compiler_win.asm',
    'win\native_host.asm',
    'build-windows-native.ps1',
    'build-windows-setup.ps1',
    'windows-installer-native\installer.c',
    'windows-installer-native\install-core.ps1',
    'windows-installer-native\uninstall-core.ps1',
    'windows-installer-native\build-installer.ps1',
    'windows-installer-native\assets\sutram.ico',
    'examples\01_hello.sm',
    'examples\37_native_gujarati.sm',
    'lang\gujarati.lang'
)
foreach ($relative in $required) {
    $path = Join-Path $Root $relative
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Required project file is missing: $relative" }
}

$integrityManifest = Join-Path $Root 'windows-build-integrity.sha256'
if (-not (Test-Path -LiteralPath $integrityManifest -PathType Leaf)) { throw 'Source integrity manifest is missing.' }
$rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\')
foreach ($line in Get-Content -LiteralPath $integrityManifest) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    if ($line -notmatch '^([0-9a-fA-F]{64}) \*(.+)$') { throw "Invalid source integrity manifest line: $line" }
    $expectedHash = $Matches[1].ToLowerInvariant()
    $relativePath = $Matches[2]
    $target = [IO.Path]::GetFullPath((Join-Path $rootFull $relativePath))
    if (-not $target.StartsWith($rootFull + '\',[StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe source integrity path: $relativePath" }
    if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { throw "Source integrity file is missing: $relativePath" }
    $actualHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $target).Hash.ToLowerInvariant()
    if ($actualHash -ne $expectedHash) { throw "Source integrity mismatch: $relativePath. Re-extract a fresh v11 package." }
}
Write-Host 'Source package integrity: PASS' -ForegroundColor Green

function Assert-AsciiFile([string]$Path,[string]$Label) {
    foreach ($byte in [IO.File]::ReadAllBytes($Path)) {
        if ($byte -gt 127) { throw "$Label contains non-ASCII source bytes: $Path" }
    }
}

function Assert-AsmQuotes([string]$Path) {
    $text = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($Path))
    $lineNumber = 0
    foreach ($line in ($text -split "`n")) {
        $lineNumber++
        $single = $false
        $double = $false
        for ($i = 0; $i -lt $line.Length; $i++) {
            $ch = $line[$i]
            if (-not $single -and -not $double -and $ch -eq ';') { break }
            if (-not $double -and $ch -eq "'") { $single = -not $single; continue }
            if (-not $single -and $ch -eq '"') { $double = -not $double; continue }
        }
        if ($single -or $double) { throw "Unterminated assembly literal at ${Path}:$lineNumber" }
    }
}

$winCompiler = Join-Path $Root 'src\sutram_compiler_win.asm'
$winHost = Join-Path $Root 'win\native_host.asm'
Assert-AsciiFile $winCompiler 'Windows compiler source'
Assert-AsciiFile $winHost 'Windows host source'
Assert-AsmQuotes $winCompiler
Assert-AsmQuotes $winHost
$compilerText = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($winCompiler))
$compilerLines = ($compilerText -split "`n").Count
if ($compilerLines -lt 9000) { throw "Windows compiler source appears truncated ($compilerLines lines)." }
foreach ($marker in @(
    'global sutram_main',
    'extern win_syscall',
    'jne parse_error            ; never recurse on an invalid primary token',
    'jne parse_error            ; other delimiters are not valid primary expressions'
)) {
    if ($compilerText.IndexOf($marker,[StringComparison]::Ordinal) -lt 0) { throw "Windows compiler source is missing marker: $marker" }
}
$hostText = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($winHost))
foreach ($marker in @('CommandLineToArgvW','CreateFileW','MultiByteToWideChar','WideCharToMultiByte','GetModuleFileNameW','GetEnvironmentStringsW')) {
    if ($hostText.IndexOf($marker,[StringComparison]::Ordinal) -lt 0) { throw "Windows host source is missing API marker: $marker" }
}
if ($hostText -match '(?ms)section \.bss.*?^\s*align\s+\d+') { throw 'Use alignb, not align, inside the BSS section.' }
Write-Host ("Assembly sources: PASS ({0} compiler lines, ASCII-stable, quote-balanced)" -f $compilerLines) -ForegroundColor Green

$sourceFiles = @(
    'build-windows-native.ps1','build-windows-setup.ps1','preflight-windows.ps1','check-windows-build-tools.ps1',
    'windows-installer-native\installer.c','windows-installer-native\build-installer.ps1',
    'windows-installer-native\install-core.ps1','windows-installer-native\uninstall-core.ps1'
)
foreach ($relative in $sourceFiles) {
    $path = Join-Path $Root $relative
    Assert-AsciiFile $path 'Build/installer source'
    $text = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes($path))
    if ($text -match '\(\s*if\s*\(') { throw "PowerShell-7-style inline if expression found in $relative" }
    if ($text -match '&\s*\$Linker\s+-nostdlib\s+-Wl,') { throw "Unsafe MinGW comma arguments found in $relative" }
}

$installerText = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes((Join-Path $Root 'windows-installer-native\installer.c')))
foreach ($marker in @('--self-test','--uninstall','ShellExecuteExW','runas','SUTPKG10','ValidatePackage','WritePackagePart','PBM_SETMARQUEE','CommandLineToArgvW','ScheduleSelfDelete')) {
    if ($installerText.IndexOf($marker,[StringComparison]::Ordinal) -lt 0) { throw "Native installer source is missing marker: $marker" }
}
foreach ($forbidden in @('FindResourceW','LoadResource','SizeofResource','RES_PAYLOAD','RT_RCDATA')) {
    if ($installerText.IndexOf($forbidden,[StringComparison]::OrdinalIgnoreCase) -ge 0) { throw "Obsolete resource-packaging dependency found in installer.c: $forbidden" }
}
$installerBuildText = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes((Join-Path $Root 'windows-installer-native\build-installer.ps1')))
foreach ($forbidden in @('windres.exe','Find-MinGwWindres','Invoke-Windres','setup.rc','setup-res.o','IExpress','ISCC.exe')) {
    if ($installerBuildText.IndexOf($forbidden,[StringComparison]::OrdinalIgnoreCase) -ge 0) { throw "Obsolete installer build dependency found: $forbidden" }
}
$installText = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes((Join-Path $Root 'windows-installer-native\install-core.ps1')))
foreach ($marker in @('Verify-Payload','payload.manifest.sha256','Set-MachinePathEntry','UninstallString','.sutram-install','Packaged sutram.exe failed its pre-install version test','Sutram is already installed at','PathOwned=','DesktopOwned=','pathAddedNow')) {
    if ($installText.IndexOf($marker,[StringComparison]::Ordinal) -lt 0) { throw "Install core is missing marker: $marker" }
}
$uninstallText = [Text.Encoding]::ASCII.GetString([IO.File]::ReadAllBytes((Join-Path $Root 'windows-installer-native\uninstall-core.ps1')))
foreach ($marker in @('Remove-MachinePathEntry','Remove-ManifestFiles','.sutram-install','The native uninstaller will remove only its own EXE','PathOwned','DesktopOwned')) {
    if ($uninstallText.IndexOf($marker,[StringComparison]::OrdinalIgnoreCase) -lt 0) { throw "Uninstall core is missing marker: $marker" }
}
Write-Host 'Source compatibility/hardening scan: PASS' -ForegroundColor Green

function Resolve-ExistingFile([string[]]$Candidates) {
    foreach ($candidate in $Candidates) {
        if ($candidate -and (Test-Path -LiteralPath $candidate -PathType Leaf)) { return (Resolve-Path -LiteralPath $candidate).Path }
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
    return Resolve-ExistingFile @('C:\mingw64\bin\nasm.exe','C:\msys64\ucrt64\bin\nasm.exe','C:\msys64\mingw64\bin\nasm.exe',(Join-Path $env:ProgramFiles 'NASM\nasm.exe'))
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
function Invoke-MinGwGcc([string]$Gcc,[string[]]$Arguments,[string]$Label) {
    $oldPath = $env:PATH
    $gccDir = Split-Path -Parent $Gcc
    try {
        $env:PATH = $gccDir + ';' + $oldPath
        & $Gcc @Arguments
        $code = $LASTEXITCODE
        if ($code -ne 0) { throw "$Label failed with exit code $code." }
    } finally {
        $env:PATH = $oldPath
    }
}

$nasm = Find-Nasm
$gcc = Find-MinGwGcc
if (-not $nasm) { throw 'NASM was not found.' }
if (-not $gcc) { throw 'MinGW x64 GCC was not found.' }
Write-Host ("NASM     : {0}" -f $nasm) -ForegroundColor Green
Write-Host ("MinGW GCC: {0}" -f $gcc) -ForegroundColor Green
Write-Host 'windres  : not required in v11' -ForegroundColor Green

$probe = Join-Path $env:TEMP ('Sutram-NativeInstaller-Probe-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Force -Path $probe | Out-Null
try {
    $probeC = Join-Path $probe 'p.c'
    $probeExe = Join-Path $probe 'p.exe'
    [IO.File]::WriteAllLines($probeC,@(
        '#include <windows.h>',
        '#include <commctrl.h>',
        '#include <shlobj.h>',
        '#include <shellapi.h>',
        'int WINAPI wWinMain(HINSTANCE a,HINSTANCE b,PWSTR c,int d){INITCOMMONCONTROLSEX x; (void)a;(void)b;(void)c;(void)d; x.dwSize=sizeof(x); x.dwICC=ICC_STANDARD_CLASSES; InitCommonControlsEx(&x); return 0;}'
    ),([Text.ASCIIEncoding]::new()))
    Invoke-MinGwGcc $gcc @('-std=c11','-municode','-mwindows',$probeC,'-o',$probeExe,'-lcomctl32','-lshell32','-lole32','-ladvapi32','-luser32','-lgdi32') 'Native installer compiler/linker probe'
    $probeBytes = [IO.File]::ReadAllBytes($probeExe)
    if ($probeBytes.Length -lt 1024 -or $probeBytes[0] -ne 0x4D -or $probeBytes[1] -ne 0x5A) { throw 'Native installer probe did not create a valid PE file.' }
    $peOffset = [BitConverter]::ToInt32($probeBytes,0x3C)
    if ($peOffset -lt 0 -or ($peOffset + 26) -ge $probeBytes.Length) { throw 'Native installer probe PE header is invalid.' }
    if ($probeBytes[$peOffset] -ne 0x50 -or $probeBytes[$peOffset + 1] -ne 0x45) { throw 'Native installer probe PE signature is invalid.' }
    if ([BitConverter]::ToUInt16($probeBytes,$peOffset + 4) -ne 0x8664) { throw 'Native installer probe did not create an x64 executable.' }
    if ([BitConverter]::ToUInt16($probeBytes,$peOffset + 24) -ne 0x20B) { throw 'Native installer probe did not create PE32+ output.' }
} finally {
    Remove-Item -LiteralPath $probe -Recurse -Force -ErrorAction SilentlyContinue
}
Write-Host 'Native installer GCC/Win32-library probe: PASS' -ForegroundColor Green
Write-Host 'Packaging path: PE overlay + SHA-256 validation (no resource compiler).' -ForegroundColor Green
Write-Host ''
Write-Host 'Project preflight passed. windres, IExpress, and Inno Setup are not used.' -ForegroundColor Green
