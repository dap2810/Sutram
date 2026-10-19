$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'preflight-windows.ps1')
& (Join-Path $PSScriptRoot 'build-windows-native.ps1')
& (Join-Path $PSScriptRoot 'gui\build-gui.ps1')
& (Join-Path $PSScriptRoot 'native-installer\build-installer.ps1')
Write-Host 'Build complete. No installation or Windows integration was performed.'
Write-Host 'Desktop and install/uninstall acceptance must pass before release.'
