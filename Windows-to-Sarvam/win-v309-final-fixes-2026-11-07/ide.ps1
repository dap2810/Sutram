$ErrorActionPreference='Stop'
$OutDir=$PSScriptRoot
$Root=Split-Path -Parent (Split-Path -Parent $OutDir)
. (Join-Path $OutDir 'ui-helper.ps1')
$identity=Get-Content -LiteralPath (Join-Path $OutDir 'initial-identity.json') -Raw|ConvertFrom-Json
if(-not $identity.pass) { throw 'Stop unless the new shell reports v309-final' }
$installed=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
$work=Join-Path $Root 'build\native-v309-final-fix\ide-save-guard'
if(Test-Path -LiteralPath $work) { throw 'Use a fresh isolated IDE test directory' }
# Save is tested only on copies. The original installed and repository examples are protected.
Copy-Item -LiteralPath $installed -Destination $work -Recurse
$ide=Join-Path $work 'sutram-ide-gui.exe'
$candidate=Get-Content -LiteralPath (Join-Path $OutDir 'candidate.json') -Raw|ConvertFrom-Json
$ideHash=($candidate.checks|Where-Object {$_.file -eq 'sutram-ide-gui.exe'}).actual
if((Get-FileHash -LiteralPath $ide).Hash -ne $ideHash) { throw 'IDE copy differs' }
$protected=@()
foreach($base in @($Root,$installed)) { foreach($name in @('01_hello.sm','105_block_nesting_capacity.sm')) { $protected+=Join-Path $base ('examples\'+$name) } }
$hello=Join-Path $work 'examples\01_hello.sm'; $big=Join-Path $work 'examples\105_block_nesting_capacity.sm'
$r=[ordered]@{started=[DateTime]::Now.ToString('o');ide=$ide;ide_sha256=(Get-FileHash $ide).Hash;scenarios=@();protected_before=@($protected|ForEach-Object {Get-FileHash -LiteralPath $_|Select-Object Path,Hash});held_file=$hello;refused_file=$big;held_before=(Get-FileHash $hello).Hash;refused_before=(Get-FileHash $big).Hash;refused_bytes=(Get-Item $big).Length}
function Open-Example([string]$Name) {
    $idx=[SutramIde]::ListFind($list,$Name)
    if($idx -lt 0) { throw "Missing example: $Name" }
    [void][SutramIde]::Send($list,0x186,$idx,0,3000)
    [void][SutramIde]::Send($main,0x111,((2 -shl 16) -bor 205),$list.ToInt64(),30000)
    Start-Sleep -Milliseconds 250
}
function Snapshot([string]$Name,[bool]$Screenshot=$false) {
    $row=[ordered]@{name=$Name;title=[SutramIde]::Text($main);editor=[SutramIde]::Text($editor);output=[SutramIde]::Text($output);status=[SutramIde]::Text($status)}
    if($Screenshot) { $row.screenshot=Shot $main $Name }
    $r.scenarios+=,$row
    return $row
}
$ip=$null
try {
    $ip=Start-Process -FilePath $ide -WorkingDirectory $work -WindowStyle Normal -PassThru
    $r.pid=$ip.Id;$r.process_started=$ip.StartTime.ToString('o')
    $main=Wait-Until { [SutramIde]::WindowsOf([uint32]$ip.Id,'SutramNativeGUIWindow')|Select-Object -First 1 } 10000
    if(-not $main) { throw 'IDE did not open' }
    Start-Sleep -Milliseconds 600
    $editor=[SutramIde]::GetDlgItem($main,201);$output=[SutramIde]::GetDlgItem($main,203)
    $status=[SutramIde]::GetDlgItem($main,206);$list=[SutramIde]::GetDlgItem($main,205)
    Open-Example '01_hello.sm'
    [void][SutramIde]::Send($main,0x111,2010,0,30000)
    $before=Snapshot 'C1-hello-run'
    if(-not $before.output.Contains('Namaste')) { throw 'Hello run did not produce expected output' }
    Open-Example '105_block_nesting_capacity.sm'
    $after=Snapshot 'C1-refused-load' $true
    $r.c1_pass=$after.editor -eq $before.editor -and $after.title.Contains('01_hello.sm') -and -not $after.output.Contains('Namaste') -and $after.output.Contains('[patram na udghatitam - sampadake purvam patram eva asti]')
    $edited=$after.editor+"`r`n# v309-final isolated Save safeguard verification`r`n"
    [SutramIde]::SetText($editor,$edited)
    $null=Snapshot 'C2-edited-before-save'
    [void][SutramIde]::Send($main,0x111,2002,0,30000)
    $null=Snapshot 'C2-after-save' $true
    $r.held_after=(Get-FileHash $hello).Hash;$r.refused_after=(Get-FileHash $big).Hash
    $saved=[IO.File]::ReadAllText($hello)
    $r.saved_text=$saved
    $r.c2_pass=$r.held_after -ne $r.held_before -and $r.refused_after -eq $r.refused_before -and $saved.Replace("`r`n","`n") -eq $edited.Replace("`r`n","`n")

    $program="vitti zero = 0`nvitti leaked = make_kosh() + zero`nprakriya make_kosh() { kosh k[1] kosh_kship(k, 7) nivartanam k }`nmukhya() { likha(leaked) }`n"
    [SutramIde]::SetText($editor,$program)
    [void][SutramIde]::Send($main,0x111,2002,0,30000)
    [void][SutramIde]::Send($main,0x111,2010,0,30000)
    $negative=Snapshot 'C3-global-refusal' $true
    $r.c3_pass=$negative.output.Contains('E_KOSH_GANIT') -and -not $negative.output.Contains('Namaste')
} catch { $r.error=$_.Exception.Message; throw }
finally {
    if($ip -and -not $ip.HasExited) {
        if($main) { [void][SutramIde]::PostMessageW($main,0x10,[IntPtr]::Zero,[IntPtr]::Zero) }
        if(-not $ip.WaitForExit(3000)) { $ip.Kill();[void]$ip.WaitForExit(3000);$r.forced_close=$true }
    }
    $r.protected_after=@($protected|ForEach-Object {Get-FileHash -LiteralPath $_|Select-Object Path,Hash})
    $r.originals_unchanged=-not [bool](Compare-Object ($r.protected_before|ConvertTo-Json) ($r.protected_after|ConvertTo-Json))
    $r.process_exited=($ip -and $ip.HasExited)
    $r.capture_warnings=@($script:captureWarnings)
    [IO.File]::WriteAllText((Join-Path $OutDir 'ide.json'),($r|ConvertTo-Json -Depth 8),[Text.UTF8Encoding]::new($false))
}
Write-Host "C1: $($r.c1_pass); C2: $($r.c2_pass); protected originals unchanged: $($r.originals_unchanged)"
if(-not($r.c1_pass -and $r.c2_pass -and $r.c3_pass -and $r.originals_unchanged)) { throw 'IDE verification failed; inspect ide.json' }
