$ideExe=Join-Path $env:LOCALAPPDATA 'Programs\Sutram\sutram-ide-gui.exe'
$install=Split-Path -Parent $ideExe
$ip=Start-Process -FilePath $ideExe -WorkingDirectory $install -PassThru
$main=Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id,'SutramNativeGUIWindow') | Select-Object -First 1 } 5000
$checks=@()
try {
    if (-not $main) { throw 'IDE failed to open in five seconds' }
    Start-Sleep -Milliseconds 800
    $editor=[SutramIde]::GetDlgItem($main,201)
    $output=[SutramIde]::GetDlgItem($main,203)
    $checks += [pscustomobject]@{test=22;result='PASS';output='Installed IDE window opened';screenshot=(Shot $main 'test22-open')}
    foreach ($case in @(@(23,'hello.sm'),@(24,'divzero.sm'),@(21,'deva.sm'))) {
        $source=[IO.File]::ReadAllText((Join-Path $PSScriptRoot ('programs\'+$case[1])),[Text.Encoding]::UTF8)
        [SutramIde]::SetText($editor,$source.Replace("`n","`r`n"))
        [void][SutramIde]::Send($main,0x111,2010,0,5000)
        $got=[SutramIde]::Text($output)
        $checks += [pscustomobject]@{test=$case[0];output=$got;screenshot=(Shot $main ('test'+$case[0]));result='OBSERVED'}
    }
} finally {
    [IO.File]::WriteAllText((Join-Path $OutDir 'gui-results.json'),($checks | ConvertTo-Json -Depth 4),[Text.UTF8Encoding]::new($false))
    if (-not $ip.HasExited) { $ip.Kill(); $ip.WaitForExit() }
}
