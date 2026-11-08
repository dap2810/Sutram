$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot;. (Join-Path $OutDir 'desktop-helper.ps1')
Add-Type -TypeDefinition @'
using System;using System.Collections.Generic;using System.Runtime.InteropServices;using System.Text;using System.Threading;
public static class ConsoleEvents {
 public class Row {public string utc;public uint eventId;public long handle;public uint pid;public string cls;public string title;public bool visible;}
 public delegate void EventProc(IntPtr hook,uint ev,IntPtr h,int obj,int child,uint thread,uint time);
 [DllImport("user32.dll")] static extern IntPtr SetWinEventHook(uint a,uint b,IntPtr mod,EventProc proc,uint pid,uint tid,uint flags);
 [DllImport("user32.dll")] static extern bool UnhookWinEvent(IntPtr h);
 [DllImport("user32.dll")] static extern bool PeekMessage(out MSG m,IntPtr h,uint a,uint b,uint remove);
 [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h,out uint p);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetClassNameW(IntPtr h,StringBuilder b,int n);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] static extern int GetWindowTextW(IntPtr h,StringBuilder b,int n);
 [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
 [StructLayout(LayoutKind.Sequential)] struct MSG {public IntPtr hwnd;public uint message;public UIntPtr wParam;public IntPtr lParam;public uint time;public int x,y;public uint priv;}
 static List<Row> rows=new List<Row>();static Thread thread;static bool stop;static EventProc cb;public static bool Ready;public static long Hook;
 public static void Start(){thread=new Thread(Run);thread.IsBackground=true;thread.Start();}
 static void Run(){cb=OnEvent;IntPtr hook=SetWinEventHook(0x8000,0x8003,IntPtr.Zero,cb,0,0,0);Hook=hook.ToInt64();Ready=true;while(!stop){MSG m;while(PeekMessage(out m,IntPtr.Zero,0,0,1)){}Thread.Sleep(5);}UnhookWinEvent(hook);}
 static void OnEvent(IntPtr hook,uint ev,IntPtr h,int obj,int child,uint thread,uint time){if(obj!=0||child!=0||h==IntPtr.Zero)return;var b=new StringBuilder(256);GetClassNameW(h,b,256);string cls=b.ToString();if(cls.IndexOf("Console",StringComparison.OrdinalIgnoreCase)<0&&cls.IndexOf("CASCADIA",StringComparison.OrdinalIgnoreCase)<0)return;uint p;GetWindowThreadProcessId(h,out p);var t=new StringBuilder(1024);GetWindowTextW(h,t,1024);lock(rows)rows.Add(new Row{utc=DateTime.UtcNow.ToString("o"),eventId=ev,handle=h.ToInt64(),pid=p,cls=cls,title=t.ToString(),visible=IsWindowVisible(h)});}
 public static Row[] Read(){lock(rows)return rows.ToArray();} public static void Stop(){stop=true;thread.Join(3000);}
}
'@
$target=Join-Path $env:LOCALAPPDATA 'Programs\Sutram\Sutram-Uninstall.exe'
$baseline=@([AcceptanceWindow]::All()|Where-Object {$_.cls -match 'Console|CASCADIA'}|ForEach-Object {$_.handle})
$r=[ordered]@{started=[DateTime]::Now.ToString('o');method='WinEvent hook for console create/destroy/show/hide plus visible-window sampling and native engine process tracking, started before Settings uninstall.';baseline_console_handles=$baseline;processes=@();samples=@();dialogs=@();window_events=@();finished=$false}
$known=@{};$watch=[Diagnostics.Stopwatch]::StartNew();$lastSave=-1;$nextProcess=0
function Save{[IO.File]::WriteAllText((Join-Path $OutDir 'uninstall-observer.json'),($r|ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false))}
[ConsoleEvents]::Start()
while(-not [ConsoleEvents]::Ready){Start-Sleep -Milliseconds 10}
$r.hook_handle=[ConsoleEvents]::Hook;if(-not $r.hook_handle){throw 'Console event hook failed'};Save
try {
while($watch.Elapsed.TotalSeconds -lt 600){
 foreach($w in [AcceptanceWindow]::All()|Where-Object {$_.cls -match 'Console|CASCADIA' -and $_.handle -notin $baseline}){
  if($w.handle -notin @($r.samples|ForEach-Object {$_.handle})){$r.samples+=@{time=[DateTime]::Now.ToString('o');handle=$w.handle;pid=$w.pid;class=$w.cls;title=$w.title}}
 }
 if($watch.Elapsed.TotalSeconds -ge $nextProcess){
  $all=@(Get-CimInstance Win32_Process -Filter "Name = 'Sutram-Uninstall.exe' OR Name = 'powershell.exe'")
  foreach($a in $all|Where-Object {$_.ExecutablePath -eq $target -or ($_.CommandLine -like '*-SelfPath*' -and $_.CommandLine.Contains($target))}){
   if(-not $known.ContainsKey([int]$a.ProcessId)){$p=Get-Process -Id $a.ProcessId -ErrorAction SilentlyContinue;if($p){[void]$p.Handle;$known[[int]$p.Id]=$p;$r.processes+=@{pid=$p.Id;parent=$a.ParentProcessId;started=$p.StartTime.ToString('o');name=$a.Name;command=$a.CommandLine};$m=[regex]::Match($a.CommandLine,'-LogPath\s+"([^"]+)"');if($m.Success){$r.log_path=$m.Groups[1].Value};Save}}
  }
  foreach($p in @($known.Values|Where-Object {-not $_.HasExited})){
   foreach($h in [SutramIde]::WindowsOf($p.Id,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)}){if($h.ToInt64() -notin @($r.dialogs|ForEach-Object {$_.handle})){$r.dialogs+=@{time=[DateTime]::Now.ToString('o');pid=$p.Id;handle=$h.ToInt64();text=[AcceptanceWindow]::VisibleTexts($h)}}}
  }
  $nextProcess=$watch.Elapsed.TotalSeconds+.15
 }
 if($watch.Elapsed.TotalSeconds-$lastSave -ge 1){$r.window_events=@([ConsoleEvents]::Read()|Where-Object {$_.handle -notin $baseline});$r.elapsed_seconds=$watch.Elapsed.TotalSeconds;Save;$lastSave=$watch.Elapsed.TotalSeconds}
 if($r.processes.Count -and @($r.processes|Where-Object {$_.name -eq 'powershell.exe'}).Count -and @($known.Values|Where-Object {-not $_.HasExited}).Count -eq 0){$r.finished=$true;break}
 Start-Sleep -Milliseconds 30
}
}finally{
 [ConsoleEvents]::Stop();$r.window_events=@([ConsoleEvents]::Read()|Where-Object {$_.handle -notin $baseline});$r.ended=[DateTime]::Now.ToString('o')
 $r.process_results=@($known.Values|ForEach-Object {$p=$_;if($p.HasExited){$p.WaitForExit()};@{pid=$p.Id;started=$p.StartTime.ToString('o');exited=$p.HasExited;exit=if($p.HasExited){$p.ExitCode}else{$null};exit_time=if($p.HasExited){$p.ExitTime.ToString('o')}else{$null}}})
 if($r.Contains('log_path') -and (Test-Path -LiteralPath $r.log_path)){Copy-Item -LiteralPath $r.log_path -Destination (Join-Path $OutDir 'uninstall-engine.log')}
 Save
}
