param(
    [Parameter(Mandatory=$true)][string]$InstallDir,
    [Parameter(Mandatory=$true)][string]$SelfPath,
    [Parameter(Mandatory=$true)][string]$LogPath
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
function Log([string]$Message) { Add-Content -LiteralPath $LogPath -Value (([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')) + ' ' + $Message) -Encoding UTF8 }
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
function Remove-UserPathEntry([string]$Entry) {
    $key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Environment',$true)
    if (-not $key) { return }
    $changed = $false
    try {
        $raw = [string]$key.GetValue('Path','',[Microsoft.Win32.RegistryValueOptions]::DoNotExpandEnvironmentNames)
        $target = Normalize-PathEntry $Entry
        $entries = New-Object System.Collections.Generic.List[string]
        foreach ($item in ($raw -split ';')) {
            $n = Normalize-PathEntry $item
            if ([string]::IsNullOrWhiteSpace($n)) { continue }
            if ([string]::Equals($n,$target,[StringComparison]::OrdinalIgnoreCase)) { $changed = $true; continue }
            $entries.Add($item.Trim())
        }
        if ($changed) { $key.SetValue('Path',[string]::Join(';',$entries.ToArray()),[Microsoft.Win32.RegistryValueKind]::ExpandString) }
    } finally { $key.Dispose() }
    if ($changed) { Broadcast-EnvironmentChange }
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
    $state=Read-State (Join-Path $InstallDir 'install-state.ini')
    $expectedSelf=Join-Path $InstallDir 'Sutram-Uninstall.exe'
    if (-not [string]::Equals([IO.Path]::GetFullPath($SelfPath),$expectedSelf,[StringComparison]::OrdinalIgnoreCase)) {
        throw 'Refusing to remove an unexpected uninstaller path.'
    }
    if (-not $state.ContainsKey('UninstallerSHA256')) { throw 'Missing uninstaller ownership hash.' }
    $selfHash=(Get-FileHash -LiteralPath $SelfPath -Algorithm SHA256).Hash
    if ($selfHash -ne $state['UninstallerSHA256']) { throw 'The uninstaller has changed; preserving it.' }

    if($state.ContainsKey('PathOwned') -and $state['PathOwned'] -eq '1'){Remove-UserPathEntry (Join-Path $InstallDir 'bin')}
    $startMenu = Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram'
    foreach ($shortcut in @('Sutram IDE.lnk','Sutram Terminal.lnk','Sutram Documentation.lnk','Uninstall Sutram.lnk')) {
        $link=Join-Path $startMenu $shortcut
        $encoded=[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($link))
        if ($state.ContainsKey('OwnedShortcuts') -and $encoded -in ($state['OwnedShortcuts'] -split ',') -and (Test-Path -LiteralPath $link -PathType Leaf)) {
            $shell=New-Object -ComObject WScript.Shell
            $sc=$shell.CreateShortcut($link)
            if ($sc.TargetPath.StartsWith($InstallDir+'\',[StringComparison]::OrdinalIgnoreCase) -or
                ($shortcut -eq 'Sutram Terminal.lnk' -and $sc.Arguments.Contains($InstallDir))) {
                Remove-Item -LiteralPath $link -Force
            }
        }
    }
    try { if ((Test-Path -LiteralPath $startMenu -PathType Container) -and -not (Get-ChildItem -LiteralPath $startMenu -Force -ErrorAction Stop | Select-Object -First 1)) { Remove-Item -LiteralPath $startMenu -Force } } catch {}
    $desktopOwned = (($state.ContainsKey('DesktopOwned') -and $state['DesktopOwned'] -eq '1') -or ($state.ContainsKey('DesktopShortcut') -and $state['DesktopShortcut'] -eq '1'))
    $desktopLink=Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'Sutram IDE.lnk'
    if ($desktopOwned -and (Test-Path -LiteralPath $desktopLink -PathType Leaf)) {
        $shell=New-Object -ComObject WScript.Shell
        if ($shell.CreateShortcut($desktopLink).TargetPath -eq (Join-Path $InstallDir 'sutram-ide-gui.exe')) {
            Remove-Item -LiteralPath $desktopLink -Force
        }
    }

    $classKey='HKCU:\Software\Classes\Sutram.Source'
    $extKey='HKCU:\Software\Classes\.sm'
    $commandKey=Join-Path $classKey 'shell\open\command'
    $expectedCommand='"'+(Join-Path $InstallDir 'sutram-ide-gui.exe')+'" "%1"'
    if ((Test-Path -LiteralPath $commandKey) -and (Get-Item -LiteralPath $commandKey).GetValue('') -eq $expectedCommand) {
        Remove-Item -LiteralPath $classKey -Recurse -Force
        if ($state.ContainsKey('AssociationOwned') -and $state['AssociationOwned'] -eq '1' -and
            (Test-Path -LiteralPath $extKey) -and (Get-Item -LiteralPath $extKey).GetValue('') -eq 'Sutram.Source') {
            $ext=[Microsoft.Win32.Registry]::CurrentUser.OpenSubKey('Software\Classes\.sm',$true)
            try { $ext.DeleteValue('', $false) } finally { $ext.Dispose() }
        }
        Remove-ItemProperty -LiteralPath (Join-Path $extKey 'OpenWithProgids') -Name 'Sutram.Source' -ErrorAction SilentlyContinue
    }
    $unKey='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram'
    $registered=Get-ItemProperty -LiteralPath $unKey -ErrorAction SilentlyContinue
    if ($registered -and $registered.InstallLocation -eq $InstallDir) {
        Remove-Item -LiteralPath $unKey -Recurse -Force
    }
    Remove-ManifestFiles $InstallDir (Join-Path $InstallDir 'payload.manifest.sha256')
    Remove-Item -LiteralPath (Join-Path $InstallDir 'payload.manifest.sha256') -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $InstallDir 'install-state.ini') -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $InstallDir '.sutram-install') -Force -ErrorAction SilentlyContinue

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
    if (-not $removed) { throw 'Uninstaller is still in use; close it and retry removal.' }
    $installLog=Join-Path $InstallDir 'install.log'
    if ($state.ContainsKey('InstallLogSHA256') -and (Test-Path -LiteralPath $installLog -PathType Leaf) -and
        (Get-FileHash -LiteralPath $installLog -Algorithm SHA256).Hash -eq $state['InstallLogSHA256']) {
        Remove-Item -LiteralPath $installLog -Force
    }
    if (-not (Get-ChildItem -LiteralPath $InstallDir -Force | Select-Object -First 1)) {
        Remove-Item -LiteralPath $InstallDir -Force
    }
    Log 'Uninstall completed; user-created and user-modified files were preserved.'

    exit 0
} catch { try{Log('ERROR: '+$_.Exception.Message)}catch{}; exit 1 }
