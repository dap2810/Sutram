# R82-00 — A `kosh` made in a block now dies with it: generation-checked, refused after the block, 0 DIFFER elsewhere; +11% worst case where it is used; the `parikshita` count rises from 63 to 88 if checked code may use a `kosh`

- **Commits on `main`, in order:** `aaf79e4` (1/3 **v278**: the generation check, examples 286–287) · `d65c072` (2/3 the gate) · then the reference §19, the changelog and this hand-back with `evidence-r82/`. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v278) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=255`, FAIL=0** (two new examples, 286–287). Library proofs **229/229**. Property
  proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 57 PASS / 0 FAIL / 1 NOT-RUN (Windows execution)** — one new, **`R82 kosh-mandapa`** (9 cases).
- **The guard, v277 (origin/main) → v278, `tools/guard_pair.py`, all three paths (Linux ELF, Linux PE, the Windows
  compiler under Wine): 665 programs — 536 byte-identical, 127 refused identically, 0 DIFFER, 2 new.** The Windows compiler's 536 outputs are byte-identical to the Linux compiler's PE outputs; 286/287 behave the same as PE under Wine (`evidence-r82/pe-under-wine.txt`).
  **Every program that does not declare a `kosh` in a block is untouched in bytes** — the feature is switched on
  per program, only by such a declaration.

## WS1 — the smallest version that works

**What I found first.** On v277 a `kosh` made in a block got out and was read afterwards with no
complaint: kept in an outer variable (`bahar = k`) and read through a `prakriya` (`padh(bahar, 0)` printed 11).
It read correctly only because a `kosh` is not stored in scratch memory — the
block never took it back. The escape check could not see it, as you said.

**What v278 does** — only in a program that declares a `kosh` inside a `mandapa`:

| | |
|---|---|
| a block that declares a `kosh` | takes a **fresh generation** on entry (`rdtsc`, kept in a stack slot of its own) and **clears it on every exit**: its end, `nivartanam` from inside it, `krama`/`agrim` out of a loop |
| each `kosh` | carries three more header words: the block's line, the slot's address (0 for a `kosh` made outside every block), the generation. Length and capacity stay where they were; growth copies the three |
| a `prakriya` with a `kosh` parameter | **checks it once, on entry**: the slot must still hold the generation (and lie in a live frame). That is enough — the callee cannot outlive the block running under it, and after its block a `kosh` can be used as a `kosh` only by passing it to a `prakriya` (its name is gone) |

**Not a range check.** A stale `kosh` and a new one can sit at the same place; the generation tells them apart,
as Gemini and ChatGPT required.

**The test that decides it**

`examples/286` — a block makes a `kosh`, pushes `i * i` for `i` = 1..n (growing it from 2 cells), reads it
through `padh(kosh k, i)` inside the block, and returns the sum: **385 and 338350 — accepted, correct.**

`examples/287` — the same `kosh`, its address kept in `bahar`, read after the block:

```
22
Sutram Error [E_KOSH_MANDAPA]: prakriya 'padh' - kosh 'k' pankti 10 mandape rachitah; sa mandapah samaptah
Sanket: mandape rachitah kosh mandapat bahih na jivati - mandape eva upayujyatam, mulyam nivartyatam
```

*(the kosh made in the block on line 10 — that block has ended; a kosh made in a block does not live outside it;
use it inside the block and return the value)*, exit 1.

**The other exits and lifetimes** (gate `R82 kosh-mandapa`, `evidence-r82/cases.txt`):
- **refused:** after `krama` out of a loop; an inner block's `kosh` once the inner block ended while the outer
  one still runs; **the same block in the next turn of a loop** (same slot, new generation); a sibling block's;
- **accepted:** recursion — a live `kosh` passed down five levels that each make their own (130, correct);
  `kosh dasham`; a `kosh` made outside every block alongside block ones.

**The gate can fail:** with the entry check switched off, all 5 refusals fail — each prints the old values
(`evidence-r82/gate-calibration.txt`).

## WS2 — the cost

**Programs that never put a `kosh` in a block: 0%**, measured as identical binaries — the guard's 665 programs
and the 8 shipped benchmarks compile to the v277 bytes. Under your 15% line by construction.

**Programs that do** (9 interleaved runs, `evidence-r82/ws2-cost.txt`) — each measured with and without one
unrelated block `kosh` at the top of `mukhya`, which switches the feature on for the whole program:

| | cost |
|---|---|
| **20,000,000 calls of `padh(kosh k, i)`** — a `prakriya` whose whole body is one `kosh` read (the worst case: one entry check per tiny call) | **+11.3%** |
| 200 × 50,000 `kosh_push` with growth (the longer header copied) | **+3.5%** |

## WS3 — the count: **63 → 88, but only if a checked function may use a `kosh`**

A block-safe `kosh` does not by itself change `parikshita`: the shipped checker still refuses `kosh` outright
(R81's rule, which I have not changed). **So I measured the what-if**, with an experimental checker in scratch
that admits a `kosh` — its declaration, the `kosh_*` builtins (not `akshar_rakh`, which sits in the same id range),
and indexing a `kosh` variable or parameter. All of these are now bounds- and lifetime-checked. Same method as
R81 (mark everything, unmark refusals to a fixpoint, recompile every module with what is left).

| checker | library functions that pass | modules whole |
|---|---|---|
| v278, `kosh` refused | **63** of 306 — **Muse's R82 table reproduces it independently** (`Muse-to-Sarvam/ROUND-82-ONE-TABLE-AND-BLOCK-REACH.md`) | 3 (`ank`, `madhava`, `sadhan`) |
| **experiment, `kosh` admitted** | **88** of 306 (+25) | **5** (+ `kalana`, `samanvaya`) |

**The 25:** all of `kalana` (6: derivatives, integrals), all of `samanvaya` (10: matrices), 9 of `sankhyiki`
(mean, variance, deviation, sum, min, max …: they take a `kosh dasham`).

**What still blocks the other 218:** 124 trace to a buffer handed in as a parameter. These are the raw-pointer
modules, which a `kosh` does not reach: `suchi` 34, `phal` 14, **`shreni` 14 (sorting: still none)**, `varna` 13,
`sangrah` 11, `ganita` 10, `nighantu` 10. The other 94 trace to byte and raw builtins: `akshar` 33,
`akshar_rakh` 30, `likh8` / `pad8` 21, `vartani_aayam` 7, `dvaram` 3.

**So the plain answer:** vectors-in-a-block is a user-code feature **and** raises the library count by 25 — but
only once `parikshita` admits `kosh`. That is a rule change: one small diff (`evidence-r82/ws3-experimental-checker.diff`,
69 added lines), and your decision. Sorting and lists need either a checked buffer parameter or a rewrite onto
`kosh`.

## What I did not do, and the limits

- **The block does not take a `kosh`'s memory back.** It stays on the persistent side, so its header — where the
  generation lives — can never be overwritten, and the check is exact. Reclaiming it needs the generation kept
  outside reusable memory (R148's slot table). That is the next step, not this one.
- **Raw reads of a `kosh`'s address** (`bahar[0]` on a plain `vitti`) are not checked, as all raw memory (§6c);
  `parikshita` refuses them.
- **`--separate`:** a module compiled on its own checks only if it has a `kosh` in a block itself. The
  whole-program compile checks every `prakriya` (`evidence-r82/separate-compilation.txt`). A module-made `kosh`
  reaching the program's checked `prakriya` is closed today by the existing `kosh`-argument type rule (`kosh tark:
  tatv prakar bhinn`), not by this check.
- **`parikshita` still refuses `kosh`** (unchanged; WS3 is the measured case for changing it).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs (no pack text), `MEMORY-DECISION.md`.
  **Not run:** real Windows (Wine only).
