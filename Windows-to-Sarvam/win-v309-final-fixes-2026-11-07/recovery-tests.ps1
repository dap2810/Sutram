$ErrorActionPreference='Stop';$out=$PSScriptRoot
function ReadRun([string]$Name){return Get-Content -LiteralPath (Join-Path $out ($Name+'.json')) -Raw|ConvertFrom-Json}
function MustFinish([string]$Name){$r=ReadRun $Name;if($r.status -ne 'FINISH' -or $r.child_exit -ne 0 -or -not $r.wizard_exited){throw "$Name did not finish"}}
MustFinish 'initial'
python (Join-Path $out 'identity.py') --name initial-identity
if($LASTEXITCODE){throw 'Fresh shell is not verified v309; stop'}
if(-not (Test-Path -LiteralPath (Join-Path $out 'backup-working-v309.json'))){
    & (Join-Path $out 'preserve.ps1') -Action backup -Name working-v309
}
$phase='d1'
try{
    & (Join-Path $out 'preserve.ps1') -Action vacate -Name before-d1
    & (Join-Path $out 'run-install.ps1') -Name d1-stop -Moment before
    $d1=ReadRun 'd1-stop'
    if($d1.status -ne 'INTERRUPTED' -or $d1.payload_files_present -ne 0 -or $d1.engine_age_seconds -ge 1){throw 'D1 did not stop before payload copying'}
    & (Join-Path $out 'run-install.ps1') -Name d1-retry
    MustFinish 'd1-retry'
    $phase='d2'
    & (Join-Path $out 'preserve.ps1') -Action vacate -Name before-d2
    & (Join-Path $out 'run-install.ps1') -Name d2-stop -Moment after
    $d2=ReadRun 'd2-stop'
    if($d2.status -eq 'INTERRUPTED'){
        if($d2.payload_files_present -ne 657 -or -not $d2.pending_exists){throw 'D2 stop did not capture the requested boundary'}
        & (Join-Path $out 'run-install.ps1') -Name d2-retry
        MustFinish 'd2-retry'
        $log=[IO.File]::ReadAllText((Join-Path $out 'd2-retry-engine.log'))
        if([regex]::Matches($log,'Already installed ').Count -ne 657 -or [regex]::Matches($log,'\] START ').Count -ne 0){throw 'Late recovery recopied payload files'}
    }elseif($d2.status -eq 'FINISH'){Write-Host 'D2 timing window missed; mark NOT CAUGHT, not a pass.'}
    else{throw 'D2 observer failed'}
    $phase='d3'
    & (Join-Path $out 'preserve.ps1') -Action vacate -Name before-d3
    & (Join-Path $out 'run-install.ps1') -Name d3-stop -Moment middle
    $d3=ReadRun 'd3-stop'
    if($d3.status -ne 'INTERRUPTED' -or $d3.payload_files_present -ge 657){throw 'D3 did not stop partway'}
    $file=Join-Path $env:LOCALAPPDATA 'Programs\Sutram\docs\BUILDING.md'
    if(-not [IO.File]::Exists($file)){throw 'D3 edit target absent'}
    $original=[IO.File]::ReadAllBytes($file)
    [IO.File]::WriteAllBytes((Join-Path $out 'd3-original-BUILDING.md'),$original)
    $before=(Get-FileHash -LiteralPath $file).Hash
    [IO.File]::AppendAllText($file,"`nV309 OWNER-EDIT RECOVERY PROBE: preserve this line.`n",[Text.UTF8Encoding]::new($false))
    $edited=(Get-FileHash -LiteralPath $file).Hash
    Copy-Item -LiteralPath $file -Destination (Join-Path $out 'd3-edited-BUILDING.md')
    & (Join-Path $out 'run-install.ps1') -Name d3-retry
    $actual=(Get-FileHash -LiteralPath $file).Hash;$retry=ReadRun 'd3-retry'
    $result=@{target=$file;original_sha256=$before;edited_sha256=$edited;after_retry_sha256=$actual;edit_preserved=($actual -eq $edited);retry_status=$retry.status;child_exit=$retry.child_exit;warning=$retry.dialog_text;time=[DateTime]::Now.ToString('o')}
    [IO.File]::WriteAllText((Join-Path $out 'd3-edit-result.json'),($result|ConvertTo-Json -Depth 4),[Text.UTF8Encoding]::new($false))
    # Preserve the test edit and its transaction intact; return the machine to
    # the independently verified v309 backup. No user/test file is deleted.
    & (Join-Path $out 'preserve.ps1') -Action restore -Name after-d3 -BackupName working-v309
    $phase='restored'
    python (Join-Path $out 'identity.py') --name final-identity
    if($LASTEXITCODE){throw 'Final installed identity failed'}
    if(-not $result.edit_preserved -or $result.child_exit -ne 1 -or $result.retry_status -ne 'ERROR_DIALOG'){throw 'Edited-file protection or observer failed'}
    $result|ConvertTo-Json -Depth 4
}catch{
    [IO.File]::WriteAllText((Join-Path $out 'recovery-controller-error.txt'),($phase+': '+$_.Exception.ToString()),[Text.UTF8Encoding]::new($false))
    if($phase -ne 'restored'){& (Join-Path $out 'preserve.ps1') -Action restore -Name ($phase+'-failed') -BackupName working-v309}
    throw
}
