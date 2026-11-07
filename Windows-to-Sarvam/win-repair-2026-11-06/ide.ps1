$ErrorActionPreference='Stop'
$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'ui-helper.ps1')
$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
$shortcut=Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'Sutram IDE.lnk'
$sc=(New-Object -ComObject WScript.Shell).CreateShortcut($shortcut)
if($sc.TargetPath -ne (Join-Path $install 'sutram-ide-gui.exe')) { throw 'Shortcut does not target repaired IDE' }
$r=[ordered]@{shortcut=$shortcut;target=$sc.TargetPath;target_sha256=(Get-FileHash $sc.TargetPath).Hash;started=[DateTime]::Now.ToString('o');cases=@()}
$ip=$null
try {
    $ip=Start-Process -FilePath $shortcut -WindowStyle Normal -PassThru
    if(-not $ip) { throw 'Shortcut launch did not return a process' }
    $r.pid=$ip.Id
    $main=Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id,'SutramNativeGUIWindow')|Select-Object -First 1 } 10000
    if(-not $main) { throw 'Installed IDE did not open' }
    $editor=[SutramIde]::GetDlgItem($main,201); $output=[SutramIde]::GetDlgItem($main,203); $list=[SutramIde]::GetDlgItem($main,205)
    foreach($name in @('01_hello.sm','02_arith.sm')) {
        $idx=[SutramIde]::ListFind($list,$name)
        if($idx -lt 0) { throw "Installed example missing: $name" }
        [void][SutramIde]::Send($list,0x186,$idx,0,3000)
        [void][SutramIde]::Send($main,0x111,((2 -shl 16) -bor 205),$list.ToInt64(),30000)
        [void][SutramIde]::Send($main,0x111,2010,0,30000)
        Start-Sleep -Milliseconds 300
        $r.cases+=@{example=$name;title=[SutramIde]::Text($main);editor=[SutramIde]::Text($editor);output=[SutramIde]::Text($output);screenshot=(Shot $main ('installed-'+[IO.Path]::GetFileNameWithoutExtension($name)))}
    }
    $r.pass=$r.cases[0].output.Contains('Namaste, Sutram!') -and $r.cases[1].output.Contains('x + y = 30')
} catch { $r.error=$_.Exception.Message; throw }
finally {
    if($ip -and -not $ip.HasExited) { [void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero); $r.closed=$ip.WaitForExit(3000) }
    [IO.File]::WriteAllText((Join-Path $OutDir 'ide.json'),($r|ConvertTo-Json -Depth 6),[Text.UTF8Encoding]::new($false))
}
$r|ConvertTo-Json -Depth 6
