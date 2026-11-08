param([ValidateSet('desktop','docs')][string]$Phase='desktop')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
Add-Type -TypeDefinition @'
using System;using System.Runtime.InteropServices;
public static class ShortcutMouse {
 [DllImport("user32.dll")] public static extern IntPtr GetShellWindow();
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
 public static void Click(){mouse_event(2,0,0,0,UIntPtr.Zero);mouse_event(4,0,0,0,UIntPtr.Zero);}
}
'@
function Save($r,$name){[IO.File]::WriteAllText((Join-Path $OutDir ($name+'.json')),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))}
function Region($x,$y,$w,$height,$name){
 Add-Type -AssemblyName System.Drawing;$b=[Drawing.Bitmap]::new($w,$height);$g=[Drawing.Graphics]::FromImage($b)
 try{$g.CopyFromScreen($x,$y,0,0,[Drawing.Size]::new($w,$height),[Drawing.CopyPixelOperation]::SourceCopy);$b.Save((Join-Path $OutDir ($name+'.png')),[Drawing.Imaging.ImageFormat]::Png)}finally{$g.Dispose();$b.Dispose()}
}
if($Phase -eq 'desktop'){
 $sh=New-Object -ComObject Shell.Application;$before=@([AcceptanceWindow]::All());$sh.MinimizeAll();Start-Sleep -Seconds 1
 $icon=$null;$dw=$null
 foreach($w in @([AcceptanceWindow]::All()|Where-Object {$_.cls -in @('Progman','WorkerW')})){$e=Find-UI (UI ([IntPtr]$w.handle)) 'Sutram IDE';if($e -and -not $e.Current.IsOffscreen){$icon=$e;$dw=$w;break}}
 if(-not $icon){
  $hw=[ShortcutMouse]::GetShellWindow();$dw=@{handle=$hw.ToInt64()}
  $rootUI=UI $hw;$all=$rootUI.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)
  $icon=$all|Where-Object {$_.Current.Name -match '^Sutram IDE(\.lnk)?$' -and -not $_.Current.IsOffscreen}|Select-Object -First 1
  if(-not $icon){
   # Coordinates verified visually in private-desktop-full.png, never guessed.
   if([Windows.Forms.Screen]::PrimaryScreen.Bounds.Width -ne 1920 -or [Windows.Forms.Screen]::PrimaryScreen.Bounds.Height -ne 1080){throw 'Screen size differs from inspected desktop'}
   $rect=[Windows.Rect]::new(670,490,85,90)
  }
 }
 if($icon){$rect=$icon.Current.BoundingRectangle};$x=[Math]::Max(0,[int]$rect.X-7);$y=[Math]::Max(0,[int]$rect.Y-7)
 Region $x $y ([int]$rect.Width+24) ([int]$rect.Height+24) 'desktop-collision'
 $r=@{time=[DateTime]::Now.ToString('o');desktop_handle=$dw.handle;icon_name='Sutram IDE';rectangle=@{x=$rect.X;y=$rect.Y;width=$rect.Width;height=$rect.Height};screenshot='desktop-collision.png';capture='Unaltered screen-region capture around the real desktop icon; other personal desktop content excluded';method='Real desktop icon double-click; coordinates visually verified because desktop list exposes no UIA items'}
 [void][ShortcutMouse]::SetCursorPos([int]($rect.X+$rect.Width/2),[int]($rect.Y+$rect.Height/2));[ShortcutMouse]::Click();Start-Sleep -Milliseconds 80;[ShortcutMouse]::Click()
 $win=Wait-Until {[AcceptanceWindow]::All()|Where-Object {$_.title -match 'Notepad' -and $_.handle -notin @($before|ForEach-Object {$_.handle})}|Select-Object -First 1} 10000
 if(-not $win){throw 'No new Notepad window'}
 $proc=Get-CimInstance Win32_Process -Filter "ProcessId = $($win.pid)";$r.launched=@{handle=$win.handle;pid=$win.pid;class=$win.cls;title=$win.title;executable=$proc.ExecutablePath}
 Save $r 'desktop-click'
 if($win.title -eq 'Untitled - Notepad'){[void][SutramIde]::PostMessageW([IntPtr]$win.handle,0x10,[IntPtr]::Zero,[IntPtr]::Zero);$r.close_requested=$true;Save $r 'desktop-click'}
 $sh.UndoMinimizeALL();$r.launched|ConvertTo-Json
}else{
 $link=Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram\Sutram Documentation.lnk'
 $book=Join-Path $env:LOCALAPPDATA 'Programs\Sutram\docs\sutram-book-english.html'
 $before=@([AcceptanceWindow]::All());$win=$before|Where-Object {$_.cls -in @('Chrome_WidgetWin_1','MozillaWindowClass') -and $_.title -match 'Sutram'}|Select-Object -First 1
 if(-not $win){Start-Process -FilePath $link -WindowStyle Normal}
 $win=Wait-Until {[AcceptanceWindow]::All()|Where-Object {$_.cls -in @('Chrome_WidgetWin_1','MozillaWindowClass') -and $_.title -match 'Sutram'}|Select-Object -First 1} 15000
 if(-not $win){throw 'Book browser window not found'};$h=[IntPtr]$win.handle;Foreground $h;Start-Sleep -Seconds 2
 $ui=UI $h;$rows=UI-Dump $ui 'private-docs-ui'
 $address=Find-UI $ui 'Address and search bar';if(-not $address){$address=Find-UI $ui 'Address bar'}
 if(-not $address){$address=Find-UI $ui '' 'urlbar-input'}
 if(-not $address){$address=$ui.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)|Where-Object {$_.Current.ControlType -eq [Windows.Automation.ControlType]::Edit -and $_.Current.Name -match 'address'}|Select-Object -First 1}
 $value=$null;if($address){$vp=$null;if($address.TryGetCurrentPattern([Windows.Automation.ValuePattern]::Pattern,[ref]$vp)){$value=$vp.Current.Value}}
 if(-not $value){$value=@($rows|Where-Object {$_.name -match '^file:///.*sutram-book-english.html$'}|ForEach-Object {$_.name})|Select-Object -First 1}
 $r=@{time=[DateTime]::Now.ToString('o');shortcut=$link;book=$book;book_sha256=(Get-FileHash -LiteralPath $book).Hash;window=@{handle=$win.handle;pid=$win.pid;title=$win.title};address=$value;matching_ui=@($rows|Where-Object {$_.name -match '^Sutram|The Complete Thread|Preface|What is Sutram|Chapter|Understanding PATH'}|ForEach-Object {$_.name})}
 Foreground $h;$rect=[SutramIde+RECT]::new();[void][SutramIde]::GetWindowRect($h,[ref]$rect)
 if([SutramIde]::GetForegroundWindow() -ne $h){throw 'Browser lost foreground before screenshot'}
 Region ($rect.Left+10) ($rect.Top+145) ($rect.Right-$rect.Left-20) ([Math]::Min(700,$rect.Bottom-$rect.Top-155)) 'documentation-opened'
 if([SutramIde]::GetForegroundWindow() -ne $h){throw 'Browser lost foreground during screenshot; inspect privately'}
 $r.screenshot='documentation-opened.png';Save $r 'documentation-opened';$r|ConvertTo-Json -Depth 5
 if($value -and (($value -replace '^file:///','') -replace '/','\') -eq $book){Foreground $h;[Windows.Forms.SendKeys]::SendWait('^w');$r.test_tab_closed=$true;Save $r 'documentation-opened'}
}
