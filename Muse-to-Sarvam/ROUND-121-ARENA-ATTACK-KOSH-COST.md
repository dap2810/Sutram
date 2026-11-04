# Muse Round 121 — Attack the arena as it is now, and measure the real cost of a kosh

- **Base for WS2/WS3:** main at v297 (`c803cc07`, compiler `Sutram 1.0 (v297)`).
- **Base for WS1:** the arena branch `remotes/origin/claude/r108-arena-review`.
- **Deliverables:** this report, `r121.json`, `r121_ws1_arena.md` (full WS1 attack log),
  WS2 probes (`r121_kosh_n1.sm`, `r121_kosh_n10.sm`, `r121_kosh_n100.sm`,
  `r121_kosh_n1000.sm`, `r121_sampler.py`), WS3 scan (`r121_ws3_scan.py`).
- **Audit/probe only.** No code was changed on main or on the branch, nothing was
  pushed or merged by this round.

## Correction to the brief, stated first

The brief says "`claude/r108-arena-review` at `3a6292e` fixes `chain40_reuse.sm`."
**That commit does not exist in this repo.** `git rev-parse 3a6292e` returns
`fatal: ambiguous argument '3a6292e': unknown revision`. No object, branch, or tag
by that name was found, so the "fixed" version could not be tested. Everything in
WS1 below is the branch **tip `0e71e546`** ("R108 review branch: the block-arena
kosh as built before ROUND-108-CORRECTION (not for main)"), built with NASM from
`~/workspace/build-tools/nasm-inst/bin`, reporting `Sutram 1.0 (v290)`. The tip's
own message is consistent with the fix being absent from it — and the results
confirm it: the R110 defect is still live at this tip.

## WS1 — The arena is fixed. Attack it again. Answer: no, it is not fixed — two defects, neither closed at this tip

### Defect 1 (known from R110, still present): the 32-round fixpoint cap

Chains of 2, 5, 10, and 32 keeping `prakriya`s are refused with `E_KOSH_MANDAPA`
("tam prakriyam na gacchati ya tam rakshati"). Chains of **33 and 40 compile**
and print `99` for the correct `11` (exit 0): the may-keep fixpoint propagates
"keeps" backwards through at most 32 rounds, so a keeper 33 links deep is never
marked, the call is allowed, the block reclaims the arena slot, the next block's
kosh takes it, and the escaped pointer reads the new kosh's value. The boundary
is exactly 32/33. Raising the cap is not a fix — a longer chain would be the
next reproducer; the fixpoint must run to convergence.

The no-reuse controls (same chains, no reuse block) compile and print `11`
(correct-looking): the pointer still escapes and dangles; reuse is only what
makes it visible as `99`. The defect is therefore not a sampling artefact.

### Defect 2 (new shape, not the chain cap): a callee storing its kosh param into a global vitti escapes

```sutram
vitti holder = 0
prakriya rakh_vitti(kosh k) {
    holder = k
    nivartanam 0
}
mukhya() {
    mandapa {
        kosh k[4]
        kosh_push(k, 11)
        rakh_vitti(k)
    }
    mandapa {
        kosh k2[4]
        kosh_push(k2, 99)
    }
    likha(holder[0])
}
```

This compiles and prints `99` (exit 0) instead of `11`. The analysis catches
every neighbouring shape — a direct store to an outer vitti (`vitti_direct`),
a return of the param as a vitti (`vitti_return`), a store to a rachana field
(`field`, refused with "smritau na likhyate"), a store to an outer kosh
(`visible_assign`) — but **not** a store from inside a callee to a global
vitti. `rakh_vitti` returns `0` and never returns, aliases, or stores the kosh
in any tracked way, so it is classified non-keeping and the call is allowed;
the global then holds a dangling arena pointer past block exit. The control
without a reuse block prints `11`, proving the read itself is faithful and the
`99` is slot reuse, not a misread.

Why this matters beyond the chain cap: fixing the fixpoint to convergence
would **not** fix this hole. The callee is only one link deep; the problem is
not depth but a missing side-channel in the may-keep analysis — stores to
global vittis (a plain address-sized variable) are not treated as keeping. Any
fix must either treat "callee stores a kosh param (or a value derived from it)
into any variable that outlives the block" as keeping, or refuse kosh params to
callees that write globals. Scope limit found while scoping this: top-level
`kosh`/`mala` declarations are a syntax error on this branch, so a
global-kosh / global-mala side channel cannot even be written to test; the
global-**vitti** channel is the expressible one, and it is open.

### Everything else attacked holds at this tip

- Rachana-field escapes, aliasing (`alias_direct`, "dvitiyam nama na labhate"),
  direct returns (`return_direct`, "nivartanam na shakyate"), direct outer-vitti
  stores, and vitti-returns: all refused with specific `E_KOSH_MANDAPA` messages.
- Reader chains still work: a kosh read through a 2-level reader chain, never
  kept, compiles and prints the correct value (`22`) — refusal is not overbroad.
- Two koshes in one block survive each other's growth intact (k1 len 8/peek 8,
  k2 len 3/peek 30, `10 20 30`, then k1 still `1…8`).
- Budgeted exhaustion refuses cleanly at run time with `E_PARIMITA`
  (`mandapa parimita 1000`, 100,000 pushes, exit 1).
- Unbudgeted exhaustion refuses cleanly with `kshetra purnam` at exactly
  33,554,432 passes / 33,554,433 refuses (the 1 GiB cumulative-slot bound), no crash.

