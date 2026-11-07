$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
$Root=Split-Path -Parent (Split-Path -Parent $OutDir)
. (Join-Path $OutDir 'ui-helper.ps1')
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Run under the normal user token'}
$backup=Get-Content -LiteralPath (Join-Path $OutDir 'preserve.json') -Raw|ConvertFrom-Json
if(-not $backup.verified){throw 'Verified backup required'}
$setup=Join-Path $Root 'Sutram-Setup.exe';$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
$r=[ordered]@{started=[DateTime]::Now.ToString('o');setup=$setup;sha256=(Get-FileHash $setup).Hash;file_count_before=$backup.file_count;observations=@();elevated=$false;stalled_observed=$false}
$childProcess=$null;$watch=$null;$lastChange=0;$lastLog='';$ip=$null
function Save{[IO.File]::WriteAllText((Join-Path $OutDir 'upgrade.json'),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))}
function Click([int]$Id){[void][SutramIde]::Send([SutramIde]::GetDlgItem($main,$Id),0xF5,0,0,3000);Start-Sleep -Milliseconds 250}
function Capture-Stall {
    $r.stalled_observed=$true;$r.stall_seconds=[math]::Round($watch.Elapsed.TotalSeconds,2)
    $at=Get-Date
    $files=@(Get-ChildItem -LiteralPath $install -Recurse -Force -File|Select-Object FullName,Length,@{n='LastWriteTime';e={$_.LastWriteTime.ToString('o')}},@{n='CreationTime';e={$_.CreationTime.ToString('o')}})
    $capture=[ordered]@{observed=$at.ToString('o');file_count=$files.Count;files=$files;written_last_two_minutes=@($files|Where-Object {[DateTime]::Parse($_.LastWriteTime) -gt $at.AddMinutes(-2)});processes=@(Get-Process|Where-Object {$_.ProcessName -match 'powershell|sutram'}|Select-Object Id,ProcessName,CPU,StartTime);owned_threads=@()}
    foreach($processId in @($ip.Id,$r.child.ProcessId)){
        $p=Get-Process -Id $processId -ErrorAction SilentlyContinue
        if($p){$capture.owned_threads+=@{pid=$processId;cpu=$p.CPU;threads=@($p.Threads|ForEach-Object {@{id=$_.Id;state=$_.ThreadState.ToString();wait=if($_.ThreadState -eq 'Wait'){$_.WaitReason.ToString()}else{''}}})}}
    }
    $capture|ConvertTo-Json -Depth 7|Set-Content (Join-Path $OutDir 'stall.json') -Encoding UTF8
    Copy-Item -LiteralPath $r.engine_log -Destination (Join-Path $OutDir 'engine-at-stall.log')
    if(Test-Path -LiteralPath (Join-Path $install 'install.log')){Copy-Item -LiteralPath (Join-Path $install 'install.log') -Destination (Join-Path $OutDir 'installed-log-at-stall.log')}
    $open=Start-Process -FilePath "$env:SystemRoot\System32\openfiles.exe" -ArgumentList '/query /fo table' -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $OutDir 'openfiles.stdout.txt') -RedirectStandardError (Join-Path $OutDir 'openfiles.stderr.txt')
    if(-not $open.WaitForExit(5000)){$open.Kill();[void]$open.WaitForExit(2000);$r.openfiles_timeout=$true}else{$r.openfiles_exit=$open.ExitCode}
    foreach($mode in @('Print','Screen')){
        $args='-NoProfile -NonInteractive -File "'+(Join-Path $OutDir 'capture.ps1')+'" -TargetProcess '+$ip.Id+' -Mode '+$mode
        $captureProcess=Start-Process -FilePath "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" -ArgumentList $args -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $OutDir ('capture-'+$mode+'.stdout.txt')) -RedirectStandardError (Join-Path $OutDir ('capture-'+$mode+'.stderr.txt'))
        if(-not $captureProcess.WaitForExit(5000)){$captureProcess.Kill();[void]$captureProcess.WaitForExit(2000)}
        if(Test-Path -LiteralPath (Join-Path $OutDir 'upgrade-stalled.png')){break}
    }
    Write-Host "No engine-log progress for 30 seconds. Captured stall evidence; leaving installer untouched for its 15-minute deadline."
    Save
}
try{
    $ip=Start-Process -FilePath $setup -WorkingDirectory $Root -WindowStyle Normal -PassThru
    $r.pid=$ip.Id;Save
    $main=Wait-Until {[SutramIde]::WindowsOf([uint32]$ip.Id,'SutramWizardWindow')|Select-Object -First 1} 10000
    if(-not $main){throw 'Wizard did not open'}
    Click 2002;Click 2010;Click 2002
    $r.destination=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2020))
    if($r.destination -ne $install){throw 'Destination differs from canonical installation'}
    Click 2002
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2030),0xF1,1,0,3000)
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2031),0xF1,1,0,3000)
    Click 2002;$r.ready_screenshot=Shot $main 'upgrade-ready'
    Click 2002;$watch=[Diagnostics.Stopwatch]::StartNew()
    while($watch.Elapsed.TotalSeconds -lt 935){
        Start-Sleep -Milliseconds 500
        $children=@(Get-CimInstance Win32_Process -Filter "ParentProcessId = $($ip.Id)"|Where-Object {$_.Name -eq 'powershell.exe'}|Select-Object ProcessId,ParentProcessId,CommandLine)
        if($children.Count -and -not $childProcess){
            $r.child=$children[0];$childProcess=Get-Process -Id $r.child.ProcessId
            $null=$childProcess.Handle
            $r.child_started=$childProcess.StartTime.ToString('o')
            $match=[regex]::Match($r.child.CommandLine,'-LogPath\s+"([^"]+)"');if($match.Success){$r.engine_log=$match.Groups[1].Value}
        }
        $line=''
        if($r.Contains('engine_log') -and (Test-Path -LiteralPath $r.engine_log)){$line=[string](Get-Content -LiteralPath $r.engine_log -Tail 1)}
        if($line -ne $lastLog){$lastLog=$line;$lastChange=$watch.Elapsed.TotalSeconds}
        $dialogs=@([SutramIde]::WindowsOf([uint32]$ip.Id,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)})
        $label='';try{$label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002))}catch{$label='UI timeout'}
        $visible=@();foreach($child in $children){$visible+=@([SutramIde]::WindowsOf([uint32]$child.ProcessId,$null)|Where-Object {[SutramIde]::IsWindowVisible($_)}|ForEach-Object {$_.ToInt64()})}
        $r.observations+=@{at=[DateTime]::Now.ToString('o');seconds=[math]::Round($watch.Elapsed.TotalSeconds,2);children=$children.Count;next_label=$label;dialogs=$dialogs.Count;last_log=$line;visible_child_windows=$visible};Save
        if($dialogs.Count){$r.status='ERROR_DIALOG';$r.dialog_text=[SutramIde]::ChildTexts($dialogs[0]);$r.dialog_seconds=[math]::Round($watch.Elapsed.TotalSeconds,2);$r.error_screenshot=Shot $dialogs[0] 'upgrade-error';[void][SutramIde]::Send([SutramIde]::GetDlgItem($dialogs[0],1),0xF5,0,0,3000);break}
        if($label -eq 'Finish'){$r.status='FINISH';$r.finish_seconds=[math]::Round($watch.Elapsed.TotalSeconds,2);$r.finish_screenshot=Shot $main 'upgrade-finish';break}
        if($ip.HasExited){$r.status='WIZARD_EXITED_WITHOUT_OBSERVED_RESULT';break}
        if(-not $r.stalled_observed -and $children.Count -and $watch.Elapsed.TotalSeconds-$lastChange -ge 30){Capture-Stall}
    }
    if(-not $r.Contains('status')){$r.status='NO_RESULT_AFTER_935_SECONDS'}
    $r.observed_seconds=[math]::Round($watch.Elapsed.TotalSeconds,2)
    if($childProcess){$r.child_exited=$childProcess.HasExited;if($childProcess.HasExited){$childProcess.WaitForExit();$r.child_exit=$childProcess.ExitCode}}
    if($r.Contains('engine_log') -and (Test-Path -LiteralPath $r.engine_log)){Copy-Item -LiteralPath $r.engine_log -Destination (Join-Path $OutDir 'engine.log')}
    elseif($r.status -eq 'FINISH'){Copy-Item -LiteralPath (Join-Path $install 'install.log') -Destination (Join-Path $OutDir 'engine.log')}
    if(-not $ip.HasExited){[void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero);$r.wizard_closed=$ip.WaitForExit(3000)}else{$r.wizard_closed=$true}
    $r.file_count_after=@(Get-ChildItem -LiteralPath $install -Recurse -Force -File).Count
    Write-Host "Upgrade result: $($r.status); seconds: $($r.observed_seconds); child exited: $($r.child_exited); files: $($r.file_count_after)"
}catch{$r.error=$_.Exception.Message;throw}
finally{
    $r.ended=[DateTime]::Now.ToString('o')
    try{$events=@(Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Windows Defender/Operational';StartTime=[DateTime]::Parse($r.started);EndTime=[DateTime]::Now} -ErrorAction Stop|Select-Object TimeCreated,Id,LevelDisplayName,Message);@{start=$r.started;end=$r.ended;events=$events}|ConvertTo-Json -Depth 5|Set-Content (Join-Path $OutDir 'defender-events.json') -Encoding UTF8}catch{@{start=$r.started;end=$r.ended;error=$_.Exception.Message}|ConvertTo-Json|Set-Content (Join-Path $OutDir 'defender-events.json') -Encoding UTF8}
    Save
}
