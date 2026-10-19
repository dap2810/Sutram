<#
.SYNOPSIS
  Sutram Windows acceptance gate (ROUND-06). One run, one machine-readable log.

.DESCRIPTION
  Run it as the user who will use Sutram, from a normal (NOT elevated) PowerShell window:

      powershell -NoProfile -ExecutionPolicy Bypass -File tools\accept-windows.ps1

  Bypass applies to this one process only; it does not change machine policy.

  The log binds every result to the SHA-256 of the binaries it tested, records the Windows build and
  whether the process was elevated, and gives each check PASS / FAIL / NOT-RUN with the exact command
  and its raw output. A check that cannot be automated is printed NOT-RUN with the reason; nothing is
  silently omitted. Under Wine every check is labelled "Wine" and the verdict says it is not Windows
  acceptance.

  What it does to the machine: installs Sutram for the current user only (no administrator rights,
  default folder under %LOCALAPPDATA%\Programs), launches the installed IDE, compiles one example,
  closes the IDE, then runs the installed uninstaller. It refuses to install over an existing Sutram
  installation (those checks become NOT-RUN). It never touches HKLM, never elevates, and only sends
  window messages to the processes it started itself. -Keyboard additionally uses SendInput (real
  keystrokes) for the Shift+Tab check, which needs the IDE in the foreground; it is off by default.

  Exit code: 0 when no required check FAILed (NOT-RUN is not a pass: see "verdict"), 1 otherwise.
  Works with Windows PowerShell 5.1 and PowerShell 7. This file is ASCII on purpose (5.1 reads
  BOM-less files as ANSI); Devanagari is built from code points.
