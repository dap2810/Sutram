$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot;. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
$n=Get-Content (Join-Path $OutDir 'notepad-opened.json') -Raw|ConvertFrom-Json
$wins=@([AcceptanceWindow]::All()|Where-Object {$_.cls -eq 'Notepad'});$wins|ConvertTo-Json
$e=Find-UI (UI ([IntPtr]$n.window.handle)) 'Text editor'
$t=[SutramIde]::Text([IntPtr]$e.Current.NativeWindowHandle)
$r=@{text=$t;length=$t.Length;codes=@($t.ToCharArray()|ForEach-Object {[int]$_});screenshot=(Shot ([IntPtr]$n.window.handle) 'notepad-type-observation')}
[IO.File]::WriteAllText((Join-Path $OutDir 'notepad-type-observation.json'),($r|ConvertTo-Json -Depth 4),[Text.UTF8Encoding]::new($false));$r|ConvertTo-Json -Depth 4
