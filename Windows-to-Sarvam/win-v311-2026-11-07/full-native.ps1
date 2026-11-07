$ErrorActionPreference='Stop'
$out=$PSScriptRoot
& (Join-Path $out 'initial-install.ps1')
python (Join-Path $out 'ownership.py') concurrency
if($LASTEXITCODE){throw 'Concurrency observer failed'}
& (Join-Path $out 'ownership-controller.ps1')
python (Join-Path $out 'ownership.py') ordinary
if($LASTEXITCODE){throw 'Ordinary recovery failed'}
& (Join-Path $out 'verify-saved.ps1')
