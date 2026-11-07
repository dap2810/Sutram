param([ValidateSet('snapshot','clear')][string]$Action='snapshot',[ValidatePattern('^[a-z0-9-]+$')][string]$Name='starting')
$ErrorActionPreference='Stop';$out=$PSScriptRoot;$root=Split-Path (Split-Path $out -Parent) -Parent
$work=Join-Path $root 'build\native-v311-acceptance';$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
$menu=Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram';$desktop=Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'Sutram IDE.lnk'
$keys=@{uninstall='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram';class='HKCU:\Software\Classes\Sutram.Source';extension='HKCU:\Software\Classes\.sm'}
$utf8=[Text.UTF8Encoding]::new($false)
function Save($Obj,[string]$File){[IO.File]::WriteAllText((Join-Path $out $File),($Obj|ConvertTo-Json -Depth 12),$utf8)}
function Shell([string]$Command){
    $psi=[Diagnostics.ProcessStartInfo]::new($env:ComSpec,('/d /c '+$Command));$psi.WorkingDirectory=$work;$psi.UseShellExecute=$false;$psi.CreateNoWindow=$true;$psi.RedirectStandardOutput=$true;$psi.RedirectStandardError=$true
    $psi.EnvironmentVariables['Path']=([Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User'))
    $p=[Diagnostics.Process]::Start($psi);$stdout=$p.StandardOutput.ReadToEndAsync();$stderr=$p.StandardError.ReadToEndAsync()
    if(-not $p.WaitForExit(15000)){$p.Kill();throw 'State command timed out'}
    return @{command=$Command;exit=$p.ExitCode;stdout=$stdout.Result;stderr=$stderr.Result;cwd=$work;fresh_registry_path=$true}
}
function Snapshot([string]$Label){
    $r=[ordered]@{name=$Label;time=[DateTime]::Now.ToString('o');commands=@();user_path=[Environment]::GetEnvironmentVariable('Path','User');machine_path=[Environment]::GetEnvironmentVariable('Path','Machine');registry=@{};install_exists=(Test-Path -LiteralPath $install);menu_exists=(Test-Path -LiteralPath $menu);desktop_exists=(Test-Path -LiteralPath $desktop)}
    foreach($cmd in @('where sutram','sutram --version','dir "%LOCALAPPDATA%\Programs"','reg query "HKCU\Environment" /v Path','reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path')){$r.commands+=Shell $cmd}
    foreach($k in $keys.Keys){$r.registry[$k]=Shell ('reg query "'+$keys[$k].Replace('HKCU:\','HKCU\')+'" /s')}
    if(Test-Path -LiteralPath $install){$r.install_files=@(Get-ChildItem -LiteralPath $install -Recurse -Force -File|ForEach-Object {@{relative=$_.FullName.Substring($install.Length+1);bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash}})}
    $r.menu_files=@(Get-ChildItem -LiteralPath $menu -Recurse -File -ErrorAction SilentlyContinue|ForEach-Object {$_.FullName})
    Save $r ($Label+'-state.json');return $r
}
if($Action -eq 'snapshot'){$r=Snapshot $Name;Write-Host "$Name state saved: where exit $($r.commands[0].exit)";exit}
if(Test-Path -LiteralPath (Join-Path $out 'clear-active-state.json')){throw 'Fresh-state preparation already performed'}
$before=Snapshot 'starting'
if($before.commands[0].stdout.Trim() -ne (Join-Path $install 'bin\sutram.exe')){throw 'Unexpected compiler resolution; inspect before changing state'}
$reg=Get-ItemProperty -LiteralPath $keys.uninstall
if($reg.InstallLocation -ne $install){throw 'Unexpected registered installation'}
# Preserve whole active trees and shortcut bytes; never delete original files.
& (Join-Path $out 'preserve.ps1') -Action backup -Name before-acceptance
$archive=Join-Path $work 'preserved-shortcuts';if(Test-Path $archive){throw 'Shortcut archive already exists'}
[void][IO.Directory]::CreateDirectory($archive)
$exports=@{}
foreach($k in $keys.Keys){
    if(Test-Path -LiteralPath $keys[$k]){
        $f=Join-Path $out ('before-'+$k+'.reg');& reg.exe export ($keys[$k].Replace('HKCU:\','HKCU\')) $f /y|Out-Null
        if($LASTEXITCODE){throw 'Registration export failed'};$exports[$k]=@{file=$f;sha256=(Get-FileHash $f).Hash}
    }
}
# This machine's .sm registration must contain only Sutram entries before moving it.
$ext=Get-Item -LiteralPath $keys.extension
if($ext.GetValue('') -ne 'Sutram.Source' -or @($ext.GetValueNames()|Where-Object {$_ -ne ''}).Count){throw 'Non-Sutram extension values present'}
if(@($ext.GetSubKeyNames()|Where-Object {$_ -ne 'OpenWithProgids'}).Count){throw 'Non-Sutram extension subkeys present'}
$ow=$ext.OpenSubKey('OpenWithProgids');if($ow){try{if(@($ow.GetValueNames()|Where-Object {$_ -ne 'Sutram.Source'}).Count){throw 'Other app association exists'}}finally{$ow.Dispose()}}
$regArchive='HKCU:\Software\SutramAcceptanceArchives\v311-20261107'
if(Test-Path -LiteralPath $regArchive){throw 'Registry archive exists'}
New-Item -Path $regArchive -Force|Out-Null
$moves=@()
foreach($k in @('uninstall','class','extension')){if(Test-Path -LiteralPath $keys[$k]){$dest=Join-Path $regArchive $k;Move-Item -LiteralPath $keys[$k] -Destination $dest;$moves+=@{from=$keys[$k];to=$dest};if(Test-Path -LiteralPath $keys[$k]){throw 'Active registry key still present'}}}
if(Test-Path -LiteralPath $menu){Move-Item -LiteralPath $menu -Destination (Join-Path $archive 'StartMenu-Sutram');$moves+=@{from=$menu;to=(Join-Path $archive 'StartMenu-Sutram')}}
if(Test-Path -LiteralPath $desktop){Move-Item -LiteralPath $desktop -Destination (Join-Path $archive 'Desktop-Sutram-IDE.lnk');$moves+=@{from=$desktop;to=(Join-Path $archive 'Desktop-Sutram-IDE.lnk')}}
& (Join-Path $out 'preserve.ps1') -Action vacate -Name active-before-first-install
$old=[Environment]::GetEnvironmentVariable('Path','User');$removed=@();$kept=@()
foreach($entry in ($old -split ';')){if($entry.Trim().Trim('"').TrimEnd('\') -match '(?i)\\Sutram(?:\\bin)?$'){$removed+=$entry}else{$kept+=$entry}}
[Environment]::SetEnvironmentVariable('Path',($kept -join ';'),'User')
Save @{exports=$exports;moves=$moves;removed_user_path_entries=$removed;original_user_path=$old;active_user_path=[Environment]::GetEnvironmentVariable('Path','User');machine_path_unchanged=([Environment]::GetEnvironmentVariable('Path','Machine') -eq $before.machine_path);preservation_note='Files and active registry subtrees moved into archives; .reg exports retained. No original file deleted.'} 'clear-active-state.json'
$after=Snapshot 'after-removal'
if($after.commands[0].exit -ne 1 -or $after.commands[0].stdout.Trim()){throw 'STOP: a Sutram compiler still resolves after removal'}
Write-Host 'Active Sutram state preserved and moved aside; new-shell where sutram returns not found.'
