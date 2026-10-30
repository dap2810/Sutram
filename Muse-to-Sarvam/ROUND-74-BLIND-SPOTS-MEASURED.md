# ROUND-74 — the R73 blind spots, measured against the built check

Base: origin/main `b667bd9e` (compiler v270 —
Step 4 check + redirect shipped). No tree
changes. Every verdict below was compiled and
run on v270; the R73 probe programs were
recreated under `~/workspace/r74/` after /tmp
was wiped by a restart.

Sarvam's stated verifications re-confirmed
first: `outer = buf + 64` refused (local
target), `m[0] = buf` refused (outer
container), plain block compiles, copying DATA
out compiles (`outer = buf[0]` prints `42`).
The R73 flat test on v270: baseline 7 MB,
control 61 MB, subject **7 MB** — flat
(S − B = 0), against Sarvam's 65,216 KB /
14,464 KB on his program. Same conclusion,
different absolutes.

## WS1 — the five R73 shapes against v270

| # | Shape | R73 predicted | v270 verdict |
|---|---|---|---|
| 1 | Scratch → function → global | Missed unless K0 call rule | **MISSED** (compiles, runs) |
| 2 | Scratch → kosh of pointers | Missed unless K1 retain-table | **CAUGHT** (E_SCRATCH_ESCAPE) |
| 3 | Scratch → rachana return | Caught / caught-by-B / missed-via-call | **CAUGHT in all 3 forms** |
| 4 | `buf + 64 - 64` identity | Caught by kind propagation | **CAUGHT as identity; see global note** |
| 5 | `buf == other` comparison | Harmless, no false positive | **NO FALSE POSITIVE** (compiles, prints 0 then 9) |

### 1. The one live miss: calls into globals

`stash(b)` storing `b` in global `g` compiles
and runs on v270, exactly as R73 predicted for
bare rules A–E. The built check did not ship
the K0 call rule (or it does not cover this
path): a call is not a store, and inside
`stash` the parameter has kind none.

**Miss consequence: silently reads the wrong
memory — proven, not hypothesized.** After the
block, a second `mandapa` allocating fresh
scratch reuses the same space; the global then
reads `99` and `98` (the new frame's values),
not the `42` it stored. No crash, no fault —
pure silent data corruption. This is possible
precisely because old buffers are never
unmapped (the arena): a dangling scratch
pointer reads whatever reused the space. The
check's value is exactly that it prevents this
silent class; this hole leaves it open.

The same hole, narrowed: the check does not
model **globals** as escape targets at all.
`g = buf + 64` with `g` global compiles, while
`outer = buf + 64` with `outer` local is
refused. So shape 4's R73 probe (which used a
global target) missed via the global hole, not
the identity hole — the identity itself is
caught (local target + `buf + 64 - 64`
refused). The remaining hole family is
**globals + calls**, not arithmetic.

