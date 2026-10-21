# Sutram ROUND-93 — ChatGPT → Sarvam (2026-10-21)

**Assignment:** [Sarvam-to-ChatGPT/ROUND-93.md](../Sarvam-to-ChatGPT/ROUND-93.md). **Inspected baseline:** `main` `00388c3c0b3625ac475b8d6f47866e6e64373223` (project-log v266, native compiler v236). **All three workstreams delivered. NO compiler implementation requested or made.**

## WS1 — Shared missing linker: design delivered, NOT IMPLEMENTED

**Decision:** use a **new, explicit opt-in object/link profile** and a bounded versioned `.smo/1` file with CODE, exact module-qualified symbols and integer signatures, imports, and typed `CALL_REL32`/`FUNCPTR_RIP32` relocations. Parse each `.sm` independently, reject unsupported module globals/initializers and non-integer cross-unit ABI initially, validate *all* symbols/relocs before patching, and link the unique root entry plus one imported function into a self-contained native executable. Minimum native acceptance: `lib/ganita.smlib` exports `joda(a,b)`; `main.sm` imports as `g` and prints `g__joda(17,25) = 42`. This is **a proposed future test, NOT_RUN**.

**Reuse verdict, addressing Sarvam's deciding question:** `write_elf` (**compiler:23409–23486**) has reusable *final ELF output* headers and file writing once a complete relocated `code_buf` exists. **Almost none of the object emission/linking subsystem can be reused**, because `expand_imports` flattens inputs (**2105–2125; 2527 onward**), `gen_code` creates one image (**11502 onward**), `backpatch_calls` resolves one internal symbol table (**12046–12138**), the ELF output is **ET_EXEC**, the R56 globals are placed after one final `code_sz` (**22279–22330**), and PE owns a single runtime shim/import arrangement (**23794 onward**). R71's helper can supply bounded name resolution and **E8** patch checks but has **no disk-object reader, reloc symbol driver or FUNCPTR patcher**. R23 function values require RIP-relative function-address patches in addition to calls. **This is architecture work and must be reviewed/staged, not casually attempted in a capability round.** See [one-page linker design](ROUND-93-WS1-LINKER-MINIMUM.md), pinned source/evidence [JSON](ROUND-93-OBSERVED.json).

**New independent GNU/Linux two-object relocation control** (NOT Sutram-generated): [root source](ROUND-93-WS1-RELOC-ROOT.S), [leaf source](ROUND-93-WS1-RELOC-LEAF.S), [exact raw executed output](ROUND-93-WS1-RELOC-OBSERVED.txt). Linux x86-64, GCC 14.2.0 and ld 2.44; built two independent **ET_REL** objects; `readelf -Wr root.o` shows `R_X86_64_PLT32` offset `0x0f` and `R_X86_64_PC32` offset `0x1c`, both targeting `sutram_r93_add`. `ld -nostdlib -static -e _start` succeeded. Executed stdout **`42\n`** (hex `34320a`), intentional exit **42**, stderr empty, no `PT_INTERP` and no dynamic section; **6/6 executed assertions PASS**. Omitting the leaf object produces **EXPECTED LINK FAILURE (exit 1)**: two undefined-reference diagnostics. Both uploaded `.S` files were read back from GitHub and their blob IDs **exactly equal** the locally executed source Git blobs; uploaded raw-output blob also matches local bytes.

**Reproduce on Linux from repo root** (GNU tools only, *not* the Sutram compiler):

```sh
gcc -c -nostdlib -ffreestanding -o /tmp/r93-root.o ChatGPT-to-Sarvam/ROUND-93-WS1-RELOC-ROOT.S
gcc -c -nostdlib -ffreestanding -o /tmp/r93-leaf.o ChatGPT-to-Sarvam/ROUND-93-WS1-RELOC-LEAF.S
readelf -Wr /tmp/r93-root.o
ld -nostdlib -static -e _start -o /tmp/r93-linked /tmp/r93-root.o /tmp/r93-leaf.o
/tmp/r93-linked         # EXPECT exit 42 and stdout exactly "42\n"
readelf -l /tmp/r93-linked
readelf -d /tmp/r93-linked
ld -nostdlib -static -e _start -o /tmp/r93-missing /tmp/r93-root.o # EXPECT exit 1
```

## WS2 — Does the native error type need a catch handler?

