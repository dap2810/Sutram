# ROUND-173 — the eleven read as one (read-only)

**Base:** main at v315 · **Tip:** v326 `702d801c` (branch `r192-paused-books-and-avaroha`) · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing compiled or run.** Every claim below comes from reading the code, the library, the books, the reference, and the handoffs, and from `git diff` between the trees. All line numbers are re-grepped on the v326 tree; nothing is carried from a brief or a handoff.

The chain is 22 commits, linear, forked from main at `112838ce` (the version string there reads `Sutram 1.0 (v315)`; the R154 commit `308c2161` also carries the v315 string but is an ancestor, and using it as the base would fold main-side R167 work into the diff). The fork point is `112838ce`.

```
v316  59d60353  → v317  501d35fd  → v318  c1f516f8  → v319  4c1159be  →
v320  9bb059ea  (+ docs fe90a9b1) → v321  c0fdebe8  → v322  602b1f10 (AUDIT-01) →
v323  25b247b3  → v324  b180bda4  → v325  d855b9dc  → v326  c744fc98
(+ ec57c197, 702d801c; docs and one test only)
```

Full diff `112838ce..702d801c -- src/ lib/`: **8 files, +1723/−81.**

```
lib/brihat.smlib        |    2 +-
lib/ganit.smlib         |    8 +-
lib/vakyank.smlib       |   31 ++
src/r11_sandesh.inc     |   22 +-
src/r163_same_file.inc  |  328 +++++++++++
src/r28_object.inc      |    3 +-
src/r65_arena.inc       |   29 +
src/sutram_compiler.asm | 1381 +++++++++++++++++++++++++++++
```

---

## Task 1 — the whole chain, read as one diff

### 1. Interactions found

**I-1. v321's refusal × v325's guard change — a validation-order interaction (safe as code, a real gap in what was checked).**
v321 added a new refusal, `E_AGYAT_AKSHAR` (`r182_unknown_char`, `src/sutram_compiler.asm:12598`, reached from the lexer). v325 changed no lexer code — its compiler diff is only the `rfx_check_likha` comment — but it changed the guard itself (`tools/guard_pair.py`): before v325 a refusal counted as REFUSED-SAME on exit code alone ("neither wrote an output, with the same exit code"); after v325 it requires both exit 1 with no output **and** matching normalized stdout/stderr ("both exited 1 without output, with matching normalized stdout/stderr"), and IDENTICAL now requires exit 0. So v321's new diagnostic was gated under a guard that could not see diagnostic text at all; only the v325+ guard can. v321's diagnostic was checked by its own gate (`R182 unknown character`, 21 checks) but never by the guard until v325. The same applies to v322's four new refusal messages (`E_AVARTAN_VINA`, `E_KOSH_SATYA`, `E_MALA_LIKHA`, `E_MALA_PARIMAN`). A second v325 guard tightening, also relevant: before v325 two compiler *timeouts* counted as REFUSED-SAME (both sides no output, equal return codes); after v325 a timeout is DIFFER. No code interaction: the lexer refusal runs before parsing, so a program carrying both an unknown character and an AUDIT-01 defect is refused by the lexer first, deterministically, in any merge order.

**I-2. v319's hoist × v320's clearing — SAFE (the range trace is in §3 below).**
No shared code: the hoist lives in `src/sutram_compiler.asm` (`r172_*`/`r175_*`), the clearing in `src/r65_arena.inc` (`r175_emit_zero_to_mark`, `:437`). The only shared surface is the arena, and the ranges are disjoint (see §3).

**I-3. v323's function × v325 — NO interaction; the brief's example misattributes.**
v323 added `vartani_grahan` / `nivesha_anta` (BN 48/49; `.ge_call_vgrahan` `:25029`, `.ge_call_nivanta` `:25084`). v325 changed neither the function nor its documentation: v325's compiler diff is only the `rfx_check_likha` comment, and v325's reference diff does not touch the `vartani_grahan` row or §4d's table — it touches only the `grahan` row (in the §4 function table) and the status headers. The function v325's reference rows actually touch is `grahan`, the function **v324** rewrote. See brief corrections.

**I-4. v324's grahan rewrite × v325's reference rows — SAFE, and accurate.**
v324 rewrote `grahan` as the `R186_GRAHAN_TAIL` macro (`:1133`, tails `:1182`/`:1187`): sign from a `-`/`+` before the first digit (last one wins), an unfinished last line returned with its sign, `-1` only when no digit was read, and `edx = 1` at end-of-input so the code after the tail sets `nivesha_anta`. v325's reference row for `grahan` adds exactly what the rewrite does — "read one line and make a number of its digits… with a sign before the first digit (v324); **past the largest `vitti` it wraps, with no message**" (`docs/LANGUAGE-REFERENCE.md:183`) — and the wrap note matches the tail, which has no overflow check (`imul r8, r8, 10; add r8, rdx`). No conflict.

**I-5. v323 × v324 — HARD dependency (the real interaction in the input story).**
v324's `.ge_call_grahan` calls `r184_ensure_flag` (`:23698`) and its post-tail code stores through `r184_gidx` — the hidden module `vitti` `0nivesha_anta` that **v323** defines (`r184_ensure_flag`, `:11689`; `r184_gidx` `:11685`). Without v323, v324 does not assemble. The dependency runs one way: v323 does not use anything from v324.

**I-6. v317–v319 hoist × v322 AUDIT-01 mala checks — SAFE, and the order inside the mala declaration matters and is right.**
In the mala declaration generator the emitted code runs, in order: `a1_mala_len_check` (v322, `:20471`) → `r173_mala_begin` (v318, `:11175`) → allocation → `a1_mala_got_check` (v322, `:20495`) → `r172_decl_end` (v317). On a reuse pass `r173_mala_begin` jumps to `.have`, skipping the allocation **and** `a1_mala_got_check` — correct, because no allocation happened and none can fail — but `a1_mala_len_check` sits before the jump, so the length is still checked every pass (it is re-evaluated every pass and a different length correctly forces a fresh allocation). The kosh declaration has the same shape: the capacity check runs every pass, `r172_decl_begin` (`:11130`) jumps past the allocation on reuse. No defect.

