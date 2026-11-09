$ErrorActionPreference='Stop'
$out=$PSScriptRoot
. (Join-Path $out 'desktop-helper.ps1')
$owned=@(
    @{label='first wizard';pid=40664;started='2026-11-07T14:58:14.4269417-05:00'},
    @{label='first engine';pid=34508;started='2026-11-07T14:58:16.6603516-05:00'},
    @{label='first default IDE';pid=20876;started='2026-11-07T14:58:45.0686626-05:00'},
    @{label='Notepad';pid=22312;started='2026-11-07T14:59:29.1581768-05:00'},
    @{label='first cmd observer attempt';pid=41060;started='2026-11-07T15:04:30.7382479-05:00'},
    @{label='conhost observer attempt';pid=23144;started='2026-11-07T15:05:13.5916338-05:00'},
    @{label='visible Command Prompt';pid=44312;started='2026-11-07T15:06:20.1313018-05:00'},
    @{label='reinstall wizard';pid=2152;started='2026-11-07T15:12:28.1723813-05:00'},
    @{label='reinstall engine';pid=37436;started='2026-11-07T15:12:30.3939115-05:00'},
    @{label='reinstall default IDE';pid=30708;started='2026-11-07T15:13:14.8255292-05:00'},
    @{label='B1-B4 shortcut IDE';pid=42488;started='2026-11-07T15:13:21.9374651-05:00'}
)
$rows=@()
foreach($item in $owned){
    $p=Get-Process -Id $item.pid -ErrorAction SilentlyContinue
    $same=$false;$currentStart=$null
    if($p){$currentStart=$p.StartTime.ToString('o');$same=[Math]::Abs(($p.StartTime-([DateTimeOffset]::Parse($item.started)).LocalDateTime).TotalSeconds) -lt 2}
    $rows+=@{label=$item.label;pid=$item.pid;recorded_start=$item.started;pid_exists=($null -ne $p);current_start=$currentStart;same_process_still_running=$same}
}
$children=@(Get-CimInstance Win32_Process -Filter 'ParentProcessId = 23144' | Select-Object ProcessId,ParentProcessId,CreationDate,Name,CommandLine)
$windows=@([AcceptanceWindow]::All() | Where-Object {$_.title -eq 'Sutram v311 acceptance - first program' -or $_.title -eq 'Sutram Setup' -or $_.title -like '* - Sutram sampadak'})
$r=@{time=[DateTime]::Now.ToString('o');owned=$rows;attempt2_remaining_children=$children;test_windows=$windows;pass=(@($rows|Where-Object {$_.same_process_still_running}).Count -eq 0 -and $children.Count -eq 0 -and $windows.Count -eq 0);note='Read-only final check; no process was stopped. Existing user Settings was not closed.'}
$log=Get-Item -LiteralPath '%USERPROFILE%\AppData\Local\Temp\STMFB5F.tmp\uninstall.log'
$logRecord=@{source=$log.FullName;last_write=$log.LastWriteTime.ToString('o');sha256=(Get-FileHash -LiteralPath $log.FullName).Hash;copied_file='uninstall-engine.log';copy_sha256=(Get-FileHash -LiteralPath (Join-Path $out 'uninstall-engine.log')).Hash;note='Only matching fresh uninstall log found after the first install; owner performed Settings uninstall before observer started.'}
$utf8=[Text.UTF8Encoding]::new($false)
[IO.File]::WriteAllText((Join-Path $out 'uninstall-log-source.json'),($logRecord|ConvertTo-Json -Depth 6),$utf8)
[IO.File]::WriteAllText((Join-Path $out 'final-process-check.json'),($r|ConvertTo-Json -Depth 8),$utf8)
$r|ConvertTo-Json -Depth 8
if(-not $r.pass){exit 1}
