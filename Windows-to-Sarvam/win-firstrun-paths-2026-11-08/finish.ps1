$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'desktop-helper.ps1')
$r=@{time=[DateTime]::Now.ToString('o');explorer_closed=@();notepad_close_requested=$false}
$sh=New-Object -ComObject Shell.Application
foreach($w in @($sh.Windows())){try{$path=$w.Document.Folder.Self.Path;if($path.StartsWith((Join-Path $OutDir 'cases\'),[StringComparison]::OrdinalIgnoreCase)){$h=[IntPtr]$w.HWND;[void][SutramIde]::PostMessageW($h,0x10,[IntPtr]::Zero,[IntPtr]::Zero);$r.explorer_closed+=@{handle=$h.ToInt64();path=$path}}}catch{}}
$d=Get-Content -LiteralPath (Join-Path $OutDir 'desktop-click.json') -Raw -Encoding UTF8|ConvertFrom-Json
$n=[AcceptanceWindow]::All()|Where-Object {$_.handle -eq $d.launched.handle -and $_.pid -eq $d.launched.pid -and $_.cls -eq 'Notepad'}|Select-Object -First 1
if($n){[void][SutramIde]::PostMessageW([IntPtr]$n.handle,0x10,[IntPtr]::Zero,[IntPtr]::Zero);$r.notepad_close_requested=$true}
Start-Sleep -Seconds 1
$r.notepad_window_still_present=@([AcceptanceWindow]::All()|Where-Object {$_.handle -eq $d.launched.handle -and $_.pid -eq $d.launched.pid}).Count -gt 0
$r.installed_app_processes=@(Get-CimInstance Win32_Process|Where-Object {$_.ExecutablePath -and $_.ExecutablePath.StartsWith((Join-Path $env:LOCALAPPDATA 'Programs\Sutram\'),[StringComparison]::OrdinalIgnoreCase)}|Select-Object ProcessId,Name,ExecutablePath)
$r.standard_user=-not ([Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$r.os=Get-CimInstance Win32_OperatingSystem|Select-Object Caption,Version,BuildNumber
[IO.File]::WriteAllText((Join-Path $OutDir 'finish.json'),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
Write-Host "Test Explorer windows closed: $($r.explorer_closed.Count); test Notepad remains: $($r.notepad_window_still_present); installed processes: $($r.installed_app_processes.Count)"
if($r.installed_app_processes.Count){throw 'Installed app still open'}
