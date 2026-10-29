# R63-00 — The last three items, closed

- **Base:** `main` at `4c55602`, compiler v261. **No source change.** Counts below are from `git grep` on this tree;
  line estimates are calibrated as in R59–R62.

## Item 1 — the word collision: mechanics and price

### What `kshetra` touches today, exactly

| Where | What | Count |
|---|---|---|
| `src/sutram_compiler.asm` | default (romanised Sanskrit) texts: `r5_msg_field` (`:313`), `r7_msg_field_amb` (`:317`), `r5_msg_field_hint2` (`:328`, *"kasyashchid api rachanayah kshetram nasti"*), `msg_rachana_fields_overflow` (`:827`) | **4 strings** |
| `lang/sanskrit.sandesh` | the same four, in Devanagari: अज्ञातं **क्षेत्रम्**, **क्षेत्रम्**, रचनायाः **क्षेत्रं** नास्ति, रचना-**क्षेत्र**-सीमातिक्रमः | **4 entries, active pack** |
| the 10 frozen `.sandesh` packs | 8 of them use the cognate for "field" (Hindi/Marathi क्षेत्र, Bengali ক্ষেত্র, Gujarati ક્ષેત્ર, Kannada ಕ್ಷೇತ್ರ, Odia କ୍ଷେତ୍ର, Telugu క్షేత్రం, Punjabi ਖੇਤਰ); Malayalam uses മണ്ഡലം, Tamil புலம் | **32 entries, frozen** |
| goldens | `tests/expect/106_rachana_field_capacity.out`, `224_unknown_field.out`, `234_ambiguous_field.out`, `tests/sandesh/expect/default/unknown_field.out` | **4 files** |
| tests | `tests/r23/test_capabilities.py:62,66` | **2 assertions** |
| binaries | `sutram_compiler`, `sutram.exe`, `win/sutram.exe` carry the strings | rebuilt anyway |

**Nowhere else.** No identifier in `lib/`, `examples/` or `tests/` is named `kshetra`, so the keyword itself collides
with no program. The collision is in diagnostics only.

### (a) Reword the field diagnostics, keep `kshetra` for the region

**Price:**

| Step | Files | Lines |
|---|---|---|
| 4 default strings in `src/sutram_compiler.asm` | 1 | 4 |
| 4 entries in `lang/sanskrit.sandesh` | 1 | 4 |
| `python3 tools/sandesh.py --write` regenerates `src/r11_sandesh.inc` and the *comment* lines of all 11 `.sandesh` files (each entry is preceded by the default text as a comment) | 12 | mechanical |
| 4 goldens, 2 assertions | 5 | 6 |
| compiler version, pins in the five places | 5 | mechanical |
| **total** | **~24 files, ~15 hand-written lines** | |

**Can it be done without breaking any program? Yes.** The four strings are compile-time refusals. Every program that
compiled still compiles to the same bytes: the guard counts refused programs by exit code, so it reads 0 DIFFER; the
crash corpus checks "errors, never crashes"; no R70 expectation contains the word. **It should ride in the same
version bump as the `kshetra` build, so it costs no pin round of its own.**

**Two things it does not fix, reported:**
- **The 10 frozen packs keep their own word for "field",** and in 8 of them it is the cognate of `kshetra`. A Hindi
  programmer will read *अज्ञात क्षेत्र* for a bad field and write `kshetra` for a region. Frozen means reported, not fixed.
- `--write` touches the frozen pack files, but only their comment lines. The translations are byte-identical. Say so
  in the hand-back when it happens.

**The replacement word — searched in the compiler first, as you asked.** There is **no third word for "field"
anywhere in the compiler today**: the field messages are the only place the concept is named, and `ghatak`
(component) is taken by modules. Of the candidates I checked against `src/`, `lang/`, `lib/`, `examples/` and
`tests/`, these have **zero occurrences** and so collide with nothing:

| Candidate | Sense | Occurrences |
|---|---|---|
| **`anga` / अङ्ग** | limb, member of a body — the classical word for a part of a whole | **0** |
| `avayava` / अवयव | component part | 0 |
| `amsha` / अंश | portion, share | 0 |

**I would propose `anga`:** *"agyat anga 'w'"*, *"rachana anga seema atikram"*, अज्ञातम् **अङ्गम्**. It is short, it is
the word a Sanskrit grammar uses for a member of a compound body, and the compiler has never used it. **It is
checked against the compiler, not yet against a dictionary — ChatGPT's check is still required, per the owner's rule.**

### (b) Rename the region instead