**WS1 verdict: there IS a next defect — two, in fact.** The chain cap (Defect 1)
is the R110 defect, still live because the brief's fix commit is not in this
repo. The global-vitti callee store (Defect 2) is new, depth-independent, and
would survive a fixpoint-convergence fix. The branch as tested is not the fixed
version, and must not be merged on the strength of the brief's claim.

## WS2 — The cost of a kosh, measured (Linux v297)

Method: a `prakriya` that creates a kosh (capacity 4, two pushes) and returns it;
`mukhya` calls it N times, holds all N handles in a `nirmmita` buffer, then
busy-loops so a Python sampler can poll `/proc/<pid>/status` for peak RSS
(`VmRSS`) and peak virtual size (`VmSize`). The program, not the sampler, is
the measurement; the sampler only reads the kernel's numbers.

| Live kosh | Peak RSS | Peak VSZ |
|---:|---:|---:|
| 1 | 32 KB (0.03 MB) | 1,088.2 MB |
| 10 | 68 KB (0.07 MB) | 1,664.2 MB |
| 100 | 428 KB (0.42 MB) | 7,424.2 MB |
| 1000 | 4,028 KB (3.93 MB) | 65,024.2 MB |

Decomposition (exact across all four runs): VSZ = 1,024 MB (the 1 GiB arena,
reserved lazily on first `nirmmita`, not at startup — see Round 124 WS2, where a
hello-world that never allocates has VSZ 0.2 MB) + N × 64 MB (one region per
kosh) + ~0.2 MB (binary, stack). RSS ≈ 4 KB per kosh — one touched page (the
region's first page holds the header and the first elements).

**Answer: 64 MiB is harmless because it is virtual, for real memory on Linux —
and it matters at scale anyway.** RSS grows by 4 KB per kosh, not 64 MB, so a
thousand live kosh cost 4 MB of real memory. But VSZ grows by exactly 64 MB per
kosh (1,000 kosh = 64 GB of address space), which is invisible to `top`'s RES
column and to `parimana()` (see Round 123 WS3, gap (iv)), and it imposes a hard
ceiling under any address-space limit: under a 1 GiB `ulimit -v`, the 16th kosh
crashes (Round 124 WS3, verified). And on Windows, where the adapter commits
rather than reserves (Round 124 WS1/WS2), the same 64 MB is real commit, not
virtual. So the design goal the brief names — "a student can reason about what
a kosh costs" — is not met by the reservation being virtual: the cost is
invisible in the two places a student looks (RSS, `parimana()`), and it becomes
a crash at a limit nobody documented.

## WS3 — The reuse question. Answer: no library function needs it; the design is a decision, not a limit, for the library — but it is a limit for user programs

Method: a scan of all 24 `lib/*.smlib` bodies for an allocation call textually
inside a loop body (braced loops: **0 hits**), plus hand-checking of all 20
functions whose body contains both a loop and an allocation call. Every one of
the 20 allocates **once, before the loop** (all allocation lines are at function
lines 1–16, of the form `vitti X = nirmmita(...)`), and the loop only fills the
pre-allocated buffer. Representative bodies:

- `suchi_srij`/`suchi_vardh`: `nd = nirmmita(ncap * 8)` once, then
  `yavat (i < lst[0]) { nd[i] = old[i] }` — fill, not allocate.
- `sangrah.rakh_sangam`: `tmpa = nirmmita(...)`, `tmpb = nirmmita(...)` once,
  then loops that `nighantu_khip` into the caller's `out` — fill, not allocate.
- `roop.roop_ank`: `rev = nirmmita(22 * 8)` once, then `yavat (val > 0) { rev[rlen] = ... }`.
- `nighantu.nighantu_vardh`: `tmp = nirmmita(...)` once, then a loop that copies
  into `newm` (itself allocated once, before the loop).

**Name any that do: none.** No library function allocates a temp per iteration
and discards it, so no library function would benefit from reuse inside a live
block. The "no reuse" design therefore costs the library at most one call's
temps per call (freed at block exit), not a per-iteration blowup — it is a
decision the library can live with, not a limit on the library. It **is** a
limit for user programs: a user loop that allocates a fresh temp per iteration
(e.g. building a string per pass and discarding it) grows without bound until
the block exits, with no way to reclaim mid-block except by exiting the block.
That is the user-facing cost, and it is the one the docs should state (see
Round 123 WS3, gap (iii): the reference implies reuse across blocks but never
states there is none inside a live block).

## NOT RUN

Windows (cannot run Windows — the branch attack is by building and running the
branch compiler on Linux, and the WS2/WS3 measurements are Linux only), browser,
implementation (none authorized — attack and measurement, not fixes), native-
speaker review, full suite (no tree changes; the v297 suite numbers stand).

## Follow-ups (not fixed here)

- The arena branch must not merge until Defect 1 (fixpoint to convergence, not
  a higher cap) and Defect 2 (global-vitti stores as keeping) are closed, and
  the `3a6292e` fix claim must be reconciled with the repo (the commit is not
  in this repo's history).
- The 64 MiB-per-kosh reservation should be counted somewhere a student can
  see it (`parimana()` counts header + capacity, not the reservation), and the
  16-kosh-under-1-GiB ceiling should be documented (Round 124 WS3).
- The "no reuse inside a live block" sentence belongs in the reference
  (Round 123 WS3, gap (iii)).
