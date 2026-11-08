param([ValidateSet('launch','exercise')][string]$Phase='launch')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
$rec=Join-Path $OutDir 'terminal.json'
function Save{[IO.File]::WriteAllText($rec,($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))}
if($Phase -eq 'launch'){
 $before=@([AcceptanceWindow]::All());$link=Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram\Sutram Terminal.lnk'
 $env:Path=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
 $r=[ordered]@{time=[DateTime]::Now.ToString('o');shortcut=$link;parent_path=$env:Path;baseline_handles=@($before|ForEach-Object {$_.handle})}
 Start-Process -FilePath $link -WindowStyle Normal
 Start-Sleep -Seconds 3
 $r.commands=@(Get-CimInstance Win32_Process -Filter "Name = 'cmd.exe'"|Where-Object {$_.CommandLine -like '*Sutram*--version*'}|Select-Object ProcessId,ParentProcessId,CommandLine)
 $r.new_windows=@([AcceptanceWindow]::All()|Where-Object {$_.handle -notin $r.baseline_handles});Save;$r.new_windows|ConvertTo-Json -Depth 5
 exit
}
$r=Get-Content -LiteralPath $rec -Encoding UTF8 -Raw|ConvertFrom-Json
$w=@($r.new_windows|Where-Object {$_.cls -in @('ConsoleWindowClass','CASCADIA_HOSTING_WINDOW_CLASS')})
if($w.Count -ne 1){throw 'Cannot uniquely select launched terminal'}
$h=[IntPtr]$w[0].handle;Foreground $h
$r|Add-Member -NotePropertyName startup_screenshot -NotePropertyValue (Shot $h 'terminal-startup')
[Windows.Forms.SendKeys]::SendWait('sutram --version{ENTER}');Start-Sleep -Seconds 1
$r|Add-Member -NotePropertyName version_screenshot -NotePropertyValue (Shot $h 'terminal-version')
$rows=UI-Dump (UI $h) 'terminal-ui';$r|Add-Member -NotePropertyName ui_names -NotePropertyValue @($rows|ForEach-Object {$_.name})
$commands=@(
 ('sutram --version > "'+(Join-Path $OutDir 'terminal-version.txt')+'" 2> "'+(Join-Path $OutDir 'terminal-stderr.txt')+'"')
 ('where sutram > "'+(Join-Path $OutDir 'terminal-where.txt')+'"')
 ('echo %PATH% > "'+(Join-Path $OutDir 'terminal-path.txt')+'"')
)
foreach($cmd in $commands){Foreground $h;foreach($ch in $cmd.ToCharArray()){if('+^%~(){}[]'.Contains([string]$ch)){[Windows.Forms.SendKeys]::SendWait('{'+$ch+'}')}else{[Windows.Forms.SendKeys]::SendWait([string]$ch)}};[Windows.Forms.SendKeys]::SendWait('{ENTER}');Start-Sleep -Milliseconds 400}
$r|Add-Member -NotePropertyName captured_commands -NotePropertyValue $commands;Save
Foreground $h;[Windows.Forms.SendKeys]::SendWait('exit{ENTER}');Start-Sleep -Milliseconds 800
Write-Host 'Terminal command exercised and captured; requested terminal exit.'
