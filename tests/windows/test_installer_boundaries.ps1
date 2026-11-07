# R142 (Sarvam R142 WS3, ChatGPT R209): the installer's own staging and publishing code, taken from
# windows\native-installer\install-core.ps1 by its syntax tree (as PR #68's fixtures do) and run against files at
# each boundary ChatGPT named. No registry, PATH, shortcut or installation is touched; everything is under build\.
#
#   superseded equality   a target is deleted only when the copy already kept under its _superseded name has its
#                         full SHA-256; a different copy under that name stops the run and nothing is deleted
#   interruption          a stop before every journal record and every rename of a small upgrade (and, again, with
#                         the last journal record torn in half), each followed by a rerun: the rerun finishes, every
#                         file has the payload's bytes, and the replaced file's old bytes are in the backup
#   suffix preservation   a '*.sutram-partial' file is left in place by the installer's recovery and the uninstaller
#   edit during publish   an edit to a file not yet reached stops the run with the edit kept; an edit landing between
#                         the hash and the rename is moved into the backup, not lost
#
# Written in the Linux container, where PowerShell could not be run: NOT RUN by its author. For the native run of
# v311:  powershell -NoProfile -ExecutionPolicy Bypass -File tests\windows\test_installer_boundaries.ps1
# Prints PASS/FAIL per check; exit 1 on any FAIL. The fixture folder is kept and named at the end.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$engine=Join-Path $root 'windows\native-installer\install-core.ps1'
$uninstaller=Join-Path $root 'windows\native-installer\uninstall-core.ps1'
function Parse-Engine([string]$Path){
    $t=$null;$e=$null
    $a=[Management.Automation.Language.Parser]::ParseFile($Path,[ref]$t,[ref]$e)
    if($e.Count){throw ($e|Out-String)}
    return $a
}
$ast=Parse-Engine $engine
$uast=Parse-Engine $uninstaller
foreach($name in @('Log','Write-Durable','Journal','Get-Sha','Assert-NoReparsePath','Stage-Payload','Move-Into','Read-Journal')){
    $f=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name},$true)
    if(-not $f){throw ('Missing function '+$name)}
    . ([ScriptBlock]::Create($f.Extent.Text))
}
$loops=@($ast.FindAll({param($n) $n -is [Management.Automation.Language.ForEachStatementAst] -and $n.Extent.Text.Contains('Move-Into $staged $target')},$true))
if($loops.Count -ne 1){throw 'Could not identify the publication loop'}
$publish=[ScriptBlock]::Create($loops[0].Extent.Text)
$recover=@($ast.FindAll({param($n) $n -is [Management.Automation.Language.IfStatementAst] -and $n.Extent.Text.StartsWith('if ($pending)') -and $n.Extent.Text.Contains("'*.sutram-partial'")},$true))
if($recover.Count -ne 1){throw 'Could not identify the recovery statement that names *.sutram-partial files'}
$recover=[ScriptBlock]::Create($recover[0].Extent.Text)
$uparts=@($uast.FindAll({param($n) $n -is [Management.Automation.Language.ForEachStatementAst] -and $n.Extent.Text.Contains("'*.sutram-partial'")},$true))
if($uparts.Count -ne 1){throw 'Could not identify the uninstaller loop that names *.sutram-partial files'}
$uparts=[ScriptBlock]::Create($uparts[0].Extent.Text)

# Every journal record and every rename goes through these two; a stop is injected before the chosen one.
$realJournal=${function:Journal}
$realMove=${function:Move-Into}
$script:ops=0;$script:stopAt=0;$script:onMove=$null
function Journal([string]$Line){
    $script:ops++
    if($script:ops -eq $script:stopAt){throw 'FIXTURE-STOP'}
    & $realJournal $Line
}
function Move-Into([string]$From,[string]$To){
    $script:ops++
    if($script:ops -eq $script:stopAt){throw 'FIXTURE-STOP'}
    if($script:onMove){& $script:onMove $From $To}
    & $realMove $From $To
}

