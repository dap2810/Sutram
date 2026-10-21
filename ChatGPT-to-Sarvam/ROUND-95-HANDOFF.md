# Sutram ROUND-95 — ChatGPT → Sarvam (2026-10-21)

**Assignment:** [ROUND-95](../Sarvam-to-ChatGPT/ROUND-95.md), with undelivered [ROUND-94](../Sarvam-to-ChatGPT/ROUND-94.md) portions carried forward. **Read the updated R28 state before integration.** Initial HEAD at trigger: `8dcd3f8cf74fbd008d879ef0e9472ff33cb6fb4e` (changelog v270, compiler v237). **During this review, Claude R28 landed** with compiler **v238**, our own Linux NASM `sutram-link`, object emission, and [actual format](../docs/OBJECT-FORMAT.md); Sarvam separately advanced the documentation to v271. **Do not implement the earlier R93/R95 hypothetical format over R28.**

## WS1 — Byte-level object format: DONE, RECALIBRATED TO LIVE IMPLEMENTATION

[Byte-accurate R95 specification and R28 audit](ROUND-95-WS1-SMO1-BYTE-SPEC.md) describes the **actual shipping-in-source `SUTRAMO1`**:

```text
0:  ASCII "SUTRAMO1"  (8 bytes = 53 55 54 52 41 4d 4f 31)
8:  u64LE code_bytes = C
16: u64LE symbol_count = S
24: u64LE relocation_count = R
32: C native code bytes
    S × {u64LE code_offset, u64LE name_bytes, name[bytes]}
    R × {u64LE displacement_field_offset, u64LE name_bytes, name[bytes]}
EOF exactly; no padding or string pool
```

The linker places the unique object with `mukhya@0` first, then others in argument order, and patches each four-byte displacement as **`target_absolute_code_offset − (site_absolute_code_offset + 4)`**. This single `rel32` representation covers direct E8 call holes and R23 RIP-relative function-address holes; no relocation-kind discriminator exists on disk. Names are unqualified; every definition is exported and duplicates are rejected. There are **no** embedded arities, type signatures or C `ET_REL` records. The R28 format is already implemented at [`src/r28_object.inc`](../src/r28_object.inc) and [`linker/sutram_link.asm`](../linker/sutram_link.asm). **Do not change this already accepted format just to match my prior R93 proposal.**

**Important reconciliation:** I initially wrote an incompatible proposed `SUTSMO1\0` 64-byte header based on Round 93 before observing that R28 had landed concurrently. I **replaced that same GitHub file in place**, verified its new Git blob `966f2f8d7c4e832c9f794ed6cb283e73732a5b20`, and explicitly marked the old proposal superseded. The true byte format is `SUTRAMO1` (32-byte header, u64 fields). **Use R28 `docs/OBJECT-FORMAT.md` as the canonical format.** This is check-the-check and history, not an unresolved format conflict.

**Development-time independent check:** [exact executed Python reference script](ROUND-95-SUTRAMO1-REFERENCE-CHECK.py) and [raw output](ROUND-95-SUTRAMO1-OBSERVED.txt) were **both read back from GitHub with Git blob IDs exactly matching the local executed bytes** (`4b63445f44491c70cf66efc0086122a710ea4ca1` and `b81072d5e0e8fd3f2d54ebc1895d2532d4b6bafe`). On Linux x86-64, Python 3.13.5: **21/21 PASS, 0 FAIL**. Two **synthetic** objects (root=143 bytes, leaf=59 bytes) yielded CODE=76; a patch at code offset 11 was `69−(11+4)=54` (`36 00 00 00`); a synthetic ELF printed hex `34320a` (`42\n`), exited 0, empty stderr. Negative controls cover truncated/invalid metadata, opcode/hole site, missing/duplicate/no-main, and wrong symbol lengths. **The reference checker is stricter than the current NASM linker in some negative cases. These are NOT Sutram compiler or NASM linker execution tests. Python is test-only, never a runtime/build requirement for ordinary users.**

**Claude's R28 independently reports** `tests/r28/test_link.py` **199/199**, **186/186** ordinary examples byte-identical through the opt-in object/link path, default-path **466 byte-identical + 77 identical rejections** versus v237, 22→**23 PASS / 0 FAIL / 1 Windows NOT_RUN** gates, full crash corpus clean. These figures belong to [Claude's R28 handback](../Claude-to-Sarvam/R28-00-HANDBACK.md), **not tests ChatGPT reran**.

**Smallest job vs type-on-variables:** R28's **link-by-name** MVP demonstrably works **without** the 371 annotations. The missing per-symbol **arity/type signature** and private/public namespace for cross-object safety are **not solved**; those require a versioned format extension and reviewed source-language typing decisions. The owner's choice of an **in-project NASM linker** supersedes Claude's R26/R94 interim proposal to use system `ld`. The **ordinary compiler still produces standalone binaries without invoking the linker**; preserve this guard.

## WS2 — R93 relocation experiment, restated in one paragraph

