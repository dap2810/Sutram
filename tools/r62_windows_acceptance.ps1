#requires -version 5.1
# Manual-only R62 Windows smoke acceptance. No network, elevation, or CI trigger.
[CmdletBinding()]
param(
 [ValidateSet('Prepare','Audit','Screenshot')][string]$Stage='Prepare',
 [string]$ResultsDir='',
 [string]$LegacyCompiler='',
 [switch]$CaptureGui
)
$ErrorActionPreference='Stop'
Set-StrictMode -Version 2.0
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
if (-not $ResultsDir) { $ResultsDir=Join-Path $env:TEMP 'Sutram-R62-Windows-Acceptance' }
New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
$ResultsDir=(Resolve-Path -LiteralPath $ResultsDir).Path
if (-not [Environment]::Is64BitOperatingSystem -or -not [Environment]::Is64BitProcess) { throw '64-bit Windows/PowerShell required.' }
$principal=[Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
if ($principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Use standard-user PowerShell; do not elevate.' }
function Hash([string]$file) {
 if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Missing file: $file" }
 return (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
}
$expectedIcon='b48aeb52516433c3cce51ffe436fa04355cb938aa0b5188c60fe7c02f2923ec1'
if ((Hash (Join-Path $root 'icons\sutram.ico')) -ne $expectedIcon) { throw 'Canonical source icon hash differs.' }
$sample=Join-Path $ResultsDir 'R62_COLOUR_FIXTURE.sm'
$sampleText=@'
# GREY comment
mukhya()
    vitti value = 123
    yadi (value > 100) {
        likha("R62_SHELL_AND_RUN_OK\n")
    }
'@
[IO.File]::WriteAllText($sample,$sampleText + [Environment]::NewLine,([Text.UTF8Encoding]::new($false)))
function Run-Bounded([string]$exe,[string]$arguments,[string]$tag,[string]$watched='') {
 $out=Join-Path $ResultsDir ($tag+'.stdout.txt'); $err=Join-Path $ResultsDir ($tag+'.stderr.txt')
 $start=@{FilePath=$exe; PassThru=$true; WorkingDirectory=$root; NoNewWindow=$true; RedirectStandardOutput=$out; RedirectStandardError=$err}
 if ($arguments) { $start.ArgumentList=$arguments }
 $p=Start-Process @start
 $sw=[Diagnostics.Stopwatch]::StartNew(); $oversize=$false
 while (-not $p.HasExited -and $sw.ElapsedMilliseconds -lt 12000) {
   if ($watched -and (Test-Path -LiteralPath $watched -PathType Leaf) -and (Get-Item -LiteralPath $watched).Length -gt 65536) { $oversize=$true; break }
   Start-Sleep -Milliseconds 80; $p.Refresh()
 }
 $timed=(-not $p.HasExited)
 if ($timed) { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue; [void]$p.WaitForExit(3000) }
 $sw.Stop(); $code=if ($timed) {-1} else {$p.ExitCode}
 $text=if (Test-Path -LiteralPath $out) {[IO.File]::ReadAllText($out)} else {''}
 Write-Host ("R62_NATIVE tag={0} exit={1} timeout={2} oversize={3} ms={4} stdout={5}" -f $tag,$code,$timed,$oversize,$sw.ElapsedMilliseconds,($text.Trim() -replace "[\r\n]+",' | '))
 if ($code -ne 0 -or $oversize -or $timed) { throw "R62 $tag failed; inspect $out and $err" }
 return $text
}
if ($Stage -eq 'Screenshot') {
 if (-not $CaptureGui) { throw 'Open the fixture in the GUI, then rerun with -CaptureGui.' }
 Add-Type -AssemblyName System.Drawing
 Add-Type -AssemblyName System.Windows.Forms
 $r=[Windows.Forms.Screen]::PrimaryScreen.Bounds
 $bmp=[Drawing.Bitmap]::new($r.Width,$r.Height)
 $g=[Drawing.Graphics]::FromImage($bmp)
 try { $g.CopyFromScreen($r.Location,[Drawing.Point]::Empty,$r.Size)
       $bmp.Save((Join-Path $ResultsDir 'GUI_REVIEW_REQUIRED.png'),[Drawing.Imaging.ImageFormat]::Png) }
 finally { $g.Dispose(); $bmp.Dispose() }
 Write-Host 'R62_SCREENSHOT_CAPTURED; MUST visually review orange/teal/green/purple/grey, menu and shell. Screenshot is not acceptance by itself.'
 exit 0
}
$cli=Join-Path $root 'win\sutram.exe'
$gui=Join-Path $root 'sutram-ide-gui.exe'
$setup=Join-Path $root 'windows\native-installer\output\Sutram-Setup-0.1.0-native-x64.exe'
$installed=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
if ($Stage -eq 'Prepare') {
 $diag=Join-Path $root 'tools\r61_windows_compiler_diagnostics.ps1'
 $diagArgs=@('-ResultsDir',(Join-Path $ResultsDir 'r61-native'))
 if ($LegacyCompiler) { $diagArgs+=@('-LegacyCompiler',$LegacyCompiler) }
 & $diag @diagArgs
 if (-not $?) { throw 'R61 CLI diagnostics did not complete.' }
 $nasm=(Get-Command nasm.exe -ErrorAction Stop).Source
 $ld=(Get-Command ld.exe -ErrorAction Stop).Source
 $obj=Join-Path $ResultsDir 'sutram-r62.obj'
 Push-Location $root
 try {
   & $nasm -f win64 -dWINDOWS -I. 'src\sutram_compiler.asm' -o $obj
   if ($LASTEXITCODE -ne 0) { throw 'NASM assembly failed.' }
   New-Item -Path (Join-Path $root 'win') -ItemType Directory -Force | Out-Null
   & $ld -mi386pep --entry=_start -o $cli $obj
   if ($LASTEXITCODE -ne 0) { throw 'PE link failed.' }
 } finally { Pop-Location }
 & (Join-Path $root 'windows\gui\build-gui.ps1')
 if (-not $?) { throw 'GUI build failed.' }
 & (Join-Path $root 'windows\native-installer\build-installer.ps1')
 if (-not $?) { throw 'Installer build failed.' }
 [void](Run-Bounded $setup '--self-test' 'installer-self-test')
 if ((Hash (Join-Path $root 'windows\native-installer\assets\sutram.ico')) -ne $expectedIcon) { throw 'Installer icon incorrect.' }
 $manifest=@('R62_PREPARE_PASS',('compiler_sha256='+(Hash $cli)),('gui_sha256='+(Hash $gui)),('setup_sha256='+(Hash $setup)),('icon_sha256='+$expectedIcon),('source_sha256='+(Hash (Join-Path $root 'src\sutram_compiler.asm'))))
 [IO.File]::WriteAllLines((Join-Path $ResultsDir 'build-manifest.txt'),$manifest,([Text.UTF8Encoding]::new($false)))
 $manifest | ForEach-Object { Write-Host $_ }
 Write-Host "NEXT: run installer as standard user: $setup"
 Write-Host 'After graphical wizard finishes, rerun this script with -Stage Audit.'
 exit 0
}
if ($Stage -eq 'Audit') {
 if (-not (Test-Path -LiteralPath (Join-Path $installed '.sutram-install') -PathType Leaf)) { throw 'Installed marker absent.' }
 $reg=Get-ItemProperty -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram' -ErrorAction Stop
 if (-not [string]::Equals([IO.Path]::GetFullPath([string]$reg.InstallLocation).TrimEnd('\'),[IO.Path]::GetFullPath($installed).TrimEnd('\'),[StringComparison]::OrdinalIgnoreCase)) { throw 'HKCU uninstall path invalid.' }
 $lnk=Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram\Sutram IDE.lnk'
 if (-not (Test-Path -LiteralPath $lnk -PathType Leaf)) { throw 'Start Menu link missing.' }
 $shell=New-Object -ComObject WScript.Shell; $sc=$shell.CreateShortcut($lnk)
 $destGui=Join-Path $installed 'sutram-ide-gui.exe'; $icon=Join-Path $installed 'assets\sutram.ico'
 if (-not [string]::Equals($sc.TargetPath,$destGui,[StringComparison]::OrdinalIgnoreCase)) { throw "Shortcut target mismatch: $($sc.TargetPath)" }
 if (-not $sc.IconLocation.StartsWith($icon,[StringComparison]::OrdinalIgnoreCase)) { throw "Shortcut icon path mismatch: $($sc.IconLocation)" }
 if ((Hash $icon) -ne $expectedIcon) { throw 'Installed icon SHA wrong.' }
 $destCli=Join-Path $installed 'bin\sutram.exe'
 if ((Hash $destCli) -ne (Hash $cli)) { throw 'Packaged/installed compiler does not match tested current compiler.' }
 $log=Join-Path $installed 'install.log'
 if (-not (Test-Path -LiteralPath $log -PathType Leaf)) { throw 'Successful installer log missing; inspect original wizard failure log under TEMP\Sutram-Setup-*.' }
 $actualLog=[IO.File]::ReadAllText($log)
 Copy-Item -LiteralPath $log -Destination (Join-Path $ResultsDir 'observed-install.log') -Force
 if ($actualLog -notmatch 'Installation complete:' -or $actualLog -match 'ERROR:') { throw 'Installer log does not prove successful completion.' }
 Write-Host "R62_INSTALL_LOG_INSPECTED $log"
 $generated=Join-Path $ResultsDir 'r62_installed_hello.exe'
 [void](Run-Bounded $destCli ('"'+$sample+'" "'+$generated+'"') 'installed-compile' $generated)
 if ((Get-Item -LiteralPath $generated).Length -gt 65536) { throw 'Oversized generated PE.' }
 $stdout=Run-Bounded $generated '' 'installed-program'
 if ($stdout.Trim() -ne 'R62_SHELL_AND_RUN_OK') { throw "Wrong native stdout: $stdout" }
 $p=Start-Process -FilePath $destGui -WorkingDirectory $installed -PassThru
 $seen=$false
 for ($i=0;$i -lt 40;$i++) {
   Start-Sleep -Milliseconds 250; $p.Refresh()
   if ($p.HasExited) { throw "Installed GUI exited: $($p.ExitCode)" }
   if ($p.MainWindowHandle -ne [IntPtr]::Zero) { $seen=$true; break }
 }
 if (-not $seen) { throw 'Installed GUI failed to create a visible main window.' }
 Write-Host 'R62_AUDIT_PASS: HKCU, real install log, shortcut, exact canonical ICO, byte-matched compiler, native stdout, GUI window.'
 Write-Host "MANUAL: in installed GUI File > Open $sample; test editor Run and >>> shell, inspect five colours; capture via -Stage Screenshot -CaptureGui."
}