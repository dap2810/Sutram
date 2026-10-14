#requires -version 5.1
# Run only on a REAL Windows host. Interactive GUI checks are not substitutes for user acceptance.
# No admin/UAC requests, policy changes, or installer actions in this smoke probe.
[CmdletBinding()]
param([string]$ResultsDir = "", [switch]$RequireVisibleDesktop)
$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $ResultsDir) { $ResultsDir=Join-Path $env:TEMP 'sutram-r60-runtime' }
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
$log=Join-Path $ResultsDir 'R60_WINDOWS_OBSERVED.txt'
$lines=New-Object System.Collections.Generic.List[string]
function Report([string]$Message) {
    Write-Host $Message
    $lines.Add($Message)
}
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms
Add-Type -TypeDefinition @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public static class SutramR60Native {
 [DllImport("user32.dll")] public static extern IntPtr GetMenu(IntPtr hwnd);
 [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr hwnd, int id);
 [DllImport("user32.dll")] public static extern int GetMenuItemCount(IntPtr hMenu);
 [DllImport("user32.dll", EntryPoint="GetMenuStringW", CharSet=CharSet.Unicode)]
 public static extern int GetMenuString(IntPtr hMenu, uint index, StringBuilder text, int capacity, uint flags);
}
'@
$setup=Join-Path $root 'Sarvam-to-ChatGPT\Sutram-Setup.exe'
$zip=Join-Path $root 'Sarvam-to-ChatGPT\sutram-windows-idle-test.zip'
$ico=Join-Path $root 'icons\sutram.ico'
Report ("R60_HOST os="+[Environment]::OSVersion.VersionString+" 64bit="+[Environment]::Is64BitOperatingSystem+" username="+$env:USERNAME)
foreach($f in @($setup,$zip,$ico)) {
    if(-not (Test-Path -LiteralPath $f -PathType Leaf)) { throw "Missing R60 source artifact: $f" }
    $item=Get-Item -LiteralPath $f
    Report ("R60_ARTIFACT "+$item.Name+" bytes="+$item.Length+" sha256="+(Get-FileHash -Algorithm SHA256 -LiteralPath $f).Hash.ToLowerInvariant())
}
$extracted=Join-Path $ResultsDir 'idle-test'
if(Test-Path $extracted){Remove-Item $extracted -Recurse -Force}
Expand-Archive -LiteralPath $zip -DestinationPath $extracted -Force
# Prefer and execute the GUI we JUST compiled from this feature branch, not
# the older prebuilt binary. Retain compiler/lang/assets from the supplied ZIP.
$sourceGui=Join-Path $root 'sutram-ide-gui.exe'
if(Test-Path $sourceGui -PathType Leaf) {
    Copy-Item -LiteralPath $sourceGui -Destination (Join-Path $extracted 'sutram-ide-gui.exe') -Force
    Report ("R60_SOURCE_BUILT_GUI_TESTED sha256="+(Get-FileHash -Algorithm SHA256 -LiteralPath $sourceGui).Hash.ToLowerInvariant())
} else {
    Report 'R60_SOURCE_BUILD_UNVERIFIED: using original uploaded GUI EXE from archive'
}
$allExes=@(Get-ChildItem -LiteralPath $extracted -File -Recurse -Filter '*.exe')
Report ("R60_EXTRACTED_EXE_COUNT "+$allExes.Count)
foreach($exe in $allExes) {
    Report ("R60_EXTRACTED_EXE "+$exe.FullName.Substring($extracted.Length).TrimStart('\')+" bytes="+$exe.Length)
}
$gui=@($allExes | Where-Object {$_.Name -match 'ide|gui'} | Select-Object -First 1)
if($gui.Count -eq 0) {
    Report 'R60_GUI_LAUNCH UNVERIFIED: No GUI EXE found inside test zip.'
    if($RequireVisibleDesktop){ throw 'Expected GUI executable was not found in the R60 archive.' }
}
function Capture-Desktop([string]$Name) {
    try {
        $screen=[System.Windows.Forms.Screen]::PrimaryScreen
        if(-not $screen){throw 'No primary desktop screen'}
        $b=$screen.Bounds
        if($b.Width -le 0 -or $b.Height -le 0){throw 'Invalid desktop dimensions'}
        $bitmap=New-Object System.Drawing.Bitmap($b.Width,$b.Height)
        $graphics=[System.Drawing.Graphics]::FromImage($bitmap)
        try {
            $graphics.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size)
            $file=Join-Path $ResultsDir ($Name+'.png')
            $bitmap.Save($file,[System.Drawing.Imaging.ImageFormat]::Png)
            Report ("R60_REAL_SCREENSHOT "+$Name+" path="+$file+" width="+$b.Width+" height="+$b.Height)
        } finally { $graphics.Dispose();$bitmap.Dispose() }
        return $true
    } catch {
        Report ("R60_SCREENSHOT_UNVERIFIED "+$Name+" reason="+$_.Exception.Message)
        return $false
    }
}
function Open-Window([string]$Path,[string]$Name,[string]$WorkingDirectory) {
    Report ("R60_START "+$Name+" exe="+$Path)
    $proc=Start-Process -FilePath $Path -WorkingDirectory $WorkingDirectory -PassThru
    try {
        $found=[IntPtr]::Zero
        for($n=0;$n -lt 50;$n++) {
            Start-Sleep -Milliseconds 200
            $proc.Refresh()
            if($proc.HasExited) { throw ($Name+" exited code="+$proc.ExitCode) }
            if($proc.MainWindowHandle -ne [IntPtr]::Zero){$found=$proc.MainWindowHandle;break}
        }
        if($found -eq [IntPtr]::Zero){throw ($Name+" produced no top-level window after 10 seconds")}
        Report ("R60_REAL_WINDOW "+$Name+" hwnd="+$found.ToInt64())
        if($Name -eq 'IDE') {
            $menu=[SutramR60Native]::GetMenu($found)
            if($menu -eq [IntPtr]::Zero){throw 'IDE has no native menu attached to the main window'}
            $count=[SutramR60Native]::GetMenuItemCount($menu)
            Report ("R60_REAL_MENU_COUNT "+$count)
            if($count -ne 7){throw ("Expected seven top-level menu items, got "+$count)}
            $expected=@('File','Edit','Shell','Debug','Options','Window','Help')
            for($i=0;$i -lt 7;$i++){
                $buf=New-Object System.Text.StringBuilder 256
                [void][SutramR60Native]::GetMenuString($menu,[uint32]$i,$buf,256,0x400)
                $menuLabel=$buf.ToString().Replace('&','')
                Report ("R60_REAL_MENU "+$i+" "+$menuLabel)
                if($menuLabel -ne $expected[$i]){throw ("Menu mismatch "+$i+": "+$menuLabel)}
            }
            Report 'R60_MENU_7_OF_7_CONFIRMED via Windows user32 GetMenu/GetMenuStringW'
            foreach($id in @(101,102,103,104,105,106,201,202,203,204,205)) {
                $child=[SutramR60Native]::GetDlgItem($found,[int]$id)
                Report ("R60_NATIVE_CHILD id="+$id+" hwnd="+$child.ToInt64())
            }
        }
        [void](Capture-Desktop $Name)
    } finally {
        if(-not $proc.HasExited) {
            [void]$proc.CloseMainWindow()
            if(-not $proc.WaitForExit(2000)){Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue}
        }
    }
}
$guiValid=$false;$setupValid=$false
try {
    if($gui.Count -ne 0) {
        Open-Window -Path $gui[0].FullName -Name 'IDE' -WorkingDirectory $gui[0].DirectoryName
        $guiValid=$true
    }
} catch {Report ("R60_IDE_UNVERIFIED_OR_FAILED "+$_.Exception.Message)}
try {
    Open-Window -Path $setup -Name 'SETUP_WIZARD' -WorkingDirectory (Split-Path $setup -Parent)
    $setupValid=$true
} catch {Report ("R60_SETUP_UNVERIFIED_OR_FAILED "+$_.Exception.Message)}
if($guiValid -and $setupValid){Report 'R60_WINDOWS_RUNTIME_PROBE two top-level native windows launched'} 
else {Report 'R60_WINDOWS_RUNTIME_PROBE PARTIAL: do not claim successful desktop acceptance'}
Report 'R60_INSTALLATION_UNVERIFIED: no installer buttons clicked, no UAC or Start Menu verification'
Report 'R60_LEXER_COLORS_UNVERIFIED: screenshot requires manual pixel/visual acceptance'
Report 'R60_SHELL_UNVERIFIED: interactive >>> source submission not exercised'
[IO.File]::WriteAllLines($log,$lines.ToArray())
if($RequireVisibleDesktop -and (-not $guiValid -or -not $setupValid)){throw 'Required Windows GUI runtime checks did not pass.'}
