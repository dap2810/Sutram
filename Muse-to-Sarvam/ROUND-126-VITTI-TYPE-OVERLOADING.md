# Muse Round 126 — The type-overloading claim. Is it true?

- **Base:** the brief says main at v299. Current main is v300 (`d2c96eaf`,
  Claude R124: Windows lazy commit + descriptor pricing + docs, plus the
  R125/R126 briefs). **No v299 → v300 drift for WS1/WS2:** all seven WS1
  probes were run on both v299 (worktree at `a4cc6540`) and v300 (worktree at
  `d2c96eaf`) with **identical** results, so the brief's base is stale but
  harmless for these results. The relevant behaviours are unchanged between
  v299 and v300.
- **Scope:** Muse rounds only. I did not work Claude's R124/R125 or ChatGPT's
  R200. I note only that Claude's R124 addendum ("`vitti a = k` is tracked")
  is consistent with what I observe on **both** v299 and v300 — the tracking
  predates v300, it was not newly added by it — as context, not as my
  evidence. My evidence is my own probes on both versions.
- **Test and analysis only.** No tracking, descriptor, or lifetime design was
  built, no code was changed.

## WS1 — Does `vitti` really lose the type?

Short answer: **partly true, partly false, and the true part is worse than the
claim states.** The compiler does track — for `kosh` — but it tracks as
"may hold" (not "currently holds"), so it crashes on reassignment instead of
either updating correctly or refusing.

### What the probes show (identical on v299 and v300)

| Probe | Result | Meaning |
|---|---|---|
| Direct kosh `k[100]` (4-element kosh, 2 pushed) | Refuses: `Sutram truti: mala ank seema atikram`, exit 1 | Direct kosh indexing **does** bounds-check |
| `vitti a = k`, then `a[100]` | Refuses, same error, exit 1 | Vitti-held kosh **does** bounds-check — the compiler **does** track that `a` holds a kosh (straight-line) and emits bounds-checked code |
| `vitti a = p` (nirmmita, 16 bytes), then `a[100]` | Prints `0`, exit 0 | Vitti-held raw pointer does **not** bounds-check |
| `vitti a = m` (mala, 4 elements), then `a[100]` | Prints `0`, exit 0 | Vitti-held mala does **not** bounds-check |
| Direct mala `m[100]` (4 elements) | Prints `0`, exit 0 | Mala **never** bounds-checks, direct or via vitti |

So "the compiler cannot tell which when it emits `a[0]`" is **FALSE for
kosh** (it can tell — it emits bounds-checked kosh code, distinct from the
unchecked raw/mala code) and **TRUE for mala vs raw** (they behave
identically, both unchecked, so the compiler cannot distinguish them by
behaviour).

### The reassignment test — the one that settles it — and it crashes

- **Forward (kosh → raw):** `a = k` (`k[0] = 11`); `a[0]` prints `11`
  (correct); then `a = p` (`p[0] = 77`); `a[0]` → **segfault, exit 139**
  (instead of `77`). On both v299 and v300.
- **Reverse (raw → kosh):** `a = p`; `a[0]` prints `77` (correct); then
  `a = k`; `a[0]` prints `11` (correct); then `a[100]` **refuses**
  (bounds check, correct). On both versions.
- **Control flow (single `yadi`, no else needed):** `a = k` initially;
  `yadi (c) { a = p }`; then `a[0]`. With `c = 1` (body executes, `a` becomes
  raw): **segfault, exit 139**. With `c = 0` (body does not execute, `a`
  stays kosh): prints `11`, correct.

Explanation: the tracking is **MAY-analysis, not flow-sensitive
MUST-analysis**. Once a variable is ever assigned a kosh, the compiler emits
kosh code (bounds check, header read) for it thereafter — which is correct
when it actually holds a kosh (reverse order, `c = 0` case) and crashes when
it actually holds a raw pointer (forward order, `c = 1` case), because kosh
code reads a header that raw buffers do not have. It does not update the
tracked type on reassignment, and it does not refuse reassignment to a
different type. The current behaviour (segfault) is the worst outcome: it
neither tracks correctly nor refuses, it crashes.

The branch test via `anyatha` could not be done as written: `anyatha` blocks
do not parse in the form I used (likha-only `anyatha` fails at the closing
brace; assignment `anyatha` fails at `=`), and there is **zero** `anyatha`
usage in `examples/` or `lib/` — the language may have no else, or a
different else syntax. Noted as a limitation; the single-`yadi` test above
suffices to prove the control-flow-dependent case (type depends on whether
the body executed, and the compiler crashes when it guesses wrong).

### Verdict on the root-cause claim

