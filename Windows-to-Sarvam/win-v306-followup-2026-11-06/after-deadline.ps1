$r=Get-Content (Join-Path $PSScriptRoot 'upgrade.json') -Raw|ConvertFrom-Json
$rows=@()
foreach($processId in @($r.pid,$r.child.ProcessId)){
    $p=Get-Process -Id $processId -ErrorAction SilentlyContinue
    if($p){
        $threads=@($p.Threads|ForEach-Object{
            @{id=$_.Id;state=$_.ThreadState.ToString();wait=if($_.ThreadState -eq 'Wait'){$_.WaitReason.ToString()}else{''}}
        })
        $rows+=@{observed=[DateTime]::Now.ToString('o');pid=$p.Id;cpu=$p.CPU;threads=$threads}
    }
}
$rows|ConvertTo-Json -Depth 6|Set-Content (Join-Path $PSScriptRoot 'after-deadline-threads.json') -Encoding UTF8
