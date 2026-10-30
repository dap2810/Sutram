# R74-00 — The memory model as a whole: five compositions, five passes; the reference rewritten

- **Commits on `main`, in order:** `bd3a804` (1/2 the composition tests and gate) · `f1e34a0` (2/2 `LANGUAGE-REFERENCE` §19
  rewritten as a reference entry) · then this hand-back. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v270) - sampurna sutra`, unchanged this round.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=237`, FAIL=0.** Library proofs **226/226**. Property proofs **86/86**.
- **Guard pages (`tools/guard_page.py`, v270): controls 5/5, suite PASS=237 FAIL=0, library proofs 226/226,
  property proofs 86/86, 0 failed.**
- **Gates (`sh tools/gates.sh`, Xvfb display): 52 PASS / 0 FAIL / 1 NOT-RUN (Windows execution)** — one more gate:
  **`R74 compose`** (9 checks).
- **The guard, `b667bd9` → this round, `tools/guard_pair.py`, all three paths (Linux ELF, Linux PE, the Windows
  compiler under Wine): 509 byte-identical, 105 refused identically, 0 DIFFER, 8 new** (this round's test files).
  No compiler change, so 0 DIFFER is what it must be.

## On your numbers

Yours: 65,216 KB without the block, **14,464 KB** with it. Mine, three runs each: **62,464 KB** without,
**264 KB** with — and **264 KB is what a program that only prints `0` takes here**. So the block's loop
costs nothing above the empty program on this machine. If your trivial program also peaks near 14 MB, the
two measurements agree (both ≈ the baseline); if it peaks well below, something is resident in your run that
is not in mine, and I would like the trivial program's number to find it. `evidence-r74/extra-measurements.txt`.

## WS1 — the five compositions

`tests/r74_compose/`, run by the gate `R74 compose` (`test_compose.py`, `evidence-r74/r74-compose-test.txt`).
Each has a control where it makes sense: the same program with `mandapa` replaced by `yadi (1 == 1)`.

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

## WS2 — the guard-page run and the gates, on v270

Numbers at the top. **One thing you must know about what the guard-page run proves:** in the `GUARD_PAGES` build
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
of thumb; Linux-only; and what it is not. Every statement in it was checked against v270 this round.

**One correction to the old text, found while checking it:** it said a `kosh` inside a block is "not supported".
It works — and its storage is persistent, not reclaimed (100,000 passes: 3,072 KB with and without the block,
`evidence-r74/extra-measurements.txt`). The reference now says exactly that.

## What I did not do

- **No compiler change.** The call blind spot (#2) is described, not closed.
- **Not run:** real Windows (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.

**Document counts:** `doc_counts_gate` NOTEs (not failures, `evidence-r74/doc-counts.txt`): `PROJECT-MASTER.md`
says 48 PASS (measured 52) and five documents say suite 225 (measured 237). Docs prose; the owner's to bump.
