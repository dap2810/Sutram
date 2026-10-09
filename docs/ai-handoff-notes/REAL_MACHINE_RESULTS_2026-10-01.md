# Sutram Windows Real-Machine Results — 2026-10-01

## Environment

```text
Windows 11 build 26200
Kernel: Windows NT 10.0.26200.0
PowerShell: 5.1.26100.9444
NASM: C:\mingw64\bin\nasm.exe
MinGW GCC: C:\msys64\ucrt64\bin\x86_64-w64-mingw32-gcc.exe
```

Other detected tools during development included MSVC x64 `link.exe` and Windows SDK libraries, but v11's installer path does not require them.

## Successful v11 build

```text
[0/3] Preflight checks...
Source package integrity: PASS
Assembly sources: PASS (10084 compiler lines, ASCII-stable, quote-balanced)
Source compatibility/hardening scan: PASS
Native installer GCC/Win32-library probe: PASS
Project preflight passed.

[1/3] Building and smoke-testing native Sutram compiler host...
Source integrity re-check: PASS (103 files)
Assembling Sutram compiler...
Assembling Windows host layer...
Linking native x64 sutram.exe...
Built and structurally validated PE32+ x64 compiler host.
Smoke tests passed: startup, help/version, disabled REPL, spaces, Unicode paths,
compile I/O, language packs, environment, missing-file errors, simple parser errors,
and nested parser-error regression.
Native compiler-host build passed.

[2/3] Building native Win32 wizard setup...
Native wizard installer built and package-overlay self-test passed.
SHA256: D8EEB96A68BCE85693B268E336BBE31E58F34AE39E7A0A444E8581BFF530BD84

[3/3] Final release verification...
BUILD PASSED ALL WINDOWS RELEASE CHECKS.
BUILD PASSED.
Installer: Sutram-Setup.exe
```

One harmless warning appeared while compiling the installer:

```text
warning: 'UNICODE' redefined
```

`UNICODE` was defined both in source and on the GCC command line. The build still passed. Clean this duplicate definition in a future source cleanup, but it is not the current blocker.

## Installed compiler test

From CMD/PowerShell after PATH installation:

```cmd
sutram --version
```

Output:

```text
Sutram 1.0 (v29) Windows host preview — the complete thread
Sanskrit-keyword language -> x86-64 machine code
```

This confirms native Windows host startup and PATH integration.

## Generated-program failure reproduced and identified

A generated `hello.exe` was created in the examples directory.

Observed file metadata:

```text
Length: 210 bytes
```

PowerShell header check:

```powershell
$b = [IO.File]::ReadAllBytes((Resolve-Path .\hello.exe).Path)
'{0:X2} {1:X2} {2:X2} {3:X2}' -f $b[0],$b[1],$b[2],$b[3]
```

Result:

```text
7F 45 4C 46
```

That is ELF64 magic. Therefore the remaining problem is definitively the generated-program backend, not PATH, installer, or compiler-host execution.

Windows may show a misleading "Unsupported 16-Bit Application" dialog for this invalid/non-PE `.exe` filename. The file is not actually 16-bit; it is ELF.

## Current source output expectation

`examples/hello.sm` is:

```sutram
# Hello World in Sutram
mukhya()
    likha("Namaste! Sutram v6.0\n")
```

After the PE64 backend is implemented, running the generated program must print:

```text
Namaste! Sutram v6.0
```
