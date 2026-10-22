<#
.SYNOPSIS
  R34: every example, one by one, through the real Windows IDE (sutram-ide-gui.exe).

.DESCRIPTION
  Run from a normal (NOT elevated) Windows PowerShell 5.1 or PowerShell 7 window:

      powershell -NoProfile -ExecutionPolicy Bypass -File tools\ide_examples_windows.ps1

  Starts the IDE from the repository (it compiles with win\sutram.exe beside it), and for each
  examples\<name>.sm that has tests\expect\<name>.out or .compile_fail:
    1. double-clicks it in the IDE's example list, as a user does (-Paste: puts the text in the
       editor instead, as typing would - no file behind it),
    2. chooses the language as a user would: Language > <pack> for the six pack examples, else
       Language > Auto,
    3. presses Shell > Run module (WM_COMMAND 2010; the IDE runs it to the end or its 10 s limit),
    4. reads the output pane and the status line, and compares the output with the golden.
  The IDE gives a program no input: the six input examples must finish at end of input (not hang).
  A file the IDE refuses to open (its editor holds 65534 bytes) is reported NOT-OPENED.
  Then two guards: a refused load followed by File > Save must leave the refused file untouched
  (checked on a throwaway copy, never the repository's files), and an example must not replace
  unsaved work without asking.
  Writes ide-examples.json (every run: output, status line, verdict) and ide-examples.txt (the
  summary) to -OutDir, and a screenshot of the IDE window (only that window) for any non-match.
  -Ide another build of the IDE (run from -Root); -Only one example; -ShotAll a screenshot of each.
  Installs nothing, elevates nothing, sends window messages only to the IDE it started.
  This file is ASCII on purpose (5.1 reads BOM-less files as ANSI).
#>
[CmdletBinding()]
param([string]$Root = '', [string]$OutDir = '', [string]$Only = '', [string]$Ide = '', [switch]$Paste, [switch]$ShotAll)
if (-not $Root) { $Root = Split-Path -Parent $PSScriptRoot }
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$Root = [IO.Path]::GetFullPath($Root)
if (-not $OutDir) { $OutDir = Join-Path $Root ('build\windows\ide-examples-' + [DateTime]::Now.ToString('yyyyMMdd-HHmmss')) }
[void](New-Item -ItemType Directory -Force -Path $OutDir)

Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public static class SutramIde {
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetClassNameW(IntPtr h, StringBuilder b, int n);
    [DllImport("user32.dll")] public static extern IntPtr GetDlgItem(IntPtr h, int id);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool PostMessageW(IntPtr h, uint m, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern IntPtr SendMessageTimeoutW(IntPtr h, uint m, IntPtr w, StringBuilder l, uint f, uint t, out IntPtr r);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern IntPtr SendMessageTimeoutW(IntPtr h, uint m, IntPtr w, string l, uint f, uint t, out IntPtr r);
    [DllImport("user32.dll")] static extern IntPtr SendMessageTimeoutW(IntPtr h, uint m, IntPtr w, IntPtr l, uint f, uint t, out IntPtr r);
    [DllImport("user32.dll")] static extern IntPtr GetDC(IntPtr h);
    [DllImport("user32.dll")] static extern int ReleaseDC(IntPtr h, IntPtr dc);
    [DllImport("gdi32.dll")] static extern IntPtr CreateCompatibleDC(IntPtr dc);
    [DllImport("gdi32.dll")] static extern bool DeleteDC(IntPtr dc);
    [DllImport("gdi32.dll")] static extern IntPtr SelectObject(IntPtr dc, IntPtr o);
    [DllImport("gdi32.dll")] static extern bool DeleteObject(IntPtr o);
    [DllImport("gdi32.dll")] static extern IntPtr CreateDIBSection(IntPtr dc, byte[] bmi, uint usage, out IntPtr bits, IntPtr sec, uint off);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    public static string ClassOf(IntPtr h) { StringBuilder b = new StringBuilder(256); GetClassNameW(h, b, 256); return b.ToString(); }
    public static IntPtr[] WindowsOf(uint pid, string cls) {
        List<IntPtr> found = new List<IntPtr>();
        EnumWindows(delegate(IntPtr h, IntPtr l) {
            uint p; GetWindowThreadProcessId(h, out p);
            if (p == pid && (cls == null || ClassOf(h) == cls)) found.Add(h);
            return true;
        }, IntPtr.Zero);
        return found.ToArray();
    }
    public static long Send(IntPtr h, uint m, long w, long l, uint ms) {
        IntPtr r;
        if (SendMessageTimeoutW(h, m, new IntPtr(w), new IntPtr(l), 2, ms, out r) == IntPtr.Zero)
            throw new Exception("SendMessageTimeout failed for message 0x" + m.ToString("X"));
        return r.ToInt64();
    }
    public static string Text(IntPtr h) {
        IntPtr r; StringBuilder b = new StringBuilder(262144);
        if (SendMessageTimeoutW(h, 0x000D, new IntPtr(262144), b, 2, 30000, out r) == IntPtr.Zero) throw new Exception("WM_GETTEXT timed out");
        return b.ToString();
    }
    public static long ListFind(IntPtr h, string s) {
        IntPtr r;   // LB_FINDSTRINGEXACT from the top
        if (SendMessageTimeoutW(h, 0x01A2, new IntPtr(-1), s, 2, 10000, out r) == IntPtr.Zero) throw new Exception("LB_FINDSTRINGEXACT timed out");
        return r.ToInt64();
    }
    public static void SetText(IntPtr h, string s) {
        IntPtr r;
        if (SendMessageTimeoutW(h, 0x000C, IntPtr.Zero, s, 2, 30000, out r) == IntPtr.Zero) throw new Exception("WM_SETTEXT timed out");
    }
    // PrintWindow of this one window into a .bmp (never the desktop).
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
            if (!PrintWindow(h, dc, 2)) return false;
            int size = w * ht * 4; byte[] px = new byte[size]; Marshal.Copy(bits, px, 0, size);
            using (System.IO.FileStream f = System.IO.File.Create(path)) {
                byte[] fh = new byte[14]; fh[0] = 0x42; fh[1] = 0x4D;
                BitConverter.GetBytes(54 + size).CopyTo(fh, 2); BitConverter.GetBytes(54).CopyTo(fh, 10);
                f.Write(fh, 0, 14); f.Write(bmi, 0, 40); f.Write(px, 0, size);
            }
            return true;
        } finally { SelectObject(dc, old); DeleteObject(dib); DeleteDC(dc); }
    }
}
'@