**The claim needs refinement.** It is not that "the compiler loses the type"
— for straight-line kosh assignments it **keeps** it (bounds check proves
it). It is that the compiler tracks the type as **may-hold** (ever assigned)
rather than **must-hold** (currently assigned at each use site), so it emits
wrong code when the current type differs from a previously assigned type, and
it has no rule for control-flow-dependent types (where the type depends on
whether a branch executed). The fix must be flow-sensitive MUST-tracking
(track the CURRENT type at each use site) **or** refuse reassignment to a
different type at compile time (a type error, not a segfault) **or** use a
runtime tag (dispatch at runtime, contradicting the proposal's "No runtime
tag"). The proposal's "statically track what was assigned to each `vitti`"
is ambiguous: if it means may-tracking (what was EVER assigned), it is wrong
(proven to crash); if it means flow-sensitive must-tracking (what is
CURRENTLY assigned at each use site), it is correct but harder — especially
for branches and loops, where the type is control-flow-dependent and the
tracking must either join (refuse, or tag) or duplicate code (emit both
paths). **The proposal as stated is incomplete: it does not address
reassignment or control-flow-dependent types.**

## WS2 — Does `mala` need a descriptor? The answer's conclusion is true for lifetime; its reasoning is incomplete, and its descriptor justification is wrong for aliasing.

### Mala is arena, not stack — and persistent, lexically, not dynamically

`mala_nava` allocates via `nirmmita` (arena bump), not from the stack. More
precisely, it allocates from the **persistent** arena, **lexically** (not
dynamically): `mala_nava` is defined outside any `mandapa` (in
`lib/mala.smlib`), so its internal `nirmmita` call is lexically outside a
`mandapa` → persistent, **even when `mala_nava` is called from inside a
`mandapa`**. Evidence: two malas created in two separate `mandapa` blocks are
at **different** addresses (`123571923845120` vs `123571923845152`,
difference exactly 32 bytes = one 4-element mala buffer) — sequential
persistent allocation, not scratch reuse (if they were scratch, the second
would reuse the first's address, difference 0). And the reuse probe (second
block writes `99`, then read the first block's mala) still prints `41`, not
`99`, confirming no reuse.

### Does a mala alias survive?

- **Returned from a `prakriya` (no `mandapa`, persistent):** prints `41`,
  survives (control, as expected).
- **Created inside a `mandapa`, assigned to an outer `vitti`, read after the
  block:** prints `41`, survives — **not refused, not garbage**. Because it
  is persistent (lexical), it legitimately survives block exit (not dangling).
- **Contrast — direct `nirmmita` inside a `mandapa`, assigned to an outer
  `vitti`:** **refused at compile time** (`E_SCRATCH_ESCAPE`: "asthayi smriti
  bahir na gacchati - mandapa-madhye nirmitam sthanam bahya-vittau na
  sthapyate"). The escape check **does** work for direct `nirmmita` (it
  refuses outer stores of scratch pointers). It does **not** refuse
  `mala_nava` stores — because `mala_nava` is a lib function, not a direct
  `nirmmita` call in the block, so the check does not know it returns a
  pointer at all — but since `mala_nava` is persistent, that bypass is
  **harmless for lifetime** (there is nothing to escape from, because
  persistent memory is never reclaimed). It is not a lifetime hole; it is a
  blind spot that happens not to matter for `mala` (but would matter for a
  lib function that allocated scratch).

### Verdict on the mala claim

- **The answer's conclusion (mala's alias is safe) is TRUE for lifetime** —
  and safe **beyond** the block close, not just until it, because `mala` is
  persistent (lexically), never reclaimed, fixed-size, never moves.
- **Its reasoning is incomplete:** it cites "never moves" but omits "never
  freed" (persistence, lexical not dynamic) and "fixed size" (no growth, so
  no relocation — unlike `kosh`, which grows and relocates at MAXCAP).
  "Never moves" alone does not guarantee safety (`kosh` also never moves
  until MAXCAP, but it **does** relocate then, breaking aliases). The real
  reasons `mala` is safe are persistence + fixed size, not just "never moves".
