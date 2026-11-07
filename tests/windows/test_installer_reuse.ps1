# From PR #68 (Windows, 664ff188/7ab8c439), taken into main in R142 unchanged, with the engine checks it exercises.
# Exercise the actual staging function against files, without installing or changing HKCU.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$engine=Join-Path $root 'windows\native-installer\install-core.ps1'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($engine,[ref]$tokens,[ref]$errors)
if($errors.Count){throw ($errors|Out-String)}
foreach($name in @('Log','Write-Durable','Journal','Get-Sha','Assert-NoReparsePath','Stage-Payload','Move-Into')){
    $f=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name},$true)
    if(-not $f){throw ('Missing function '+$name)}
    . ([ScriptBlock]::Create($f.Extent.Text))
}
$work=Join-Path $root ('build\reuse-fixture-'+[guid]::NewGuid().ToString('N'))
$source=Join-Path $work 'payload';$staging=Join-Path $work 'transaction';$target=Join-Path $work 'installed'
foreach($path in @($source,$staging,$target)){[void][IO.Directory]::CreateDirectory($path)}
$LogPath=Join-Path $work 'run.log';$script:journalPath=Join-Path $work 'journal.txt'
$utf8=[Text.UTF8Encoding]::new($false)
$files=@{}
foreach($name in @('same.md','missing.md','changed.md','staged.md')){
    [IO.File]::WriteAllText((Join-Path $source $name),('payload '+$name+"`n"),$utf8)
    $files[$name]=Get-Sha (Join-Path $source $name)
}
Copy-Item -LiteralPath (Join-Path $source 'same.md') -Destination $target
Copy-Item -LiteralPath (Join-Path $source 'staged.md') -Destination $staging
[IO.File]::WriteAllText((Join-Path $target 'changed.md'),'owner edit',$utf8)
$before=Get-Sha (Join-Path $target 'changed.md')
$stamp=(Get-Item -LiteralPath (Join-Path $target 'same.md')).LastWriteTimeUtc
$result=Stage-Payload $source $staging $files $target
$checks=[ordered]@{
    all_files_returned=($result.Count -eq 4)
    matching_target_not_staged=(-not [IO.File]::Exists((Join-Path $staging 'same.md')))
    matching_target_unchanged=((Get-Item -LiteralPath (Join-Path $target 'same.md')).LastWriteTimeUtc -eq $stamp)
    missing_target_staged=((Get-Sha (Join-Path $staging 'missing.md')) -eq $files['missing.md'])
    changed_target_preserved=((Get-Sha (Join-Path $target 'changed.md')) -eq $before)
    changed_target_replacement_staged=((Get-Sha (Join-Path $staging 'changed.md')) -eq $files['changed.md'])
    staged_copy_reused=((Get-Sha (Join-Path $staging 'staged.md')) -eq $files['staged.md'])
}
$log=[IO.File]::ReadAllText($LogPath)
$checks.only_two_copy_starts=([regex]::Matches($log,'\] START ').Count -eq 2)
$checks.reuse_visible=($log.Contains('Already installed ') -and $log.Contains('Already staged '))
# Execute the actual publish loop with a target modified after reuse was chosen.
# This catches the dangerous case where the engine would move the only copy away
# and then discover there was no staged replacement. No registry or installer runs.
$loops=@($ast.FindAll({param($n) $n -is [Management.Automation.Language.ForEachStatementAst] -and $n.Extent.Text.Contains('Move-Into $staged $target')},$true))
if($loops.Count -ne 1){throw 'Could not identify the publication loop'}
$publish=[ScriptBlock]::Create($loops[0].Extent.Text)
$stage=$source;$txnStage=$staging;$txnBackup=Join-Path $work 'backup';$InstallDir=$target
$newFiles=$files;$files=@(Join-Path $source 'same.md')
$previousFiles=@{};$pendingFiles=@{};$earlier=@{Known=@{}}
$same=Join-Path $target 'same.md'
[IO.File]::WriteAllText($same,'edited after reuse check',$utf8)
$edited=Get-Sha $same;$caught=$false
try {. $publish} catch {$caught=$_.Exception.Message.Contains('not replaced')}
$checks.edit_after_reuse_refused=($caught -and (Get-Sha $same) -eq $edited -and -not [IO.Directory]::Exists($txnBackup))
$previousFiles['same.md']=$edited
$caught=$false
try {. $publish} catch {$caught=$_.Exception.Message.Contains('after its installed copy was verified')}
$checks.known_changed_copy_not_moved_without_replacement=($caught -and (Get-Sha $same) -eq $edited -and -not [IO.Directory]::Exists($txnBackup))
# Move only the fixture's known file to a verified sibling; preserve its bytes.
$saved=Join-Path $InstallDir 'same.saved'
if([IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($same)) -ne $InstallDir -or [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($saved)) -ne $InstallDir){throw 'Unsafe fixture move'}
[IO.File]::Move($same,$saved)
$caught=$false
try {. $publish} catch {$caught=$_.Exception.Message.Contains('disappeared after')}
$checks.removed_copy_requires_restage=($caught -and (Get-Sha $saved) -eq $edited)
$checks.failed_publication_not_journaled=(-not [IO.File]::ReadAllText($script:journalPath).Contains("PUBLISH`t"))
# A new staging pass provides the missing file; publication then succeeds.
$files=Stage-Payload $source $staging $newFiles $InstallDir
$files=@($files|Where-Object {[IO.Path]::GetFileName($_) -eq 'same.md'})
. $publish
$checks.retry_restages_and_publishes=((Get-Sha $same) -eq $newFiles['same.md'] -and [IO.File]::ReadAllText($script:journalPath).Contains("PUBLISHED`tsame.md`t"))
$checks|ConvertTo-Json
Write-Host ('Fixture retained at '+$work)
if(@($checks.Values|Where-Object {-not $_}).Count){throw 'Installer reuse fixture failed'}
