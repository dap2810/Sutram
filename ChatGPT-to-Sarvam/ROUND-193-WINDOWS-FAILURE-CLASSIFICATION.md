# R193 — Windows failures: evidence before fixes

Source pin: `b7439d8127144ff2f6b6c6b82a571710fc2228fb` (v297 handoff). Read `Windows-to-Sarvam/win-v297-2026-11-03/native-cases.json` in full as JSON; extracted all eight FAIL entries and inspected their examples and relevant emitter paths. No Windows execution performed.

## WS1: classification of every failure

| Case | Observed evidence | Classification and action |
|---|---|---|
| 220_hindi_parse_error | Compilation exits 1 as expected; Sanskrit diagnostic instead of Hindi. Recorded command lacks --lang hindi. | Harness invocation mismatch. Example explicitly requires --lang hindi. Supply that option and rerun before blaming a frozen pack. No pack edits. |
| 288_r86_kosh_alias_moves | Compile/run 0; alias reads 41 while k reads 99, then alias 7 while k stays 99. | Known Windows semantic gap plus Linux-only golden. Example explicitly says Windows still moves. Do not label language alias safety solved on Windows or silently mark the split identity correct cross-platform. |
| 29_nishkriya | Exact expected text, exit 0 instead of 42. | Linux raw syscall example run with a Linux exit expectation on Windows. Its yantra bytes use Linux syscall 60; inline bytes are not portable OS services. Mark target-specific; this evidence does not show an ordinary Sutram exit bug. |
| 303_r103_parimita_refuses | Compile 0, run 0; prints `not reached 499999500000`, expected E_PARIMITA and exit 1. | Real missing Windows budget enforcement. Not an allocation-count mismatch. Reject unsupported budget syntax or implement enforcement; do not accept silent success. |
| 317_r107_parimana | Compile/run 0; every measurement is zero. | Linux golden applied to an explicit PE zero stub. Known capability gap, not a numeric rounding issue. |
| 318_r108_parimana_moves | Compile/run 0; every measurement is zero. | Same PE zero stub; expected dynamic Linux accounting cannot be met. |
| 322_r111_new_names | Compile 0; partial correct output, replacement character before 42, then process exits 3221225477 (0xC0000005). | Runtime access violation and preceding character corruption. Shared operation/lifetime/emission defect candidate, not a compiler refusal or message-only mismatch. |
| 323_r111_old_names | Compile 0 with expected old-name warnings; same output prefix and same exception status as 322. | Same runtime failure. Warning text cannot explain the exception. |

Seven compile successfully; 220 is an intentional syntax refusal whose language selection is wrong. Two cases crash at runtime; the remaining five runtime cases finish with behavior incompatible with the selected golden. This is not eight newly introduced compiler regressions.

### Renames: neither proposed explanation fits

Both spellings map to the same builtin IDs: src/sutram_compiler.asm:814/853 for BN_VARTCAT and :821/856 for BN_CHARFR. Dispatch at :21671–21688 reaches the same emitter labels. Both recorded outputs have code size 3623 and identical failing runtime output; equal size alone is not a binary-identity proof.

The suspicious common paths are:

- `.ge_call_charfr` (:24195 onward) constructs a character buffer on the generated stack, returns its pointer and only partly restores the reservation. Review its lifetime, stack balance, subsequent calls and Windows call-frame use. The bad byte appears at `shabda(anka_akshar(66))` / `shabda(char_from(66))`, before concatenation. Do not infer the original byte from the JSON replacement character; collect raw stdout bytes.
- `.ge_call_vartcat` (:23765 onward) explicitly emits an in-place strcat loop, including `mov [rdi],cl`. The example passes string literal `"ab"` as destination, with no caller-owned append capacity. PE text is RX (:31462); its distinct data section is RW (:31484). Writing a literal in text is a strong access-violation candidate; confirm its actual address and fault instruction with native tracing. Even writable literal storage would not establish spare capacity. The source comment and test expecting concatenation need reconciliation with the public ownership/capacity contract.

