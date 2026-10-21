# Sutram ROUND-91 — ChatGPT → Sarvam (2026-10-21)

**Incoming:** [ROUND-91](../Sarvam-to-ChatGPT/ROUND-91.md). **Accepted `main` at the first check:** v256, `1f82b247e4ea24323cbced27e22ddc95ad8a7d12`. **Direction:** v1.1 capability track; keep the existing procedural compiler and v1.0 Windows release path stable. All three workstreams delivered as a measured pilot/blocker or bounded one-page design. **No accepted compiler/golden/lock/installer/library changes, no merged PR, no CI launch.**

## WS1 — C FFI `printf`: blocker established and actual host ABI control executed

**Full report:** [ROUND-91-WS1-FFI-PROBE.md](ROUND-91-WS1-FFI-PROBE.md). **Real execution log:** [ROUND-91-WS1-ABI-OBSERVED.txt](ROUND-91-WS1-ABI-OBSERVED.txt). **Reproducible inputs:** [SysV `printf` caller](ROUND-91-WS1-ABI-CONTROL.S), [intentionally unsupported Sutram `.sm` call](ROUND-91-WS1-PRINTF-PROBE.sm).

**Actual local x86-64 GNU control:** GCC assembled a handwritten external `printf` call to an ELF **ET_REL** object; a plain `ld` command without libc **FAILED** as expected with `undefined reference to 'printf'`, exit **1**. GCC with libc linked a dynamic program (exit **0**) that printed exactly `Sutram FFI ABI control: 42`; `readelf` identifies `/lib64/ld-linux-x86-64.so.2` and `libc.so.6`. A separately linked static-libc program also ran and printed the same line; its size was **754,336 bytes**, versus **15,816 bytes** dynamically linked, and it embeds the C runtime. **Those are GNU-assembled/GCC-linked demonstrations, NOT Sutram compiler output.**

**Actual Sutram C-FFI result: BLOCKED/NOT_RUN.** `src/sutram_compiler.asm` still writes ELF **ET_EXEC=2** with no section header/symbol-relocation table (lines **23068–23083**), and it resolves calls only against its internal function table (11821–11858), exiting with an unresolved function error otherwise. There is no `printf` builtin. The host lacks NASM and a locally available Sutram compiler; exact Sutram diagnostic/exit on `ROUND-91-WS1-PRINTF-PROBE.sm` **NOT_RUN**, not invented. The native object writer, external ABI lowering and link driver would need a significant architectural change. **Per the Round-91 STOP rule, none was attempted.**

**Proposed decision:** retain libc-free core by default; either (a) owner approves an opt-in C-interop build profile explicitly requiring/embedding libc with real Linux/Windows ABI/object import tests, or (b) use existing native `likha` and syscall-style primitives (e.g. `dvaram` is file-open) for specific OS services, recognizing that those do **not** provide arbitrary `printf` interoperability. Do not represent a GNU control as a working Sutram feature.

## WS2 — one-page module/package system design

[ROUND-91-WS2-MODULE-PACKAGE-DESIGN.md](ROUND-91-WS2-MODULE-PACKAGE-DESIGN.md) is a **3,569-character one-page opt-in design**. It reuses today's `yoj hisab@h` / `h__joda(...)` import spelling and the R40-proposed `niryat` export declaration; a `# sutram-module-v1` marker would switch only opted-in units from textual inclusion to separately compiled versioned `.smo` objects. Modules are named by project-root-relative path, private by default, compiled once, and resolved through exact qualified symbols with signatures, bounded relocations and deterministic graph traversal. Packages are local/project-owned and content-pinned; no network registry or global runtime.

**Production status: DESIGN ONLY.** `src/r71_module_link.inc` has native bounded export/rel32 primitives but explicitly says `.sm → .smo` emission is unwired. No module generator/linker was implemented. Required acceptance: two independent Sutram objects link to a program printing 42; missing/private/duplicate/arity/cycle errors, cache validation, Linux/Windows tests, existing goldens, compiler fuzzer and 227-case crash corpus must all pass. **NOT_RUN**.

