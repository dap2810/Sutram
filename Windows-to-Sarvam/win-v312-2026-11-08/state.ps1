param([ValidateSet('snapshot')][string]$Action='snapshot',[ValidatePattern('^[a-z0-9-]+$')][string]$Name='starting')
$ErrorActionPreference='Stop';$out=$PSScriptRoot;$root=Split-Path (Split-Path $out -Parent) -Parent
$work=Join-Path $root 'build\native-v312';$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
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
