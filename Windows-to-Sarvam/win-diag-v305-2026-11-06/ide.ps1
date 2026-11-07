$ErrorActionPreference='Stop'
$OutDir=$PSScriptRoot
$Root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
. (Join-Path $PSScriptRoot 'ui-helper.ps1')
$ide=Join-Path $Root 'sutram-ide-gui.exe'
$compiler=Join-Path $Root 'win\sutram.exe'
if ((Get-FileHash $ide).Hash -ne '829F8658DE55BE045C6273339244D099022B373725EAD3681228C00BA3D5C051') { throw 'Original IDE required' }
if ((Get-FileHash $compiler).Hash -ne 'DB5EDA53871AAFA4749D593DDEF2D29E2841E3EB4D3CB7CDF680223FB45A073C') { throw 'Original v305 compiler required' }
$records=[Collections.Generic.List[object]]::new()
$r=[ordered]@{ide=$ide; ide_sha256=(Get-FileHash $ide).Hash;compiler=$compiler;compiler_sha256=(Get-FileHash $compiler).Hash;started=[DateTime]::Now.ToString('o');scenarios=$records}
$protected=@('examples\01_hello.sm','examples\02_arith.sm','examples\105_block_nesting_capacity.sm')
$r.before=@($protected | ForEach-Object { Get-FileHash -LiteralPath (Join-Path $Root $_) | Select-Object Path,Hash })
$ip=$null
function Open-Example([string]$Name) {
    $idx=[SutramIde]::ListFind($list,$Name)
    if ($idx -lt 0) { throw "Missing example: $Name" }
    [void][SutramIde]::Send($list,0x186,$idx,0,3000)
    [void][SutramIde]::Send($main,0x111,((2 -shl 16) -bor 205),$list.ToInt64(),30000)
    Start-Sleep -Milliseconds 250
}
function Run-Editor {
    [void][SutramIde]::Send($main,0x111,2010,0,30000)
    Start-Sleep -Milliseconds 250
}
function Snapshot([string]$Name,[bool]$Screenshot=$false) {
    $row=[ordered]@{name=$Name;title=[SutramIde]::Text($main);editor=[SutramIde]::Text($editor);output=[SutramIde]::Text($output);status=[SutramIde]::Text($status)}
    if ($Screenshot) { $row.screenshot=Shot $main $Name }
    $records.Add($row)
}
function Open-Probe([string]$Name) {
    [void][SutramIde]::PostMessageW($main,0x111,[IntPtr]2001,[IntPtr]::Zero)
    $dialog=Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id,'#32770') | Where-Object { [SutramIde]::IsWindowVisible($_) } | Select-Object -First 1 } 5000
    if (-not $dialog) { throw 'Open dialog did not appear' }
    # Explorer-style OPENFILENAME filename combo (cmb13), with edt1 fallback.
    $filename=[SutramIde]::GetDlgItem($dialog,1148)
    if ($filename -eq [IntPtr]::Zero) { $filename=[SutramIde]::GetDlgItem($dialog,1152) }
    if ($filename -eq [IntPtr]::Zero) { throw 'Filename field not found' }
    [SutramIde]::SetText($filename,(Join-Path $OutDir $Name))
    [void][SutramIde]::PostMessageW($dialog,0x111,[IntPtr]1,[IntPtr]::Zero)
    $closed=Wait-Until { -not [SutramIde]::IsWindowVisible($dialog) } 5000
    if (-not $closed) { throw 'Open dialog did not finish' }
    Start-Sleep -Milliseconds 250
    if (-not [SutramIde]::Text($main).Contains($Name)) { throw "Probe was not loaded: $Name" }
}
try {
    # A visible window is required for this explicitly requested GUI/screenshot round.
    $ip=Start-Process -FilePath $ide -WorkingDirectory $Root -WindowStyle Normal -PassThru
    $main=Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id,'SutramNativeGUIWindow') | Select-Object -First 1 } 10000
    if (-not $main) { throw 'IDE did not open' }
    Start-Sleep -Milliseconds 600
    $editor=[SutramIde]::GetDlgItem($main,201)
    $output=[SutramIde]::GetDlgItem($main,203)
    $status=[SutramIde]::GetDlgItem($main,206)
    $list=[SutramIde]::GetDlgItem($main,205)
    Open-Example '01_hello.sm'; Run-Editor; Snapshot 'B1-before-compile-error'
    Open-Probe 'B1-syntax-error.sm'; Snapshot 'B1-loaded-before-run'
    Run-Editor; Snapshot 'B1-compile-error' $true
    Open-Example '01_hello.sm'; Run-Editor; Snapshot 'B2-before-runtime-error'
    Open-Probe 'B2-runtime-error.sm'; Snapshot 'B2-loaded-before-run'
    Run-Editor; Snapshot 'B2-runtime-error' $true
    Open-Example '01_hello.sm'; Run-Editor; Snapshot 'B3-before-refusal'
    Open-Example '105_block_nesting_capacity.sm'; Snapshot 'B3-large-file-refusal' $true
    Open-Example '02_arith.sm'; Snapshot 'B3-recovered-before-run'
    Run-Editor; Snapshot 'B3-recovered-after-run' $true
    $r.status='OBSERVED'
} catch { $r.status='ERROR'; $r.error=$_.Exception.Message; throw }
finally {
    if ($ip -and -not $ip.HasExited) {
        if ($main) { [void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero) }
        if (-not $ip.WaitForExit(3000)) { $ip.Kill(); [void]$ip.WaitForExit(3000); $r.forced_close=$true }
    }
    $r.after=@($protected | ForEach-Object { Get-FileHash -LiteralPath (Join-Path $Root $_) | Select-Object Path,Hash })
    [IO.File]::WriteAllText((Join-Path $OutDir 'ide.json'),($r | ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
}
$r | ConvertTo-Json -Depth 8
