$ErrorActionPreference='Stop'
Add-Type -TypeDefinition @'
using System;using System.Runtime.InteropServices;
public static class SourceFontMeasure {
 [DllImport("user32.dll")] static extern IntPtr GetDC(IntPtr h);
 [DllImport("user32.dll")] static extern int ReleaseDC(IntPtr h,IntPtr dc);
 [DllImport("gdi32.dll",CharSet=CharSet.Unicode)] static extern IntPtr CreateFontW(int height,int width,int escapement,int orientation,int weight,uint italic,uint underline,uint strike,uint charset,uint outprec,uint clipprec,uint quality,uint pitch,string face);
 [DllImport("gdi32.dll")] static extern IntPtr SelectObject(IntPtr dc,IntPtr obj);
 [DllImport("gdi32.dll")] static extern bool DeleteObject(IntPtr obj);
 [DllImport("gdi32.dll",CharSet=CharSet.Unicode)] static extern bool GetTextExtentPoint32W(IntPtr dc,string text,int len,out SIZE size);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int DrawTextW(IntPtr dc,string text,int len,ref RECT rect,uint format);
 [StructLayout(LayoutKind.Sequential)] struct SIZE {public int width,height;}
 [StructLayout(LayoutKind.Sequential)] struct RECT {public int left,top,right,bottom;}
 public static int[] Measure(string text,int width){IntPtr dc=GetDC(IntPtr.Zero);IntPtr font=CreateFontW(-19,0,0,0,400,0,0,0,1,0,0,0,0,"Segoe UI");if(font==IntPtr.Zero)throw new Exception("CreateFont failed");IntPtr old=SelectObject(dc,font);if(old==IntPtr.Zero||old.ToInt64()==-1)throw new Exception("SelectObject failed");try{SIZE size;if(!GetTextExtentPoint32W(dc,text,text.Length,out size))throw new Exception("Measure failed");RECT r=new RECT{right=width};int h=DrawTextW(dc,text,text.Length,ref r,0x410);return new int[]{size.width,size.height,h,r.right};}finally{SelectObject(dc,old);DeleteObject(font);ReleaseDC(IntPtr.Zero,dc);}}
}
'@
$text='Please read the following license agreement. You must accept the terms to continue.'
$r=@{scope='Source-based layout calculation using a locally created Segoe UI -19/400 font; not an in-process measurement of the installer.';source_label_width=530;source_label_height=26;source_license_body_y=94;source_label_y=62;measurements=[SourceFontMeasure]::Measure($text,530);measurement_fields=@('single_line_width','font_height','required_wordwrap_height','wordwrap_width');discarded_foreign_font_measurement='label-capture.json gdi_metrics did not verify SelectObject success and contradicts visible clipping. It is not used as layout evidence.'}
[IO.File]::WriteAllText((Join-Path $PSScriptRoot 'label-layout-model.json'),($r|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
$r|ConvertTo-Json -Depth 5
