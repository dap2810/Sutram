# Exercise the actual staging function against files, without installing or changing HKCU.
$ErrorActionPreference='Stop'
$root=Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$engine=Join-Path $root 'windows\native-installer\install-core.ps1'
$tokens=$null;$errors=$null
$ast=[Management.Automation.Language.Parser]::ParseFile($engine,[ref]$tokens,[ref]$errors)
if($errors.Count){throw ($errors|Out-String)}
foreach($name in @('Log','Write-Durable','Journal','Get-Sha','Assert-NoReparsePath','Stage-Payload')){
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
# The real engine's publish path is exercised in the native interrupted/edit probes.
$checks|ConvertTo-Json
Write-Host ('Fixture retained at '+$work)
if(@($checks.Values|Where-Object {-not $_}).Count){throw 'Installer reuse fixture failed'}
