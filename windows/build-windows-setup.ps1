$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $Root
try {
    Write-Host '[0/3] Preflight checks...' -ForegroundColor Cyan
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\preflight-windows.ps1'
    $stageCode = $LASTEXITCODE
    if ($stageCode -ne 0) { throw "Preflight failed with exit code $stageCode." }

    Write-Host ''
    Write-Host '[1/3] Building and smoke-testing native Sutram compiler host...' -ForegroundColor Cyan
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\build-windows-native.ps1'
    $stageCode = $LASTEXITCODE
    if ($stageCode -ne 0) { throw "Native compiler build or smoke test failed with exit code $stageCode." }

    Write-Host ''
    Write-Host '[2/3] Building native Win32 wizard setup...' -ForegroundColor Cyan
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\windows-installer-native\build-installer.ps1'
    $stageCode = $LASTEXITCODE
    if ($stageCode -ne 0) { throw "Native installer build failed with exit code $stageCode." }

    Write-Host ''
    Write-Host '[3/3] Final release verification...' -ForegroundColor Cyan
    $setup = '.\windows-installer-native\output\Sutram-Setup-0.1.0-native-x64.exe'
    if (-not (Test-Path -LiteralPath $setup -PathType Leaf)) { throw "Setup file was not produced: $setup" }
    $resolvedSetup = (Resolve-Path -LiteralPath $setup).Path
    $bytes = [IO.File]::ReadAllBytes($resolvedSetup)
    if ($bytes.Length -lt 4096 -or $bytes[0] -ne 0x4D -or $bytes[1] -ne 0x5A) { throw 'Setup output is not a valid Windows executable.' }
    $peOffset = [BitConverter]::ToInt32($bytes,0x3C)
    if ($peOffset -lt 0 -or ($peOffset + 26) -ge $bytes.Length) { throw 'Setup PE header offset is invalid.' }
    if ($bytes[$peOffset] -ne 0x50 -or $bytes[$peOffset + 1] -ne 0x45) { throw 'Setup PE signature is invalid.' }
    if ([BitConverter]::ToUInt16($bytes,$peOffset + 4) -ne 0x8664) { throw 'Setup output is not an x64 PE executable.' }
    if ([BitConverter]::ToUInt16($bytes,$peOffset + 24) -ne 0x20B) { throw 'Setup output is not PE32+.' }

    $selfTest = Start-Process -FilePath $resolvedSetup -ArgumentList '--self-test' -Wait -PassThru
    if ($selfTest.ExitCode -ne 0) { throw "Final setup resource self-test failed with exit code $($selfTest.ExitCode)." }

    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $resolvedSetup).Hash
    $releaseCopy = Join-Path $Root 'Sutram-Setup.exe'
    Copy-Item -LiteralPath $resolvedSetup -Destination $releaseCopy -Force
    $releaseHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $releaseCopy).Hash
    if ($releaseHash -ne $hash) { throw 'Release-copy SHA-256 verification failed.' }
    Write-Host ''
    Write-Host 'BUILD PASSED ALL WINDOWS RELEASE CHECKS.' -ForegroundColor Green
    Write-Host ("Setup : {0}" -f $resolvedSetup) -ForegroundColor Green
    Write-Host ("Release copy: {0}" -f $releaseCopy) -ForegroundColor Green
    Write-Host ("SHA256: {0}" -f $hash) -ForegroundColor Green
    Write-Host 'Installer: native 64-bit Win32 wizard; no windres, IExpress, or Inno Setup dependency.' -ForegroundColor Green
    Write-Host 'End-user runtime: no NASM, MinGW, Visual Studio, WSL, or Linux required.' -ForegroundColor Green
    Write-Host 'Compiler status: native Windows compiler host; generated Sutram programs still use the transitional ELF backend.' -ForegroundColor Yellow
} finally {
    Pop-Location
}
