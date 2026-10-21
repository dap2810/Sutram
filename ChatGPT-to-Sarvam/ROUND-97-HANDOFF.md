# Sutram ROUND-97 — ChatGPT → Sarvam (2026-10-21)

**New assignment:** [Sarvam ROUND-97](../Sarvam-to-ChatGPT/ROUND-97.md). **Pinned live source baseline:** `18dbad0a9cb732d09ace5e3d348713149db83057`, project log **v282**, native compiler **v239** (prior accepted version; not freshly rebuilt). **All three workstreams delivered**, design/source evidence + genuine *developer-host* tests. **No compiler/linker edits, no tests/golden changes, no CI launches or PR merges.** All new files are under `ChatGPT-to-Sarvam/` on `main`.

## WS1 — Sidecar: exact format, discovery and failure BEFORE linking

Read [byte-exact proposed `.sffi` contract](ROUND-97-WS1-SIDECAR-SPEC.md), [sample](ROUND-97-WS1-SIDECAR-SAMPLE.sffi), [executed model](ROUND-97-WS1-SIDECAR-ORACLE.py), and [raw stdout](ROUND-97-WS1-SIDECAR-OBSERVED.txt).

**Proposed strict file**, ASCII-compatible UTF-8, LF-only, max 8 KiB/64 declarations, no BOM, CR, whitespace, comments, duplicates or ignored fields:

```text
sutram-ffi-v1|linux-x86_64-sysv
s_add|2|i64,i64|i64|sutram_ffi_add
```

Each record: `sutram_local_name|arity_0_to_6|exact_arg_kinds|return_kind|external_elf_symbol`. The grammar recognizes `i64, ptr, f64` arguments and `i64,ptr,f64,void` returns, but **the first implementation MUST reject everything except i64 arguments + i64 return** (`E_FFI_ABI_UNSUPPORTED`) until real types/register ABI are supported. The importer should find the file **only by explicit new `--ffi-sidecar <path>` flag, valid only alongside opt-in `--object/--separate`**; don't alter regular `yoj` or default mode. The flag is **proposed**, not currently implemented.

**The deciding negative:** a source call `s_add(17)` against this sidecar must be rejected by the actual compiler's existing-style **source-located `E_ARITY`**, with nonzero exit and **NO `.smo` output**. Likewise `s_add(17,25,1)`. The correct call `s_add(17,25)` must generate a **named `rel32` relocation for `sutram_ffi_add`** and **no fake function definition / `prati 0` stub**. Consult live `src/sutram_compiler.asm:7666–7767` (`r7_note_call` + `r7_check_arity`), keeping foreign signatures in a **separate table**, not `r7_defs`/`FUNCDEF`/R55 prototype expecting a body. The foreign-name→link-symbol translation is necessary if the names differ. A missing declaration must fail before link. No change to `SUTRAMO1` on disk.

**Actually executed model (Python, not Sutram): 26/26 PASS.** Positive records and two correct arguments passed; wrong 1/3 arguments returned **EXPECTED `E_ARITY`**; name/ABI/field/duplicate/overflow/unsupported-type negatives rejected. Exact tested script Git blob `8fdad8063e6a664b8c5a05ba35a63bdab2b933a0`; stdout Git blob `431ccc4ec3ab32920b54d319b7f082c91c577182`, both read back and matched locally executed bytes. **The native Sutram compiler DOES NOT yet enforce the sidecar: NOT_IMPLEMENTED / NOT_RUN.**

## WS2 — What our NASM linker must extract from ELF

Read [byte-level ELF bridge contract](ROUND-97-WS2-ELF-BRIDGE-SPEC.md), [positive C](ROUND-97-WS2-FREESTANDING-C.c), [negative C](ROUND-97-WS2-NEGATIVE-C.c), and [raw readelf/gcc output](ROUND-97-WS2-ELF-OBSERVED.txt).

**Header:** require ELF64 little endian, `ET_REL=1`, x86-64 machine 62. Read `e_shoff@40`, `e_shentsize@58=64`, `e_shnum@60`, `e_shstrndx@62` with checked bounds. **Sections:** each 64-byte `Elf64_Shdr` contains name/type/flags/offset/size/link/info/align/entsize; find one allocated executable `.text`. **Symbol table:** 24-byte `Elf64_Sym`, names via symtab's `sh_link` string table; require exactly one sidecar-named, global, visible `STT_FUNC` inside `.text`, correct offset/size; ELF does **not** encode a C function's arity/kinds. **Relocations:** `Elf64_Rela` is 24 bytes (`r_offset`, `r_info`, signed `r_addend`); `R_X86_64_PLT32=4` and `R_X86_64_PC32=2` use `S+A-P` with P at the field and typical `A=-4`. In contrast `SUTRAMO1` stores only a named field and uses `S-(field+4)`, with no kind or addend. Thus general ELF REL/RELA cannot simply be copied into a `SUTRAMO1` hole. **First milestone: reject ALL nonempty ELF relocations, all unresolved helpers, data/TLS/nonempty extra allocated sections, PIC/GOT, CRT, and unsupported ABI.** Wrap only validated freestanding `.text` as `SUTRAMO1` CODE + one definition, no relocations; our project NASM linker then resolves the Sutram caller's existing named hole. Later broaden relocations in a versioned, separately tested phase.

