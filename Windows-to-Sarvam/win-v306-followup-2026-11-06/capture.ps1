param([int]$TargetProcess,[ValidateSet('Print','Screen')][string]$Mode='Print')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
. (Join-Path $OutDir 'ui-helper.ps1')
$h=[SutramIde]::WindowsOf([uint32]$TargetProcess,'SutramWizardWindow')|Select-Object -First 1
if(-not $h){throw 'Test wizard window not found'}
if($Mode -eq 'Print'){Write-Output (Shot $h 'upgrade-stalled');exit}
# Bounded caller uses this only if PrintWindow cannot return for a hung UI.
# Capture only the selected wizard rectangle; inspect the resulting image before
# publishing because an externally suspended window may not accept foreground focus.
$originalRect=[SutramIde+RECT]::new();[void][SutramIde]::GetWindowRect($h,[ref]$originalRect)
foreach($ghost in [SutramIde]::SetupGhosts()){
    $ghostRect=[SutramIde+RECT]::new();[void][SutramIde]::GetWindowRect($ghost,[ref]$ghostRect)
    if($ghostRect.Left -eq $originalRect.Left -and $ghostRect.Top -eq $originalRect.Top -and $ghostRect.Right -eq $originalRect.Right -and $ghostRect.Bottom -eq $originalRect.Bottom){$h=$ghost;break}
}
[void][SutramIde]::SetForegroundWindow($h)
Start-Sleep -Milliseconds 500
$isForeground=[SutramIde]::GetForegroundWindow() -eq $h
$rect=[SutramIde+RECT]::new()
if(-not [SutramIde]::GetWindowRect($h,[ref]$rect)){throw 'No wizard rectangle'}
Add-Type -AssemblyName System.Drawing
$w=$rect.Right-$rect.Left;$height=$rect.Bottom-$rect.Top
if($w -le 0 -or $height -le 0 -or $w -gt 8000 -or $height -gt 8000){throw 'Invalid wizard rectangle'}
$bitmap=[Drawing.Bitmap]::new($w,$height)
$graphics=[Drawing.Graphics]::FromImage($bitmap)
try{$graphics.CopyFromScreen($rect.Left,$rect.Top,0,0,[Drawing.Size]::new($w,$height));$bitmap.Save((Join-Path $OutDir 'upgrade-stalled-screen.png'),[Drawing.Imaging.ImageFormat]::Png)}finally{$graphics.Dispose();$bitmap.Dispose()}
@{observed=[DateTime]::Now.ToString('o');target_process=$TargetProcess;window=$h.ToInt64();foreground=$isForeground;rectangle=$rect;method='screen rectangle; requires visual inspection for occlusion'}|ConvertTo-Json -Depth 4|Set-Content (Join-Path $OutDir 'screenshot.json') -Encoding UTF8
Write-Output 'upgrade-stalled-screen.png'
