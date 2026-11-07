$ErrorActionPreference='Stop'
$OutDir=$PSScriptRoot
$Root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
. (Join-Path $PSScriptRoot 'ui-helper.ps1')
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Diagnostic must be unelevated' }
$setup=Join-Path $Root 'Sutram-Setup.exe'
if ((Get-FileHash $setup).Hash -ne '99D26A89F355A2B20BDF7FE1FBD94AA8E304C3EAE3A9B54C8364ECF8F1E6E6F5') { throw 'Installer changed; inspect before testing' }
$r=[ordered]@{setup=$setup;sha256=(Get-FileHash $setup).Hash;started=[DateTime]::Now.ToString('o');elevated=$false;observations=@()}
function Save-Record { [IO.File]::WriteAllText((Join-Path $OutDir 'installer.json'),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false)) }
function Observe([string]$Phase) {
    $all=@(Get-CimInstance Win32_Process)
    $ids=[Collections.Generic.List[uint32]]::new(); $ids.Add([uint32]$ip.Id)
    do { $added=$false; foreach ($p in $all) { if ($ids.Contains([uint32]$p.ParentProcessId) -and -not $ids.Contains([uint32]$p.ProcessId)) { $ids.Add([uint32]$p.ProcessId); $added=$true } } } while ($added)
    $tree=@($all|Where-Object {$ids.Contains([uint32]$_.ProcessId)}|Select-Object ProcessId,ParentProcessId,Name,CommandLine,CreationDate)
    $row=[ordered]@{phase=$Phase;time=[DateTime]::Now.ToString('o');tree=$tree;processes=@(Get-Process | Where-Object {$_.ProcessName -match 'powershell|sutram|wscript|cscript'} | Select-Object Id,ProcessName,StartTime,CPU)}
    $r.observations+= $row
    Save-Record
    foreach ($p in $tree | Where-Object {$_.Name -eq 'powershell.exe' -and $_.CommandLine -like '*install-core.ps1*'}) {
        Write-Host "Installer child PID $($p.ProcessId): $($p.CommandLine)"
        & python (Join-Path $OutDir 'console.py') $p.ProcessId read (Join-Path $OutDir ($Phase+'-console.json'))
        $c=Get-Content (Join-Path $OutDir ($Phase+'-console.json')) -Raw | ConvertFrom-Json
        if ($c.text) { Write-Host $c.text }
        $m=[regex]::Match($p.CommandLine,'-LogPath\s+"([^"]+)"')
        if ($m.Success -and (Test-Path -LiteralPath $m.Groups[1].Value)) {
            $r.engine_log=$m.Groups[1].Value
            Copy-Item -LiteralPath $r.engine_log -Destination (Join-Path $OutDir ($Phase+'-engine.log'))
        }
    }
    Save-Record
}
function Click-Control([int]$Id) {
    $h=[SutramIde]::GetDlgItem($main,$Id)
    if ($h -eq [IntPtr]::Zero) { throw "Control missing: $Id" }
    [void][SutramIde]::Send($h,0xF5,0,0,3000)
    Start-Sleep -Milliseconds 250
}
Start-Transcript -Path (Join-Path $OutDir 'transcript.txt') -Force
try {
    & (Join-Path $OutDir 'snapshot.ps1') before
    Write-Host "Starting current installer $setup; SHA256 $($r.sha256); unelevated."
    $ip=Start-Process -FilePath $setup -WorkingDirectory $Root -WindowStyle Normal -PassThru
    $r.pid=$ip.Id; Save-Record
    $main=Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id,'SutramWizardWindow') | Select-Object -First 1 } 10000
    if (-not $main) { throw 'Wizard did not appear within 10 seconds' }
    $r.main_hwnd=$main.ToInt64(); $r.welcome=Shot $main 'welcome'; Save-Record
    Click-Control 2002; Click-Control 2010; Click-Control 2002
    $r.destination=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2020))
    if ($r.destination.TrimEnd('\') -ne (Join-Path $env:LOCALAPPDATA 'Programs\Sutram')) { throw 'Unexpected destination' }
    Click-Control 2002
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2030),0xF1,1,0,3000)
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2031),0xF1,0,0,3000)
    Click-Control 2002
    $r.ready=Shot $main 'ready'; Save-Record
    Click-Control 2002
    Start-Sleep -Seconds 1
    Observe 'after-1s'
    Start-Sleep -Seconds 9
    Observe 'after-10s'
    Write-Host 'Observing for another 60 seconds without input.'
    Start-Sleep -Seconds 60
    Observe 'after-70s'
    try {
        [void][SutramIde]::Send($main,0,0,0,1000)
        $r.observed=Shot $main 'after-70s-wizard'
        $r.next_label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002))
    } catch { $r.capture_error=$_.Exception.Message }
    $liveChildren=@((Get-CimInstance Win32_Process)|Where-Object {$_.ParentProcessId -eq $ip.Id -and $_.Name -eq 'powershell.exe'})
    if ($liveChildren.Count -eq 0) {
        $r.enter_test='NOT APPLICABLE: installer PowerShell already exited'
        $r.y_enter_test='NOT APPLICABLE: installer PowerShell already exited'
        [void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero)
        if (-not $ip.WaitForExit(3000)) { $ip.Kill(); [void]$ip.WaitForExit(3000); $r.forced_wizard_close=$true }
        $r.status='CHILD_EXITED_WITHOUT_HANG'
    } else { $r.status='AWAITING_INPUT_DIAGNOSTIC' }
    Save-Record
    & (Join-Path $OutDir 'snapshot.ps1') after
    Write-Host "Observation result: $($r.status)"
} catch { $r.error=$_.Exception.Message; Save-Record; throw }
finally { Stop-Transcript }
