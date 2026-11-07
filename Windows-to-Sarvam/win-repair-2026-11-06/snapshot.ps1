param([string]$Phase)
$ErrorActionPreference='Stop'
$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
function Raw-Path($Hive,$KeyPath) {
    $key=$Hive.OpenSubKey($KeyPath)
    try { return [ordered]@{value=$key.GetValue('Path','',[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames);kind=$key.GetValueKind('Path').ToString()} }
    finally { $key.Dispose() }
}
function Bounded([string]$File,[string]$Arguments) {
    $p=[Diagnostics.Process]::new(); $p.StartInfo.FileName=$File; $p.StartInfo.Arguments=$Arguments
    $p.StartInfo.UseShellExecute=$false; $p.StartInfo.CreateNoWindow=$true
    $p.StartInfo.RedirectStandardOutput=$true; $p.StartInfo.RedirectStandardError=$true
    try {
        [void]$p.Start(); $ot=$p.StandardOutput.ReadToEndAsync(); $et=$p.StandardError.ReadToEndAsync()
        $timed=-not $p.WaitForExit(10000)
        if ($timed) { $p.Kill(); [void]$p.WaitForExit(2000) }
        return @{file=$File;arguments=$Arguments;stdout=$ot.Result;stderr=$et.Result;exit=$p.ExitCode;timed_out=$timed}
    } finally { $p.Dispose() }
}
$r=[ordered]@{phase=$Phase;time=[DateTime]::Now.ToString('o');install=$install}
$r.machine=Raw-Path ([Microsoft.Win32.Registry]::LocalMachine) 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment'
$r.user=Raw-Path ([Microsoft.Win32.Registry]::CurrentUser) 'Environment'
$r.process_path=$env:PATH
$r.reg_machine=Bounded 'reg.exe' 'query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path'
$r.reg_user=Bounded 'reg.exe' 'query "HKCU\Environment" /v Path'
$r.inherited_where=Bounded 'where.exe' 'sutram'
$oldPath=$env:PATH
try {
    $env:PATH=[Environment]::GetEnvironmentVariable('Path','Machine')+';'+[Environment]::GetEnvironmentVariable('Path','User')
    $r.persisted_where=Bounded 'where.exe' 'sutram'
    $r.persisted_version=Bounded $env:ComSpec '/d /c sutram --version'
} finally { $env:PATH=$oldPath }
$r.tree=@(Get-ChildItem -LiteralPath $install -Recurse -Force -File | ForEach-Object {
    [ordered]@{path=$_.FullName.Substring($install.Length+1);bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash;modified=$_.LastWriteTime.ToString('o')}
})
$r.root_listing=@(Get-ChildItem -LiteralPath $install -Force | Select-Object Name,Length,Mode)
$r.bin_listing=@(Get-ChildItem -LiteralPath (Join-Path $install 'bin') -Force | Select-Object Name,Length,Mode)
$r.uninstallers=@(Get-ChildItem -LiteralPath $install -Filter '*uninstall*' | Select-Object Name,Length)
$r.metadata=@{}
foreach ($name in @('install-state.ini','install.log','.sutram-install','payload.manifest.sha256')) {
    $p=Join-Path $install $name
    if (Test-Path -LiteralPath $p) { $r.metadata[$name]=[IO.File]::ReadAllText($p) }
}
$r.registration=Get-ItemProperty -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram' -ErrorAction SilentlyContinue | Select-Object DisplayName,DisplayVersion,InstallLocation,UninstallString
[IO.File]::WriteAllText((Join-Path $PSScriptRoot ($Phase+'.json')),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
Write-Host "Snapshot $Phase saved; installed files: $($r.tree.Count)"
