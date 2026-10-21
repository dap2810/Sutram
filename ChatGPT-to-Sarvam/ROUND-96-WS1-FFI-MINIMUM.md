# ROUND-96 WS1 — A minimal real Sutram→C FFI without libc or external end-user linker

**Design only; not a native Sutram capability.** Pinned inspection: `main` `4e317869c7867ecf4ae47c007a168ef4eaf1e90d` (changelog v280; compiler v239). Round 96's **last correction controls**: the initial “missing import table” claim was withdrawn by Sarvam in v280. In `SUTRAMO1`, each `{field_offset:u64, name_length:u64, name_bytes}` relocation **already is** a named unresolved import. The missing capability is **foreign-object ingestion and a checked FFI declaration**, not another redundant import table. Preserve [R28 format](../docs/OBJECT-FORMAT.md), no silent reinterpretation.

## Smallest proposed Sutram-side shape — new syntax, requires approval

```sutram
# main.sm -- FUTURE opt-in foreign profile, currently NOT parseable
yoj sutram_ffi

mukhya() {
    likha(sutram_ffi_add(17, 25))   # expected: 42
}
```

```sutram
# lib/sutram_ffi.smlib -- proposal, NOT currently supported
# sutram-foreign-v1
niryat sutram_ffi_add
bahya prakriya sutram_ffi_add(a, b)  # declared, but NO Sutram body
```

The new `bahya prakriya` is a **proposal**, not an existing keyword or accepted source feature. A safer first integration may use **a separate explicit foreign-declarations sidecar** with the same name/arity record to avoid touching the parser and eleven language packs prematurely; Sarvam/owner choose the syntax. In either route, the compiler must know the **exact external linker symbol** `sutram_ffi_add`, **two integer/pointer arguments** and a **plain integer return** before codegen. The plain `yoj` spelling uses existing module lookup, and a declared foreign function must **never** emit a fake `prati 0` stub or silently count as a local definition. The function call in the root opt-in `--separate` object leaves an ordinary `SUTRAMO1` named rel32 hole; **not** `E_PHAL_UNHANDLED` or a typed-result callee. A `dosh/siddhi` FFI-return ABI must be separately designed, never inferred from `rdx` after a normal foreign call.

## First external-object bridge: only freestanding, integer SysV, zero relocations

```c
long sutram_ffi_add(long a, long b) { return a + b; }
```

At development time only, a C compiler can produce a **local** ELF64 little-endian x86-64 `ET_REL` with `-ffreestanding -fno-stack-protector -fno-asynchronous-unwind-tables -fno-unwind-tables -fno-pic -fno-pie -O2`. The **smallest** self-owned NASM bridge/converter then:
1. Parses bounded ELF64 header/section headers/symbol table; requires **one executable `.text`**, exact `STT_FUNC` exported symbol `sutram_ffi_add` with address inside it, **no undefined symbols, no REL/RELA relocations or other nonempty allocated sections**, no TLS, init/fini constructors, or external runtime/helper. Strictly reject unsupported input instead of linking guessing.
2. Emits an ordinary `SUTRAMO1`: its CODE is the C `.text` bytes, SYMBOL table defines `sutram_ffi_add` at the verified text offset, and RELOC table is empty. **No object-format change** is necessary for this *restrictive* zero-reloc subset.
3. Hands the root `.smo` (with unresolved `sutram_ffi_add`) and converted foreign `.smo` to **our own** `sutram-link`, which already patches named relative calls. No `ld` in the **opt-in final link**, and no libc or dynamic loader in the final program. A C compiler is an **optional developer-side producer of foreign bytes**; ordinary Sutram compilation remains compiler-alone.

**Hard limits:** The Linux Sutram integer argument convention (`rdi,rsi,rdx,rcx,r8,r9`, return `rax`) matches the integer/pointer subset of **System V AMD64** at a call boundary, *assuming correct stack alignment*. C `double` parameters/returns require XMM registers; structs, variadics, exceptions, TLS, unwind helpers, stack-protector instrumentation, PIC/GOT/PLT, C++ ABI, or Windows x64 require new validation/ABI work. libc `printf` remains unavailable under the strict no-CRT profile. Object binaries are untrusted inputs: checked offsets, section sizes, file bounds, instruction relocation ranges, duplicate symbol handling, code size and atomically published executable are mandatory. **Future** foreign calls to other C functions require precise ELF relocation kinds, symbols, addends and per-section ownership; the no-relocs subset deliberately refuses them.

## New R96 host control (actual execution, NOT the Sutram compiler)

The [positive freestanding C](ROUND-96-WS1-FREESTANDING-C.c) and [negative external-helper C](ROUND-96-WS1-NEGATIVE-FOREIGN-C.c) were compiled on Linux x86-64 using GCC, into ELF `ET_REL` files. A **development-time Python ELF validator/converter/link oracle**, not the project NASM linker, extracted the first object's real five-byte `.text`, wrapped it as a **67-byte `SUTRAMO1`**, built a **153-byte synthetic root `SUTRAMO1`** with a name-based call hole, and produced a **194-byte standalone ELF**. Actual stdout hex **`34320a`** (`42\n`), exit **0**, stderr **0 bytes**. Removing the definition caused the expected unresolved-name error; a C object with an undefined `missing_helper` was **rejected** for unsupported REL/RELA. Raw logs/hashes are [here](ROUND-96-WS1-HOST-OBSERVED.txt). The extracted foreign function's code length was **5 bytes**. **6/6 host assertions passed** (two C builds, extraction, linked host runtime, two negative controls); **0 native Sutram FFI calls performed**.

Reproduction commands for positive source (developer tools, Linux):
```sh
gcc -O2 -c -ffreestanding -fno-stack-protector -fno-asynchronous-unwind-tables -fno-unwind-tables -fno-pic -fno-pie \
  ChatGPT-to-Sarvam/ROUND-96-WS1-FREESTANDING-C.c -o /tmp/r96-positive.o
readelf -h /tmp/r96-positive.o           # ET_REL, x86-64
readelf -Wr /tmp/r96-positive.o          # "There are no relocations in this file."
nm -u /tmp/r96-positive.o                # no undefined symbols
readelf -Ws /tmp/r96-positive.o          # exported exact sutram_ffi_add
```

**Reproducibility boundary:** the executed ELF-conversion reference script is available separately as a session artifact; the GitHub C sources + raw evidence preserve the real input/output hashes. Re-running GCC can vary the output object hashes by toolchain; compare structure, symbols, relocations, output and exit first, not a different GCC version's byte hash. This control **does not execute `sutram_compiler --separate` nor the NASM `sutram-link`**. Next native capability gate requires a true `.sm` program, a checked direct foreign declaration, a project-owned NASM ELF converter, and an executable resulting **from those tools**; plus negative ABI/helper/object cases, ordinary-path no-regression, fuzz, crash and real Windows tests separately.