$work=Join-Path $root ('build\boundary-fixture-'+[guid]::NewGuid().ToString('N'))
[void][IO.Directory]::CreateDirectory($work)
$LogPath=Join-Path $work 'run.log'
$utf8=[Text.UTF8Encoding]::new($false)
$checks=[ordered]@{}
function Write-Fixture([string]$Path,[string]$Text){
    $d=[IO.Path]::GetDirectoryName($Path)
    if(-not [IO.Directory]::Exists($d)){[void][IO.Directory]::CreateDirectory($d)}
    [IO.File]::WriteAllText($Path,$Text,$utf8)
}
function Read-Fixture([string]$Path){
    if([IO.File]::Exists($Path)){return [IO.File]::ReadAllText($Path)}
    return $null
}
function New-Case([string]$Name,[hashtable]$Payload,[hashtable]$Installed){
    $c=@{Dir=(Join-Path $work $Name)}
    $c.Stage=Join-Path $c.Dir 'payload'
    $c.Install=Join-Path $c.Dir 'installed'
    $c.Txn=Join-Path $c.Dir 'installed.sutram-transaction'
    $c.TxnStage=Join-Path $c.Txn 'stage'
    $c.TxnBackup=Join-Path $c.Txn 'backup'
    $c.Journal=Join-Path $c.Txn 'journal.txt'
    foreach($d in @($c.Stage,$c.Install,$c.TxnStage)){[void][IO.Directory]::CreateDirectory($d)}
    $c.New=@{}
    foreach($rel in $Payload.Keys){Write-Fixture (Join-Path $c.Stage $rel) $Payload[$rel];$c.New[$rel]=Get-Sha (Join-Path $c.Stage $rel)}
    $c.Previous=@{}
    foreach($rel in $Installed.Keys){Write-Fixture (Join-Path $c.Install $rel) $Installed[$rel];$c.Previous[$rel]=Get-Sha (Join-Path $c.Install $rel)}
    return $c
}
# One run of the engine's middle: what an earlier run journaled, BEGIN, staging, publishing - as install-core.ps1
# does them, with the variables it gives them. (The checks before BEGIN - lock, ownership, conflicts - are not run
# here; test_installer_lock.ps1 and the R134 gate cover them.)
function Invoke-Run($c,[hashtable]$Previous,[hashtable]$Pending){
    $script:journalPath=$c.Journal
    $stage=$c.Stage;$txnStage=$c.TxnStage;$txnBackup=$c.TxnBackup;$InstallDir=$c.Install
    $newFiles=$c.New;$previousFiles=$Previous;$pendingFiles=$Pending
    $earlier=Read-Journal $c.Journal
    Journal ("BEGIN`tfixture")
    $files=Stage-Payload $stage $txnStage $newFiles $InstallDir
    . $publish
}

# --- superseded equality ------------------------------------------------------------------------------------
$copy="a stopped run's own copy`n"
foreach($kind in @('identical','differs','absent')){
    $c=New-Case ('superseded-'+$kind) @{'a.txt'="the payload`n"} @{'a.txt'=$copy}
    $have=$c.Previous['a.txt']
    Write-Fixture (Join-Path $c.TxnBackup 'a.txt') "the original installation`n"
    $sup=Join-Path (Join-Path $c.TxnBackup '_superseded') ('a.txt.'+$have.Substring(0,12))
    if($kind -eq 'identical'){Write-Fixture $sup $copy}
    if($kind -eq 'differs'){Write-Fixture $sup "other bytes under the same name`n"}
    Write-Fixture $c.Journal ("PUBLISHED`ta.txt`t"+$have+"`r`n")       # the earlier run's own file
    $err=$null
    try{Invoke-Run $c @{} @{}}catch{$err=$_.Exception.Message}
    $target=Join-Path $c.Install 'a.txt'
    $original=((Read-Fixture (Join-Path $c.TxnBackup 'a.txt')) -eq "the original installation`n")
    if($kind -eq 'differs'){
        $checks.superseded_differs_refused=($null -ne $err -and $err.Contains('Nothing was deleted'))
        $checks.superseded_differs_target_kept=((Read-Fixture $target) -eq $copy)
        $checks.superseded_differs_other_copy_kept=((Read-Fixture $sup) -eq "other bytes under the same name`n")
        $checks.superseded_differs_original_kept=$original
        $checks.superseded_differs_not_journaled=(-not (Read-Fixture $c.Journal).Contains("SUPERSEDED`t"))
    } else {
        $checks['superseded_'+$kind+'_completes']=($null -eq $err -and (Get-Sha $target) -eq $c.New['a.txt'])
        $checks['superseded_'+$kind+'_copy_kept']=((Read-Fixture $sup) -eq $copy)
        $checks['superseded_'+$kind+'_original_kept']=$original
    }
}

