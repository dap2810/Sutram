$ErrorActionPreference='Stop'
$start=(Get-Content (Join-Path $PSScriptRoot 'clean.json') -Raw|ConvertFrom-Json).started
$end=(Get-Content (Join-Path $PSScriptRoot 'final-state.json') -Raw|ConvertFrom-Json).observed_at
$r=[ordered]@{log='Microsoft-Windows-Windows Defender/Operational';start=$start;end=$end;events=@()}
try{$r.events=@(Get-WinEvent -FilterHashtable @{LogName=$r.log;StartTime=[DateTime]$start;EndTime=[DateTime]$end}|Select-Object TimeCreated,Id,LevelDisplayName,Message);$r.query_success=$true}
catch{$r.error=$_.Exception.Message;$r.error_id=$_.FullyQualifiedErrorId;$r.query_success=$_.FullyQualifiedErrorId -like 'NoMatchingEventsFound*'}
$r|ConvertTo-Json -Depth 5|Set-Content (Join-Path $PSScriptRoot 'defender.json') -Encoding UTF8
$r|ConvertTo-Json -Depth 5
