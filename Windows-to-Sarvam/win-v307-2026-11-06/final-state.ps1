$ErrorActionPreference='Stop'
$install=Join-Path $env:LOCALAPPDATA 'Programs\Sutram'
$r=[ordered]@{observed_at=[DateTime]::Now.ToString('o');owned_processes=@();pending_exists=(Test-Path -LiteralPath (Join-Path $install 'payload.pending.sha256'));partial_files=@(Get-ChildItem -LiteralPath $install -Recurse -File -Filter '*.sutram-partial'|ForEach-Object {$_.FullName});file_count=@(Get-ChildItem -LiteralPath $install -Recurse -File).Count}
foreach($phase in @('clean','upgrade-observer-failed','upgrade','reader-interference/interrupt','reader-interference/recovery','interrupt','recovery')){
    $path=Join-Path $PSScriptRoot ($phase+'.json')
    if(-not(Test-Path -LiteralPath $path)){continue}
    $p=Get-Content -LiteralPath $path -Raw|ConvertFrom-Json
    foreach($entry in @(@{id=$p.pid;started=$p.process_started},@{id=$p.child.pid;started=$p.child.started})){
        if(-not $entry.id){continue}
        $live=Get-Process -Id $entry.id -ErrorAction SilentlyContinue
        $same=$live -and ($live.StartTime.ToString('o') -eq $entry.started)
        $r.owned_processes+=@{phase=$phase;pid=$entry.id;same_process_still_running=[bool]$same;pid_reused=[bool]($live -and -not $same)}
    }
}
$key=Get-ItemProperty 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram' -ErrorAction SilentlyContinue
$r.display_version=$key.DisplayVersion
$r.cli=@(& (Join-Path $install 'bin\sutram.exe') --version);$r.cli_exit=$LASTEXITCODE
$r.pass=-not $r.pending_exists -and -not $r.partial_files.Count -and -not @($r.owned_processes|Where-Object same_process_still_running).Count -and $r.cli_exit -eq 0 -and $r.cli[0] -eq 'Sutram 1.0 (v307) - sampurna sutra' -and $r.display_version -eq '1.0.307'
$r|ConvertTo-Json -Depth 5|Set-Content (Join-Path $PSScriptRoot 'final-state.json') -Encoding UTF8
$r|ConvertTo-Json -Depth 5
if(-not $r.pass){throw 'Final state verification failed'}
