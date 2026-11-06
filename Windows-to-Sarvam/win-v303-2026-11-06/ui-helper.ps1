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