R93 constructed **two independently assembled GNU x86-64 ET_REL control objects**, one raw `_start` caller and one freestanding `sutram_r93_add` function; `readelf -Wr` measured **`R_X86_64_PLT32` at `0x0f`** for the direct call and **`R_X86_64_PC32` at `0x1c`** for `lea ...(%rip)` holding the function address, both targeting the external name with GNU `−4` addends. `ld -nostdlib -static -e _start` linked both without a C runtime, the executable printed **`42\n`**, deliberately exited **42**, and contained **no `PT_INTERP` or dynamic section**; omitting the leaf object **failed** with two undefined-reference diagnostics. Six assertions passed. This proves that external direct calls **and** first-class function addresses have 32-bit RIP-relative holes with **the same target-minus-next-instruction arithmetic**, not that Sutram already supported foreign C or GNU ELF input. R28's custom linker represents the two as named `rel32` holes, but FFI conversion from external ELF objects is **still absent**. [Exact prior raw control](ROUND-93-WS1-RELOC-OBSERVED.txt), [root](ROUND-93-WS1-RELOC-ROOT.S), [leaf](ROUND-93-WS1-RELOC-LEAF.S).

## WS3 / R94 WS1 — Recovery handler review: DONE, WITH EXPLICIT SCOPE

[Independent line-anchored source review](ROUND-95-WS3-HANDLER-REVIEW.md) reads `src/r25_phal.inc` and the compiler's call/handler hooks. **For recognized direct `phal-prakriya` calls**, `r25_check_call` rejects an unguarded call at compile time (or `prasar` on a plain function); `r25_gen_prasar` propagates `rax` + `rdx` status, returning the failure or exiting in `mukhya`; `r26_gen_handle` calls once, writes the value or code to `q`, checks `rdx` and branches into `yadi dosh` failure / optional `anya` success. A handled failure continues and does not bubble upward. **Fail-fast `mukhya` is an acceptable deliberate CLI choice**, but its OS exit uses only the low byte, so `dosh(0)` may look successful and `dosh(256)` exits 0; document/test that contract. Claude's prior native tests show `249` exits 3 while `250` catches and exits 0. **NOT an R95 native rerun.**

**Not the R84 strict mutable Result checker:** legacy `lib/phal.smlib` still allows unchecked `phal_mulya(r)` after failure; no native `E_PHAL_UNHANDLED` strict-flow/alias enforcement. **Known remaining hole:** `r25_check_call` skips phal classification when the callee is an **indirect function-valued variable**, and `yadi dosh` / `prasar` reject such indirect calls. Thus current safety is **for directly named phal-prakriyas**, not all callable phal values. The type-on-variables decision still matters.

## R94 WS2 and R93 unresolved: current state, no duplicate work

R94's system-`ld` object alternative has been **superseded by owner's NASM linker decision** and R28 integration. Separate linking of **Sutram** objects on Linux is **now implemented and prior-test-verified**; do **not** still say all separate compilation is hypothetical. What remains: proper module IDs/visibility and duplicate-import resolution, ABI/arity enforcement, genuine C/ELF foreign object reader and optional FFI, Windows/PE linker, global/data relocations, full strict legacy phal checker, first-class phal indirect-call checking, owner variable-typing decision, and real owner Windows acceptance. R28 specifically does not support `vitti` module globals or C objects. No speculative network/package manager work.

**High-priority source-review hardening to place with Claude (NOT measured native defects):** `linker/sutram_link.asm:169` forms `code_size+32` without overflow-safe subtraction; symbol offsets become final addresses at **412–413** with no CODE bounds check; relocation `field_offset+4` at **447–449** can overflow for malformed u64 offsets and the patch at **455** truncates to `eax` without a signed-range guard; the format has no opcode/hole/overlap metadata and the linker does not verify those bytes. A 16 MiB final image makes genuine in-range rel32 distances safe once all offsets are checked, but a malformed object can supply out-of-range offsets. **These are source-derived risk candidates, not live exploit reproductions**; test malformed native `.smo` on an isolated process before declaring FAIL, then add fail-closed tests and preserve format compatibility. Oracle's negative rejections do NOT mean the actual native linker already rejects them.

## Evidence/status

| Claim | Result |
|---|---|
| WS1 exact implemented byte layout + migration correction | **PASS (source/readback)** |
| WS2 R93 relocation control restated from earlier executed evidence | **PASS (prior host result, not new native)** |
| WS3 direct handler semantics and R84 comparison | **PASS (source/readback)** |
| Current-source predicate audit | **PASS 20/20** after one false checker predicate was corrected; not native |
| Synthetic `SUTRAMO1` byte-level oracle + executable control | **PASS 21/21**, Linux/Python development-time only |
| Current v238 native compiler, NASM linker, Windows and complete gates in this ROUND-95 execution | **NOT_RUN** |
| R28 prior native results | **REPORTED BY CLAUDE**, not independently rerun by us |
| Source/file modifications outside `ChatGPT-to-Sarvam/` | **NONE** |

All deliverables here are explanatory docs, a developer-time reproducible reference checker, its exact raw stdout, and JSON machine evidence **in `ChatGPT-to-Sarvam/` on main**. No compiler, linker, language pack, existing tests, goldens, source locks, Windows build, installer, CI or PR was changed. Every write must be read back and blob-verified; see [ROUND-95-OBSERVED.json](ROUND-95-OBSERVED.json).

**For Sarvam:** The linker is no longer a proposed capability; Claude R28 shipped the first Linux slice. Preserve R28's `SUTRAMO1` as the exact current v1. Schedule independent malformed-input validation + source range/overflow fixes as bounded defensive work; do not conflate a synthetic reference oracle with native acceptance. Await the owner's next `CHECK FOLDER` before assigning new ChatGPT work.
