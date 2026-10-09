# USER-RUN Windows desktop smoke test. Standard-user rights; no hooks or policy changes.
# Run from a normal interactive PowerShell desktop session, not a service/CI headless session.
# Unexecuted in the ChatGPT Linux sandbox; a manual checklist is also required.
[CmdletBinding()]
param([string]$Exe = '')
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
$root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not $Exe) { $Exe = Join-Path $root 'sutram-ide-gui.exe' }
if (-not (Test-Path $Exe)) { throw "Build first: $Exe" }
if (-not (Test-Path (Join-Path $root 'win\sutram.exe'))) { throw 'Expected win\sutram.exe not found' }
$proc = Start-Process -FilePath $Exe -WorkingDirectory $root -PassThru
try {
    $main = $null
    for ($i=0; $i -lt 40; $i++) {
        Start-Sleep -Milliseconds 250
        $proc.Refresh()
        if ($proc.HasExited) { throw "GUI exited unexpectedly ($($proc.ExitCode))" }
        if ($proc.MainWindowHandle -ne [IntPtr]::Zero) {
            $main = [System.Windows.Automation.AutomationElement]::FromHandle($proc.MainWindowHandle)
            if ($main) { break }
        }
    }
    if (-not $main) { throw 'Window did not appear within 10 seconds' }
    if ($main.Current.Name -ne 'Sutram - Native Windows IDE (Preview)') { throw "Wrong window title: $($main.Current.Name)" }
    Write-Host 'PASS GUI window/title' -ForegroundColor Green
    $desc = $main.FindAll('Descendants',[System.Windows.Automation.Condition]::TrueCondition)
    $run = $null
    $edit = $null
    $out = $null
    foreach ($item in $desc) {
        if ($item.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and $item.Current.Name -eq 'Run') { $run = $item }
        if ($item.Current.AutomationId -eq '201') { $edit = $item }
        if ($item.Current.AutomationId -eq '203') { $out = $item }
    }
    if (-not $run -or -not $edit -or -not $out) { throw 'Run button, editor or output control not found' }
    Write-Host 'PASS editor/output/Run controls' -ForegroundColor Green
    # Prefer UIA ValuePattern for editable text; RichEdit may expose TextPattern instead.
    $pat = $null
    if ($edit.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$pat)) {
        $pat.SetValue("mukhya()`r`n    likha(`"GUI_AUTOTEST_OK\n`")`r`n")
    } else {
        $edit.SetFocus()
        [System.Windows.Forms.SendKeys]::SendWait('^a')
        [System.Windows.Forms.SendKeys]::SendWait('mukhya(){ENTER}    likha("GUI_AUTOTEST_OK\n")')
    }
    $invoke = $run.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
    $invoke.Invoke()
    Start-Sleep -Seconds 2
    $val = $null
    if (-not $out.TryGetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern,[ref]$val)) {
        throw 'Output edit has no ValuePattern; inspect manually instead'
    }
    $got = $val.Current.Value
    if ($got -notmatch 'GUI_AUTOTEST_OK') { throw "Expected stdout not captured. Actual: $got" }
    Write-Host 'PASS typed source compiled and output pane updated' -ForegroundColor Green
    Write-Host 'Automated smoke PASSED; complete MANUAL-WINDOWS-GUI-TEST.md before acceptance.'
} finally {
    if (-not $proc.HasExited) {
        $proc.CloseMainWindow() | Out-Null
        if (-not $proc.WaitForExit(3000)) { Write-Warning 'GUI did not exit cleanly; close it manually.' }
    }
}