The log gives no exception instruction address. These are source-backed defect candidates, not a proven unique crash location. Isolate character construction/output and concatenation into separate probes, then inspect the fault address, section flags and stack discipline. Do not “fix” this by making text writable or accepting corrupted output. No alias-table rewrite is justified by this evidence.

## WS2: the budget refusal itself is missing

The golden asserts a refusal message (including 1048576-byte budget and source line) and exit 1. It does **not** assert 16,384 successful allocations. The program loops one million times allocating 64 bytes and prints only if the loop completes. The observed sum 499999500000 is the full arithmetic sum, confirming completion of that loop.

Source explains the difference: `r65_active` in src/r65_arena.inc:115–123 returns inactive for target_pe. `.r73_ge_scratch` in src/sutram_compiler.asm:23398–23410 consequently takes ordinary allocation instead of `r73_gen_scratch_nirm`. The budget check call is in that skipped scratch path (src/r65_arena.inc:435). Windows allocation reaches VirtualAlloc in win/winrt_blob.asm. Allocator granularity does not explain bypassing the check entirely.

This is a safety-contract gap. Until Windows enforcement exists, an explicit compile-time unsupported-feature refusal is preferable to accepting a budget and ignoring it. A revised test must check termination before the sentinel and the correct failure channel, without weakening the budget promise. Exact counts may additionally test the documented logical accounting policy, independent of physical OS page allocation.

The same `r65_active` decision also explains parimana: `.ge_call_parimana` (:23607 onward) explicitly emits zero on the inactive path. That is an implementation stub, not meaningful Windows memory telemetry.

## WS3: Linux-shaped categories and acceptance policy

| Category | Evidence here / next audit target |
|---|---|
| Allocator/accounting numbers | 317/318 use arena lifetime and exact byte totals; 288 assumes in-place growth. Separate logical contract from OS commitment/reservation and unsupported capability. |
| Raw syscalls and ABI | 29 embeds Linux syscall bytes. Check all yantra examples, register/clobber assumptions, Windows shadow space/alignment and mixed argument types. |
| Invocation and locale | 220 omits a required flag. tools/ide_examples_windows.ps1:139 already has a case-to-language mapping; compare the native harness actually used against that mapping. |
| Diagnostics and paths | Audit absolute paths, separators, line endings, source locations, Unicode decoding and stdout/stderr selection. Normalize only incidental representation; preserve codes, meaningful text and refusal status. |
| Exit status | Distinguish expected nonzero refusal from process faults/timeouts. Store signed/unsigned Windows exception status as raw data; never count any nonzero as success. |
| Filesystem semantics | Permission tests, case sensitivity, missing-file versus access-denied, locked handles and deletion behavior need platform-specific setup and a common logical oracle. These are audit targets, not defects demonstrated by these eight logs. |
| Binary/tool assumptions | ELF headers, executable bits, POSIX paths, shell utilities, /proc and mmap-based tooling cannot silently serve as PE acceptance. |
| Feature availability | Linux-only accounting and alias behavior need explicit capability status, not unexplained FAIL or unconditional PASS. Track accepted, unsupported, known-defect and harness-invalid separately. |

Correct harness inputs first; preserve real defects. Record exact compiler/build/input hashes, target, flags, expected semantics, output and process status per case. A portable test should state its target requirements. Platform-specific tests are legitimate when clearly labelled. Keep unsupported Windows safety behavior visible in readiness totals. Add deliberate Windows acceptance gates through the owner-approved workflow; no automatic CI trigger changes are made here.

## WS4: direct error-handling sort

The sort is worth doing. The complete 55-item reconstruction follows again, inline. It is historical R185 scope, not a fresh v297 census: 40 compile-time, 4 mixed, 2 fatal runtime, 1 conditional fatal runtime, 4 reference-tool diagnostics and 4 placeholders. R190 additionally identified E_RACHANA_GANIT and E_PRATYAHRITA as compile refusals. Do not count placeholder tags as runtime exceptions.

A running program cannot catch a pre-execution compiler refusal. Runtime fatal traps are not currently catchable. Prevent expected failures or use explicit fallible operations before the trap; siddhi/dosh/prasar/yadi dosh already provide result handling. This inventory supports extending fallible APIs; it does not itself require nonlocal exceptions with unwinding.