**I-7. v317 hoist × v326 R190 warning — SAFE, adjacent in the same function, independent.**
Both touch the `chakra` generator: `r172_for_enter` is called at `:21341`, the R190 warning block at `:21370–21399` (`.r190_quiet` at `:21399`). The warning fires on shape (start not a number, end a number) whether or not the loop's kosh are hoisted; the hoist does not change the direction decision. One wart, not an interaction defect: the warning fires on shape, not values, so `chakra i = n tak 5` with `n = 3` — which counts up correctly — is warned about too (pinned by the R190 gate test as `variable-to-number-up`, `tests/r190/test_chakra_and_converter.py:40`).

**I-8. v316 output/input separation × everything else — SAFE.**
`r163_out` (`:33859`), the `os_open` read-hook (notes every file opened for reading by identity), and the `_start` root-open are the only v316 code paths; no other branch adds a compiler file-open or an output path. `r163_open_out` uses a raw syscall, not `os_open`, so an output is never noted as its own input. The 256-input cap (`R163_CAP`) is shared with no other branch. The `--debug` path that ran past the cap in the first staged build (542 opens of three files for `examples/import_demo.sm`) is outside the guard, which "compiles the ordinary way only" (CHANGELOG v316) — a named limit, not an interaction.

**I-9. v320 zeroing × v326 `vartani_tak_ank`'s mandapa — SAFE.**
`vartani_tak_ank` (`lib/vakyank.smlib:148`, added v326) allocates its scratch `nirmmita(32 * 8)` inside a `mandapa`, converts, and returns `r` — which lives in a variable, not in the scratch. The mandapa's exit zeroes the scratch after the conversion is done; nothing after the exit reads it. The `ok[0]` write goes through `okp` to the caller's mala (persistent side).

**I-10. v321 lexer × v323/v324 new builtins — SAFE.**
The new names (`vartani_grahan`, `nivesha_anta`, and their Devanagari spellings) lex as ordinary identifiers/keywords; the refusal never fires on them. Strings are scanned as units (`.lex_string`, `:7551`) and `#` / `/* */` comments are skipped before the operator fall-through where the refusal sits, so the refusal never fires inside a string or a comment. The BOM carve-out (EF BB BF at the start of the text or of a line) is the only exception.

**I-11. v319 hoist × v320 zeroing, second facet — v319's published timings predate v320 and were not re-measured.**
v319's measurements (800,000 passes; a `kosh` in a `mandapa` inside a loop 50,012 → 16–20 KB, 18–20 → 8.2–9.5 ms) were taken without v320's per-exit zeroing. The zeroing zeroes `[end, mark)`, i.e. only scratch taken inside the block that pass; for the pure hoist shape (a proven-local kosh/mala in a mandapa, no scratch allocation per pass) `end == mark` at the exit and the zeroing is a no-op (`jbe .none`), so the memory numbers stand and the time numbers are at most a few instructions per pass worse. The numbers were not re-measured on the combined tree; the interaction is benign but the v319 timings are stale as stated. No defect.

**I-12. v322 fall-off × v324 grahan — SAFE.**
`a1_emit_fall_off` makes a `prakriya` that falls off return 0. A `prakriya` that calls `grahan()` and falls off now returns 0 rather than whatever `rax` held — that is v322's intended behaviour, and it does not touch the `nivesha_anta` flag (set by the `grahan` call itself).

No other pair shares a file, a line, a global word, or a test file. The `r11_sandesh.inc` version string (`v315` → `v326`, 11 languages × 2 lines) is touched by every branch mechanically and is the "22 lines" in every per-branch diff. Shared globals: the `r172_*` tables are extended linearly by v317 → v318 → v319 (no conflict); `r184_gidx`/`r184_gset` are defined by v323 and used by v324 (I-5); `r175_z1`/`r175_z2` (v320, `r65_arena.inc:339/343`) are touched by no other branch.

### 2. Order-dependence

HARD — a different order produces a different (or unbuildable) compiler:

