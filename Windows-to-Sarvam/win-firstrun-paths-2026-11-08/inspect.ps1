$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'desktop-helper.ps1')
$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram';$shell=New-Object -ComObject WScript.Shell
$paths=@([Environment]::GetFolderPath('DesktopDirectory'),[Environment]::GetFolderPath('CommonDesktopDirectory'),(Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram'))
$links=@();foreach($dir in $paths){foreach($f in (Get-ChildItem -LiteralPath $dir -Filter '*Sutram*.lnk' -ErrorAction SilentlyContinue)){$s=$shell.CreateShortcut($f.FullName);$links+=@{path=$f.FullName;sha256=(Get-FileHash -LiteralPath $f.FullName).Hash;target=$s.TargetPath;arguments=$s.Arguments;cwd=$s.WorkingDirectory}}}
[IO.File]::WriteAllText((Join-Path $OutDir 'shortcuts.json'),($links|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
$links|ConvertTo-Json -Depth 5
[AcceptanceWindow]::All()|Where-Object {$_.cls -in @('SutramNativeGUIWindow','CASCADIA_HOSTING_WINDOW_CLASS','ConsoleWindowClass','CabinetWClass','Progman','WorkerW')}|ConvertTo-Json
