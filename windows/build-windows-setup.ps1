$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $Root
try {
    Write-Host '[0/4] Preflight checks...'
    & powershell.exe -NoProfile -File '.\preflight-windows.ps1'
    if ($LASTEXITCODE -ne 0) { throw "Preflight failed ($LASTEXITCODE)." }
    Write-Host '[1/4] Building native compiler...'
    & powershell.exe -NoProfile -File '.\build-windows-native.ps1'
    if ($LASTEXITCODE -ne 0) { throw "Native compiler build failed ($LASTEXITCODE)." }
    Write-Host '[2/4] Building GUI with linked cluster helper...'
    & powershell.exe -NoProfile -File '.\gui\build-gui.ps1'
    if ($LASTEXITCODE -ne 0) { throw "GUI build failed ($LASTEXITCODE)." }
    Write-Host '[3/4] Building supported per-user native installer...'
    & powershell.exe -NoProfile -File '.\native-installer\build-installer.ps1'
    if ($LASTEXITCODE -ne 0) { throw "Native installer build failed ($LASTEXITCODE)." }
    Write-Host '[4/4] Verifying package...'
    $setup = Join-Path $Root 'native-installer\output\Sutram-Setup-0.1.0-native-x64.exe'
    if (-not (Test-Path -LiteralPath $setup -PathType Leaf)) { throw "Setup missing: $setup" }
    $bytes = [IO.File]::ReadAllBytes($setup)
    if ($bytes.Length -lt 4096 -or $bytes[0] -ne 0x4d -or $bytes[1] -ne 0x5a) { throw 'Invalid MZ output.' }
    $pe = [BitConverter]::ToInt32($bytes,0x3c)
    if ($pe -lt 0 -or ($pe + 26) -gt $bytes.Length -or
        $bytes[$pe] -ne 0x50 -or $bytes[$pe+1] -ne 0x45 -or
        [BitConverter]::ToUInt16($bytes,$pe+4) -ne 0x8664 -or
        [BitConverter]::ToUInt16($bytes,$pe+24) -ne 0x20b) { throw 'Invalid PE32+ AMD64 package.' }
    $p = Start-Process -FilePath $setup -ArgumentList '--self-test' -PassThru
    try {
        if (-not $p.WaitForExit(15000)) {
            try { $p.Kill() } catch {}
            throw 'Setup resource self-test timed out after 15 seconds.'
        }
        if ($p.ExitCode -ne 0) { throw "Setup resource self-test failed ($($p.ExitCode))." }
    } finally { $p.Dispose() }
    $hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $setup).Hash
    $releaseCopy = Join-Path $Root 'Sutram-Setup.exe'
    Copy-Item -LiteralPath $setup -Destination $releaseCopy -Force
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $releaseCopy).Hash -ne $hash) { throw 'Release-copy hash mismatch.' }
    Write-Host "Package format and resource checks passed: $releaseCopy"
    Write-Host "SHA256: $hash"
    Write-Host 'This is not GUI/installer acceptance. Perform the standard-user Windows checklist and inspect the log/screenshots.'
} finally { Pop-Location }
