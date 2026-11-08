. (Join-Path $PSScriptRoot 'ui-helper.ps1')
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -AssemblyName System.Windows.Forms
if(-not ('AcceptanceWindow' -as [type])){Add-Type -TypeDefinition @'
using System; using System.Collections.Generic; using System.Runtime.InteropServices; using System.Text;
public class AcceptanceWindow {
 public long handle; public uint pid; public string cls; public string title;
 public delegate bool EnumProc(IntPtr h,IntPtr l);
 [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb,IntPtr l);
 [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr h,EnumProc cb,IntPtr l);
 [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
 [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h,out uint pid);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetClassNameW(IntPtr h,StringBuilder b,int n);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetWindowTextW(IntPtr h,StringBuilder b,int n);
 [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h,IntPtr after,int x,int y,int w,int ht,uint flags);
 [DllImport("user32.dll")] static extern bool AttachThreadInput(uint a,uint b,bool attach);
 [DllImport("user32.dll")] static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] static extern bool BringWindowToTop(IntPtr h);
 [DllImport("kernel32.dll")] static extern uint GetCurrentThreadId();
 public static void Focus(IntPtr h){uint ignored;uint current=GetCurrentThreadId();uint fg=GetWindowThreadProcessId(GetForegroundWindow(),out ignored);uint target=GetWindowThreadProcessId(h,out ignored);bool a=fg!=current&&AttachThreadInput(current,fg,true);bool b=target!=current&&target!=fg&&AttachThreadInput(current,target,true);try{BringWindowToTop(h);SetForegroundWindow(h);}finally{if(b)AttachThreadInput(current,target,false);if(a)AttachThreadInput(current,fg,false);}}
 public static AcceptanceWindow[] All(){var rows=new List<AcceptanceWindow>();EnumWindows(delegate(IntPtr h,IntPtr l){if(IsWindowVisible(h)){uint p;GetWindowThreadProcessId(h,out p);var c=new StringBuilder(256);var t=new StringBuilder(1024);GetClassNameW(h,c,256);GetWindowTextW(h,t,1024);rows.Add(new AcceptanceWindow{handle=h.ToInt64(),pid=p,cls=c.ToString(),title=t.ToString()});}return true;},IntPtr.Zero);return rows.ToArray();}
 public static string[] VisibleTexts(IntPtr parent){var rows=new List<string>();EnumChildWindows(parent,delegate(IntPtr h,IntPtr l){if(IsWindowVisible(h)){var t=new StringBuilder(8192);GetWindowTextW(h,t,8192);if(t.Length>0)rows.Add(t.ToString());}return true;},IntPtr.Zero);return rows.ToArray();}
}
'@}
function UI([IntPtr]$H){return [Windows.Automation.AutomationElement]::FromHandle($H)}
function Find-UI($Element,[string]$Name,[string]$Id=''){
 $prop=[Windows.Automation.AutomationElement]::NameProperty;$value=$Name
 if($Id){$prop=[Windows.Automation.AutomationElement]::AutomationIdProperty;$value=$Id}
 return $Element.FindFirst([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.PropertyCondition]::new($prop,$value))
}
function UI-Invoke($Element){$p=$Element.GetCurrentPattern([Windows.Automation.InvokePattern]::Pattern);$p.Invoke()}
function UI-Dump($Element,[string]$Name){
 $all=$Element.FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.Condition]::TrueCondition)
 $rows=@();foreach($e in $all){$c=$e.Current;$rows+=@{name=$c.Name;id=$c.AutomationId;class=$c.ClassName;type=$c.ControlType.ProgrammaticName;offscreen=$c.IsOffscreen;handle=$c.NativeWindowHandle;pid=$c.ProcessId}}
 [IO.File]::WriteAllText((Join-Path $OutDir ($Name+'.json')),($rows|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false));return $rows
}
function Foreground([IntPtr]$H){
 $ok=Wait-Until {[void][SutramIde]::ShowWindow($H,9);[AcceptanceWindow]::Focus($H);Start-Sleep -Milliseconds 150;[SutramIde]::GetForegroundWindow() -eq $H} 5000
 if(-not $ok){throw 'Intended window not foreground; refusing keyboard input'}
}
