param([string]$SourceRoot = 'E:\Github_Projects\Sutram\build\windows-v303-review')
$ErrorActionPreference = 'Stop'
$OutDir = $PSScriptRoot
. (Join-Path $PSScriptRoot 'ui-helper.ps1')
$setup = Join-Path $SourceRoot 'Sutram-Setup.exe'
$install = Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
$record = [ordered]@{ setup=$setup; setup_sha256=(Get-FileHash $setup).Hash; install=$install; started=[DateTime]::Now.ToString('o'); steps=@() }
$ip = $null
function Click-Control([int]$ControlId) {
    $control = [SutramIde]::GetDlgItem($main,$ControlId)
    if ($control -eq [IntPtr]::Zero) { throw "Missing control $ControlId" }
    [void][SutramIde]::Send($control,0xF5,0,0,3000)
    Start-Sleep -Milliseconds 300
}
try {
    $identity=[Security.Principal.WindowsIdentity]::GetCurrent()
    $principal=New-Object Security.Principal.WindowsPrincipal($identity)
    $record.elevated=$principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if ($record.elevated) { throw 'Must run as a non-elevated user' }
    $ip=Start-Process -FilePath $setup -WorkingDirectory $SourceRoot -WindowStyle Hidden -PassThru
    $main=Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id,'SutramWizardWindow') | Select-Object -First 1 } 10000
    if (-not $main) { throw 'Wizard did not open in 10 seconds' }
    $record.welcome=Shot $main 'installer-welcome'
    Click-Control 2002
    Click-Control 2010
    Click-Control 2002
    $record.destination=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2020))
    if ($record.destination.TrimEnd('\') -ne $install.TrimEnd('\')) { throw 'Unexpected install destination' }
    Click-Control 2002
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2030),0xF1,1,0,3000)
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2031),0xF1,0,0,3000)
    Click-Control 2002
    $record.ready=Shot $main 'installer-ready'
    Click-Control 2002
    $finish=Wait-Until { $label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002)); if ($label -match 'Finish') { $label } } 30000
    $record.finish_label=$finish
    $record.finished=Shot $main 'installer-finished'
    if (-not $finish) { throw 'Installation did not reach Finish within 30 seconds' }
    # Close only this wizard; do not launch a terminal from its optional checkbox.
    [void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero)
    [void]$ip.WaitForExit(3000)
    Copy-Item -LiteralPath (Join-Path $install 'install.log') -Destination (Join-Path $OutDir 'install.log')
    $record.status='PASS'
} catch {
    $record.status='FAIL'; $record.error=$_.Exception.Message
    throw
} finally {
    if ($ip -and -not $ip.HasExited) { $ip.Kill(); [void]$ip.WaitForExit(3000) }
    [IO.File]::WriteAllText((Join-Path $OutDir 'installer.json'),($record | ConvertTo-Json -Depth 6),[Text.UTF8Encoding]::new($false))
}
$record | ConvertTo-Json -Depth 6
