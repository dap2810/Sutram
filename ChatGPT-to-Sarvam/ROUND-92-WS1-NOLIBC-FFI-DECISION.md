# Sutram ROUND-92 WS1 — A C function without a C runtime: YES, but not libc printf (design verdict)

**Question:** Can Sutram call a C function while its native executable remains free of libc, a C startup runtime, and a dynamic-language runtime? **Answer: YES for a freestanding C function with all dependencies resolved at static link time. NO for libc's `printf` without either libc or another formatter providing the equivalent behavior.** The current Sutram compiler cannot yet perform either arbitrary C call.

## Measured minimal control: no libc and no dynamic interpreter

The exact [freestanding C source](ROUND-92-WS1-FREESTANDING-C.c) defines `long sutram_ffi_add(long a, long b) { return a+b; }`. A tiny [Linux assembly entry](ROUND-92-WS1-FREESTANDING-ENTRY.S) passes 17 and 25 using the x86-64 System V **C ABI**, receives 42, prints a confirmation through raw Linux `sys_write`, and exits through raw `sys_exit`. Both objects were compiled with GCC; GNU `ld -nostdlib -static -e _start` linked them into one 9,096-byte ELF executable.

**Actually executed on Linux:** `NO_LIBC_C_CALL=42\n`, process exit **42** (intentional success code). `readelf` reports **no `PT_INTERP`, no dynamic section and no `NEEDED` libraries**, and `nm -u` on the C object lists no unresolved dependencies. The caller's object had `R_X86_64_PLT32` for `sutram_ffi_add`, resolved by the static linker. Omitting the C object made `ld` fail exit 1 with `undefined reference to 'sutram_ffi_add'` — a useful negative control. [Raw output, exact commands and SHA-256 hashes](ROUND-92-WS1-NOLIBC-OBSERVED.txt). **This is GNU/C assembly, not Sutram-emitted code; Sutram FFI remains NOT_RUN/NOT IMPLEMENTED.**

## Decision table — separate a C ABI from a C library

| Technique | Can call a C-ABI function? | Requires libc at runtime? | Fits hard no-runtime contract? |
|---|---|---|---|
| Statically link a small **freestanding C object** with no unresolved symbols | YES — actually controlled | **NO** | **YES** for the produced executable, but needs a build-time C compiler/linker or equivalent |
| Dynamic ELF `PLT/GOT`, `PT_INTERP`, DT_NEEDED a third-party `.so` | YES | Not necessarily libc, but **requires loader and external shared library** | **NO** under strict dependency-free distribution |
| Static-link libc's real `printf` | YES | No dynamic libc file; libc implementation is **embedded** | **NO** if the goal is to avoid C-runtime code, despite being self-contained |
| Hand-built Windows PE import table for OS-provided C-callable functions | YES (e.g. `WriteFile`) | **NO CRT**; depends on Windows DLL and its loader | **Conditional:** reasonable OS ABI dependency, not arbitrary portable C FFI |
| Direct Linux syscalls / Windows kernel APIs | YES for OS services, no general C function | **NO CRT** | **YES** for selected OS services; **NOT** equivalent to libc `printf` |

Sutram's compiler already uses hand-built Windows **`KERNEL32.dll` imports** (see `win/pe_imports.inc`: `WriteFile`, `ReadFile`, `CreateFileA`, `VirtualAlloc`, `ExitProcess`). That is a model for **OS API calls without a CRT**, not a general linker for arbitrary user C symbols. On Linux, a hand-written ELF dynamic import table still needs a loader and the target shared library; adding entries cannot conjure a missing symbol into existence.

## Smallest Sutram compiler extension that WOULD be needed

1. New **opt-in foreign declaration with exact symbol, static C-compatible integer/pointer signature and target ABI**, initially no variadics, floats, callbacks, exceptions or C struct passing. Keep ordinary `prakriya` calls unchanged. Scope C objects to explicitly supplied, pinned local files.
2. Emit a true relocatable code/object unit or an explicit vetted object-input/link phase; the existing `write_elf` writes `ET_EXEC` without symbols/relocations, and current `backpatch_calls` resolves only same-image Sutram names. `-o something.o` does not fix that.
3. Use x86-64 SysV registers and stack alignment for Linux, **separately** implement Windows x64 calling convention/shadow space. Only accept foreign objects whose undefined-symbol closure is empty (or all imports explicitly allowed as OS APIs); reject hidden `libgcc`/stack-check/TLS/constructor dependencies if the profile is freestanding. Verify architecture, section sizes, relocation types, executable-memory policy, export arity and hash. Reuse a reviewed static linker or build a bounded one; **do not write an ad-hoc unvalidated loader**.
4. Preserve the current pure-NASM standalone path by default. A development-time C compiler/linker may be needed for the opt-in build; the **end-user executable** need not ship GCC or libc. This is an architecture change, not a safe one-routine patch. **STOP, do not modify the compiler in this round.**

## Nearest useful capability now: syscall-only OS abstraction

For **file I/O**, Linux `openat`/`read`/`write`/`close`; Windows `CreateFileW`/`ReadFile`/`WriteFile`/`CloseHandle`. For **memory**, Linux `mmap`/`munmap` (and optional `mprotect`); Windows `VirtualAlloc`/`VirtualFree`. For **time**, Linux `clock_gettime` syscall; Windows `GetSystemTimePreciseAsFileTime` or `QueryPerformanceCounter`, with distinct realtime vs monotonic semantics. The OS wrappers must check errors, bounds and lifetimes, and expose a portable Sutram-facing API only where contracts actually match. Existing `dvaram` is a file-open builtin and `likha` writes output; neither is an arbitrary C-call bridge.

A `printf`-like **limited formatter** can convert bounded integers/strings into bytes and call `write`/OS output, but **it is not libc `printf`** (no full `%f`, locale, vararg promotions, stream buffering). Do not use the library name for a subset.

**R92 WS1 verdict:** measured freestanding C ABI call without libc **PASS (GNU control)**; meaningful runtime-free design **YES but new Sutram object/link support required**; actual Sutram C FFI and libc printf **NOT_RUN / NOT IMPLEMENTED**; no compiler modifications.
