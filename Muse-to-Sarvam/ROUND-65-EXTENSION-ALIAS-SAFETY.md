# ROUND-65 — in-place extension is alias-safe (memory), coherent only when in place; the kept leak is small

Base: origin/main `f0714d09` (v416 decision: Step 0 stopped,
bins dropped, extension only), compiler v261.
Read first: `docs/decisions/MEMORY-DECISION.md` (the correction),
`Claude-to-Sarvam/R64-00-STEP0-STOPPED.md` and
`evidence-r64/`, my ROUND-59 (kosh surface) and ROUND-62
§3.3 (exhaustion split).

Design + measurement. No tree changes. The mechanism under
test does not exist yet (it needs the Step 1/2 persistent
cursor), so the proof is in two parts: (a) a representation
argument from the mechanism's stated check — `old_ptr +
old_capacity == persistent_cursor` — plus the kosh
representation as it exists in source; (b) programs built
and run under today's compiler, which is the pure-relocation
regime, establishing the baseline semantics that extension
must preserve or improve. Where today's behavior and the
extension regime differ, I say so and give both outputs —
because for aliasing programs they genuinely differ, and
that difference is the point, not a footnote.

## 0. The representation: three lemmas

These are facts about the compiler as it exists, checked in
source, not assumptions:

- **L1 — a handle is one base pointer; the header lives in
  the buffer.** A `kosh` variable holds a base pointer.
  The header (`[base]` = len, `[base+8]` = cap) and the
  elements live in the allocation itself (emitter
  `.ge_call_koshpush`, `:15651` and following; growth at
  `:15720-15900`). Every handle to the same buffer — a
  `vitti` alias, a parameter, a `mala` cell, a `rachana`
  field — shares that one header. There is no per-handle
  len/cap.
- **L2 — in-place growth touches only the header's cap (and
  the cursor).** Under the stated check, extension appends
  capacity at the buffer's end. No handle's stored pointer
  changes (there is nothing to update — the base is the
  same). No memory is freed, unmapped, or handed to another
  allocation. Existing elements do not move.
- **L3 — relocating growth touches only the growing
  handle.** Today's growth allocates a new block, copies
  elements, writes the new header, and stores the new base
  into the growing handle's slot only. Every other handle
  keeps the old base. The old buffer is never unmapped
  (zero `munmap` anywhere in `src/` or `win/`, ROUND-59)
  and, with the bins dropped, never reused.

**Theorem (memory safety).** In every case below, every
handle denotes valid memory holding a valid kosh header and
elements. Nothing dangles, nothing is corrupted, no handle's
memory is ever given to another allocation. This holds
under in-place growth (L2) and under relocating growth
(L3).

**Theorem (coherence, strictly weaker).** All handles agree
— same len, cap, elements — if and only if every growth
since aliasing was in place. Relocation diverges handles
into stale copies. Coherence is a semantic property, not a
safety property, and the two theorems must not be confused:
extension is memory-safe in all four cases; it is coherent
only in the in-place subcases. Today's regime is safe but
*never* coherent across a growth; extension makes the
common case coherent.

## WS1 — the four cases

### Case 1: two aliases, one grows in place, then the other grows — SAFE, second growth also in place (if nothing allocated between)

Program P1 (Claude's invariant-1 program, extended with a
second round of growth), run today (all growth relocates):

```
kosh k[1]; push 7; vitti a = k; push k 8, 9; a[0] = 99
→ a[0]=99, k[0]=7, len(a)=2, len(k)=3   (after push a 5)
→ push k 10: len(k)=4, len(a)=2, a[1]=5
```

Two live buffers, fully functional, diverged. Under
in-place extension with no interleaving allocation, the
same program prints something *different* — and the
difference is the fix:

```
→ a[0]=99, k[0]=99, len(a)=len(k)=4     (after push a 5)
→ push k 10: len(k)=len(a)=5, a[1]=8
```

`a[0] = 99` writes the shared buffer, so `k` sees it; the
lengths never diverge; `a[1]` is 8 (the shared second
element), not 5. **The second growth also extends in
place**: after `k`'s in-place growth the block is still
topmost (its extended end *is* the cursor), and `a`'s
growth addresses the same block, which is still topmost —
so the same check passes again. The condition is sharp:
if anything allocates between the two growths, the block is
no longer topmost, the second growth relocates, and the
handles diverge (safe, stale — exactly today's behavior
for that growth). **Verdict: SAFE in all subcases;
coherent iff no allocation interleaves between the
growths.**

Note the semantic consequence, stated plainly: in-place
extension is *not* behavior-preserving for aliasing
programs. It changes what aliasing programs print (from
divergence to coherence). That is the intended semantics —
R42: "an alias of a kosh is the kosh" — but any golden
depending on growth-divergence would change. I checked:
no tree golden does. The only alias goldens are
`252_r38_alias_kosh_oob` (alias + bounds, no growth) and
`255_r42_alias_kosh_push` (alias push, no growth — see
below); neither exercises growth-divergence.

### Case 2: a `kosh` passed to a `prakriya` that pushes — TODAY REFUSED, and in-place extension does not lift the refusal

Verified by compiling it:

```
prakriya dhakka(kosh k) { kosh_push(k, 99) }
→ Sutram Error: kosh-tarke kosh_push asamarthitam
```

Source reason (`.ge_call_koshpush`, `:15651` and the
`is_kosh_param_var` check): the callee holds its own copy
of the pointer, and a relocating growth would update only
the callee's copy — "the callee's pointer without updating
the caller, so kosh_push is rejected on parameters until a
deliberate reference ABI is introduced."

Under in-place extension the *subcase* analysis is:

- Growth in place: the callee's push extends the shared
  buffer; the caller's variable (same base, shared header)
  sees the new length and elements. Safe AND coherent —
  in-place growth is exactly the case where the missing
  reference ABI does not matter, because there is nothing
  to update.
- Growth relocating: the callee's slot gets the new base;
  the caller's variable keeps the old base. The callee's
  pushes are invisible to the caller (lost from the
  caller's view) — stale, not dangling, but a silent
  semantic bug, worse than today's loud refusal.

**The refusal must stay.** At-cursor is a *runtime*
property — the compiler cannot prove, at the call site,
that the passed kosh will be topmost at every push inside
the callee (that depends on the whole allocation history).
So in-place extension does not fix the parameter case in
general; it fixes only the in-place subcase, which cannot
be distinguished statically. Lifting the refusal would
trade today's compile error for a silent lost-push bug on
the relocating path. If parameter-push is ever wanted, it
needs what the source comment already says: a deliberate
reference ABI (or a rule that a kosh parameter's growth
must be in place, enforced at runtime with a fallback
diagnostic — a language change, not a Step 1 detail).

Two adjacent facts, both verified: a callee that only
*reads* a passed kosh is fine in both regimes (shared
buffer, no growth). A callee that *stores* the passed kosh
in a global, after which the caller grows (R59 case E):
today the global reads the old block (stale, safe); under
in-place extension it reads the current buffer (coherent).
Same pattern as case 1.

### Case 3: a `kosh` stored inside a `mala` or a `rachana` — SAFE; the cursor check does not care where the pointer lives

Program P3 (mala cell + rachana field), run today:

```
kosh k[1]; push 7; m[0] = k; d.k = k; push k 8, 9
→ b = m[0]; b[0] = 7      (old block)
→ c = d.k;  c[0] = 7      (old block)
→ kosh_len(k) = 3
```

**The extension check is per-buffer, not per-variable.**
It compares `old_ptr + old_capacity` (the *current*
capacity, from the shared header — not the declared
capacity) against the persistent cursor. A pointer stored
in a `mala` cell or a `rachana` field yields the same base
as the variable, so the same check answers the same way:
if the buffer is topmost, it extends, and every stored
handle sees the larger buffer (same base, shared header);
if not, it relocates, and stored handles go stale (today's
7). **The storage location is irrelevant to the check.**
Verdict: SAFE in both subcases; coherent iff in place.

One refinement the brief's question invites, verified by
bisecting the compiler's refusals: a handle *retrieved*
from a mala cell or a rachana field can be read through
(`b[0]` works — indexing is untyped pointer arithmetic),
but kosh builtins on it are **refused**:

```
vitti b = m[0]; kosh_len(b)   → kosh prakriya hetu kosh-vitti avashyak
vitti b = m[0]; kosh_push(b, 5) → same refusal
```

The R38 kind propagation marks `vitti a = k` as a kosh
variable, but it does not propagate through a container
read — so a retrieved handle is not a kosh variable for
builtin purposes. That *limits* the case-3 surface: stored
handles are read-only views (for builtins); growth happens
only through true variables and `vitti` aliases. A stored
handle therefore cannot itself trigger the growth whose
safety is in question — it can only observe it, and
observation is safe in both regimes.

### Case 4: the block is NOT at the cursor — relocation, two buffers, stale copy, NOT a dangling pointer — YES, proven by today's regime

This case needs no new argument, because **today's regime
IS this case**: every growth today relocates (there is no
cursor, no extension). P1 and P3 above are case-4
programs, and their old buffers are not merely
still-mapped — they are still fully functional koshes
(`a` grows independently to len 2, `a[1] = 5` reads back;
`b[0]` reads 7). The mechanism is L3 plus two absences:
no `munmap` (so the old mapping survives) and no reuse
(bins dropped, so the old address is never handed to
another allocation). **Stale, not dangling — proven, not
asserted.**

**The forward invariant this depends on, which must be
recorded with the design:** an old kosh buffer must never
be unmapped or reused while it can still be named. Today
that holds by absence (no free primitive, no bins). The
day a free primitive arrives, it must respect this — a
`munmap` of a buffer with live aliases turns every stale
copy in this report into a use-after-free. That is the
same warning R59 gave for the `munmap`-on-move fix, and it
applies unchanged to any future reclamation: reclamation
needs alias knowledge (or a refusal, as the parameter case
has), not just a free list.

### The breaking case I hunted and did not find

I tried to break *memory safety* (not coherence) and
could not, for structural reasons: single-threaded
execution (no races on the cursor or header); the header
is shared, so no handle can observe a torn length;
extension appends capacity without moving elements; the
cursor check, correctly implemented, is exactly the
condition "nothing sits above this block." The genuine
risks are implementation conditions, not design flaws, and
they should be written into the Step 1 spec:

1. The check must use the **current header capacity**,
   not the declared capacity (declared 3 → current 12
   after growth; using 3 would miscompute the block's
   end).
2. Extension failure (arena exhausted) must fall back to
   relocation — never a partial extension, never a silent
   truncation.
3. The check must be against the **persistent** cursor
   (dvi-mukha: kosh lives on the persistent side), not
   the scratch cursor.
4. `--fail-alloc` numbering changes when extension skips
   an allocation (Claude's note; the r38 baselines that
   count growth allocations must be re-baselined, not
   silently broken).

If any of those four is violated, extension can overwrite
the next allocation — but that is a bug in the check, not
a counterexample to the design. Under the stated check,
there is no aliasing case that breaks memory safety.

## WS2 — extendable vs not: the rate, simulated exactly

Method: a bump-cursor simulator over explicit push
sequences, using the growth policy verified on v261
(`newcap = cap*2`, else 4 — checked against Claude's
table: `k[3]` → 12 after 9 pushes, `k[1]` → 16,
`k[5]` → 10, `k[1000000]` → unchanged). A growth is
extendable iff the growing kosh is the most recently
allocated-or-grown block at that moment. These are
**projections for the Step 1/2 cursor design**, not
measurements of today's allocator (which has no cursor) —
stated so the numbers are not misread as observed.

| Sample | Growths | Extendable | Rate |
|---|---|---|---|
| S1: single kosh, loop ×1000 | 10 | 10 | 100% |
| S2: two kosh interleaved, ×1000 each | 20 | 0 | 0% |
| S3: three kosh round-robin, ×1000 each | 30 | 0 | 0% |
| S4: single kosh + one other allocation per iteration, ×1000 | 10 | 0 | 0% |
| S5: single kosh, 3 pushes/iteration | 10 | 10 | 100% |
| S6: two kosh phased (1000 then 1000) | 20 | 18 | 90% |
| S7: decl a, b; push a ×10 only | 4 | 3 | 75% |

**The rule in one sentence:** a growth is extendable iff
nothing has allocated since that kosh's last allocation
or growth. That is why S2/S3 are 0% (after the first
cycle, every growth finds another kosh on top), why S4 is
0% (even a *single* kosh loses extendability if anything
else allocates in the loop — the loop's other allocation
is always on top at growth time), and why S6 is 90%
(only the first growth of each phase relocates — the
phase's kosh is not top yet — and every later growth in
the phase extends).

**What this buys, in bytes:** a single-kosh 1,000,000-push
program grows ~20 times with abandoned ≈ final capacity
(~8 MB, Claude's measurement: 16.0 MB total, ~8 MB
abandoned). With extension, all 20 growths extend: the
abandoned term goes to ~0, and the program's footprint is
just its final buffer. An interleaved 1,000,000-push ×2
program grows ~40 times with abandoned ≈ 2× final
capacity (~16 MB); extension saves ~0 of it. **So the
answer to "is it worth building": yes for the single-kosh
loop (the common case the decision doc names), no for the
interleaved loop — and the two cases are cleanly
separated by the one-sentence rule, so there is no
judgment call at build time.**

## WS3 — the leak we keep: 1 interleaved program in `examples/`, and it is small

Scope as briefed: `examples/` (229 programs; 36 use
`kosh_push`). Six push to ≥2 distinct kosh variables;
hand-checked for interleaving (same loop, alternating)
versus phasing (separate blocks/loops):

| Example | Shape | Interleaved? |
|---|---|---|
| `208_kalana.sm` | one loop pushes `ank_suchi` + `ys` alternately | **YES — the only one** |
| `118_t18_kosh_param.sm` | `mulya` block, then `nums` block | No (phased) |
| `126_numeric_pipeline.sm` | `mulya`, then `u`, then `v` blocks; its 100,000-iteration loop only reads (`maap`) | No (phased) |
| `207_sankhyiki_vector.sm` | `a`, then `b`, then `c` blocks | No (phased) |
| `209_samanvaya.sm` | `a`, `b` blocks; `c` loop and `id` loop each push one kosh | No (phased; single-kosh loops) |
| `255_r42_alias_kosh_push.sm` | `v` and `w` are aliases of ONE buffer (no growth in the program) | No (not two koshes) |

**The kept leak in the tree is therefore one program,
`208_kalana`**: `ank_suchi[4]` + `ys[4]`, 11 iterations,
2 growths each, all 4 relocating under the model
(neither is ever top at its growth — verified by the same
simulation). Abandoned: the cap-4 (48 B) and cap-8 (80 B)
buffers per kosh, ~256 B total. Small, because the loop is
short. The phased examples' growths are mostly extendable
(S6: only the first growth per phase relocates).

The honest scope note: the tree's examples contain no
*long* interleaved loop, so the kept leak's size in the
tree is small — but that is a property of these examples,
not of the design. A long interleaved loop (server code
accumulating into two vectors per request) would leak at
~2× final capacity and extension would save none of it.
The decision doc's framing stands: a bounded leak, kept
knowingly, is better than a use-after-free. What this
round adds is the bound's shape: the kept leak is exactly
the interleaved (and alloc-mixed, S4) growths, and nothing
else.

## Verdict (for the build decision)

- **Build in-place extension (after Step 2, ~20 lines at
  the growth site, per Claude).** It is memory-safe under
  every aliasing shape in WS1 — the proof is L1–L3 plus
  the run programs, and no breaking case exists under the
  stated check (only the four implementation conditions
  in §WS1, which belong in the spec).
- **Keep the parameter-push refusal.** Extension does not
  lift it, for the runtime-property reason in case 2.
- **Keep the kept leak named as bounded:** interleaved
  and alloc-mixed growths only; in the current tree, one
  short example (~256 B); the single-kosh loop — the
  common case — is fully fixed.
- **Record the forward invariant with the design:** a kosh
  buffer is never unmapped or reused while it can still be
  named. Any future free primitive must respect it.

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.
- The Step 1/2 cursor itself: it does not exist yet, so
  the WS2 rates are simulations under its stated check,
  not runs of an implementation; the WS1 run programs
  execute under today's relocating compiler and establish
  the baseline semantics, not extension behavior.
- Implementation: no compiler code was changed.
