$ErrorActionPreference='Stop'
# Finish the current observation before touching its processes or installed files.
$deadline=[DateTime]::Now.AddMinutes(20)
do{
    if([DateTime]::Now -gt $deadline){throw 'Observer did not finish; no cleanup performed'}
    Start-Sleep -Seconds 5
    try{$upgrade=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'upgrade.json') -Raw|ConvertFrom-Json}catch{continue}
}until($upgrade.ended -and $upgrade.status)
if($upgrade.status -ne 'FINISH'){
    & (Join-Path $PSScriptRoot 'restore-after-test.ps1') -Phase upgrade
}
Write-Host 'Upgrade observation complete; starting controlled partial-install test.'
& (Join-Path $PSScriptRoot 'run-install.ps1') -Phase interrupt
$interrupted=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'interrupt.json') -Raw|ConvertFrom-Json
if($interrupted.status -ne 'INTERRUPTED_AS_REQUESTED' -or -not $interrupted.pending_exists){throw 'Did not obtain the requested partial installation; inspect before proceeding'}
$pending=Join-Path $env:LOCALAPPDATA 'Programs\Sutram\payload.pending.sha256'
Copy-Item -LiteralPath $pending -Destination (Join-Path $PSScriptRoot 'interrupted-payload.pending.sha256')
Write-Host 'Deliberate interruption captured; retrying the same partial installation.'
& (Join-Path $PSScriptRoot 'run-install.ps1') -Phase recovery
$recovery=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'recovery.json') -Raw|ConvertFrom-Json
if($recovery.status -ne 'FINISH'){
    & (Join-Path $PSScriptRoot 'restore-after-test.ps1') -Phase recovery
}
python (Join-Path $PSScriptRoot 'identity.py')
if($LASTEXITCODE -ne 0){throw 'Final installed identity/manifest failed'}
python (Join-Path $PSScriptRoot 'security-log-read.py')
Write-Host 'Installer tests and final installed-state verification finished.'
