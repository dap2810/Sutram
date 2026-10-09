# Sutram Windows Native Port — AI Handoff (2026-10-01)

This file is the canonical continuation point for another AI/developer. Read this before changing code.

## 1. Current milestone

The **Sutram compiler host and Windows installer are working natively on Windows 11**.

Verified on the user's real machine:

- OS: Windows 11, build 26200
- Kernel string: Windows NT 10.0.26200.0
- PowerShell: 5.1.26100.9444
- NASM: `C:\mingw64\bin\nasm.exe`
- MinGW GCC: `C:\msys64\ucrt64\bin\x86_64-w64-mingw32-gcc.exe`
- Native compiler host builds as PE32+ x64.
- Native compiler smoke tests pass.
- Native Win32 setup wizard builds and passes its package-overlay self-test.
- Installer adds Sutram to PATH when selected.
- After install, `sutram --version` works directly from CMD/PowerShell.

Real-machine `sutram --version` output:

```text
Sutram 1.0 (v29) Windows host preview — the complete thread
Sanskrit-keyword language -> x86-64 machine code
```

The v11 setup build completed with:

```text
BUILD PASSED ALL WINDOWS RELEASE CHECKS.
BUILD PASSED.
Installer: Sutram-Setup.exe
```

Installer SHA-256 from the user's successful Windows build:

```text
D8EEB96A68BCE85693B268E336BBE31E58F34AE39E7A0A444E8581BFF530BD84
```

## 2. Critical remaining blocker

The compiler executable (`sutram.exe`) is a native Windows PE64 program, **but programs produced by Sutram are still Linux ELF executables**.

This was confirmed on the user's real machine after compiling the hello example to `hello.exe`:

- Generated file size: 210 bytes
- First four bytes: `7F 45 4C 46`
- That is the ELF magic header, not Windows PE.
- Windows therefore refuses to execute the generated file despite the `.exe` extension.

A valid Windows executable must begin with `4D 5A` (`MZ`) and contain a later `50 45 00 00` (`PE\0\0`) signature.

**Do not spend more time on the installer unless a regression is found. The priority is the generated-program PE64 backend.**

## 3. Exact hello example and expected output

Current source file: `examples/hello.sm`

```sutram
# Hello World in Sutram
mukhya()
    likha("Namaste! Sutram v6.0\n")
```

The acceptance test for the new backend is:

```cmd
sutram examples\hello.sm hello.exe
hello.exe
```

Expected output:

```text
Namaste! Sutram v6.0
```

Then verify:

```powershell
$b = [IO.File]::ReadAllBytes((Resolve-Path .\hello.exe).Path)
'{0:X2} {1:X2}' -f $b[0],$b[1]
```

Expected:

```text
4D 5A
```

## 4. Source locations to start with

### Windows compiler source

`src/sutram_compiler_win.asm`

Important current locations in v11:

- Around line 1364: compiler calls `write_elf` after generating machine code.
- Around line 4391: `emit_byte`.
- Around line 4402: `emit_u32`.
- Around line 4420: `emit_u64`.
- Around line 4514: generated main epilogue emits Linux `sys_exit(0)` (`rax=60`, `syscall`).
- Around lines 6373/6412/6453 and later: generated builtins emit Linux `syscall` instructions.
- Around line 9715: `write_elf` constructs the ELF64 header/program header and writes `code_buf`.

Search for these terms before editing:

```text
write_elf
sys_exit
syscall
0x0F, 0x05
.ge_call_band
.ge_call_dvaram
.ge_call_paadh
.ge_call_likha
```

### Windows compiler-host shim

`win/native_host.asm`

This already contains working host-side WinAPI integration, including imports/calls for:

- `GetStdHandle`
- `ReadFile`
- `WriteFile`
- `ExitProcess`

This host shim makes the compiler itself run on Windows. It is **not automatically available to generated programs**. Generated PE programs need their own PE import table/runtime stubs or another deliberate runtime architecture.

## 5. Recommended PE64 implementation sequence

Do not attempt every language feature at once.

### Phase A — minimal native PE64 hello executable

1. Add a Windows generated-program backend alongside the current ELF backend.
2. Replace `write_elf` on the Windows compiler path with a PE32+ x64 writer (`write_pe64` is a reasonable name).
3. Build a minimal PE image containing:
   - DOS/MZ header
   - PE signature
   - AMD64 COFF header (`Machine = 0x8664`)
   - PE32+ optional header (`Magic = 0x20B`)
   - `.text`
   - `.rdata` as needed
   - `.idata` import table
   - correct file alignment and section alignment
   - entry point RVA
