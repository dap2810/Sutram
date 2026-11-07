$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'ui-helper.ps1')
$run=Get-Content -LiteralPath (Join-Path $OutDir 'upgrade.json') -Raw|ConvertFrom-Json
$source=[SutramIde]::WindowsOf([uint32]$run.pid,'SutramWizardWindow')|Select-Object -First 1
if(-not $source){throw 'Owned wizard window missing'}
Add-Type -ReferencedAssemblies System.Windows.Forms,System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Windows.Forms;
using System.Runtime.InteropServices;
public static class SutramDwmCapture {
    [StructLayout(LayoutKind.Sequential)] public struct Rect { public int Left, Top, Right, Bottom; }
    [StructLayout(LayoutKind.Sequential)] public struct SizeNative { public int Width, Height; }
    [StructLayout(LayoutKind.Sequential)] public struct Props {
        public uint Flags; public Rect Destination, Source; public byte Opacity;
        [MarshalAs(UnmanagedType.Bool)] public bool Visible;
        [MarshalAs(UnmanagedType.Bool)] public bool ClientOnly;
    }
    [DllImport("user32.dll")] static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
    [DllImport("user32.dll")] static extern bool PrintWindow(IntPtr h, IntPtr dc, uint flags);
    [DllImport("dwmapi.dll")] static extern int DwmRegisterThumbnail(IntPtr dst, IntPtr src, out IntPtr thumb);
    [DllImport("dwmapi.dll")] static extern int DwmQueryThumbnailSourceSize(IntPtr thumb, out SizeNative size);
    [DllImport("dwmapi.dll")] static extern int DwmUpdateThumbnailProperties(IntPtr thumb, ref Props properties);
    [DllImport("dwmapi.dll")] static extern int DwmUnregisterThumbnail(IntPtr thumb);
    static void Check(int result) { if(result != 0) Marshal.ThrowExceptionForHR(result); }
    public static void Save(IntPtr source, string path) {
        SetProcessDPIAware();
        using(Form form = new Form()) {
            form.FormBorderStyle=FormBorderStyle.None; form.ShowInTaskbar=false; form.TopMost=true;
            form.StartPosition=FormStartPosition.Manual; form.Location=new Point(0,0);
            IntPtr thumb=IntPtr.Zero; Exception failure=null;
            try {
                Check(DwmRegisterThumbnail(form.Handle, source, out thumb));
                SizeNative size; Check(DwmQueryThumbnailSourceSize(thumb, out size));
                if(size.Width<=0 || size.Height<=0) throw new Exception("Invalid source size");
                Rectangle screen=Screen.PrimaryScreen.Bounds;
                double scale=Math.Min(1.0,Math.Min((double)screen.Width/size.Width,(double)screen.Height/size.Height));
                int w=(int)(size.Width*scale), h=(int)(size.Height*scale);
                form.ClientSize=new Size(w,h);
                Props props=new Props(); props.Flags=1|4|8|16; props.Opacity=255; props.Visible=true; props.ClientOnly=false;
                props.Destination=new Rect {Left=0,Top=0,Right=w,Bottom=h};
                Check(DwmUpdateThumbnailProperties(thumb,ref props));
                using(Timer timer=new Timer()) {
                    timer.Interval=1200;
                    timer.Tick += delegate {
                        timer.Stop();
                        try {
                            SetWindowPos(form.Handle,new IntPtr(-1),0,0,0,0,0x43);
                            Application.DoEvents();
                            using(Bitmap bitmap=new Bitmap(w,h)) using(Graphics graphics=Graphics.FromImage(bitmap)) {
                                IntPtr dc=graphics.GetHdc();
                                try {if(!PrintWindow(form.Handle,dc,2))throw new Exception("Preview PrintWindow failed");}
                                finally {graphics.ReleaseHdc(dc);}
                                bitmap.Save(path,System.Drawing.Imaging.ImageFormat.Png);
                            }
                        } catch(Exception ex) {failure=ex;}
                        form.Close();
                    };
                    form.Shown += delegate {timer.Start();};
                    Application.Run(form);
                }
                if(failure!=null)throw failure;
            } finally {if(thumb!=IntPtr.Zero)DwmUnregisterThumbnail(thumb);}
        }
    }
}
'@
$path=Join-Path $OutDir 'upgrade-stalled-dwm.png'
[SutramDwmCapture]::Save($source,$path)
@{observed=[DateTime]::Now.ToString('o');source_pid=$run.pid;source_window=$source.ToInt64();method='Desktop Window Manager thumbnail of the existing suspended wizard, captured from a temporary preview';image='upgrade-stalled-dwm.png';installer_messages_sent=$false}|ConvertTo-Json|Set-Content (Join-Path $OutDir 'dwm-screenshot.json') -Encoding UTF8
Write-Output $path
