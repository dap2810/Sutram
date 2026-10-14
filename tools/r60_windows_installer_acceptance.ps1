#requires -version 5.1
# Real hosted-Windows per-user installer execution; isolated ephemeral VM only.
# No registry machine writes, elevation, policy change, installer bypass.
[CmdletBinding()]
param([Parameter(Mandatory=$true)][string]$Setup,[Parameter(Mandatory=$true)][string]$CanonicalIcon,[string]$ResultsDir="")
$ErrorActionPreference='Stop'
if(-not $ResultsDir){$ResultsDir=Join-Path $env:TEMP 'sutram-r60'}
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class SutramR60Install {
 [DllImport("user32.dll",EntryPoint="PostMessageW",SetLastError=true)]
 public static extern bool PostMessage(IntPtr hwnd,uint msg,IntPtr wParam,IntPtr lParam);
 [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr hwnd,int id);
}
'@
function Capture([string]$name) {
    try {
        $r=[System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        $bmp=New-Object Drawing.Bitmap($r.Width,$r.Height)
        $g=[Drawing.Graphics]::FromImage($bmp)
        try{
            $g.CopyFromScreen($r.Location,[Drawing.Point]::Empty,$r.Size)
            $dest=Join-Path $ResultsDir ($name+".png")
            $bmp.Save($dest,[Drawing.Imaging.ImageFormat]::Png)
            Write-Host ("R60_INSTALL_SCREENSHOT path="+$dest)
        }finally{$g.Dispose();$bmp.Dispose()}
    }catch{Write-Host ("R60_INSTALL_SCREENSHOT_UNVERIFIED "+$_.Exception.Message)}
}
$setup=(Resolve-Path -LiteralPath $Setup).Path
$expected=(Get-FileHash -Algorithm SHA256 -LiteralPath $CanonicalIcon).Hash.ToLowerInvariant()
$installRoot=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
$gui=Join-Path $installRoot 'sutram-ide-gui.exe'
$icon=Join-Path $installRoot 'assets\sutram.ico'
$link=Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram\Sutram IDE.lnk'
if(Test-Path -LiteralPath $gui){throw "Refuse to test over pre-existing installation $gui"}
$proc=Start-Process -FilePath $setup -WorkingDirectory (Split-Path $setup -Parent) -PassThru
try {
    $hwnd=[IntPtr]::Zero
    for($i=0;$i -lt 40;$i++){
        Start-Sleep -Milliseconds 200
        $proc.Refresh()
        if($proc.HasExited){throw ("Setup exited unexpectedly "+$proc.ExitCode)}
        if($proc.MainWindowHandle -ne [IntPtr]::Zero){$hwnd=$proc.MainWindowHandle;break}
    }
    if($hwnd -eq [IntPtr]::Zero){throw 'Installer main HWND absent'}
    $installButton=[SutramR60Install]::GetDlgItem($hwnd,1001)
    if($installButton -eq [IntPtr]::Zero){throw 'Install button ID 1001 missing'}
    Write-Host ("R60_INSTALL_CLICK_REAL_BUTTON hwnd="+$installButton.ToInt64()+" user="+$env:USERNAME)
    Capture 'SETUP_PRE_INSTALL'
    if(-not [SutramR60Install]::PostMessage($hwnd,0x111,[IntPtr]1001,$installButton)){throw 'WM_COMMAND install PostMessage failed'}
    $found=$false
    for($i=0;$i -lt 90;$i++){
        Start-Sleep -Milliseconds 500
        if((Test-Path -LiteralPath $gui -PathType Leaf) -and
           (Test-Path -LiteralPath $icon -PathType Leaf) -and
           (Test-Path -LiteralPath $link -PathType Leaf)){$found=$true;break}
        $proc.Refresh()
        if($proc.HasExited){Write-Host ("R60_INSTALLER_EXIT_EARLY code="+$proc.ExitCode);break}
    }
    Capture 'SETUP_POST_INSTALL'
    if(-not $found){
        Write-Host ("R60_INSTALL_FILE_PRESENCE gui="+(Test-Path $gui)+" icon="+(Test-Path $icon)+" shortcut="+(Test-Path $link))
        throw "Installer did not create GUI/icon/shortcut within bounded 45s"
    }
    $got=(Get-FileHash -Algorithm SHA256 -LiteralPath $icon).Hash.ToLowerInvariant()
    if($got -ne $expected){throw ("Installed icon SHA mismatch expected="+$expected+" got="+$got)}
    Write-Host ("R60_INSTALL_CANONICAL_ICON_SHA_PASS "+$got)
    $shell=New-Object -ComObject WScript.Shell
    $shortcut=$shell.CreateShortcut($link)
    $target=[IO.Path]::GetFullPath($shortcut.TargetPath)
    $expectedGui=[IO.Path]::GetFullPath($gui)
    if($target -ine $expectedGui){throw ("Shortcut target mismatch got="+$target+" expected="+$expectedGui)}
    Write-Host ("R60_INSTALL_SHORTCUT_TARGET_PASS "+$target)
    Write-Host ("R60_INSTALL_SHORTCUT_ICON "+$shortcut.IconLocation)
    if($shortcut.IconLocation -notmatch 'sutram.ico'){throw 'Shortcut does not reference canonical Sutram icon'}
    $uninstall='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram'
    if(-not(Test-Path $uninstall)){throw 'Expected per-user HKCU uninstall registry key absent'}
    Write-Host "R60_INSTALL_HKCU_PASS $uninstall"
    Write-Host ("R60_PER_USER_INSTALL_PASS gui_bytes="+(Get-Item $gui).Length+" icon_sha256="+$got+" shortcut="+$link)
    Write-Host 'R60_UAC_PROMPT_NOT_OBSERVED_IN_RUNNER (not a general Windows guarantee)'
}finally{
    if(-not $proc.HasExited) {
        [void]$proc.CloseMainWindow()
        if(-not $proc.WaitForExit(2000)){Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue}
    }
}
