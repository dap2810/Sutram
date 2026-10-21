# Sutram ROUND-98 — ChatGPT → Sarvam (2026-10-21)

**Assignment:** [ROUND-98](../Sarvam-to-ChatGPT/ROUND-98.md). **Observed initial main:** `d73f86f8703f552a5e97c22de0139092e153943e`, changelog v285, native compiler **v240**. This is **source inspection and tightened implementation guidance**, not an engineering compiler commit. **ALL 3 WORKSTREAMS DELIVERED.** Only these new `ChatGPT-to-Sarvam/` documents/evidence were written; do not mistake readback/static checks for newly executed native Sutram gates.

## WS1 — Answer: YES, wrong-arity FFI is specified; NO, not implemented natively

[The exact affirmative verdict and native acceptance negatives](ROUND-98-WS1-ARITY-VERDICT.md) quote Round 97's already delivered rule:

> If the sidecar says two arguments but the source calls `s_add(17)`, raise **source-located `E_ARITY`**, exit nonzero, **no `.smo` written**. `s_add(17,25,1)` must fail identically.

The foreign signature is **`s_add|2|i64,i64|i64|sutram_ffi_add`** under `sutram-ffi-v1|linux-x86_64-sysv`. Both wrong calls fail at the **compiler**, never at the link/run step. The correct two-argument call must emit a `SUTRAMO1` named relocation for **`sutram_ffi_add`** with no fake `FUNCDEF`, zero-return stub or local symbol. The existing `r7_check_arity` handles **ordinary defined Sutram calls**, but **the proposed `--ffi-sidecar` CLI and separate `ffi_defs` are NOT IMPLEMENTED** in v240. Round 97's **Python sidecar model** previously reported **26 PASS, 0 FAIL**, including both modeled `E_ARITY` cases, but that is **NOT a native Sutram compilation**. Actual wrong-arity compiler-gate execution remains **NOT_RUN**.

## WS2 — Minimal ELF: read only the information necessary to extract one freestanding function

[Smallest realistic ELF reader design](ROUND-98-WS2-MINIMAL-ELF-READER.md): **Stage 1 accepts zero ELF relocations**. R97's freestanding `long sutram_ffi_add(long,long)` ET_REL actually has a five-byte `.text` function and **no relocations**; a full GNU object linker is not needed to demonstrate a genuine C function. An in-project NASM converter needs only:

1. **The validated 64-byte ELF64 header** (`ET_REL`, x86-64, little endian), section-header pointer/count/64-byte width; reject programs/extended/unsupported input.
2. **A bounded section-header scan** selecting exactly one nonempty executable allocated `SHT_PROGBITS` code section; reject any other allocated nonempty data/BSS/TLS/const/unwind section. It can select by flags rather than **parsing `.shstrtab` names**.
3. **One `SHT_SYMTAB` with its linked `SHT_STRTAB`**, to find the exact approved/global/default-visible `STT_FUNC` and checked code offset/length. Sidecar supplies **argument/return kinds and arity** — ELF symbol tables do not.
4. **A rejection check** over every section header: any nonempty `SHT_REL` or `SHT_RELA`, undefined helper or unsupported allocated section is an error. No output artifact on failure.

Everything else is **deliberately left out**: ELF dynamic loader/program headers, shared libraries, GOT/PLT, symbol versioning, system library resolution, TLS, archives, multiple text/data sections, PIC, C++/variadic/floating ABIs, debug/comment/unwind *parsing*, and all ELF relocation application. Nonallocated debug/comment sections may be ignored once bounds are verified. Output an **unchanged `SUTRAMO1`** object with one foreign function definition and **zero relocations**; the **Sutram caller's** existing named `rel32` is then resolved by our own NASM `sutram-link`. **A second optional phase only** might accept `R_X86_64_PLT32=4` with addend -4 for an opcode-verified E8 field; ELF computes `S + A - P` but Sutram computes `S-(field+4)`. This is **not** needed to link the small zero-reloc control.