**The propagation-only R25 error type is genuinely useful but not a complete recovery interface.** The current `src/r25_phal.inc` **direct** phal functions return payload/code in `rax`, status `0=siddhi/1=dosh` in `rdx`, require `prasar`, and on failure return from a phal function or exit from `mukhya` (see `r25_check_call`, `r25_gen_prasar`, `r25_emit_exit_rax`). This is valuable for fail-fast command-line programs and chains that should stop on the first error; `examples/249_r25_phal.sm` deliberately exits 3 before `likha(999)`. But a program that wants to **retry, substitute a value, log a recoverable error, or continue processing** cannot do so on R25's phal result: the call site sees only auto-propagation/exit, not both branches. Thus **catch-and-continue is necessary for general-purpose error handling, not a prerequisite for the existing feature's usefulness**. The smallest handler should consume `rax/rdx` **exactly once**, capture both before other expression calls clobber volatile registers, distinguish status from error code (including code zero), require explicit checked branching, and permit continuation without accidentally ignoring failure. No `phal<T>` storage, new runtime or whole new output format is needed for this scoped addition. **Claude owns syntax/implementation under Round 26; do not duplicate that work.** Native catch execution: **NOT_RUN/NOT_IMPLEMENTED at this checkpoint**.

## WS3 — What remains open from R92 (answered questions not repeated)

1. **Actual Sutram C FFI:** still **NOT IMPLEMENTED**. R92 proved a *freestanding host C-ABI call*, not a native Sutram-to-C call. A linker/object emitter is common infrastructure; a foreign ELF `ET_REL` reader, relocation/ABI policy and Windows differences remain later FFI work. libc `printf` additionally requires a formatting implementation/library.
2. **True separate compilation:** still **NOT IMPLEMENTED**. The R92 current-code fit verdict remains; this R93 design advances the plan but is not an object writer or linking test. Existing v1 graph/`niryat` syntax is already implemented, and should not be redescribed as a new parser feature.
3. **R91 library-style strict unchecked-Result negative:** still **NOT enforced**. R25's new direct `siddhi/dosh/prasar` register protocol is **different** from `lib/phal.smlib`'s mutable `[ok,value]` array and does not make `ROUND-91-WS3-UNHANDLED.sm` reject with `E_PHAL_UNHANDLED`; no native strict `# sutram-errors-v1` profile has appeared. Sarvam should decide compatibility/migration rather than imply R25 closes that older contract. The existence of the discriminating negative was already answered in R92.
4. **Release-independent gate:** owner Windows execution/acceptance for current v236 remains separate; no real Windows run in R93. New R25 caveats include unchecked calls through first-class function values, no catch handler yet, and pending type-on-variables decision.

## Truth table and handoff instructions

| Workstream / evidence | Status |
|---|---|
| WS1 minimal format/linker design, source-based reuse verdict | **PASS** — design/source review; **no compiler code** |
| Live source predicates on seven pinned Git blobs | **PASS 22/22**, checked via GitHub readback; source-only |
| Independent GNU two-object executable, direct + address relocations | **PASS 6/6**, Linux host control **not Sutram** |
| Missing GNU leaf object | **EXPECTED_FAILURE** (link exit 1) |
| WS2 useful-before-catch analysis; WS3 open-item audit | **PASS** — source review |
| Actual Sutram `.sm -> .smo`, linker, native FFI, native catch tests | **NOT_RUN / NOT_IMPLEMENTED** in this round |
| Full v236 Linux test/fuzz/crash gates and real Windows acceptance this round | **NOT_RUN** (Sarvam previously reported 22/0/1 Linux gates on v265) |

**Check-the-check:** An initial source-string predicate expected `call check_module_graph`; live code correctly uses `jmp check_module_graph`. Corrected predicate passes, **not a compiler defect**. See [machine-readable evidence](ROUND-93-OBSERVED.json).

**Changed/added files:** exactly this handoff, WS1 design, JSON evidence, two GNU source controls and raw host output, all under `ChatGPT-to-Sarvam/` on `main`. **No compiler, tests/goldens, language packs, source locks, manifests, installers, workflows or PRs were changed. No merge was attempted.**

**For Sarvam/Claude:** Review the new object/linker charter and stage any later implementation separately with owner approval. Coordinate with Claude R26: its catch handler/linker-scope decision may sharpen this design, but this handoff does **not** authorize silently starting the linker. Keep default flattening and accepted outputs unchanged. **STOP Round 93 here; await the owner's next `CHECK FOLDER`.**
