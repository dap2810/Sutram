param(
    [string]$NasmPath = "",
    [string]$LinkerPath = "",
    [switch]$SkipSmokeTests,
    [switch]$SkipIntegrityCheck
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version 2.0
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Build = Join-Path $Root "build"

function Resolve-ExistingFile([string[]]$Candidates) {
    foreach ($c in $Candidates) {
        if ($c -and (Test-Path -LiteralPath $c -PathType Leaf)) {
            return (Resolve-Path -LiteralPath $c).Path
        }
    }
    return $null
}

function Find-CommandPath([string[]]$Names) {
    foreach ($n in $Names) {
        $cmd = Get-Command $n -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    return $null
}

function Find-Nasm {
    if ($NasmPath) {
        $p = Resolve-ExistingFile @($NasmPath)
        if (-not $p) { throw "NASM was not found at: $NasmPath" }
        return $p
    }
    $p = Find-CommandPath @("nasm.exe", "nasm")
    if ($p) { return $p }
    $candidates = @(
        "C:\mingw64\bin\nasm.exe",
        "C:\msys64\ucrt64\bin\nasm.exe",
        "C:\msys64\mingw64\bin\nasm.exe",
        (Join-Path $env:ProgramFiles "NASM\nasm.exe"),
        (Join-Path $env:USERPROFILE "scoop\apps\nasm\current\nasm.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\NASM\nasm.exe")
    )
    if (${env:ProgramFiles(x86)}) {
        $candidates += (Join-Path ${env:ProgramFiles(x86)} "NASM\nasm.exe")
    }
    return Resolve-ExistingFile $candidates
}

function Find-MinGwGcc {
    $p = Find-CommandPath @("x86_64-w64-mingw32-gcc.exe", "gcc.exe")
    if ($p -and $p -match "(?i)(mingw|msys|ucrt)") { return $p }
    return Resolve-ExistingFile @(
        "C:\msys64\ucrt64\bin\x86_64-w64-mingw32-gcc.exe",
        "C:\msys64\ucrt64\bin\gcc.exe",
        "C:\msys64\mingw64\bin\x86_64-w64-mingw32-gcc.exe",
        "C:\msys64\mingw64\bin\gcc.exe",
        "C:\mingw64\bin\x86_64-w64-mingw32-gcc.exe",
        "C:\mingw64\bin\gcc.exe"
    )
}

function Find-LldLink {
    $p = Find-CommandPath @("lld-link.exe", "lld-link")
    if ($p) { return $p }
    $candidates = @(
        (Join-Path $env:ProgramFiles "LLVM\bin\lld-link.exe"),
        (Join-Path $env:USERPROFILE "scoop\apps\llvm\current\bin\lld-link.exe")
    )
    if (${env:ProgramFiles(x86)}) {
        $candidates += (Join-Path ${env:ProgramFiles(x86)} "LLVM\bin\lld-link.exe")
    }
    return Resolve-ExistingFile $candidates
}

function Find-VsWhere {
    $p = Find-CommandPath @("vswhere.exe")
    if ($p) { return $p }
    $candidates = @((Join-Path $env:ProgramFiles "Microsoft Visual Studio\Installer\vswhere.exe"))
    if (${env:ProgramFiles(x86)}) {
        $candidates += (Join-Path ${env:ProgramFiles(x86)} "Microsoft Visual Studio\Installer\vswhere.exe")
    }
    return Resolve-ExistingFile $candidates
}

function Get-MsvcLinkFromInstall([string]$InstallRoot) {
    if (-not $InstallRoot -or -not (Test-Path -LiteralPath $InstallRoot -PathType Container)) { return $null }
    $msvcRoot = Join-Path $InstallRoot "VC\Tools\MSVC"
    if (-not (Test-Path -LiteralPath $msvcRoot -PathType Container)) { return $null }
    $versions = Get-ChildItem -LiteralPath $msvcRoot -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
    foreach ($v in $versions) {
        foreach ($relative in @("bin\Hostx64\x64\link.exe", "bin\Hostx86\x64\link.exe")) {
            $candidate = Join-Path $v.FullName $relative
            if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
        }
    }
    return $null
}

function Find-MsvcLink {
    $cmd = Get-Command link.exe -ErrorAction SilentlyContinue
    if ($cmd -and $cmd.Source -match "(?i)\\Microsoft Visual Studio\\|\\VC\\Tools\\MSVC\\") { return $cmd.Source }
    $vswhere = Find-VsWhere
    if ($vswhere) {
        $installs = & $vswhere -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2>$null
        foreach ($install in @($installs)) {
            if ($install) {
                $p = Get-MsvcLinkFromInstall $install.Trim()
                if ($p) { return $p }
            }
        }
    }
    return $null
}

function Find-WindowsSdkLib([string]$FileName) {
    $roots = @()
    if (${env:ProgramFiles(x86)}) { $roots += (Join-Path ${env:ProgramFiles(x86)} "Windows Kits\10\Lib") }
    $roots += (Join-Path $env:ProgramFiles "Windows Kits\10\Lib")
    foreach ($root in $roots) {
        if (Test-Path -LiteralPath $root -PathType Container) {
            $versions = Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
            foreach ($v in $versions) {
                $candidate = Join-Path $v.FullName ("um\x64\" + $FileName)
                if (Test-Path -LiteralPath $candidate -PathType Leaf) { return $candidate }
            }
        }
    }
    return $null
}

function Assert-AsmQuotes([string]$Text,[string]$Path) {
    $lineNo = 0
    foreach ($line in ($Text -split "`n")) {
        $lineNo++
        $inSingle = $false
        $inDouble = $false
        for ($i = 0; $i -lt $line.Length; $i++) {
            $ch = $line[$i]
            if (-not $inSingle -and -not $inDouble -and $ch -eq ';') { break }
            if (-not $inDouble -and $ch -eq "'") { $inSingle = -not $inSingle; continue }
            if (-not $inSingle -and $ch -eq '"') { $inDouble = -not $inDouble; continue }
        }
        if ($inSingle -or $inDouble) { throw "Unterminated assembly string/character literal at ${Path}:$lineNo" }
    }
}

function Assert-SourceSanity([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing source: $Path" }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    foreach ($b in $bytes) { if ($b -gt 127) { throw "Windows compiler source must be ASCII-stable for Windows PowerShell/NASM portability: $Path" } }
    $text = [System.Text.Encoding]::ASCII.GetString($bytes)
    Assert-AsmQuotes $text $Path

    $lineCount = ($text -split "`n").Count
    if ($lineCount -lt 9000) { throw "Windows compiler source looks truncated ($lineCount lines): $Path" }
    if ($text -notmatch "global\s+sutram_main") { throw "Windows compiler source is missing global sutram_main." }
    if ($text -notmatch "extern\s+win_syscall") { throw "Windows compiler source is missing extern win_syscall." }
    if ($text -notmatch "build_exe_lang_path") { throw "Windows compiler source is missing the installed language-pack path resolver." }
    if ($text -match "(?m)^\s*syscall\s*(?:;.*)?$") { throw "A compiler-host Linux syscall instruction remains in the Windows source." }
}

function Assert-HostSanity([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Missing Windows host source: $Path" }
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    foreach ($b in $bytes) { if ($b -gt 127) { throw "Windows host source must be ASCII-stable: $Path" } }
    $text = [System.Text.Encoding]::ASCII.GetString($bytes)
    Assert-AsmQuotes $text $Path
    foreach ($required in @('CommandLineToArgvW','CreateFileW','MultiByteToWideChar','WideCharToMultiByte','GetModuleFileNameW')) {
        if ($text -notmatch [regex]::Escape($required)) { throw "Windows host source is missing required Unicode API: $required" }
    }
}

function Assert-Pe64([string]$Path) {
    $bytes = [System.IO.File]::ReadAllBytes($Path)
    if ($bytes.Length -lt 0x200) { throw "Output is too small to be a valid Windows executable: $Path" }
    if ($bytes[0] -ne 0x4D -or $bytes[1] -ne 0x5A) { throw "Output is not a Windows PE executable (missing MZ header)." }
    $peOff = [BitConverter]::ToInt32($bytes, 0x3C)
    if ($peOff -lt 0 -or ($peOff + 0x100) -ge $bytes.Length) { throw "Invalid PE header offset in $Path" }
    if ($bytes[$peOff] -ne 0x50 -or $bytes[$peOff+1] -ne 0x45 -or $bytes[$peOff+2] -ne 0 -or $bytes[$peOff+3] -ne 0) { throw "Output is not a valid PE executable." }
    $machine = [BitConverter]::ToUInt16($bytes, $peOff + 4)
    if ($machine -ne 0x8664) { throw ("Expected x64 PE machine 0x8664, got 0x{0:X4}" -f $machine) }
    $opt = $peOff + 24
    $optionalMagic = [BitConverter]::ToUInt16($bytes, $opt)
    if ($optionalMagic -ne 0x20B) { throw ("Expected PE32+ optional header 0x20B, got 0x{0:X4}" -f $optionalMagic) }
    $subsystem = [BitConverter]::ToUInt16($bytes, $opt + 68)
    if ($subsystem -ne 3) { throw ("Expected Windows console subsystem 3, got {0}" -f $subsystem) }
    $importRva = [BitConverter]::ToUInt32($bytes, $opt + 120)
    if ($importRva -eq 0) { throw "PE import directory is empty; WinAPI imports were not linked correctly." }
}

function Run-SmokeTests([string]$ExePath) {
    Write-Host "Running native Windows smoke tests..." -ForegroundColor Cyan

    # Make the suite deterministic. A user's SUTRAM_LANG must not change the
    # expected English diagnostics or cause an unrelated local language pack to
    # affect build validation. Restore the user's environment exactly afterward.
    $hadUserLang = Test-Path Env:\SUTRAM_LANG
    $savedUserLang = $null
    if ($hadUserLang) { $savedUserLang = $env:SUTRAM_LANG }
    Remove-Item Env:\SUTRAM_LANG -ErrorAction SilentlyContinue

    try {
        $version = (& $ExePath --version 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0) { throw "sutram.exe --version failed with exit code $LASTEXITCODE.`n$version" }
        if ($version -notmatch "Sutram 1\.0") { throw "Unexpected --version output:`n$version" }

        $help = (& $ExePath --help 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0) { throw "sutram.exe --help failed with exit code $LASTEXITCODE.`n$help" }
        if ($help -notmatch "Usage:") { throw "Unexpected --help output:`n$help" }

        $shell = (& $ExePath -i 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0 -or $shell -notmatch "not enabled") { throw "Disabled-REPL safety check failed.`n$shell" }

        # Quoted executable path with spaces.
        $spaceDir = Join-Path $Build "path with spaces"
        New-Item -ItemType Directory -Force -Path $spaceDir | Out-Null
        $spaceExe = Join-Path $spaceDir "sutram.exe"
        Copy-Item -LiteralPath $ExePath -Destination $spaceExe -Force
        $quoted = (& $spaceExe -v 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0 -or $quoted -notmatch "Sutram 1\.0") { throw "Quoted-path launch smoke test failed.`n$quoted" }

        # Unicode directory path. Construct the name from code points so this PS1
        # remains pure ASCII and parses identically in Windows PowerShell 5.1.
        $unicodeLeaf = -join @([char]0x092A,[char]0x0925,[char]0x0020,[char]0x0A97,[char]0x0AC1)
        $unicodeDir = Join-Path $Build $unicodeLeaf
        New-Item -ItemType Directory -Force -Path $unicodeDir | Out-Null
        $unicodeExe = Join-Path $unicodeDir "sutram.exe"
        Copy-Item -LiteralPath $ExePath -Destination $unicodeExe -Force
        $unicodeVersion = (& $unicodeExe --version 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0 -or $unicodeVersion -notmatch "Sutram 1\.0") { throw "Unicode executable-path smoke test failed.`n$unicodeVersion" }

        # Full compiler-host path: read, parse, generate, create/write/close output.
        $hello = Join-Path $Root "examples\01_hello.sm"
        $smokeOut = Join-Path $Build "smoke-hello.bin"
        Remove-Item -LiteralPath $smokeOut -Force -ErrorAction SilentlyContinue
        $compile = (& $ExePath $hello $smokeOut 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0) { throw "Compiler smoke test failed with exit code $LASTEXITCODE.`n$compile" }
        if (-not (Test-Path -LiteralPath $smokeOut -PathType Leaf)) { throw "Compiler smoke test did not create output." }
        $b = [System.IO.File]::ReadAllBytes($smokeOut)
        if ($b.Length -lt 4 -or $b[0] -ne 0x7F -or $b[1] -ne 0x45 -or $b[2] -ne 0x4C -or $b[3] -ne 0x46) {
            throw "Transitional generated output is not the expected ELF binary. This test intentionally verifies the current backend honestly."
        }

        # Compile with both source and output under a Unicode path. This exercises
        # CreateFileW and UTF-8/UTF-16 path conversion, not only process startup.
        $unicodeSource = Join-Path $unicodeDir "hello.sm"
        $unicodeOut = Join-Path $unicodeDir "hello-output.bin"
        Copy-Item -LiteralPath $hello -Destination $unicodeSource -Force
        Remove-Item -LiteralPath $unicodeOut -Force -ErrorAction SilentlyContinue
        $unicodeCompile = (& $unicodeExe $unicodeSource $unicodeOut 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0 -or -not (Test-Path -LiteralPath $unicodeOut -PathType Leaf)) { throw "Unicode source/output path smoke test failed.`n$unicodeCompile" }

        # Installed language-pack lookup path: emulate final layout bin + lang.
        $layout = Join-Path $Build "installed-layout"
        $layoutBin = Join-Path $layout "bin"
        $layoutLang = Join-Path $layout "lang"
        Remove-Item -LiteralPath $layout -Recurse -Force -ErrorAction SilentlyContinue
        New-Item -ItemType Directory -Force -Path $layoutBin,$layoutLang | Out-Null
        $layoutExe = Join-Path $layoutBin "sutram.exe"
        Copy-Item -LiteralPath $ExePath -Destination $layoutExe -Force
        Copy-Item -LiteralPath (Join-Path $Root "lang\gujarati.lang") -Destination (Join-Path $layoutLang "gujarati.lang") -Force
        $langOut = Join-Path $layout "gujarati-smoke.bin"
        $nativeExample = Join-Path $Root "examples\37_native_gujarati.sm"
        $langResult = (& $layoutExe --lang gujarati $nativeExample $langOut 2>&1 | Out-String)
        if ($LASTEXITCODE -ne 0) { throw "Language-pack smoke test failed with exit code $LASTEXITCODE.`n$langResult" }
        if ($langResult -notmatch "Language pack loaded: gujarati") { throw "Installed-layout language pack was not found.`n$langResult" }
        if (-not (Test-Path -LiteralPath $langOut -PathType Leaf)) { throw "Language-pack smoke test did not create output." }

        # Environment-vector compatibility: SUTRAM_LANG must survive the Win64 host.
        $envOut = Join-Path $layout "env-lang-smoke.bin"
        try {
            $env:SUTRAM_LANG = 'gujarati'
            $envResult = (& $layoutExe $nativeExample $envOut 2>&1 | Out-String)
            $envExit = $LASTEXITCODE
        } finally {
            Remove-Item Env:\SUTRAM_LANG -ErrorAction SilentlyContinue
        }
        if ($envExit -ne 0) { throw "SUTRAM_LANG environment smoke test failed with exit code $envExit.`n$envResult" }
        if ($envResult -notmatch "Language pack loaded: gujarati") { throw "SUTRAM_LANG was not preserved by the Windows host.`n$envResult" }
        if (-not (Test-Path -LiteralPath $envOut -PathType Leaf)) { throw "SUTRAM_LANG smoke test did not create output." }

        # Negative I/O path: a missing source file must fail cleanly, emit a
        # readable diagnostic, and must not create an output file.
        $missingSource = Join-Path $Build ('missing-' + [guid]::NewGuid().ToString('N') + '.sm')
        $missingOut = Join-Path $Build "missing-source.bin"
        Remove-Item -LiteralPath $missingOut -Force -ErrorAction SilentlyContinue
        $missingResult = (& $ExePath $missingSource $missingOut 2>&1 | Out-String)
        $missingExit = $LASTEXITCODE
        if ($missingExit -eq 0) { throw "Missing-source smoke test unexpectedly succeeded.`n$missingResult" }
        if (Test-Path -LiteralPath $missingOut -PathType Leaf) { throw "Missing-source smoke test created an output file unexpectedly." }
        if ([string]::IsNullOrWhiteSpace($missingResult)) { throw "Missing-source smoke test failed without emitting a diagnostic." }
        if ($missingResult -notmatch '(?i)(error|cannot open|input file)') { throw "Missing-source smoke test emitted an unexpected diagnostic.`n$missingResult" }

        # Controlled parser error. Use one valid identifier token where the
        # grammar requires the top-level keyword 'mukhya'. This reaches the
        # parser's normal error path without relying on a deeply malformed AST.
        $badSource = Join-Path $Build "intentional-parse-error.sm"
        $badOut = Join-Path $Build "intentional-parse-error.bin"
        [IO.File]::WriteAllText($badSource,"not_a_valid_top_level_token`r`n",(New-Object Text.UTF8Encoding($false)))
        Remove-Item -LiteralPath $badOut -Force -ErrorAction SilentlyContinue
        $badResult = (& $ExePath $badSource $badOut 2>&1 | Out-String)
        $badExit = $LASTEXITCODE
        if ($badExit -eq 0) { throw "Intentional parser-error smoke test unexpectedly succeeded.`n$badResult" }
        if (Test-Path -LiteralPath $badOut -PathType Leaf) { throw "Intentional parser-error smoke test created an output file unexpectedly." }
        if ([string]::IsNullOrWhiteSpace($badResult)) { throw "Intentional parser-error smoke test failed without emitting a diagnostic." }
        if ($badResult -notmatch '(?i)(Sutram Error|parse error|Hint:)') { throw "Intentional parser-error smoke test emitted an unexpected diagnostic.`n$badResult" }

        # Regression for the v6 failure: an invalid delimiter inside an if
        # expression used to fall back into .pp_paren recursively and could
        # terminate without a diagnostic. It must now reach parse_error cleanly.
        $nestedBadSource = Join-Path $Build "intentional-nested-parse-error.sm"
        $nestedBadOut = Join-Path $Build "intentional-nested-parse-error.bin"
        [IO.File]::WriteAllText($nestedBadSource,"mukhya() { yadi ( }`r`n",(New-Object Text.UTF8Encoding($false)))
        Remove-Item -LiteralPath $nestedBadOut -Force -ErrorAction SilentlyContinue
        $nestedBadResult = (& $ExePath $nestedBadSource $nestedBadOut 2>&1 | Out-String)
        $nestedBadExit = $LASTEXITCODE
        if ($nestedBadExit -eq 0) { throw "Nested parser-error regression test unexpectedly succeeded.`n$nestedBadResult" }
        if (Test-Path -LiteralPath $nestedBadOut -PathType Leaf) { throw "Nested parser-error regression test created an output file unexpectedly." }
        if ([string]::IsNullOrWhiteSpace($nestedBadResult)) { throw "Nested parser-error regression test failed without emitting a diagnostic. The invalid-primary recursion bug may have returned." }
        if ($nestedBadResult -notmatch '(?i)(Sutram Error|parse error|Hint:)') { throw "Nested parser-error regression test emitted an unexpected diagnostic.`n$nestedBadResult" }

        Write-Host "Smoke tests passed: startup, help/version, disabled REPL, spaces, Unicode paths, compile I/O, language packs, environment, missing-file errors, simple parser errors, and nested parser-error regression." -ForegroundColor Green
    } finally {
        Remove-Item Env:\SUTRAM_LANG -ErrorAction SilentlyContinue
        if ($hadUserLang) { $env:SUTRAM_LANG = $savedUserLang }
    }
}

$CompilerSource = Join-Path $Root "src\sutram_compiler_win.asm"
$HostSource = Join-Path $Root "win\native_host.asm"
Assert-SourceSanity $CompilerSource
Assert-HostSanity $HostSource

if (-not $SkipIntegrityCheck) {
    $integrityFile = Join-Path $Root "windows-build-integrity.sha256"
    if (-not (Test-Path -LiteralPath $integrityFile -PathType Leaf)) {
        throw "Source integrity manifest is missing: windows-build-integrity.sha256"
    }
    $rootFull = [IO.Path]::GetFullPath($Root).TrimEnd('\')
    $integrityCount = 0
    foreach ($line in Get-Content -LiteralPath $integrityFile) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        # Standard sha256sum binary-mode format is: 64hex + space + *relative-path.
        # Keep this parser identical to preflight-windows.ps1 so stage 0 and stage 1
        # cannot disagree about the leading '*' marker again.
        if ($line -notmatch '^([0-9a-fA-F]{64}) \*(.+)$') {
            throw "Invalid source integrity manifest line: $line"
        }
        $expected = $Matches[1].ToLowerInvariant()
        $relativePath = $Matches[2]
        if ([string]::IsNullOrWhiteSpace($relativePath)) { throw "Integrity manifest contains an empty path." }
        $file = [IO.Path]::GetFullPath((Join-Path $rootFull $relativePath))
        if (-not $file.StartsWith($rootFull + '\',[StringComparison]::OrdinalIgnoreCase)) {
            throw "Unsafe source integrity path: $relativePath"
        }
        if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
            throw "Integrity file is missing: $relativePath"
        }
        $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $file).Hash.ToLowerInvariant()
        if ($actual -ne $expected) {
            throw "Integrity check failed for $relativePath. Re-extract a fresh package or use -SkipIntegrityCheck only if you intentionally edited the source."
        }
        $integrityCount++
    }
    if ($integrityCount -eq 0) { throw "Source integrity manifest contains no file entries." }
    Write-Host ("Source integrity re-check: PASS ({0} files)" -f $integrityCount) -ForegroundColor Green
}

$Nasm = Find-Nasm
if (-not $Nasm) { throw "NASM was not found. NASM is needed only to build Sutram itself." }

$Linker = $null
$LinkerKind = $null
if ($LinkerPath) {
    $Linker = Resolve-ExistingFile @($LinkerPath)
    if (-not $Linker) { throw "Linker was not found at: $LinkerPath" }
    $name = [IO.Path]::GetFileName($Linker)
    if ($name -match "(?i)gcc") { $LinkerKind = "MinGW GCC" }
    elseif ($name -match "(?i)lld-link") { $LinkerKind = "lld-link" }
    elseif ($name -match "(?i)^link\.exe$") { $LinkerKind = "MSVC link.exe" }
    else { throw "Unsupported linker path: $Linker" }
} else {
    $Linker = Find-MinGwGcc
    if ($Linker) { $LinkerKind = "MinGW GCC" }
    if (-not $Linker) { $Linker = Find-LldLink; if ($Linker) { $LinkerKind = "lld-link" } }
    if (-not $Linker) { $Linker = Find-MsvcLink; if ($Linker) { $LinkerKind = "MSVC link.exe" } }
}
if (-not $Linker) {
    throw "No supported x64 Windows linker was found. Supported: MinGW GCC, LLVM lld-link, or Visual Studio link.exe."
}

$Kernel32Lib = $null
$Shell32Lib = $null
if ($LinkerKind -ne "MinGW GCC") {
    $Kernel32Lib = Find-WindowsSdkLib "kernel32.lib"
    $Shell32Lib = Find-WindowsSdkLib "shell32.lib"
    if (-not $Kernel32Lib -or -not $Shell32Lib) { throw "kernel32.lib/shell32.lib were not found in the Windows SDK. Install the Windows 10/11 SDK or use MinGW GCC." }
}

Write-Host "NASM   : $Nasm" -ForegroundColor Green
Write-Host "Linker : $Linker ($LinkerKind)" -ForegroundColor Green
if ($Kernel32Lib) { Write-Host "WinAPI : $Kernel32Lib" -ForegroundColor Green; Write-Host "         $Shell32Lib" -ForegroundColor Green }

New-Item -ItemType Directory -Force -Path $Build | Out-Null
$CompilerObj = Join-Path $Build "sutram_compiler_win.obj"
$HostObj = Join-Path $Build "native_host.obj"
$Exe = Join-Path $Build "sutram.exe"
Remove-Item -LiteralPath $CompilerObj,$HostObj,$Exe -Force -ErrorAction SilentlyContinue

Write-Host "Assembling Sutram compiler..."
& $Nasm -f win64 $CompilerSource -o $CompilerObj
if ($LASTEXITCODE -ne 0) { throw "NASM failed while assembling src\sutram_compiler_win.asm (exit $LASTEXITCODE)." }

Write-Host "Assembling Windows host layer..."
& $Nasm -f win64 $HostSource -o $HostObj
if ($LASTEXITCODE -ne 0) { throw "NASM failed while assembling win\native_host.asm (exit $LASTEXITCODE)." }

Write-Host "Linking native x64 sutram.exe..."
if ($LinkerKind -eq "MinGW GCC") {
    $gccArgs = @(
        "-nostdlib",
        "-Wl,--entry,_start",
        "-Wl,--subsystem,console",
        "-Wl,--dynamicbase",
        "-Wl,--nxcompat",
        "-o", $Exe,
        $HostObj,
        $CompilerObj,
        "-lkernel32",
        "-lshell32"
    )
    & $Linker @gccArgs
} else {
    $linkArgs = @(
        "/entry:_start",
        "/subsystem:console",
        "/machine:x64",
        "/nodefaultlib",
        "/dynamicbase",
        "/nxcompat",
        "/out:$Exe",
        $HostObj,
        $CompilerObj,
        $Kernel32Lib,
        $Shell32Lib
    )
    & $Linker @linkArgs
}
if ($LASTEXITCODE -ne 0) { throw "$LinkerKind failed with exit code $LASTEXITCODE." }

Assert-Pe64 $Exe
Write-Host "Built and structurally validated PE32+ x64 compiler host:" -ForegroundColor Green
Write-Host "  $Exe"

if (-not $SkipSmokeTests) { Run-SmokeTests $Exe }

Write-Host "" 
Write-Host "Native compiler-host build passed." -ForegroundColor Green
Write-Host "NOTE: generated Sutram programs are still on the transitional ELF backend; the PE generated-program backend remains a separate unfinished stage." -ForegroundColor Yellow
