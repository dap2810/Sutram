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
function Remove-ManifestFiles([string]$Root,[string]$Manifest) {
    if (-not (Test-Path -LiteralPath $Manifest -PathType Leaf)) { return }
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    $dirs = New-Object System.Collections.Generic.List[string]
    foreach ($line in Get-Content -LiteralPath $Manifest) {
        if ($line -notmatch '^[0-9a-fA-F]{64} \*(.+)$') { continue }
        $rel = $Matches[1]
        $target = [IO.Path]::GetFullPath((Join-Path $rootFull $rel))
        if (-not $target.StartsWith($rootFull + '\',[StringComparison]::OrdinalIgnoreCase)) { throw "Unsafe manifest path: $rel" }
        Remove-Item -LiteralPath $target -Force -ErrorAction SilentlyContinue
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
    if (-not $env:LOCALAPPDATA) { throw 'LOCALAPPDATA is unavailable for this user.' }
    $userProgramsRoot=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
    if (-not $InstallDir.StartsWith($userProgramsRoot + '\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Refusing to uninstall outside the current user Programs folder.' }
    if (-not (Test-SutramMarker (Join-Path $InstallDir '.sutram-install'))) { throw 'This folder is not marked as a valid Sutram installation.' }
    $state=Read-State (Join-Path $InstallDir 'install-state.ini')
    if($state.ContainsKey('PathOwned') -and $state['PathOwned'] -eq '1'){Remove-UserPathEntry (Join-Path $InstallDir 'bin')}
    $startMenu = Join-Path ([Environment]::GetFolderPath('StartMenu')) 'Programs\Sutram'
    foreach ($shortcut in @('Sutram IDE.lnk','Sutram Terminal.lnk','Sutram Documentation.lnk','Uninstall Sutram.lnk')) {
        Remove-Item -LiteralPath (Join-Path $startMenu $shortcut) -Force -ErrorAction SilentlyContinue
    }
    try { if ((Test-Path -LiteralPath $startMenu -PathType Container) -and -not (Get-ChildItem -LiteralPath $startMenu -Force -ErrorAction Stop | Select-Object -First 1)) { Remove-Item -LiteralPath $startMenu -Force } } catch {}
    $desktopOwned = (($state.ContainsKey('DesktopOwned') -and $state['DesktopOwned'] -eq '1') -or ($state.ContainsKey('DesktopShortcut') -and $state['DesktopShortcut'] -eq '1'))
    if ($desktopOwned) { Remove-Item -LiteralPath (Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'Sutram Terminal.lnk') -Force -ErrorAction SilentlyContinue }
    Remove-Item -LiteralPath 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram' -Recurse -Force -ErrorAction SilentlyContinue
    Remove-ManifestFiles $InstallDir (Join-Path $InstallDir 'payload.manifest.sha256')
    Remove-Item -LiteralPath (Join-Path $InstallDir 'payload.manifest.sha256') -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $InstallDir 'install-state.ini') -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $InstallDir '.sutram-install') -Force -ErrorAction SilentlyContinue
    Log 'Uninstall payload removal completed. The native uninstaller will remove only its own EXE after it exits.'
    exit 0
} catch { try{Log('ERROR: '+$_.Exception.Message)}catch{}; exit 1 }
