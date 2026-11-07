$ErrorActionPreference='Stop'
$r=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'a3.json') -Raw|ConvertFrom-Json
if(-not $r.status) { throw 'A3 observation is still running' }
$cleanup=[ordered]@{started=[DateTime]::Now.ToString('o');reason='Close only this test-owned A3 wizard/child after the full timeout observation';stopped=@()}
if($r.status -eq 'NO_RESULT_AFTER_930_SECONDS') {
    if(([DateTime]::Now-[DateTime]::Parse($r.started)).TotalSeconds -lt 930) { throw 'Do not interrupt the natural timeout observation' }
    foreach($target in @(@{pid=$r.child.ProcessId;command=$r.child.CommandLine},@{pid=$r.pid;exe=$r.setup})) {
        $processId=[int]$target.pid
        $actual=Get-CimInstance Win32_Process -Filter "ProcessId = $processId"
        if(-not $actual) { continue }
        if($target.command -and $actual.CommandLine -ne $target.command) { throw 'Child PID identity changed' }
        if($target.exe -and $actual.ExecutablePath -ne $target.exe) { throw 'Wizard PID identity changed' }
        $p=Get-Process -Id $processId
        if($p.StartTime -lt [DateTime]::Parse($r.started).AddSeconds(-2)) { throw 'Process predates our test' }
        Stop-Process -InputObject $p -Force
        if(-not $p.WaitForExit(5000)) { throw 'Owned process did not stop' }
        $cleanup.stopped+=@{pid=$processId;name=$actual.Name;at=[DateTime]::Now.ToString('o')}
    }
}
if($r.engine_log -and (Test-Path -LiteralPath $r.engine_log)) { Copy-Item -LiteralPath $r.engine_log -Destination (Join-Path $PSScriptRoot 'a3-engine.log') -Force }
$cleanup|ConvertTo-Json -Depth 5|Set-Content (Join-Path $PSScriptRoot 'cleanup-a3.json') -Encoding UTF8
& (Join-Path $PSScriptRoot 'prepare-clean.ps1')
& (Join-Path $PSScriptRoot 'install.ps1') -Phase a4
