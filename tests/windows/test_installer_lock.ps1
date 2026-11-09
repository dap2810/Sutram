# From PR #68 (Windows, 664ff188/7ab8c439), taken into main in R142. R162: the lock statement is Open-SutramLock now. One change: main's preflight begins with
# '$lockParent =' (the lock's folder), so that is accepted as its first statement too.
# Run the actual ownership/lock preflight in child PowerShell processes.
# Registry/discovery reads are stubs: only isolated workspace files are changed.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$engine=Join-Path $root 'windows\native-installer\install-core.ps1'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($engine,[ref]$tokens,[ref]$errors)
if($errors.Count){throw ($errors|Out-String)}
$main=@($ast.EndBlock.Statements|Where-Object {$_ -is [Management.Automation.Language.TryStatementAst]})[-1]
$items=@($main.Body.Statements)
$start=0;$finish=0
for($i=0;$i -lt $items.Count;$i++){
    $s=$items[$i].Extent.Text
    if($s.StartsWith('$lockParent =') -or $s.StartsWith('$unKey =') -or $s.StartsWith('$txnDir =')){if(-not $start){$start=$i}}
    if($s.StartsWith('$earlier = Read-Journal')){$finish=$i;break}
}
if(-not $start -or $finish -le $start){throw 'Ownership preflight was not located'}
$preflight=($items[$start..$finish]|ForEach-Object {$_.Extent.Text}) -join "`n"
$work=Join-Path $root ('build\lock-fixture-'+[guid]::NewGuid().ToString('N'))
$install=Join-Path $work 'installed'
[void][IO.Directory]::CreateDirectory($install)
$utf8=[Text.UTF8Encoding]::new($false)
$definitions=foreach($name in @('Assert-NoReparsePath','Read-State','Read-Journal','Open-SutramLock')){
    $f=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name},$true)
    if(-not $f){throw ('Missing '+$name)}
    $f.Extent.Text.Replace('function Read-State','function Read-StateImpl')
}
$child=Join-Path $work 'child.ps1'
$harness=@'
param([string]$Work,[string]$Name,[switch]$Barrier)
$ErrorActionPreference='Stop'
$InstallDir=Join-Path $Work 'installed'
$reads=Join-Path $Work ($Name+'-reads.txt')
function Record([string]$Name){[IO.File]::AppendAllText($reads,$Name+"`n")}
function Read-State([string]$Path){Record 'state';Read-StateImpl $Path}
function Get-ItemProperty {param($LiteralPath,$ErrorAction) Record 'registry';return $null}
function Find-OtherSutram {param($Path) Record 'discovery';return ,@()}
function Log {param($Message)}
'@
$barrier=@'
if($Barrier){
    [IO.File]::WriteAllText((Join-Path $Work ($Name+'-ready')),'ready')
    $timer=[Diagnostics.Stopwatch]::StartNew()
    while(-not [IO.File]::Exists((Join-Path $Work ($Name+'-go')))){
        if($timer.Elapsed.TotalSeconds -gt 20){throw 'Fixture barrier timeout'}
        Start-Sleep -Milliseconds 25
    }
}
'@
# Pause immediately before the real lock-acquisition statement to reproduce the reviewed interleaving.
$lockTry=@($items|Where-Object {$_ -is [Management.Automation.Language.TryStatementAst] -and $_.Extent.Text.Contains('$script:txnLock = Open-SutramLock')})
if($lockTry.Count -ne 1){throw 'Lock acquisition was not located'}
$preflight=$preflight.Replace($lockTry[0].Extent.Text,($barrier+"`n"+$lockTry[0].Extent.Text))
$tail=@'
$result=[ordered]@{error=$null;state=$null;pending=$null;reads=@()}
try {
__PREFLIGHT__
    $result.state=$oldState;$result.pending=$pending
} catch {$result.error=$_.Exception.Message}
finally {if($script:txnLock){$script:txnLock.Dispose()}}
if([IO.File]::Exists($reads)){$result.reads=@([IO.File]::ReadAllLines($reads))}
[IO.File]::WriteAllText((Join-Path $Work ($Name+'.json')),($result|ConvertTo-Json -Depth 5))
'@
[IO.File]::WriteAllText($child,($harness+"`n"+($definitions -join "`n")+"`n"+$tail.Replace('__PREFLIGHT__',$preflight)),$utf8)
function Launch([string]$Name,[bool]$Barrier=$false){
    $args=@('-NoProfile','-ExecutionPolicy','Bypass','-File',('"'+$child+'"'),'-Work',('"'+$work+'"'),'-Name',$Name)
    if($Barrier){$args+='-Barrier'}
    Start-Process -FilePath (Join-Path $PSHOME 'powershell.exe') -ArgumentList $args -WindowStyle Hidden -PassThru
}
function Finish($Process,[string]$Name){
    if(-not $Process.WaitForExit(25000)){$Process.Kill();throw 'Fixture child timeout'}
    Get-Content -LiteralPath (Join-Path $work ($Name+'.json')) -Raw|ConvertFrom-Json
}
$state=Join-Path $install 'install-state.ini';$pendingPath=Join-Path $install 'payload.pending.sha256'
[IO.File]::WriteAllText($state,"PathAdded=0`n",$utf8)
$lockPath=$install+'.sutram-lock'
$holder=[IO.FileStream]::new($lockPath,[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None,1,[IO.FileOptions]::DeleteOnClose)
try {
    $blocked=Finish (Launch 'blocked') 'blocked'
    $waiting=Launch 'after-owner' $true
    $timer=[Diagnostics.Stopwatch]::StartNew()
    while(-not [IO.File]::Exists((Join-Path $work 'after-owner-ready'))){if($timer.Elapsed.TotalSeconds -gt 20){throw 'No barrier'};Start-Sleep -Milliseconds 25}
    [IO.File]::WriteAllText($state,"PathAdded=1`nShortcutOwned=1`n",$utf8)
    [IO.File]::WriteAllText($pendingPath,'fixture pending',$utf8)
} finally {$holder.Dispose()}
[IO.File]::WriteAllText((Join-Path $work 'after-owner-go'),'go',$utf8)
$fresh=Finish $waiting 'after-owner'
$checks=[ordered]@{
    concurrent_owner_refused=($blocked.error -like 'Another Sutram installer*')
    no_ownership_reads_while_locked=($blocked.reads.Count -eq 0)
    next_owner_succeeds=(-not $fresh.error)
    refreshed_state=($fresh.state.PathAdded -eq '1' -and $fresh.state.ShortcutOwned -eq '1')
    refreshed_pending=($fresh.pending -eq $true)
    all_reads_under_lock=($fresh.reads.Count -eq 3)
    lock_removed_after_exit=(-not [IO.File]::Exists($lockPath))
}
foreach($key in $checks.Keys){Write-Output ((@('FAIL','PASS')[[int][bool]$checks[$key]])+' '+$key)}
[IO.File]::WriteAllText((Join-Path $work 'results.json'),(@{checks=$checks;blocked=$blocked;fresh=$fresh}|ConvertTo-Json -Depth 6),$utf8)
Write-Output ('Evidence: '+$work)
if($checks.Values -contains $false){exit 1}
