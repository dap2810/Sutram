param(
    [Parameter(Mandatory=$true)][string]$PayloadZip,
    [Parameter(Mandatory=$true)][string]$InstallDir,
    [Parameter(Mandatory=$true)][string]$SetupExePath,
    [Parameter(Mandatory=$true)][string]$LogPath,
    [switch]$AddPath,
    [switch]$DesktopShortcut,
    [switch]$VerifyOnly
)
$ErrorActionPreference = 'Stop'
$script:txnLock = $null       # R134: the transaction folder's lock, held while this run installs
$script:journalPath = $null
# R130: no progress bars (Expand-Archive and Copy-Item draw one, which a console can stall) and no confirmation
# prompts: the wizard runs this with -NonInteractive and no console window, and waits at most 15 minutes.
$ProgressPreference = 'SilentlyContinue'
$ConfirmPreference = 'None'
Set-StrictMode -Version 2.0

# R136: the log is appended through a stream that shares read, write and delete with anyone else, and a log line
# that cannot be written never stops the installation. Windows PowerShell 5.1's Add-Content refuses while another
# process holds the log open, even a reader that shares everything (ChatGPT's native fixture, v307), and with
# ErrorActionPreference = Stop that refusal ended the install.
function Log([string]$Message) {
    $stamp = [DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')
    $line = "[{0}] {1}`r`n" -f $stamp,$Message
    for ($try = 0; $try -lt 3; $try++) {
        try {
            $share = [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete
            $fs = New-Object IO.FileStream($LogPath,[IO.FileMode]::Append,[IO.FileAccess]::Write,$share)
            try {
                $bytes = ([Text.UTF8Encoding]::new($false)).GetBytes($line)
                $fs.Write($bytes,0,$bytes.Length)
            } finally { $fs.Dispose() }
            return
        } catch { Start-Sleep -Milliseconds 50 }
    }
}
# No unbounded compiler preflights: a broken native compiler must not
# freeze the Windows wizard forever inside WaitForSingleObject(INFINITE).
# Keep the log in the user's TEMP directory and fail closed (no install).
function Invoke-SutramSelfTest([string]$ExePath,[string]$Argument,[string]$Stage) {
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo.FileName = $ExePath
    $p.StartInfo.Arguments = $Argument
    $p.StartInfo.UseShellExecute = $false
    $p.StartInfo.RedirectStandardOutput = $true
    $p.StartInfo.RedirectStandardError = $true
    $p.StartInfo.CreateNoWindow = $true
    try {
        Log ("Native self-test start: " + $Stage)
        if (-not $p.Start()) { throw ("Unable to start " + $Stage) }
        $outTask=$p.StandardOutput.ReadToEndAsync()
        $errTask=$p.StandardError.ReadToEndAsync()
        if (-not $p.WaitForExit(8000)) {
            try { $p.Kill() } catch {}
            try { [void]$p.WaitForExit(2000) } catch {}
            throw ("Native compiler timed out during " + $Stage + " after 8000 ms; installation aborted.")
        }
        $stdout = $outTask.Result
        $stderr = $errTask.Result
        Log ("Native self-test exit: " + $Stage + " code=" + $p.ExitCode)
        if ($p.ExitCode -ne 0 -or [string]::IsNullOrWhiteSpace($stdout)) {
            throw ("Native compiler failed " + $Stage + " code=" + $p.ExitCode + " stderr=" + $stderr.Trim())
        }
        return $stdout
    } finally {
        $p.Dispose()
    }
}
# R134 (ChatGPT R207 WS3): the installation transaction. A private folder beside the target, on the same volume
# (<target>.sutram-transaction), holds a durable journal, the staged files and the backups of replaced files.
# Nothing in the target is deleted, truncated or replaced before the journal says what will happen to it; every
# file reaches the target by a rename on the same volume, so a target file is never half-written; a rerun reads the
# journal and finishes what an interrupted run began. The v303 and v306 stalls each left a folder no later run could
# classify (an empty file under a real name, the previous payload deleted, the new one partly written).
function Write-Durable([string]$Path,[string]$Text,[bool]$Append) {
    $mode = [IO.FileMode]::Create
    if ($Append) { $mode = [IO.FileMode]::Append }
    $fs = New-Object IO.FileStream($Path,$mode,[IO.FileAccess]::Write,[IO.FileShare]::Read,4096,[IO.FileOptions]::WriteThrough)
    try {
        $bytes = ([Text.UTF8Encoding]::new($false)).GetBytes($Text)
        $fs.Write($bytes,0,$bytes.Length)
        $fs.Flush($true)
    } finally { $fs.Dispose() }
}
function Journal([string]$Line) { Write-Durable $script:journalPath ($Line + "`r`n") $true }
function Get-Sha([string]$Path) { return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToUpperInvariant() }
function Move-Into([string]$From,[string]$To) {
    $dir = [IO.Path]::GetDirectoryName($To)
    if (-not [IO.Directory]::Exists($dir)) { [void][IO.Directory]::CreateDirectory($dir) }
    [IO.File]::Move($From,$To)
}
# Read-Journal(path) -> what an earlier run recorded: whether it committed, and every hash it staged or published
# for each file (those files are this installer's own, whatever version wrote them).
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
# Stage-Payload(stage, txnStage, newFiles): copy every payload file into the transaction folder, verified by hash.
# Each file is logged when its copy starts and when it is done, so a stop names the file it stopped in.
function Stage-Payload([string]$From,[string]$To,[hashtable]$NewFiles) {
    $files = @([IO.Directory]::GetFiles($From,'*',[IO.SearchOption]::AllDirectories) | Where-Object {
        -not [string]::Equals([IO.Path]::GetFileName($_),'payload.manifest.sha256',[StringComparison]::OrdinalIgnoreCase) } | Sort-Object)
    Log ('Staging ' + $files.Length + ' Sutram files in ' + $To + '.')
    $n = 0
    foreach ($src in $files) {
        $rel = $src.Substring($From.Length).TrimStart('\')
        $n++
        $staged = Join-Path $To $rel
        if ((Test-Path -LiteralPath $staged -PathType Leaf) -and (Get-Sha $staged) -eq $NewFiles[$rel]) {
            Log ('Already staged ' + $n + '/' + $files.Length + ': ' + $rel)
            continue
        }
        Log ('START ' + $n + '/' + $files.Length + ': ' + $rel)
        $part = $staged + '.part'
        $dir = [IO.Path]::GetDirectoryName($staged)
        if (-not [IO.Directory]::Exists($dir)) { [void][IO.Directory]::CreateDirectory($dir) }
        [IO.File]::Copy($src,$part,$true)
        if ((Get-Sha $part) -ne $NewFiles[$rel]) { throw ('The staged copy of ' + $rel + ' does not match the payload.') }
        if ([IO.File]::Exists($staged)) { [IO.File]::Delete($staged) }
        [IO.File]::Move($part,$staged)
        Journal ("STAGED`t" + $rel + "`t" + $NewFiles[$rel])
        Log ('DONE  ' + $n + '/' + $files.Length + ': ' + $rel)
    }
    return ,$files
}
# R133: a manifest file ('<sha256> *<relative path>' per line) as a table, relative path -> upper-case hash.
function Read-Manifest([string]$Path) {
    $t = @{}
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $t }
    foreach ($line in [IO.File]::ReadAllLines($Path)) {
        if ($line -notmatch '^([0-9a-fA-F]{64}) \*(.+)$') { throw ('Invalid manifest: ' + $Path) }
        $t[$Matches[2]] = $Matches[1].ToUpperInvariant()
    }
    return $t
}
# R130: the PATH a terminal opened now would get - the machine's entries, then the user's - and the first folder on it
# that has a sutram.exe. A new terminal runs that one: if it is not this installation, the student runs another Sutram.
function Get-FreshPath {
    $machine = [Environment]::GetEnvironmentVariable('Path','Machine')
    $user = [Environment]::GetEnvironmentVariable('Path','User')
    return (@($machine,$user) | Where-Object { $_ }) -join ';'
}
function Find-SutramOnPath([string]$PathValue) {
    foreach ($item in ($PathValue -split ';')) {
        $dir = Normalize-PathEntry $item
        if ([string]::IsNullOrWhiteSpace($dir)) { continue }
        try { if (Test-Path -LiteralPath (Join-Path $dir 'sutram.exe') -PathType Leaf) { return (Join-Path $dir 'sutram.exe') } } catch { continue }
    }
    return $null
}
# R130: every other Sutram this user's terminals could find - on the machine or user PATH, or in the folder the
# older Sutram installers used (%LOCALAPPDATA%\Sutram) - excluding this installation's own bin folder.
function Find-OtherSutram([string]$OwnBin) {
    $found = New-Object System.Collections.Generic.List[string]
    $own = Normalize-PathEntry $OwnBin
    foreach ($item in ((Get-FreshPath) -split ';')) {
        $dir = Normalize-PathEntry $item
        if ([string]::IsNullOrWhiteSpace($dir)) { continue }
        if ([string]::Equals($dir,$own,[StringComparison]::OrdinalIgnoreCase)) { continue }
        try {
            $exe = Join-Path $dir 'sutram.exe'
            if ((Test-Path -LiteralPath $exe -PathType Leaf) -and -not $found.Contains($exe)) { $found.Add($exe) }
        } catch { continue }
    }
    if ($env:LOCALAPPDATA) {
        foreach ($legacy in @((Join-Path $env:LOCALAPPDATA 'Sutram\bin\sutram.exe'),(Join-Path $env:LOCALAPPDATA 'Sutram\sutram.exe'))) {
            $legacyDir = Normalize-PathEntry ([IO.Path]::GetDirectoryName($legacy))
            if ([string]::Equals($legacyDir,$own,[StringComparison]::OrdinalIgnoreCase)) { continue }
            if ((Test-Path -LiteralPath $legacy -PathType Leaf) -and -not $found.Contains($legacy)) { $found.Add($legacy) }
        }
    }
    return ,$found.ToArray()
}
# R130: run 'sutram --version' as a new terminal would - cmd.exe, the fresh PATH, a working folder without Sutram in it.
function Invoke-FreshShellVersion {
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo.FileName = $env:ComSpec
    $p.StartInfo.Arguments = '/d /c sutram --version'
    $p.StartInfo.UseShellExecute = $false
    $p.StartInfo.RedirectStandardOutput = $true
    $p.StartInfo.RedirectStandardError = $true
    $p.StartInfo.CreateNoWindow = $true
    $p.StartInfo.WorkingDirectory = $env:TEMP
    $p.StartInfo.EnvironmentVariables['PATH'] = (Get-FreshPath)
    try {
        Log 'New-terminal check start: sutram --version through PATH.'
        if (-not $p.Start()) { throw 'Unable to start cmd.exe for the new-terminal check.' }
        $outTask=$p.StandardOutput.ReadToEndAsync()
        $errTask=$p.StandardError.ReadToEndAsync()
        if (-not $p.WaitForExit(8000)) {
            try { $p.Kill() } catch {}
            throw 'The new-terminal check timed out after 8000 ms.'
        }
        Log ('New-terminal check exit: code=' + $p.ExitCode)
        return $outTask.Result
    } finally { $p.Dispose() }
}
function Normalize-PathEntry([string]$Value) {
    if ($null -eq $Value) { return '' }
    $clean = $Value.Trim().Trim('"').TrimEnd('\')
    if ([string]::IsNullOrWhiteSpace($clean)) { return '' }
    return [Environment]::ExpandEnvironmentVariables($clean).TrimEnd('\')
}
function Broadcast-EnvironmentChange {
    if (-not ('Sutram.NativeMethods' -as [type])) {
        Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
namespace Sutram {
  public static class NativeMethods {
    [DllImport("user32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    public static extern IntPtr SendMessageTimeout(IntPtr hWnd, uint Msg, UIntPtr wParam, string lParam, uint flags, uint timeout, out UIntPtr result);
  }
}
'@
    }
    $result = [UIntPtr]::Zero
    [void][Sutram.NativeMethods]::SendMessageTimeout([IntPtr]0xffff,0x001A,[UIntPtr]::Zero,'Environment',2,5000,[ref]$result)
}
function Set-UserPathEntry([string]$Entry,[bool]$ShouldExist) {
    $key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment',$true)
    if (-not $key) { $key = [Microsoft.Win32.Registry]::CurrentUser.CreateSubKey('Environment') }
    if (-not $key) { throw 'Unable to open the current user Environment registry key.' }
    $changed = $false
    try {
        $raw = [string]$key.GetValue('Path','',[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
        $entries = New-Object System.Collections.Generic.List[string]
        $target = Normalize-PathEntry $Entry
        $found = $false
        foreach ($item in ($raw -split ';')) {
            $n = Normalize-PathEntry $item
            if ([string]::IsNullOrWhiteSpace($n)) { continue }
            if ([string]::Equals($n,$target,[StringComparison]::OrdinalIgnoreCase)) {
                $found = $true
                if (-not $ShouldExist) { $changed = $true; continue }
            }
            $entries.Add($item.Trim())
        }
        if ($ShouldExist -and -not $found) { $entries.Add($Entry); $changed = $true }
        if ($changed) {
            $newPath = [string]::Join(';',$entries.ToArray())
            if ($newPath.Length -gt 32760) { throw 'The user PATH would become too long.' }
            $key.SetValue('Path',$newPath,[Microsoft.Win32.RegistryValueKind]::ExpandString)
        }
    } finally { $key.Dispose() }
    if ($changed) { Broadcast-EnvironmentChange }
    return $changed
}
function Read-State([string]$Path) {
    $state = @{}
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        foreach ($line in Get-Content -LiteralPath $Path) {
            $p = $line.IndexOf('=')
            if ($p -gt 0) { $state[$line.Substring(0,$p)] = $line.Substring($p+1) }
        }
    }
    return $state
}
function Test-SutramMarker([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $false }
    try {
        $text = [IO.File]::ReadAllText($Path,[Text.Encoding]::UTF8).Trim()
        return [string]::Equals($text,'Sutram Windows installation',[StringComparison]::Ordinal)
    } catch { return $false }
}
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
function Remove-ManifestFiles([string]$Root,[string]$Manifest,[hashtable]$Keep = @{}) {
    if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) { return }
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    Assert-NoReparsePath $rootFull
    $dirs = New-Object System.Collections.Generic.List[string]
    foreach ($line in Get-Content -LiteralPath $Manifest) {
        if ($line -notmatch '^([0-9a-fA-F]{64}) \*(.+)$') { throw 'Invalid installed manifest.' }
        $expectedHash = $Matches[1]
        $rel = $Matches[2]
        if ($Keep.ContainsKey($rel)) { continue }   # R133: still in the payload - overwritten, not deleted
        $target = [IO.Path]::GetFullPath((Join-Path $rootFull $rel))
        if (-not $target.StartsWith($rootFull + '\',[StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe manifest path: $rel" }
        $walk = $target
        while ($walk -and $walk.StartsWith($rootFull + '\',[StringComparison]::OrdinalIgnoreCase)) {
            if (Test-Path -LiteralPath $walk) {
                if ((Get-Item -LiteralPath $walk -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
                    throw "Refusing a reparse-point path: $walk"
                }
            }
            $walk = [IO.Path]::GetDirectoryName($walk)
        }
        if (Test-Path -LiteralPath $target -PathType Leaf) {
            $actualHash=(Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash
            if ($actualHash -ne $expectedHash) {
                Log ("Preserved user-modified package file: " + $target)
                continue
            }
            Remove-Item -LiteralPath $target -Force
        }
        $dir = [IO.Path]::GetDirectoryName($target)
        while ($dir -and $dir.StartsWith($rootFull + '\',[StringComparison]::OrdinalIgnoreCase)) {
            if (-not $dirs.Contains($dir)) { $dirs.Add($dir) }
            $parent = [IO.Path]::GetDirectoryName($dir)
            if (-not $parent -or [string]::Equals($parent,$dir,[StringComparison]::OrdinalIgnoreCase)) { break }
            $dir = $parent
        }
    }
    foreach ($dir in ($dirs.ToArray() | Sort-Object { $_.Length } -Descending)) {
        try {
            if ((Test-Path -LiteralPath $dir -PathType Container) -and -not (Get-ChildItem -LiteralPath $dir -Force -ErrorAction Stop | Select-Object -First 1)) {
                Remove-Item -LiteralPath $dir -Force
            }
        } catch {}
    }
}
function Verify-Payload([string]$Stage) {
    $manifest = Join-Path $Stage 'payload.manifest.sha256'
    if (-not (Test-Path -LiteralPath $manifest -PathType Leaf)) { throw 'Payload integrity manifest is missing.' }
    $rootFull = [IO.Path]::GetFullPath($Stage).TrimEnd('\')
    $expectedFiles = @{}
    foreach ($line in Get-Content -LiteralPath $manifest) {
        if ($line -notmatch '^([0-9a-fA-F]{64}) \*(.+)$') { throw "Invalid payload manifest line: $line" }
        $expected = $Matches[1].ToLowerInvariant(); $rel = $Matches[2]
        $file = [IO.Path]::GetFullPath((Join-Path $rootFull $rel))
        if (-not $file.StartsWith($rootFull + '\',[StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe payload path: $rel" }
        if ($expectedFiles.ContainsKey($rel)) { throw "Duplicate payload manifest path: $rel" }
        $expectedFiles[$rel] = $true
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) { throw "Payload file missing: $rel" }
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $file).Hash.ToLowerInvariant()
        if ($actual -ne $expected) { throw "Payload hash mismatch: $rel" }
    }
    foreach ($file in Get-ChildItem -LiteralPath $rootFull -File -Recurse) {
        if ([string]::Equals($file.FullName,$manifest,[StringComparison]::OrdinalIgnoreCase)) { continue }
        $rel = $file.FullName.Substring($rootFull.Length).TrimStart('\')
        if (-not $expectedFiles.ContainsKey($rel)) { throw "Unmanifested payload file found: $rel" }
    }
}
$script:ownedShortcuts = New-Object Collections.Generic.List[string]
function New-Shortcut([string]$Path,[string]$Target,[string]$Arguments,[string]$WorkingDir,[string]$Icon) {
    $shell = New-Object -ComObject WScript.Shell
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        $encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Path))
        if (-not $oldState.ContainsKey('OwnedShortcuts') -or $encoded -notin ($oldState['OwnedShortcuts'] -split ',')) {
            Log ('Preserved pre-existing user shortcut: '+$Path)
            return
        }
    }
    $script:ownedShortcuts.Add([Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($Path)))
    $sc = $shell.CreateShortcut($Path)
    $sc.TargetPath = $Target
    if ($Arguments) { $sc.Arguments = $Arguments }
    if ($WorkingDir) { $sc.WorkingDirectory = $WorkingDir }
    if ($Icon) { $sc.IconLocation = $Icon }
    $sc.Save()
}

try {
    [IO.File]::WriteAllText($LogPath,'Sutram Setup Log' + [Environment]::NewLine,([Text.UTF8Encoding]::new($false)))
    Log 'Starting installation.'
    if (-not [Environment]::Is64BitOperatingSystem) { throw 'Sutram requires 64-bit Windows.' }
    if (-not [Environment]::Is64BitProcess) { throw 'Setup must run in a 64-bit PowerShell process.' }
    if (-not (Test-Path -LiteralPath $PayloadZip -PathType Leaf)) { throw 'Embedded payload.zip is missing.' }
    if (-not (Test-Path -LiteralPath $SetupExePath -PathType Leaf)) { throw 'Setup executable path is invalid.' }

    $InstallDir = [IO.Path]::GetFullPath($InstallDir).TrimEnd('\')
    Assert-NoReparsePath $InstallDir
    if (-not $env:LOCALAPPDATA) { throw 'LOCALAPPDATA is unavailable for this user.' }
    $userProgramsRoot = [IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
    if (-not $InstallDir.StartsWith($userProgramsRoot + '\',[StringComparison]::OrdinalIgnoreCase)) {
        throw ('Sutram is a per-user install and must stay under: ' + $userProgramsRoot)
    }
    if ($InstallDir.Length -gt 220) { throw 'The installation path is too long. Choose a shorter folder.' }
    if ($InstallDir.StartsWith('\\')) { throw 'Network/UNC installation folders are not supported. Choose a local drive.' }
    if ($InstallDir.IndexOfAny([char[]]'%&|<>^!') -ge 0) { throw 'The installation path contains shell metacharacters that are not supported.' }
    if ($AddPath -and $InstallDir.Contains(';')) { throw 'The installation path cannot contain a semicolon when Add to PATH is selected.' }
    $root = [IO.Path]::GetPathRoot($InstallDir).TrimEnd('\')
    if ([string]::Equals($InstallDir,$root,[StringComparison]::OrdinalIgnoreCase)) { throw 'Installing directly into a drive root is not allowed.' }
    foreach ($unsafe in @($env:WINDIR,$env:SystemRoot,$env:ProgramFiles,${env:ProgramFiles(x86)},$env:USERPROFILE)) {
        if ($unsafe -and [string]::Equals($InstallDir,[IO.Path]::GetFullPath($unsafe).TrimEnd('\'),[StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe installation folder: $InstallDir" }
    }

    $unKey = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram'
    $registered = Get-ItemProperty -LiteralPath $unKey -ErrorAction SilentlyContinue
    if ($registered -and $registered.InstallLocation) {
        $registeredDir = [IO.Path]::GetFullPath([string]$registered.InstallLocation).TrimEnd('\')
        if (-not [string]::Equals($registeredDir,$InstallDir,[StringComparison]::OrdinalIgnoreCase) -and (Test-SutramMarker (Join-Path $registeredDir '.sutram-install'))) {
            throw ("Sutram is already installed at: {0}. Uninstall that copy first, or choose the same installation folder." -f $registeredDir)
        }
    }

    # R130: refuse while another Sutram is installed where a terminal could find it. Two installations side by side
    # made a new terminal run the older one (Windows round, v303: 'Sutram 1.4.0'), and a student cannot tell which.
    Log 'Checking for another Sutram installation.'
    $others = Find-OtherSutram (Join-Path $InstallDir 'bin')
    if ($others.Length -gt 0) {
        foreach ($o in $others) { Log ('Another Sutram is installed: ' + $o) }
        throw ('Another Sutram is already installed: ' + ($others -join '; ') + '. A new terminal could run that one instead of this. Uninstall it (Settings > Apps > Sutram, or its own uninstaller), or delete that folder and remove it from PATH, then run this installer again.')
    }

    $marker = Join-Path $InstallDir '.sutram-install'
    $statePath = Join-Path $InstallDir 'install-state.ini'
    $oldState = Read-State $statePath
    # R133: an installation that stopped part-way (a hang, a closed window, a machine that slept) left this file,
    # written before anything else was changed: the payload it was installing. Its files are this installer's own.
    $pendingPath = Join-Path $InstallDir 'payload.pending.sha256'
    $pending = Test-Path -LiteralPath $pendingPath -PathType Leaf
    # R134: the transaction folder beside the target, and what its journal says.
    $txnDir = Join-Path ([IO.Path]::GetDirectoryName($InstallDir)) ([IO.Path]::GetFileName($InstallDir) + '.sutram-transaction')
    Assert-NoReparsePath $txnDir
    $script:journalPath = Join-Path $txnDir 'journal.txt'
    $earlier = Read-Journal $script:journalPath
    if ($earlier.Exists -and $earlier.Committed) {
        Log ('Removing the folder of an installation that completed: ' + $txnDir)
        Remove-Item -LiteralPath $txnDir -Recurse -Force
        $earlier = Read-Journal $script:journalPath
    }
    if ($earlier.Exists) {
        Log ('A previous installation stopped part-way (its journal is ' + $script:journalPath + '); this run finishes it.')
        $pending = $true
    }
    if ($pending) {
        Log ('A previous installation stopped part-way (it left ' + $pendingPath + '); this run finishes it.')
        $parts = @()
        if ([IO.Directory]::Exists($InstallDir)) { $parts = [IO.Directory]::GetFiles($InstallDir,'*.sutram-partial',[IO.SearchOption]::AllDirectories) }
        foreach ($part in $parts) {
            Assert-NoReparsePath $part
            Log ('Removing an unfinished copy: ' + $part)
            [IO.File]::Delete($part)
        }
    }
    if (Test-Path -LiteralPath $InstallDir -PathType Container) {
        $first = Get-ChildItem -LiteralPath $InstallDir -Force -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($first -and -not (Test-SutramMarker $marker) -and -not $pending) { throw "The selected folder is not empty and is not an existing Sutram installation: $InstallDir" }
    }

    # Check ownership conflicts before creating or changing an installation.
    $classCommand='HKCU:\Software\Classes\Sutram.Source\shell\open\command'
    $wantedCommand='"'+(Join-Path $InstallDir 'sutram-ide-gui.exe')+'" "%1"'
    if (Test-Path -LiteralPath $classCommand) {
        $currentCommand=(Get-Item -LiteralPath $classCommand).GetValue('')
        if ($currentCommand -and $currentCommand -ne $wantedCommand) { throw 'A conflicting Sutram.Source registration exists.' }
    }
    # R133: after a stopped installation the metadata is between two states (the marker written, the state not yet;
    # the uninstaller replaced, its hash not yet recorded); the pending record says whose they are.
    if ((Test-SutramMarker $marker) -and -not $pending) {
        if (-not (Test-Path -LiteralPath (Join-Path $InstallDir 'payload.manifest.sha256') -PathType Leaf) -or
            -not $oldState.ContainsKey('UninstallerSHA256')) { throw 'Existing installation ownership metadata is incomplete.' }
        $oldUninstaller=Join-Path $InstallDir 'Sutram-Uninstall.exe'
        if ((Test-Path -LiteralPath $oldUninstaller -PathType Leaf) -and
            (Get-FileHash -LiteralPath $oldUninstaller -Algorithm SHA256).Hash -ne $oldState['UninstallerSHA256']) {
            throw 'The existing uninstaller has been modified; refusing to overwrite it.'
        }
    }

    $stage = Join-Path $env:TEMP ('Sutram-Payload-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Force -Path $stage | Out-Null
    try {
        Log 'Extracting embedded payload.'
        Expand-Archive -LiteralPath $PayloadZip -DestinationPath $stage -Force
        Verify-Payload $stage
        $testExe = Join-Path $stage 'bin\sutram.exe'
        $guiTestExe = Join-Path $stage 'sutram-ide-gui.exe'
        $guiCompiler = Join-Path $stage 'win\sutram.exe'
        if (-not (Test-Path -LiteralPath $guiTestExe -PathType Leaf)) { throw 'Payload is missing Sutram GUI.' }
        if (-not (Test-Path -LiteralPath $guiCompiler -PathType Leaf)) { throw 'Payload is missing GUI-compatible compiler path.' }
        if (-not (Test-Path -LiteralPath $testExe -PathType Leaf)) { throw 'Payload does not contain bin\sutram.exe.' }
        $v = Invoke-SutramSelfTest $testExe '--version' 'pre-install --version'
        $h = Invoke-SutramSelfTest $testExe '--help' 'pre-install --help'

        if ($VerifyOnly) {
            Log 'VERIFY ONLY PASS: payload hashes and compiler checks; installation not performed.'
            exit 0
        }
        # Refuse an upgrade that would replace user edits or newly conflicting files.
        # R133: a file is this installer's own - safe to replace - if it is what the previous installation's manifest
        # says, what an installation that stopped part-way was writing (payload.pending.sha256), or byte for byte
        # what this payload puts there. v305 called its own half-copied linker 'a user file' and refused for good.
        $previousManifest = Join-Path $InstallDir 'payload.manifest.sha256'
        $previousFiles = Read-Manifest $previousManifest
        $pendingFiles = Read-Manifest $pendingPath
        $newFiles = Read-Manifest (Join-Path $stage 'payload.manifest.sha256')
        # R134: and what an interrupted run's journal says it staged or published. A file that matches none of these
        # is not this installer's to replace (changed since installation, or not ours at all): it is preserved, and
        # every such file is listed with a way out, before anything changes.
        $conflicts = New-Object System.Collections.Generic.List[string]
        if ($previousFiles.Count -gt 0 -or $pendingFiles.Count -gt 0 -or $earlier.Exists) {
            foreach ($file in Get-ChildItem -LiteralPath $stage -File -Recurse) {
                $relative=$file.FullName.Substring($stage.Length+1)
                if ($relative -eq 'payload.manifest.sha256') { continue }
                $target=Join-Path $InstallDir $relative
                if (Test-Path -LiteralPath $target -PathType Leaf) {
                    $have = Get-Sha $target
                    $ours = ($previousFiles.ContainsKey($relative) -and $have -eq $previousFiles[$relative].ToUpperInvariant()) -or
                            ($pendingFiles.ContainsKey($relative) -and $have -eq $pendingFiles[$relative]) -or
                            ($newFiles.ContainsKey($relative) -and $have -eq $newFiles[$relative]) -or
                            ($earlier.Known.ContainsKey($relative) -and ($earlier.Known[$relative] -contains $have))
                    if (-not $ours) { $conflicts.Add($target) }
                }
            }
        }
        if ($conflicts.Count -gt 0) {
            foreach ($c in $conflicts) { Log ('Not this installer''s file (preserved): ' + $c) }
            $recovery = $InstallDir + '-recovery-' + [DateTime]::Now.ToString('yyyyMMdd-HHmmss')
            throw ($conflicts.Count.ToString() + " file(s) in the installation folder are not what this installer wrote (changed since installation, or not Sutram's), so it will not replace them: " +
                   (($conflicts | Select-Object -First 5) -join '; ') + '. Nothing was changed. Move those files elsewhere, or move the whole folder aside (for example to ' + $recovery + '), then run this installer again.')
        }
        foreach ($file in Get-ChildItem -LiteralPath $stage -File -Recurse) {
            Assert-NoReparsePath (Join-Path $InstallDir $file.FullName.Substring($stage.Length+1))
        }
        New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
        $txnStage = Join-Path $txnDir 'stage'
        $txnBackup = Join-Path $txnDir 'backup'
        foreach ($d in @($txnDir,$txnStage,$txnBackup)) { if (-not [IO.Directory]::Exists($d)) { [void][IO.Directory]::CreateDirectory($d) } }
        # One installer at a time for this folder: the lock is held until this run ends.
        try {
            $script:txnLock = [IO.File]::Open((Join-Path $txnDir 'lock'),[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
        } catch { throw ('Another Sutram installer is working on ' + $InstallDir + '. Let it finish, then run this one again.') }
        $txid = [guid]::NewGuid().ToString('N')
        $oldManifestSha = 'none'
        if (Test-Path -LiteralPath $previousManifest -PathType Leaf) { $oldManifestSha = Get-Sha $previousManifest }
        # R134: the journal is durably written before anything in the target is changed.
        Journal ("BEGIN`t" + $txid + "`t" + $InstallDir + "`t" + (Get-Sha (Join-Path $stage 'payload.manifest.sha256')) + "`t" + $oldManifestSha)
        Log ('Transaction ' + $txid + ' begun (journal ' + $script:journalPath + ').')
        foreach ($meta in @('payload.manifest.sha256','install-state.ini','.sutram-install','Sutram-Uninstall.exe')) {
            $m = Join-Path $InstallDir $meta
            $mb = Join-Path (Join-Path $txnBackup '_previous') $meta
            if ((Test-Path -LiteralPath $m -PathType Leaf) -and -not (Test-Path -LiteralPath $mb -PathType Leaf)) {
                $mbDir = [IO.Path]::GetDirectoryName($mb)
                if (-not [IO.Directory]::Exists($mbDir)) { [void][IO.Directory]::CreateDirectory($mbDir) }
                [IO.File]::Copy($m,$mb,$false)
            }
        }
        Log 'Recording the payload being installed (payload.pending.sha256).'
        [IO.File]::Copy((Join-Path $stage 'payload.manifest.sha256'),$pendingPath,$true)
        # Stage every file beside the target first (the target is not touched while the payload is copied).
        $files = Stage-Payload $stage $txnStage $newFiles
        # Publish: the old file, if any, goes to the backup (journaled first), then the staged file is renamed in.
        # v303-v306 deleted the whole previous payload first, then wrote the new one into the target.
        Log ('Publishing ' + $files.Length + ' files into ' + $InstallDir + '.')
        $n = 0
        foreach ($src in $files) {
            $rel = $src.Substring($stage.Length).TrimStart('\')
            $n++
            $target = Join-Path $InstallDir $rel
            $staged = Join-Path $txnStage $rel
            $prior = 'absent'
            if (Test-Path -LiteralPath $target -PathType Leaf) {
                $have = Get-Sha $target
                if ($have -eq $newFiles[$rel]) {
                    if (Test-Path -LiteralPath $staged -PathType Leaf) { [IO.File]::Delete($staged) }
                    Journal ("PUBLISHED`t" + $rel + "`t" + $newFiles[$rel])
                    continue
                }
                $bk = Join-Path $txnBackup $rel
                if (Test-Path -LiteralPath $bk -PathType Leaf) {
                    [IO.File]::Delete($target)   # an earlier run kept the original; this is that run's own copy
                } else {
                    Journal ("BACKUP`t" + $rel + "`t" + $have)
                    Move-Into $target $bk
                }
                $prior = $have
            }
            Journal ("PUBLISH`t" + $rel + "`t" + $prior)
            Log ('PUBLISH ' + $n + '/' + $files.Length + ': ' + $rel)
            Move-Into $staged $target
            Journal ("PUBLISHED`t" + $rel + "`t" + $newFiles[$rel])
        }
        # Files of the previous payload (or of a stopped run) that this one does not have go to the backup too,
        # if they are still as installed; a changed one stays where it is.
        foreach ($known in @($previousFiles,$pendingFiles)) {
            foreach ($rel in @($known.Keys)) {
                if ($newFiles.ContainsKey($rel)) { continue }
                $target = Join-Path $InstallDir $rel
                if (-not (Test-Path -LiteralPath $target -PathType Leaf)) { continue }
                if ((Get-Sha $target) -ne $known[$rel].ToUpperInvariant()) { Log ('Preserved a changed file the new payload does not have: ' + $target); continue }
                Journal ("OBSOLETE`t" + $rel + "`t" + $known[$rel])
                Move-Into $target (Join-Path $txnBackup $rel)
            }
        }
        Log 'Writing the payload manifest.'
        Write-Durable $previousManifest ([IO.File]::ReadAllText((Join-Path $stage 'payload.manifest.sha256'))) $false
        Journal "FINALIZE"
        Log 'Copying the uninstaller.'
        [IO.File]::Copy($SetupExePath,(Join-Path $InstallDir 'Sutram-Uninstall.exe'),$true)
        Log 'Writing the installation marker.'
        [IO.File]::WriteAllText($marker,'Sutram Windows installation' + [Environment]::NewLine,([Text.UTF8Encoding]::new($false)))

        $installedExe = Join-Path $InstallDir 'bin\sutram.exe'
        $check = Invoke-SutramSelfTest $installedExe '--version' 'post-install --version'

        $binDir = Join-Path $InstallDir 'bin'
        $previousOwned = ($oldState.ContainsKey('PathOwned') -and $oldState['PathOwned'] -eq '1')
        $pathOwned = $previousOwned
        if ($AddPath) {
            Log 'Ensuring Sutram is present in the current user PATH.'
            $pathAddedNow = [bool](Set-UserPathEntry $binDir $true)
            # Own the entry only if this installer created it now or already owned it
            # from the previous Sutram installation. A pre-existing manual PATH entry
            # remains user-owned and will not be removed by uninstall.
            $pathOwned = ($previousOwned -or $pathAddedNow)
        } elseif ($previousOwned) {
            Log 'Removing previously installer-owned Sutram PATH entry.'
            [void](Set-UserPathEntry $binDir $false)
            $pathOwned = $false
        } else {
            $pathOwned = $false
        }

        # R130: the completion check that verifies something - a new terminal must run THIS compiler.
        if ($AddPath) {
            $first = Find-SutramOnPath (Get-FreshPath)
            $ownExe = Join-Path $binDir 'sutram.exe'
            if (-not $first -or -not [string]::Equals([IO.Path]::GetFullPath($first),[IO.Path]::GetFullPath($ownExe),[StringComparison]::OrdinalIgnoreCase)) {
                throw ('A new terminal would run ' + $first + ', not ' + $ownExe + '. Remove that one from PATH and run this installer again.')
            }
            $fresh = Invoke-FreshShellVersion
            if ($fresh.Trim() -ne $check.Trim()) {
                throw ('A new terminal reports a different Sutram: [' + $fresh.Trim() + '] instead of [' + $check.Trim() + '].')
            }
            Log ('New-terminal check: ' + ($fresh -split "`n")[0].Trim())
        } else {
            Log 'PATH was not requested: a new terminal finds this Sutram only through its Start-menu terminal.'
        }

        Log 'Creating Start-menu shortcuts.'
        $startMenu = Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram'
        New-Item -ItemType Directory -Force -Path $startMenu | Out-Null
        $icon = Join-Path $InstallDir 'assets\sutram.ico'
        $guiInstalled = Join-Path $InstallDir 'sutram-ide-gui.exe'
        if (-not (Test-Path -LiteralPath $guiInstalled -PathType Leaf)) { throw 'GUI executable missing after extraction.' }
        New-Shortcut (Join-Path $startMenu 'Sutram IDE.lnk') $guiInstalled '' $InstallDir $icon
        $terminalArgs = '/K "set "PATH=' + $binDir + ';%PATH%" && sutram --version"'
        New-Shortcut (Join-Path $startMenu 'Sutram Terminal.lnk') $env:ComSpec $terminalArgs $env:USERPROFILE $icon
        $doc = Join-Path $InstallDir 'docs\sutram-book-english.html'
        if (Test-Path -LiteralPath $doc) { New-Shortcut (Join-Path $startMenu 'Sutram Documentation.lnk') $doc '' $InstallDir $icon }
        New-Shortcut (Join-Path $startMenu 'Uninstall Sutram.lnk') (Join-Path $InstallDir 'Sutram-Uninstall.exe') '--uninstall' $InstallDir $icon
        $desktopLink = Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'Sutram IDE.lnk'
        $previousDesktopOwned = (($oldState.ContainsKey('DesktopOwned') -and $oldState['DesktopOwned'] -eq '1') -or ($oldState.ContainsKey('DesktopShortcut') -and $oldState['DesktopShortcut'] -eq '1'))
        $desktopOwned = $previousDesktopOwned
        if ($DesktopShortcut) {
            if ((Test-Path -LiteralPath $desktopLink -PathType Leaf) -and -not $previousDesktopOwned) {
                Log 'A pre-existing user desktop shortcut named Sutram IDE.lnk was preserved.'
                $desktopOwned = $false
            } else {
                New-Shortcut $desktopLink $guiInstalled '' $InstallDir $icon
                $desktopOwned = $true
            }
        } elseif ($previousDesktopOwned) {
            Remove-Item -LiteralPath $desktopLink -Force -ErrorAction SilentlyContinue
            $desktopOwned = $false
        } else {
            $desktopOwned = $false
        }

        Log 'Registering the .sm file type and the uninstaller.'
        $classKey='HKCU:\Software\Classes\Sutram.Source'
        $extKey='HKCU:\Software\Classes\.sm'
        $commandKey=Join-Path $classKey 'shell\open\command'
        $openCommand='"' + $guiInstalled + '" "%1"'
        if (Test-Path -LiteralPath $commandKey) {
            $existing=(Get-Item -LiteralPath $commandKey).GetValue('')
            if ($existing -and $existing -ne $openCommand) { throw 'A conflicting Sutram.Source registration exists.' }
        }
        [void](New-Item -Path $commandKey -Force)
        Set-Item -LiteralPath $commandKey -Value $openCommand
        [void](New-Item -Path (Join-Path $classKey 'DefaultIcon') -Force)
        Set-Item -LiteralPath (Join-Path $classKey 'DefaultIcon') -Value $icon
        [void](New-Item -Path $extKey -Force)
        $existingDefault=(Get-Item -LiteralPath $extKey).GetValue('')
        $associationOwned=($oldState.ContainsKey('AssociationOwned') -and $oldState['AssociationOwned'] -eq '1')
        if (-not $existingDefault) {
            Set-Item -LiteralPath $extKey -Value 'Sutram.Source'
            $associationOwned=$true
        }
        [void](New-Item -Path (Join-Path $extKey 'OpenWithProgids') -Force)
        [void](New-ItemProperty -Path (Join-Path $extKey 'OpenWithProgids') -Name 'Sutram.Source' -Value '' -PropertyType String -Force)
        New-Item -Path $unKey -Force | Out-Null
        New-ItemProperty -Path $unKey -Name DisplayName -Value 'Sutram' -PropertyType String -Force | Out-Null
        # R133: the version Windows shows is the compiler's (its --version 'Sutram X.Y (vN)' gives X.Y.N), not a fixed 0.1.0.
        $displayVersion = '0.0.0'
        if ($check -match 'Sutram (\d+\.\d+) \(v(\d+)\)') { $displayVersion = $Matches[1] + '.' + $Matches[2] }
        New-ItemProperty -Path $unKey -Name DisplayVersion -Value $displayVersion -PropertyType String -Force | Out-Null
        New-ItemProperty -Path $unKey -Name Publisher -Value 'Sutram Project' -PropertyType String -Force | Out-Null
        New-ItemProperty -Path $unKey -Name InstallLocation -Value $InstallDir -PropertyType String -Force | Out-Null
        New-ItemProperty -Path $unKey -Name DisplayIcon -Value (Join-Path $InstallDir 'assets\sutram.ico') -PropertyType String -Force | Out-Null
        New-ItemProperty -Path $unKey -Name UninstallString -Value ('"' + (Join-Path $InstallDir 'Sutram-Uninstall.exe') + '" --uninstall') -PropertyType String -Force | Out-Null
        New-ItemProperty -Path $unKey -Name NoModify -Value 1 -PropertyType DWord -Force | Out-Null
        New-ItemProperty -Path $unKey -Name NoRepair -Value 1 -PropertyType DWord -Force | Out-Null

        $pathOwnedValue = '0'
        if ($pathOwned) { $pathOwnedValue = '1' }
        $desktopOwnedValue = '0'
        if ($desktopOwned) { $desktopOwnedValue = '1' }
        $stateLines = @(
            ('Version=' + $displayVersion),
            ('OwnedShortcuts=' + ($script:ownedShortcuts.ToArray() -join ',')),
            ('PathOwned=' + $pathOwnedValue),
            ('DesktopOwned=' + $desktopOwnedValue),
            ('AssociationOwned=' + [int]$associationOwned),
            ('UninstallerSHA256=' + (Get-FileHash -LiteralPath $SetupExePath -Algorithm SHA256).Hash)
        )
        [IO.File]::WriteAllLines($statePath,$stateLines,([Text.UTF8Encoding]::new($false)))

        Journal ("COMMITTED`t" + $txid)
        if ($pending -or (Test-Path -LiteralPath $pendingPath -PathType Leaf)) { Remove-Item -LiteralPath $pendingPath -Force }
        Log ('Installation complete: ' + $InstallDir)
        # R134: the committed transaction's folder goes: its journal is kept as install-journal.log, the backups
        # (the previous installation's files) are removed once the new one is complete. A stop here leaves a
        # committed journal, which the next run only cleans up.
        try {
            [IO.File]::Copy($script:journalPath,(Join-Path $InstallDir 'install-journal.log'),$true)
            if ($script:txnLock) { $script:txnLock.Dispose(); $script:txnLock = $null }
            Remove-Item -LiteralPath $txnDir -Recurse -Force
        } catch { Log ('The transaction folder could not be removed now (the next run removes it): ' + $txnDir) }
        # The wizard deletes its temporary staging directory after success.
        # Preserve the actual installer log under this user's installed tree
        # so the Round 62 auditor can examine real installation events.
        Copy-Item -LiteralPath $LogPath -Destination (Join-Path $InstallDir 'install.log') -Force
        Add-Content -LiteralPath $statePath -Encoding UTF8 -Value ('InstallLogSHA256='+(Get-FileHash -LiteralPath (Join-Path $InstallDir 'install.log') -Algorithm SHA256).Hash)
    } finally {
        if ($script:txnLock) { $script:txnLock.Dispose(); $script:txnLock = $null }
        $stageFull=[IO.Path]::GetFullPath($stage)
        $tempFull=[IO.Path]::GetFullPath($env:TEMP).TrimEnd('\')
        if (-not $stageFull.StartsWith($tempFull+'\Sutram-Payload-',[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe stage cleanup path.' }
        Remove-Item -LiteralPath $stageFull -Recurse -Force -ErrorAction SilentlyContinue
    }
    exit 0
} catch {
    try { Log ('ERROR: ' + $_.Exception.Message) } catch {}
    exit 1
}