function Wait-Until([scriptblock]$Cond, [int]$Ms) {
    $sw = [Diagnostics.Stopwatch]::StartNew()
    while ($sw.ElapsedMilliseconds -lt $Ms) { $v = & $Cond; if ($v) { return $v }; Start-Sleep -Milliseconds 100 }
    return $null
}
function Shot([IntPtr]$H, [string]$Name) {
    $bmp = Join-Path $OutDir ($Name + '.bmp')
    if (-not [SutramIde]::Capture($H, $bmp)) { return '(no screenshot)' }
    try {
        Add-Type -AssemblyName System.Drawing
        $img = [Drawing.Image]::FromFile($bmp); $png = [IO.Path]::ChangeExtension($bmp, '.png')
        $img.Save($png, [Drawing.Imaging.ImageFormat]::Png); $img.Dispose(); Remove-Item -LiteralPath $bmp -Force
        return [IO.Path]::GetFileName($png)
    } catch { return [IO.Path]::GetFileName($bmp) }
}

$packMenu = @{ sanskrit = 2042; bengali = 2043; gujarati = 2044; hindi = 2045; kannada = 2046; malayalam = 2047
               marathi = 2048; odia = 2049; punjabi = 2050; tamil = 2051; telugu = 2052 }
$lang = @{ '37_native_gujarati' = 'gujarati'; '38_native_hindi' = 'hindi'; '39_native_tamil' = 'tamil'
           '218_sanskrit_devanagari' = 'sanskrit'; '219_sanskrit_kosh_aliases' = 'sanskrit'; '220_hindi_parse_error' = 'hindi' }
$stdinNeeded = @('23_grahan_input','24_guess_game','26_calculator','number_game','46_language_reference','59_windows_grahan_runtime')

$ideExe = Join-Path $Root 'sutram-ide-gui.exe'
if ($Ide) { $ideExe = [IO.Path]::GetFullPath($Ide) }   # another build of the IDE, run from -Root
$compiler = Join-Path $Root 'win\sutram.exe'
foreach ($p in @($ideExe, $compiler)) { if (-not (Test-Path -LiteralPath $p)) { throw "missing: $p" } }
$ideHash = (Get-FileHash -LiteralPath $ideExe -Algorithm SHA256).Hash.ToLowerInvariant()
$compHash = (Get-FileHash -LiteralPath $compiler -Algorithm SHA256).Hash.ToLowerInvariant()

