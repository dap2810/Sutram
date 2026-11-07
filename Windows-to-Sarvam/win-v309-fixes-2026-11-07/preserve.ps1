param([ValidateSet('backup','vacate','restore')][string]$Action,[ValidatePattern('^[a-z0-9-]+$')][string]$Name='before-v309',[string]$BackupName='working-v309')
$ErrorActionPreference='Stop';$OutDir=$PSScriptRoot
$parent=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
$install=Join-Path $parent 'Sutram';$txn=Join-Path $parent 'Sutram.sutram-transaction'
function Guard([string]$Path){
    if([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($Path)) -ne $parent){throw 'Target outside Programs'}
    $walk=$Path
    while($walk){if((Test-Path -LiteralPath $walk) -and ((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint)){throw 'Reparse ancestor'};$walk=[IO.Path]::GetDirectoryName($walk)}
    if((Test-Path -LiteralPath $Path) -and (Get-ChildItem -LiteralPath $Path -Recurse -Force|Where-Object {$_.Attributes -band [IO.FileAttributes]::ReparsePoint}|Select-Object -First 1)){throw 'Reparse content'}
}
function Inventory([string]$Path){return @(Get-ChildItem -LiteralPath $Path -Recurse -Force -File|ForEach-Object {@{relative=$_.FullName.Substring($Path.Length+1);bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash}})}
function Verify([string]$Path,$Rows){foreach($f in $Rows){if((Get-FileHash -LiteralPath (Join-Path $Path $f.relative)).Hash -ne $f.sha256){throw ('Hash mismatch '+$f.relative)}};if(@(Get-ChildItem -LiteralPath $Path -Recurse -Force -File).Count -ne $Rows.Count){throw 'File count mismatch'}}
Guard $install;Guard $txn
if(Test-Path -LiteralPath (Join-Path $parent 'Sutram.sutram-lock')){throw 'Installer lock exists; inspect owner before preserving'}
$r=[ordered]@{action=$Action;name=$Name;time=[DateTime]::Now.ToString('o');user_path=[Environment]::GetEnvironmentVariable('Path','User');machine_path=[Environment]::GetEnvironmentVariable('Path','Machine')}
if($Action -eq 'backup'){
    if(Test-Path -LiteralPath $txn){throw 'Unexpected transaction exists before backup'}
    $backup=Join-Path $parent ('Sutram-v309-fix-'+$Name+'-20261107');Guard $backup
    if(Test-Path -LiteralPath $backup){throw 'Backup already exists'}
    $r.files=Inventory $install;Copy-Item -LiteralPath $install -Destination $backup -Recurse;Verify $backup $r.files
    $r.backup=$backup;$r.verified=$true
}else{
    $saved=Join-Path $parent ('Sutram-v309-fix-'+$Name+'-'+[DateTime]::Now.ToString('yyyyMMdd-HHmmss'));Guard $saved
    if(Test-Path -LiteralPath $saved){throw 'Preservation destination exists'}
    if(Test-Path -LiteralPath $install){$r.files=Inventory $install;Move-Item -LiteralPath $install -Destination $saved;$r.preserved=$saved}
    if(Test-Path -LiteralPath $txn){$savedTxn=$saved+'.transaction';Guard $savedTxn;if(Test-Path -LiteralPath $savedTxn){throw 'Transaction destination exists'};Move-Item -LiteralPath $txn -Destination $savedTxn;$r.preserved_transaction=$savedTxn}
    if($Action -eq 'restore'){
        $savedRecord=Get-Content -LiteralPath (Join-Path $OutDir ('backup-'+$BackupName+'.json')) -Raw|ConvertFrom-Json
        Guard $savedRecord.backup;Verify $savedRecord.backup $savedRecord.files
        Copy-Item -LiteralPath $savedRecord.backup -Destination $install -Recurse;Verify $install $savedRecord.files
        $r.restored=$savedRecord.backup;$r.verified=$true
    }
}
[IO.File]::WriteAllText((Join-Path $OutDir ($Action+'-'+$Name+'.json')),($r|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
Write-Host "$Action $Name completed; files preserved and no deletion performed."