4. Initially import only what hello needs:
   - `KERNEL32.dll`
   - `GetStdHandle`
   - `WriteFile`
   - `ExitProcess`
5. Replace generated Linux write/exit sequences with Win64 calls.
6. Use Microsoft x64 ABI:
   - RCX, RDX, R8, R9 for first four integer/pointer args
   - 32-byte shadow space before calls
   - 16-byte stack alignment at call boundaries
   - preserve nonvolatile registers appropriately
7. Make `hello.exe` run directly on Windows and print exactly `Namaste! Sutram v6.0`.

### Phase B — console input

Add/import `ReadFile` and map Sutram input operations to standard input handle semantics.

### Phase C — file APIs

Current generated builtins use Linux fd/syscall semantics (`open`, `read`, `close`, etc.). Port these deliberately to Windows handles, likely using:

- `CreateFileW` or `CreateFileA`
- `ReadFile`
- `WriteFile`
- `CloseHandle`

Do not simply reinterpret Linux fd values as Windows HANDLEs without a compatibility design.

### Phase D — remaining syscall-backed features

Search all emitted `0F 05` sequences and port them one by one. Networking and other OS services may require additional DLL imports (for example Winsock) and initialization rules.

### Phase E — regression suite

Every Windows release should fail unless all of these pass:

- generated file begins `MZ`
- PE signature exists and machine is AMD64
- generated file is not ELF
- generated hello runs on Windows 11
- exact stdout matches expected source output
- exit code is 0
- paths with spaces work
- Unicode source/output paths work
- malformed Sutram source still gives a diagnostic and nonzero exit
- existing compiler-host smoke suite still passes

## 6. Do not regress these solved Windows issues

The Windows port went through many packaging/build failures that are already resolved in v11:

1. Linker auto-detection for Visual Studio/LLVM/MinGW.
2. MinGW selected successfully on the user's machine.
3. PowerShell 5.1 `-Wl,...` comma parsing fixed.
4. PowerShell 5.1 inline `(if ...)` incompatibilities fixed.
5. Corrupted/mojibake Indic assembly literals repaired and compiler source made ASCII-stable where NASM parses strings.
6. Parser recursion bug fixed so malformed nested syntax reports a compiler diagnostic instead of silently recursing/crashing.
7. IExpress abandoned because it was unreliable on the target system.
8. `windres` abandoned because its subprocess preprocessor chain was unreliable in the detected mixed MinGW/MSYS2 environment.
9. Native Win32 installer now uses MinGW GCC plus a SHA-256-validated PE overlay payload.
10. Standard `sha256sum` manifest lines use `hash *filename`; the `*` must be stripped when interpreting the filename on Windows. v11 fixed this consistently in both preflight and build stages.
11. Installer PATH ownership is tracked so manually existing PATH entries are not removed on uninstall.
12. Uninstall preserves unknown/user-created files and only removes installer-owned payload/integration.

Avoid reintroducing IExpress, Inno Setup, `windres`, WSL, or Linux runtime dependencies into the end-user installer path unless there is a compelling reason and the user explicitly agrees.

## 7. Installer status

The v11 installer is considered a working milestone. Its architecture is documented in `HANDOFF.md` and `RELEASE_CHECKS_V11.txt`.

It provides:

- native x64 Win32 wizard
- default `Program Files\Sutram` destination
- optional machine PATH integration
- Start Menu integration
- optional Desktop shortcut
- Apps & Features registration
- safe upgrade/reinstall checks
- SHA-256 payload verification
- setup self-test
- safe uninstall ownership rules

The **end user does not need NASM, MinGW, Visual Studio, WSL, or Linux** after setup is built.

## 8. Definition of done for the next milestone

Do not call the Windows port complete until all of the following are true on a real Windows machine:

```cmd
sutram --version
sutram examples\hello.sm hello.exe
hello.exe
```

and:

- `hello.exe` begins `4D 5A`
- it contains a valid PE32+ AMD64 header
- it prints exactly `Namaste! Sutram v6.0`
- it exits 0
- no WSL/Linux subsystem is involved
- no separate runtime/tool installation is needed to run the generated EXE

When that minimal milestone passes, expand Windows coverage to the rest of Sutram's syscall-backed features without breaking Linux support.