- **Mala does NOT have an alias cliff** (fixed-size, persistent, never moves,
  never freed, so its aliases never break) — so giving it a descriptor does
  **NOT** "close an alias cliff" (there is not one to close). The descriptor
  for `mala` would be for **bounds-checking** (which `mala` currently lacks
  entirely — direct and via `vitti`, `m[100]` and `a[100]` both print `0`, no
  refusal) and for **uniformity** (one mechanism), not for aliasing. Decision
  #2 ("Give `mala` the descriptor too, so both safe types share one mechanism
  and the alias cliff closes for both") is **unnecessary for aliasing** (no
  mala cliff exists) but **useful for bounds** (mala has none) and uniformity
  (a design choice, not a fix). Its justification ("alias cliff closes for
  both") is wrong for `mala`.
- **Decision #3 ("Restrict `nirmmita` to its `mandapa` region") is incomplete
  without addressing lib-function allocations:** the `mandapa` scratch
  mechanism is **lexical, not dynamic** — lib functions called from inside a
  `mandapa` still allocate persistent, because their source is outside. This
  is the Round 124 WS1(c) bypass (called procedures' persistent allocations
  are never charged and escape the block's rewind), now confirmed for
  `mala_nava` specifically. If `nirmmita` is to be restricted to its `mandapa`
  region, then lib functions that allocate via `nirmmita` need a rule (either
  they allocate persistent always — current behaviour, which means they
  escape `mandapa` bounds — or they must be treated as scratch when called
  from inside a `mandapa` — dynamic, not lexical, which is a bigger change:
  runtime tracking of caller context, or inlining, or a parameter).

## WS3 — The 2.2 ns number for `mala`: today's 10M-iteration loop, and what the descriptor would add

Measured today on v300 (Sutram, not C; both loops print the correct sum, so
the timings are for correct loops):

| Loop (10M iterations) | Today | Descriptor would add | Descriptor total |
|---|---|---|---|
| Sequential mala loop (1024 elements, wrapping counter, no division; sum 5114877120) | **0.074 s** (7.4 ns/iter) | **~0** (R125 array-loop difference ≈ 0, pipelined/hoisted, throughput-bound) | **~0.074 s** (no measurable increase) |
| Dependent mala chain loop (1024 elements as linked list via indices, `p = m[p]`; sum 5114877760) | **0.054 s** (5.4 ns/step) | **+22.4 ms** (10M × 2.240 ns, R125 hot dependent extra) | **~0.076 s** (+41%, 54 ms → 76 ms) |

**Correction to the brief's premise:** "if a descriptor adds 2.2 ns to it,
what does that cost in a tight loop?" assumes 2.2 ns per iteration applies to
a tight (sequential) loop. That is **wrong**. 2.2 ns is a **latency**
(dependent chain) cost, not a **throughput** (sequential loop) cost. For a
sequential loop, the descriptor adds ~0 (because the load is pipelined/hoisted
and the CPU does 2 loads/cycle). For a dependent loop, it adds 2.2 ns/step
(22 ms for 10M steps). **So `mala`'s "fast" reputation for sequential loops is
NOT threatened by descriptors (they are free there); for pointer-chasing
loops, the cost is real (+41% for 10M steps) but not catastrophic (54 ms →
76 ms).**

Caution: an earlier sequential loop using division for modulo
(`j - (j/1024)*1024`) took 0.328 s (32.8 ns/iter), but that was dominated by
integer division (25.4 ns/division), not by mala access. The wrapping-counter
version (0.074 s) is the clean measurement (no division); both print the same
correct sum, confirming the loops are correct and the difference is division
overhead, not mala access.

## Summary: which claims survive

| Claim | Verdict | One-line reason |
|---|---|---|
| Vitti loses the type (compiler cannot tell) | PARTLY FALSE, PARTLY TRUE | False for kosh (bounds check proves it tracks, straight-line); true for mala vs raw (both unchecked, indistinguishable); and worse: for reassignment/control flow it tracks as may-hold and crashes (segfault) instead of updating or refusing |
| Mala never moves, so alias is safe until block closes | TRUE for lifetime, INCOMPLETE reasoning | Safe beyond the block close (persistent, lexical, fixed-size, never freed) — not just "never moves"; and the descriptor for mala is for bounds (which it lacks), not for aliasing (no mala cliff exists) |
| Mala needs the descriptor too (alias cliff closes for both) | UNNECESSARY for aliasing, USEFUL for bounds/uniformity | No mala alias cliff exists (fixed-size, persistent, never moves); descriptor would add the bounds check mala currently lacks, and one mechanism — a design choice, not a fix |
| Restrict nirmmita to its mandapa region | INCOMPLETE without lib functions | Mandapa scratch is lexical, not dynamic: lib functions (mala_nava) called from inside a mandapa still allocate persistent and escape the block's rewind/budget (R124 WS1(c) bypass, confirmed for mala_nava) |
| Descriptor adds 2.2 ns to a tight mala loop | WRONG for sequential, TRUE for dependent | Sequential 10M loop today 0.074 s, descriptor adds ~0 (throughput-bound); dependent 10M chain today 0.054 s, descriptor adds ~22.4 ms → ~0.076 s (+41%) |

## NOT RUN

Windows execution (cannot run Windows; v300's lazy commit is Windows/PE and
does not affect these Linux results — verified by identical WS1 results on
v299 and v300), browser, implementation (none authorized — test and analysis,
not building the tracking or descriptor designs), native-speaker review, full
suite (no tree changes; the v300 suite numbers stand, not re-run here).
The `anyatha`/else syntax was not resolved (zero usage in examples/lib);
the control-flow case was proven with a single `yadi` instead, which suffices.
