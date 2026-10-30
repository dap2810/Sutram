# ROUND-70 — the loop "clobber" census (premise corrected: it was the parser)

Base: origin/main `c32999ea` (compiler v265 — the
fix is already in). No tree changes. Read with
ROUND-71, which reframes this census; this report
answers R70's questions as asked, with the premise
corrected where the evidence overturns it.

## The premise was wrong, verified both directions

R70's repro, run here:

- **v265: `i=0 i=1 i=2 done`** — correct.
- **v261 (kept compiler): `i=0` forever** — the same
  source hangs, printing `i=0` without end.

So the bug predates the memory work entirely, and
it is not the allocator: an indented body was
parsed as ONE statement, so `i = i + 1` sat outside
the loop. Every count below must be read with that
correction — "affected" means "indented
multi-statement body", not "allocation in a loop".

## 1. `nirmmita` inside a loop: 3 sites, all new tests

| Site | Form |
|---|---|
| `examples/258_r70_loop_indent.sm:7` | indented, 3-statement body (the R70 repro itself) |
| `examples/258_r70_loop_indent.sm:14` | indented, 4-statement body (allocate after increment) |
| `examples/258_r70_loop_indent.sm:32` | indented, 4-statement body (1000 allocations, counter intact) |

**Zero in `tests/`, zero in `lib/`, and zero in the
pre-fix `examples/`.** 258 is the fix's own test
file (commit `1a98f098`, "the tests that would
have caught it"). If the answer is zero, say zero:
in the tree the bug shipped against, no program
called `nirmmita` inside a loop at all — that is
why nothing caught it.

## 2. `nirmmita` with a variable live across it: 182 sites, all working

Textual approximation, method stated: within each
function, a `nirmmita` site where some variable
assigned before the call is referenced after it
(excluding the call's own target). **182 sites in
76 files** across `examples/` + `tests/` + `lib/`.

This number is the evidence against the clobber
theory: if `nirmmita` clobbered a live register,
these 182 sites would misbehave, and the suite is
green. They all work. The parser bug was the sole
cause; there is no allocator clobber to hunt.

## 3. `kosh_push` inside a loop: 7 sites in 5 files, all braced

| File | Loop sites |
|---|---|
| `examples/203_meru_with_kosh.sm` | 2 |
| `examples/205_madhava_pi_kosh.sm` | 1 |
| `examples/208_kalana.sm` | 1 |
| `tests/stdlib/kosh_reuse.sm` | 2 |
| `tests/stdlib/r37_bounds.sm` | 1 |

All braced — never touched by the parser bug.
R70's intuition is confirmed in the sharp form:
the loop+allocation shape existed in the tree ONLY
via `kosh_push` (through the library, braced), and
never via `nirmmita`, until the fix's tests added
it. That is why nobody looked at `nirmmita`.

## 4. `mala` / `rachana` creation inside a loop: no, and the question dissolves

- **`mala` declaration inside a loop: 0 anywhere**
  in `examples/` + `tests/` + `lib/`.
- **`rachana` creation inside a loop: 0.** The three
  258 `nirmmita` calls are plain buffers (indexed,
  not field-written), not rachana values.

But the deeper answer: the family question assumed
an allocator defect, and there is none. Braced
loops of ANY kind were never affected; indented
multi-statement loops of any kind were affected
(statements dropped). The fix is in one place —
the parser — not one place per container kind.

## The guard-page question: what test would catch a register clobber?

The answer is as R70 guessed: **a program whose
output depends on a variable held across the call.**
How many such tests exist today:

- **329 loop sites in 112 files** hold the loop
  variable across a call inside the loop and use it
  afterward (the clobber-catcher set) — including
  217's loop (`ank_tak_varna` + `pad_vam` with `i`
  live), 208, and 203. A loop-variable clobber
  would have been caught many times over.
- **182 `nirmmita` sites** (Q2 above) hold a
  variable across the call in straight-line code —
  a general `nirmmita` clobber would have been
  caught there too.

So the suite hole is NOT "no live-across tests".
It is narrower, and it is R71's finding: **no test
combined `nirmmita` + loop + indented
multi-statement body, because no pre-fix program
had an indented multi-statement body at all.**
The guard-page variant could not have caught this
either way (a dropped statement writes no
out-of-bounds memory) — the hole is in the suite's
shape coverage, not in any memory gate.

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.
- Implementation: no code was changed; the fix is
  Claude's v265, already on main.
