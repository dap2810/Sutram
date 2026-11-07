$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$out=Join-Path $root 'Windows-to-Sarvam\win-v307-fixes-2026-11-06'
$upgrade=Get-Content -LiteralPath (Join-Path $out 'upgrade.json') -Raw|ConvertFrom-Json
if($upgrade.status -ne 'FINISH' -or $upgrade.child_exit -ne 0 -or -not $upgrade.wizard_exited){throw 'Upgrade not complete'}
& (Join-Path $PSScriptRoot 'restore-native.ps1') -Phase upgrade -PreserveOnly
& (Join-Path $out 'install.ps1') -Phase clean
$clean=Get-Content -LiteralPath (Join-Path $out 'clean.json') -Raw|ConvertFrom-Json
if($clean.status -ne 'FINISH' -or $clean.child_exit -ne 0){throw 'Clean installation failed; restore baseline'}
& (Join-Path $PSScriptRoot 'restore-native.ps1') -Phase clean -PreserveOnly
& (Join-Path $out 'install.ps1') -Phase interrupt
$interrupt=Get-Content -LiteralPath (Join-Path $out 'interrupt.json') -Raw|ConvertFrom-Json
if($interrupt.status -ne 'INTERRUPTED_AS_REQUESTED' -or -not $interrupt.pending_exists){throw 'Interruption fixture failed'}
Copy-Item -LiteralPath (Join-Path $env:LOCALAPPDATA 'Programs\Sutram\payload.pending.sha256') -Destination (Join-Path $out 'interrupted-payload.pending.sha256')
& (Join-Path $out 'install.ps1') -Phase recovery
$recovery=Get-Content -LiteralPath (Join-Path $out 'recovery.json') -Raw|ConvertFrom-Json
if($recovery.status -ne 'FINISH' -or $recovery.child_exit -ne 0){throw 'Recovery failed; restore baseline'}
Copy-Item -LiteralPath (Join-Path $root 'Windows-to-Sarvam\win-v307-2026-11-06\identity.py') -Destination $out
python (Join-Path $out 'identity.py')
if($LASTEXITCODE){throw 'Final installed identity failed'}
python (Join-Path $out 'security-log-read.py')
