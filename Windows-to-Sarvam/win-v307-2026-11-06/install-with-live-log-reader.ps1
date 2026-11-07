param([ValidateSet('clean','upgrade','interrupt','recovery')][string]$Phase)
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
$Root=Split-Path -Parent (Split-Path -Parent $OutDir)
. (Join-Path $OutDir 'ui-helper.ps1')
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Run unelevated'}
$setup=Join-Path $Root 'Sutram-Setup.exe';$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
if((Get-FileHash $setup).Hash -ne 'CBBFD0A66C0A9728C3FD88096631462430C0185CD8C6738964D5B885253E7481'){throw 'Unexpected setup'}
if($Phase -in @('clean','interrupt') -and (Test-Path -LiteralPath $install)){throw 'Expected absent target'}
if($Phase -eq 'recovery' -and -not(Test-Path -LiteralPath (Join-Path $install 'payload.pending.sha256'))){throw 'No interrupted-install record'}
$r=[ordered]@{phase=$Phase;setup=$setup;sha256=(Get-FileHash $setup).Hash;started=[DateTime]::Now.ToString('o');elevated=$false;observations=@()}
$childProcess=$null
function Save{[IO.File]::WriteAllText((Join-Path $OutDir ($Phase+'.json')),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))}
function Click([int]$Id){
    $h=Wait-Until {$h=[SutramIde]::GetDlgItem($main,$Id);if($h -ne [IntPtr]::Zero -and [SutramIde]::IsWindowVisible($h)){$h}} 5000
    if(-not $h){throw "Control $Id not visible"}
    [void][SutramIde]::Send($h,0xF5,0,0,3000);Start-Sleep -Milliseconds 150
}
function Read-SharedLog([string]$Path){
    $f=[IO.File]::Open($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
    try{$ms=[IO.MemoryStream]::new();try{$f.CopyTo($ms);return ,$ms.ToArray()}finally{$ms.Dispose()}}finally{$f.Dispose()}
}
function Preserve-Log{
    try{
        $path=if($r.Contains('engine_log') -and (Test-Path -LiteralPath $r.engine_log)){$r.engine_log}else{Join-Path $install 'install.log'}
        if(Test-Path -LiteralPath $path){[IO.File]::WriteAllBytes((Join-Path $OutDir ($Phase+'-engine.log')),(Read-SharedLog $path))}
    }catch{$r.log_snapshot_error=$_.Exception.Message}
}
try{
    $ip=Start-Process -FilePath $setup -WorkingDirectory $Root -WindowStyle Normal -PassThru
    $r.pid=$ip.Id;$r.process_started=$ip.StartTime.ToString('o');[void]$ip.Handle;Save
    $main=Wait-Until {[SutramIde]::WindowsOf([uint32]$ip.Id,'SutramWizardWindow')|Select-Object -First 1} 10000
    if(-not $main){throw 'Wizard did not open'}
    Click 2002;Click 2010;Click 2002
    $r.destination=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2020))
    if($r.destination -ne $install){throw 'Unexpected destination'}
    Click 2002
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2030),0xF1,1,0,3000)
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2031),0xF1,1,0,3000)
    Click 2002;$r.ready=Shot $main ($Phase+'-ready');Click 2002
    $watch=[Diagnostics.Stopwatch]::StartNew();$lastRecord=-10;$lastText='';$lastChange=0
    while($watch.Elapsed.TotalSeconds -lt 935){
        Start-Sleep -Milliseconds $(if($Phase -eq 'interrupt'){20}else{300})
        if(-not $childProcess){
            $p=Get-CimInstance Win32_Process -Filter "ParentProcessId = $($ip.Id)"|Where-Object {$_.Name -eq 'powershell.exe'}|Select-Object -First 1
            if($p){$childProcess=Get-Process -Id $p.ProcessId;[void]$childProcess.Handle;$r.child=@{pid=$p.ProcessId;parent=$p.ParentProcessId;command=$p.CommandLine;started=$childProcess.StartTime.ToString('o')};$m=[regex]::Match($p.CommandLine,'-LogPath\s+"([^"]+)"');if($m.Success){$r.engine_log=$m.Groups[1].Value};Save}
        }
        $tail=''
        if($r.Contains('engine_log') -and (Test-Path -LiteralPath $r.engine_log)){
            try{$lines=[Text.Encoding]::UTF8.GetString((Read-SharedLog $r.engine_log)).TrimEnd([char[]]"`r`n").Split([char]10);$tail=$lines[-1].TrimEnd([char]13)}catch{$tail=$lastText;$r.transient_log_read_error=$_.Exception.Message}
        }
        if($tail -ne $lastText){$lastText=$tail;$lastChange=$watch.Elapsed.TotalSeconds}
        if($Phase -eq 'interrupt' -and $childProcess -and $tail -match 'Copying (\d+)/(\d+):' -and [int]$Matches[1] -ge 4 -and [int]$Matches[1] -lt [int]$Matches[2]){
            $r.interrupt_trigger=$tail;$r.interrupt_seconds=$watch.Elapsed.TotalSeconds
            # Handles belong to this test's captured processes, never a name-wide kill.
            if(-not $ip.HasExited){$ip.Kill();$ip.WaitForExit()}
            if(-not $childProcess.HasExited){$childProcess.Kill();$childProcess.WaitForExit()}
            $r.status='INTERRUPTED_AS_REQUESTED';break
        }
        if($Phase -eq 'interrupt' -and $watch.Elapsed.TotalSeconds-$lastRecord -lt 1){continue}
        $dialogs=@([SutramIde]::WindowsOf([uint32]$ip.Id,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)})
        $label='';try{$label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002))}catch{$label='UI timeout'}
        if($watch.Elapsed.TotalSeconds-$lastRecord -ge 5){
            $r.observations+=@{seconds=[math]::Round($watch.Elapsed.TotalSeconds,2);next_label=$label;dialogs=$dialogs.Count;last_line=$tail;child_exited=($childProcess -and $childProcess.HasExited)};$lastRecord=$watch.Elapsed.TotalSeconds;Save
        }
        if($dialogs.Count){$r.dialog_text=[SutramIde]::ChildTexts($dialogs[0]);$r.error_screenshot=Shot $dialogs[0] ($Phase+'-error');$r.status='ERROR_DIALOG';Preserve-Log;[void][SutramIde]::Send([SutramIde]::GetDlgItem($dialogs[0],1),0xF5,0,0,3000);break}
        if($label -eq 'Finish'){
            $r.status='FINISH';$r.finish_seconds=[math]::Round($watch.Elapsed.TotalSeconds,2);$r.finish_screenshot=Shot $main ($Phase+'-finish')
            $r.wizard_self_closed_before_finish_click=$false
            [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2060),0xF1,0,0,3000)
            Click 2002;$r.closed_after_finish_click=$ip.WaitForExit(5000);break
        }
        if($ip.HasExited){$r.status='EXIT_WITHOUT_FINISH';break}
        if($watch.Elapsed.TotalSeconds-$lastChange -ge 30 -and -not $r.Contains('stall')){
            $r.stall=@{at=[DateTime]::Now.ToString('o');seconds=$watch.Elapsed.TotalSeconds;last_line=$tail}
            $r.stall_threads=@(foreach($proc in @($ip,$childProcess)){if($proc -and -not $proc.HasExited){$proc.Refresh();foreach($thread in $proc.Threads){@{pid=$proc.Id;id=$thread.Id;state=$thread.ThreadState.ToString();wait_reason=$(if($thread.ThreadState -eq 'Wait'){$thread.WaitReason.ToString()}else{''})}}}});Preserve-Log;Save
        }
    }
    if(-not $r.Contains('status')){$r.status='NO_RESULT_AFTER_935_SECONDS'}
    $r.observed_seconds=[math]::Round($watch.Elapsed.TotalSeconds,2);Preserve-Log
    if($childProcess){$r.child_exited=$childProcess.HasExited;if($childProcess.HasExited){$childProcess.WaitForExit();$r.child_exit=$childProcess.ExitCode}}
    if(-not $ip.HasExited){[void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero);$r.closed_after_observation=$ip.WaitForExit(3000)}
    $r.wizard_exited=$ip.HasExited
    $r.pending_exists=Test-Path -LiteralPath (Join-Path $install 'payload.pending.sha256')
    $r.files=@(Get-ChildItem -LiteralPath $install -Recurse -File -ErrorAction SilentlyContinue|ForEach-Object {@{relative=$_.FullName.Substring($install.Length+1);bytes=$_.Length;created=$_.CreationTime.ToString('o')}})
    $r.ended=[DateTime]::Now.ToString('o');Save
    try{$events=@(Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Windows Defender/Operational';StartTime=[DateTime]$r.started} -ErrorAction Stop|Select-Object TimeCreated,Id,LevelDisplayName,Message);$events|ConvertTo-Json -Depth 5|Set-Content (Join-Path $OutDir ($Phase+'-defender.json')) -Encoding UTF8}catch{@{query_error=$_.Exception.Message}|ConvertTo-Json|Set-Content (Join-Path $OutDir ($Phase+'-defender.json')) -Encoding UTF8}
    Write-Host "$Phase result: $($r.status); child exit: $($r.child_exit); wizard exited: $($r.wizard_exited); pending: $($r.pending_exists)"
}catch{$r.error=$_.Exception.Message;Preserve-Log;Save;throw}
