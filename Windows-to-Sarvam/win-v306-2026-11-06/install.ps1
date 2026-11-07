param([ValidateSet('a3','a4')][string]$Phase='a3')
$ErrorActionPreference='Stop'; $OutDir=$PSScriptRoot
$Root=Split-Path -Parent (Split-Path -Parent $OutDir)
. (Join-Path $OutDir 'ui-helper.ps1')
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Run unelevated' }
$setup=Join-Path $Root 'Sutram-Setup.exe'; $install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
if((Get-FileHash $setup).Hash -ne 'E6006CAF2BACEBF378B9D3B8CD4527D63C1DE6AC2E96EFA630E5C268FF852E5F') { throw 'Unexpected installer' }
if(-not(Test-Path (Join-Path $OutDir 'preserve.json'))) { throw 'Preserve v305 first' }
if($Phase -eq 'a4' -and (Test-Path -LiteralPath $install)) { throw 'Clean target must be absent' }
$r=[ordered]@{phase=$Phase;setup=$setup;sha256=(Get-FileHash $setup).Hash;started=[DateTime]::Now.ToString('o');elevated=$false;observations=@()}
$childProcess=$null
function Save { [IO.File]::WriteAllText((Join-Path $OutDir ($Phase+'.json')),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false)) }
function Click([int]$Id) { [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,$Id),0xF5,0,0,3000); Start-Sleep -Milliseconds 250 }
try {
    $ip=Start-Process -FilePath $setup -WorkingDirectory $Root -WindowStyle Normal -PassThru
    $r.pid=$ip.Id; Save
    $main=Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id,'SutramWizardWindow')|Select-Object -First 1 } 10000
    if(-not $main) { throw 'Wizard did not open' }
    Click 2002; Click 2010; Click 2002
    $r.destination=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2020))
    if($r.destination -ne $install) { throw 'Unexpected destination' }
    Click 2002
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2030),0xF1,1,0,3000)
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2031),0xF1,1,0,3000)
    Click 2002; $r.ready=Shot $main ($Phase+'-ready'); Click 2002
    $watch=[Diagnostics.Stopwatch]::StartNew()
    while($watch.Elapsed.TotalSeconds -lt 930) {
        Start-Sleep -Milliseconds 500
        $children=@(Get-CimInstance Win32_Process -Filter "ParentProcessId = $($ip.Id)" | Where-Object {$_.Name -eq 'powershell.exe'} | Select-Object ProcessId,ParentProcessId,CommandLine)
        $visible=@()
        foreach($p in $children) {
            if(-not $childProcess) { $childProcess=Get-Process -Id $p.ProcessId; $r.child=$p; $m=[regex]::Match($p.CommandLine,'-LogPath\s+"([^"]+)"'); if($m.Success) { $r.engine_log=$m.Groups[1].Value } }
            $visible+=@([SutramIde]::WindowsOf([uint32]$p.ProcessId,$null)|Where-Object {[SutramIde]::IsWindowVisible($_)}|ForEach-Object {$_.ToInt64()})
        }
        $dialogs=@([SutramIde]::WindowsOf([uint32]$ip.Id,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)})
        $label=''; try {$label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002))} catch {$label='UI timeout'}
        $r.observations+=@{seconds=[math]::Round($watch.Elapsed.TotalSeconds,2);children=$children.Count;visible_child_windows=$visible;next_label=$label;dialogs=$dialogs.Count}; Save
        if($dialogs.Count) {
            $r.dialog_text=[SutramIde]::ChildTexts($dialogs[0])
            $r.dialog_seconds=[math]::Round($watch.Elapsed.TotalSeconds,2)
            $r.error_screenshot=Shot $dialogs[0] ($Phase+'-error')
            $r.status='ERROR_DIALOG'
            if($r.Contains('engine_log')) { Copy-Item -LiteralPath $r.engine_log -Destination (Join-Path $OutDir ($Phase+'-engine.log')) }
            [void][SutramIde]::Send([SutramIde]::GetDlgItem($dialogs[0],1),0xF5,0,0,3000)
            break
        }
        if($label -eq 'Finish') {
            $r.status='FINISH'; $r.finish_seconds=[math]::Round($watch.Elapsed.TotalSeconds,2)
            $r.finish_screenshot=Shot $main ($Phase+'-finish')
            Copy-Item -LiteralPath (Join-Path $install 'install.log') -Destination (Join-Path $OutDir ($Phase+'-engine.log'))
            break
        }
    }
    if(-not $r.Contains('status')) { $r.status='NO_RESULT_AFTER_930_SECONDS' }
    $r.observed_seconds=[math]::Round($watch.Elapsed.TotalSeconds,2)
    if($r.Contains('engine_log') -and (Test-Path -LiteralPath $r.engine_log)) { Copy-Item -LiteralPath $r.engine_log -Destination (Join-Path $OutDir ($Phase+'-engine.log')) -Force }
    if($childProcess -and $childProcess.HasExited) { $childProcess.WaitForExit(); $r.child_exit=$childProcess.ExitCode; $r.child_exited=$true }
    [void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero)
    $r.closed=$ip.WaitForExit(3000); Save
    & (Join-Path $OutDir 'snapshot.ps1') ($Phase+'-after')
    Write-Host "$Phase result: $($r.status); wizard closed: $($r.closed)"
} catch { $r.error=$_.Exception.Message; Save; throw }
