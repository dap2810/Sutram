$ErrorActionPreference='Stop'
$OutDir=$PSScriptRoot
$Root=Split-Path -Parent (Split-Path -Parent $OutDir)
. (Join-Path $OutDir 'ui-helper.ps1')
$setup=Join-Path $Root 'Sutram-Setup.exe'
$backup=Get-Content (Join-Path $OutDir 'backup.json') -Raw|ConvertFrom-Json
if($backup.status -ne 'PRESERVED' -or (Test-Path -LiteralPath $backup.source)) { throw 'Expected preserved backup and absent canonical installation' }
if((Get-FileHash $setup).Hash -ne '99D26A89F355A2B20BDF7FE1FBD94AA8E304C3EAE3A9B54C8364ECF8F1E6E6F5') { throw 'Unexpected installer' }
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Run unelevated' }
$r=[ordered]@{setup=$setup;sha256=(Get-FileHash $setup).Hash;started=[DateTime]::Now.ToString('o');elevated=$false;observations=@()}
function Save { [IO.File]::WriteAllText((Join-Path $OutDir 'install.json'),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false)) }
function Click([int]$Id) { [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,$Id),0xF5,0,0,3000); Start-Sleep -Milliseconds 250 }
Start-Transcript -Path (Join-Path $OutDir 'install-transcript.txt') -Force
try {
    $ip=Start-Process -FilePath $setup -WorkingDirectory $Root -WindowStyle Normal -PassThru
    $r.pid=$ip.Id; Save
    $main=Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id,'SutramWizardWindow')|Select-Object -First 1 } 10000
    if(-not $main) { throw 'Wizard did not open' }
    $r.main_hwnd=$main.ToInt64()
    Click 2002; Click 2010; Click 2002
    $r.destination=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2020))
    if($r.destination -ne $backup.source) { throw 'Unexpected install destination' }
    Click 2002
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2030),0xF1,1,0,3000)
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2031),0xF1,1,0,3000)
    Click 2002
    $r.ready=Shot $main 'ready'; Click 2002
    $watch=[Diagnostics.Stopwatch]::StartNew()
    while($watch.Elapsed.TotalSeconds -lt 120) {
        Start-Sleep -Seconds 2
        $children=@(Get-CimInstance Win32_Process -Filter "ParentProcessId = $($ip.Id)" | Where-Object {$_.Name -eq 'powershell.exe'} | Select-Object ProcessId,ParentProcessId,CommandLine)
        foreach($p in $children) {
            if(-not $r.Contains('engine_log')) {
                $r.child=$p
                $m=[regex]::Match($p.CommandLine,'-LogPath\s+"([^"]+)"')
                if($m.Success) { $r.engine_log=$m.Groups[1].Value }
            }
        }
        $label=''
        try { $label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002)) } catch { $label='UI not responding' }
        $r.observations+=@{seconds=[math]::Round($watch.Elapsed.TotalSeconds,1);children=$children.Count;next_label=$label}
        Save
        if($label -eq 'Finish') { $r.finished=$true; break }
    }
    if($r.Contains('finished') -and $r.finished) {
        $r.screenshot=Shot $main 'installer-finished'
        # Close the completed wizard without activating its optional IDE launch.
        [void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero)
        $r.closed=$ip.WaitForExit(3000)
        Copy-Item -LiteralPath (Join-Path $backup.source 'install.log') -Destination (Join-Path $OutDir 'engine.log')
        $r.status='WIZARD_FINISHED'
    } else {
        $r.status='NEEDS_INVESTIGATION'
        if($r.Contains('engine_log') -and (Test-Path -LiteralPath $r.engine_log)) { Copy-Item -LiteralPath $r.engine_log -Destination (Join-Path $OutDir 'engine.log') }
        foreach($p in $children) { & python (Join-Path $OutDir 'console.py') $p.ProcessId read (Join-Path $OutDir 'stalled-console.json') }
    }
    Save
    & (Join-Path $OutDir 'snapshot.ps1') after
    Write-Host "Installer result: $($r.status)"
} catch { $r.error=$_.Exception.Message; Save; throw }
finally { Stop-Transcript }
