$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'preserve.ps1')
& (Join-Path $PSScriptRoot 'upgrade.ps1')
