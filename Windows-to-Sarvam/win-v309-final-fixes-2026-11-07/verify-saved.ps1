# Read-only checks of the completed run. Writes evidence only to this folder.
$ErrorActionPreference='Stop'
$out=$PSScriptRoot
$root=Split-Path -Parent (Split-Path -Parent $out)
$rows=@()
foreach($file in Get-ChildItem -LiteralPath $out -Filter '*.json' -Recurse -File){
    $r=Get-Content -LiteralPath $file.FullName -Raw|ConvertFrom-Json
    # Other reports are arrays of test cases. PowerShell's property enumeration
    # turns absent pid properties into a truthy array of nulls; do not treat it as PID 0.
    if($r -is [array] -or -not $r.PSObject.Properties['pid'] -or -not $r.PSObject.Properties['process_started']){continue}
    if([int]$r.pid -le 0 -or -not $r.process_started){throw ('Invalid process identity in '+$file.Name)}
    $name=$file.FullName.Substring($out.Length+1)
    $identities=@(@{role='wizard';id=$r.pid;started=$r.process_started})
    if($r.child){$identities+=@{role='engine';id=$r.child.pid;started=$r.child.started}}
    foreach($identity in $identities){
        $p=Get-Process -Id $identity.id -ErrorAction SilentlyContinue
        $same=$false;$currentStart=$null
        if($p){$currentStart=$p.StartTime.ToString('o');$same=($p.StartTime.ToUniversalTime() -eq ([DateTime]::Parse($identity.started)).ToUniversalTime())}
        $rows+=@{phase=$name;role=$identity.role;pid=$identity.id;recorded_start=$identity.started;pid_present=($null -ne $p);current_start=$currentStart;same_process_alive=$same}
    }
}
$r=@{checked_at=[DateTime]::Now.ToString('o');processes=$rows;all_owned_processes_closed=(@($rows|Where-Object {$_.same_process_alive}).Count -eq 0);installer_lock_exists=(Test-Path -LiteralPath (Join-Path $env:LOCALAPPDATA 'Programs\Sutram.sutram-lock'))}
[IO.File]::WriteAllText((Join-Path $out 'final-processes.json'),($r|ConvertTo-Json -Depth 5),[Text.UTF8Encoding]::new($false))
$text=@()
foreach($relative in @('docs\LANGUAGE-REFERENCE.md','lang\sanskrit.lang','README.md')){
    $text+=('> certutil -hashfile '+$relative+' SHA256')
    $text+=(& certutil -hashfile (Join-Path $root $relative) SHA256)
    if($LASTEXITCODE){throw 'certutil failed'}
}
$text+='> (Get-Content -Raw docs\LANGUAGE-REFERENCE.md) -match "`r`n"'
$text+=((Get-Content -LiteralPath (Join-Path $root 'docs\LANGUAGE-REFERENCE.md') -Raw) -match "`r`n").ToString()
[IO.File]::WriteAllLines((Join-Path $out 'payload-native-commands.txt'),[string[]]$text,[Text.UTF8Encoding]::new($false))
python (Join-Path $out 'identity.py') --name handoff-identity
if($LASTEXITCODE){throw 'Installed identity changed'}
$r|ConvertTo-Json -Depth 5
if(-not $r.all_owned_processes_closed -or $r.installer_lock_exists){throw 'An installer process/lock remains'}
