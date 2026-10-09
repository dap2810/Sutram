# Next Engineering Task — Native PE64 Generated Programs

## Objective

Change the Windows Sutram compiler from producing ELF64 files to producing directly runnable Windows PE32+ AMD64 executables.

## Current implementation anchors

File: `src/sutram_compiler_win.asm`

- `write_elf` starts around line 9715 in v11.
- The call to `write_elf` occurs around line 1364.
- `emit_byte`, `emit_u32`, and `emit_u64` are around lines 4391, 4402, and 4420.
- Generated main currently emits Linux `sys_exit(0)` around line 4514.
- Generated builtin/file operations contain multiple raw `syscall` emissions around the 6300-7200 range and later.

File: `win/native_host.asm`

The compiler-host side already demonstrates functioning WinAPI calls/imports for console I/O and process exit. Use it as a reference for calling convention and API semantics, not as a runtime automatically linked into generated programs.

## Minimal first implementation

Create a PE writer that supports one `.text` section plus import/read-only data as needed and imports:

- KERNEL32.dll!GetStdHandle
- KERNEL32.dll!WriteFile
- KERNEL32.dll!ExitProcess

Generate code for `likha("literal")` that obtains stdout and calls `WriteFile`, then calls `ExitProcess(0)`.

Required Win64 ABI properties:

- RCX/RDX/R8/R9 argument registers
- 32 bytes of shadow space for calls
- 16-byte stack alignment at call boundaries
- valid RIP-relative/IAT calls or another correct import-call mechanism

## Suggested PE structure

At minimum:

- DOS header and DOS stub / `e_lfanew`
- `PE\0\0`
- IMAGE_FILE_HEADER (`Machine=AMD64`)
- IMAGE_OPTIONAL_HEADER64 (`Magic=0x20B`)
- data directories including import directory
- section table
- `.text`
- `.rdata` or combined read-only payload
- `.idata` import descriptors, INT/IAT, hint/name entries, DLL string

Use normal alignments unless there is a deliberate reason otherwise, e.g.:

- SectionAlignment: 0x1000
- FileAlignment: 0x200

## Acceptance test

```cmd
sutram examples\hello.sm hello.exe
hello.exe
```

Expected stdout:

```text
Namaste! Sutram v6.0
```

And file verification:

- bytes 0-1 = `4D 5A`
- PE signature exists at `e_lfanew`
- COFF machine = `0x8664`
- optional-header magic = `0x20B`
- process exit code = 0
- no ELF magic

Do not rename an ELF file to `.exe` and consider the task complete.

## After hello works

Port generated runtime/builtins incrementally:

1. console output
2. console input (`ReadFile`)
3. file handles (`CreateFileW/A`, `ReadFile`, `WriteFile`, `CloseHandle`)
4. memory/runtime needs if present
5. networking/system APIs
6. all remaining emitted Linux `syscall` sequences

Preserve the Linux backend independently if cross-platform support is desired.
