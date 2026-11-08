param([ValidateSet('prepare','restore')][string]$Phase='prepare')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)){throw 'Must run non-elevated'}
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$install=Join-Path $parent 'Sutram';$backup=Join-Path $parent 'Sutram-before-firstrun-20261108'
$menu=Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram'
$desktop=Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'Sutram IDE.lnk'
$record=Join-Path $OutDir 'preserve.json';$saved=Join-Path $OutDir 'preserved';$stamp='FirstRun20261108'
function Save($o,$name){[IO.File]::WriteAllText((Join-Path $OutDir $name),($o|ConvertTo-Json -Depth 12),[Text.UTF8Encoding]::new($false))}
function Guard($p,$base){
 $p=[IO.Path]::GetFullPath($p);$base=[IO.Path]::GetFullPath($base).TrimEnd('\')
 if(-not $p.StartsWith($base+'\',[StringComparison]::OrdinalIgnoreCase)){throw 'Move target outside intended root'}
 $w=$p;while($w){if((Test-Path -LiteralPath $w) -and ((Get-Item -LiteralPath $w -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Reparse path'};$w=[IO.Path]::GetDirectoryName($w)}
 if((Test-Path -LiteralPath $p) -and (Get-ChildItem -LiteralPath $p -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1)){throw 'Reparse contents'}
}
function Inventory($p){@(Get-ChildItem -LiteralPath $p -Recurse -File -Force|ForEach-Object {@{relative=$_.FullName.Substring($p.Length+1);bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash}})}
function Verify($p,$rows){foreach($f in $rows){if((Get-FileHash -LiteralPath (Join-Path $p $f.relative)).Hash -ne $f.sha256){throw 'Preserved file hash mismatch'}};if(@(Get-ChildItem -LiteralPath $p -Recurse -Force -File).Count -ne $rows.Count){throw 'File count mismatch'}}
Guard $install $parent;Guard $backup $parent;Guard $menu ([Environment]::GetFolderPath('StartMenu'));Guard $desktop ([Environment]::GetFolderPath('DesktopDirectory'));Guard $saved $OutDir
if(Test-Path -LiteralPath ($install+'.sutram-lock')){throw 'Install lock exists'}
if(Test-Path -LiteralPath ($install+'.sutram-transaction')){throw 'Install transaction exists'}
$active=@(Get-CimInstance Win32_Process|Where-Object {$_.ExecutablePath -and $_.ExecutablePath.StartsWith($install+'\',[StringComparison]::OrdinalIgnoreCase)})
if($active.Count){throw 'An installed app is open; preserve its work first'}
if($Phase -eq 'prepare'){
 if((Test-Path -LiteralPath $record) -or (Test-Path -LiteralPath $backup) -or (Test-Path -LiteralPath $saved)){throw 'Preservation already exists'}
 $r=[ordered]@{time=[DateTime]::Now.ToString('o');install=$install;backup=$backup;menu=$menu;desktop=$desktop;user_path=[Environment]::GetEnvironmentVariable('Path','User');machine_path=[Environment]::GetEnvironmentVariable('Path','Machine');files=(Inventory $install);registry=@();moves=@();standard_user=$true}
 New-Item -ItemType Directory -Path $saved|Out-Null
 foreach($key in @('HKCU:\Software\Classes\.sm','HKCU:\Software\Classes\Sutram.Source','HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram')){
  $exists=Test-Path -LiteralPath $key;$leaf=Split-Path $key -Leaf;$new=$leaf+'-'+$stamp
  if(Test-Path -LiteralPath (Join-Path (Split-Path $key) $new)){throw 'Registry backup exists'}
  $r.registry+=@{key=$key;existed=$exists;preserved_name=$new}
 }
 Save $r 'preserve.json'
 Move-Item -LiteralPath $install -Destination $backup;Verify $backup $r.files
 if(Test-Path -LiteralPath $menu){Move-Item -LiteralPath $menu -Destination (Join-Path $saved 'start-menu');$r.moves+=@{source=$menu;backup=(Join-Path $saved 'start-menu')}}
 if(Test-Path -LiteralPath $desktop){Move-Item -LiteralPath $desktop -Destination (Join-Path $saved 'original-desktop.lnk');$r.moves+=@{source=$desktop;backup=(Join-Path $saved 'original-desktop.lnk')}}
 foreach($k in $r.registry){if($k.existed){Rename-Item -LiteralPath $k.key -NewName $k.preserved_name}}
 $bin=Join-Path $install 'bin'
 $clean=($r.user_path -split ';'|Where-Object {$_.TrimEnd('\') -ine $bin -and $_.TrimEnd('\') -ine $install}) -join ';'
 [Environment]::SetEnvironmentVariable('Path',$clean,'User');$env:Path=$r.machine_path+';'+$clean
 $r.test_user_path=$clean;$r.files_verified=$r.files.Count
 $sc=(New-Object -ComObject WScript.Shell).CreateShortcut($desktop);$sc.TargetPath=Join-Path $env:WINDIR 'System32\notepad.exe';$sc.Description='Harmless first-run collision fixture';$sc.Save()
 $r.collision_sha256=(Get-FileHash -LiteralPath $desktop).Hash;$r.phase='prepared';Save $r 'preserve.json'
 Write-Host "Preserved $($r.files.Count) installation files; moved menu and registry keys; created Notepad collision fixture."
}else{
 $r=Get-Content -LiteralPath $record -Encoding UTF8 -Raw|ConvertFrom-Json
 if($r.phase -ne 'prepared'){throw 'Not prepared'}
 $test=Join-Path $parent 'Sutram-firstrun-tested-20261108';Guard $test $parent
 if(Test-Path -LiteralPath $test){throw 'Test preservation exists'}
 Verify $backup $r.files
 $testFiles=Inventory $install;Move-Item -LiteralPath $install -Destination $test;Verify $test $testFiles
 Move-Item -LiteralPath $backup -Destination $install;Verify $install $r.files
 if(Test-Path -LiteralPath $menu){Move-Item -LiteralPath $menu -Destination (Join-Path $saved 'tested-start-menu')}
 if(Test-Path -LiteralPath $desktop){Move-Item -LiteralPath $desktop -Destination (Join-Path $saved 'tested-desktop-collision.lnk')}
 foreach($m in $r.moves){Move-Item -LiteralPath $m.backup -Destination $m.source}
 foreach($k in $r.registry){if(Test-Path -LiteralPath $k.key){Rename-Item -LiteralPath $k.key -NewName ((Split-Path $k.key -Leaf)+'-Tested'+$stamp)};if($k.existed){Rename-Item -LiteralPath (Join-Path (Split-Path $k.key) $k.preserved_name) -NewName (Split-Path $k.key -Leaf)}}
 [Environment]::SetEnvironmentVariable('Path',$r.user_path,'User')
 if([Environment]::GetEnvironmentVariable('Path','Machine') -cne $r.machine_path){throw 'Machine PATH changed'}
 Save @{time=[DateTime]::Now.ToString('o');restored=$install;original_files_verified=$r.files.Count;tested_install_preserved=$test;tested_files=$testFiles;user_path_restored=([Environment]::GetEnvironmentVariable('Path','User') -ceq $r.user_path);no_deletions=$true} 'restore.json'
 Write-Host 'Original installation, shortcuts, registry keys and PATH restored; test installation and collision shortcut preserved.'
}
