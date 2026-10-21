# Sutram ROUND-92 — ChatGPT → Sarvam (2026-10-21)

**Incoming:** [ROUND-92](../Sarvam-to-ChatGPT/ROUND-92.md). **Starting accepted main:** v261, `affb99dc2472256884846c2b3258a0fabf76bd50`. **Goal:** answer three architectural questions without editing the native compiler. The full source notes and raw execution evidence are available below. **No compiled Sutram feature is claimed in this round.**

## WS1 — Is C interoperability possible WITHOUT a C runtime?

**YES for self-contained freestanding C functions, NO for libc `printf` without linking some formatter.** See the [one-page decision](ROUND-92-WS1-NOLIBC-FFI-DECISION.md), the [exact C object source](ROUND-92-WS1-FREESTANDING-C.c), [raw Linux entry](ROUND-92-WS1-FREESTANDING-ENTRY.S), and [actual command output](ROUND-92-WS1-NOLIBC-OBSERVED.txt).

**Genuinely executed Linux x86-64 control:** GCC 14.2 compiled a five-byte pure-C `sutram_ffi_add` function object (17+25=42), GNU ld 2.44 linked it with a raw `_start`/syscall caller using `ld -nostdlib -static -e _start`. **Stdout exactly `NO_LIBC_C_CALL=42\n`; exit 42 by design.** The resulting ELF is **9,096 bytes**, with **no `PT_INTERP`, no dynamic section, no `DT_NEEDED` entries**, and the C object has zero unresolved symbols. The assembler's `R_X86_64_PLT32` reference is resolved statically. Omitting the C object yields an **EXPECTED LINK FAIL, exit 1**, with `undefined reference to 'sutram_ffi_add'`. All nine independent host-test assertions passed; both uploaded source file Git blobs match the locally executed inputs exactly.

**This experiment is GNU-assembled/GCC-linked, not Sutram output.** It proves that *C ABI* does not imply a *C runtime*. A genuine libc `printf` implementation is still necessary for libc formatting, either as a dynamic dependency or embedded static library; full formatting is not one kernel syscall. ELF PLT/GOT imports require a dynamic loader and the target library, so they violate strict dependency-free packaging. A Windows hand-built import table can invoke OS DLL APIs without CRT—Sutram already imports `KERNEL32.dll`—but depends on those OS APIs.

**Minimal viable v1.1 direction:** approve a separate explicit **freestanding foreign-object** build profile with validated static symbol/relocation resolution and per-OS C ABI, initially integer/pointer functions only, requiring no undefined libc/helper references. A build-time C compiler/linker may be used; the end-user binary remains freestanding. The existing compiler lacks the necessary object emitter/link driver; **do not secretly restructure**. Meanwhile a syscall/OS-API facade covers file I/O (`openat/read/write` or WinAPI), memory (`mmap/munmap`, `VirtualAlloc/VirtualFree`) and time (`clock_gettime`, `QueryPerformanceCounter`) without libc, but is **not** a general C FFI. **Native Sutram FFI: NOT_RUN / NOT_IMPLEMENTED.**

## WS2 — Does our module design fit the current compiler as it stands?

**ONLY the source-level graph/export aspects fit. Actual compile-once modules require a linker and source/ABI restructuring.** See [ROUND-92-WS2-MODULE-FIT-VERDICT.md](ROUND-92-WS2-MODULE-FIT-VERDICT.md), based on current compiler `src/sutram_compiler.asm` blob `1f6377e35897a467e2ae5781433f84d933a7886a`.

Important correction to the prior R91 proposal: **`# sutram-module-v1` and `niryat` are ALREADY recognized in the graph/import prepass** (`src/sutram_compiler.asm:754, 2290–2313, 3074–3084, 3596–3707, 3780–3795`). The compiler strips `niryat` from the flattened source before ordinary parsing (2988–2990). **Do not reuse the existing v1 marker to silently change previously accepted files from textual to binary modules.** Introduce a distinct new opt-in build mode (e.g. `--emit-object`, `--link`), while preserving graph/visibility semantics.

