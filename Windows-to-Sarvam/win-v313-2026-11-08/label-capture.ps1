$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot;. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
$setup=Join-Path (Split-Path (Split-Path $OutDir -Parent) -Parent) 'artifacts/available-Sutram-Setup.exe'
$identity=Get-Content -LiteralPath (Join-Path $OutDir 'availability.json') -Encoding UTF8 -Raw|ConvertFrom-Json
if((Get-FileHash -LiteralPath $setup).Hash -ne $identity.available_setup_sha256){throw 'Setup hash differs'}
$full='Please read the following license agreement. You must accept the terms to continue.'
Add-Type -TypeDefinition @'
using System;using System.Collections.Generic;using System.Runtime.InteropServices;using System.Text;
public static class LabelMeasure {
 public delegate bool EnumProc(IntPtr h,IntPtr l);
 [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr p,EnumProc cb,IntPtr l);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetWindowTextW(IntPtr h,StringBuilder b,int n);
 [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h,out RECT r);
 [DllImport("user32.dll")] public static extern uint GetDpiForWindow(IntPtr h);
 [DllImport("user32.dll",EntryPoint="GetWindowLongPtrW")] public static extern IntPtr GetWindowLongPtr(IntPtr h,int index);
 [DllImport("user32.dll")] static extern IntPtr GetDC(IntPtr h);
 [DllImport("user32.dll")] static extern int ReleaseDC(IntPtr h,IntPtr dc);
 [DllImport("gdi32.dll")] static extern IntPtr SelectObject(IntPtr dc,IntPtr o);
 [DllImport("gdi32.dll",CharSet=CharSet.Unicode)] static extern bool GetTextExtentPoint32W(IntPtr dc,string s,int n,out SIZE size);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int DrawTextW(IntPtr dc,string s,int n,ref RECT r,uint flags);
 [StructLayout(LayoutKind.Sequential)] public struct RECT {public int Left,Top,Right,Bottom;}
 [StructLayout(LayoutKind.Sequential)] public struct SIZE {public int Width,Height;}
 public static IntPtr Find(IntPtr parent,string text){IntPtr found=IntPtr.Zero;EnumChildWindows(parent,delegate(IntPtr h,IntPtr l){var b=new StringBuilder(4096);GetWindowTextW(h,b,b.Capacity);if(b.ToString()==text)found=h;return true;},IntPtr.Zero);return found;}
 public static int[] Measure(IntPtr h,IntPtr font,string s){RECT r;GetClientRect(h,out r);IntPtr dc=GetDC(h);IntPtr old=SelectObject(dc,font);try{SIZE z;GetTextExtentPoint32W(dc,s,s.Length,out z);RECT wrap=new RECT{Right=r.Right};int height=DrawTextW(dc,s,s.Length,ref wrap,0x410);return new int[]{r.Right,r.Bottom,z.Width,z.Height,height,wrap.Right};}finally{SelectObject(dc,old);ReleaseDC(h,dc);}}
}
'@
$r=[ordered]@{started=[DateTime]::Now.ToString('o');scope='PRE-FIX v312 only; v313 unavailable';setup_sha256=$identity.available_setup_sha256;expected_text=$full;installation_attempted=$false}
$p=Start-Process -FilePath $setup -WindowStyle Normal -PassThru;[void]$p.Handle;$r.pid=$p.Id;$r.process_started=$p.StartTime.ToString('o')
try{
 $main=Wait-Until {[SutramIde]::WindowsOf($p.Id,'SutramWizardWindow')|Select-Object -First 1} 15000
 if(-not $main){throw 'Wizard not found'}
 [void][SutramIde]::PostMessageW([SutramIde]::GetDlgItem($main,2002),0xF5,[IntPtr]::Zero,[IntPtr]::Zero);Start-Sleep -Milliseconds 300
 $label=[LabelMeasure]::Find($main,$full);if($label -eq [IntPtr]::Zero){throw 'Instruction label not found'}
 $r.actual_control_text=[SutramIde]::Text($label);$r.native_style=[LabelMeasure]::GetWindowLongPtr($main,-16).ToInt64();$r.resizable_border=($r.native_style -band 0x40000) -ne 0;$r.window_dpi=[LabelMeasure]::GetDpiForWindow($main)
 $r.gdi_metrics=[LabelMeasure]::Measure($label,[IntPtr][SutramIde]::Send($label,0x31,0,0,3000),$full)
 $r.gdi_metrics_fields=@('client_width','client_height','full_text_single_line_width','font_height','required_wordwrap_height','wordwrap_width')
 $wr=[SutramIde+RECT]::new();[void][SutramIde]::GetWindowRect($main,[ref]$wr);$r.window_rect=$wr
 Foreground $main;$r.full_screenshot=Shot $main 'prefixed-licence-default'
 if(-not $r.full_screenshot){throw 'Unable to capture intended wizard'}
 Foreground $main;$lr=[SutramIde+RECT]::new();[void][SutramIde]::GetWindowRect($label,[ref]$lr);$r.label_screen_rect=$lr
 Add-Type -AssemblyName System.Drawing
 $width=$lr.Right-$lr.Left;$height=$lr.Bottom-$lr.Top
 $bmp=[Drawing.Bitmap]::new($width,$height);$g=[Drawing.Graphics]::FromImage($bmp)
 try{$g.CopyFromScreen($lr.Left,$lr.Top,0,0,[Drawing.Size]::new($width,$height));$bmp.Save((Join-Path $OutDir 'prefixed-instruction-crop.png'),[Drawing.Imaging.ImageFormat]::Png)}finally{$g.Dispose();$bmp.Dispose()}
}finally{
 if($main -and -not $p.HasExited){[void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero)}
 $r.closed_without_install=$p.WaitForExit(5000);$r.capture_warnings=@($script:captureWarnings);$r.ended=[DateTime]::Now.ToString('o')
 [IO.File]::WriteAllText((Join-Path $OutDir 'label-capture.json'),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
}
$r|ConvertTo-Json -Depth 6
