# ROUND-73 — Step 4's blind spots, found before it is built

Base: origin/main `e03f6dce` (compiler v268 —
`mandapa` inert, `E_SCRATCH_ESCAPE` live). No tree
changes. All five WS1 shapes were compiled and run
on v268; the check itself does not exist yet, so
"caught" below means caught by the check as
designed (Claude's rules A–E + K0
unknown-rejection + K1 retain-table, per R62/R63),
and "missed" means the designed rules do not see
it. Since `mandapa` is inert today, every shape
below runs harmlessly now — a "silently wrong"
verdict means: once rewind ships, an uncaught
escape becomes a pointer into reused scratch
(wrong data, no crash).

Reference for the rules: A = assignment of a
block-kind value to an outer variable, refused;
B = store of a block-kind value into an outer
container, refused; C = return of a block-kind
value, refused; D = calls have kind none (the
returned value's provenance is unknown); kind
propagates through `+`/`-` (a block-kind operand
makes a block-kind result); container reads have
kind none (R62's hole #3).

## WS1 — the five shapes

### 1. Scratch passed to a function that stores it in a global: MISSED by the store rules

Probed: `stash(b)` stores `b` in global `g`;
after the block, `g[0]` reads `42` — the escape
is real and observable. Why the check misses it:
at the call site, a call is not a store (rules
A/B see assignments, not calls); inside `stash`,
the parameter has kind none, so its store into
`g` is not a block-kind store either. Both sides
of the escape are invisible to rules A–E.

Contained only by the call rule: under K0
(unknown = rejection), passing a block-kind
argument to a callee without a verified
non-retaining summary is rejected — fail-safe,
at the cost of refusing calls the callee would
not retain (the K1 summaries narrow that). If
Step 4 ships bare rules A–E without the K0 call
rule, this shape is **silently wrong** after
rewind: the global dangles into reused scratch.

### 2. Scratch stored in a kosh of pointers: MISSED — ChatGPT's "invisible" confirmed

Probed: `kosh_push(k, b)` inside the block,
`k[0]` retrieved after it, `h[0]` reads `42`.
Invisible for three independent reasons:

1. **The store is a call, not an assignment.**
   Rules A/B do not model builtin calls as
   stores (same gap as shape 1).
2. **A kosh has no element type.** `kosh k` holds
   qwords; the check cannot tell "kosh of
   pointers" from "kosh of ints", so it cannot
   even frame the question without tracking the
   pushed value's kind through the call — which
   rule D forbids (kind none).
3. **K0's kosh exclusion does not contain it by
   itself.** K0 excludes kosh from *checked*
   functions — but rewind is a codegen property,
   not a check property. Unless rewind is gated
   on checking, an unchecked function with a
   `mandapa` and a `kosh_push` still rewinds
   around a live escape.

Caught only by the K1 retain-table (which lists
`kosh_push` as retaining its value argument).
Without it: **silently wrong** after rewind (the
kosh element dangles; kosh growth relocating the
kosh itself is a second, separate hazard).

### 3. Scratch returned inside a rachana: caught twice, missed once

Three forms, probed separately:

- **Direct** — the rachana itself is
  block-allocated (`r = nirmmita(16); r[0] = b;
  nivartanam r`): **CAUGHT ALREADY.** Step 3's
  refusal fires today: `E_SCRATCH_ESCAPE`
  ("asthayi smriti bahir na gacchati").
- **Outer rachana, field stored inside** (`r`
  allocated outside, `r[0] = b` inside, `r`
  used after): compiles today (`h[0]` reads
  `42`); **CAUGHT by rule B** when Step 4 ships
  (store into an outer container).
- **Laundered through a call** (`nivartanam
  wrap(r)`, where `wrap` returns its argument):
  **MISSED — compiles today, exit 0.** Step 3's
  refusal keys on the returned expression being
  a scratch address; a call result is not one,
  and rule D gives it kind none. After rewind,
  the returned rachana's field dangles:
  **silently wrong**.

So the shape as stated is mostly caught; its
call form is the hole — the same rule-D hole as
shapes 1 and 2.

### 4. Arithmetic identity `buf + 64 - 64`: CAUGHT by design

Probed: `g = b + 64 - 64` inside the block,
`g[0]` reads `42` after it — the identity
preserves the pointer exactly, so catching it is
correct, not a false positive. The design
catches it because kind propagates through
arithmetic: `kind(e1 + e2)` is block if either
operand is block, so `buf + 64` is block and
`(buf + 64) - 64` is block, and storing it
outside trips rule A.

Dependency to record: this holds only if
arithmetic kind propagation ships. If Step 4
propagates kind through assignments alone, the
identity launders the pointer to kind none and
the shape becomes **missed, silently wrong**.
The propagation rule is load-bearing, not
incidental.

### 5. Comparison `buf == other`: HARMLESS, no false positive

Probed: the comparison runs, prints `0` (not
equal), execution continues normally. A
comparison stores nothing, creates no alias,
and yields a boolean (kind none) — the check
flags stores and returns of block-kind values,
not uses, so there is nothing to false-positive
on. Two caveats, neither a false positive:
comparing `buf` *after* the block is a
use-after-rewind question (a scope/lifetime
check, not Step 4's escape check), and a
comparison that *conditions* a store is caught
as the store itself.

### The pattern

All three holes are rule-D-shaped: **calls erase
kind.** The store rules (A/B/C) plus arithmetic
propagation cover every syntactic escape; every
miss goes through a call boundary (argument,
builtin, or return). Recommendation: ship Step 4
**with** K0's call rule (reject block-kind
arguments to callees without verified
non-retaining summaries) and the K1 retain-table
for library builtins — not bare rules A–E.
Without the call rule, shapes 1, 2, and
3-laundered are live on the first day rewind
ships. Keep the debug fail-stop (no-rewind +
mprotect in `--debug`, R62) as backstop, not
closure.

## WS2 — false-positive census: 0

Question as operationalized: an example would
be refused if wrapping its allocation's enclosing
block in a `mandapa` left the pointer needed
outside that block (used after the block,
returned, or stored globally/outside).

**Count: 0 of 234 examples** (0 of the 231
Sarvam named; the 3 newer ones are block-shape
tests whose allocations stay inside their
blocks).

Checked both scopes: no example allocates
inside a control block and uses the allocation
after that block, and no example returns a
freshly allocated block or stores one globally
(R66's count-3 result, re-verified). Kosh
declarations are function-top-level, never in
blocks. The check's refusal set does not
intersect any example's actual structure — so
no common pattern would be falsely refused,
and the "pattern is wrong in the design"
warning does not trigger. Boundary note: lib
constructors return persistent blocks, but they
do not use `mandapa`, so the check does not
touch them; the census is about `mandapa`-wrapped
code only. The canonical `263_r72_mandapa`
example uses its scratch inside only, as designed.

## WS3 — the flat-RSS test, designed and harness-validated

### The program (exact)

```sutram
mukhya() {
    vitti s = 0
    vitti i = 0
    yavat (i < 1000000) {
        mandapa {
            vitti b = nirmmita(64)
            b[0] = i
            s = s + b[0]
        }
        i = i + 1
    }
    likha(s)
}
```

`mandapa` inside the loop body (parses on v268;
the block is per-iteration, so each iteration's
scratch must be reclaimed). The checksum `s`
printed at the end must equal **499999500000**
(sum 0..999999) — it proves the allocations
were live, not eliminated. The control is the
same program with the `mandapa` lines removed;
the baseline is a trivial program printing `0`.

### The harness (exact)

A Python driver that, per program, `fork`s,
`exec`s the binary with stdout discarded, and
`wait4`s for that child's `ru_maxrss` (peak RSS,
KB). One fresh process per measurement — do NOT
use `RUSAGE_CHILDREN`, which maxes across all
waited children and would contaminate the
readings. Measure baseline B, control C, and
subject S in the same run, on the same machine.

### The assertions (exact, relative — floors vary)

- **S − B < 8 MB** — flat: at most a few live
  blocks plus page slack.
- **C − B > 48 MB** — the control proves the
  test can see growth (1M × 64 B ≈ 61 MB).
- **Subject output = 499999500000, exit 0** —
  allocations were live and correct.
- If S − B ≥ 8 MB after the redirect, the
  redirect leaks (rewind not reclaiming per
  iteration).

### Validated today (pre-redirect, v268)

| Program | Peak RSS | Output |
|---|---|---|
| Baseline | 7 MB | 0 |
| Control (no block) | 61 MB | 499999500000 |
| Subject (inert `mandapa`) | 61 MB | 499999500000 |

The subject equals the control exactly
(505 bytes both ways — inert confirmed), so
**the test FAILS today by design** (S − B =
54 MB, not < 8 MB) and will pass only when the
redirect ships. Two measurement notes: the
observed growth (54 MB) is below the
theoretical 61 MB — `ru_maxrss` under-reports
in this sandbox (cf. R67) — which is why the
assertions are relative with 6× margins between
the bars (8 vs 48), not absolute; and the
control bar (48 MB) still passes despite the
under-reporting, so the test discriminates.

The test must be marked expected-fail (or
skipped) until the redirect lands; after that
it is the gate for "redirect works".

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.
- Implementation: no code was changed; Step 4 and
  the redirect belong to Claude's parallel brief.
  The WS3 test program above is a design, not a
  committed test — it becomes a test when the
  redirect ships.