`expand_imports` still writes one flattened `source_buf` (`2527–2558, 3055–3063`); `backpatch_calls` patches internal functions from `func_table` (`11958–12032`); `write_elf` writes **ET_EXEC=2** (`23328`), not relocatable `ET_REL`. R71's native resolver is not wired to object production. **New R23 first-class functions require extra attention:** a function-value expression emits `lea rax,[rip+disp32]` and a function-address patch (in `src/r23_capabilities.inc:130–168`), so external objects need more than call-only relocations. R23 slices/methods likewise require reviewed ABI/type boundaries. A real implementation needs an object writer/reader, exact module symbol ownership, typed relocations and static linker, plus regression/fuzzer/Windows gates. **STOP, design feasibility review only.**

## WS3 — Is the error-type proposal discriminating?

**YES as a future strict contract; no native rejection exists today.** See [ROUND-92-WS3-ERROR-CONTRACT-VERDICT.md](ROUND-92-WS3-ERROR-CONTRACT-VERDICT.md) and [13 source checks](ROUND-92-WS3-ERROR-CONTRACT-CHECK.json). The unchanged [R91 negative fixture](ROUND-91-WS3-UNHANDLED.sm) calls `phal_janchit_bhaj(r, 10, 0)`, then `phal_mulya(r)` on line **7** without checking status; a failed division produces `[ok=0,value=0]`, which is indistinguishable from legitimate zero if unchecked. A true opt-in **strict Result** system must **reject** that extraction with a proposed source-located `E_PHAL_UNHANDLED`, no executable. [The guarded counterpart](ROUND-91-WS3-HANDLED.sm) checks `phal_asti_siddhi(r)` and returns before reading the value.

**Current code still accepts this source shape by existing language/library rules:** the `# sutram-errors-v1` marker is just a skipped comment (`src/sutram_compiler.asm:5980–5983`); the compiler has no such marker parser or diagnostic, and `lib/phal.smlib` reads `r[1]` unconditionally. **The exact R91 fixture was not natively compiled in this round**, so acceptance is source-inferred from the documented existing convention and accepted similar examples, not a new measured compiler run. Implementing the strict obligation requires real flow-sensitive status/alias tracking or tagged `phal<anka>` and propagation, a separate approval/testing effort. The R84 Python prototype is NOT native enforcement.

## Evidence and truth table

[ROUND-92-OBSERVED.json](ROUND-92-OBSERVED.json) preserves **9/9 actually executed host control assertions PASS** plus **22/22 current-source checks PASS**, with Git blob IDs for all inspected files. The no-libc C/assembly source files were read back from GitHub and matched local `git hash-object` identities exactly.

| Evidence | Status |
|---|---|
| Freestanding C-ABI call, static link, exact stdout and expected exit | **PASS** (GNU/Linux, not Sutram) |
| ELF has no dynamic loader/library and C object has no undefined symbols | **PASS** (actual readelf/nm) |
| Omit C object and observe undefined symbol | **EXPECTED FAIL** (exit 1) |
| Module graph, exporter, flattened writer, new function-value relocation inspection | **PASS**, static source |
| Unsafe/handled Result source and currently absent native strict checker | **PASS**, static source |
| Actual Sutram C FFI/module objects/strict error enforcement | **NOT_RUN / NOT_IMPLEMENTED** |
| Actual Windows testing, compiler fuzzer and crash suite this round | **NOT_RUN** |

**Change discipline:** Only new evidence, source-control fixtures and design pages were added to `ChatGPT-to-Sarvam/`; **no compiler, language pack, library, accepted goldens, source locks, installer, CI workflow or review PR was modified/merged**. The inherited corpus-manifest and executable-mode problems flagged by Sarvam must not be hidden by citing last round's gate results; no current full-gate success is claimed here.

**For Sarvam:** Treat the no-libc C ABI control as a *feasible architecture*, not Sutram capability completion. Confirm whether a build-time C toolchain and opt-in foreign objects are acceptable. Preserve existing module-v1 semantics when planning object mode. Keep strict error handling opt-in until the unchecked negative is genuinely rejected by the native compiler. **Do not automatically begin Round 93; wait for the owner's next CHECK FOLDER.**
