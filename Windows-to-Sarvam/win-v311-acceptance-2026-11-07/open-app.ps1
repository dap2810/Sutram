param([ValidateSet('notepad','settings')][string]$App)
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot;. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
$before=@([AcceptanceWindow]::All()|Where-Object {$_.cls -eq 'Notepad' -or $_.title -eq 'Settings'})
if($App -eq 'notepad'){Start-Process -FilePath notepad.exe -WindowStyle Normal}
else{Start-Process 'ms-settings:appsfeatures' -WindowStyle Normal}
Start-Sleep -Seconds 3
$wins=@([AcceptanceWindow]::All()|Where-Object {if($App -eq 'notepad'){$_.cls -eq 'Notepad'}else{$_.title -eq 'Settings' -and $_.cls -eq 'ApplicationFrameWindow'}})
$new=@($wins|Where-Object {$_.handle -notin @($before|ForEach-Object {$_.handle})})
if($new.Count -eq 1){$w=$new[0]}elseif($wins.Count -eq 1){$w=$wins[0]}else{throw 'App window not uniquely identified'}
$h=[IntPtr]$w.handle;[void][AcceptanceWindow]::SetWindowPos($h,[IntPtr]::Zero,20,30,950,680,0x0040)
$record=@{app=$App;before=$before;window=$w;new_window=($new.Count -eq 1);process_started=(Get-Process -Id $w.pid).StartTime.ToString('o');screenshot=(Shot $h ($App+'-opened'))}
[IO.File]::WriteAllText((Join-Path $OutDir ($App+'-opened.json')),($record|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
$rows=UI-Dump (UI $h) ($App+'-initial-ui');$rows|Select-Object name,id,class,type,handle|Format-Table -AutoSize
