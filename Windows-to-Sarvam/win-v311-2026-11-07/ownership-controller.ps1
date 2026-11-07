$ErrorActionPreference='Stop'
$out=$PSScriptRoot
python (Join-Path $out 'ownership.py') edit
if($LASTEXITCODE){throw 'C3 observer failed; inspect its preserved evidence before proceeding'}
python (Join-Path $out 'identity.py') --name after-c3-identity
if($LASTEXITCODE){throw 'C3 baseline restoration failed'}
try {
    & (Join-Path $out 'preserve.ps1') -Action vacate -Name before-c1
    & (Join-Path $out 'run-install.ps1') -Name c1-stop -Moment middle
    python (Join-Path $out 'ownership.py') fixtures
    if($LASTEXITCODE){throw 'C1/C4 fixture observer failed'}
} catch {
    & (Join-Path $out 'preserve.ps1') -Action restore -Name fixture-error -BackupName working-v311
    throw
}
python (Join-Path $out 'identity.py') --name after-c4-identity
if($LASTEXITCODE){throw 'Final baseline restoration failed'}