**Genuinely executed host check:** GCC 14.2 x86-64 compiled freestanding `sutram_ffi_add(long,long)` to an **856-byte ELF `ET_REL`** with `.text` **5 bytes at file offset 0x40**, **GLOBAL STT_FUNC at offset 0, size 5**, no relocations and no undefined symbols. A negative C function calling `missing_helper` generated a **992-byte ET_REL** with **`.rela.text` `R_X86_64_PLT32` field offset 4, addend -4 and undefined `missing_helper`**. Raw host output Git blob `ecd4135f24472f59448abf37a8fd60344d9a61d1` matches exact local file. **This round did NOT execute the NASM foreign loader, since one is not implemented.** R96's Python conversion/linked control remains prior test evidence, not a new native capability.

Reproduce from repository root (Linux, development controls only):

```sh
gcc -O2 -c -ffreestanding -fno-stack-protector -fno-asynchronous-unwind-tables -fno-unwind-tables -fno-pic -fno-pie ChatGPT-to-Sarvam/ROUND-97-WS2-FREESTANDING-C.c -o /tmp/r97good.o
gcc -O2 -c -ffreestanding -fno-stack-protector -fno-asynchronous-unwind-tables -fno-unwind-tables -fno-pic -fno-pie ChatGPT-to-Sarvam/ROUND-97-WS2-NEGATIVE-C.c -o /tmp/r97bad.o
readelf -h -SW -Ws -Wr /tmp/r97good.o
nm -u /tmp/r97bad.o
readelf -Wr /tmp/r97bad.o
python3 -B ChatGPT-to-Sarvam/ROUND-97-WS1-SIDECAR-ORACLE.py
```

## WS3 — Bounded performance decision, NOT speed development yet

[Acceptance spec](ROUND-97-WS3-BENCHMARK-ACCEPTANCE.md) upgrades R96's seven non-flattering benchmarks with an explicit threshold. **On seven predeclared, semantically equivalent workloads, 7/7 must show Sutram median steady-state runtime at least 5% faster than the FASTEST comparable C or Zig build** (`speedup≥1.05`) and paired bootstrap 95% CI lower bound **>1.0**, with **≥30 independent random-order runs** per profile, replicated on **two hardware hosts**. All output/exit/error/safety and full compiler correctness gates must pass first; otherwise comparison is INVALID. If **even one** workload misses that requirement, the bounded seven-workload speed goal is **NOT MET**. Additional much stricter **all measured aspects** acceptance requires startup at least 5% better plus binary size, peak memory and developer build time no worse than either language across all seven. If any axis missing/failing, all-aspect threshold is **NOT MET**. **This can never logically prove faster on every possible program and machine**; report only the measured scope. New benchmarking **NOT_RUN**, per owner's development-first priority.

## What Claude/Sarvam should do next

1. Approve/adjust sidecar header and flag contract, then **implement actual compiler validation and `E_ARITY` negative** (wrong arity must not produce any object). Preserve ordinary direct mode, 558-program byte guard, full suite/fuzz/corpus and Windows-specific gate.
2. Implement the **project-owned NASM** strict zero-ELF-reloc bridge (or a NASM linker mode for the same contract). Test exact symbol and section bounds, missing/helper/duplicate/unsupported inputs, actual Sutram-generated caller and final executable. The first foreign object should **not** require libc or GNU `ld` for the final Sutram link.
3. Only after this native proof, expand ABI/reloc/format support. Keep benchmark execution in the deferred optimisation phase, not this round.

## Truth table (do not upgrade design controls into native PASS)

| Evidence / workstream | Status |
|---|---|
| WS1 exact sidecar spec, discovery decision, E_ARITY integration plan | **PASS — design/source** |
| WS1 developer Python sidecar model | **PASS 26/26** |
| Wrong-arity 1 and 3 in the *model* | **EXPECTED_REJECTION** (`E_ARITY`), no Sutram compile |
| WS2 ELF64 host C compilation and readelf inspection | **PASS**; positive zero-relocation object + negative PLT32 observed |
| Actual Sutram compile-time FFI arity & NASM ELF bridge | **NOT_IMPLEMENTED / NOT_RUN** |
| WS3 explicit seven-program performance acceptance | **PASS — design**; actual benchmarks **NOT_RUN** |
| Fresh Sutram regression/fuzz/corpus or native Windows run in R97 | **NOT_RUN** |

[Structured raw evidence / Git SHA ledger](ROUND-97-OBSERVED.json) records exact tools, blobs, input/output and separate statuses. **No source/compiler/linker/goldens/installer/pack/CI files were changed**. This delivery ends **Round 97**; await the owner's next manual `CHECK FOLDER`.
