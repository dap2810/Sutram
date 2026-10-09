param(
    [Parameter(Mandatory=$true)][string]$PayloadZip,
    [Parameter(Mandatory=$true)][string]$InstallDir,
    [Parameter(Mandatory=$true)][string]$SetupExePath,
    [Parameter(Mandatory=$true)][string]$LogPath,
    [switch]$AddPath,
    [switch]$DesktopShortcut
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0

function Log([string]$Message) {
    $stamp = [DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')
    Add-Content -LiteralPath $LogPath -Value ("[{0}] {1}" -f $stamp,$Message) -Encoding UTF8
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
function New-Shortcut([string]$Path,[string]$Target,[string]$Arguments,[string]$WorkingDir,[string]$Icon) {
    $shell = New-Object -ComObject WScript.Shell
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

    $marker = Join-Path $InstallDir '.sutram-install'
    $statePath = Join-Path $InstallDir 'install-state.ini'
    $oldState = Read-State $statePath
    if (Test-Path -LiteralPath $InstallDir -PathType Container) {
        $first = Get-ChildItem -LiteralPath $InstallDir -Force -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($first -and -not (Test-SutramMarker $marker)) { throw "The selected folder is not empty and is not an existing Sutram installation: $InstallDir" }
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
        $v = & $testExe --version 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($v)) { throw 'Packaged sutram.exe failed its pre-install version test.' }
        $h = & $testExe --help 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($h)) { throw 'Packaged sutram.exe failed its pre-install help test.' }

        New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
        if (Test-Path -LiteralPath (Join-Path $InstallDir 'payload.manifest.sha256') -PathType Leaf) {
            Log 'Removing files owned by the previous Sutram payload.'
            Remove-ManifestFiles $InstallDir (Join-Path $InstallDir 'payload.manifest.sha256')
        }
        Log 'Copying Sutram files.'
        Copy-Item -Path (Join-Path $stage '*') -Destination $InstallDir -Recurse -Force
        Copy-Item -LiteralPath $SetupExePath -Destination (Join-Path $InstallDir 'Sutram-Uninstall.exe') -Force
        [IO.File]::WriteAllText($marker,'Sutram Windows installation' + [Environment]::NewLine,([Text.UTF8Encoding]::new($false)))

        $installedExe = Join-Path $InstallDir 'bin\sutram.exe'
        $check = & $installedExe --version 2>&1 | Out-String
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($check)) { throw 'Installed sutram.exe failed its final validation before Windows integration.' }

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
        $desktopLink = Join-Path ([Environment]::GetFolderPath('DesktopDirectory')) 'Sutram Terminal.lnk'
        $previousDesktopOwned = (($oldState.ContainsKey('DesktopOwned') -and $oldState['DesktopOwned'] -eq '1') -or ($oldState.ContainsKey('DesktopShortcut') -and $oldState['DesktopShortcut'] -eq '1'))
        $desktopOwned = $previousDesktopOwned
        if ($DesktopShortcut) {
            if ((Test-Path -LiteralPath $desktopLink -PathType Leaf) -and -not $previousDesktopOwned) {
                Log 'A pre-existing user desktop shortcut named Sutram Terminal.lnk was preserved.'
                $desktopOwned = $false
            } else {
                New-Shortcut $desktopLink $env:ComSpec $terminalArgs $env:USERPROFILE $icon
                $desktopOwned = $true
            }
        } elseif ($previousDesktopOwned) {
            Remove-Item -LiteralPath $desktopLink -Force -ErrorAction SilentlyContinue
            $desktopOwned = $false
        } else {
            $desktopOwned = $false
        }

        New-Item -Path $unKey -Force | Out-Null
        New-ItemProperty -Path $unKey -Name DisplayName -Value 'Sutram' -PropertyType String -Force | Out-Null
        New-ItemProperty -Path $unKey -Name DisplayVersion -Value '0.1.0' -PropertyType String -Force | Out-Null
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
            'Version=0.1.0',
            ('PathOwned=' + $pathOwnedValue),
            ('DesktopOwned=' + $desktopOwnedValue)
        )
        [IO.File]::WriteAllLines($statePath,$stateLines,([Text.UTF8Encoding]::new($false)))

        Log ('Installation complete: ' + $InstallDir)
    } finally {
        Remove-Item -LiteralPath $stage -Recurse -Force -ErrorAction SilentlyContinue
    }
    exit 0
} catch {
    try { Log ('ERROR: ' + $_.Exception.Message) } catch {}
    exit 1
}