One boundary that closes part of the call
family: a scratch pointer cannot be smuggled
into a kosh through a callee, because kosh
parameters are refused ("kosh prakriya hetu
kosh-vitti avashyak") and top-level kosh
declarations do not parse — the
stash-into-kosh shape is inexpressible, so
the call hole is effectively globals-only.

### 2. Kosh: caught — the retain-table (or equivalent) shipped

Direct `kosh_push(k, b)` with `b` scratch is
refused (`smritau na likhyate` — "not written
to memory"). R73 said "caught only by K1";
K1 or an equivalent kosh-store rule is in the
built check. Variable aliases do not launder
it either: `q = b; kosh_push(k, q)` refused.

### 3. Rachana: caught in all three forms — stronger than predicted

- Direct return of a block-allocated rachana:
  refused (as in v268).
- Outer-rachana field store (`r[0] = b`, `r`
  outside): refused (rule B, as predicted).
- Call-laundered return (`nivartanam wrap(r)`):
  **refused** — R73 predicted missed (rule D
  kind none), but the built check sees through
  a call that returns its argument. The check
  is stronger than bare rules A–E here.

### The unified rule the built check actually enforces

Probing the boundary further: a scratch
pointer stored into a block-kind container
used only inside the block (`r[0] = b`, no
escape) is **refused** — stricter than R62's
rule B as I described it (which allowed
stores into block-kind containers). But a
scratch pointer aliased through a variable
(`q = b; likha(q[0])`) **compiles**. So the
rule is: **scratch pointers may live in
variables (kind-tracked) but never in memory
(untracked)** — because container reads have
kind none, any pointer in memory could be
laundered on read. That single rule explains
shapes 2, 3, and the 215 refusal below.

### The Sanket caveat, read against the evidence

Every `E_SCRATCH_ESCAPE` refusal now carries:
"Sanket: ayam parikshah prakriya-ahvane
kosh-madhye va gacchantam sthanam na
pashyati" ("this check does not see a place
going into a function call or into a kosh").
It is honest but broad: the direct call-return
and direct kosh paths ARE seen (shapes 2, 3),
while the indirect call-store path (shape 1,
into globals) is NOT. The caveat warns about
the right hole family; its kosh clause is
forward-looking (or covers call-mediated kosh
paths) rather than descriptive of direct
`kosh_push`, which is refused.

## WS2 — false-positive census, empirically

Method: for each example, wrap each function
body containing a `nirmmita` allocation in a
`mandapa` (braced bodies: `mandapa { ... }`;
indented bodies: `mandapa` line + re-indent)
and compile with v270. Excluded from the
census: examples already containing `mandapa`
(263–269, the R72/R73 mandapa tests — wrapping
them again double-wraps and refuses 269 as an
artifact, not a finding), pre-existing
compile-fail tests (224/234/235 field errors,
259), and examples with no `nirmmita` in a
function body (kosh-only and no-alloc
examples — `mandapa` does not apply to them).

**Clean census: 14 wrappable examples — 13
compile wrapped, 1 refused.**

**The 1 genuine refusal: `215_r12_wordfreq`.**
Wrapped, it refuses at `uptrs[nuniq] = wbuf +
wpos` — a scratch pointer (`wbuf + wpos`,
arithmetic on scratch) written into scratch
memory (`uptrs`). Its pattern is a **pointer
table**: an array of pointers into a packed
buffer. That pattern is refused **by design**,
not by a check bug: under the unified rule
above, no scratch pointer may be written to
memory, because a later read would launder it.
215 is a valid program unwrapped (its buffers
are persistent, correctly) — `mandapa` is
simply the wrong tool for a pointer table.
The v1.0 scope says it plainly (MEMORY-DECISION:
"a few temporary buffers of plain numbers").

**No common pattern is falsely refused.**
The 13 that compile wrapped include the loop
allocations (258), the report buffers (217),
the method tables (247), and the long-variable
example (237). The four positive mandapa
tests already in-tree (266 inside-only, 267
outer number, 268 value return, 269 data
copy-out) all compile as written, and the two
negative mandapa tests (264 arithmetic escape,
265 mala escape) refuse as designed.

## WS3 — recursion, 1000 deep: per-frame marks hold, RSS flat

Program: `rec(d)` with a `mandapa` inside,
allocating 1024 bytes per frame, writing its
own depth, recursing to `d - 1`, then adding
its scratch value to a global checksum after
the recursive call returns — the read-after-
return is what a non-per-frame mark would
corrupt (an inner frame's rewind truncating
an outer frame's scratch).

| Program | Checksum | Peak RSS |
|---|---|---|
| `rec(1000)` once, mandapa | 500500 (sum 0..1000) ✓ | 7 MB (= baseline) |
| `rec(1000)` × 10, mandapa | 5005000 (10 × 500500) ✓ | 7 MB (flat across reps) |
| `rec(1000)` × 10, no block (control) | 5005000 ✓ | 11 MB (grows with reps) |

**The per-frame mark holds.** Every frame's
scratch value survived its recursive call —
1001 frames × 10 repetitions, checksum exact.
If the mark were a single global, inner
rewinds would clobber outer frames' scratch
and the checksum would be wrong. **RSS stays
flat across repetitions:** the mandapa peak is
identical for 1 rep and 10 reps (7 MB), while
the control grows with reps (11 MB) — the
cursor is fully restored between top-level
calls, and deep recursion does not corrupt it.
(The control's growth, 4 MB vs 10 MB
theoretical, reflects the sandbox's
`ru_maxrss` under-reporting noted in R73;
the direction — mandapa flat, control growing
— is unambiguous.)

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.
- Implementation: no code was changed; the
  remaining globals/call hole is a Step 4
  follow-up for its owner (K0 call rule or
  global tracking), not a Muse-side fix.
