param([string]$Work,[string]$Name,[switch]$Barrier)
$ErrorActionPreference='Stop'
$InstallDir=Join-Path $Work 'installed'
$reads=Join-Path $Work ($Name+'-reads.txt')
function Record([string]$Name){[IO.File]::AppendAllText($reads,$Name+"`n")}
function Read-State([string]$Path){Record 'state';Read-StateImpl $Path}
function Get-ItemProperty {param($LiteralPath,$ErrorAction) Record 'registry';return $null}
function Find-OtherSutram {param($Path) Record 'discovery';return ,@()}
function Log {param($Message)}
function Assert-NoReparsePath([string]$Path) {
    $walk=[IO.Path]::GetFullPath($Path)
    while ($walk) {
        if (Test-Path -LiteralPath $walk) {
            if ((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                throw "Refusing a reparse-point path: $walk"
            }
        }
        $parent=[IO.Path]::GetDirectoryName($walk)
        if ($parent -eq $walk) { break }
        $walk=$parent
    }
}
function Read-StateImpl([string]$Path) {
    $state = @{}
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        foreach ($line in Get-Content -LiteralPath $Path) {
            $p = $line.IndexOf('=')
            if ($p -gt 0) { $state[$line.Substring(0,$p)] = $line.Substring($p+1) }
        }
    }
    return $state
}
function Read-Journal([string]$Path) {
    $j = @{ Exists = $false; Committed = $false; Known = @{} }
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $j }
    $j.Exists = $true
    foreach ($line in [IO.File]::ReadAllLines($Path)) {
        $f = $line.Split("`t")
        if ($f[0] -eq 'COMMITTED') { $j.Committed = $true; $j.Known = @{} }
        elseif ($f[0] -eq 'BEGIN') { $j.Committed = $false }
        elseif (($f[0] -eq 'STAGED' -or $f[0] -eq 'PUBLISHED') -and $f.Length -ge 3) {
            if (-not $j.Known.ContainsKey($f[1])) { $j.Known[$f[1]] = @() }
            $j.Known[$f[1]] += $f[2].ToUpperInvariant()
        }
    }
    return $j
}
$result=[ordered]@{error=$null;state=$null;pending=$null;reads=@()}
try {
$txnDir = Join-Path ([IO.Path]::GetDirectoryName($InstallDir)) ([IO.Path]::GetFileName($InstallDir) + '.sutram-transaction')
Assert-NoReparsePath $txnDir
$lockPath = Join-Path ([IO.Path]::GetDirectoryName($InstallDir)) ([IO.Path]::GetFileName($InstallDir) + '.sutram-lock')
Assert-NoReparsePath $lockPath
if($Barrier){
    [IO.File]::WriteAllText((Join-Path $Work ($Name+'-ready')),'ready')
    $timer=[Diagnostics.Stopwatch]::StartNew()
    while(-not [IO.File]::Exists((Join-Path $Work ($Name+'-go')))){
        if($timer.Elapsed.TotalSeconds -gt 20){throw 'Fixture barrier timeout'}
        Start-Sleep -Milliseconds 25
    }
}
try {
        $script:txnLock = New-Object IO.FileStream($lockPath,[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None,1,[IO.FileOptions]::DeleteOnClose)
    } catch { throw ('Another Sutram installer or uninstaller is working on ' + $InstallDir + '. Let it finish, then run this one again.') }
$unKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram'
$registered = Get-ItemProperty -LiteralPath $unKey -ErrorAction SilentlyContinue
if ($registered -and $registered.InstallLocation) {
        $registeredDir = [IO.Path]::GetFullPath([string]$registered.InstallLocation).TrimEnd('\')
        if (-not [string]::Equals($registeredDir,$InstallDir,[StringComparison]::OrdinalIgnoreCase) -and (Test-SutramMarker (Join-Path $registeredDir '.sutram-install'))) {
            throw ("Sutram is already installed at: {0}. Uninstall that copy first, or choose the same installation folder." -f $registeredDir)
        }
    }
Log 'Checking for another Sutram installation.'
$others = Find-OtherSutram (Join-Path $InstallDir 'bin')
if ($others.Length -gt 0) {
        foreach ($o in $others) { Log ('Another Sutram is installed: ' + $o) }
        throw ('Another Sutram is already installed: ' + ($others -join '; ') + '. A new terminal could run that one instead of this. Uninstall it (Settings > Apps > Sutram, or its own uninstaller), or delete that folder and remove it from PATH, then run this installer again.')
    }
$marker = Join-Path $InstallDir '.sutram-install'
$statePath = Join-Path $InstallDir 'install-state.ini'
$oldState = Read-State $statePath
$pendingPath = Join-Path $InstallDir 'payload.pending.sha256'
$pending = Test-Path -LiteralPath $pendingPath -PathType Leaf
$script:journalPath = Join-Path $txnDir 'journal.txt'
$earlier = Read-Journal $script:journalPath
    $result.state=$oldState;$result.pending=$pending
} catch {$result.error=$_.Exception.Message}
finally {if($script:txnLock){$script:txnLock.Dispose()}}
if([IO.File]::Exists($reads)){$result.reads=@([IO.File]::ReadAllLines($reads))}
[IO.File]::WriteAllText((Join-Path $Work ($Name+'.json')),($result|ConvertTo-Json -Depth 5))