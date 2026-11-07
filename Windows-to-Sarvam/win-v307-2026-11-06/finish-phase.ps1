param([ValidateSet('upgrade')][string]$Phase='upgrade')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'ui-helper.ps1')
$prior=Get-Content (Join-Path $OutDir ($Phase+'.json')) -Raw|ConvertFrom-Json
$wizard=Get-Process -Id $prior.pid
if($wizard.StartTime.ToString('o') -ne $prior.process_started){throw 'Wizard identity mismatch'}
$main=Wait-Until {[SutramIde]::WindowsOf([uint32]$prior.pid,'SutramWizardWindow')|Select-Object -First 1} 5000
if(-not $main){throw 'No wizard window'}
$r=[ordered]@{observed_at=[DateTime]::Now.ToString('o');pid=$prior.pid;engine_child_pid=$prior.child.pid;engine_child_still_running=[bool](Get-Process -Id $prior.child.pid -ErrorAction SilentlyContinue);timing_note='Observer stopped on log sharing violation. This attaches to the same wizard; no second installer was launched.'}
if($r.engine_child_still_running){throw 'Child is still running; use observer instead'}
$dialogs=@([SutramIde]::WindowsOf([uint32]$prior.pid,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)})
if($dialogs.Count){
    $r.status='ERROR_DIALOG';$r.dialog_text=[SutramIde]::ChildTexts($dialogs[0]);$r.screenshot=Shot $dialogs[0] ($Phase+'-error')
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($dialogs[0],1),0xF5,0,0,3000)
    [void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero)
}else{
    $label=[SutramIde]::Text([SutramIde]::GetDlgItem($main,2002))
    if($label -ne 'Finish'){throw "Unexpected page: $label"}
    $r.status='FINISH';$r.wizard_self_closed_before_finish_click=$false;$r.screenshot=Shot $main ($Phase+'-finish')
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2060),0xF1,0,0,3000)
    [void][SutramIde]::Send([SutramIde]::GetDlgItem($main,2002),0xF5,0,0,3000)
}
$r.closed_after_action=$wizard.WaitForExit(5000)
$log=if(Test-Path -LiteralPath $prior.engine_log){$prior.engine_log}else{Join-Path $env:LOCALAPPDATA 'Programs\Sutram\install.log'}
Copy-Item -LiteralPath $log -Destination (Join-Path $OutDir ($Phase+'-engine.log')) -Force
$r|ConvertTo-Json -Depth 4|Set-Content (Join-Path $OutDir ($Phase+'-finish.json')) -Encoding UTF8
$r|ConvertTo-Json -Depth 4
