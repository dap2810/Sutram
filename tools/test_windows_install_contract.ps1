# Isolated function tests: no script entrypoint, registry, PATH or shortcuts run.
$ErrorActionPreference='Stop'
Set-StrictMode -Version 2.0
$project=[IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$testRoot=Join-Path $project ('build\windows\contract-'+[guid]::NewGuid().ToString('N'))
[void](New-Item -ItemType Directory -Path $testRoot)
function Assert-Test([bool]$Condition,[string]$Name) {
    if (-not $Condition) { throw ('FAIL '+$Name) }
    Write-Output ('PASS '+$Name)
}
foreach ($scriptName in @('install-core.ps1','uninstall-core.ps1')) {
    & {
        param($scriptName,$testRoot,$project)
        $tokens=$null;$parseErrors=$null
        $path=Join-Path $project ('windows\native-installer\'+$scriptName)
        $ast=[Management.Automation.Language.Parser]::ParseFile($path,[ref]$tokens,[ref]$parseErrors)
        Assert-Test ($parseErrors.Count -eq 0) ($scriptName+' parses')
        foreach ($name in @('Assert-NoReparsePath','Remove-ManifestFiles','Verify-Payload')) {
            $node=$ast.Find({param($n) $n -is [Management.Automation.Language.FunctionDefinitionAst] -and $n.Name -eq $name},$true)
            if ($node) { . ([scriptblock]::Create($node.Extent.Text)) }
        }
        function Log([string]$Message) { Write-Output $Message }
        $root=Join-Path $testRoot $scriptName
        [void](New-Item -ItemType Directory -Path $root)
        $owned=Join-Path $root 'owned.txt';$modified=Join-Path $root 'modified.txt';$user=Join-Path $root 'user.sm'
        [IO.File]::WriteAllText($owned,'packaged')
        [IO.File]::WriteAllText($modified,'original')
        [IO.File]::WriteAllText($user,'user data')
        $manifest=Join-Path $root 'payload.manifest.sha256'
        $rows=@(((Get-FileHash $owned).Hash+' *owned.txt'),((Get-FileHash $modified).Hash+' *modified.txt'))
        [IO.File]::WriteAllLines($manifest,$rows)
        [IO.File]::WriteAllText($modified,'user edits')
        Remove-ManifestFiles $root $manifest
        Assert-Test (-not (Test-Path $owned)) ($scriptName+' removes unchanged owned file')
        Assert-Test (([IO.File]::ReadAllText($modified)) -eq 'user edits') ($scriptName+' preserves edited file')
        Assert-Test (([IO.File]::ReadAllText($user)) -eq 'user data') ($scriptName+' preserves new user file')
        $outside=Join-Path $testRoot 'outside.txt'
        [IO.File]::WriteAllText($outside,'outside')
        [IO.File]::WriteAllText($manifest,(Get-FileHash $outside).Hash+' *..\outside.txt')
        $rejected=$false
        try { Remove-ManifestFiles $root $manifest } catch { $rejected=$true;Write-Output $_.Exception.Message }
        Assert-Test ($rejected -and (Test-Path $outside)) ($scriptName+' refuses traversal')
        if ($scriptName -eq 'install-core.ps1') {
            $payload=Join-Path $root 'payload'
            [void](New-Item -ItemType Directory -Path $payload)
            $file=Join-Path $payload 'one.txt';$hashes=Join-Path $payload 'payload.manifest.sha256'
            [IO.File]::WriteAllText($file,'one')
            [IO.File]::WriteAllText($hashes,(Get-FileHash $file).Hash+' *one.txt')
            Verify-Payload $payload
            Write-Output 'PASS correct payload hash'
            [IO.File]::WriteAllText($file,'tampered')
            $rejected=$false
            try { Verify-Payload $payload } catch { $rejected=$true;Write-Output $_.Exception.Message }
            Assert-Test $rejected 'refuses altered payload'
            [IO.File]::WriteAllText($file,'one')
            [IO.File]::WriteAllText((Join-Path $payload 'unexpected.txt'),'unexpected')
            $rejected=$false
            try { Verify-Payload $payload } catch { $rejected=$true;Write-Output $_.Exception.Message }
            Assert-Test $rejected 'refuses unmanifested payload'
        }
    } $scriptName $testRoot $project
}
Write-Output ('Fixtures retained for review: '+$testRoot)
Write-Output 'CONTRACT PASS; no install/uninstall entrypoint or Windows integration executed.'