$ip = Start-Process -FilePath $ideExe -WorkingDirectory $Root -PassThru
$main = Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id, 'SutramNativeGUIWindow') | Select-Object -First 1 } 15000
if (-not $main) { throw 'the IDE did not open a SutramNativeGUIWindow within 15 s' }
Start-Sleep -Milliseconds 800
$editor = [SutramIde]::GetDlgItem($main, 201); $output = [SutramIde]::GetDlgItem($main, 203); $status = [SutramIde]::GetDlgItem($main, 206)
$list = [SutramIde]::GetDlgItem($main, 205)
$startShot = Shot $main 'ide-open'

$names = Get-ChildItem -LiteralPath (Join-Path $Root 'examples') -Filter '*.sm' | ForEach-Object { $_.BaseName } | Sort-Object
$results = @()
foreach ($n in $names) {
    if ($Only -and $n -ne $Only) { continue }
    $outF = Join-Path $Root ('tests\expect\' + $n + '.out'); $cfF = Join-Path $Root ('tests\expect\' + $n + '.compile_fail')
    $exitF = Join-Path $Root ('tests\expect\' + $n + '.exit')
    if (-not (Test-Path -LiteralPath $outF) -and -not (Test-Path -LiteralPath $cfF)) { continue }
    $how = 'list'
    $idx = [SutramIde]::ListFind($list, ($n + '.sm'))
    if ($Paste -or $idx -lt 0) {
        # typed / pasted text: no file behind it (and the only way when the list lacks the name)
        $how = 'paste'
        $src = [IO.File]::ReadAllText((Join-Path $Root ('examples\' + $n + '.sm')), [Text.Encoding]::UTF8).Replace("`r`n", "`n").Replace("`n", "`r`n")
        [SutramIde]::SetText($editor, $src)
    } else {
        # as a user does: select it in the example list and double-click (LBN_DBLCLK) - the file itself
        [void][SutramIde]::Send($list, 0x0186, $idx, 0, 10000)                       # LB_SETCURSEL
        [void][SutramIde]::Send($main, 0x0111, (2 -shl 16) -bor 205, $list.ToInt64(), 30000)
        $dlg = Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id, '#32770') | Where-Object { [SutramIde]::IsWindowVisible($_) } | Select-Object -First 1 } 300
        if ($dlg) { $b = [SutramIde]::GetDlgItem($dlg, 7); if ($b -ne [IntPtr]::Zero) { [void][SutramIde]::PostMessageW($b, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero) }; Start-Sleep -Milliseconds 300 }
    }
    $opened = $true
    if ($how -eq 'list') { $opened = ([SutramIde]::Text($main)).StartsWith($n + '.sm') }   # the title names the file in the editor
    $menuId = 2040; $langName = 'auto'
    if ($lang.ContainsKey($n)) { $menuId = $packMenu[$lang[$n]]; $langName = $lang[$n] }
    [void][SutramIde]::Send($main, 0x0111, $menuId, 0, 10000)
    $sw = [Diagnostics.Stopwatch]::StartNew()
    $err = ''
    try { [void][SutramIde]::Send($main, 0x0111, 2010, 0, 60000) } catch { $err = $_.Exception.Message }
    $ms = $sw.ElapsedMilliseconds
    $got = ''; $st = ''
    try { $got = ([SutramIde]::Text($output)).Replace("`r`n", "`n"); $st = [SutramIde]::Text($status) }
    catch { if (-not $err) { $err = $_.Exception.Message } }
    $verdict = ''
    $detail = ''
    if ($err) {
        $verdict = 'IDE-HUNG'; $detail = 'the IDE did not answer: ' + $err
        [void](Wait-Until { try { [void][SutramIde]::Text($status); $true } catch { $false } } 120000)   # let it come back
    }
    elseif (-not $opened) {
        # the IDE refused to open it (the editor holds at most 65534 bytes); what ran was another file
        $verdict = 'NOT-OPENED'; $detail = 'the IDE refused to open it; title: ' + [SutramIde]::Text($main)
    }
    elseif ($stdinNeeded -contains $n) {
        # the IDE gives a run no input: the program must see end of input and finish, not hang
        if ($ms -lt 10000) { $verdict = 'NO-INPUT-OK'; $detail = 'finished at end of input: ' + (($got -split "`n" | Where-Object { $_ } | Select-Object -Last 1)) }
        else { $verdict = 'NO-INPUT-HANG'; $detail = 'ran into the 10 s limit with no input' }
    }
    elseif (Test-Path -LiteralPath $cfF) {
        $want = ([IO.File]::ReadAllText($outF, [Text.Encoding]::UTF8)).Replace("`r`n", "`n")
        $firstWant = ($want -split "`n" | Where-Object { $_ -match 'Error' } | Select-Object -First 1)
        if ($firstWant) { $key = ($firstWant -replace '^.*?(Sutram Error[^:]*:?)', '$1'); $key = $key.Substring(0, [Math]::Min(40, $key.Length)) } else { $key = 'Error' }
        if ($got.Contains($key) -or ($key -eq 'Error' -and $got -match 'Error|Truti|truti')) { $verdict = 'MATCH' } else { $verdict = 'DIFFER'; $detail = 'expected the diagnostic: ' + $key }
    } else {
        $want = ([IO.File]::ReadAllText($outF, [Text.Encoding]::UTF8)).Replace("`r`n", "`n")
        $wantExit = 0; if (Test-Path -LiteralPath $exitF) { $wantExit = [int]([IO.File]::ReadAllText($exitF).Trim()) }
        if ($got -eq $want) { $verdict = 'MATCH' }
        elseif ($got.StartsWith($want) -and $wantExit -ne 0) { $verdict = 'MATCH'; $detail = 'output matches; the IDE adds its note for exit ' + $wantExit }
        elseif ($ms -ge 10000) { $verdict = 'TIMEOUT' }
        else {
            $verdict = 'DIFFER'
            $a = $want -split "`n"; $b = $got -split "`n"
            for ($i = 0; $i -lt [Math]::Max($a.Count, $b.Count); $i++) {
                $x = if ($i -lt $a.Count) { $a[$i] } else { '<none>' }; $y = if ($i -lt $b.Count) { $b[$i] } else { '<none>' }
                if ($x -ne $y) { $detail = 'line ' + ($i + 1) + ': expected [' + $x + '] got [' + $y + ']'; break }
            }
        }
    }
    $pic = ''
    if ($verdict -ne 'MATCH' -or $ShotAll) { $pic = Shot $main ('ide-' + $n) }
    $results += [pscustomobject]@{ name = $n; loaded = $how; language = $langName; verdict = $verdict; ms = $ms; detail = $detail
                                   status_line = $st; output = $got; screenshot = $pic }
    Write-Host ('{0,-12} {1,-40} {2,-5} {3,6} ms  {4}' -f $verdict, $n, $how, $ms, $detail)
}

# Two guards, checked directly (only when the whole list ran):
#  1. a refused load keeps the previous file's name (else Save would write one file's text over another)
#  2. loading an example asks about unsaved work, as File > New and File > Open do
$guards = @()
if (-not $Only -and -not $Paste) {
    $big = $null
    foreach ($n in $names) { $f = Join-Path $Root ('examples\' + $n + '.sm'); if ((Get-Item -LiteralPath $f).Length -ge 65534) { $big = $n; break } }
    $i1 = [SutramIde]::ListFind($list, '01_hello.sm')
    [void][SutramIde]::Send($list, 0x0186, $i1, 0, 10000)
    [void][SutramIde]::Send($main, 0x0111, (2 -shl 16) -bor 205, $list.ToInt64(), 30000)
    if ($big) {
        # In a throwaway copy (never the repository's files): open a small example, then the big one
        # (refused), then File > Save. The big file must be untouched - before R34 it was overwritten
        # with the small one's text.
        $tr = Join-Path $OutDir 'save-guard'
        foreach ($d in @($tr, (Join-Path $tr 'win'), (Join-Path $tr 'examples'))) { [void](New-Item -ItemType Directory -Force -Path $d) }
        Copy-Item -LiteralPath $ideExe -Destination (Join-Path $tr 'sutram-ide-gui.exe') -Force
        Copy-Item -LiteralPath $compiler -Destination (Join-Path $tr 'win\sutram.exe') -Force
        Copy-Item -LiteralPath (Join-Path $Root 'examples\01_hello.sm') -Destination (Join-Path $tr 'examples\01_hello.sm') -Force
        $bigCopy = Join-Path $tr ('examples\' + $big + '.sm')
        Copy-Item -LiteralPath (Join-Path $Root ('examples\' + $big + '.sm')) -Destination $bigCopy -Force
        $before = (Get-FileHash -LiteralPath $bigCopy).Hash
        $gp = Start-Process -FilePath (Join-Path $tr 'sutram-ide-gui.exe') -WorkingDirectory $tr -PassThru
        $gm = Wait-Until { [SutramIde]::WindowsOf([uint32]$gp.Id, 'SutramNativeGUIWindow') | Select-Object -First 1 } 15000
        $saved = 'IDE did not open'
        if ($gm) {
            Start-Sleep -Milliseconds 800
            $gl = [SutramIde]::GetDlgItem($gm, 205)
            foreach ($name in @('01_hello.sm', ($big + '.sm'))) {
                [void][SutramIde]::Send($gl, 0x0186, [SutramIde]::ListFind($gl, $name), 0, 10000)
                [void][SutramIde]::Send($gm, 0x0111, (2 -shl 16) -bor 205, $gl.ToInt64(), 30000)
            }
            [void][SutramIde]::PostMessageW($gm, 0x0111, [IntPtr]2002, [IntPtr]::Zero)            # File > Save
            Start-Sleep -Milliseconds 1500
            $sd = [SutramIde]::WindowsOf([uint32]$gp.Id, '#32770') | Where-Object { [SutramIde]::IsWindowVisible($_) } | Select-Object -First 1
            if ($sd) { [void][SutramIde]::PostMessageW($sd, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) }  # a Save As box: cancel it
            $saved = 'title: ' + [SutramIde]::Text($gm)
            [void][SutramIde]::PostMessageW($gm, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)
            if (-not (Wait-Until { $gp.HasExited } 5000)) { try { $gp.Kill() } catch {} }
        }
        $after = (Get-FileHash -LiteralPath $bigCopy).Hash
        $ok = $before -eq $after
        $guards += [pscustomobject]@{ check = 'a refused load, then Save, leaves the refused file untouched'; result = $(if ($ok) { 'PASS' } else { 'FAIL' })
                                      detail = $big + ' (' + (Get-Item -LiteralPath (Join-Path $Root ('examples\' + $big + '.sm'))).Length + ' bytes, a copy) is now ' + (Get-Item -LiteralPath $bigCopy).Length + ' bytes; ' + $saved }
    }
    [SutramIde]::SetText($editor, "mukhya() {`r`n    likha(`"unsaved`")`r`n}`r`n")              # unsaved work
    [void][SutramIde]::Send($list, 0x0186, $i1, 0, 10000)
    [void][SutramIde]::PostMessageW($main, 0x0111, [IntPtr]((2 -shl 16) -bor 205), $list)      # posted: the question is modal
    $dlg = Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id, '#32770') | Where-Object { [SutramIde]::IsWindowVisible($_) } | Select-Object -First 1 } 5000
    if ($dlg) { $b = [SutramIde]::GetDlgItem($dlg, 2); [void][SutramIde]::PostMessageW($b, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero); Start-Sleep -Milliseconds 500 }   # Cancel
    $kept = ([SutramIde]::Text($editor)).Contains('unsaved')
    $guards += [pscustomobject]@{ check = 'an example asks before replacing unsaved work'; result = $(if ($dlg -and $kept) { 'PASS' } else { 'FAIL' }); detail = 'question shown: ' + [bool]$dlg + '; after Cancel the editor kept the text: ' + $kept }
    foreach ($g in $guards) { Write-Host ('{0,-12} {1}  ({2})' -f $g.result, $g.check, $g.detail) }
}

# Close: the unsaved-work guard may ask; answer No (discard). Only the IDE this script started.
[void][SutramIde]::PostMessageW($main, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)
$dlg = Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id, '#32770') | Where-Object { [SutramIde]::IsWindowVisible($_) } | Select-Object -First 1 } 3000
if ($dlg) { $b = [SutramIde]::GetDlgItem($dlg, 7); if ($b -ne [IntPtr]::Zero) { [void][SutramIde]::PostMessageW($b, 0x00F5, [IntPtr]::Zero, [IntPtr]::Zero) } }
if (-not (Wait-Until { $ip.HasExited } 8000)) { try { $ip.Kill() } catch {} }

$counts = $results | Group-Object verdict | ForEach-Object { $_.Name + '=' + $_.Count }
$summary = @('Sutram IDE, every example: ' + ($counts -join '  '),
             'IDE ' + [IO.Path]::GetFileName($ideExe) + ' ' + $ideHash, 'compiler win\sutram.exe ' + $compHash,
             'Windows ' + [Environment]::OSVersion.Version.ToString() + '  PowerShell ' + $PSVersionTable.PSVersion.ToString(),
             'opened: ' + $startShot, '')
$summary += ($results | Where-Object { $_.verdict -ne 'MATCH' } | ForEach-Object { '{0,-12} {1,-40} {2}' -f $_.verdict, $_.name, $_.detail })
if ($guards.Count) { $summary += ''; $summary += ($guards | ForEach-Object { '{0,-12} {1}  ({2})' -f $_.result, $_.check, $_.detail }) }
[IO.File]::WriteAllLines((Join-Path $OutDir 'ide-examples.txt'), [string[]]$summary, (New-Object Text.UTF8Encoding($false)))
[IO.File]::WriteAllText((Join-Path $OutDir 'ide-examples.json'), ($results | ConvertTo-Json -Depth 4), (New-Object Text.UTF8Encoding($false)))
$summary[0]
'OUT ' + $OutDir