**Price: zero compiler work now,** since nothing is built. The cost is the risk of repeating this mistake, so each
candidate was checked against the compiler: `pradesh` (प्रदेश, region), `avadhi` (अवधि, bound, extent), `parisar`
(परिसर, precinct) — **0 occurrences each.** Not `mandal`: Malayalam's frozen pack already uses മണ്ഡലം for "field".
Not `seema`: 300 occurrences, it means a limit in every capacity message.

**My recommendation agrees with yours: (a).** The region is the better owner of "field/extent"; a struct member is an
*anga*. And (a)'s whole cost is 15 hand-written lines inside a build that is happening anyway.

## Item 2 — `nivartanam` inside a region: the evaluation-order question, answered

**The order is: evaluate, check, restore, return. "Restore before the jump/return" means after the expression and
before the `ret` instruction — one place, 14 bytes.**

Take Gemini's case, `nivartanam helper(buf)` inside a block:
1. **The expression is evaluated while the region is live.** `helper` reads `buf`; if `helper`'s own `nirmmita`s
   are inside a block of *its* own, they are rewound by its own exits; if not, they go to the persistent cursor
   (the region is lexical). Either way the result lands in `rax` (and `rdx` for a phal-prakriya).
2. **Step 4 has already decided, at compile time, whether the value may leave:** `kind(helper(buf))` is *none* (a
   call), so it may; `nivartanam buf` or `nivartanam buf + 8` is refused before any byte is emitted.
3. **Then the restore:** `mov r11, [mark]; mov [rip+cursor], r11`. `r11` is caller-saved and unused by the return
   convention, so `rax`, `rdx` and `xmm0` are untouched. The scratch the expression may have allocated inside the
   block lies below the mark and is released by this store — which is correct, because nothing admissible can still
   point into it after step 2.
4. The existing epilogue.

**So Gemini's concern ("the expression may allocate") is exactly what makes restore-after-evaluation right, not
wrong:** the allocation is scratch for computing the value, and the value that survives is, by step 2, not a
pointer into it. **Restoring before evaluation would be the bug** — `helper(buf)` would read rewound memory.

**The remaining case is the documented hole, not an ordering problem:** a `helper` that returns its own argument
launders `buf` through a call result. That is rule D below, and the `--debug` fail-stop is what catches it.

**What Gemini's ban would buy and cost:**
- buys: rule C disappears (~15 lines) and the 14-byte emitter is not needed at the two return sites (~15 lines);
- costs: the block cannot be used in this library's own style — 677 `nivartanam` in `lib/`, most of them guards at
  the top of a function — and `prasar` would have to be banned with it, or the ban is inconsistent.

**Decision: allow.** Thirty lines against the common shape of every function in the tree. ChatGPT's R135 reaches the
same decision by the same ordering argument.

## Item 3 — one rule set

**The mechanism both agree on:** a per-function list of (variable, depth) kinds, computed by `kind(expr)` during the
existing generation walk, with a pre-scan of each block's subtree for loop-carried flow (R62 §4.1–4.2).

**Where they differ:** Gemini allows calls and documents the hole; ChatGPT's K0 rejects every unknown — pointer
arguments to any call, pointers stored in any buffer, the raw-buffer `likha`, dynamic sizes — and verifies callees.
**K0 is sound and it is a different, much smaller language inside the block**: `varna_maap(buf)` is not allowed,
nor is a `mala` of pointers, nor `nirmmita(n)` with a runtime `n`. ChatGPT prices it at 960–1,800 lines and says so
plainly. **The owner's million-allocation test passes under K0; almost no existing library call does.**

**Converged set: Gemini's permissiveness where refusing would remove the block's purpose, ChatGPT's "unknown is
rejection" wherever a rejection costs no real program.** Each rule says what it emits (always nothing), what it
catches, and what it lets through.

| # | Rule | Catches | Lets through |
|---|---|---|---|
| **A** | `x = e`, `vitti x = e`: refuse if `kind(e)` is block at depth d and `x` is declared before block d's watermark, or is a module global | `outer = p`, `outer = p + 64`, `g = p`, inner-to-outer-block assignment | `outer = helper(p)` (a call result has no kind) |
| **B** | a store — `x[i] = e`, `x.f = e`, `likh8(a, e)`, `kosh_push(x, e)`, `smaran_cp` — refuse if `kind(e)` is block **unless the container is itself block-kind at depth ≥ d** | storing a block pointer into an outer `mala`, a `rachana`, a parameter, a global `kosh`, or through any pointer the compiler cannot place | a store through a laundered pointer |
| **C** | `nivartanam e`, `prasar f(...)`, `siddhi(e)`/`dosh(e)` payloads: refuse if `kind(e)` is block | `nivartanam p`, `nivartanam p + 8` | `nivartanam helper(p)` where `helper` returns its argument |
| **D** | a block-kind argument to a **direct** `prakriya` call: **allow** | — | **a callee that keeps its argument** (`suchi_khip(outer_list, p)` stores it). Documented. |
| **D′** (from K0) | a block-kind argument to an **indirect** call (`t[0](x)`, `p.f(x)`), to a foreign `--ffi` call, or a block-kind value handed to `yantra`-adjacent raw forms: **refuse** | retention through code the compiler cannot name | — |
| **E** | arithmetic and conversions on a block-kind operand keep the kind (`+`, `-`, `*`, bit ops, `dasham` conversion) | laundering by `+ 0`, by masking, by float round-trip | laundering **through memory**: `likh8(cell, p)` then `outer = pad8(cell)` — a loaded word has no kind |
| **F** | the pre-scan at block entry: a variable assigned a block-kind value anywhere in the block is block-kind from its first line | the loop-carried escape of R62 §4.1 | — |

