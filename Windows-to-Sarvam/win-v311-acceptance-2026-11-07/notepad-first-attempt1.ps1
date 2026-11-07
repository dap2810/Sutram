param([ValidateSet('type','save')][string]$Phase='type')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot;$Root=Split-Path (Split-Path $OutDir -Parent) -Parent
. (Join-Path $OutDir 'desktop-helper.ps1');$script:captureWarnings=@()
$saved=Get-Content (Join-Path $OutDir 'notepad-opened.json') -Raw|ConvertFrom-Json;$h=[IntPtr]$saved.window.handle
$p=Get-Process -Id $saved.window.pid
if($p.StartTime.ToUniversalTime() -ne ([DateTime]::Parse($saved.process_started)).ToUniversalTime()){throw 'Notepad process identity changed'}
$target=Join-Path $Root 'build\native-v311-acceptance\first.sm'
if($Phase -eq 'type'){
 if(Test-Path $target){throw 'first.sm already exists'}
 $editor=Find-UI (UI $h) 'Text editor';if(-not $editor){throw 'Notepad editor not found'}
 Foreground $h;$editor.SetFocus()
 $text="mukhya() {`r`n    likha(`"namaste`")`r`n}`r`n"
 foreach($ch in $text.ToCharArray()){if([int]$ch -ne 10){[void][SutramIde]::Send([IntPtr]$editor.Current.NativeWindowHandle,0x102,[int]$ch,0,3000)}}
 $entered=[SutramIde]::Text([IntPtr]$editor.Current.NativeWindowHandle)
 if($entered.Replace("`r`n","`n").Replace("`r","`n") -ne $text.Replace("`r`n","`n")){throw 'Notepad entered text mismatch'}
 $null=Shot $h 'notepad-first-typed';[Windows.Forms.SendKeys]::SendWait('^s');Start-Sleep -Milliseconds 700
 $dialog=Wait-Until {[SutramIde]::WindowsOf($p.Id,'#32770')|Where-Object {[SutramIde]::IsWindowVisible($_)}|Select-Object -First 1} 5000
 if(-not $dialog){throw 'Save dialog did not appear'}
 $null=UI-Dump (UI $dialog) 'notepad-save-dialog-ui';$null=Shot $dialog 'notepad-save-dialog'
 [IO.File]::WriteAllText((Join-Path $OutDir 'notepad-entered.json'),(@{method='WM_CHAR typing into the actual Notepad text editor, then Ctrl+S; no source file prewritten';entered=$entered;target=$target;pid=$p.Id;dialog=$dialog.ToInt64()}|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
}else{
 $r=Get-Content (Join-Path $OutDir 'notepad-entered.json') -Raw|ConvertFrom-Json;$dialog=[IntPtr]$r.dialog;$ui=UI $dialog
 $filename=Find-UI $ui 'File name:'
 if(-not $filename){throw 'Save filename field not found'}
 $value=$filename.GetCurrentPattern([Windows.Automation.ValuePattern]::Pattern)
 $value.SetValue('"'+$target+'"')
 $save=Find-UI $ui 'Save';if(-not $save){throw 'Save button not found'};UI-Invoke $save
 if(-not (Wait-Until {Test-Path -LiteralPath $target} 5000)){throw 'Notepad did not save first.sm'}
 $bytes=[IO.File]::ReadAllBytes($target);$actual=[IO.File]::ReadAllText($target)
 if($actual.Replace("`r`n","`n") -ne "mukhya() {`n    likha(`"namaste`")`n}`n"){throw 'Saved source differs'}
 Copy-Item -LiteralPath $target -Destination (Join-Path $OutDir 'first.sm')
 $shot=Shot $h 'notepad-first-saved'
 [void][SutramIde]::PostMessageW($h,0x10,[IntPtr]::Zero,[IntPtr]::Zero);[void]$p.WaitForExit(5000)
 [IO.File]::WriteAllText((Join-Path $OutDir 'notepad-saved.json'),(@{source=$target;sha256=(Get-FileHash $target).Hash;bytes=$bytes.Length;text=$actual;screenshot=$shot;process_exited=$p.HasExited}|ConvertTo-Json),[Text.UTF8Encoding]::new($false))
}
