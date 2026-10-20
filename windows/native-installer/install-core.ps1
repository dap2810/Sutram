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
Set-StrictMode -Version 2.0

function Log([string]$Message) {
    $stamp = [DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')
    Add-Content -LiteralPath $LogPath -Value ("[{0}] {1}" -f $stamp,$Message) -Encoding UTF8
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

# R77: a display-availability check only. This does NOT install fonts or keymaps.
# R79: verify representative native-script glyphs, not merely a font family name.
# Nine distinct writing scripts serve Sutram's eleven packs; English is NOT a pack.
# Read-only: no redistribution of Microsoft's fonts, no elevated installs, no network.
function Check-R79IndicFonts([bool]$ShowWarning) {
    try {
        Add-Type -AssemblyName System.Drawing -ErrorAction Stop
        if (-not ('SutramIndicFontProbe' -as [type])) {
            Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class SutramIndicFontProbe {
    [DllImport("gdi32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    private static extern IntPtr CreateFontW(int h,int w,int esc,int orient,int weight,
        uint italic,uint underline,uint strike,uint charset,uint outPrecision,
        uint clipPrecision,uint quality,uint pitchFamily,string face);
    [DllImport("gdi32.dll", SetLastError=true)]
    private static extern IntPtr CreateCompatibleDC(IntPtr source);
    [DllImport("gdi32.dll", SetLastError=true)]
    private static extern IntPtr SelectObject(IntPtr dc,IntPtr obj);
    [DllImport("gdi32.dll", SetLastError=true)]
    private static extern bool DeleteObject(IntPtr obj);
    [DllImport("gdi32.dll", SetLastError=true)]
    private static extern bool DeleteDC(IntPtr dc);
    [DllImport("gdi32.dll", CharSet=CharSet.Unicode, SetLastError=true)]
    private static extern uint GetGlyphIndicesW(IntPtr dc,string text,int length,
        [Out] ushort[] glyphs,uint flags);
    public static bool HasGlyph(string family,int codepoint) {
        IntPtr dc=IntPtr.Zero, font=IntPtr.Zero, prior=IntPtr.Zero;
        try {
            dc=CreateCompatibleDC(IntPtr.Zero);
            if(dc==IntPtr.Zero) throw new InvalidOperationException("CreateCompatibleDC failed");
            font=CreateFontW(-20,0,0,0,400,0,0,0,1,0,0,0,0,family);
            if(font==IntPtr.Zero) throw new InvalidOperationException("CreateFontW failed");
            prior=SelectObject(dc,font);
            if(prior==IntPtr.Zero || prior==new IntPtr(-1))
                throw new InvalidOperationException("SelectObject failed");
            string text=Char.ConvertFromUtf32(codepoint);
            ushort[] glyphs=new ushort[text.Length];
            uint count=GetGlyphIndicesW(dc,text,text.Length,glyphs,1);
            if(count==0xffffffffu) throw new InvalidOperationException("GetGlyphIndicesW failed");
            for(int i=0;i<glyphs.Length;i++) if(glyphs[i]==0xffff) return false;
            return true;
        } finally {
            if(prior!=IntPtr.Zero && prior!=new IntPtr(-1)) SelectObject(dc,prior);
            if(font!=IntPtr.Zero) DeleteObject(font);
            if(dc!=IntPtr.Zero) DeleteDC(dc);
        }
    }
}
'@ -ErrorAction Stop
        }
        $collection=New-Object System.Drawing.Text.InstalledFontCollection
        $available=@{}  # Windows PowerShell hashtables compare keys case-insensitively.
        foreach ($family in $collection.Families) { $available[$family.Name]=$true }
        # One representative native consonant for each DISTINCT script.
        # A glyph probe is a renderability check, not a full shaping/font quality test.
        $scripts=@(
            @{ Script='Devanagari'; Packs='sanskrit,hindi,marathi'; Code=0x0915; Faces=@('Nirmala UI','Mangal','Noto Sans Devanagari') },
            @{ Script='Gujarati'; Packs='gujarati'; Code=0x0A95; Faces=@('Nirmala UI','Shruti','Noto Sans Gujarati') },
            @{ Script='Bengali'; Packs='bengali'; Code=0x0995; Faces=@('Nirmala UI','Vrinda','Noto Sans Bengali') },
            @{ Script='Gurmukhi'; Packs='punjabi'; Code=0x0A15; Faces=@('Nirmala UI','Raavi','Noto Sans Gurmukhi') },
            @{ Script='Odia'; Packs='odia'; Code=0x0B15; Faces=@('Nirmala UI','Kalinga','Noto Sans Oriya') },
            @{ Script='Tamil'; Packs='tamil'; Code=0x0B95; Faces=@('Nirmala UI','Latha','Noto Sans Tamil') },
            @{ Script='Telugu'; Packs='telugu'; Code=0x0C15; Faces=@('Nirmala UI','Gautami','Noto Sans Telugu') },
            @{ Script='Kannada'; Packs='kannada'; Code=0x0C95; Faces=@('Nirmala UI','Tunga','Noto Sans Kannada') },
            @{ Script='Malayalam'; Packs='malayalam'; Code=0x0D15; Faces=@('Nirmala UI','Kartika','Noto Sans Malayalam') }
        )
        $missing=New-Object 'System.Collections.Generic.List[string]'
        $found=New-Object 'System.Collections.Generic.List[string]'
        foreach ($entry in $scripts) {
            $chosen=''
            foreach ($family in $entry.Faces) {
                if (-not $available.ContainsKey($family)) { continue }
                if ([SutramIndicFontProbe]::HasGlyph($family,[int]$entry.Code)) {
                    $chosen=$family
                    break
                }
            }
            if ($chosen) {
                $found.Add(($entry.Script+' ('+$entry.Packs+'): '+$chosen))
                Log ('R79 FONT FOUND: '+$entry.Script+' packs='+$entry.Packs+' font='+$chosen)
            } else {
                $missing.Add(($entry.Script+' ('+$entry.Packs+')'))
                Log ('R79 FONT MISSING: '+$entry.Script+' packs='+$entry.Packs)
            }
        }
        Log ('R79 FONT SUMMARY: scripts found='+$found.Count+' missing='+$missing.Count+
             ' installed_by_setup=0; Microsoft font files are never bundled or downloaded.')
        if ($missing.Count -gt 0) {
            $message=('Sutram cannot display all language scripts yet. Missing script coverage: '+
                [string]::Join(', ',$missing.ToArray())+'. '+
                'Open Windows Settings > Time & language > Language & region > Add a language; '+
                'install the corresponding Windows language/font feature, then restart Sutram Setup. '+
                'The installer cannot safely download or enable missing optional fonts without '+
                'additional Windows permissions. No third-party or Microsoft font files were bundled.')
            Log ('WARNING: '+$message)
            if ($ShowWarning) {
                Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
                [void][System.Windows.Forms.MessageBox]::Show($message,'Sutram script font coverage',
                    [System.Windows.Forms.MessageBoxButtons]::OK,
                    [System.Windows.Forms.MessageBoxIcon]::Warning)
            }
        }
    } catch {
        # A failed probe is UNKNOWN, never silently mistaken for complete coverage.
        $msg='Sutram could not verify Indic script fonts: '+$_.Exception.Message+
             '. Open Windows Settings > Time & language > Language & region and enable your script fonts.'
        Log ('WARNING: '+$msg)
        if ($ShowWarning) {
            try {
                Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
                [void][System.Windows.Forms.MessageBox]::Show($msg,'Sutram font verification',
                    [System.Windows.Forms.MessageBoxButtons]::OK,
                    [System.Windows.Forms.MessageBoxIcon]::Warning)
            } catch { Log ('Font warning dialog unavailable: '+$_.Exception.Message) }
        }
    }
}

# R77: conservative rollback for an attempted FRESH installation only.
# Never recurse-delete a user-chosen directory; remove exact staged paths,
# preserve unknown paths, refuse reparse points, and remove empty directories.
$script:r77FreshInstall=$false
$script:r77InstallTouched=$false
$script:r77HadInstallDir=$true
$script:r77OwnedRelatives=@()
$script:r77UninstallKeyWasPresent=$true
$script:r77ClassKeyWasPresent=$true
$script:r77ExtKeyWasPresent=$true
$script:r77AddedPath=$false
function Undo-R77FailedFreshInstall {
    if (-not $script:r77FreshInstall -or -not $script:r77InstallTouched) { return }
    $dest=[IO.Path]::GetFullPath($InstallDir).TrimEnd('\')
    $programs=[IO.Path]::GetFullPath((Join-Path $env:LOCALAPPDATA 'Programs')).TrimEnd('\')
    if (-not $dest.StartsWith($programs+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Rollback refused outside user Programs.' }
    Assert-NoReparsePath $dest
    if (-not (Test-Path -LiteralPath $dest -PathType Container)) { return }
    foreach ($relative in $script:r77OwnedRelatives) {
        $target=[IO.Path]::GetFullPath((Join-Path $dest $relative))
        if (-not $target.StartsWith($dest+'\',[StringComparison]::OrdinalIgnoreCase)) { throw 'Rollback path escaped install root.' }
        Assert-NoReparsePath $target
        if (Test-Path -LiteralPath $target -PathType Leaf) {
            Remove-Item -LiteralPath $target -Force -ErrorAction Stop
        }
    }
    foreach ($name in @('Sutram-Uninstall.exe','.sutram-install','install-state.ini','install.log')) {
        $target=Join-Path $dest $name
        Assert-NoReparsePath $target
        if (Test-Path -LiteralPath $target -PathType Leaf) { Remove-Item -LiteralPath $target -Force -ErrorAction Stop }
    }
    if ($script:r77AddedPath) {
        [void](Set-UserPathEntry (Join-Path $dest 'bin') $false)
    }
    foreach ($encoded in $script:ownedShortcuts) {
        try {
            $shortcut=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($encoded))
            if (-not (Test-Path -LiteralPath $shortcut -PathType Leaf)) { continue }
            Assert-NoReparsePath $shortcut
            $sc=(New-Object -ComObject WScript.Shell).CreateShortcut($shortcut)
            if ($sc.TargetPath.StartsWith($dest+'\',[StringComparison]::OrdinalIgnoreCase) -or
                (($shortcut -like '*Sutram Terminal.lnk') -and $sc.Arguments.Contains($dest))) {
                Remove-Item -LiteralPath $shortcut -Force -ErrorAction Stop
            }
        } catch { Log ('Shortcut rollback preserved path: ' + $_.Exception.Message) }
    }
    # Restore only registration keys first created by this attempt.
    $unKey='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram'
    if (-not $script:r77UninstallKeyWasPresent -and (Test-Path -LiteralPath $unKey)) {
        $reg=Get-ItemProperty -LiteralPath $unKey -ErrorAction SilentlyContinue
        if ($reg -and [string]::Equals([string]$reg.InstallLocation,$dest,[StringComparison]::OrdinalIgnoreCase)) {
            Remove-Item -LiteralPath $unKey -Recurse -Force -ErrorAction Stop
        }
    }
    $classKey='HKCU:\Software\Classes\Sutram.Source'
    if (-not $script:r77ClassKeyWasPresent -and (Test-Path -LiteralPath $classKey)) {
        $commandKey=Join-Path $classKey 'shell\open\command'
        if (Test-Path -LiteralPath $commandKey) {
            $activeCommand=[string](Get-Item -LiteralPath $commandKey).GetValue('')
            if ($activeCommand -eq ('"'+(Join-Path $dest 'sutram-ide-gui.exe')+'" "%1"')) {
                Remove-Item -LiteralPath $classKey -Recurse -Force -ErrorAction Stop
            }
        }
    }
    $extKey='HKCU:\Software\Classes\.sm'
    if (-not $script:r77ExtKeyWasPresent -and (Test-Path -LiteralPath $extKey)) {
        $default=[string](Get-Item -LiteralPath $extKey).GetValue('')
        if ($default -eq 'Sutram.Source') {
            Remove-Item -LiteralPath $extKey -Recurse -Force -ErrorAction Stop
        }
    }
    $folders=Get-ChildItem -LiteralPath $dest -Directory -Recurse -ErrorAction SilentlyContinue | Sort-Object { $_.FullName.Length } -Descending
    foreach ($d in $folders) {
        try {
            Assert-NoReparsePath $d.FullName
            if (-not (Get-ChildItem -LiteralPath $d.FullName -Force -ErrorAction Stop | Select-Object -First 1)) {
                Remove-Item -LiteralPath $d.FullName -Force -ErrorAction Stop
            }
        } catch { Log ('Preserving rollback directory: '+$d.FullName) }
    }
    if (-not $script:r77HadInstallDir -and
        -not (Get-ChildItem -LiteralPath $dest -Force -ErrorAction Stop | Select-Object -First 1)) {
        Remove-Item -LiteralPath $dest -Force -ErrorAction Stop
    }
    Log 'R77 fresh-install rollback: attempted files and owned shortcuts removed; unknown files preserved.'
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

    $marker = Join-Path $InstallDir '.sutram-install'
    $script:r77HadInstallDir = (Test-Path -LiteralPath $InstallDir -PathType Container)
    $script:r77FreshInstall = -not (Test-SutramMarker $marker)
    $script:r77UninstallKeyWasPresent = (Test-Path -LiteralPath $unKey)
    $script:r77ClassKeyWasPresent = (Test-Path -LiteralPath 'HKCU:\Software\Classes\Sutram.Source')
    $script:r77ExtKeyWasPresent = (Test-Path -LiteralPath 'HKCU:\Software\Classes\.sm')
    $statePath = Join-Path $InstallDir 'install-state.ini'
    $oldState = Read-State $statePath
    if (Test-Path -LiteralPath $InstallDir -PathType Container) {
        $first = Get-ChildItem -LiteralPath $InstallDir -Force -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($first -and -not (Test-SutramMarker $marker)) { throw "The selected folder is not empty and is not an existing Sutram installation: $InstallDir" }
    }

    # Check ownership conflicts before creating or changing an installation.
    $classCommand='HKCU:\Software\Classes\Sutram.Source\shell\open\command'
    $wantedCommand='"'+(Join-Path $InstallDir 'sutram-ide-gui.exe')+'" "%1"'
    if (Test-Path -LiteralPath $classCommand) {
        $currentCommand=(Get-Item -LiteralPath $classCommand).GetValue('')
        if ($currentCommand -and $currentCommand -ne $wantedCommand) { throw 'A conflicting Sutram.Source registration exists.' }
    }
    if (Test-SutramMarker $marker) {
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
        $script:r77OwnedRelatives=@(Get-ChildItem -LiteralPath $stage -File -Recurse | ForEach-Object { $_.FullName.Substring($stage.Length+1) })
        Check-R79IndicFonts (-not $VerifyOnly)
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
        $previousManifest = Join-Path $InstallDir 'payload.manifest.sha256'
        if (Test-Path -LiteralPath $previousManifest -PathType Leaf) {
            $previousFiles=@{}
            foreach ($line in [IO.File]::ReadAllLines($previousManifest)) {
                if ($line -notmatch '^([0-9a-fA-F]{64}) \*(.+)$') { throw 'Invalid previous manifest.' }
                $previousFiles[$Matches[2]]=$Matches[1]
            }
            foreach ($file in Get-ChildItem -LiteralPath $stage -File -Recurse) {
                $relative=$file.FullName.Substring($stage.Length+1)
                if ($relative -eq 'payload.manifest.sha256') { continue }
                $target=Join-Path $InstallDir $relative
                if (Test-Path -LiteralPath $target -PathType Leaf) {
                    if (-not $previousFiles.ContainsKey($relative) -or
                        (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash -ne $previousFiles[$relative]) {
                        throw ("Upgrade would overwrite a user file; preserve it elsewhere first: " + $target)
                    }
                }
            }
        }
        foreach ($file in Get-ChildItem -LiteralPath $stage -File -Recurse) {
            Assert-NoReparsePath (Join-Path $InstallDir $file.FullName.Substring($stage.Length+1))
        }
        $script:r77InstallTouched=$true
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
        $check = Invoke-SutramSelfTest $installedExe '--version' 'post-install --version'

        $binDir = Join-Path $InstallDir 'bin'
        $previousOwned = ($oldState.ContainsKey('PathOwned') -and $oldState['PathOwned'] -eq '1')
        $pathOwned = $previousOwned
        if ($AddPath) {
            Log 'Ensuring Sutram is present in the current user PATH.'
            $pathAddedNow = [bool](Set-UserPathEntry $binDir $true)
            if ($script:r77FreshInstall -and $pathAddedNow) { $script:r77AddedPath=$true }
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
            ('OwnedShortcuts=' + ($script:ownedShortcuts.ToArray() -join ',')),
            ('PathOwned=' + $pathOwnedValue),
            ('DesktopOwned=' + $desktopOwnedValue),
            ('AssociationOwned=' + [int]$associationOwned),
            ('UninstallerSHA256=' + (Get-FileHash -LiteralPath $SetupExePath -Algorithm SHA256).Hash)
        )
        [IO.File]::WriteAllLines($statePath,$stateLines,([Text.UTF8Encoding]::new($false)))

        Log ('Installation complete: ' + $InstallDir)
        # The wizard deletes its temporary staging directory after success.
        # Preserve the actual installer log under this user's installed tree
        # so the Round 62 auditor can examine real installation events.
        Copy-Item -LiteralPath $LogPath -Destination (Join-Path $InstallDir 'install.log') -Force
        Add-Content -LiteralPath $statePath -Encoding UTF8 -Value ('InstallLogSHA256='+(Get-FileHash -LiteralPath (Join-Path $InstallDir 'install.log') -Algorithm SHA256).Hash)
    } finally {
        $stageFull=[IO.Path]::GetFullPath($stage)
        $tempFull=[IO.Path]::GetFullPath($env:TEMP).TrimEnd('\')
        if (-not $stageFull.StartsWith($tempFull+'\Sutram-Payload-',[StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe stage cleanup path.' }
        Remove-Item -LiteralPath $stageFull -Recurse -Force -ErrorAction SilentlyContinue
    }
    exit 0
} catch {
    try { Log ('ERROR: ' + $_.Exception.Message) } catch {}
    try { Undo-R77FailedFreshInstall } catch { try { Log ('R77 rollback was incomplete: '+$_.Exception.Message) } catch {} }
    exit 1
}