# --- interruption at every boundary, then a rerun -----------------------------------------------------------
$payload=@{'a.txt'="added`n";'b.txt'="b, new`n";'c.txt'="c, unchanged`n";'sub\d.txt'="d, new`n"}
$installed=@{'b.txt'="b, old`n";'c.txt'="c, unchanged`n";'sub\d.txt'="d, old`n"}
$c=New-Case 'count' $payload $installed
$script:ops=0;$script:stopAt=0
Invoke-Run $c $c.Previous @{}
$total=$script:ops
$checks.interruption_reference_run=(@($payload.Keys|Where-Object {(Get-Sha (Join-Path $c.Install $_)) -ne $c.New[$_]}).Count -eq 0)
$failures=New-Object Collections.Generic.List[string]
$runs=0
foreach($torn in @($false,$true)){
    for($k=1;$k -le $total;$k++){
        $c=New-Case ('stop-'+$k+'-torn-'+[int]$torn) $payload $installed
        $script:ops=0;$script:stopAt=$k
        $first=$null
        try{Invoke-Run $c $c.Previous @{}}catch{$first=$_.Exception.Message}
        $script:stopAt=0
        if($first -ne 'FIXTURE-STOP'){$failures.Add(('stop '+$k+': the first run did not stop there ('+$first+')'));continue}
        if($torn -and [IO.File]::Exists($c.Journal)){
            $t=[IO.File]::ReadAllText($c.Journal).TrimEnd("`r","`n")
            $start=$t.LastIndexOf("`n")+1
            [IO.File]::WriteAllText($c.Journal,$t.Substring(0,$start+[int][Math]::Floor(($t.Length-$start)/2)),$utf8)
        }
        $second=$null
        try{Invoke-Run $c $c.Previous $c.New}catch{$second=$_.Exception.Message}   # BEGIN wrote the pending record
        $runs++
        $wrong=@($payload.Keys|Where-Object {-not [IO.File]::Exists((Join-Path $c.Install $_)) -or (Get-Sha (Join-Path $c.Install $_)) -ne $c.New[$_]})
        $lost=@(@('b.txt','sub\d.txt')|Where-Object {(Read-Fixture (Join-Path $c.TxnBackup $_)) -ne $installed[$_]})
        if($second -or $wrong.Count -or $lost.Count){
            $failures.Add(('stop '+$k+' torn='+$torn+': rerun error='+$second+' wrong='+($wrong -join ',')+' old bytes missing='+($lost -join ',')))
        }
    }
}
$checks.interruption_every_boundary_recovers=($failures.Count -eq 0 -and $runs -eq 2*$total)
foreach($f in $failures){Write-Output ('  '+$f)}
Write-Output ('  '+$total+' boundaries, '+$runs+' stopped-and-rerun installations')

# --- suffix preservation -----------------------------------------------------------------------------------
$c=New-Case 'suffix' @{'lib\x.txt'="x, new`n"} @{'lib\x.txt'="x, old`n"}
$part=Join-Path $c.Install 'lib\x.txt.sutram-partial'
Write-Fixture $part "a file with the old suffix`n"
$InstallDir=$c.Install;$pending=$true;$pendingPath=Join-Path $c.Install 'payload.pending.sha256'
$before=[IO.File]::ReadAllText($LogPath).Length
. $recover
Invoke-Run $c $c.Previous @{}
. $uparts
$said=[IO.File]::ReadAllText($LogPath).Substring($before)
$checks.suffix_file_left_by_installer_and_uninstaller=((Read-Fixture $part) -eq "a file with the old suffix`n")
$checks.suffix_file_named_in_the_log=([regex]::Matches($said,[regex]::Escape('Left in place')).Count -ge 2)

# --- an edit during publication ----------------------------------------------------------------------------
$payload=@{'b.txt'="b, new`n";'c.txt'="c, new`n"}
$installed=@{'b.txt'="b, old`n";'c.txt'="c, old`n"}
$c=New-Case 'edit-ahead' $payload $installed
$cTarget=Join-Path $c.Install 'c.txt'
$script:onMove={param($From,$To) if($From.EndsWith('installed\b.txt') -and $To.Contains('\backup\')){[IO.File]::WriteAllText($cTarget,"c, edited by its owner`n",$utf8)}}
$err=$null
try{Invoke-Run $c $c.Previous @{}}catch{$err=$_.Exception.Message}
$script:onMove=$null
$checks.edit_ahead_stops_the_run=($null -ne $err -and $err.Contains('not replaced'))
$checks.edit_ahead_kept=((Read-Fixture $cTarget) -eq "c, edited by its owner`n")
$checks.edit_ahead_earlier_file_published=((Get-Sha (Join-Path $c.Install 'b.txt')) -eq $c.New['b.txt'])
$c=New-Case 'edit-in-window' $payload $installed
$cTarget=Join-Path $c.Install 'c.txt'
$script:onMove={param($From,$To) if($From.EndsWith('installed\c.txt') -and $To.Contains('\backup\')){[IO.File]::WriteAllText($From,"c, edited between the hash and the rename`n",$utf8)}}
$err=$null
try{Invoke-Run $c $c.Previous @{}}catch{$err=$_.Exception.Message}
$script:onMove=$null
$checks.edit_in_window_not_lost=((Read-Fixture (Join-Path $c.TxnBackup 'c.txt')) -eq "c, edited between the hash and the rename`n")

foreach($key in $checks.Keys){Write-Output ((@('FAIL','PASS')[[int][bool]$checks[$key]])+' '+$key)}
[IO.File]::WriteAllText((Join-Path $work 'results.json'),(@{checks=$checks;failures=@($failures)}|ConvertTo-Json -Depth 5),$utf8)
Write-Output ('Evidence: '+$work)
if($checks.Values -contains $false){exit 1}