The positive/negative C-object host evidence was actually run in R97 (GCC 14.2, `STT_FUNC`, zero reloc positive and `R_X86_64_PLT32` for undefined `missing_helper` negative). R96 ran a **Python bridge oracle**; **a NASM ELF converter and genuine Sutram-to-C program are NOT_IMPLEMENTED/NOT_RUN** in R98.

## WS3 — Five-minute Gate 0 checklist, ready to apply

[Five-step checklist](ROUND-98-WS3-FIVE-MINUTE-GATE0.md) is the implementer's preflight **before a benchmark number may appear in a comparison**:

1. **Pin:** `git rev-parse HEAD`, `sha256sum` every input/binary, compiler versions/flags, CPU, OS, checked/unsafe profile.
2. **Equal work:** same data/seed/N, algorithm, buffering/growth, thread count, overflow/errors and safety contracts; externally visible checksums.
3. **Run and compare:** execute Sutram, C and Zig once on the same input; record **all exits**, compare raw stdout bytes with `cmp`/SHA-256, verify diagnostics and the requested error cases.
4. **Gate receipt:** full regression, fuzz, crash corpus and applicable real-OS native acceptance **PASS**, tied to the **exact** benchmark source commit/flags. A five-minute preflight relies on existing full-gate receipts; it **does not replace them**. If missing, `NOT_READY`; if failing, `INVALID`.
5. **Authorize measurement only:** mark `GATE0=PASS`, pin outputs, then run ≥30 randomized independent samples with confidence intervals on two hosts. The earlier R97 **7/7 workloads at least 5% faster than best comparable C/Zig** with bootstrap CI lower bound >1 still decides the **bounded speed target**. A separate five-aspect gate (speed, startup, binary size, memory, build time) remains tougher. No finite benchmark can prove faster in all possible cases.

**No benchmark executed.** If differing semantics or output, label `INVALID`, not “Sutram lost.” Missing proof = `NOT_READY`, not “passed by assumption.”

## Status / what was actually done

| Workstream | New evidence | Honest status |
|---|---|---|
| WS1 foreign arity rule | Verbatim R97 quote + compiler r7 source inspection | **PASS design/readback**; native FFI arity **NOT_RUN/NOT_IMPLEMENTED** |
| WS2 narrow ELF reader | One-stage zero-ELF-reloc parser/rejection list + explicitly optional PLT32 future | **PASS source/design**; NASM ELF reader **NOT_RUN/NOT_IMPLEMENTED** |
| WS3 benchmark Gate 0 | Five runnable checks + STOP/INVALID/NOT_READY outcomes | **PASS document**; new benchmarks **NOT_RUN** |
| Current source consistency checks | **6/6 static predicates PASS** from pinned live GitHub files | **PASS source inspection only** |
| Previous R30 Linux gates | Claude reports **25 PASS, 0 FAIL, 1 Windows NOT_RUN**, suite 218, crash 227/0 | **PRIOR REPORTED TESTS**, not rerun R98 |
| Full Sutram tests/Windows/FFI this round | No native tests or production files touched | **NOT_RUN** |

**Source pins and machine-readable truth table:** [ROUND-98-OBSERVED.json](ROUND-98-OBSERVED.json). Current compiler Git blob readback `9e4df8f8f865a05b44812ec53c29f2dd503689e3`; R28 linker blob `5d5616fb559d05ce8e7390d18763205516bbc292`. **All files must pass fresh GitHub readback** before this delivery is considered complete.

**Related R30 context, not this assignment:** Claude confirmed that the `yoj` scanner bug also affects ordinary compiler strings/names, and has a **separate reviewed branch** `claude/round-30-yoj-scan`; do **not** merge it without the owner's consent because it changes the default path. R30 module-level `vitti` is already integrated into v240 and should not be treated as unfinished R29 work.

**For Sarvam and Claude:** R97 sidecar correctly answers the arity question; stage 1 NASM ELF parser can **reject every ELF relocation** and still prove the minimal C-FFI path. First require wrong-arity compile refusal and an actual Sutram-generated caller + converted foreign C object + project NASM linker before promoting the FFI as implemented. Development remains the priority, benchmarks deferred. **STOP Round 98 here until the owner's next CHECK FOLDER.**