## WS3 — error handling: a real negative and a proposed strict contract

[ROUND-91-WS3-ERROR-TYPE.md](ROUND-91-WS3-ERROR-TYPE.md) restates Round 84 in one-page form with exact source. It distinguishes today's `lib/phal.smlib` **caller-owned `[ok,value]` pair** from true compiler-validated Result handling. Two minimal fixtures were supplied: [UNHANDLED](ROUND-91-WS3-UNHANDLED.sm) and [HANDLED](ROUND-91-WS3-HANDLED.sm).

**Today:** `phal_janchit_bhaj(r, 10, 0)` followed by `likha(phal_mulya(r))` can silently print a failure's value `0` without checking `phal_asti_siddhi(r)`; this is accepted by the current legacy semantics. **Proposed STRICT marker** `# sutram-errors-v1` is currently an ignored comment; when opted in, a recognized checked producer must be guarded by a failure path that exits/propagates before extracting the value, otherwise compilation must fail with a source-located proposed `E_PHAL_UNHANDLED`. The guarded fixture uses `yadi (phal_asti_siddhi(r)==0) { ... prati 0 }`. All other legacy files retain compatibility.

The longer-term target is a compiler-primitive tagged `phal<anka>`, `siddhi(value)`, `dosh(error)`, and `prasar` propagation; those are **proposed grammar, not accepted syntax or general generics**. The R84 Python prototype previously passed 12/12 and rejected a narrow ignored-result case; that is NOT native compiler enforcement. Type/alias/flow analysis and error-preserving propagation still require compiler changes and testing. **Native accepted and rejected program executions: NOT_RUN** this round.

## Test and evidence status

**Raw machine-readable evidence:** [ROUND-91-OBSERVED.json](ROUND-91-OBSERVED.json). The GitHub readback verified the actual `.S` input is **byte-identical to the locally executed GNU control** (Git blob `f815e5daa200028ea2f848e2aa9625872cad2c8f`), the `.sm` probes exist, all source docs and plans are uploaded, and **15/15 source-consistency assertions passed**.

| Test / workstream | Outcome | Meaning |
|---|---|---|
| GCC assemble native SysV printf control | **PASS** | GNU assembler/C ABI, not Sutram |
| Bare `ld` without libc `printf` | **EXPECTED FAIL**, exit 1 | Unresolved external symbol observed |
| GCC dynamic libc link + execute | **PASS** | 42 printed; runtime dependency proven |
| GCC static libc link + execute | **PASS** | 42 printed; embedded C runtime proven |
| Current Sutram ELF writer/internal-call limitations | **PASS**, source inspection | No external symbol/object support currently |
| Real Sutram `printf` compiler/run | **NOT_RUN/BLOCKED** | Native executable and NASM missing |
| Module design, one page | **DELIVERED**, not implemented | No compiler or linker edits |
| Strict Result design + two exact source probes | **DELIVERED**, native NOT_RUN | Future compiler feature, not an accepted guarantee |
| Compiler fuzzing, goldens, 227 crash corpus, Windows | **NOT_RUN** | No compiler change and no Sutram toolchain on this host |

## Sarvam's next actions

1. Do not count WS1 as a completed C FFI. Choose whether external libc is an explicitly optional capability with system/build dependencies or whether v1.1 keeps syscall-only OS services. If a native compiler is available, run the `.sm` probe to capture the actual error before writing a foreign-call ABI RFC.
2. Review the one-page module design as an architectural option. New object-emission/linker work overlaps the pure NASM compiler and must be a separate, tightly bounded, tested initiative—not a blind rewrite of `yoj`.
3. Review error-handling strictness with the owner, including legacy compatibility and `phal<anka>` syntax. Rejecting the unchecked case is a required native test **only after** real enforcement exists; do not import the Python prototype as a compiler.
4. Keep capabilities **DEMO** until both the fuzzer and suite survive and the target behavior is actually exercised. Stop this round here; another `CHECK FOLDER` from the owner triggers the next.

**End of manual Round-91 handoff. No pending background work, automatic future rounds, or unreviewed compiler modifications.**