1. **v324 depends on v323** (I-5): `grahan`'s tail calls `r184_ensure_flag` and stores through `r184_gidx`. Merging v324 before v323 breaks the build.
2. **v318 depends on v317, v319 depends on v317+v318**: v318 extends the `r172_*` machinery (`r173_mala_begin`, the scan's mala branch); v319 rewrites `r172_decl_begin` (R82 stamp) and adds `r175_walk`/`r175_while_enter`. Without the earlier branches the later ones reference code that does not exist.
3. **v326's books and examples depend on v323**: examples 360/361/363/364 and the books' input sections call `vartani_grahan()`/`nivesha_anta()`. Merging v326's docs/examples before v323 leaves the taught programs uncompilable (undefined function). The lib part (`vartani_tak_ank` itself) is order-free — it takes a string and calls only pre-existing `varna_tak_ank`/`akshar`/`vartani_aayam`.
4. **v325's reference rows depend on v324 and v321**: the `grahan` row describes v324's sign/unfinished-line/wrap behaviour, and the status header names v321's unknown-character refusal. Merging v325's docs first makes those rows false. (v325's compiler change — a comment only — is order-free.)
5. **v325's guard change vs v321/v322 — validation order**: the guard compares refusal diagnostics only from v325. If v325's guard had merged first, v321's and v322's new diagnostics would have been guard-checked at their own gates instead of only by their gates. The code outcome is the same either way; what was *validated* differs.

NOT order-dependent (checked, no dependence):

- **v320 vs v317–v319**: the zeroing is arena-only and does not reference hoist slots; the hoist works with or without it (v317–v319 were gated before v320).
- **v321 vs v322**: both add refusals, but lexing always precedes parsing, so the lexer refusal wins deterministically in any merge order.
- **v322 vs v318**: `a1_mala_len_check`/`a1_mala_got_check` wrap the mala allocation, not the hoist hook; they are valid with or without v318.
- **v326's warning vs v317–v319**: the warning and the hoist entry are adjacent in the `chakra` generator but neither reads the other's state.
- **v316 vs everything**: no other branch touches an output path or adds a compiler file-open.
- **v325's library fixes vs everything**: `laghuttam_samapavartya` and `brihat_ank_tak_laghu` contain no loop with a kosh/mala declaration, so the hoist cannot touch them; they call only pre-existing functions.

### 3. The check-first question: does v320's clearing interact with v319's hoist?

**Verdict: SAFE.** The ranges are disjoint by construction, and every shape traced stays disjoint.

The trace. `r175_emit_zero_to_mark` (`src/r65_arena.inc:437`) zeroes `[end, mark)`: `push rax` (the mark); `mov rcx,rax`; `mov rax,[end]`; `sub rcx,rdi`; `jbe .none`; `shr rcx,3`; a plain loop up to 128 qwords (1 KiB), `rep stosq` above. It is called from exactly two places, `r73_gen_rewind` (`:415`, call at `:422`, a mandapa's ordinary exit) and `r73_gen_ret_rewind` (`:563`, call at `:574`, leaving through `nivartanam`/`prasar`). `end` is the scratch cursor: it starts at `sima` (base + 1 GiB), moves down only by 16-aligned amounts (`r73_gen_scratch_nirm`, `:451`: `lea rdx,[rsi+15]; and rdx,-16; sub rax,rdx`), and moves back only to a mark, which is a snapshot of `end`. So at every exit `mark - end` is a multiple of 16 and the qword loop covers `[end, mark)` exactly — no partial tail.

Where hoisted allocations live:

- **Hoisted kosh descriptor + first elements — persistent side.** The kosh declaration generator calls `r108_kosh_alloc` (`:20401`), which records an open-block kosh in the `r108_bk_*` tables when declared in a mandapa and then jumps to `r101a_emit_kosh_alloc` (`:9212`), whose first instruction (R127) is `jmp emit_nirmmita_from_rax` (`:9213`) — one ordinary **persistent** allocation (`emit_nirmmita_from_rax`, `:27901`; `cur` grows up from the arena base). The call-site comment "in a mandapa, a slot of the block's arena" is stale: since R127 the allocation is persistent in both cases. The R82 header (40 bytes, written by `r82_emit_kosh_header`) and the v319 reuse stamp (`mov [rcx-24],rdx` in `r172_decl_begin`, `:11130`) are in the same persistent allocation.
- **Hoisted kosh grown past 4,097 elements — a 64 MiB region.** Growth past 64 KiB of elements (`R127_BIG`) moves the elements to a separately reserved region (`r127_emit_grow`); the descriptor stays persistent. A region is not in the arena at all, so it cannot be inside `[end, mark)`.
- **Hoisted mala elements — persistent side.** The mala declaration generator calls `emit_nirmmita_from_rax` directly (after `a1_mala_len_check` / `r173_mala_begin`); the header (length) is at the allocation base, the user pointer is base + 8. A mala is never given back at a block exit — that is why the hoist's reuse path zeroes its elements itself (`rep stosq` in `r173_mala_begin`, `:11175`).

The zeroed range `[end, mark)` is always at or above the current scratch cursor, hence at or above `cur`; every hoisted allocation is below `cur` or in a separate region. Disjoint.

Shapes traced concretely:

- **Hoisted kosh declared inside a mandapa inside a loop (v319's widening).** Still persistent (above); the mandapa's exit zeroes only scratch taken inside that mandapa that pass. The descriptor survives in the frame slot (`[rbp+slot]`, set by `r172_decl_end`, `:11215`) and the next pass finds it and resets `[rcx-16]` (length) to 0. SAFE.
- **Hoisted mala declared inside a mandapa inside a loop.** Its elements are persistent, so the mandapa's exit zeroing does not touch them; the hoist's own reuse zeroing (`rep stosq`) is what clears them, as before. SAFE — the two zeroings are idempotent with each other and touch different memory.
- **A block exit inside a loop body.** The zeroing covers scratch taken since that block's entry mark. A hoisted allocation made *before* the block was entered sits above the mark (scratch grows down) and is outside the range; a hoisted allocation made *inside* the block is persistent and outside the range by side. SAFE.
- **Nested blocks.** Each exit zeroes `[end, mark)` for its own mark and restores `end` to it; the ranges nest, they do not overlap a hoisted allocation. SAFE.
- **A hoisted kosh that grew to a 64 MiB region.** The region is a separate reservation; the descriptor stays persistent. Neither is scratch. SAFE.
- **The hoist's own assumption.** `r172_decl_begin` reuses a kosh "with nothing zeroed, because nothing past the length can be read" — that assumption is about bounds-checked reads, not about stale bytes, and v320 does not change persistent memory. No assumption is violated.

One boundary, stated for precision: the zeroing covers every exit that rewinds — ordinary exit (`r73_gen_rewind`), `nivartanam` (`r73_gen_ret_rewind`, both value and no-value forms), `krama`/`agrim` leaving blocks (`r73_wrap_jump`, `:8533`, wraps the jump in an `AST_REWIND` that rewinds), and `prasar` inside a mandapa (`r25_gen_prasar`, `src/r25_phal.inc:178`, rewinds "as nivartanam does"). A `nivartanam` in `mukhya` exits the program without rewinding, and `sthagita` exits the program — both unobservable, nothing can read the memory afterwards. `r65_active` returns 1 on ELF and PE alike (unless `GUARD_PAGES`), so the clearing applies on both platforms; the "Not Linux ELF: nothing" comment in `r73_gen_rewind` is stale.

### 4. Does anything in the chain assume the arena layout v320 changed?

v320 changed no layout — it changed the *contents* of scratch memory at a block's exit (zeroed instead of stale). I checked every place in the chain that touches the arena:

- `cur` / `end` / `sima` / marks: `r65_emit_nirm` (persistent bump, `cur = align16(cur + size)`), `r73_gen_scratch_nirm` (scratch bump, 16-aligned), `r73_gen_rewind` / `r73_gen_ret_rewind` (store mark into `end`), `r65_emit_kosh_extend` (growth), `parimana()` (counts `(cur - start)` + `(sima - end)` + regions — sizes, not contents). None reads scratch bytes after a block exit, and none assumes stale data. The one piece of code that *did* rely on stale data was the pinned test `tests/r73_scratch/blind_kosh_via_call.sm` (a scratch address kept through a `prakriya`, printed 99 — the next block's data — and now prints 0; its comment reads "Up to v318 it printed 99"); v320 updated its comment to pin the new behaviour, and the reference §19 and both books were updated in R181 to say a block's memory is cleared. The chain corrected its own stale-data assumption.
- `r73_gen_scratch_nirm` zeroes a fresh scratch allocation at allocation time (`r73_s6`); it assumes the memory may be reused, so it zeroes either way — v320's exit-zeroing makes that zeroing redundant for block memory but the code assumes neither.
- The v320 comment's claim — "the cursor moves back only in `r73_gen_rewind` and `r73_gen_ret_rewind`, so zeroing in these two covers every way out; a way out that did not rewind would keep the memory, and nothing could reach it" — holds on the v326 tree: the only stores to `end` are the initialisation (`r65_emit_nirm` / `r73_emit_reserve`, setting it to `sima`), the scratch bump (down only), and the two rewinds (back to a mark). The only non-rewinding exits are program exits.

**Nothing in the chain reads wrong when the eleven are taken together that was right alone**, with two qualifications that are not defects: (a) v319's published time measurements predate v320's per-exit zeroing (I-11); (b) the v321 refusal is undocumented in the reference (see Task 3, v321), which v325's "Tier 1 reference rows" fix did not add.

---

## Task 2 — the guard's blind spot

**What the guard compares.** `tools/guard_pair.py` (v326, 87 lines): for each program in `examples/*.sm`, `examples/*/*.sm`, `tests/stdlib/*.sm`, `tests/r*/*.sm`, `tests/r*/*/*.sm` of NEW_TREE, it compiles the program once with OLD_COMPILER (from OLD_TREE as working directory, so `yoj` finds that tree's `lib/`) and once with NEW_COMPILER, and compares:

- **IDENTICAL**: both exited 0 and wrote byte-identical output.
- **REFUSED-SAME**: both exited 1 without output, with matching normalized stdout/stderr (only the output path and the tree root are normalised; every other diagnostic byte matters).
- **DIFFER**: anything else.
- **NEW**: the program does not exist in OLD_TREE — printed and skipped, never compiled by the old compiler at all.

It never runs a compiled program (so no stdout, exit code, timing, or memory behaviour of the *program* is compared — only the compiler's exit code, the compiler's diagnostics, and the compiled bytes), never passes `--ffi`, `--debug`, `--check`, or any other flag, and runs ELF and PE only (PE under Wine per the changelog). The corpus on v326 is **788 programs** (349 examples + 439 tests), counted by glob on the tree — matching the brief.

The per-branch guard lines recorded in `docs/CHANGELOG.md` are: v316 0 DIFFER; v317 0 DIFFER (783 programs); v318 0 DIFFER; v319 0 DIFFER; v320 **38 DIFFER** (exactly the programs containing a `mandapa`); v321 0 DIFFER (587 + 196); v322 **84 DIFFER** (bytes only; 503 identical + 196 refused); v323 0 DIFFER; v324 **7 DIFFER** (the grahan programs; 582 + 196 + 2 new); v325 differs only where a program brings in `ganit` or `brihat`. The brief's whole-chain line (788 / 592 / 196 / 0) is addressed under brief corrections.

### Blind-spot shapes (each verified against the corpus, counted where I could)

**S1. A program that only behaves differently past a size the corpus never reaches.**
- *Kosh grown past 4,097 elements (the 64 MiB region path, `R127_BIG`).* **0** corpus programs declare a kosh with capacity ≥ 4,097; **0** have a `chakra 0 tak N` with N ≥ 4,097. Hides: the hoist's interaction with region growth (a hoisted kosh that grows past 4,097 elements mid-loop takes a region and its descriptor keeps pointing at it), and the region path generally (v317–v319, and the v320 zeroing's irrelevance to regions). The hoist's gate covers growth to 20,000,000, but the guard does not.
- *Mandapa nested past 32 depths (the marks table).* Max nesting in the corpus is **3**. Hides: v320's zeroing at deep nesting, and the `r108_bk_*` / `r73_marks` 256-entry tables. Any of v317–v320.
- *A program with more than 128 prakriya (`FUNC_DEFS_CAP`, `:54`).* Max in the corpus is **33** (`examples/321_r109_kosh_long_chain.sm`); one program has ≥ 20. Hides: nothing in the eleven directly (no branch touches the cap), but it is the shape the task named — absent.
- *A source past the 64 KiB expanded-source cap.* Exactly **one** corpus program is over 64 KiB by file size (`examples/105_block_nesting_capacity.sm`, 70,422 bytes); the cap is on *expanded* source (after `yoj`), so a program with many imports could exceed it while every file is small — no corpus program tests that shape. Hides: v316's `_start` root-open and `r163_note` accounting under many inputs (the 256-input cap bit the `--debug` path once already).

**S2. A program refused on one side and compiling on the other — and, since v325, a refusal whose diagnostic text changed.**
- *A new refusal v321 added.* **0** corpus programs contain an unknown character outside a string or comment (26 em-dashes in the corpus are all inside strings/comments; **0** programs carry a BOM). So no corpus program exercises `E_AGYAT_AKSHAR` in code position, and none exercises the BOM carve-out. Hides: v321 entirely (its 21-check gate is the only cover), and the carve-out specifically.
- *Refusal diagnostics generally.* Before v325 the guard did not compare them (I-1). Hides: v321's message (code point, caret, hint) and v322's four new refusal messages, at their own gates; only the v325+ guard compares them.
- *A change correct for every program that compiles but wrong for one that is refused.* The guard's REFUSED-SAME compares normalized diagnostics, but a refusal whose *position* is wrong (wrong line/col, wrong caret) is compared only if the program is in the corpus — and the corpus's refused programs are the 196 that were already refused. A new refusal on a shape the corpus lacks (S2's first bullet, S6) has no baseline.

**S3. A change that alters only timing or memory.**
- *The hoist's resident size and time (v317–v319).* **0** loop bodies in the corpus contain a kosh or a mala at all — checked by brace-matching every `chakra`/`yavat`/`kuru` body in all 788 programs; the changelog's v317 line says the same for `chakra` ("40 of them contain a `chakra`, none declares a `kosh` in one"). 22 files contain both a loop keyword and the word `kosh`, but in every one the kosh is declared outside the loop (e.g. `examples/353_r127_muse_loop.sm` declares `kosh k[4]` before its `yavat`; `examples/286_r82_kosh_in_mandapa.sm` declares its kosh in the mandapa, with the `yavat` a sibling statement after it, not around it). The guard compares compiled bytes, which the hoist does not change for programs without the shape, and never measures memory or time. The hoist is validated only by its gates (24 + 12 + 16 checks). This is the chain's largest validation gap.
- *v320's zeroing cost.* The guard never times a compile or a run. The cost (a block of `nirmmita(64)`: 5.5 → 8.9 ms per 1,000,000 passes, per the v320 changelog) is invisible to it. The one *output* change (blind_kosh 99 → 0) is invisible too, because the guard never runs the program.
- *A region's commit behaviour.* Unreachable for the guard (S1) and unmeasured by it in any case.

**S4. A change that alters only a diagnostic's text or position, or only documentation.**
- *v321's error position.* No corpus program triggers it (S2). Hides: a wrong line/col, a wrong caret, a wrong code point for a multi-byte character, a missing hint.
- *v325's reference-only fixes.* The guard cannot see docs at all. The Tier 1 reference rows, the §6a chakra rule, the books' corrections, and the paused books' notice are all outside it. Hides: a reference row that is still false (e.g. the `grahan` wrap note, the `vartani_tul` row) — only the `R233 verification` and `R158 doc currency` gates look at docs.
- *v326's warning.* The warning goes to stderr at compile time; the guard *does* compare stderr for refused programs, but the warning fires on programs that compile (exit 0), and IDENTICAL compares only the output bytes, not stdout/stderr. **0** corpus programs have the warned shape (`chakra <var> tak <number>`) — the changelog says "None of the 787 guard programs has that shape". So a missing, duplicated, or mis-worded warning is invisible to the guard. Hides: v326's warning entirely (its R190 gate is the only cover).

**S5. A change whose effect needs two features together.**
- *A hoisted kosh inside a mandapa inside a loop with a foreign call (R162's hole).* The guard never passes `--ffi`, and only 3 corpus files mention FFI at all (`tests/r32/main.sm`, `tests/r33/modmain.sm`, `tests/r147/slices/15_ffi_argument.sm`) — and those are compiled by the guard *without* `--ffi`, so the foreign names are undefined and the programs are refused identically on both sides. The R162 hole shape (a block kosh passed to a foreign `ptr` parameter as a bare statement) is never compiled with the FFI on. Hides: v317–v319 (the hoist scan's treatment of a foreign call) and the R162 hole itself, which no branch in the chain closes. Note the hoist scan *does* see statement-path `AST_FUNCALL`s, so a hoisted kosh passed to a foreign function escapes the hoist (fails toward leaking) — but that is gate knowledge, not guard knowledge.
- *A kuru loop with a hoisted kosh (R172's gap).* **3** corpus programs use `kuru` (`examples/260_r71_indented_bodies.sm`, `examples/78_do_while.sm`, `tests/r73_scratch/escape_f2_kuru.sm`); **0** of them mention a kosh or a mala. Hides: v317–v319's kuru gap (a kosh/mala declared in a kuru body is made every pass) — the guard cannot tell a hoisted kuru-kosh from an unhoisted one because no such program exists in the corpus.
- *A hoisted kosh/mala under `yadi`/`anya` in a `yavat` (v319's widening).* Subsumed by S3: **0** loop bodies contain a kosh/mala, so no combination of the widening with any other feature is in the corpus.

**S6. A change that alters behaviour only on Windows (the PE path).**
The guard runs PE under Wine (per the changelog), not on real Windows, and the brief states fifteen versions have never run on real Windows. Hides: anything in the PE-only paths of the eleven — v316's Windows identity check (`GetFileInformationByHandle`, `OPEN_ALWAYS` + `SetEndOfFile`), v324's `R186_GRAHAN_TAIL 5` (the PE tail's computed jump back to the read loop), and v320's clearing on the PE runtime. The `--pe` guard run compares PE *bytes*, not PE behaviour.

**S7. A change that alters behaviour only for a program the corpus never imports, or a builtin it never calls.**
- *Modules.* All **24** `lib/` modules are `yoj`'d by at least one corpus program (`ganit` 47, `varna` 36, `ganita` 29 … `gudh` 1, `patra` 4, `aadhar` 5), so no module is wholly absent. But the counts are thin at the tail, and the v325 fixes sit in `ganit` (47 programs) and `brihat` (15) — covered.
- *Builtins never called by any corpus program.* `paadh` — **0** programs call it directly (example 362 reads a file through `patra_path_sarv`, a lib function). `paadh`'s codegen is exercised only through the `patra` module (4 programs `yoj patra`). Hides: v324's file story at the builtin level (the `dvaram`/`paadh` row correction in v325 is docs-only; the builtin itself is pre-existing, so the exposure is small). Every other builtin the eleven touch is called: `grahan` 9 programs, `vartani_grahan` 4, `nivesha_anta` 2, `vartani_tak_ank` 1, `kosh_kship` 109, `nirmmita` 248.
- *The new programs are NEW.* Examples 360/361/362/363/364 — the only programs exercising v323/v324/v326's new features — were added inside the chain, so a guard run of the whole chain against v315 reports them NEW and never compiles them with the old compiler. The guard's 0 DIFFER says nothing about them. (The v324 run recorded 2 new; the v326 run's arithmetic is addressed under brief corrections.)

---

## Task 3 — the eleven descriptions

- **v316 "outputs never overwrite inputs" — ACCURATE, with named exceptions.**
  The mechanism matches the code (`r163_same_file.inc`: identity by device+inode / volume+file-index, output opened without truncation, compared, then cut; fail-closed on unsure; the compiler, the linker, and both object readers use it; `E_NIRGAM_PATRA` for an unopenable output). The reference §7 names the exceptions the one-liner omits: the shell emptying a file before the compiler starts, the REPL/IDE fixed scratch files, a write failing part-way. The exceptions are documented where the behaviour is described, not hidden.
- **v317 "a kosh in a loop's body is made once" — ACCURATE but incomplete.**
  True for a *proven-local* kosh declared as a statement of a *chakra's* own body (`r172_for_enter`, `:10981`, called only from the `chakra` generator, `:21341`). It omits both qualifiers: a kosh that escapes (second name, argument of a `prakriya`, slice, `kosh_ksham`, anything the whitelist scan does not know) is made every pass, as before; and a kosh under `yadi`, in a `mandapa`, or in a `yavat` is not made once on v317 (that is v319).
- **v318 "a mala too" — ACCURATE but incomplete, same qualifications.**
  True for a proven-local mala declared as a statement of a `chakra`'s body, with the same length every pass (`r173_mala_begin`, `:11175`, zeroes the elements on reuse). A different length that pass makes a new mala, as before; a mala that escapes is made every pass.
- **v319 "anywhere in a loop — under yadi, in a mandapa, in a yavat" — OVERSTATED.**
  The three named cases are true (`r175_walk`, `:10997`, descends into `yadi` / `anya` / block / `mandapa`; `r175_while_enter`, `:10988`, for `yavat`). But "anywhere" is false: there is no hoist entry for `kuru ... yavat` — the do-while generator (`.gs_do_while`, `:21987`) calls neither `r172_for_enter` nor `r175_while_enter` — so a kosh/mala declared in a kuru body, or in a kuru nested inside a chakra (which `r175_walk` does not descend into, by design: "a loop inside has its own entry"), is made every pass. The word "anywhere" is the overstatement; the R162 hole is not a counterexample to this line (the scan fails toward leaking for FFI uses), the kuru gap is.
- **v320 "a block's memory is cleared at its exit" — ACCURATE.**
  Every exit rewinds and both rewind sites zero (`r73_gen_rewind`, `:415`, and `r73_gen_ret_rewind`, `:563`, both call `r175_emit_zero_to_mark`, `:437`): ordinary exit, `nivartanam`, `krama`/`agrim` leaving blocks (`r73_wrap_jump`, `:8533`), `prasar` in a mandapa. Qualifications, both unobservable or immaterial: a `nivartanam` in `mukhya` exits the program without rewinding, and the zeroing is qword-granular over `[end, mark)` — exact because `mark - end` is always a multiple of 16.
- **v321 "an unknown character is refused at its position" — ACCURATE, and understated.**
  The refusal carries more than position: `file:line:col`, the character, its code point (`U+XXXX`, five or six digits when needed), the source line, a caret, and a `Sanket` hint from a table when the intention is known (`r182_unknown_char`, `:12598`); a byte that is not UTF-8 is named as a byte (`0x..`, "UTF-8 na asti"); a BOM at the start of the text or of a line is carved out. Gap, not in the description but in the tree: the reference has **no** `E_AGYAT_AKSHAR` section — 0 hits in `docs/LANGUAGE-REFERENCE.md` — the refusal is named only in the status header ("an unknown character is refused") and the CHANGELOG. v325's "Tier 1 reference rows" fix did not add it.
- **v322/v323 "vartani_grahan reads a line; nivesha_anta ends the loop" — ACCURATE as shorthand.**
  `vartani_grahan()` reads a whole line, no length limit (buffer starts at 64 bytes and doubles), strips LF and CR LF, returns an unfinished last line whole, and returns `""` at the end of input (`.ge_call_vgrahan`, `:25029`). `nivesha_anta()` is 1 once the end is found, and stays 1. "Ends the loop" is student shorthand: the flag does not end anything by itself; the program tests it (`yadi (nivesha_anta()) { krama }`, as the books and §4d show). The mechanism is stated in §4d.
- **v324 "file examples; grahan's sign and unfinished last line" — ACCURATE but incomplete.**
  Examples 362 (whole file by path, `patra_path_sarv`) and 363 (file as input, line by line) exist with goldens; `grahan()` reads a `-`/`+` before the first digit (last one wins) and returns an unfinished last number instead of -1 (`R186_GRAHAN_TAIL`, `:1133`). Omitted: the `nivesha_anta` coupling — from v324 `grahan()` sets the flag at end of input, because a typed `-1` is now read as -1 and can no longer serve as the end sign. That is the most consequential part for a student writing a `grahan()` loop, and the description does not mention it.
- **v325 "the audit's fixes: two library defects, the Tier 1 reference rows" — ACCURATE.**
  The two defects, named: (1) `laghuttam_samapavartya` (lcm, `lib/ganit.smlib:86`) — the gcd it calls stopped the program for (MIN, 0), (0, MIN), (MIN, MIN); now an lcm with 0 is 0 and (MIN, MIN) is -1, as for any lcm that does not fit (R233 R16). (2) `brihat_ank_tak_laghu` (`lib/brihat.smlib:71`) — a digit of -1 was accepted (`d <= 9` only) and returned -1; now `d >= 0 && d <= 9`, else the documented `E_MULYA_AYOGYA` (R233 R14). The reference rows I sampled (the `grahan` row, the `akshar` family, `dvaram` opens / `paadh` reads, the braces section, §6a's chakra rule) are corrected as claimed; I did not re-verify all eleven Tier 1 rows in this round. Note: v325's compiler change is a comment only — the compiler's bytes are v324's — which the description does not claim otherwise.
- **v326 "the input story, four book mismatches, the paused books marked, avaroha set out" — ACCURATE on the first three; "avaroha set out" needs its qualifier.**
  The input story is real (§4d's table and the taught `vartani_tak_ank` program, the "Reading text" book sections, examples 360–364). The four book mismatches are real (first program's printed size 97 → 112; "What you need" said Linux "or WSL on Windows" while chapter 17 installs natively, and never said the compiler is the file `sutram_compiler` on Linux; the `grahan()` example was a fragment with `krama` outside any loop, refused `E_AVARTAN_VINA` if typed as printed, now a whole program; the `sutram -i` session numbers 69/216, not 54/201, and `--lang gujarati` answers in Gujarati). The paused books (Hindi, Gujarati, Tamil, Telugu) keep their text and their notice now names the one sentence known to be false (the "Descending Loops" sentence) and what they do not cover. **Avaroha is not a built word**: it appears only in the R190 warning's hint (`r190_msg_b`, `:1010`: "avarohaya 'yavat' likhatu"), in the reference (quoting the warning), in the CHANGELOG ("proposed `avaroha`"), and in `docs/WHATS-LEFT.md` ("Proposed: `avaroha` … Not designed further, not built: a language addition is the owner's"). A student cannot write `avaroha`. "Set out" is accurate read as "set out as a question"; overstated read as a feature.

---

## Task 4 — what a student gets

One concrete capability per change, in the student's terms:

- **v316**: You can no longer destroy your own program by naming it as the output. `sutram hello.sm hello.sm` used to compile, write the binary over your source, and say `Siddh`. Now it refuses (`E_NIRGAM_NIVESH`), your file stays as it was. An output that cannot be opened is an error now (`E_NIRGAM_PATRA`) instead of a false `Siddh`.
- **v317/v318/v319**: A loop that builds a fresh `kosh` or `mala` every pass no longer eats memory and time. The program's output is identical; what changes is that 800,000 passes of a one-element `kosh` go from 37,516 KB resident to 16–20 KB, and the loop from 5 ms to 0.9 ms per 200,000 passes (per the v319 handoff's measurements). A student notices it only if their program was slow or ran out of memory before.
- **v320**: A `mala` or `nirmmita` taken after a block no longer reads the block's old data (a new `mala m[8]` used to read 77 in its first and last number). A student notices it only in the rare program that was reading stale data — a bug they probably did not know they had.
- **v321**: If you type a curly quote, an en-dash, `$`, `@`, an apostrophe, a no-break space, or an emoji, you now get an error at the character — file, line, column, the character and its code point, the line with a caret under it, and a hint ("use `"`", "use `-`"). Before, the character vanished silently and `5 <en dash> 2` compiled and printed 5.
- **v322**: Four new errors you will hit instead of silent wrong answers, and one fixed one. `krama`/`agrim` outside a loop are refused (`E_AVARTAN_VINA`); `likha` of a whole `mala` is refused (`E_MALA_LIKHA` — it used to print the address); a bare `kosh` as a condition is refused (`E_KOSH_SATYA` — every `kosh`, even an empty one, used to be true); a bad `mala` length is refused (`E_MALA_PARIMAN` — `mala m[-3]` used to crash). And a `prakriya` that ends without `nivartanam` now returns 0 instead of whatever the last instruction left (it used to return 15 for `f(5)`).
- **v323**: You can read text. `vartani_grahan()` reads a whole line as a string — the first way to read text at all (`grahan()` only reads numbers, and `hello` gave 0). `nivesha_anta()` tells you when the input has ended, so a loop that reads every line stops at the end and not at an empty line (examples 360, 361).
- **v324**: You can read a file, and `grahan()` works properly. Example 362 reads a whole file by its path and sums its numbers; example 363 counts a file's lines by being given the file as input. `grahan()` now reads `-5` as -5 (before: 5) and does not lose a last number with no newline after it. And because a typed `-1` is now a number, `grahan()` sets `nivesha_anta()` at the end of input — a `grahan()` loop should ask it.
- **v325**: Two library answers are fixed (only if you hit those inputs): `laghuttam_samapavartya` no longer stops the program for a pair with 0, and `brihat_ank_tak_laghu` refuses a negative digit instead of returning -1. And the reference tells the truth in the rows that were false: `dvaram` opens and `paadh` reads, `akshar` works on bytes, the braces section, and the `chakra` rule in §6a.
- **v326**: You get a warning when a `chakra` has the shape of a countdown it will not make (`chakra i = n tak 1` prints a `Sutram suchana` on stderr, the program unchanged), and a converter: `vartani_tak_ank(s, ok)` turns text into a number and tells you whether it was one (`ok[0]`), so `hello` is reported instead of silently becoming 0 (example 364). The books' first program now prints the size the compiler actually prints (112, not 97), the `grahan()` example is a whole program that adds the numbers it is given, and the "Descending Loops" sentence is true. The paused books name the one sentence in them known to be false.

**Worth the risk, per change** (risk = guard DIFFER + interaction surface + merge-order sensitivity):

- **v316 — worth it.** Risk low: 0 DIFFER; identity-based and fail-closed (an unidentifiable output is refused, not written). The only new failure mode is a refusal where the compiler used to write. It prevents the worst failure in the chain — destroying a student's source.
- **v317/v318/v319 — worth it, with the chain's biggest validation gap.** Risk medium-high: ~800 lines of new codegen, a whitelist scan, frame slots, an R82 stamp; its shape is absent from the guard corpus (0 loop bodies in 788 programs contain a kosh or mala), so it rests on its gates alone. The risk is bounded the right way: the scan "fails toward leaking", so a missed case leaks memory as before rather than corrupting anything. The payoff (37,516 KB → 16 KB) is the largest in the chain.
- **v320 — worth it.** Risk medium: 38 DIFFER — every program with a `mandapa` changes bytes — plus a timing cost on every block exit, and one pinned program's output changed (99 → 0). It fixes a silent-wrong-data defect, the 38 DIFFER are accounted for, and the decision (zeroing over the floor) is accepted under the rule as written. Invisible to almost every student, but the defect it fixes was invisible too, and worse.
- **v321 — worth it.** Risk low-medium: 0 DIFFER on the guard, but the refusal is entirely unguarded in code position (no corpus program triggers it) and the BOM carve-out is unguarded too; it rests on its 21-check gate. Silent skipping was a silent wrong answer; the diagnostic is good. The residual risk is over-refusal of a character a student legitimately uses — mitigated by the carve-out and the pack handling, neither guard-covered.
- **v322 — worth it.** Risk medium: 84 DIFFER in bytes (all print and exit the same), and five behaviour changes — a program that compiled before can now refuse, and every falling-off `prakriya` returns a different value. Four of the five close silent-wrong or crash holes (`mala m[-3]` used to SIGSEGV). The fall-off change carries the most risk of the five and the least student-visible benefit (it fixes a return value nobody should have relied on).
- **v323 — worth it.** Risk low: 0 DIFFER; two new builtins, no existing program changes; the cost (≥ 64 bytes per call, never given back) is documented in §4d. The first way to read text.
- **v324 — worth it.** Risk medium: 7 DIFFER; the rewrite is a hand-built macro with one computed jump, and it adds a hidden global to every `grahan` program. Two silent wrong answers fixed, covered by a 24-check gate.
- **v325 — worth it.** Risk low: the compiler's bytes are v324's (a comment only); the library fixes are 2 and 8 lines, guard-covered through `ganit` (47 programs) and `brihat` (15); the guard tightening is pure win. The docs fixes cost nothing.
- **v326 — worth it.** Risk low: the compiler change is a stderr warning only (no program's bytes change); the lib addition is a new function; the rest is docs. The warning's false-positive shape (`n tak 5` warned even when it counts up) is a small cost — it warns on shape, not values.

**The invisible ones, plainly:** v317–v319 are invisible in output (only memory and time); v320 is invisible except to the one pinned program; v325's guard change is invisible to a student entirely (it is a verification tool); v316 is invisible except when it saves your file. All four were worth doing: the hoist and the zeroing fix real defects (runaway memory; stale data read as truth), v316 prevents data loss, and the guard change is what makes the refusal diagnostics checkable at all. What a student would never notice is not the same as what does not matter — but it is worth saying that the two most visible changes in the chain are v321 (a clear error where there was silence) and v323/v324/v326 (reading text, reading files, converting text to a number), and those are the ones a student would name.

---

## Brief corrections

1. **"A guard v321 added and v325 changed" (Task 1 example 1).** As stated this conflates two things. v321 added a *lexer refusal* (`E_AGYAT_AKSHAR`); v325 changed *the guard tool* (`tools/guard_pair.py`) to compare refusal diagnostics. There is no guard v321 added that v325 changed in the compiler. The interaction is real but it is a validation-order one (I-1), not a code one.
2. **"A function v323 added and v325 fixed" (Task 1 example 3).** Wrong attribution. v325 changed neither `vartani_grahan`'s code (v325's compiler diff is only the `rfx_check_likha` comment) nor its reference row or §4d. The function v325's reference rows touch in that neighbourhood is `grahan` — the function **v324** rewrote (I-3, I-4). The real v323 interaction is with v324 (I-5): `grahan`'s tail depends on v323's hidden `0nivesha_anta` global.
3. **The guard line "788 programs, 592 identical, 196 refused identically, 0 DIFFER".** 592 + 196 = 788 with 0 NEW is inconsistent with a v326-vs-v325 run: example 364 (`examples/364_r190_vartani_tak_ank.sm`) is absent from the v325 tip `22466bda` and present from the R190 tip `c3b7b9ef`, so it would be NEW and 787 compared. No file in the v326 tree records a 592-identical guard run (searched `docs/`, `tests/r190/`, `tests/r233/` and the tree). The consistent reading is a run between two v326 trees (e.g. tip vs R190 tip), where the compiler bytes are identical — which validates nothing about the eleven changes. The per-branch guard lines in `docs/CHANGELOG.md` are the ones that carry the validation, and they include accounted DIFFER sets (v320: 38; v322: 84; v324: 7; v325: ganit/brihat). Relatedly, the shared state's "every one reads 0 DIFFER against its parent" is not literally true per branch; the accurate form is the brief's own Task 2 premise, "0 DIFFER across the chain, except the accounted-for sets".
4. **v319's "anywhere in a loop".** Overstated: `kuru ... yavat` is not covered (no hoist entry for do-while). See Task 3, v319.
5. **"Sixty-seven false claims by Sarvam this stretch."** Up from 66 at R172; the 66 → 67 step is the brief's count, not re-derived here.

## Could not determine

- Which two trees the brief's guard line (788 / 592 / 196 / 0) was run between: no guard output file in the v326 tree records it, and the arithmetic rules out v326-vs-v325.
- A full re-verification of all eleven Tier 1 reference rows v325 claims to have fixed: I sampled the `grahan` row, the `akshar` family, `dvaram`/`paadh`, the braces section, and §6a, and all sampled rows are corrected as claimed.
- Anything about real Windows behaviour: the guard runs PE under Wine, and fifteen versions have never run on real Windows (per the brief). The PE-only paths in the chain (v316's Windows identity check, v324's PE grahan tail, v320's clearing on PE) are therefore guard-compared for bytes only, never behaviour-checked on Windows.
- Whether the v319 time measurements hold on the combined tree with v320's zeroing: the zeroing is a no-op for the pure hoist shape (`end == mark` at the exit), so the memory numbers stand and the time numbers are at most a few instructions per pass worse — but they were not re-measured.

## Verdicts

- **Task 1:** Read as one diff, the eleven hang together. The only hard merge-order dependencies are v324 on v323 (`grahan`'s tail needs the hidden `nivesha_anta` global), v318/v319 on v317 (the hoist machinery), v326's books and examples on v323, and v325's reference rows on v324 and v321 — plus a validation-order dependence, in that v325 strengthened the guard (refusal diagnostics now compared) only after v321 and v322 had added the refusals it now checks. The check-first question is **safe**: v320's clearing zeroes only the scratch side `[end, mark)`, while every hoisted kosh/mala descriptor, element, and region lives on the persistent side or in a separate 64 MiB region, so no hoisted allocation can sit inside a range a block clears — traced for the mandapa-in-a-loop shape, nested blocks, and region growth alike, and every exit path (ordinary, `nivartanam`, `krama`/`agrim`, `prasar`) rewinds through one of the two zeroing sites.
- **Task 2:** The guard's blind spots are specific and counted: no loop body in any of the 788 programs contains a kosh or a mala (the hoist is guard-invisible), no corpus program triggers v321's refusal or carries a BOM, no corpus program grows a kosh past 4,097 elements or nests a mandapa past 3 depths, the warned chakra shape occurs 0 times, the FFI path is never run with `--ffi`, and the five new input examples were NEW and never compared against an old compiler.
- **Task 3:** Of the eleven descriptions, nine are accurate (v321 and v324 understated, v317/v318 accurate but incomplete), one is overstated (v319's "anywhere", falsified by the kuru gap), and v326's "avaroha set out" is accurate only as a question — avaroha is proposed, not built.
- **Task 4:** For a student the chain lands as: text can be read, files can be read, a minus sign is read, a countdown-shaped chakra warns, a wrong character is refused at its place, and the books' sentences can be trusted — while the invisible work (the hoist's memory, the block's clearing, the output that can no longer overwrite its input) was worth doing because the defects it fixes were invisible too, and worse.
