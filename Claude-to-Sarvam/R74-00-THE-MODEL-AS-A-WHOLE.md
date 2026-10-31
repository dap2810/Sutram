# R74-00 — The memory model as a whole: five compositions pass; five holes found by others were real, and are closed (v272)

- **Commits on `main`, in order:** `38d032f` (the composition tests and gate) · `297558f` (`LANGUAGE-REFERENCE` §19
  rewritten as a reference entry) · `641713b` (hand-back, first state) · `684079b` (**v271**: R146's F1–F4 closed) ·
  `8593471` (§19 for v271) · `bb380e9` (hand-back) · `f314b08` (**v272**: the module-`vitti` hole Muse found; the
  formatter fix) · `ffeec4e` (§19) · then this hand-back. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v272) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=237`, FAIL=0.** Library proofs **226/226**. Property proofs **86/86**.
- **Guard pages (`tools/guard_page.py`), on v270, v271 and v272 alike: controls 5/5, suite PASS=237 FAIL=0, library
  proofs 226/226, property proofs 86/86, 0 failed.**
- **Gates (`sh tools/gates.sh`, Xvfb display): 52 PASS / 0 FAIL / 1 NOT-RUN (Windows execution)**, on v270, v271 and
  v272. One more gate: **`R74 compose`** (9 checks); **`R73 scratch`** grows from 15 checks to 33.
- **The guard, v270 → v272, `tools/guard_pair.py`:**
  - **Linux PE and the Windows compiler under Wine: 509 byte-identical, 105 refused identically, 0 DIFFER, 26 new.**
  - **Linux ELF: 493 byte-identical, 105 refused identically, 16 DIFFER, 26 new.** The 16 are exactly the programs
    with a scratch `nirmmita`; **in every one the only bytes that differ are the F4 fix — `jz` → `jle`, one byte
    per scratch `nirmmita` (0x84 → 0x8E) — same length, same output, same exit code.** Checked file by file
    (`evidence-r74/elf-diff-check-v272.txt`). The v272 change itself alters no binary: it only refuses more.
  - (v270 → v271 gave the same 16/0/0; the tree changes alone on v270, before any compiler change: 0 DIFFER on all three.)

## On your numbers

Yours: 65,216 KB without the block, **14,464 KB** with it. Mine, three runs each: **62,464 KB** without,
**264 KB** with — and **264 KB is what a program that only prints `0` takes here**. So the block's loop
costs nothing above the empty program on this machine. If your trivial program also peaks near 14 MB, the
two measurements agree (both ≈ the baseline); if it peaks well below, something is resident in your run that
is not in mine, and I would like the trivial program's number to find it. `evidence-r74/extra-measurements.txt`.

## WS1 — the five compositions

`tests/r74_compose/`, run by the gate `R74 compose` (`test_compose.py`, `evidence-r74/r74-compose-test.txt`).
Each has a control where it makes sense: the same program with `mandapa` replaced by `yadi (1 == 1)`. **Run on v270, and again on v271 and v272 after the fixes: 9/9 every time, the same numbers.** Your own run (`docs/reports/MEMORY-COMPOSITION-TEST.md`, 64 MB × 1,000 at 67 MB peak; 500 deep exact) agrees with these.

| # | composition | result | the number |
|---|---|---|---|
| 1 | a block in a loop pushes 1,000,000 values into a `kosh` declared **outside** it | **PASS — all three hold** | the `kosh` keeps everything (length 1,000,000, sum 1,499,998,500,000, first 0, last 2,999,997); peak **7.8 MB** — the `kosh` itself is 8 MB of numbers — against **78 MB** without the block |
| 2 | a `prakriya` given a scratch pointer, returning a value derived from it | **PASS — allowed, and defensible for a number; NOT defensible for an address** | `yoga(buf, 4)` returns the sum of the data, **10**: allowed and right. `madhya(buf)` returns `buf + 8` — **also compiles**: the stated blind spot. Pinned in the same file |
| 3 | two sibling blocks in sequence | **PASS — the second gets a clean cursor** | 1,000,000 pairs: the second block found the first's data **0 times**; peak **312 KB**. The two blocks get **the same address** (difference 0) |
| 4 | a block that allocates 100 MB | **PASS — it fits; past the field it stops in Sanskrit** | 100 MB fits the 1 GiB field: twenty passes, every page written, peak **100 MB**, not 2 GB. Twelve 100 MB allocations in one block stop after the tenth: **`Sutram Error: kshetra purnam - mandapa-smritih samapta`** (*the field is full — the block's memory is used up*), exit 1 |
| 5 | recursion: a block in a `prakriya`, 1,000 deep | **PASS — the mark is per frame, RSS flat** | every frame checks, after its callees return, that its own buffer still holds its own numbers: sum **500,500,000** (all 1,000 frames, 1,000 times). Peak **2 MB**, against **64 MB** without the block |

**On #2, plainly.** The answer the check gives is right for a number and wrong for an address, and the check
cannot tell them apart through a call: a call's result is never treated as an address. Returning *data* derived
from scratch is what the block is for, so refusing every call that receives a scratch pointer (ChatGPT's K0 rule,
Muse's recommendation in `Muse-to-Sarvam/ROUND-73-CHECK-BLIND-SPOTS.md`) would refuse `yoga` too. Closing it
properly needs a per-`prakriya` summary — "returns or stores a parameter" — computed after the whole file is
parsed. Not built; stated in every refusal's `Sanket` line and in the reference.

**On #3**, a program cannot print two scratch addresses to compare them — carrying one out is what the check
refuses. The same-address measurement uses the blind spot on purpose (`adr(p)` returns `p`), in the evidence
only, not in a test.

**On #4**, one thing worth knowing: **rewinding reuses pages, it does not return them.** After a 100 MB block the
process still holds 100 MB; the next block uses the same pages. The reference says so.

## R146 — ChatGPT predicted four holes from reading the source. All four were real. All four are closed.

ChatGPT's R146 (`00dce01`) arrived while I worked; it predicted F1–F4 without running anything. I ran its witnesses
on v270 before calling the model verified — **each one reproduced** — and fixed them in v271
(`evidence-r74/r146-f1-f4-v270-v271.txt`, both compilers, the same programs):

| | the hole | v270 | v271 |
|---|---|---|---|
| **F1** | a store call inside an expression — `vitti count = kosh_push(saved, b)` — was not checked (only a call standing alone as a statement was); `likh(addr, value)` was never checked at all | **compiled; the `kosh` held a dangling address** (printed `1`, the second pass's data) | **refused** — every store call is checked where it is built: statement, initializer, argument, condition |
| **F2** | a loop's back edge: `outside = q` written above `q = buf` in the same loop | **compiled; printed `777`** — the next block's data, through the escaped address | **refused** — inside a loop in a block every flow is remembered; leaving the loop re-checks them all with the loop's final taints until nothing rises (a chain of three names needs three passes; tested) |
| **F3** | a failure passed on by `prasar` returned without rewinding | 1,000,000 failures: **62 MB** | **264 KB** — the failure exit rewinds, as `nivartanam` does; code and value arrive intact (tested through two blocks and two `prakriya`) |
| **F4** | `nirmmita(0 - 1)` in a block: the size rounded to 0 bytes and the zeroing wrote one qword into the block above | the outer block's `123` became **`0`** | **`123`** — a negative size gives 0, exactly as `nirmmita` does outside a block |

The tests are in `tests/r73_scratch/` (13 files: 9 refusals, 4 allowed/measured), run by the `R73 scratch` gate.
**Each refusal has an allowed twin with the same shape and numbers instead of addresses** — so the fix refuses
addresses, not loops or stores: `allowed_f1_numbers` (`kosh_push`/`likh8` of scratch *data* in initializers) and
`allowed_f2_numbers` (the F2 shape with `q = b[0]`) compile and print the right values.

**What R146 is right about beyond the four:** a program that compiles is not proved safe — the call blind spot
(composition #2) is still open. §19 now says so in one sentence.

## Muse's R74 — one more live hole, on v270 and v271: a module `vitti`. Closed in v272.

`Muse-to-Sarvam/ROUND-74-BLIND-SPOTS-MEASURED.md` (`71c95f2`) measured the check on v270 and found **`g = buf + 64`
compiles when `g` is a module-level `vitti`**, while the same assignment to a local is refused. I reproduced it on
v270 and on my v271: compiled, and the program crashed reading through `g` after the block. **The cause:** R4
records every `x = ...` as a sighting of `x`, so inside a `prakriya` the assignment itself was the global's *first*
sighting, and the check placed the global at the block's depth. **v272: a module `vitti` is outside every block**;
one declared further down the file than the `prakriya` that assigns it is checked when the whole program has been
read. Refused: into a global, into a global round a loop back edge, into a global declared later. Allowed: a number
read out of scratch into a global (prints 42). `evidence-r74/module-vitti-v270-v272.txt`.

**Muse's other live miss — `stash(b)`, a `prakriya` that stores its argument in a global — is the call blind spot,
still open,** as stated. Muse also measured that direct `kosh_push`, an alias through `q = b`, and a returned
rachana are refused on v270; those hold on v272.

**Found on the way, in a tool of mine:** `sutram-fmt` indented a module `vitti` written at column 0 after a braceless
`prakriya` *into* that `prakriya` — the compiler reads it as a module `vitti`, so formatting changed the program.
Fixed: a code line at column 0 ends a braceless `prakriya`'s body in the formatter, as in the compiler (a braceless
`mukhya` still runs to the end of the file). The tree's formatting gate is unchanged (`FORMATTED`).
`evidence-r74/formatter-column0-prakriya.txt`.

## WS2 — the guard-page run and the gates

Numbers at the top (v270, v271 and v272 alike). **One thing you must know about what the guard-page run proves:** in the `GUARD_PAGES` build
a `mandapa` is an ordinary block — `nirmmita` inside it takes the guard-page allocator, not the scratch side
(R73's design, so the guard-page run still covers every program with a block). **So the guard-page run proves the
programs' own reads and writes stay in bounds; it does not exercise the scratch allocator's code.** The code it
cannot see is small — the cursor arithmetic and the zeroing loop — so I tested that directly:
**`c6_adjacent`**: for every size 1..200 bytes, a filled block, then a second block allocated just below it,
zeroed: **0 bad cells** — the first block intact every time, the second all zeros. It is in the `R74 compose` gate.

## WS3 — `LANGUAGE-REFERENCE` §19, as it is

Rewritten as a reference entry, not a design note: **what it is for** first — *"a `mandapa` holds the temporary
buffers of one piece of work. Every `nirmmita` written inside it is given back, all at once, when the block ends —
so work that allocates in a loop does not grow the program."* Then: the form (indented, braces, one statement on
the line, `मण्डप`); an example; **what it holds in v1.0 — scalar scratch, not a `kosh` of pointers**; run time,
with the measured numbers; **the two escapes it refuses** (into an outer variable, into memory — and out by
`nivartanam`); **the one it does not see** (an address kept by a `prakriya`, or hidden in a `kosh`) with the rule
of thumb; Linux-only; and what it is not. Every statement in it was checked against v270, and again after the fixes (stores anywhere, loops, `prasar`, negative sizes, module `vitti`, and: *a program that compiles is not proved safe*).

**One correction to the old text, found while checking it:** it said a `kosh` inside a block is "not supported".
It works — and its storage is persistent, not reclaimed (100,000 passes: 3,072 KB with and without the block,
`evidence-r74/extra-measurements.txt`). The reference now says exactly that.

## What I did not do

- **The call blind spot (#2, and Muse's `stash`) is described, not closed** — it needs a per-`prakriya` summary of what each one does with its parameters; R146 agrees it is a design limit.
- **The R146 README sentence** — not mine to write; R146's own assessment of it stands with my evidence attached.
- **Not run:** real Windows (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.

**Document counts:** `doc_counts_gate` NOTEs (not failures, `evidence-r74/doc-counts.txt`): `PROJECT-MASTER.md`
says 48 PASS (measured 52) and five documents say suite 225 (measured 237). Docs prose; the owner's to bump.