| Code | Phase | Program response |
|---|---|---|
| `E_ABBREVIATION_VALUE` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_AMBIGUOUS_FIELD` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_ANTARAL_MISHRA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_APARIKSHITA_AHVAN` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_APARIKSHITA_KARYA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_APARIKSHITA_SMRITI` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_ARITY` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_ATIPRAVAH` | compile/tool pre-execution | Literal/constant-expression overflow detected during compilation; use representable constants. Runtime checked arithmetic has its separate result/trap paths. |
| `E_CHAKRA_DASHAM` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_DASHAM_KRIYA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_DASHAM_VITTI` | compile + runtime | Literal/type checks or exact float-to-integer conversion failure. Validate/convert through an explicitly fallible API; no current trap catch. |
| `E_DUPLICATE_NAME` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_EXPORT_UNDEFINED` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_FFI_KIND` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_GAHANATA` | runtime fatal | Recursion-depth protection. Bound recursion/use iteration; do not resume the trapped operation. |
| `E_INTEGER_TRAP` | conditional runtime fatal | R65 checked-integer build path. Use checked arithmetic results to branch; not an ordinary handler event. |
| `E_KOSH_GANIT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_KOSH_MANDAPA` | compile + runtime | Static escape refusal and runtime lifetime/generation check. Repair ownership; never continue using a dead reference. |
| `E_LIKHA_TRAYA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MALA_GANIT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_ALIAS_REUSE` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_CYCLE` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_DEPTH` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_DUP_EXPORT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_INVALID` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_LIMIT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_MISSING` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_NOT_EXPORTED` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MODULE_V1_ALIAS` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_MULYA_VINA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_NIRMMITA_RNA` | compile/tool pre-execution | Negative literal allocation size refuses at compile time; validate dynamic input in a fallible allocation contract, not by catching this code. |
| `E_NIRMMITA_SEEMA` | compile/tool pre-execution | Known raw allocation + constant out-of-range index refuses at compile time. Dynamic analogous bounds use another trap path; validate index before access. |
| `E_PARIKSHITA_STHAN` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_PARIMITA` | compile + runtime | Invalid budget refuses; dynamic budget exhaustion terminates. Bound work; a future fallible allocation must check before mutation. |
| `E_PARSE` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_SCRATCH_ESCAPE` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_SHUNYA_BHAJAN` | compile + runtime | Constant zero can refuse at compile time; dynamic zero stops. Check divisor or use checked phal division before the trap. |
| `E_UNDEFINED_FUNCTION` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_UNDEFINED_NAME` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_UNKNOWN_FIELD` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_UNSAFE_BOUNDARY` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_UTF8` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_VARTANI_CAT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_VARTANI_GANIT` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_VARTANI_SATYA` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_VARTANI_SMRITI` | runtime fatal | String allocation failure. A future fallible allocator could report failure before publication; checking available memory beforehand is insufficient. |
| `E_VARTANI_TUL` | compile/tool pre-execution | Fix source, declarations, verification requirements or build/module inputs; the not-yet-running program cannot handle this diagnostic. |
| `E_EXPORT_COLLISION` | reference tool | Correct build/module inputs; not native runtime recovery. |
| `E_EXPORT_DUPLICATE` | reference tool | Correct build/module inputs; not native runtime recovery. |
| `E_IMPORT_ALIAS` | reference tool | Correct build/module inputs; not native runtime recovery. |
| `E_PRIVATE_SYMBOL` | reference tool | Correct build/module inputs; not native runtime recovery. |
| `E_BAD` | fixture/placeholder | No production operation to recover from. |
| `E_CODE` | fixture/placeholder | No production operation to recover from. |
| `E_OTHER` | fixture/placeholder | No production operation to recover from. |
| `E_TEST` | fixture/placeholder | No production operation to recover from. |

## Verification limits

Read evidence and source only. Windows reproduction, fault tracing, native suite, guard and CI: **NOT RUN — no Windows execution/toolchain used.** Do not claim an independently reproduced fix or accepted installer. No changes to production code, tests, tools, frozen packs or Windows-to-Sarvam. This documentation-only handoff awaits independent implementation and native verification.
