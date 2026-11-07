$ErrorActionPreference='Stop'
& (Join-Path $PSScriptRoot 'preserve.ps1') -Action backup -Name before-v310
& (Join-Path $PSScriptRoot 'run-install.ps1') -Name initial
$r=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'initial.json') -Raw|ConvertFrom-Json
if($r.status -ne 'FINISH' -or $r.child_exit -ne 0){throw 'Candidate upgrade failed; original backup retained'}
python (Join-Path $PSScriptRoot 'identity.py') --name initial-identity
if($LASTEXITCODE){throw 'Candidate installed identity failed'}
