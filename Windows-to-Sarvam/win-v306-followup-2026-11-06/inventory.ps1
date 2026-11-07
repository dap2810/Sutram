$ErrorActionPreference='Stop'
$names=@('procdump.exe','procdump64.exe','windbg.exe','windbgx.exe','cdb.exe','handle.exe','handle64.exe','openfiles.exe')
$r=[ordered]@{recorded=[DateTime]::Now.ToString('o');commands=@();known_locations=@();store_packages=@()}
foreach($name in $names) { $r.commands+=@{name=$name;found=@(Get-Command $name -ErrorAction SilentlyContinue|Select-Object Name,Source)} }
foreach($pattern in @('C:\Program Files (x86)\Windows Kits\10\Debuggers\*\cdb.exe','C:\Program Files (x86)\Windows Kits\10\Debuggers\*\windbg.exe','C:\Tools\*procdump*.exe','C:\Sysinternals\*procdump*.exe','C:\Program Files\SysinternalsSuite\*procdump*.exe',"$env:LOCALAPPDATA\Microsoft\WindowsApps\*windbg*","$env:USERPROFILE\Downloads\*procdump*.exe")) {
    $r.known_locations+=@{pattern=$pattern;found=@(Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue|Select-Object -ExpandProperty FullName)}
}
try { $r.store_packages=@(Get-AppxPackage -Name Microsoft.WinDbg -ErrorAction Stop|Select-Object Name,Version,InstallLocation) } catch { $r.store_query_error=$_.Exception.Message }
$r|ConvertTo-Json -Depth 6|Set-Content (Join-Path $PSScriptRoot 'debugger-inventory.json') -Encoding UTF8
$r|ConvertTo-Json -Depth 6
