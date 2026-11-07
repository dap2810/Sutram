param([ValidateSet('clean','upgrade','interrupt','recovery')][string]$Phase)
$ErrorActionPreference='Stop'
if($Phase -ne 'recovery'){& (Join-Path $PSScriptRoot 'prepare.ps1') -Phase $Phase}
& (Join-Path $PSScriptRoot 'install.ps1') -Phase $Phase
