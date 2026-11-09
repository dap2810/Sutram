param(
    [Parameter(Mandatory=$true)][string]$InstallDir,
    [Parameter(Mandatory=$true)][string]$SelfPath,
    [Parameter(Mandatory=$true)][string]$LogPath
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
function Log([string]$Message) {   # R136: as install-core.ps1 - shared append; a log line never stops the uninstall
    $line = ([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')) + ' ' + $Message + "`r`n"
    for ($try = 0; $try -lt 3; $try++) {
        try {
            $fs = New-Object IO.FileStream($LogPath,[IO.FileMode]::Append,[IO.FileAccess]::Write,([IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete))
            try { $bytes = ([Text.UTF8Encoding]::new($false)).GetBytes($line); $fs.Write($bytes,0,$bytes.Length) } finally { $fs.Dispose() }
            return
        } catch { Start-Sleep -Milliseconds 50 }
    }
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
# R155: removes one entry - the first whose text (spaces around it aside) is the recorded one - and the one ';' that
# joined it, and changes nothing else: the other entries' text, empty entries and the value's kind stay. When the
# installer made the PATH value ($DeleteIfEmpty) and nothing else is left in it, the value itself goes.
function Remove-UserPathEntryOnce([string]$Entry,[bool]$DeleteIfEmpty) {
    $key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment',$true)
    if (-not $key) { return $false }
    $removed = $false
    try {
        if (-not ($key.GetValueNames() -contains 'Path')) { return $false }
        $raw = [string]$key.GetValue('Path','',[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
        $kind = $key.GetValueKind('Path')
        $parts = $raw -split ';'
        $rest = New-Object System.Collections.Generic.List[string]
        foreach ($item in $parts) {
            if (-not $removed -and [string]::Equals($item.Trim(),$Entry,[StringComparison]::OrdinalIgnoreCase)) { $removed = $true; continue }
            $rest.Add($item)
        }
        if ($removed) {
            $newPath = [string]::Join(';',$rest.ToArray())
            if ($DeleteIfEmpty -and $newPath.Length -eq 0) { $key.DeleteValue('Path',$false) }
            else { $key.SetValue('Path',$newPath,$kind) }
        }
    } finally { $key.Dispose() }
    if ($removed) { Broadcast-EnvironmentChange }
    return $removed
}
# R162 (ChatGPT R223 A): the lock is a file this installer creates and marks, and only such a file is taken. Up to
# R161 it was opened with OpenOrCreate and DeleteOnClose: a file a user had at that path was opened and deleted when
# the lock closed - by a run that then refused, too - and nothing read it first. Now the lock is made with CreateNew
# (it must not exist yet), still DeleteOnClose, and a marker is written into it. A file already at the path is read
# before anything is decided: held by another process -> another installer or uninstaller is working; a stale Sutram
# lock (the marker, or empty - up to R161 nothing was written into it; a lock is left only if the machine stopped)
# -> removed, after it was read, and the lock made again; anything else -> left as it is, and the run stops.
function Open-SutramLock([string]$Path) {
    $mark = [Text.Encoding]::ASCII.GetBytes("Sutram installer lock`r`n")
    for ($try = 0; $try -lt 3; $try++) {
        try {
            $fs = [IO.FileStream]::new($Path,[IO.FileMode]::CreateNew,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None,1,[IO.FileOptions]::DeleteOnClose)
            $fs.Write($mark,0,$mark.Length)
            $fs.Flush()
            return $fs
        } catch {
            if (-not [IO.File]::Exists($Path)) {
                if ($try -lt 2) { continue }
                throw ('The installer lock could not be made: ' + $Path + ' - ' + $_.Exception.Message)
            }
        }
        $len = -1
        $head = $null
        try {
            $held = [IO.FileStream]::new($Path,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::None)
        } catch {
            throw ('Another Sutram installer or uninstaller is working on this folder (its lock is ' + $Path + '). Let it finish, then run this one again.')
        }
        try {
            $len = $held.Length
            $head = New-Object byte[] ([int][Math]::Min([long]$len,[long]64))
            [void]$held.Read($head,0,$head.Length)
        } finally { $held.Dispose() }
        $stale = ($len -eq 0) -or (($len -eq $mark.Length) -and ([Convert]::ToBase64String($head) -eq [Convert]::ToBase64String($mark)))
        if (-not $stale) {
            throw ('A file that is not a Sutram lock is at ' + $Path + ' (' + $len + ' bytes). It was not changed. Move it elsewhere, then run this again.')
        }
        [IO.File]::Delete($Path)
    }
    throw ('The installer lock could not be taken: ' + $Path + '. Run this again.')
}
function Read-State([string]$Path) {
    $state = @{}
    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        foreach ($line in Get-Content -LiteralPath $Path) { $p=$line.IndexOf('='); if($p -gt 0){$state[$line.Substring(0,$p)]=$line.Substring($p+1)} }
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
function Remove-ManifestFiles([string]$Root,[string]$Manifest) {
    if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) { return }
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    Assert-NoReparsePath $rootFull
    $dirs = New-Object System.Collections.Generic.List[string]
    foreach ($line in Get-Content -LiteralPath $Manifest) {
        if ($line -notmatch '^([0-9a-fA-F]{64}) \*(.+)$') { throw 'Invalid installed manifest.' }
        $expectedHash = $Matches[1]
        $rel = $Matches[2]
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
try {
    [IO.File]::WriteAllText($LogPath,'Sutram Uninstall Log' + [Environment]::NewLine,([Text.UTF8Encoding]::new($false)))
    if (-not [Environment]::Is64BitProcess) { throw 'Uninstaller must run in 64-bit PowerShell.' }
    $InstallDir=[IO.Path]::GetFullPath($InstallDir).TrimEnd('\')
    Assert-NoReparsePath $InstallDir
    if (-not $env:LOCALAPPDATA) { throw 'LOCALAPPDATA is unavailable for this user.' }
    $userProgramsRoot=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
    if (-not $InstallDir.StartsWith($userProgramsRoot + '\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Refusing to uninstall outside the current user Programs folder.' }
    if (-not (Test-SutramMarker (Join-Path $InstallDir '.sutram-install'))) { throw 'This folder is not marked as a valid Sutram installation.' }
    # R137: not while an installer holds the folder's lock (install-core.ps1); held until this process ends.
    try {
        $script:lock = Open-SutramLock ($InstallDir + '.sutram-lock')
    } catch { throw $_.Exception.Message }
    $state=Read-State (Join-Path $InstallDir 'install-state.ini')
    $expectedSelf=Join-Path $InstallDir 'Sutram-Uninstall.exe'
    if (-not [string]::Equals([IO.Path]::GetFullPath($SelfPath),$expectedSelf,[StringComparison]::OrdinalIgnoreCase)) {
        throw 'Refusing to remove an unexpected uninstaller path.'
    }
    if (-not $state.ContainsKey('UninstallerSHA256')) { throw 'Missing uninstaller ownership hash.' }
    $selfHash=(Get-FileHash -LiteralPath $SelfPath -Algorithm SHA256).Hash
    if ($selfHash -ne $state['UninstallerSHA256']) { throw 'The uninstaller has changed; preserving it.' }

    if ($state.ContainsKey('PathAdded') -and $state['PathAdded']) { [void](Remove-UserPathEntryOnce $state['PathAdded'] ($state.ContainsKey('PathValueCreated') -and $state['PathValueCreated'] -eq '1')) }   # R154: the record, not PathOwned
    # R153 (ChatGPT R218 follow-up, Sarvam R153 WS1): a shortcut is removed only when it is one the installer
    # recorded as written - OwnedShortcuts, "<base64 path>|<SHA-256 of the .lnk>" - and its bytes are still those.
    # Not on a target that matches (a user's own link can point at the IDE), and not on DesktopOwned (v314's
    # installer wrote it for a link it had preserved). A link changed since, or recorded without a hash, is kept.
    $startMenu = Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram'
    $desktopDir = [Environment]::GetFolderPath('DesktopDirectory')
    if ($state.ContainsKey('OwnedShortcuts')) {
        foreach ($entry in ($state['OwnedShortcuts'] -split ',')) {
            $parts = $entry -split '\|', 2
            if ($parts.Count -lt 2 -or -not $parts[1]) { continue }
            try { $link = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($parts[0])) } catch { continue }
            $parent = [IO.Path]::GetDirectoryName($link)
            if (-not ([string]::Equals($parent,$startMenu,[StringComparison]::OrdinalIgnoreCase) -or
                      [string]::Equals($parent,$desktopDir,[StringComparison]::OrdinalIgnoreCase))) { continue }
            if (-not $link.EndsWith('.lnk',[StringComparison]::OrdinalIgnoreCase)) { continue }
            if (Test-Path -LiteralPath $link -PathType Leaf) {
                if ((Get-FileHash -LiteralPath $link -Algorithm SHA256).Hash -eq $parts[1]) { Remove-Item -LiteralPath $link -Force }
                else { Log ('Kept a shortcut changed since the installer wrote it: ' + $link) }
            }
        }
    }
    try { if ((Test-Path -LiteralPath $startMenu -PathType Container) -and -not (Get-ChildItem -LiteralPath $startMenu -Force -ErrorAction Stop | Select-Object -First 1)) { Remove-Item -LiteralPath $startMenu -Force } } catch {}

    $classKey='HKCU:\Software\Classes\Sutram.Source'
    $extKey='HKCU:\Software\Classes\.sm'
    $commandKey=Join-Path $classKey 'shell\open\command'
    $expectedCommand='"'+(Join-Path $InstallDir 'sutram-ide-gui.exe')+'" "%1"'
    # R154 (Sarvam R154 WS2-WS3, Muse R151 pair 3): what the installer wrote, and only that. v314 deleted the whole
    # Sutram.Source tree when its command matched - a verb a user had added under it went too. Now the values the
    # installer set go when they are still what it set, then each key it made goes only if nothing is left in it;
    # .sm's default goes only when the installer recorded setting it (AssociationSet) and it is still that value.
    $expectedIcon=Join-Path $InstallDir 'assets\sutram.ico'
    if ((Test-Path -LiteralPath $commandKey) -and (Get-Item -LiteralPath $commandKey).GetValue('') -eq $expectedCommand) {
        foreach ($pair in @(@('Software\Classes\Sutram.Source\shell\open\command',$expectedCommand),@('Software\Classes\Sutram.Source\DefaultIcon',$expectedIcon))) {
            $k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($pair[0],$true)
            if ($k) { try { if ([string]$k.GetValue('') -eq $pair[1]) { $k.DeleteValue('', $false) } } finally { $k.Dispose() } }
        }
        foreach ($sub in @('Software\Classes\Sutram.Source\shell\open\command','Software\Classes\Sutram.Source\shell\open','Software\Classes\Sutram.Source\shell','Software\Classes\Sutram.Source\DefaultIcon','Software\Classes\Sutram.Source')) {
            $k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($sub,$false)
            if ($k) {
                $empty=($k.ValueCount -eq 0 -and $k.SubKeyCount -eq 0)
                $k.Dispose()
                if ($empty) { [Microsoft.Win32.Registry]::CurrentUser.DeleteSubKey($sub,$false) } else { Log ('Kept HKCU\' + $sub + ': something else is in it.') }
            }
        }
        $setValue=''
        if ($state.ContainsKey('AssociationSet') -and $state['AssociationSet']) { $setValue=$state['AssociationSet'] }
        if ($setValue -and (Test-Path -LiteralPath $extKey) -and (Get-Item -LiteralPath $extKey).GetValue('') -eq $setValue) {
            $ext=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Software\Classes\.sm',$true)
            # R155: put back what was there before: an empty default if there was one, otherwise none.
            try {
                if ($state.ContainsKey('AssociationBefore') -and $state['AssociationBefore'] -eq 'empty') { $ext.SetValue('','',[Microsoft.Win32.RegistryValueKind]::String) }
                else { $ext.DeleteValue('', $false) }
            } finally { $ext.Dispose() }
        }
        Remove-ItemProperty -LiteralPath (Join-Path $extKey 'OpenWithProgids') -Name 'Sutram.Source' -ErrorAction SilentlyContinue
        # R143 (Windows v311 acceptance): the installer creates .sm\OpenWithProgids; removing its value left the key,
        # empty. A key is removed only when it has no value and no subkey left - another program's association,
        # or anything else under .sm, keeps it.
        foreach ($sub in @('Software\Classes\.sm\OpenWithProgids','Software\Classes\.sm')) {
            $k=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($sub,$false)
            if ($k) {
                $empty=($k.ValueCount -eq 0 -and $k.SubKeyCount -eq 0)
                $k.Dispose()
                if ($empty) { [Microsoft.Win32.Registry]::CurrentUser.DeleteSubKey($sub,$false); Log ('Removed the empty registry key HKCU\' + $sub) }
            }
        }
    }
    Remove-ManifestFiles $InstallDir (Join-Path $InstallDir 'payload.manifest.sha256')
    # R133: an installation that stopped part-way left the payload it was installing, and perhaps unfinished copies.
    Remove-ManifestFiles $InstallDir (Join-Path $InstallDir 'payload.pending.sha256')
    # R137 (I1): a '*.sutram-partial' file is left and named - its suffix does not prove the installer wrote it.
    foreach ($part in [IO.Directory]::GetFiles($InstallDir,'*.sutram-partial',[IO.SearchOption]::AllDirectories)) {
        Log ('Left in place (not removed; perhaps an unfinished v307 copy): ' + $part)
    }
    Remove-Item -LiteralPath (Join-Path $InstallDir 'payload.pending.sha256') -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $InstallDir 'install-journal.log') -Force -ErrorAction SilentlyContinue
    # R134: an installation that stopped part-way keeps the previous files in <folder>.sutram-transaction\backup;
    # they are the user's only copy of that installation, so uninstall leaves that folder and says where it is.
    $txnDir = $InstallDir + '.sutram-transaction'
    if (Test-Path -LiteralPath $txnDir -PathType Container) { Log ('Left in place (a stopped installation''s journal and backups): ' + $txnDir) }

    # The native launcher exits after starting this script. Delete only its
    # exact, hash-verified image, after Windows releases the executable mapping.
    $removed=$false
    for ($attempt=0;$attempt -lt 100;$attempt++) {
        try {
            Remove-Item -LiteralPath $expectedSelf -Force -ErrorAction Stop
            $removed=$true
            break
        } catch { Start-Sleep -Milliseconds 100 }
    }
    # R161 (ChatGPT R221): what a retry needs - the Settings entry, the manifest, the state with the uninstaller's hash,
    # the marker - is removed only now that the uninstaller itself is gone. Before R161 they went first, so a retry
    # after this loop ran out found 'not a valid Sutram installation' and no Settings entry. Every step above is safe
    # to run again: each removes only what is still there and still matches its record.
    if (-not $removed) { throw ('Uninstaller is still in use; close it and run uninstall again (Settings > Apps > Sutram, or ' + $expectedSelf + ').') }
    $unKey='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram'
    $registered=Get-ItemProperty -LiteralPath $unKey -ErrorAction SilentlyContinue
    if ($registered -and $registered.InstallLocation -eq $InstallDir) {
        Remove-Item -LiteralPath $unKey -Recurse -Force
    }
    Remove-Item -LiteralPath (Join-Path $InstallDir 'payload.manifest.sha256') -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $InstallDir 'install-state.ini') -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $InstallDir '.sutram-install') -Force -ErrorAction SilentlyContinue
    $installLog=Join-Path $InstallDir 'install.log'
    if ($state.ContainsKey('InstallLogSHA256') -and (Test-Path -LiteralPath $installLog -PathType Leaf) -and
        (Get-FileHash -LiteralPath $installLog -Algorithm SHA256).Hash -eq $state['InstallLogSHA256']) {
        Remove-Item -LiteralPath $installLog -Force
    }
    if (-not (Get-ChildItem -LiteralPath $InstallDir -Force | Select-Object -First 1)) {
        Remove-Item -LiteralPath $InstallDir -Force
    }
    Log 'Uninstall completed; user-created and user-modified files were preserved.'
    # R147 (Windows v312 acceptance: "uninstall leaves a temporary directory with a script and a log"): the wizard
    # staged this script and its log in a fresh %TEMP%\STMxxxx.tmp folder (GetTempFileNameW). On success that folder
    # goes, and only that: it must be in TEMP, have the wizard's name, and hold exactly this script and this log.
    # Each file is removed by its exact path and the folder by a non-recursive delete, so anything else in it keeps
    # it. A failed uninstall keeps both (the message box names the log).
    try {
        $stageDir = [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($PSCommandPath))
        $tempDir = [IO.Path]::GetFullPath([IO.Path]::GetTempPath()).TrimEnd('\')
        $names = @([IO.Directory]::GetFileSystemEntries($stageDir) | ForEach-Object { [IO.Path]::GetFileName($_) })
        if (([IO.Path]::GetDirectoryName($stageDir)).TrimEnd('\') -ieq $tempDir -and
            [IO.Path]::GetFileName($stageDir) -match '^STM[0-9A-Fa-f]{1,8}\.tmp$' -and
            [IO.Path]::GetDirectoryName([IO.Path]::GetFullPath($LogPath)) -ieq $stageDir -and
            $names.Count -eq 2 -and ($names -contains 'uninstall-core.ps1') -and ($names -contains 'uninstall.log')) {
            [IO.File]::Delete([IO.Path]::GetFullPath($LogPath))
            [IO.File]::Delete([IO.Path]::GetFullPath($PSCommandPath))
            [IO.Directory]::Delete($stageDir, $false)
        }
    } catch {}

    exit 0
} catch {
    $failure=$_.Exception.Message
    try{Log('ERROR: '+$failure)}catch{}
    # R143: this script runs with no console (the wizard starts it with CREATE_NO_WINDOW), so a failure is shown.
    try { [void](New-Object -ComObject WScript.Shell).Popup(('Sutram was not fully uninstalled: ' + $failure + [Environment]::NewLine + [Environment]::NewLine + 'Log: ' + $LogPath),0,'Sutram Uninstall',16) } catch {}
    exit 1
}
