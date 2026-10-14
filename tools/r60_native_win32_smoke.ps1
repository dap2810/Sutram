#requires -version 5.1
# Real Windows Win32 control driver. Pure native messages are used because
# MSFTEDIT RICHEDIT50W is not enumerated by UIAutomation on the hosted runner.
# This test DOES execute Sutram compiler+result and shell, not merely a source scan.
[CmdletBinding()]
param([string]$Exe,[string]$ResultsDir="")
$ErrorActionPreference='Stop'
if(-not $Exe){ throw 'Provide the exact compiled GUI path using -Exe' }
if(-not (Test-Path -LiteralPath $Exe)){throw "Missing GUI executable $Exe"}
$exeRoot=(Resolve-Path (Split-Path -Parent $Exe)).Path
if(-not (Test-Path (Join-Path $exeRoot 'win\sutram.exe'))){ throw "Missing compiler relative to GUI: $exeRoot\win\sutram.exe" }
if(-not $ResultsDir){$ResultsDir=Join-Path $env:TEMP 'sutram-r60-desktop'}
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class SutramR60Driver {
 [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr parent,int id);
 [DllImport("user32.dll",EntryPoint="SetWindowTextW",CharSet=CharSet.Unicode,SetLastError=true)]
 public static extern bool SetWindowText(IntPtr handle,string text);
 [DllImport("user32.dll",EntryPoint="GetWindowTextW",CharSet=CharSet.Unicode)]
 public static extern int GetWindowText(IntPtr handle,StringBuilder text,int max);
 [DllImport("user32.dll",EntryPoint="SendMessageW",CharSet=CharSet.Unicode)]
 public static extern IntPtr SendMessage(IntPtr hwnd,uint msg,IntPtr wparam,IntPtr lparam);
}
'@
function Get-Text([IntPtr]$h) {
    $sb=New-Object System.Text.StringBuilder 32768
    [void][SutramR60Driver]::GetWindowText($h,$sb,$sb.Capacity)
    return $sb.ToString()
}
function Screenshot([string]$name) {
    $r=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp=New-Object System.Drawing.Bitmap($r.Width,$r.Height)
    $gr=[System.Drawing.Graphics]::FromImage($bmp)
    try {
        $gr.CopyFromScreen($r.Location,[System.Drawing.Point]::Empty,$r.Size)
        $dest=Join-Path $ResultsDir ($name+'.png')
        $bmp.Save($dest,[System.Drawing.Imaging.ImageFormat]::Png)
        Write-Host ("R60_NATIVE_SCREENSHOT "+$name+" path="+$dest)
    } finally {$gr.Dispose();$bmp.Dispose()}
}
$proc=Start-Process -FilePath $Exe -WorkingDirectory $exeRoot -PassThru
try {
    $h=[IntPtr]::Zero
    for($i=0;$i -lt 50;$i++) {
        Start-Sleep -Milliseconds 200
        $proc.Refresh()
        if($proc.HasExited){ throw ("Native IDE process quit unexpectedly, exit="+$proc.ExitCode) }
        if($proc.MainWindowHandle -ne [IntPtr]::Zero) {$h=$proc.MainWindowHandle; break}
    }
    if($h -eq [IntPtr]::Zero){throw 'No native IDE top-level HWND'}
    $ids=@(101,201,203,204,105)
    $handles=@{}
    foreach($id in $ids) {
        $child=[SutramR60Driver]::GetDlgItem($h,[int]$id)
        if($child -eq [IntPtr]::Zero){throw ("Native child missing id="+$id)}
        $handles[$id]=$child
        Write-Host ("R60_NATIVE_CHILD_FOUND id="+$id+" hwnd="+$child.ToInt64())
    }
    $code="mukhya() {"+ [Environment]::NewLine+
          '    likha("GUI_AUTOTEST_OK")'+[Environment]::NewLine+
          '}'+[Environment]::NewLine
    if(-not [SutramR60Driver]::SetWindowText($handles[201],$code)){throw 'SetWindowTextW failed in MSFTEDIT editor'}
    Start-Sleep -Milliseconds 700
    Screenshot 'IDE_SYNTAX_TEST'
    [void][SutramR60Driver]::SendMessage($h,0x111,[IntPtr]101,$handles[101])
    Start-Sleep -Milliseconds 500
    $out=Get-Text $handles[203]
    Write-Host ("R60_EDITOR_OUTPUT "+[regex]::Escape($out.Substring(0,[Math]::Min($out.Length,240))))
    if($out -notmatch "GUI_AUTOTEST_OK"){throw ("Actual native compiler/editor execution failed: "+$out)}
    Write-Host 'R60_EDITOR_RUN_NATIVE_PASS exact stdout match'
    $shellCode='likha("SHELL_AUTOTEST_OK")'
    if(-not [SutramR60Driver]::SetWindowText($handles[204],$shellCode)){throw 'SetWindowTextW failed in shell input'}
    [void][SutramR60Driver]::SendMessage($h,0x111,[IntPtr]105,$handles[105])
    Start-Sleep -Milliseconds 650
    $out=Get-Text $handles[203]
    Write-Host ("R60_SHELL_OUTPUT "+[regex]::Escape($out.Substring(0,[Math]::Min($out.Length,240))))
    Screenshot 'IDE_SHELL_TEST'
    if($out -notmatch "SHELL_AUTOTEST_OK"){throw ("Shell did not execute submitted source: "+$out)}
    Write-Host 'R60_SHELL_RUN_NATIVE_PASS exact stdout match'
} finally {
    if(-not $proc.HasExited) {
        [void]$proc.CloseMainWindow()
        if(-not $proc.WaitForExit(3000)){Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue}
    }
}
