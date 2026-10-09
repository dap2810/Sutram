$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$WindowsRoot = Split-Path -Parent $Here
$Root = Split-Path -Parent $WindowsRoot
$Work = Join-Path $Here 'work'
$Output = Join-Path $Here 'output'
$PayloadStage = Join-Path $Work 'payload'
$SetupExe = Join-Path $Output 'Sutram-Setup-0.1.0-native-x64.exe'

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
function Write-PayloadManifest([string]$Stage) {
    $manifest = Join-Path $Stage 'payload.manifest.sha256'
    $rows = New-Object System.Collections.Generic.List[string]
    $files = Get-ChildItem -LiteralPath $Stage -File -Recurse | Where-Object { $_.FullName -ne $manifest } | Sort-Object FullName
    foreach ($file in $files) {
        $relative = $file.FullName.Substring($Stage.Length).TrimStart('\')
        $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $file.FullName).Hash.ToLowerInvariant()
        $rows.Add($hash + ' *' + $relative)
    }
    [IO.File]::WriteAllLines($manifest,$rows.ToArray(),([Text.UTF8Encoding]::new($false)))
}
function Assert-Pe64([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing executable: $Path" }
    $bytes = [IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 4096 -or $bytes[0] -ne 0x4D -or $bytes[1] -ne 0x5A) { throw 'Installer is not an MZ executable.' }
    $peOffset = [BitConverter]::ToInt32($bytes,0x3C)
    if ($peOffset -lt 0 -or ($peOffset + 32) -ge $bytes.Length) { throw 'Installer PE header offset is invalid.' }
    if ($bytes[$peOffset] -ne 0x50 -or $bytes[$peOffset + 1] -ne 0x45) { throw 'Installer PE signature is invalid.' }
    if ([BitConverter]::ToUInt16($bytes,$peOffset + 4) -ne 0x8664) { throw 'Installer is not x64.' }
    if ([BitConverter]::ToUInt16($bytes,$peOffset + 24) -ne 0x20B) { throw 'Installer is not PE32+.' }
}
function Convert-HexToBytes([string]$Hex) {
    if (-not $Hex -or ($Hex.Length % 2) -ne 0) { throw 'Invalid hexadecimal hash.' }
    $bytes = New-Object byte[] ($Hex.Length / 2)
    for ($i = 0; $i -lt $bytes.Length; $i++) { $bytes[$i] = [Convert]::ToByte($Hex.Substring($i * 2,2),16) }
    return ,$bytes
}
function Add-PackagePart([IO.FileStream]$OutputStream,[string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Package part is missing: $Path" }
    $offset = [uint64]$OutputStream.Position
    $input = [IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
    try { $input.CopyTo($OutputStream) } finally { $input.Dispose() }
    $size = [uint64]($OutputStream.Position - [int64]$offset)
    if ($size -eq 0) { throw "Package part is empty: $Path" }
    $hash = Convert-HexToBytes ((Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash)
    return [pscustomobject]@{ Offset=$offset; Size=$size; Hash=$hash }
}
function Append-PackageOverlay([string]$ExePath,[string]$Payload,[string]$InstallScript,[string]$UninstallScript,[string]$Icon) {
    $stream = [IO.File]::Open($ExePath,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::Read)
    try {
        [void]$stream.Seek(0,[IO.SeekOrigin]::End)
        $payloadInfo = Add-PackagePart $stream $Payload
        $installInfo = Add-PackagePart $stream $InstallScript
        $uninstallInfo = Add-PackagePart $stream $UninstallScript
        $iconInfo = Add-PackagePart $stream $Icon

        $writer = New-Object System.IO.BinaryWriter($stream)
        try {
            $writer.Write([Text.Encoding]::ASCII.GetBytes('SUTPKG10'))
            $writer.Write([uint32]1)
            $writer.Write([uint32]0)
            foreach ($info in @($payloadInfo,$installInfo,$uninstallInfo,$iconInfo)) {
                $writer.Write([uint64]$info.Offset)
                $writer.Write([uint64]$info.Size)
            }
            foreach ($info in @($payloadInfo,$installInfo,$uninstallInfo,$iconInfo)) { $writer.Write([byte[]]$info.Hash) }
            $writer.Flush()
        } finally { $writer.Dispose() }
    } finally {
        if ($stream) { $stream.Dispose() }
    }
}

function Assert-LeastPrivilegeInstallerSources {
    $installerText = [IO.File]::ReadAllText((Join-Path $Here 'installer.c'))
    $installText = [IO.File]::ReadAllText((Join-Path $Here 'install-core.ps1'))
    $uninstallText = [IO.File]::ReadAllText((Join-Path $Here 'uninstall-core.ps1'))
    $rules = @(
        @{ Name='UAC runas verb'; Text=$installerText; Needle='L"runas"' },
        @{ Name='UAC relaunch helper'; Text=$installerText; Needle='RelaunchElevated' },
        @{ Name='elevation probe'; Text=$installerText; Needle='IsElevated' },
        @{ Name='elevated command flag'; Text=$installerText; Needle='--elevated' },
        @{ Name='machine uninstall registry'; Text=($installText + "`n" + $uninstallText); Needle='HKLM:' },
        @{ Name='machine registry API'; Text=($installText + "`n" + $uninstallText); Needle='::LocalMachine' },
        @{ Name='machine PATH helper'; Text=($installText + "`n" + $uninstallText); Needle='MachinePathEntry' },
        @{ Name='machine environment registry'; Text=($installText + "`n" + $uninstallText); Needle='CurrentControlSet\Control\Session Manager\Environment' },
        @{ Name='common Start Menu'; Text=($installText + "`n" + $uninstallText); Needle='CommonStartMenu' },
        @{ Name='common Desktop'; Text=($installText + "`n" + $uninstallText); Needle='CommonDesktopDirectory' },
        @{ Name='Program Files environment'; Text=$installerText; Needle='ProgramW6432' },
        @{ Name='Program Files default'; Text=$installerText; Needle='GetEnvironmentVariableW(L"ProgramFiles"' }
    )
    foreach ($rule in $rules) {
        if ($rule.Text.IndexOf($rule.Needle,[StringComparison]::OrdinalIgnoreCase) -ge 0) {
            throw ("Least-privilege gate failed: {0}." -f $rule.Name)
        }
    }
    if ($installerText.IndexOf('LOCALAPPDATA',[StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw 'Least-privilege gate failed: LOCALAPPDATA per-user default is missing.'
    }
    if ($installText.IndexOf('HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram',[StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw 'Least-privilege gate failed: HKCU uninstall registration is missing.'
    }
    if ($installText.IndexOf("GetFolderPath('StartMenu')",[StringComparison]::OrdinalIgnoreCase) -lt 0 -or
        $installText.IndexOf("GetFolderPath('DesktopDirectory')",[StringComparison]::OrdinalIgnoreCase) -lt 0) {
        throw 'Least-privilege gate failed: current-user shortcut locations are missing.'
    }
    Write-Host 'Least-privilege source gate passed (no UAC/machine-wide integration).' -ForegroundColor Green
}

Assert-LeastPrivilegeInstallerSources

$gcc = Find-MinGwGcc
if (-not $gcc) { throw 'MinGW x64 GCC was not found.' }
Write-Host ("Installer compiler: {0}" -f $gcc) -ForegroundColor Green
Write-Host 'Resource compiler : not required (v11 uses a SHA-256 package overlay).' -ForegroundColor Green

$compilerExe = Join-Path $Root 'win\sutram.exe'
$guiExe = Join-Path $Root 'sutram-ide-gui.exe'
if (-not (Test-Path -LiteralPath $guiExe -PathType Leaf)) {
    throw 'GUI executable missing: build with windows\gui\build-gui.ps1 before packaging the installer.'
}
$iconSource = Join-Path $Here 'assets\sutram.ico'
if (-not (Test-Path -LiteralPath $compilerExe -PathType Leaf)) { throw 'Native sutram.exe has not been built.' }
if (-not (Test-Path -LiteralPath $iconSource -PathType Leaf)) { throw 'Sutram icon is missing.' }
Assert-Pe64 $compilerExe
Assert-Pe64 $guiExe

Remove-Item -LiteralPath $Work -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $Work,$Output,$PayloadStage,(Join-Path $PayloadStage 'bin'),(Join-Path $PayloadStage 'assets') | Out-Null
Copy-Item -LiteralPath $compilerExe -Destination (Join-Path $PayloadStage 'bin\sutram.exe') -Force
# The GUI locates native compiler relative to its own installation directory.
New-Item -ItemType Directory -Force -Path (Join-Path $PayloadStage 'win') | Out-Null
Copy-Item -LiteralPath $compilerExe -Destination (Join-Path $PayloadStage 'win\sutram.exe') -Force
Copy-Item -LiteralPath $guiExe -Destination (Join-Path $PayloadStage 'sutram-ide-gui.exe') -Force
Copy-Item -LiteralPath $iconSource -Destination (Join-Path $PayloadStage 'assets\sutram.ico') -Force
foreach ($folder in @('lang','examples','docs')) {
    $source = Join-Path $Root $folder
    if (-not (Test-Path -LiteralPath $source -PathType Container)) { throw "Required payload folder is missing: $folder" }
    Copy-Item -LiteralPath $source -Destination (Join-Path $PayloadStage $folder) -Recurse -Force
}
foreach ($name in @('README.md','LICENSE.txt','WINDOWS-NATIVE-README.md')) {
    $source = Join-Path $Root $name
    if (Test-Path -LiteralPath $source -PathType Leaf) { Copy-Item -LiteralPath $source -Destination (Join-Path $PayloadStage $name) -Force }
}
Write-PayloadManifest $PayloadStage

$payloadZip = Join-Path $Work 'payload.zip'
Compress-Archive -Path (Join-Path $PayloadStage '*') -DestinationPath $payloadZip -CompressionLevel Optimal -Force
if ((Get-Item -LiteralPath $payloadZip).Length -lt 1024) { throw 'Payload archive is unexpectedly small.' }

$installerSource = Join-Path $Here 'installer.c'
$installScript = Join-Path $Here 'install-core.ps1'
$uninstallScript = Join-Path $Here 'uninstall-core.ps1'
foreach ($required in @($installerSource,$installScript,$uninstallScript)) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) { throw "Installer source is missing: $required" }
}

Remove-Item -LiteralPath $SetupExe -Force -ErrorAction SilentlyContinue
$gccArguments = @(
    '-std=c11','-O2','-Wall','-Wextra','-municode','-mwindows','-static-libgcc',
    '-Wl,--dynamicbase','-Wl,--nxcompat','-Wl,--high-entropy-va',
    $installerSource,'-o',$SetupExe,
    '-lcomctl32','-lshell32','-lole32','-ladvapi32','-luser32','-lgdi32'
)
Invoke-MinGwGcc $gcc $gccArguments 'MinGW GCC installer link'
Assert-Pe64 $SetupExe

Append-PackageOverlay $SetupExe $payloadZip $installScript $uninstallScript $iconSource
Assert-Pe64 $SetupExe

$selfTest = Start-Process -FilePath $SetupExe -ArgumentList '--self-test' -Wait -PassThru
if ($selfTest.ExitCode -ne 0) { throw "Installer package-overlay self-test failed with exit code $($selfTest.ExitCode)." }
if ((Get-Item -LiteralPath $SetupExe).Length -le (Get-Item -LiteralPath $payloadZip).Length) { throw 'Installer EXE is unexpectedly smaller than its appended payload.' }

$setupHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $SetupExe).Hash
Write-Host 'Native wizard installer built and package-overlay self-test passed.' -ForegroundColor Green
Write-Host ("Setup : {0}" -f $SetupExe) -ForegroundColor Green
Write-Host ("SHA256: {0}" -f $setupHash) -ForegroundColor Green
