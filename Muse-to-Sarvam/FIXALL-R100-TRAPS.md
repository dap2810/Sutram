# FIXALL: R100 release blockers — patch + verification report

**From:** Muse (Ank) — the Muse side, per the owner's 2026-11-02 "fix all and return to Sarvam" assignment
**To:** Sarvam (for review — this is a PATCH, not a code change to main)
**Base:** `origin/main` 66556f20, compiler v283. The patch is `fixall_r100.patch` (18 files, +757/−68, 46 KiB, applies cleanly onto origin/main — verified with `git apply --check`).
**Status:** All five items implemented, built, and verified locally. Nothing is pushed to main; nothing in this patch is applied anywhere until the owners accept it.

## What R100 blocked, and what this patch does

R100's verdict was NO on v283, with four silent wrong-answer traps plus a silent recursion crash. Each is now a compile-time refusal or a clean runtime message:

| Trap | Before (v283) | After (this patch) |
|---|---|---|
| (a) `likha(a, " ", b)` — variable first, 3 args | prints nothing, exit 0 | refuses: `E_LIKHA_TRAYA` |
| (b) `vitti s = "ab"; likha(s == "ab")` | prints `0` (addresses compared) | refuses: `E_VARTANI_TUL` |
| (c) `vitti u = s + t` on two string variables | prints an address sum, then `shabda(u)` segfaults (139) | refuses: `E_VARTANI_CAT` |
| (d) `vitti x` with no value, function called twice / in a loop | `0 99 99` / `0 50 51` (previous call's leftover) | refuses: `E_MULYA_VINA` |
| Recursion with no base case / mutual recursion | exit 139, 0 bytes | prints `E_GAHANATA`, exit 1 |

New diagnostics are Sanskrit-only strings in `src/sutram_compiler.asm`, outside the per-pack sandesh table (R52 precedent). All new Sanskrit wording is best-effort and awaits native-speaker review — that review is NOT RUN here.

## (a) likha: new builtin `dvaram_likha`, refusal, 57-site migration

**Name decision — `dvaram_likha`, NOT R100's suggested `likha_fd`.** LANGUAGE-PRIORITY is Sanskrit-only until v1.0 and "fd" is an English abbreviation. `dvaram` (door/opening) completes the existing dvaram/band/grahan fd family. Renaming later is one table entry plus one hint string. R100's "existing likh8 family" does not hold: `likh8` is a memory store, and `likha_fd` exists nowhere — a new builtin was required.

- New builtin `dvaram_likha(fd, smriti, sankhya)`, `BN_DVARLIKHA equ 46`: name table entry, arity 3, dispatch arm that is a byte-for-byte copy of likha's raw-write path (result stays in `rax`, so the return value contract is preserved).
- Refusal: `likha` with exactly 3 arguments whose first argument is not a string literal refuses with `E_LIKHA_TRAYA` (`tri-mulya-likha prathamam uddharanam apeksate`, hint: use `dvaram_likha(fd, smriti, sankhya)`). 2-arg and literal-first 3-arg forms are untouched. The codegen raw path in `.ge_call_likha` is left in place (unreachable via the parser once the refusal lands; the builtin is the legitimate path).
- **Migration: 57 `.sm` sites + 2 `.py` sites.** Tree impact was exactly 3 deliberate raw writes in examples+lib (examples/215:76, examples/217:60, lib/patra.smlib:67 — patra's `patra_likh_sarv` USES the return value, so the replacement preserves it) plus 54 sites in tests/ (all `likha(1, buf, len)` except patra's fd variable). `tests/r73_scratch/blind_call.sm:13` (`likha(1, "\n")`, 2-arg) is correctly NOT migrated. `tests/r52/test_r52.py` gains 2 regression checks (trap refuses; `dvaram_likha` writes raw) and `tests/r81_parikshita/test_parikshita.py` renames its case to the new builtin.
- **No separate R54 test matrix file exists** (searched tests/ + tools/). Coverage for (a) is the migrated sites plus the guard run below.
- Parikshita: no checker change needed — `dvaram_likha` falls to the generic refuse in the r81 walk (reason = its own name) = KARYA, same outcome as raw likha. Proven by the migrated r81 test passing (24/0).

## (b)/(c) strings: `==`/`!=` refused, `+` refused except pointer arithmetic

- `==` is broken in EVERY shape on v283 (literals are NOT pooled — `"ab" == "ab"` is 0). Refusal covers every runtime binop plus the three bypasses found by testing (yadi conditions, yavat conditions, and the int-reg decl/assign fast paths). Hint teaches the inverted convention: `vartani_tul` (builtin 17) returns 0 if equal, 1 if not.
- `+` concatenates ONLY for literal+literal (folded at parse time). Any variable operand + any string-ish operand used to add addresses. The rule now refuses string+string and string+non-int, with one deliberate narrowing (see below). Hint for `+` teaches `vartani_cat` (builtin 18, strcat) and warns it has NO runtime capacity guard — the destination must have room.
- Tracking is slot-indexed and flow-insensitive (last-write-wins): a flag is SET on string-literal assignment (decl-init AND reassignment) and CLEARED on numeric reassignment, so `s = "ab"; s = 5; s + 3` correctly runs and prints 8. Flag maintenance covers all paths including the decl/assign fast paths, loop-counter slot reuse (a chakra counter reusing a string variable's slot clears the flag), and function-entry zeroing at both var-table reset sites.
- **Narrowing — string + int is pointer arithmetic, NOT a trap.** The first version of this rule refused any string+int, and verification caught two tree programs it breaks: `tests/stdlib/slices23.sm` (`base + 6`, the khand slice idiom) and `tests/r79_real/report_blocks.sm` (`letters + shreni_varna(total[s]) - 65`, a call offset). The rule now allows exactly one string-ish operand plus an int-like other operand, where int-like = int literal, int variable (neither string-, float- nor kosh-flagged), or any other expression whose result is not dasham (calls, binops, indices — via `expr_is_float`). This supersedes the early probe matrix on `s + 5`, `5 + s`, and `s + x` (all now allowed as pointer arithmetic); `s + t`, `s + "b"`, `"a" + s`, string+dasham, and string+kosh still refuse. The (c) trap itself (`vitti u = s + t`) is still refused.
- **Stated scope limits for (b)/(c):** params, call results, kosh elements, and module globals are NOT tracked for var-vs-var (a LITERAL operand still refuses those shapes); string ORDERING (`<`, `>`, `<=`, `>=`) is untouched (no ordering builtin to redirect to); SUB/MUL/DIV on string operands are NOT refused (same address-arithmetic family — a one-line-extension follow-up needing owner approval); `yadi (s)` truthiness of a string variable is untouched.

## (d) uninit scalars: blanket refusal, zero tree impact

- Mechanism (disassembly-verified): `.gs_decl_noinit` emits NO store, and there is NO prologue zeroing anywhere, for any type. Locals in unsaved registers (r12–r15) leak across calls; rbx is pushed/popped so it does not; stack slots leak in the loop shape. R82's "reads 0 / zeroed locals" note is wrong as a general claim — it is what you observe when the slot happens to be pristine or a restored register; R100's leftover is what you observe otherwise. Both follow from "no zeroing + slot-dependent persistence."
- **Tree census: scalar `vitti`/`dasham` without initializer = 0 in examples+lib** (R100's "handful" guess is actually zero), so blanket refusal breaks ZERO tree programs. The refusal is scoped by construction: arrays route to a separate parser branch (25 decls: 23 write-first safe, 1 call-write safe-by-call, 1 dead — all untouched), kosh decls are empty containers (untouched), and module globals live in BSS/data and read deterministic 0 (untouched; refusing them would change what the r56 fixture tests).
- Message: `Sutram Error [E_MULYA_VINA]: vitti 'x' mulyam vina ghoshita - prathamam mulyam dehi` + `Sanket: ghoshana-kale mulyam likha` (dasham twin likewise). DECL nodes carry no source position, so the message names the variable without a line+caret, like other position-less diagnostics.
- Alternatives rejected: prologue zeroing is insufficient as specified (it would not fix the loop shape, where iteration 2 reads iteration 1's value) and declaration-site zeroing silently redefines a bare declaration to mean `= 0` without teaching the student anything; definite-assignment analysis is disproportionate here (new AST pre-pass, branch intersection, yavat fixpoints, call-write policy) and buys nothing over refusal on a tree with zero occurrences.

## Recursion: prologue guard, Linux-only, threshold pinned by measurement

- Design: the mukhya prologue saves the entry `rsp` into one appended slot (first emitted instruction); every function prologue, right after `sub rsp, 2048`, loads it, computes `entry_rsp - rsp`, and refuses cleanly when it exceeds the threshold. The check fires while `rsp` is still tens of KiB above the true bottom, so the trap's write/exit syscalls (which use no stack) are always safe — unlike a post-fault handler, which is why R100's guard-page-plus-handler option was not taken (it also needs sigaltstack/rt_sigaction emitted from scratch and fault discrimination against the nirmmita PROT_NONE guard pages, for zero extra depth).
- **Threshold: 8,339,456 bytes (8 MiB − 48 KiB).** It sits below every usage ever observed to survive (depth 4020 = 8,365,776 bytes for the probe frame shape), so the guard always fires before the true bottom in every ASLR run. Measured trip point for the probe shape: depth 4007 survives with correct output, depth 4008 refuses — deterministic, where 4020/4030 used to be a flaky survive/crash band. Depths that survive today up to ~4020 will refuse once they cross the threshold; zero tree programs live there (deepest tree recursion is single-digit).
- Message: `Sutram Error [E_GAHANATA]: aahvan-gahanata seema atikram`, exit 1, no line number (runtime check, like variable-form `E_CHAKRA_DASHAM`).
- **Two implementation bugs found by verification and fixed in this patch:**
  1. The first design indexed the slot by `r56_global_count` captured during codegen. That collides: nirmmita registers its allocator globals during codegen (when first emitted), so the count grows after the mukhya save is emitted — the save's slot collided with the allocator's first global (the allocator then saw a nonzero "initialized" flag and skipped its mmap, and the guard read a corrupted slot). The patch instead records the save/check fields in a dedicated patch list and patches them after ALL r56 globals are appended, so the slot lands strictly after everything. Evidence: the nirmmita program that printed `E_GAHANATA` on one call now prints 81.
  2. The trap-message emission loop first used `rcx` as its counter across `emit_byte` calls, but `emit_byte` clobbers `rcx` — the loop ran away into a code-buffer overflow. The counter now lives in a pushed/popped `r12`.
- **Windows: plainly NOT DONE.** PE stack/VEH differ and are untestable from this Linux VM. All new emission is gated on `target_pe == 0` (and non-object mode), and PE output is verified byte-identical between patched and unpatched compilers (same SHA-256). Object mode also compiles cleanly.

## Verification (all with the final patched binary, built from `src/r68_compiler_entry.asm`)

- Suite: **PASS=270, NO-EXPECTATION=4, 0 fail** (exit 1 is the clean signature — `bad` counts the 4 no-expectation items).
- Proofs: **229/229** (`proof_lib.py`), **86/86** (`proof_props.py`).
- Guard (`tools/guard_pair.py`, 680 programs, old tree vs patched tree): **131 refused identically, 549 DIFFER, 0 new, 0 refusal changes.** Every DIFFER is a byte-only difference (both sides rc=0) attributable to the recursion prologue bytes in every function; outputs are proven equivalent by the suite and proofs above. **Guard re-baseline required:** any future guard run against v283 must expect these 549 DIFFERs until the patch is applied.
- r52: **12 checks, 0 failed.** r81: **24 checks, 0 failed.**
- r79 real programs (20,000 students, reference.py as oracle): both compile, both print output **identical to the reference**; memory with blocks 22,016 KB = **62% of** plain 35,456 KB (under the 75% bar). Note: the r79 harness itself needs `/usr/bin/time`, which is absent here — output identity was checked directly and peak RSS via per-process `wait4` rusage instead.
- Trap probe matrix (final binary): (a) variable-first refuses, literal-first prints `a 7`, `dvaram_likha` prints raw; (b) `s == "ab"` refuses, yadi conditions refuse; (c) `s + t` refuses, `s + "b"` refuses, `s + 5` prints the pointer, `"a" + "b"` prints `ab`; (d) two-call and loop uninit refuse, initialized prints 42, global bare decl still compiles and reads 0, array and kosh decls unaffected; (rec) no-base-case and mutual recursion print `E_GAHANATA` exit 1, depths 2000/4000/4007 survive, 4008/4020 refuse.
- PE: byte-identical (see above). Object mode: compiles.

## What this patch deliberately does NOT do (follow-ups, not fixes)

- Installer rebuild (maintainer's Windows step; the v243 package is still stale).
- ChatGPT's R170 memory-design return (awaiting Sarvam routing; not read or audited here).
- `examples/91` + `chakravala` failure path: `chakravala` returns without writing its out-param on one failure path, so a failed call would silently print the previous solution. 91's own inputs succeed, so this is a follow-up, not trap (d).
- A future `mala`-inside-`mandapa` scratch-reuse shape (0 occurrences in the tree).
- Documented behaviours, unchanged: int overflow wraps (§3a), kosh aliasing (§16), dasham overflow to inf (current README sentence), parikshita 0/306.
- Reference updates for owners: §4 raw-write prose should point at `dvaram_likha`; §16/§4a notes should mention the new refusals. Not edited here — docs change on acceptance.

## NOT RUN

Windows (PE recursion guard, installer rebuild, wizard test), browser, native-speaker review of all new Sanskrit strings, direct-to-main application (this patch awaits Sarvam/owner review), R100's unverified 2^63-literal claim (still awaiting a reproducing program; R95's probes contradict it in natural forms).

## Files in this delivery

- `fixall_r100.patch` — the patch (apply with `git apply` onto origin/main).
- `FIXALL-R100-TRAPS.md` — this report.
- `fixall_evidence.json` — the verification numbers in machine-readable form.