**What this set is, honestly:** a lint with two known holes, D and E-through-memory, plus the `--debug` build in
which the scratch cursor never rewinds and each block's pages are `mprotect`ed on exit, so that anything slipping
through either hole **faults at its first use**. ChatGPT would call this "not a proof"; it is right, and the design
does not claim one. **What it buys over K0 is that every library function remains callable from inside a block.**

**Price:**

| | emitted instructions | compiler work |
|---|---|---|
| per assignment / store | **0** | one `kind()` walk of the right-hand side, one scan of the per-function kind list, one index compare against the block watermark |
| per call | **0** | D: nothing; D′: one test of the call form |
| per arithmetic operation | **0** | one recursion step in `kind()` |
| per block entry | **0** | the pre-scan of the block's statements |
| **compiler lines** | | kind list ~50 · `kind()` ~60 · pre-scan ~60 · hooks A–D′ (about 9 sites) ~90 · error with line number ~20 · **~280** |

**Zero extra bytes for programs without a block — confirmed by construction:** every hook begins with
`cmp [r62_depth], 0 / je`, the kind list is empty when no block has opened, and the keyword appears in no existing
program. **The first thing to run after the hooks land, before the block itself works, is the guard: 577 programs,
0 DIFFER on ELF, PE and Wine.** If it is not 0, the gate leaks and the veto applies.

## The whole of steps 3 and 4, priced together

| Part | Location in `src/sutram_compiler.asm` (or new file) | Lines | Existing path touched? |
|---|---|---|---|
| keyword, Latin + Devanagari, `KW_` constant | `kw_table` `:473`, `lang/sanskrit.lang` | 8 | table entry only |
| parse `kshetra` + braces-optional body, AST node | beside `.ps_if` `:9053` | 30 | no |
| generate: hidden mark local, entry/exit assignments, depth bookkeeping | beside `.gs_assign` `:13074` | 70 | no |
| the 14-byte restore emitter and its 4 exit hooks | `.gs_return` `:14440`, `.gs_break` `:14063`, `.gs_continue` `:14085`, `r25_gen_prasar` (`src/r25_phal.inc:178`) | 65 | **yes — gated; 0 bytes when no block** |
| kshetra depth recorded at loop entry | the loop generator's save area, `:14015`/`:14054` | 10 | yes — compiler-side only, emits nothing |
| scratch-cursor `nirmmita` path with zeroing | beside `r38_nirm_seq` `:19892` | 120 | **gated on depth** |
| outer-`kosh` growth picks the persistent cursor | `:15799` | 10 | gated on depth |
| runtime error for `kosh`/`mala` declared in a block when scratch is exhausted | the `:14620` construction | 25 | gated on depth |
| the check (item 3) | new `src/r63_kshetra.inc` + one-line hooks | 280 | gated on depth |
| `--debug`: no rewind, `mprotect` on exit | `src/r45_debug.inc` | 40 | debug builds only |
| item 1(a): four field strings, Sanskrit pack, goldens, tests | `:313`, `:317`, `:328`, `:827`; `lang/sanskrit.sandesh`; 4 goldens; `tests/r23` | 15 | changes 4 compile-error texts only |
| **total** | **about 16 one-line hooks in existing paths, 1 new include** | **~670** | |

R62 gave ~580 for steps 3 and 4 alone; the difference is the debug fail-stop (40), the runtime error for declarations
(25), item 1(a) (15), and the loop-entry record (10), all of which this round adds or makes explicit.

**Not in this number, by the owner's decision:** Steps 0–2 (the `kosh` fix, the contiguous bump, `dvi-mukha`), which
are the guard-visible parts, and Windows.

**The order that keeps the guard meaningful:** hooks and gates first, guard at 0 DIFFER; then the block with a plain
rewind; then the check; then the debug fail-stop; then the three deciding tests (million allocations in a loop; the
outer assignment refused with a line number; the loop-carried case of rule F).
