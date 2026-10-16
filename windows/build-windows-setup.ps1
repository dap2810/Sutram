# R69: canonical entry -> linked GUI -> actual native-installer, as a standard user.
[CmdletBinding()]
param([switch]$ReplaceOutput)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
. (Join-Path $PSScriptRoot 'r69-build-common.ps1')
Assert-R69StandardUser
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Assert-R69SourcePins $Root
$powerShell = Join-Path $PSHOME 'powershell.exe'
if (-not (Test-Path -LiteralPath $powerShell -PathType Leaf)) {
    throw 'Use Windows PowerShell 5.1 for this Windows build. No policy change is made by this script.'
}
$nativeBuilder = Join-Path $PSScriptRoot 'build-windows-native.ps1'
$guiBuilder = Join-Path $PSScriptRoot 'gui\build-gui.ps1'
$installerBuilder = Join-Path $PSScriptRoot 'native-installer\build-installer.ps1'
$setup = Join-Path $PSScriptRoot 'native-installer\output\Sutram-Setup-0.1.0-native-x64.exe'
$release = Join-Path $Root 'Sutram-Setup.exe'
foreach ($file in @($nativeBuilder,$guiBuilder,$installerBuilder)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Required builder missing: $file" }
}
# Fail before expensive work rather than overwrite an existing release accidentally.
if ((Get-Item -LiteralPath $release -Force -ErrorAction SilentlyContinue) -and -not $ReplaceOutput) {
    throw 'Sutram-Setup.exe already exists. Pass -ReplaceOutput explicitly to replace a build artifact.'
}
Write-Host '[1/4] Build canonical compiler and run its native smoke checks.'
$argsNative = @('-NoProfile','-NonInteractive','-File',$nativeBuilder)
if ($ReplaceOutput) { $argsNative += '-ReplaceOutput' }
$result = Invoke-R69Process $powerShell $argsNative $Root 300
Write-Host $result.Stdout
Write-Host '[2/4] Rebuild the GUI with the linked cluster helpers.'
$result = Invoke-R69Process $powerShell @('-NoProfile','-NonInteractive','-File',$guiBuilder) $Root 180
Write-Host $result.Stdout
Assert-R69Pe64 (Join-Path $Root 'win\sutram.exe')
Assert-R69Pe64 (Join-Path $Root 'sutram-ide-gui.exe')
$compilerHash = (Get-FileHash -LiteralPath (Join-Path $Root 'win\sutram.exe') -Algorithm SHA256).Hash
$guiHash = (Get-FileHash -LiteralPath (Join-Path $Root 'sutram-ide-gui.exe') -Algorithm SHA256).Hash
Write-Host '[3/4] Build the per-user native installer; retain its least-privilege and payload gates.'
$result = Invoke-R69Process $powerShell @('-NoProfile','-NonInteractive','-File',$installerBuilder) $Root 900
Write-Host $result.Stdout
Assert-R69Pe64 $setup
# Verify the actual staging files, not only the top-level input binaries.
$payload = Join-Path $PSScriptRoot 'native-installer\work\payload'
foreach ($path in @('bin\sutram.exe','win\sutram.exe')) {
    if ((Get-FileHash -LiteralPath (Join-Path $payload $path) -Algorithm SHA256).Hash -ne $compilerHash) {
        throw "Installer staged a different compiler: $path"
    }
}
if ((Get-FileHash -LiteralPath (Join-Path $payload 'sutram-ide-gui.exe') -Algorithm SHA256).Hash -ne $guiHash) {
    throw 'Installer staged a different GUI.'
}
Write-Host '[4/4] Bounded resource self-test and verified candidate publication.'
[void](Invoke-R69Process $setup @('--self-test') $Root 30)
Assert-R69SourcePins $Root
Publish-R69Artifact $setup $release ([bool]$ReplaceOutput)
Write-Host "Installer candidate: $release"
Write-Host ('SHA256: ' + (Get-FileHash -LiteralPath $release -Algorithm SHA256).Hash)
Write-Host 'Resource tests do not prove install/uninstall or GUI behavior. Complete real Windows acceptance before release.'
