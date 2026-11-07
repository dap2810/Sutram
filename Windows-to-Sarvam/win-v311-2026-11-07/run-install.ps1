param([Parameter(Mandatory=$true)][ValidatePattern('^[a-z0-9-]+$')][string]$Name,[ValidateSet('complete','before','after','middle')][string]$Moment='complete')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
$Root=Split-Path -Parent (Split-Path -Parent $OutDir)
. (Join-Path $OutDir 'ui-helper.ps1')
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Run unelevated'}
$setup=Join-Path $Root 'build\native-v311\Sutram-Setup.exe'
$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram';$txn=$install+'.sutram-transaction'
if((Get-FileHash -LiteralPath $setup).Hash -ne (Get-Content (Join-Path $OutDir 'candidate.json') -Raw|ConvertFrom-Json).setup_sha256){throw 'Setup hash changed'}
if($Moment -ne 'complete' -and ((Test-Path -LiteralPath $install) -or (Test-Path -LiteralPath $txn))){throw 'Stop-phase requires absent target/transaction'}
$manifest=@(Get-Content -LiteralPath (Join-Path $OutDir 'payload.manifest.sha256')|ForEach-Object {($_ -split ' \*',2)[1]})
$last=($manifest|Sort-Object|Select-Object -Last 1)
$r=[ordered]@{name=$Name;moment=$Moment;setup=$setup;setup_sha256=(Get-FileHash $setup).Hash;started=[DateTime]::Now.ToString('o');observations=@();live_log_opened=$false}
$child=$null;$wizard=$null;$script:captureWarnings=@()
function Save{[IO.File]::WriteAllText((Join-Path $OutDir ($Name+'.json')),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))}
function Click([int]$Id){$h=Wait-Until {$c=[SutramIde]::GetDlgItem($main,$Id);if($c -ne [IntPtr]::Zero -and [SutramIde]::IsWindowVisible($c)){$c}} 5000;if(-not $h){throw "Control $Id unavailable"};if(-not [SutramIde]::PostMessageW($h,0xF5,[IntPtr]::Zero,[IntPtr]::Zero)){throw 'Button click could not be posted'};Start-Sleep -Milliseconds 120}
function ReadShared([string]$Path){$f=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete));try{$m=[IO.MemoryStream]::new();try{$f.CopyTo($m);return ,$m.ToArray()}finally{$m.Dispose()}}finally{$f.Dispose()}}
try{
    $wizard=Start-Process -FilePath $setup -WorkingDirectory $Root -WindowStyle Normal -PassThru
    [void]$wizard.Handle;$r.pid=$wizard.Id;$r.process_started=$wizard.StartTime.ToString('o');Save
    $main=Wait-Until {[SutramIde]::WindowsOf([uint32]$wizard.Id,'SutramWizardWindow')|Select-Object -First 1} 10000
    if(-not $main){throw 'Wizard did not open'}
    Click 2002;Click 2010;Click 2002
    $r.destination=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2020))
    if($r.destination -ne $install){throw 'Destination mismatch'}
    Click 2002
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2030),0xF1,1,0,3000)
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2031),0xF1,1,0,3000)
    Click 2002;$r.ready_screenshot=Shot $main ($Name+'-ready')
    $watch=[Diagnostics.Stopwatch]::StartNew();Click 2002;$lastRecord=-5;$lastUI=-1
    while($watch.Elapsed.TotalSeconds -lt 240){
        if(-not $child){
            $p=Get-CimInstance Win32_Process -Filter "ParentProcessId = $($wizard.Id)"|Where-Object {$_.Name -eq 'powershell.exe'}|Select-Object -First 1
            if($p){$child=Get-Process -Id $p.ProcessId;[void]$child.Handle;$r.child=@{pid=$child.Id;parent=$p.ParentProcessId;command=$p.CommandLine;started=$child.StartTime.ToString('o')};$m=[regex]::Match($p.CommandLine,'-LogPath\s+"([^"]+)"');if($m.Success){$r.engine_log=$m.Groups[1].Value};Save}
        }
        $stop=$false
        if($child -and -not $child.HasExited){
            if($Moment -eq 'before'){$stop=$true}
            elseif($Moment -eq 'middle'){$stop=[IO.File]::Exists((Join-Path $install 'docs\BUILDING.md')) -and -not [IO.File]::Exists((Join-Path $install $last))}
            elseif($Moment -eq 'after'){$stop=[IO.File]::Exists((Join-Path $install $last)) -and [IO.File]::Exists((Join-Path $install 'payload.pending.sha256'))}
        }
        if($stop){
            $r.stop_observed_at=[DateTime]::Now.ToString('o');$r.seconds=$watch.Elapsed.TotalSeconds
            $r.engine_age_seconds=([DateTime]::Now-$child.StartTime).TotalSeconds
            if(-not $child.HasExited){$child.Kill();[void]$child.WaitForExit(5000)}
            if(-not $wizard.HasExited){$wizard.Kill();[void]$wizard.WaitForExit(5000)}
            $r.status='INTERRUPTED';break
        }
        if($watch.Elapsed.TotalSeconds-$lastUI -ge 0.3){
            $dialogs=@([SutramIde]::WindowsOf([uint32]$wizard.Id,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)})
            if($dialogs.Count){$r.status='ERROR_DIALOG';$r.dialog_text=[SutramIde]::ChildTexts($dialogs[0]);$r.error_screenshot=Shot $dialogs[0] ($Name+'-error');if(-not [SutramIde]::PostMessageW([SutramIde]::GetDlgItem($dialogs[0],1),0xF5,[IntPtr]::Zero,[IntPtr]::Zero)){throw 'Dialog acknowledgement could not be posted'};$r.dialog_closed=$wizard.WaitForExit(5000);break}
            try{$label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002))}catch{$label='UI timeout'}
            if($label -eq 'Finish'){
                $r.status='FINISH';$r.finish_seconds=$watch.Elapsed.TotalSeconds
                [void][SutramIde]::SetForegroundWindow($main);Start-Sleep -Milliseconds 500
                $r.finish_screenshot=Shot $main ($Name+'-finish')
                [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2060),0xF1,0,0,3000)
                Click 2002;$r.closed_after_finish_click=$wizard.WaitForExit(5000);break
            }
            if($watch.Elapsed.TotalSeconds-$lastRecord -ge 5){$r.observations+=@{seconds=$watch.Elapsed.TotalSeconds;next_label=$label;child_exited=($child -and $child.HasExited)};Save;$lastRecord=$watch.Elapsed.TotalSeconds}
            if($wizard.HasExited){$r.status='EXIT_WITHOUT_FINISH';break}
            $lastUI=$watch.Elapsed.TotalSeconds
        }
        Start-Sleep -Milliseconds $(if($Moment -eq 'complete'){120}else{5})
    }
    if(-not $r.Contains('status')){$r.status='OBSERVER_LIMIT_240_SECONDS'}
    $r.observed_seconds=$watch.Elapsed.TotalSeconds
}catch{$r.observer_error=$_.Exception.Message;$r.status='OBSERVER_ERROR';Save;throw}
finally{
    # A failed observation must not leave our wizard/engine running. Never touch unrelated processes.
    $r.stopped_during_cleanup=@()
    if($child -and -not $child.HasExited){$child.Kill();[void]$child.WaitForExit(5000);$r.stopped_during_cleanup+=$child.Id}
    if($wizard -and -not $wizard.HasExited){try{[void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero);[void]$wizard.WaitForExit(2000)}catch{};if(-not $wizard.HasExited){$wizard.Kill();[void]$wizard.WaitForExit(5000);$r.stopped_during_cleanup+=$wizard.Id}}
    $r.child_exited=($child -and $child.HasExited);if($child -and $child.HasExited){$child.WaitForExit();$r.child_exit=$child.ExitCode}
    $r.wizard_exited=($wizard -and $wizard.HasExited)
    if($r.Contains('engine_log') -and [IO.File]::Exists($r.engine_log)){[IO.File]::WriteAllBytes((Join-Path $OutDir ($Name+'-engine.log')),(ReadShared $r.engine_log))}
    elseif([IO.File]::Exists((Join-Path $install 'install.log')) -and $r.status -eq 'FINISH'){[IO.File]::WriteAllBytes((Join-Path $OutDir ($Name+'-engine.log')),(ReadShared (Join-Path $install 'install.log')))}
    $journal=Join-Path $txn 'journal.txt'
    if([IO.File]::Exists($journal)){[IO.File]::WriteAllBytes((Join-Path $OutDir ($Name+'-journal.txt')),(ReadShared $journal))}
    $r.pending_exists=[IO.File]::Exists((Join-Path $install 'payload.pending.sha256'));$r.transaction_exists=[IO.Directory]::Exists($txn)
    $r.payload_files_present=@($manifest|Where-Object {[IO.File]::Exists((Join-Path $install $_))}).Count
    $r.capture_warnings=@($script:captureWarnings)
    $r.ended=[DateTime]::Now.ToString('o');Save
}
Write-Host "$Name : $($r.status), engine=$($r.child_exit), files=$($r.payload_files_present), pending=$($r.pending_exists)"
