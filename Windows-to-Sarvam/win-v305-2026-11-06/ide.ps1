$ErrorActionPreference='Stop'
$OutDir=$PSScriptRoot
$Root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
. (Join-Path $PSScriptRoot 'ui-helper.ps1')
$ide=Join-Path $Root 'sutram-ide-gui.exe'
$compiler=Join-Path $Root 'win\sutram.exe'
$big=Join-Path $Root 'examples\105_block_nesting_capacity.sm'
$r=[ordered]@{ide=$ide;ide_sha256=(Get-FileHash $ide).Hash;compiler=$compiler;compiler_sha256=(Get-FileHash $compiler).Hash;big_file=$big;big_bytes=(Get-Item $big).Length;big_sha256_before=(Get-FileHash $big).Hash;started=[DateTime]::Now.ToString('o')}
$ip=$null
function Open-Example([string]$Name) {
    $idx=[SutramIde]::ListFind($list,$Name)
    if ($idx -lt 0) { throw "Missing example: $Name" }
    [void][SutramIde]::Send($list,0x186,$idx,0,3000)
    [void][SutramIde]::Send($main,0x111,((2 -shl 16) -bor 205),$list.ToInt64(),30000)
    Start-Sleep -Milliseconds 400
}
try {
    # The requested visible IDE run and screenshot require a normal window.
    $ip=Start-Process -FilePath $ide -WorkingDirectory $Root -WindowStyle Normal -PassThru
    $main=Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id,'SutramNativeGUIWindow') | Select-Object -First 1 } 10000
    if (-not $main) { throw 'IDE did not open within ten seconds' }
    Start-Sleep -Milliseconds 800
    $editor=[SutramIde]::GetDlgItem($main,201)
    $output=[SutramIde]::GetDlgItem($main,203)
    $status=[SutramIde]::GetDlgItem($main,206)
    $list=[SutramIde]::GetDlgItem($main,205)
    Open-Example '01_hello.sm'
    $r.hello_title=[SutramIde]::Text($main)
    [void][SutramIde]::Send($main,0x111,2010,0,30000)
    Start-Sleep -Milliseconds 400
    $r.hello_output=[SutramIde]::Text($output)
    $r.hello_status=[SutramIde]::Text($status)
    $r.hello_screenshot=Shot $main 'ide-hello'
    $r.hello_pass=$r.hello_output.Contains('Namaste, Sutram!')
    $r.editor_before=[SutramIde]::Text($editor)
    Open-Example '105_block_nesting_capacity.sm'
    $r.after_title=[SutramIde]::Text($main)
    $r.after_output=[SutramIde]::Text($output)
    $r.after_status=[SutramIde]::Text($status)
    $r.editor_after=[SutramIde]::Text($editor)
    $r.big_screenshot=Shot $main 'ide-large-refusal'
    $r.previous_editor_retained=$r.editor_before -eq $r.editor_after
    $r.entire_output_unchanged=$r.hello_output -eq $r.after_output
    $r.previous_output_retained=$r.after_output.Contains($r.hello_output)
    $r.output_cleared=[string]::IsNullOrWhiteSpace($r.after_output)
    $r.big_sha256_after=(Get-FileHash $big).Hash
    $r.status='OBSERVED'
} catch { $r.status='ERROR'; $r.error=$_.Exception.Message; throw }
finally {
    if ($ip -and -not $ip.HasExited) {
        if ($main) { [void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero) }
        if (-not $ip.WaitForExit(3000)) { $ip.Kill(); [void]$ip.WaitForExit(3000); $r.forced_close=$true }
    }
    [IO.File]::WriteAllText((Join-Path $OutDir 'ide.json'),($r | ConvertTo-Json -Depth 6),[Text.UTF8Encoding]::new($false))
}
$r | ConvertTo-Json -Depth 6
