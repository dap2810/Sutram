param([ValidateSet('doubleclick','openwith')][string]$Phase='doubleclick')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
Add-Type -TypeDefinition @'
using System;using System.Runtime.InteropServices;
public static class FirstRunMouse {
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] static extern void mouse_event(uint f,uint x,uint y,uint d,UIntPtr e);
 public static void Click(bool right){mouse_event(right?8u:2u,0,0,0,UIntPtr.Zero);mouse_event(right?16u:4u,0,0,0,UIntPtr.Zero);}
}
'@
$shell=New-Object -ComObject Shell.Application
function Save($o,$name){[IO.File]::WriteAllText((Join-Path $OutDir ($name+'.json')),($o|ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false))}
function Open-Folder($path){
 $previous=@($shell.Windows()|ForEach-Object {$_.HWND})
 Start-Process -FilePath explorer.exe -ArgumentList ('"'+$path+'"') -WindowStyle Normal
 $w=Wait-Until {@($shell.Windows())|Where-Object {try{$_.HWND -notin $previous -and $_.Document.Folder.Self.Path -eq $path}catch{$false}}|Select-Object -First 1} 5000
 if(-not $w){$w=@($shell.Windows())|Where-Object {try{$_.Document.Folder.Self.Path -eq $path}catch{$false}}|Select-Object -Last 1}
 if(-not $w){throw 'Explorer folder did not open'};return $w
}
function File-Element($h){$ui=UI $h;$f=Find-UI $ui 'hello.sm';if(-not $f){$f=Find-UI $ui 'hello'};if(-not $f){UI-Dump $ui 'private-explorer-ui'|Out-Null;throw 'File element absent'};return $f}
function Mouse-File($f,$right=$false){$rect=$f.Current.BoundingRectangle;if($rect.IsEmpty){throw 'File has no screen rectangle'};[void][FirstRunMouse]::SetCursorPos([int]($rect.X+$rect.Width/2),[int]($rect.Y+$rect.Height/2));[FirstRunMouse]::Click($right)}
function Observe-Ide($name,$expected,$prior){
 $p=Wait-Until {Get-Process -Name sutram-ide-gui -ErrorAction SilentlyContinue|Where-Object {$_.Id -notin $prior}|Select-Object -First 1} 12000
 if(-not $p){Save @([AcceptanceWindow]::All()) ('private-'+$name+'-windows');throw 'No new IDE; inspect shell chooser before continuing'}
 $h=Wait-Until {[SutramIde]::WindowsOf($p.Id,'SutramNativeGUIWindow')|Select-Object -First 1} 10000
 if(-not $h){throw 'IDE window absent'};Start-Sleep -Milliseconds 600;Foreground $h
 $editor=[SutramIde]::Text([SutramIde]::GetDlgItem($h,201))
 $r=@{pid=$p.Id;started=$p.StartTime.ToString('o');title=[SutramIde]::Text($h);editor=$editor;output=[SutramIde]::Text([SutramIde]::GetDlgItem($h,203));status=[SutramIde]::Text([SutramIde]::GetDlgItem($h,206));expected=$expected;loaded=($editor.Replace("`r`n","`n").TrimEnd() -ceq $expected.Replace("`r`n","`n").TrimEnd());screenshot=(Shot $h ('shell-'+$name));dialogs=@([SutramIde]::WindowsOf($p.Id,'#32770')|ForEach-Object {[AcceptanceWindow]::VisibleTexts($_)})}
 [void][SutramIde]::PostMessageW($h,0x10,[IntPtr]::Zero,[IntPtr]::Zero);$r.closed=$p.WaitForExit(5000)
 if(-not $r.closed){Save $r ('shell-'+$name);throw 'IDE did not close; no forced termination'};return $r
}
$cases=@(@{name='spaces';folder='My Sutram Files';marker='FIRST_RUN_SPACES'},@{name='devanagari';folder=([string][char]0x0938+[char]0x0942+[char]0x0924+[char]0x094D+[char]0x0930+[char]0x092E+[char]0x094D);marker='FIRST_RUN_DEVANAGARI'},@{name='ampersand';folder='Ampersand & Files';marker='FIRST_RUN_AMPERSAND'},@{name='percent';folder='Percent %USERNAME% Files';marker='FIRST_RUN_PERCENT'})
if($Phase -eq 'doubleclick'){
 foreach($c in $cases){
  $rec=Join-Path $OutDir ('shell-'+$c.name+'.json');if(Test-Path -LiteralPath $rec){continue}
  $folder=Join-Path $OutDir ('cases\'+$c.folder);New-Item -ItemType Directory -Path $folder -Force|Out-Null
  $file=Join-Path $folder 'hello.sm';$code='mukhya() {'+"`r`n"+'    likha("'+$c.marker+'")'+"`r`n}`r`n"
  if(Test-Path -LiteralPath $file){if([IO.File]::ReadAllText($file) -cne $code){throw 'Fixture differs'}}else{[IO.File]::WriteAllText($file,$code,[Text.UTF8Encoding]::new($false))}
  $w=Open-Folder $folder;$h=[IntPtr]$w.HWND;Foreground $h;$f=File-Element $h
  $prior=@(Get-Process -Name sutram-ide-gui -ErrorAction SilentlyContinue|ForEach-Object {$_.Id})
  Mouse-File $f;Start-Sleep -Milliseconds 80;Mouse-File $f
  $r=Observe-Ide $c.name $code $prior;$r.path=$file;$r.method='Two real left clicks in Explorer, 80 ms apart';$r.file_sha256=(Get-FileHash -LiteralPath $file).Hash;Save $r ('shell-'+$c.name)
  [void][SutramIde]::PostMessageW($h,0x10,[IntPtr]::Zero,[IntPtr]::Zero)
  Write-Host "$($c.name): loaded=$($r.loaded); closed=$($r.closed)"
 }
}else{
 $folder=Join-Path $OutDir 'cases\My Sutram Files';$w=Open-Folder $folder;$h=[IntPtr]$w.HWND;Foreground $h;[Windows.Forms.SendKeys]::SendWait('{ESC}');$f=File-Element $h
 $rect=$f.Current.BoundingRectangle;Write-Host ('File rectangle '+$rect+' type '+$f.Current.ControlType.ProgrammaticName)
 Mouse-File $f $true;Start-Sleep -Milliseconds 1000
 $menu=Wait-Until {(UI $h).FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.PropertyCondition]::new([Windows.Automation.AutomationElement]::AutomationIdProperty,'openas'))|Where-Object {-not $_.Current.IsOffscreen -and $_.Current.BoundingRectangle.Width -gt 0}|Select-Object -Last 1} 3000
 if(-not $menu){UI-Dump (UI $h) 'private-openwith-missing'|ForEach-Object {[pscustomobject]$_}|Where-Object {$_.type -eq 'ControlType.MenuItem'}|Select-Object name,id;throw 'Open with item absent'}
 $rect=$menu.Current.BoundingRectangle;Write-Host ('Open with rectangle '+$rect);[void][FirstRunMouse]::SetCursorPos([int]($rect.X+$rect.Width/2),[int]($rect.Y+$rect.Height/2));[FirstRunMouse]::Click($false)
 Start-Sleep -Milliseconds 1200
 $rows=UI-Dump (UI $h) 'private-openwith-submenu';$rows|Where-Object {$_.name -match 'Open|Sutram|Choose|Show more|app'}|ForEach-Object {[pscustomobject]$_}|Select-Object name,id,type
 Save @{handle=$h.ToInt64();new_windows=@([AcceptanceWindow]::All()|Where-Object {$_.cls -in @('#32768','Microsoft.UI.Content.PopupWindowSiteBridge','XamlExplorerHostIslandWindow')})} 'openwith-context'
 $fg=[SutramIde]::GetForegroundWindow();Write-Host ('After hover foreground '+$fg+' '+[SutramIde]::ClassOf($fg)+' '+[SutramIde]::Text($fg))
 $null=Shot $h 'openwith-menu'
 UI-Dump (UI $fg) 'private-openwith-hover'|ForEach-Object {[pscustomobject]$_}|Where-Object {$_.name -match 'Open|Sutram|Choose|app'}|Select-Object name,id,type
 $choice=(UI $h).FindAll([Windows.Automation.TreeScope]::Descendants,[Windows.Automation.PropertyCondition]::new([Windows.Automation.AutomationElement]::NameProperty,'sutram-ide-gui'))|Where-Object {-not $_.Current.IsOffscreen -and $_.Current.ControlType -eq [Windows.Automation.ControlType]::MenuItem}|Select-Object -First 1
 if(-not $choice){throw 'IDE choice absent'}
 $rect=$choice.Current.BoundingRectangle;$prior=@(Get-Process -Name sutram-ide-gui -ErrorAction SilentlyContinue|ForEach-Object {$_.Id})
 [void][FirstRunMouse]::SetCursorPos([int]($rect.X+$rect.Width/2),[int]($rect.Y+$rect.Height/2));[FirstRunMouse]::Click($false)
 $file=Join-Path $folder 'hello.sm';$r=Observe-Ide 'openwith' ([IO.File]::ReadAllText($file)) $prior;$r.path=$file;$r.method='Explorer right click -> Open with -> sutram-ide-gui';$r.default_association_changed=$false;Save $r 'shell-openwith'
 Write-Host ('Open with loaded='+$r.loaded)
}