#>
[CmdletBinding()]
param(
    [string]$Root = (Split-Path -Parent $PSScriptRoot),
    [string]$Setup = '',
    [string]$OutDir = '',
    [switch]$KeepInstalled,
    [switch]$Keyboard,
    [int]$InstallTimeoutSec = 300
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$Root = [IO.Path]::GetFullPath($Root)
if (-not $Setup) { $Setup = Join-Path $Root 'Sutram-Setup.exe' }
if (-not $OutDir) { $OutDir = Join-Path $Root ('build\windows\accept-' + [DateTime]::Now.ToString('yyyyMMdd-HHmmss')) }
[void](New-Item -ItemType Directory -Force -Path $OutDir)
$OutDir = [IO.Path]::GetFullPath($OutDir)

# ------------------------------------------------------------------------------------------------
# Native helpers. C# 5 syntax so Windows PowerShell 5.1 (CodeDom) compiles it.
# ------------------------------------------------------------------------------------------------
$native = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class SutramAccept {
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr parent, EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClassNameW(IntPtr h, StringBuilder b, int n);
    [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr h, int id);
    [DllImport("user32.dll")] public static extern int GetDlgCtrlID(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsWindowEnabled(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool PostMessageW(IntPtr h, uint m, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern IntPtr GetMenu(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr GetSubMenu(IntPtr m, int pos);
    [DllImport("user32.dll")] public static extern int GetMenuItemCount(IntPtr m);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetMenuStringW(IntPtr m, uint id, StringBuilder b, int n, uint flags);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern IntPtr SendMessageTimeoutW(IntPtr h, uint m, IntPtr w, StringBuilder l, uint f, uint t, out IntPtr r);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern IntPtr SendMessageTimeoutW(IntPtr h, uint m, IntPtr w, string l, uint f, uint t, out IntPtr r);
    [DllImport("user32.dll")] static extern IntPtr SendMessageTimeoutW(IntPtr h, uint m, IntPtr w, IntPtr l, uint f, uint t, out IntPtr r);
    [DllImport("user32.dll", SetLastError=true)] static extern uint SendInput(uint n, INPUT[] inputs, int size);
    [DllImport("kernel32.dll", SetLastError=true)] static extern IntPtr OpenProcess(uint access, bool inherit, uint pid);
    [DllImport("kernel32.dll")] static extern bool CloseHandle(IntPtr h);
    [DllImport("kernel32.dll")] static extern IntPtr GetCurrentProcess();
    [DllImport("advapi32.dll", SetLastError=true)] static extern bool OpenProcessToken(IntPtr p, uint access, out IntPtr t);
    [DllImport("advapi32.dll", SetLastError=true)] static extern bool GetTokenInformation(IntPtr t, int cls, IntPtr buf, int len, out int ret);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)] struct KEYBDINPUT { public ushort vk; public ushort scan; public uint flags; public uint time; public IntPtr extra; }
    [StructLayout(LayoutKind.Explicit)] struct INPUT { [FieldOffset(0)] public uint type; [FieldOffset(8)] public KEYBDINPUT ki; [FieldOffset(8)] public long pad0; [FieldOffset(16)] public long pad1; [FieldOffset(24)] public long pad2; [FieldOffset(32)] public long pad3; }   // 40 bytes on x64, as SendInput requires

    public static string ClassOf(IntPtr h) { StringBuilder b = new StringBuilder(256); GetClassNameW(h, b, 256); return b.ToString(); }
    public static uint PidOf(IntPtr h) { uint p; GetWindowThreadProcessId(h, out p); return p; }

    // Top-level windows of one process, optionally of one class.
    public static IntPtr[] WindowsOf(uint pid, string cls) {
        List<IntPtr> found = new List<IntPtr>();
        EnumWindows(delegate(IntPtr h, IntPtr l) {
            if (PidOf(h) == pid && (cls == null || ClassOf(h) == cls)) found.Add(h);
            return true;
        }, IntPtr.Zero);
        return found.ToArray();
    }
    public static IntPtr[] Children(IntPtr parent) {
        List<IntPtr> found = new List<IntPtr>();
        EnumChildWindows(parent, delegate(IntPtr h, IntPtr l) { found.Add(h); return true; }, IntPtr.Zero);
        return found.ToArray();
    }
    public static long Send(IntPtr h, uint m, long w, long l) {
        IntPtr r;
        if (SendMessageTimeoutW(h, m, new IntPtr(w), new IntPtr(l), 2, 30000, out r) == IntPtr.Zero)
            throw new Exception("SendMessageTimeout failed for message 0x" + m.ToString("X"));
        return r.ToInt64();
    }
    public static string Text(IntPtr h) {
        IntPtr r;
        StringBuilder b = new StringBuilder(65536);
        if (SendMessageTimeoutW(h, 0x000D, new IntPtr(65536), b, 2, 30000, out r) == IntPtr.Zero)
            throw new Exception("WM_GETTEXT timed out");
        return b.ToString();
    }
    public static void SetText(IntPtr h, string s) {
        IntPtr r;
        if (SendMessageTimeoutW(h, 0x000C, IntPtr.Zero, s, 2, 30000, out r) == IntPtr.Zero)
            throw new Exception("WM_SETTEXT timed out");
    }
    public static string MenuString(IntPtr m, int pos) {
        StringBuilder b = new StringBuilder(256);
        GetMenuStringW(m, (uint)pos, b, 256, 0x400);  // MF_BYPOSITION
        return b.ToString();
    }
    // TokenElevationType: 1 default (UAC off or standard user), 2 full (elevated), 3 limited.
    // TokenElevation: 1 when the token is elevated.
    static int[] TokenInfo(IntPtr process) {
        IntPtr tok; int[] res = new int[] { -1, -1 };
        if (!OpenProcessToken(process, 0x0008, out tok)) return res;
        try {
            IntPtr buf = Marshal.AllocHGlobal(4); int ret;
            try {
                if (GetTokenInformation(tok, 18, buf, 4, out ret)) res[0] = Marshal.ReadInt32(buf);
                if (GetTokenInformation(tok, 20, buf, 4, out ret)) res[1] = Marshal.ReadInt32(buf);
            } finally { Marshal.FreeHGlobal(buf); }
        } finally { CloseHandle(tok); }
        return res;
    }
    public static int[] SelfElevation() { return TokenInfo(GetCurrentProcess()); }
    public static int[] ProcessElevation(uint pid) {
        IntPtr p = OpenProcess(0x1000, false, pid);   // PROCESS_QUERY_LIMITED_INFORMATION
        if (p == IntPtr.Zero) return new int[] { -2, -2 };
        try { return TokenInfo(p); } finally { CloseHandle(p); }
    }
    [DllImport("user32.dll")] static extern IntPtr GetDC(IntPtr h);
    [DllImport("user32.dll")] static extern IntPtr GetWindowDC(IntPtr h);
    [DllImport("gdi32.dll")] static extern bool BitBlt(IntPtr d, int x, int y, int w, int h, IntPtr s, int sx, int sy, uint rop);
    [DllImport("user32.dll")] static extern int ReleaseDC(IntPtr h, IntPtr dc);
    [DllImport("gdi32.dll")] static extern IntPtr CreateCompatibleDC(IntPtr dc);
    [DllImport("gdi32.dll")] static extern bool DeleteDC(IntPtr dc);
    [DllImport("gdi32.dll")] static extern IntPtr SelectObject(IntPtr dc, IntPtr o);
    [DllImport("gdi32.dll")] static extern bool DeleteObject(IntPtr o);
    [DllImport("gdi32.dll")] static extern IntPtr CreateDIBSection(IntPtr dc, byte[] bmi, uint usage, out IntPtr bits, IntPtr sec, uint off);
    // PrintWindow into a 32-bit DIB and write a .bmp (no System.Drawing: it does not compile the same
    // way in 5.1 and 7). The script converts it to .png afterwards when it can.
    public static bool Capture(IntPtr h, string path) {
        RECT r; if (!GetWindowRect(h, out r)) return false;
        int w = r.Right - r.Left, ht = r.Bottom - r.Top; if (w <= 0 || ht <= 0 || w > 8000 || ht > 8000) return false;
        byte[] bmi = new byte[40];
        BitConverter.GetBytes(40).CopyTo(bmi, 0); BitConverter.GetBytes(w).CopyTo(bmi, 4); BitConverter.GetBytes(-ht).CopyTo(bmi, 8);
        BitConverter.GetBytes((short)1).CopyTo(bmi, 12); BitConverter.GetBytes((short)32).CopyTo(bmi, 14);
        IntPtr screen = GetDC(IntPtr.Zero), dc = CreateCompatibleDC(screen), bits;
        IntPtr dib = CreateDIBSection(dc, bmi, 0, out bits, IntPtr.Zero, 0);
        ReleaseDC(IntPtr.Zero, screen);
        if (dib == IntPtr.Zero) { DeleteDC(dc); return false; }
        IntPtr old = SelectObject(dc, dib);
        try {
            int size = w * ht * 4; byte[] px = new byte[size];
            // PW_RENDERFULLCONTENT first; then plain PrintWindow; then a copy of the window's own DC
            // (Wine renders the first two black). All three read only this window.
            bool got = false;
            for (int attempt = 0; attempt < 3 && !got; attempt++) {
                bool ok;
                if (attempt < 2) ok = PrintWindow(h, dc, attempt == 0 ? 2u : 0u);
                else { IntPtr wdc = GetWindowDC(h); ok = BitBlt(dc, 0, 0, w, ht, wdc, 0, 0, 0x00CC0020); ReleaseDC(h, wdc); }
                if (!ok) continue;
                Marshal.Copy(bits, px, 0, size);
                for (int i = 0; i < size; i += 4) { if (px[i] != 0 || px[i + 1] != 0 || px[i + 2] != 0) { got = true; break; } }
            }
            if (!got) return false;
            using (System.IO.FileStream f = System.IO.File.Create(path)) {
                byte[] fh = new byte[14]; fh[0] = 0x42; fh[1] = 0x4D;
                BitConverter.GetBytes(54 + size).CopyTo(fh, 2); BitConverter.GetBytes(54).CopyTo(fh, 10);
                f.Write(fh, 0, 14); f.Write(bmi, 0, 40); f.Write(px, 0, size);
            }
            return true;
        } finally { SelectObject(dc, old); DeleteObject(dib); DeleteDC(dc); }
    }
    // Real Shift+Tab through the input queue (only with -Keyboard).
    public static uint ShiftTab() {
        INPUT[] k = new INPUT[4];
        ushort[] vk = new ushort[] { 0x10, 0x09, 0x09, 0x10 };
        uint[] fl = new uint[] { 0, 0, 2, 2 };
        for (int i = 0; i < 4; i++) { k[i].type = 1; k[i].ki.vk = vk[i]; k[i].ki.flags = fl[i]; }
        return SendInput(4, k, Marshal.SizeOf(typeof(INPUT)));
    }
}
'@
Add-Type -TypeDefinition $native

# ------------------------------------------------------------------------------------------------
# Log model
# ------------------------------------------------------------------------------------------------
function Test-Wine {
    foreach ($k in @('HKLM:\Software\Wine','HKCU:\Software\Wine')) { if (Test-Path -LiteralPath $k) { return $true } }
    return $false
}
$isWine = Test-Wine
$envName = 'Windows'; if ($isWine) { $envName = 'Wine' }
$checks = New-Object System.Collections.ArrayList
$artefacts = New-Object System.Collections.ArrayList

function Add-Check([string]$Id, [string]$Status, [string]$Command, [string]$Output, [string]$Detail, [bool]$Required = $true) {
    if ($Output -and $Output.Length -gt 20000) { $Output = $Output.Substring(0,20000) + "`n[... truncated at 20000 characters]" }
    $row = [ordered]@{
        id = $Id; status = $Status; required = $Required; environment = $envName
        command = $Command; output = $Output; detail = $Detail
        time = [DateTime]::Now.ToString('yyyy-MM-ddTHH:mm:ss')
    }
    [void]$checks.Add($row)
    Write-Host ('{0,-8} {1,-34} {2}' -f $Status, $Id, $Detail)
}
function NotRun([string]$Id, [string]$Why, [bool]$Required = $true) { Add-Check $Id 'NOT-RUN' '' '' $Why $Required }
function Get-Sha256([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}
function Add-Artefact([string]$Role, [string]$Path) {
    $h = Get-Sha256 $Path
    $len = $null; if ($h) { $len = (Get-Item -LiteralPath $Path).Length }
    [void]$artefacts.Add([ordered]@{ role = $Role; path = $Path; sha256 = $h; bytes = $len })
    if ($h) { Write-Host ('SHA256   {0}  {1}  ({2})' -f $h, $Role, $Path) } else { Write-Host ('SHA256   (missing)  {0}  ({1})' -f $Role, $Path) }
    return $h
}
function Wait-Until([scriptblock]$Cond, [int]$Ms) {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    while ($sw.ElapsedMilliseconds -lt $Ms) { $v = & $Cond; if ($v) { return $v }; Start-Sleep -Milliseconds 100 }
    return $null
}
function Run-Exe([string]$Exe, [string]$Arguments, [string]$Cwd, [int]$TimeoutMs = 30000) {
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo.FileName = $Exe; $p.StartInfo.Arguments = $Arguments; $p.StartInfo.WorkingDirectory = $Cwd
    $p.StartInfo.UseShellExecute = $false; $p.StartInfo.CreateNoWindow = $true
    $p.StartInfo.RedirectStandardOutput = $true; $p.StartInfo.RedirectStandardError = $true
    $p.StartInfo.StandardOutputEncoding = [Text.Encoding]::UTF8; $p.StartInfo.StandardErrorEncoding = [Text.Encoding]::UTF8
    [void]$p.Start()
    $o = $p.StandardOutput.ReadToEndAsync(); $e = $p.StandardError.ReadToEndAsync()
    if (-not $p.WaitForExit($TimeoutMs)) { try { $p.Kill() } catch {}; return @{ exit = 'TIMEOUT'; out = $o.Result + $e.Result } }
    return @{ exit = $p.ExitCode; out = $o.Result + $e.Result }
}
function Find-Dialog([int]$ProcessId) {
    $d = [SutramAccept]::WindowsOf([uint32]$ProcessId, '#32770') | Where-Object { [SutramAccept]::IsWindowVisible($_) } | Select-Object -First 1
    return $d
}
function Dialog-Text([IntPtr]$Dlg) {
    $parts = @(); foreach ($c in [SutramAccept]::Children($Dlg)) { if ([SutramAccept]::ClassOf($c) -eq 'Static') { $t = [SutramAccept]::Text($c); if ($t) { $parts += $t } } }
    return ($parts -join ' | ')
}
function Click([IntPtr]$Parent, [int]$Id) {
    # BM_CLICK, posted (the click may open a modal box). Returns $false when the control does not exist.
    $b = [SutramAccept]::GetDlgItem($Parent, $Id)
    if ($b -eq [IntPtr]::Zero) { return $false }
    return [SutramAccept]::PostMessageW($b, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero)
}
function Shot([IntPtr]$H, [string]$Name) {
    # Captures only a window this script started (PrintWindow), never the desktop.
    $bmp = Join-Path $OutDir ([IO.Path]::ChangeExtension($Name, '.bmp'))
    try { if (-not [SutramAccept]::Capture($H, $bmp)) { return $null } } catch { return $null }
    try {
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop
        $img = [System.Drawing.Image]::FromFile($bmp)
        try { $img.Save((Join-Path $OutDir $Name), [System.Drawing.Imaging.ImageFormat]::Png) } finally { $img.Dispose() }
        Remove-Item -LiteralPath $bmp -Force
        return $Name
    } catch { return [IO.Path]::GetFileName($bmp) }
}
function Text-Of([string[]]$CodePoints) { return -join ($CodePoints | ForEach-Object { [char][Convert]::ToInt32($_,16) }) }
$yogah15 = (Text-Of @('092F','094B','0917','0903')) + ' = 15'      # the expected Devanagari output

# ------------------------------------------------------------------------------------------------
# Environment record
# ------------------------------------------------------------------------------------------------
$cv = $null; try { $cv = Get-ItemProperty -LiteralPath 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' } catch {}
function CvValue([string]$Name) { if ($cv -and ($cv.PSObject.Properties.Name -contains $Name)) { return [string]$cv.$Name } return $null }
$elev = [SutramAccept]::SelfElevation()
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdminRole = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$elevated = ($elev[1] -eq 1) -or $isAdminRole
$commit = $null
try { $g = Run-Exe 'git' ('-C "' + $Root + '" rev-parse HEAD') $Root 5000; if ($g.exit -eq 0) { $commit = $g.out.Trim() } } catch {}
if (-not $commit) {   # no git on the machine: read .git directly
    try {
        $head = (Get-Content -LiteralPath (Join-Path $Root '.git\HEAD') -TotalCount 1).Trim()
        if ($head -like 'ref: *') { $ref = Join-Path $Root ('.git\' + $head.Substring(5).Replace('/','\')); if (Test-Path -LiteralPath $ref) { $commit = (Get-Content -LiteralPath $ref -TotalCount 1).Trim() } }
        else { $commit = $head }
    } catch {}
}
$wineVersion = $null; if ($isWine) { try { $wineVersion = (Get-ItemProperty 'HKLM:\Software\Wine' -ErrorAction Stop).PSObject.Properties | Where-Object { $_.Name -like '*ersion*' } | ForEach-Object { [string]$_.Value } | Select-Object -First 1 } catch {} }
$environment = [ordered]@{
    environment = $envName
    wine = $isWine; wine_version = $wineVersion
    windows_product = CvValue 'ProductName'; windows_display_version = CvValue 'DisplayVersion'
    windows_build = CvValue 'CurrentBuild'; windows_ubr = CvValue 'UBR'
    os_version = [Environment]::OSVersion.VersionString
    architecture = $env:PROCESSOR_ARCHITECTURE
    powershell = $PSVersionTable.PSVersion.ToString(); powershell_edition = [string]$PSVersionTable['PSEdition']
    elevated = $elevated; token_elevation_type = $elev[0]; token_elevated = $elev[1]; in_administrators_role = $isAdminRole
    script_sha256 = Get-Sha256 $PSCommandPath; repo_root = $Root; git_commit = $commit
    started = [DateTime]::Now.ToString('yyyy-MM-ddTHH:mm:sszzz')
}
Write-Host ('Sutram Windows acceptance  env={0}  build={1}.{2}  PS={3}  elevated={4}' -f $envName, $environment.windows_build, $environment.windows_ubr, $environment.powershell, $elevated)

$tokenTypes = @{ '1' = 'default'; '2' = 'full (elevated)'; '3' = 'limited (UAC-filtered)' }
if ($isWine) {
    # Wine has no UAC: every process runs with an administrator token, so elevation proves nothing here.
    Add-Check 'runner-not-elevated' 'NOT-RUN' 'GetTokenInformation(TokenElevation, TokenElevationType)' ('TokenElevationType=' + $elev[0] + ' TokenElevation=' + $elev[1] + ' AdministratorsRole=' + $isAdminRole) 'Wine has no UAC and reports every process as administrator; least privilege can only be shown on Windows'
    $elevated = $false
} elseif ($elevated) {
    Add-Check 'runner-not-elevated' 'FAIL' 'whoami /groups; GetTokenInformation(TokenElevation)' ('TokenElevationType=' + $elev[0] + ' TokenElevation=' + $elev[1] + ' AdministratorsRole=' + $isAdminRole) 'This run is elevated. Least privilege cannot be shown; rerun from a normal PowerShell window. Install checks are skipped.'
} else {
    Add-Check 'runner-not-elevated' 'PASS' 'GetTokenInformation(TokenElevation, TokenElevationType)' ('TokenElevationType=' + $elev[0] + ' (' + $tokenTypes[[string]$elev[0]] + ') TokenElevation=' + $elev[1] + ' AdministratorsRole=' + $isAdminRole) 'the acceptance process itself is not elevated'
}

# ------------------------------------------------------------------------------------------------
# Artefacts under test
# ------------------------------------------------------------------------------------------------
$hSetup = Add-Artefact 'setup' $Setup
foreach ($rel in @('win\sutram.exe','sutram.exe')) { if (Test-Path -LiteralPath (Join-Path $Root $rel)) { [void](Add-Artefact ('repo-compiler ' + $rel) (Join-Path $Root $rel)) } }
[void](Add-Artefact 'repo-ide sutram-ide-gui.exe' (Join-Path $Root 'sutram-ide-gui.exe'))
if (Test-Path -LiteralPath (Join-Path $Root 'Sutram-Setup.sha256')) {
    $declared = ((Get-Content -LiteralPath (Join-Path $Root 'Sutram-Setup.sha256') -TotalCount 1) -split '\s+')[0].ToLowerInvariant()
    if ($hSetup -and $declared -eq $hSetup) { Add-Check 'setup-hash-file' 'PASS' 'Get-FileHash Sutram-Setup.exe vs Sutram-Setup.sha256' $declared 'matches the committed hash file' }
    else { Add-Check 'setup-hash-file' 'FAIL' 'Get-FileHash Sutram-Setup.exe vs Sutram-Setup.sha256' ('declared=' + $declared + ' actual=' + $hSetup) 'the setup binary is not the one the hash file names' }
} else { NotRun 'setup-hash-file' 'no Sutram-Setup.sha256 next to the setup' $false }

# ------------------------------------------------------------------------------------------------
# Install
# ------------------------------------------------------------------------------------------------
$unKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram'
$installDir = $null; $installed = $false; $skipInstall = $null
if (-not $hSetup) { $skipInstall = 'setup binary missing: ' + $Setup }
elseif ($elevated) { $skipInstall = 'the acceptance process is elevated' }
elseif (Test-Path -LiteralPath $unKey) {
    $prev = (Get-ItemProperty -LiteralPath $unKey).InstallLocation
    $skipInstall = 'Sutram is already installed for this user (' + $prev + '). This gate does not install over or remove an existing copy; uninstall it first.'
}

if ($skipInstall) {
    foreach ($id in @('setup-self-test','install-no-elevation-prompt','install-wizard','install-footprint')) { NotRun $id $skipInstall }
} else {
    $r = Run-Exe $Setup '--self-test' $Root 20000
    if ($r.exit -eq 0) { Add-Check 'setup-self-test' 'PASS' ('"' + $Setup + '" --self-test') $r.out 'embedded SHA-256 self-test exit 0' }
    else { Add-Check 'setup-self-test' 'FAIL' ('"' + $Setup + '" --self-test') $r.out ('exit ' + $r.exit) }

    $tempBefore = @(Get-ChildItem -LiteralPath $env:TEMP -Directory -Filter 'STM*.tmp' -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
    $consentBefore = @(Get-Process -Name consent -ErrorAction SilentlyContinue).Count
    $cmd = 'Start-Process -FilePath "' + $Setup + '" (no RunAs verb)'
    try {
        $sp = Start-Process -FilePath $Setup -WorkingDirectory $Root -PassThru
    } catch {
        $sp = $null
        Add-Check 'install-no-elevation-prompt' 'FAIL' $cmd $_.Exception.Message 'the setup could not start without elevation (ERROR_ELEVATION_REQUIRED would mean it asks for admin)'
    }
    if ($sp) {
        $wiz = Wait-Until { [SutramAccept]::WindowsOf([uint32]$sp.Id, 'SutramWizardWindow') | Select-Object -First 1 } 15000
        $consentSeen = $false
        $pe = [SutramAccept]::ProcessElevation([uint32]$sp.Id)
        if (-not $wiz) {
            Add-Check 'install-wizard' 'FAIL' $cmd '' 'no SutramWizardWindow within 15 s'
        } else {
            Start-Sleep -Milliseconds 1000                                                     # let the first page paint
            $pages = @(); $log = New-Object System.Text.StringBuilder
            function Page-Step([string]$Name) { $script:pages += (Shot $wiz ('wizard-' + $Name + '.png')); [void]$log.AppendLine('page: ' + $Name) }
            Page-Step 'welcome'; [void](Click $wiz 2002); Start-Sleep -Milliseconds 500            # Next
            Page-Step 'license'
            $next = [SutramAccept]::GetDlgItem($wiz, 2002)
            [void]$log.AppendLine('Next enabled before accepting: ' + [SutramAccept]::IsWindowEnabled($next))
            [void](Click $wiz 2010); Start-Sleep -Milliseconds 300                                     # I accept
            [void]$log.AppendLine('Next enabled after accepting: ' + [SutramAccept]::IsWindowEnabled($next))
            [void](Click $wiz 2002); Start-Sleep -Milliseconds 500
            Page-Step 'location'
            $installDir = [SutramAccept]::Text([SutramAccept]::GetDlgItem($wiz, 2020))
            [void]$log.AppendLine('install folder (default, unchanged): ' + $installDir)
            [void](Click $wiz 2002); Start-Sleep -Milliseconds 500
            Page-Step 'components'
            [void]$log.AppendLine('add-to-PATH checked: ' + ([SutramAccept]::Send([SutramAccept]::GetDlgItem($wiz, 2030), 0x00F0, 0, 0)))
            [void]$log.AppendLine('desktop shortcut checked: ' + ([SutramAccept]::Send([SutramAccept]::GetDlgItem($wiz, 2031), 0x00F0, 0, 0)))
            [void](Click $wiz 2002); Start-Sleep -Milliseconds 500
            Page-Step 'ready'
            [void](Click $wiz 2002)                                                            # Install
            $sw = [Diagnostics.Stopwatch]::StartNew(); $outcome = $null
            while ($sw.Elapsed.TotalSeconds -lt $InstallTimeoutSec) {
                if (@(Get-Process -Name consent -ErrorAction SilentlyContinue).Count -gt $consentBefore) { $consentSeen = $true }
                $dlg = Find-Dialog $sp.Id
                if ($dlg) { $outcome = 'dialog: ' + (Dialog-Text $dlg); [void](Shot $dlg 'wizard-failure-box.png'); [void](Click $dlg 1); [void](Click $dlg 2); break }
                $launch = [SutramAccept]::GetDlgItem($wiz, 2060)
                if ($launch -ne [IntPtr]::Zero -and [SutramAccept]::IsWindowVisible($launch)) { $outcome = 'done page'; break }
                if ($sp.HasExited) { $outcome = 'setup exited ' + $sp.ExitCode; break }
                Start-Sleep -Milliseconds 250
            }
            if (-not $outcome) { $outcome = 'timeout after ' + $InstallTimeoutSec + ' s' }
            [void]$log.AppendLine('outcome: ' + $outcome + ' after ' + [int]$sw.Elapsed.TotalSeconds + ' s')
            if ($outcome -eq 'done page') {
                Page-Step 'done'
                [void][SutramAccept]::Send([SutramAccept]::GetDlgItem($wiz, 2060), 0x00F1, 0, 0)   # BM_SETCHECK unchecked: do not auto-launch
                [void](Click $wiz 2002)                                                          # Finish
                [void](Wait-Until { $sp.HasExited } 10000)
            }
            $stage = Get-ChildItem -LiteralPath $env:TEMP -Directory -Filter 'STM*.tmp' -ErrorAction SilentlyContinue | Where-Object { $tempBefore -notcontains $_.FullName } | Sort-Object LastWriteTime | Select-Object -Last 1
            if ($stage -and (Test-Path -LiteralPath (Join-Path $stage.FullName 'install.log'))) {
                Copy-Item -LiteralPath (Join-Path $stage.FullName 'install.log') -Destination (Join-Path $OutDir 'install.log') -Force
                [void]$log.AppendLine('install.log copied from ' + $stage.FullName)
            }
            $installed = ($outcome -eq 'done page') -and (Test-Path -LiteralPath $unKey)
            if ($installed) { $installDir = (Get-ItemProperty -LiteralPath $unKey).InstallLocation }
            $st = 'FAIL'; if ($installed) { $st = 'PASS' }
            Add-Check 'install-wizard' $st 'BM_CLICK Next / I accept / Next / Next / Install / Finish (launch unchecked) on the wizard this script started' $log.ToString() ('outcome=' + $outcome + '; screenshots: ' + (($pages | Where-Object { $_ }) -join ', '))
        }
        $peText = 'setup TokenElevationType=' + $pe[0] + ' TokenElevation=' + $pe[1] + '; consent.exe appeared during install: ' + $consentSeen
        if ($isWine) { Add-Check 'install-no-elevation-prompt' 'NOT-RUN' $cmd $peText 'Wine has no UAC; this check means something only on Windows' }
        elseif ($pe[1] -eq 0 -and -not $consentSeen) { Add-Check 'install-no-elevation-prompt' 'PASS' $cmd $peText 'setup ran unelevated and no UAC consent prompt appeared' }
        elseif ($pe[1] -lt 0) { Add-Check 'install-no-elevation-prompt' 'NOT-RUN' $cmd $peText 'could not read the setup process token' }
        else { Add-Check 'install-no-elevation-prompt' 'FAIL' $cmd $peText 'setup was elevated or a UAC prompt appeared' }
    }

    if ($installed) {
        $foot = [ordered]@{}
        foreach ($rel in @('sutram-ide-gui.exe','bin\sutram.exe','win\sutram.exe','Sutram-Uninstall.exe','payload.manifest.sha256','examples\218_sanskrit_devanagari.sm','lang\sanskrit.lang')) { $foot[$rel] = Test-Path -LiteralPath (Join-Path $installDir $rel) }
        $sm = Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram'
        foreach ($lnk in @('Sutram IDE.lnk','Sutram Terminal.lnk','Uninstall Sutram.lnk')) { $foot['StartMenu\' + $lnk] = Test-Path -LiteralPath (Join-Path $sm $lnk) }
        $foot['HKCU uninstall key'] = Test-Path -LiteralPath $unKey
        $foot['HKCU Classes\Sutram.Source'] = Test-Path -LiteralPath 'HKCU:\Software\Classes\Sutram.Source'
        $userPath = [string]([Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment').GetValue('Path','',[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames))
        $foot['user PATH has bin'] = @($userPath -split ';' | Where-Object { $_.TrimEnd('\') -ieq (Join-Path $installDir 'bin') }).Count -gt 0
        $missing = @($foot.Keys | Where-Object { -not $foot[$_] })
        $hi = Add-Artefact 'installed bin\sutram.exe' (Join-Path $installDir 'bin\sutram.exe')
        [void](Add-Artefact 'installed win\sutram.exe' (Join-Path $installDir 'win\sutram.exe'))
        [void](Add-Artefact 'installed sutram-ide-gui.exe' (Join-Path $installDir 'sutram-ide-gui.exe'))
        [void](Add-Artefact 'installed Sutram-Uninstall.exe' (Join-Path $installDir 'Sutram-Uninstall.exe'))
        $st = 'PASS'; if ($missing.Count) { $st = 'FAIL' }
        Add-Check 'install-footprint' $st 'Test-Path on the installed files, Start Menu shortcuts, HKCU keys, user PATH' (($foot.Keys | ForEach-Object { $_ + ' = ' + $foot[$_] }) -join "`n") ('missing: ' + ($missing -join ', '))
    } elseif (-not $skipInstall) { NotRun 'install-footprint' 'install did not complete' }
}

# ------------------------------------------------------------------------------------------------
# Compiler: Devanagari program through the sanskrit pack (CLI)
# ------------------------------------------------------------------------------------------------
$base = $Root; $where = 'repository build'
if ($installed) { $base = $installDir; $where = 'installed copy' }
$compiler = $null
foreach ($rel in @('bin\sutram.exe','win\sutram.exe','sutram.exe')) { if (-not $compiler -and (Test-Path -LiteralPath (Join-Path $base $rel))) { $compiler = Join-Path $base $rel } }
if (-not $compiler) { $compiler = Join-Path $base 'bin\sutram.exe' }
$example = Join-Path $base 'examples\218_sanskrit_devanagari.sm'
if ((Test-Path -LiteralPath $compiler) -and (Test-Path -LiteralPath $example)) {
    $exe = Join-Path $OutDir 'devanagari-218.exe'
    $c = Run-Exe $compiler ('--lang sanskrit "' + $example + '" "' + $exe + '"') $base 30000
    $out = 'compile exit=' + $c.exit + "`n" + $c.out
    $ok = $false
    if ($c.exit -eq 0 -and (Test-Path -LiteralPath $exe)) { $x = Run-Exe $exe '' $OutDir 10000; $out += "`nrun exit=" + $x.exit + "`n" + $x.out; $ok = ($x.exit -eq 0) -and $x.out.Contains($yogah15) }
    $st = 'FAIL'; if ($ok) { $st = 'PASS' }
    Add-Check 'devanagari-cli' $st ('"' + $compiler + '" --lang sanskrit 218_sanskrit_devanagari.sm; run it') $out ($where + '; expects the line ' + $yogah15)
} else { NotRun 'devanagari-cli' ('no compiler or example under ' + $base) }

# ------------------------------------------------------------------------------------------------
# IDE
# ------------------------------------------------------------------------------------------------
$ideExe = Join-Path $base 'sutram-ide-gui.exe'
$ideIds = @('ide-launches','ide-menus-english','ide-buttons-english','devanagari-ide','tab-indent','shift-tab-dedent','unsaved-guard')
if (-not (Test-Path -LiteralPath $ideExe)) { foreach ($id in $ideIds) { NotRun $id ('no IDE at ' + $ideExe) } }
else {
    $ip = Start-Process -FilePath $ideExe -WorkingDirectory $base -PassThru
    $main = Wait-Until { [SutramAccept]::WindowsOf([uint32]$ip.Id, 'SutramNativeGUIWindow') | Select-Object -First 1 } 15000
    if (-not $main) {
        Add-Check 'ide-launches' 'FAIL' ('Start-Process "' + $ideExe + '"') '' 'no SutramNativeGUIWindow within 15 s'
        foreach ($id in $ideIds[1..($ideIds.Count-1)]) { NotRun $id 'the IDE did not open' }
    } else {
        Start-Sleep -Milliseconds 800
        $ie = [SutramAccept]::ProcessElevation([uint32]$ip.Id)
        Add-Check 'ide-launches' 'PASS' ('Start-Process "' + $ideExe + '" -WorkingDirectory "' + $base + '"') ('pid=' + $ip.Id + ' title=' + [SutramAccept]::Text($main) + ' TokenElevation=' + $ie[1]) ($where + '; screenshot ' + (Shot $main 'ide-start.png'))
        function Ctl([int]$Id) { return [SutramAccept]::GetDlgItem($main, $Id) }
        function Editor() { return ([SutramAccept]::Text((Ctl 201))).Replace("`r`n", "`n") }
        function SetEditor([string]$S) { [SutramAccept]::SetText((Ctl 201), $S) }
        function CaretEnd() { [void][SutramAccept]::Send((Ctl 201), 0x00B1, 1000000, 1000000) }

        # Menus: top level and every item, compared with what the source declares.
        $menu = [SutramAccept]::GetMenu($main); $tree = @(); $top = @()
        $menuCount = [SutramAccept]::GetMenuItemCount($menu)
        for ($i = 0; $i -lt $menuCount; $i++) {
            $name = [SutramAccept]::MenuString($menu, $i); $top += $name
            $sub = [SutramAccept]::GetSubMenu($menu, $i); $items = @()
            if ($sub -ne [IntPtr]::Zero) { for ($j = 0; $j -lt [SutramAccept]::GetMenuItemCount($sub); $j++) { $t = [SutramAccept]::MenuString($sub, $j); if ($t) { $items += $t } } }
            $tree += ($name + ': ' + ($items -join ' / '))
        }
        $wantTop = @('File','Edit','Shell','Language','Help')
        $wantItems = @('New','Open...','Save','Save As...','Exit','Undo','Cut','Copy','Paste','Select All','Find...','Find Next','Indent (4 spaces)','Dedent','Run module','Send (shell line)','Clear shell','Auto (detect script)','Core (Latin keywords)','Shortcut keys','About Sutram')
        $flat = ($tree -join "`n")
        $missingItems = @($wantItems | Where-Object { -not $flat.Contains($_) })
        $menuCmd = 'GetMenu / GetMenuItemCount / GetMenuStringW(MF_BYPOSITION)'
        if ($menuCount -le 0 -and $isWine) {
            Add-Check 'ide-menus-english' 'NOT-RUN' $menuCmd ('HMENU=' + $menu + ' count=' + $menuCount) 'Wine keeps menus per process, so another process cannot read them; this check needs Windows'
        } else {
            $st = 'FAIL'; if ((($top -join ',') -eq ($wantTop -join ',')) -and $missingItems.Count -eq 0) { $st = 'PASS' }
            Add-Check 'ide-menus-english' $st $menuCmd ('HMENU=' + $menu + ' count=' + $menuCount + "`n" + $flat) ('expected top ' + ($wantTop -join ' ') + '; missing items: ' + ($missingItems -join ', '))
        }

        $want = [ordered]@{ '101' = 'Run'; '102' = 'Open'; '103' = 'Save'; '104' = 'Load example'; '105' = 'Send'; '106' = 'Clear shell'; '208' = 'Find:' }
        $got = @(); $bad = @()
        foreach ($k in $want.Keys) { $t = [SutramAccept]::Text((Ctl ([int]$k))); $got += ($k + '=' + $t); if ($t -ne $want[$k]) { $bad += $k } }
        $st = 'FAIL'; if ($bad.Count -eq 0) { $st = 'PASS' }
        Add-Check 'ide-buttons-english' $st 'WM_GETTEXT on controls 101-106 and 208' ($got -join "`n") ('mismatched ids: ' + ($bad -join ','))

        # Devanagari through the IDE: Language > Auto, then Shell > Run module.
        try {
            $deva = [IO.File]::ReadAllText($example, [Text.Encoding]::UTF8).Replace("`r`n", "`n").Replace("`n", "`r`n")
            SetEditor $deva
            [void][SutramAccept]::Send($main, 0x0111, 2040, 0)
            [void][SutramAccept]::Send($main, 0x0111, 2010, 0)
            $o = [SutramAccept]::Text((Ctl 203)); $s = [SutramAccept]::Text((Ctl 206))
            $st = 'FAIL'; if ($o.Contains($yogah15)) { $st = 'PASS' }
            Add-Check 'devanagari-ide' $st 'WM_SETTEXT editor = 218_sanskrit_devanagari.sm; WM_COMMAND Language>Auto (2040); WM_COMMAND Run module (2010); WM_GETTEXT output' ($o + "`n[status] " + $s) ('expects ' + $yogah15 + '; screenshot ' + (Shot $main 'ide-devanagari.png'))
        } catch { Add-Check 'devanagari-ide' 'FAIL' 'WM_COMMAND 2040, 2010' $_.Exception.Message 'exception' }

        # Tab: real key messages to the editor (the subclass handles WM_KEYDOWN/WM_CHAR VK_TAB).
        try {
            SetEditor "mukhya() {`r`n"; CaretEnd
            [void][SutramAccept]::Send((Ctl 201), 0x0100, 9, 0); [void][SutramAccept]::Send((Ctl 201), 0x0102, 9, 0)
            $e1 = Editor
            SetEditor "mukhya() {`r`n    likha(1)`r`n    likha(2)`r`n}`r`n"; [void][SutramAccept]::Send((Ctl 201), 0x00B1, 11, 30)
            [void][SutramAccept]::Send((Ctl 201), 0x0100, 9, 0); [void][SutramAccept]::Send((Ctl 201), 0x0102, 9, 0)
            $e2 = Editor
            $ok = ($e1 -eq "mukhya() {`n    ") -and ($e2 -eq "mukhya() {`n        likha(1)`n        likha(2)`n}`n")
            $st = 'FAIL'; if ($ok) { $st = 'PASS' }
            Add-Check 'tab-indent' $st 'WM_KEYDOWN+WM_CHAR VK_TAB to the editor: once at the end of a line, once on a two-line selection' ("caret: " + ($e1 | ConvertTo-Json) + "`nblock: " + ($e2 | ConvertTo-Json)) 'four spaces, no tab character; a selection moves right by four'
        } catch { Add-Check 'tab-indent' 'FAIL' 'WM_KEYDOWN VK_TAB' $_.Exception.Message 'exception' }

        # Shift+Tab: the menu command always; the real key only with -Keyboard.
        try {
            SetEditor "    likha(1)"; CaretEnd
            [void][SutramAccept]::Send($main, 0x0111, 2039, 0)
            $m1 = Editor
            $menuOk = ($m1 -eq 'likha(1)')
            if ($Keyboard) {
                SetEditor "    likha(1)"; CaretEnd
                [void][SutramAccept]::SetForegroundWindow($main); Start-Sleep -Milliseconds 300
                [void][SutramAccept]::Send($main, 0x0028, (Ctl 201).ToInt64(), 1)            # WM_NEXTDLGCTL: focus the editor
                $sent = [SutramAccept]::ShiftTab(); Start-Sleep -Milliseconds 500
                $k1 = Editor
                $st = 'FAIL'; if ($menuOk -and $k1 -eq 'likha(1)') { $st = 'PASS' }
                Add-Check 'shift-tab-dedent' $st 'Edit > Dedent (WM_COMMAND 2039); then SendInput Shift+Tab with the IDE in the foreground' ('menu: ' + ($m1 | ConvertTo-Json) + "`nkeys sent=" + $sent + ' editor: ' + ($k1 | ConvertTo-Json)) 'four spaces removed both ways'
            } else {
                $st = 'FAIL'; if ($menuOk) { $st = 'PASS' }
                Add-Check 'shift-tab-dedent' $st 'Edit > Dedent (WM_COMMAND 2039), the command Shift+Tab is bound to' ('menu: ' + ($m1 | ConvertTo-Json)) 'menu path only'
                NotRun 'shift-tab-keyboard' 'a real Shift+Tab needs the keyboard state, i.e. SendInput into the foreground window; rerun with -Keyboard and do not touch the mouse/keyboard while it runs' $false
            }
        } catch { Add-Check 'shift-tab-dedent' 'FAIL' 'WM_COMMAND 2039' $_.Exception.Message 'exception' }

        # Unsaved-work guard: change the text, ask for File > New, expect the question, press Cancel.
        try {
            SetEditor "mukhya() {`r`n    likha(`"guard`")`r`n}`r`n"
            $title = [SutramAccept]::Text($main)
            [void][SutramAccept]::PostMessageW($main, 0x0111, [IntPtr]2004, [IntPtr]::Zero)   # posted: the answer box is modal
            $dlg = Wait-Until { Find-Dialog $ip.Id } 5000
            if ($dlg) {
                $q = Dialog-Text $dlg; $pic = Shot $dlg 'ide-unsaved-guard.png'
                [void](Click $dlg 2); Start-Sleep -Milliseconds 500                                # Cancel
                $kept = (Editor).Contains('guard')
                $st = 'FAIL'; if ($q.Contains('The file has changed') -and $kept) { $st = 'PASS' }
                Add-Check 'unsaved-guard' $st 'WM_SETTEXT editor; WM_COMMAND File>New (2004); read the box; BM_CLICK Cancel' ('title=' + $title + "`nbox: " + $q + "`neditor kept after Cancel: " + $kept) ('screenshot ' + $pic)
            } else { Add-Check 'unsaved-guard' 'FAIL' 'WM_COMMAND File>New (2004)' ('title=' + $title + "`neditor now: " + (Editor)) 'no question box within 5 s: unsaved work would be dropped' }
        } catch { Add-Check 'unsaved-guard' 'FAIL' 'WM_COMMAND 2004' $_.Exception.Message 'exception' }

        # Close the IDE: the guard asks again; answer No (discard).
        [void][SutramAccept]::PostMessageW($main, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)
        $dlg = Wait-Until { Find-Dialog $ip.Id } 3000
        if ($dlg) { [void](Click $dlg 7) }
        if (-not (Wait-Until { $ip.HasExited } 8000)) { try { $ip.Kill() } catch {} }
    }
}

# ------------------------------------------------------------------------------------------------
# Uninstall
# ------------------------------------------------------------------------------------------------
if ($installed -and -not $KeepInstalled) {
    $un = Join-Path $installDir 'Sutram-Uninstall.exe'
    $cmd = '"' + $un + '" --uninstall   (the Start Menu "Uninstall Sutram" target)'
    $stagesBefore = @(Get-ChildItem -LiteralPath $env:TEMP -Directory -Filter 'STM*.tmp' -ErrorAction SilentlyContinue | ForEach-Object { $_.FullName })
    $up = Start-Process -FilePath $un -ArgumentList '--uninstall' -WorkingDirectory $env:TEMP -PassThru
    # The uninstaller starts PowerShell and exits at once (so it can remove its own file); success shows no
    # box. So wait for its log in the new %TEMP%\STM*.tmp folder, and click OK on a failure box if one shows.
    $boxText = ''; $ulogText = ''; $sw = [Diagnostics.Stopwatch]::StartNew()
    while ($sw.Elapsed.TotalSeconds -lt 180) {
        if (-not $up.HasExited) { $box = Find-Dialog $up.Id; if ($box) { $boxText = Dialog-Text $box; [void](Shot $box 'uninstall-box.png'); [void](Click $box 1) } }
        $ulog = Get-ChildItem -LiteralPath $env:TEMP -Directory -Filter 'STM*.tmp' -ErrorAction SilentlyContinue | Where-Object { $stagesBefore -notcontains $_.FullName } | ForEach-Object { Join-Path $_.FullName 'uninstall.log' } | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
        if ($ulog) { $ulogText = [IO.File]::ReadAllText($ulog); if ($ulogText -match 'Uninstall completed|ERROR') { Copy-Item -LiteralPath $ulog -Destination (Join-Path $OutDir 'uninstall.log') -Force; break } }
        Start-Sleep -Milliseconds 500
    }
    if (-not $ulogText) { $ulogText = '(no uninstall.log appeared within 180 s)' }
    Start-Sleep -Seconds 2
    $after = [ordered]@{}
    foreach ($rel in @('sutram-ide-gui.exe','bin\sutram.exe','win\sutram.exe','payload.manifest.sha256')) { $after[$rel + ' removed'] = -not (Test-Path -LiteralPath (Join-Path $installDir $rel)) }
    $sm = Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram'
    $after['Start Menu folder removed'] = -not (Test-Path -LiteralPath $sm)
    $after['HKCU uninstall key removed'] = -not (Test-Path -LiteralPath $unKey)
    $after['HKCU Classes\Sutram.Source removed'] = -not (Test-Path -LiteralPath 'HKCU:\Software\Classes\Sutram.Source')
    $userPath = [string]([Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment').GetValue('Path','',[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames))
    $after['user PATH entry removed'] = @($userPath -split ';' | Where-Object { $_.TrimEnd('\') -ieq (Join-Path $installDir 'bin') }).Count -eq 0
    $left = @($after.Keys | Where-Object { -not $after[$_] })
    $st = 'FAIL'; if ($left.Count -eq 0) { $st = 'PASS' }
    Add-Check 'uninstall-removes-install' $st $cmd ((($after.Keys | ForEach-Object { $_ + ' = ' + $after[$_] }) -join "`n") + "`n[uninstall.log]`n" + $ulogText) ('failure box: ' + $boxText + '; not removed: ' + ($left -join ', '))
    $leftDir = (Test-Path -LiteralPath $installDir)
    Add-Check 'uninstall-folder-gone' $(if ($leftDir) { 'FAIL' } else { 'PASS' }) ('Test-Path "' + $installDir + '"') ('exists=' + $leftDir) 'the install folder itself (it is kept when it holds user files)' $false
} elseif ($installed) { NotRun 'uninstall-removes-install' '-KeepInstalled was given' }
else { NotRun 'uninstall-removes-install' 'nothing was installed by this run' }

# Known defect (R4-03 section 3, ChatGPT's): staging folders are left in %TEMP%. Advisory, not required.
if ($installed) {
    $leftStages = @(Get-ChildItem -LiteralPath $env:TEMP -Directory -Filter 'STM*.tmp' -ErrorAction SilentlyContinue | Where-Object { $tempBefore -notcontains $_.FullName } | ForEach-Object { $_.Name })
    Add-Check 'temp-staging-cleaned' $(if ($leftStages.Count) { 'FAIL' } else { 'PASS' }) 'Get-ChildItem $env:TEMP STM*.tmp (new during this run)' ($leftStages -join "`n") 'known defect R4-03 s3; advisory only' $false
}

# ------------------------------------------------------------------------------------------------
# Verdict and log
# ------------------------------------------------------------------------------------------------
$req = @($checks | Where-Object { $_.required })
$fail = @($req | Where-Object { $_.status -eq 'FAIL' }).Count
$notrun = @($req | Where-Object { $_.status -eq 'NOT-RUN' }).Count
$pass = @($req | Where-Object { $_.status -eq 'PASS' }).Count
if ($fail) { $verdict = 'FAIL' } elseif ($notrun) { $verdict = 'PARTIAL' } else { $verdict = 'PASS' }
if ($isWine) { $verdict = $verdict + ' (Wine only - NOT Windows acceptance)' }
$result = [ordered]@{
    tool = 'tools/accept-windows.ps1'; schema = 1
    verdict = $verdict; required_pass = $pass; required_fail = $fail; required_not_run = $notrun
    environment = $environment; artefacts = $artefacts; checks = $checks
    finished = [DateTime]::Now.ToString('yyyy-MM-ddTHH:mm:sszzz')
}
$json = $result | ConvertTo-Json -Depth 6
$logPath = Join-Path $OutDir 'accept-windows.json'
[IO.File]::WriteAllText($logPath, $json, (New-Object Text.UTF8Encoding($false)))
Write-Host ''
Write-Host ('VERDICT  {0}   required: {1} PASS / {2} FAIL / {3} NOT-RUN' -f $verdict, $pass, $fail, $notrun)
Write-Host ('LOG      {0}' -f $logPath)
Write-Host ('LOG-SHA256 {0}' -f (Get-Sha256 $logPath))
if ($fail) { exit 1 } else { exit 0 }
