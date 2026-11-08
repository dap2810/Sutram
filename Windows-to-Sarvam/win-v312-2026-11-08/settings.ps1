param([ValidateSet('open','inspect','search','menu','uninstall','confirm')][string]$Action='open')
$ErrorActionPreference='Stop';$Evidence=$PSScriptRoot;. (Join-Path $Evidence 'desktop-helper.ps1');$script:captureWarnings=@()
$OutDir=Join-Path (Split-Path (Split-Path $Evidence -Parent) -Parent) 'build/native-v312'
if($Action -eq 'open'){Start-Process 'ms-settings:appsfeatures' -WindowStyle Normal;Start-Sleep -Seconds 3}
$w=@([AcceptanceWindow]::All()|Where-Object {$_.title -eq 'Settings' -and $_.cls -eq 'ApplicationFrameWindow'})
if($w.Count -ne 1){throw 'Settings window not unique'}
$h=[IntPtr]$w[0].handle;Foreground $h;$ui=UI $h
function CaptureApps([string]$Name){
 Foreground $h
 $search=Find-UI $ui '' 'SystemSettings_StorageSense_AppSizesListFilter_DisplayStringValue'
 if(-not $search){throw 'No application search region'}
 $rect=$search.Current.BoundingRectangle;$wr=[SutramIde+RECT]::new();[void][SutramIde]::GetWindowRect($h,[ref]$wr)
 $x=[int]$rect.Left-10;$y=[int]$rect.Top-55;$width=$wr.Right-$x-20;$height=[Math]::Min(490,$wr.Bottom-$y-20)
 Add-Type -AssemblyName System.Drawing
 $bmp=[Drawing.Bitmap]::new($width,$height);$g=[Drawing.Graphics]::FromImage($bmp)
 try{$g.CopyFromScreen($x,$y,0,0,[Drawing.Size]::new($width,$height));$bmp.Save((Join-Path $Evidence ($Name+'.png')),[Drawing.Imaging.ImageFormat]::Png)}finally{$g.Dispose();$bmp.Dispose()}
}
if($Action -eq 'inspect'){CaptureApps 'settings-uninstall-final-recheck'}
if($Action -eq 'search'){
 $e=Find-UI $ui '' 'SystemSettings_StorageSense_AppSizesListFilter_DisplayStringValue'
 if(-not $e){throw 'No search edit'}
 $e.GetCurrentPattern([Windows.Automation.ValuePattern]::Pattern).SetValue('Sutram');Start-Sleep -Seconds 2
}
if($Action -eq 'menu'){
 $app=Find-UI $ui '' 'Sutram_ListItem';if(-not $app -or $app.Current.Name -notlike 'Sutram, 1.0.312,*'){throw 'v312 Settings entry missing'}
 $button=Find-UI $app '' 'AppOptionsButton';if(-not $button){throw 'No Sutram options button'}
 UI-Invoke $button;Start-Sleep -Milliseconds 300
}
if($Action -eq 'uninstall'){
 $app=Find-UI $ui '' 'Sutram_ListItem';if(-not $app -or $app.Current.Name -notlike 'Sutram, 1.0.312,*'){throw 'v312 Settings entry missing'}
 $observer=Get-Content -LiteralPath (Join-Path $Evidence 'uninstall-observer.json') -Raw|ConvertFrom-Json
 if($observer.finished -or -not $observer.hook_handle){throw 'Observer not ready'}
 $button=Find-UI $ui '' 'SystemSettings_StorageSense_AppSizesList_UninstallButton_UninstallButton'
 if(-not $button){UI-Invoke (Find-UI $app '' 'AppOptionsButton');Start-Sleep -Milliseconds 250;$button=Find-UI $ui '' 'SystemSettings_StorageSense_AppSizesList_UninstallButton_UninstallButton'}
 if(-not $button){throw 'Uninstall menu item missing'}
 @{menu_clicked=[DateTime]::Now.ToString('o');app=$app.Current.Name}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $Evidence 'settings-uninstall-start.json') -Encoding UTF8
 UI-Invoke $button;Start-Sleep -Milliseconds 400;CaptureApps 'settings-uninstall-confirmation'
}
if($Action -eq 'confirm'){
 $button=Find-UI $ui '' 'SystemSettings_StorageSense_AppSizesList_UninstallButton_ConfirmButton'
 if(-not $button){
  $app=Find-UI $ui '' 'Sutram_ListItem';if(-not $app -or $app.Current.Name -notlike 'Sutram, 1.0.312,*'){throw 'Wrong app'}
  UI-Invoke (Find-UI $app '' 'AppOptionsButton');Start-Sleep -Milliseconds 200
  UI-Invoke (Find-UI $ui '' 'SystemSettings_StorageSense_AppSizesList_UninstallButton_UninstallButton');Start-Sleep -Milliseconds 200
  $button=Find-UI $ui '' 'SystemSettings_StorageSense_AppSizesList_UninstallButton_ConfirmButton'
 }
 if(-not $button){throw 'Confirmation control missing'}
 $r=[ordered]@{confirmed=[DateTime]::Now.ToString('o');observations=@()};$watch=[Diagnostics.Stopwatch]::StartNew()
 UI-Invoke $button
 while($watch.Elapsed.TotalSeconds -lt 120){
  $app=Find-UI $ui '' 'Sutram_ListItem'
  $r.observations+=@{seconds=$watch.Elapsed.TotalSeconds;app_visible=($app -and -not $app.Current.IsOffscreen)}
  $obs=Get-Content -LiteralPath (Join-Path $Evidence 'uninstall-observer.json') -Raw|ConvertFrom-Json
  if($obs.finished){$r.engine_finished_seen=[DateTime]::Now.ToString('o');$r.elapsed_seconds=$watch.Elapsed.TotalSeconds;break}
  Start-Sleep -Milliseconds 500
 }
 Start-Sleep -Seconds 2;CaptureApps 'settings-uninstall-final'
 $r.final_app_exists=[bool](Find-UI $ui '' 'Sutram_ListItem');$r.ended=[DateTime]::Now.ToString('o')
 [IO.File]::WriteAllText((Join-Path $Evidence 'settings-uninstall.json'),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
}
$rows=UI-Dump $ui ('settings-'+$Action)
$rows|ForEach-Object {[pscustomobject]$_}|Where-Object {-not $_.offscreen -and ($_.name -match 'Sutram|Uninstall|Search|installed|found|More options' -or $_.class -match 'Flyout')}|Select-Object name,id,class,type,handle|ConvertTo-Json
