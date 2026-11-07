$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'ui-helper.ps1')
# The first observer serialized PowerShell provider metadata from Get-Content.
# Stop only that observer, whose command and start time are checked here.
$observer=Get-CimInstance Win32_Process -Filter 'ProcessId = 40500'
if($observer -and $observer.CommandLine -like '*win-v307-2026-11-06\run-install.ps1 -Phase clean*'){
    $p=Get-Process -Id 40500
    if($p.StartTime.Date -ne [datetime]'2026-11-06'){throw 'Observer identity mismatch'}
    Stop-Process -Id 40500 -Force
}
$wizard=Get-Process -Id 5584
if($wizard.StartTime.ToString('yyyy-MM-ddTHH:mm:ss') -ne '2026-11-06T22:39:02'){throw 'Wizard identity mismatch'}
$main=Wait-Until {[SutramIde]::WindowsOf(5584,'SutramWizardWindow')|Select-Object -First 1} 5000
if(-not $main){throw 'No wizard window'}
$label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002))
if($label -ne 'Finish'){throw "Unexpected page: $label"}
$r=[ordered]@{observed_at=[DateTime]::Now.ToString('o');status='FINISH';pid=5584;engine_child_pid=20260;engine_child_still_running=[bool](Get-Process -Id 20260 -ErrorAction SilentlyContinue);wizard_self_closed_before_finish_click=$false;screenshot=(Shot $main 'clean-finish');timing_note='Engine log timestamps are usable; initial observer JSON serialization delayed Finish observation.'}
Copy-Item -LiteralPath (Join-Path $env:LOCALAPPDATA 'Programs\Sutram\install.log') -Destination (Join-Path $OutDir 'clean-engine.log')
[void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2060),0xF1,0,0,3000)
[void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2002),0xF5,0,0,3000)
$r.closed_after_finish_click=$wizard.WaitForExit(5000)
$r|ConvertTo-Json -Depth 4|Set-Content (Join-Path $OutDir 'clean-finish.json') -Encoding UTF8
$r|ConvertTo-Json -Depth 4
