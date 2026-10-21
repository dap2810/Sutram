# Sutram ROUND-91 WS1 — C FFI `printf`: smallest probe and verified linking blocker

**Assignment:** `Sarvam-to-ChatGPT/ROUND-91.md`. **Accepted source checked:** `src/sutram_compiler.asm`, Git blob `4547e4737843567ad4b807dd6d9a5e06ca1cb085`, in v256. **Status: current Sutram C FFI NOT IMPLEMENTED; separate C-ABI control PASS; native Sutram compile NOT_RUN.**

## Minimal Sutram-side attempt (cannot link today)

[ROUND-91-WS1-PRINTF-PROBE.sm](ROUND-91-WS1-PRINTF-PROBE.sm) is the minimal intentionally unsupported Sutram program:

```sutram
mukhya() {
    printf("Hello from Sutram C FFI\n")
}
```

**Required native verification on a machine with a current Sutram compiler:**

```sh
./sutram_compiler --check ChatGPT-to-Sarvam/ROUND-91-WS1-PRINTF-PROBE.sm
./sutram_compiler ChatGPT-to-Sarvam/ROUND-91-WS1-PRINTF-PROBE.sm /tmp/r91_ffi_test.bin
```

**Sutram command/status/stderr: NOT_RUN.** This environment has GNU `as`/`ld`/`gcc` but **no NASM, no locally mounted `sutram_compiler`**, and a full GitHub clone was unavailable. Thus the precise *native* Sutram error bytes are not reported or invented. The source path `src/sutram_compiler.asm:11839–11858` establishes what is expected at this point: `backpatch_calls` searches the compiler-local `func_table`; an unresolved function reaches `msg_undefined_func` (11851) and exits 1 (11857–11858). The compiler's builtins table has no `printf`. A source-predicted complaint is not a measured CLI result.

## Exact structural blocker

Current `src/sutram_compiler.asm:23049–23125` builds a fixed native ELF image, not a linkable `.o` unit:

- Line **23068** writes `e_type=2` (`ET_EXEC`, not `ET_REL=1`); 23069 chooses AMD x86-64.
- Lines **23075–23083** set section-table offset 0, section-header count 0, and one program header; it has **no external symbol table / relocation records**.
- Lines **23089–23113** write one directly loadable `PT_LOAD` code segment, rather than a relocatable object with `printf` as an undefined external.
- No `PT_INTERP` / dynamic symbol-import support is emitted, and the writer never invokes a C-aware linker. A filename ending `.o` does not change these ELF fields.
- The release's regular `prakriya` call path uses internal rel32 backpatches against Sutram functions (11821–11838) and errors on unresolved names (11839–11858). This is not the Linux SysV external symbol ABI; translating every function call to libc-compatible ABI by assumption would risk regressions.

**Conclusion:** A genuine Sutram `printf` call requires explicit foreign declarations, argument ABI lowering, external symbols/relocations, a compatible linker/interface to it, and libc being present somehow. Those changes touch the compiler object and link model: **STOP, do not restructure the working compiler in this capability round**.

## ACTUALLY EXECUTED Linux x86-64 C-ABI control — not a Sutram compiler test

The source in [ROUND-91-WS1-ABI-CONTROL.S](ROUND-91-WS1-ABI-CONTROL.S) is a minimal handwritten x86-64 SysV assembly caller of `printf`, with one `long` argument (42). It sets `rdi` to the format, `rsi` to 42, and `al=0` for a variadic libc call; linking adds the C startup/loader. These exact commands ran on Linux x86-64, GCC **14.2.0**, GNU ld **2.44**:

```sh
gcc -c /mnt/data/sutram_round91/ffi_abi_control.S -o /mnt/data/sutram_round91/ffi_abi_control.o
ld -o /mnt/data/sutram_round91/ffi_bare /mnt/data/sutram_round91/ffi_abi_control.o
gcc -no-pie /mnt/data/sutram_round91/ffi_abi_control.o -o /mnt/data/sutram_round91/ffi_abi_control
/mnt/data/sutram_round91/ffi_abi_control
readelf -l /mnt/data/sutram_round91/ffi_abi_control
readelf -d /mnt/data/sutram_round91/ffi_abi_control
gcc -static -no-pie /mnt/data/sutram_round91/ffi_abi_control.o -o /mnt/data/sutram_round91/ffi_static_control
/mnt/data/sutram_round91/ffi_static_control
```

Exact observed results:

```text
GCC_COMPILE_EXIT=0
LD_BARE_EXIT=1
GCC_LINK_EXIT=0
CONTROL_RUN_EXIT=0
LD_BARE_STDERR:
ld: warning: cannot find entry symbol _start; defaulting to 0000000000401000
ld: /mnt/data/sutram_round91/ffi_abi_control.o: in function `main':
(.text+0x15): undefined reference to `printf'
RUN_STDOUT:
Sutram FFI ABI control: 42
INTERPRETER:
  INTERP
  [Requesting program interpreter: /lib64/ld-linux-x86-64.so.2]
NEEDED:
  Shared library: [libc.so.6]
STATIC_LINK_EXIT=0
STATIC_RUN_EXIT=0
STATIC_RUN_STDOUT:
Sutram FFI ABI control: 42
DYNAMIC_FILE_BYTES=15816
STATIC_FILE_BYTES=754336
```

The generated `.o` is ELF64 **ET_REL** and has an **undefined `printf` symbol** (`readelf -Ws`); the linked dynamic ELF has `PT_INTERP` and `NEEDED libc.so.6`. A standalone linker without libc fails. The static `gcc -static` build runs without dynamic libc but **embeds** hundreds of KiB of libc and startup machinery; it is not a no-C-runtime Sutram output. These experiments prove the OS toolchain can call `printf`, **not that Sutram can**.

### Runtime-free alternative available today

For ordinary printing, `likha("Hello from Sutram\n")` and Sutram's native Linux `sys_write`-based output need no libc. Existing `dvaram(path,flags[,mode])` is a **file-open** syscall builtin, not a generic C-call mechanism. A limited new syscall wrapper patterned on `likha`/`dvaram` could expose additional OS services with distinct Linux/Windows adapters, **but it cannot provide an arbitrary C FFI or libc `printf` semantics**. Keep the C-FFI track optional and explicitly dependency-bearing if the owner later approves the necessary linking architecture.

## Future acceptance contract (after a separate owner-approved architecture decision)

1. A new opt-in foreign declaration names the exact C symbol and its signature/target ABI; all foreign calls require a verified declaration (fail closed).
2. Emit a true relocatable object or supported foreign imports. A linker, either bundled with developer tooling or explicit at build time, resolves `printf` (no silent fallback).
3. Linux SysV ABI (integer registers, 16-byte stack alignment and `al` vector-arg count for varargs) and Windows x64 ABI (four register arguments, 32-byte shadow, stack alignment, suitable UCRT linkage) are separate targets, not interchangeable.
4. Only an **explicit opt-in** may introduce libc/linker dependencies; default pure-NASM toolchain-free binaries stay unchanged. Compare program output, exit status and dynamic dependencies on actual hosts; run standard regression/fuzz/negative suites before claiming FEATURE.
5. Missing declared symbol/ABI mismatch/module collision must give deterministic diagnostics and no runnable output, with source locations.

**Final WS1 status:** GNU C-ABI control dynamic and static **PASS**; standalone linker unresolved-symbol rejection **EXPECTED FAIL, observed**; Sutram `printf` call and native compiler **NOT_RUN**; true Sutram FFI **BLOCKED by object writer / no external runtime contract**. No compiler/library/codegen/golden or installer modification.
