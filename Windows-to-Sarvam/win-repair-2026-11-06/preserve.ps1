$ErrorActionPreference='Stop'
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Run unelevated' }
if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'backup.json')) { throw 'Backup record already exists; do not repeat automatically' }
& (Join-Path $PSScriptRoot 'snapshot.ps1') before
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$source=[IO.Path]::GetFullPath((Join-Path $parent 'Sutram'))
$backup=[IO.Path]::GetFullPath((Join-Path $parent ('Sutram-recovery-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss'))))
if ([IO.Path]::GetDirectoryName($source) -ne $parent -or [IO.Path]::GetDirectoryName($backup) -ne $parent -or [IO.Path]::GetFileName($source) -ne 'Sutram') { throw 'Unsafe move scope' }
if (-not (Test-Path -LiteralPath (Join-Path $source '.sutram-install')) -or (Test-Path -LiteralPath $backup)) { throw 'Unexpected source or backup destination' }
$walk=$source
while ($walk) {
    if ((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Refusing reparse path' }
    $next=[IO.Path]::GetDirectoryName($walk); if ($next -eq $walk) { break }; $walk=$next
}
if (Get-ChildItem -LiteralPath $source -Recurse -Force | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint } | Select-Object -First 1) { throw 'Refusing reparse content' }
$active=@(Get-CimInstance Win32_Process | Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($source+'\',[StringComparison]::OrdinalIgnoreCase) })
if ($active.Count) { throw 'An installed Sutram process is open; preserve its work before moving' }
$links=@()
$shell=New-Object -ComObject WScript.Shell
$shortcutPaths=@((Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'Sutram IDE.lnk'))
$menu=Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram'
if (Test-Path -LiteralPath $menu) { $shortcutPaths+=@(Get-ChildItem -LiteralPath $menu -Filter '*.lnk' | ForEach-Object {$_.FullName}) }
foreach($p in $shortcutPaths) { if(Test-Path -LiteralPath $p) { $sc=$shell.CreateShortcut($p); $links+=@{path=$p;sha256=(Get-FileHash -LiteralPath $p).Hash;target=$sc.TargetPath;arguments=$sc.Arguments;working_directory=$sc.WorkingDirectory} } }
$r=[ordered]@{source=$source;backup=$backup;time=[DateTime]::Now.ToString('o');shortcuts_before=$links;operation='Move-Item of validated canonical directory to a new sibling; no deletion'}
Move-Item -LiteralPath $source -Destination $backup -ErrorAction Stop
$before=Get-Content (Join-Path $PSScriptRoot 'before.json') -Raw|ConvertFrom-Json
$r.verified_files=0
foreach($f in $before.tree) {
    $p=Join-Path $backup $f.path
    if (-not(Test-Path -LiteralPath $p) -or (Get-FileHash -LiteralPath $p).Hash -ne $f.sha256) { throw "Backup verification failed: $($f.path)" }
    $r.verified_files++
}
$r.status='PRESERVED'
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'backup.json'),($r|ConvertTo-Json -Depth 6),[Text.UTF8Encoding]::new($false))
$r|ConvertTo-Json -Depth 6
