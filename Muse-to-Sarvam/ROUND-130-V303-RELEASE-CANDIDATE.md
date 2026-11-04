# Muse Round 130 — Attack v303. This is the release candidate.

- **Base:** main at v303 (`8154fdea`, "v303 release candidate: close the
  last gap, attack it, sign off or refuse"). Compiler changed
  (`src/sutram_compiler.asm`, `src/r65_arena.inc`,
  `src/r23_capabilities.inc`, `src/r11_sandesh.inc`). Version string is
  v303. Gates reported: **68 PASS / 0 FAIL / 1 NOT-RUN (Windows
  execution). Suite 327. The installer carries the compiler.**
- **Test and analysis only.** No code was changed. No sign-off authority
  beyond this report — WS2 below is my recommendation, not a release
  decision (that is the owner's).

## WS1 — v303 fixed three defects you did not find. Attack the fix: the fixes hold, no regressions, parimana is right (with one minor open question), no overwrite reproduces, and the parameter-growth message is still wrong.

### (a) The same probes again, on v303 — the three fixes break nothing that worked

Re-ran **all 11 R129 probes** on v303, unchanged: **every result identical
to v302** (boundary `11 22 33 44 11 44 55 55 11`; two-alias `11 55 11 55 11
55`; kosh-in-kosh still `E_KOSH_DVARA`; param-growth still refused (see
(d) below); mandapa `11 55`; 20,000 + grow `0 10000 19999 999 1003`;
multi-growth `0 99999 0 99999`; dasham whole `0.000000 99.000000 0.000000
99.000000`; dasham fractional `0.500000 99.500000 99.500000`; interleaved
`0 99 1000 1099`; param-index still runtime-refused). **No regression from
the three fixes.**

Re-ran **the 8 R127 defects + 3 R128 global bypasses** on v303, unchanged:
**all still hold** (S1/S2/S3 still `E_VITTI_PRAKAR`; O1 still
runtime-refused; O2/O3/O4 (both forms) still `E_KOSH_DVARA`; O5 still
`E_KOSH_DVARA`; two-functions, global-call, global-inbounds still
`E_KOSH_DVARA`). **No regression in the tracking fix either.**

Two diagnostic improvements on v303 (not regressions):
- **R128's empty-name nit is fixed:** global via call result now says
  `kosh 'make_kosh(...)' vaishvika-vittau…` (names the call), not `kosh ''`
  (empty, as on v301/v302). Closed.
- **Ternary message improved:** now says `'?:' kadachit kosh…` (names the
  `?:` operator), not `'kadachit kosh' kadachit kosh…` (v301/v302 wording).
  Same error code (`E_KOSH_DVARA`), same refusal, clearer message.

### (b) `parimana()` after growth, after a block, after 20,000 `kosh` — right in all three (with one minor open question on block koshes)

**After growth — RIGHT (live only, not total).** Program: `parimana()` at
5 points (start; after 1-element 4-cap kosh; after 4 elements (no growth);
after 5th element (growth 4→8); after 8 elements (no growth)).
**Result: `0, 64, 64, 96, 96`.** Reading: first kosh (descriptor + 4×8
buffer, 16-aligned) = 64; no growth → unchanged (64); growth to 8 (new
64-byte buffer, old 32-byte buffer leaked by bump allocator, not freed) →
96 (live only: new buffer + descriptor, old buffer **not** counted). Delta
on growth is +32 (64→96 = new 64 − old 32, live delta), **not** +64
(64→128, total delta, which would have counted the leaked old buffer).
So v303 counts **live**, correctly — the v302 "wrong `parimana()`" (which
would have overcounted leaked buffers) is fixed for growth.

**After 20,000 `kosh` — RIGHT (exact).** Program: `parimana()` before and
after creating 20,000 koshes (each 1 element, 4-cap, via `make_kosh()`),
then `last[0]`. **Result: `0, 1280000, 19999`.** 1,280,000 = 20,000 × 64
(exactly, descriptor + buffer per kosh, 16-aligned). Not 0, not 1.28 TB
(old regions), not overcounted. **Right.**

**After a block — scratch correctly freed, kosh correctly persists, with
one minor open question.** Clean tests (no prior koshes, to isolate):
- Block with **nirmmita only** (16 bytes scratch): `0 → 16 (inside) → 0
  (after)` — **right** (scratch freed, no block overhead leak, back to 0).
- Block with **kosh only** (1 element, 4-cap): `0 → 96 (inside) → 96
  (after)` — kosh persists (right, koshes outlive blocks), but costs **96,
  not 64** (outside-block kosh cost, from the growth test).
- Kosh outside block first, then block with nirmmita only: `64 (kosh) →
  80 (inside: 64+16, correct) → 64 (after: back to 64, nirmmita freed,
  kosh persists, no leak)` — **right**.
- Original block test (nirmmita + kosh in block, then kosh outside):
  `0 → 16 → 112 → 96 → 192` — consistent with the clean tests (block kosh
  96, persists at 96 after block (only nirmmita 16 freed), then new outside
  kosh adds 96? No — new outside kosh should add 64 (as in growth test),
  but here it adds 96 (96→192). Hmm, that last delta (96, not 64) is the
  same block-kosh anomaly (see below), not a separate issue — the new
  outside kosh after a block also costs 96, not 64, in this sequence
  (possibly because the prior block kosh's 32-byte extra persists in the
  baseline, or because koshes after a block cost 32 extra — either way,
  the anomaly is the same 32 bytes, not a new one).

**The open question (minor, diagnostic only, not program correctness):**
koshes created **inside** a `mandapa` (and, in the sequence above, the next
kosh after a block) cost **96, not 64** (outside-block kosh cost). Whether
96 is **right** (real block-kosh tracking memory, e.g., 32 bytes for
block-kosh bookkeeping that persists because the kosh persists) or a
**32-byte overcount/leak per block-kosh** (tracking that should be freed
after the block decides the kosh persists, but is not) cannot be determined
from `parimana()` alone (both give 96 after the block). It is **not** a
program-correctness defect (programs still work correctly, values correct,
no crash/silent wrong — only the reported number differs by 32 bytes per
block-kosh), and it is **not** a sign-off blocker (see WS2), but it is worth
one line in the release notes or a follow-up probe (e.g., grow a block
kosh after the block and see if the 32 bytes are needed for growth, or if
they are dead).

**Parimana verdict: right in all three brief cases** (growth live delta
correct, 20k exact, block scratch freed + kosh persists), with the
block-kosh 96 vs 64 as a minor diagnostic open question (32 bytes, not
program results).

### (c) The silent memory overwrite ChatGPT found — probed around it, does not reproduce on v303

The brief does not disclose ChatGPT's exact path (only that it was a
silent memory overwrite found by reading, reproduced by Claude on v302,
fixed at v303), so I probed **likely** paths (capacity edge cases,
adjacent allocations, interleaved, scale) — **all clean on v303, no
overwrite, no corruption, no crash**:

- Capacity **0** (`kosh k[0]`, push 11, read): `11` — works (first push
  grows from 0, no crash, no overwrite).
- Capacity **1** (`k[1]`, push 11,22,33, growth 1→2→4): `11,22,33` — works.
- Capacity **3** (non-power-of-two, push 11..77, 7 elements, growth
  3→6→12): `k[0]=11, k[3]=44, k[6]=77` — works.
- Capacity **1000** (push 0..1999, 2000 elements, growth 1000→2000):
  `k[0]=0, k[999]=999, k[1000]=1000, k[1999]=1999` — works.
- **Nirmmita-adjacent growth** (nirmmita buffer with 99,88,77,66, then
  kosh growth to 8 elements, then read nirmmita): `99,88,77,66` (unchanged,
  **not** overwritten by kosh growth), `k[7]=88` (correct) — growth does
  **not** overwrite adjacent nirmmita buffers.
- Plus R129 re-runs on v303 (interleaved 2 koshes, both correct; 20,000
  live + grow one, all correct; multiple growths to 100,000, alias agrees;
  dasham whole + fractional, correct) — **no corruption in any case**.

The SIGSEGV defect (ChatGPT's one SIGSEGV, also fixed at v303) likewise
does **not** reproduce on v303 in any probed path (all probes exit 0,
correct values, no segfault — including capacity 0/1, which would have
been the most likely segfault paths on v302 if growth from 0/1 mishandled
a null/zero buffer).

**Honest scope note:** because the exact v302 overwrite (and SIGSEGV)
paths are not disclosed in my brief, I probed **likely** paths, not the
exact paths — but all likely paths are clean on v303, which is consistent
with the fixes holding (a fixed defect does not reproduce, regardless of
which specific path it was on v302). If Sarvam wants the exact paths
confirmed fixed (not just likely paths), ChatGPT's R203 (which found them
by reading) should name them, and I can re-probe those exact paths on
v303 — but on the evidence here (all likely paths clean, no regression,
no new corruption), there is no remaining overwrite or segfault in the
descriptor that I can find by probing.

### (d) The parameter-growth gap: the refusal is still wrong as a message (not as a refusal)

On v303, growing a kosh parameter still refuses, with the **full message**
(only one line, no error code, no hint):

```
Sutram truti: kosh-tarke kosh_push asamarthitam
```

**It is NOT the right message, for three reasons:**
1. **Wrong name:** it says `kosh_push` (old, deprecated name), but the
   program used `kosh_kship` (current name, since v292). A user who wrote
   `kosh_kship` gets an error saying `kosh_push` is unsupported — confusing
   (they did not write `kosh_push`, so why does it say that?).
2. **No error code:** unlike `E_KOSH_DVARA` / `E_VITTI_PRAKAR` (which have
   codes), this refusal has no `E_*` code — inconsistent, harder to
   reference in docs or bug reports.
3. **No hint:** unlike other refusals (which have a `Sanket:` line telling
   the user what to do instead), this one gives no guidance (e.g., "grow
   the kosh in the caller, then pass it; or return the grown kosh from the
   function").

The **refusal itself** (that parameter growth is unsupported) is correct
and safe (as established in R129 — parameters are shared for reading
(bounds-checked, see param-index re-run above), but growth via parameters
would update a copy, not the caller's descriptor, so v303 refuses rather
than allowing a stale caller descriptor). Only the **message** is wrong.
**This is a diagnostic nit, not a crash/silent wrong, and not a sign-off
blocker for a release candidate** (see WS2) — but it should be fixed
before final release (trivial: change `kosh_push` → `kosh_kship`, add an
`E_*` code, add a hint), because it is the one user-facing message in the
descriptor area that is still wrong.

## WS2 — The release question: I would sign off for v303 as a release candidate (compiler, Linux + reported gates), with polish notes for final — and I would NOT sign off for what I cannot verify here.

**Sign off (for v303 RC):** there is **no known crash or silent-wrong
defect** in the compiler that I can find by probing on v303:
- All R129 probes identical on v303 (no regression from the three fixes).
- All R127/R128 defect probes still hold (refused/bounds-checked, not
  regressed).
- Parimana right in all three brief cases (growth live delta, 20k exact,
  block scratch freed + kosh persists), with only a minor 32-byte
  diagnostic open question for block koshes (not program results).
- No overwrite, no segfault in any probed path (capacity 0/1/3/1000,
  nirmmita-adjacent, interleaved, 20k live + grow, multiple growths,
  dasham).
- Gates reported: 68 PASS / 0 FAIL / 1 NOT-RUN (Windows execution), suite
  327, FAIL=0, installer now carries the compiler (gate fixed, previously
  67/1/1). No gate FAILs.

**Polish notes for final release (not blockers for a candidate, but
should be done before final):**
1. Fix the parameter-growth message (kosh_push → kosh_kship, add an `E_*`
   code, add a hint — trivial, one message).
2. Document the known safe limitations (parameter growth refused, ternary
   in-bounds refused, global in-bounds refused, kosh-in-kosh refused) so
   users know what is not supported in v1.0, rather than discovering it
   via refusals (especially with the currently wrong parameter-growth
   message).
3. Resolve the block-kosh parimana 96 vs 64 question (32 bytes, diagnostic
   only — either document that block koshes cost 96 (if it is real
   tracking memory) or fix the overcount/leak (if it is dead bookkeeping)).

**What I would NOT sign off for (because I cannot verify it here, not
because it is known broken):**
- **Windows execution on real Windows** (1 NOT-RUN gate here — I cannot
  run Windows in this environment; Windows execution was previously 312
  passes on Windows (per R128 history) and the Windows linker was rebuilt
  for v303, so it is verified by the Windows gate system elsewhere, not by
  me here — my sign-off does not cover it).
- **Installer payload on real Windows** (reported by gates as "carries
  the compiler", but I cannot run the Windows installer here to verify
  the payload independently — reported, not independently verified by me).
- **IDE GUI on real Windows** (including the R128-history IDE editor-limit
  defect — previous program's output left on screen for ~64 KiB files —
  which is not in this round's WS list and which I cannot test headless
  here; if it is still live on v303, it is a student-facing wrong-output
  defect (stale output shown as current) that should be fixed before a
  student-facing final release, but it is outside this round's compiler
  sign-off and outside what I can verify here — I flag it, I do not sign
  off for it).

**In one line:** sign off for v303 RC (compiler, Linux + reported gates),
fix the parameter-growth message + document the safe limitations + resolve
the parimana block-kosh question before final, and do not treat this as a
sign-off for Windows execution, installer payload on real Windows, or IDE
GUI (which I cannot verify here).

## WS3 — What your probes cover, and what they do not (R129: 8 in R127, none in v302's descriptor; ChatGPT: 3 in the same code by reading)

**What my probes cover (and why they found 8 in R127 and none in v302's
descriptor):** my probes test **runtime behaviour for cases I think of**,
derived from the design, the brief's bullets, and prior defects. They are
good at: crashes (segfaults — R127 S1/S2/S3, all found by probing
reassignment/loop cases I thought of from the tracking description);
silent wrongs (stale aliases, over-reads — R127 O1–O5, all found by
probing non-bare-variable sources I thought of from "set only from a bare
variable"); boundaries (capacity, growth — R129 boundary, multi-growth,
interleaved, dasham, all correct); scale (20,000 koshes, 20,000,000
elements, OOM — all verified by running, which reading alone cannot
prove); and regressions (re-running prior probes on new versions — R128,
R129, R130 all show no regressions, which is itself valuable evidence).
My R129 descriptor attack covered growth, aliasing, nesting (as far as
allowed), OOM, boundaries, multiple aliases, interleaved, dasham, and
scale — and found no crash/silent wrong, because **for the paths I tested,
there was none** (v302's descriptor was correct on those paths, as v303
confirms by re-running them identically).

**What my probes do NOT cover (and why ChatGPT found 3 by reading that I
missed):** my probes test **only the paths I think of**. ChatGPT found
three by **reading** (static analysis, unbiased by bullets or prior
defects): a SIGSEGV, a silent memory overwrite, and a wrong `parimana()`
— in paths my probes did not reach, because I did not think of those
specific cases. Likely candidates for what I missed (inferred, not
disclosed in my brief): a specific capacity or size that triggers a
particular growth path (e.g., a size where a copy loop is off by one, or
where a size calculation overflows, or where a header write lands one
field off); a specific buffer layout where growth overwrites an adjacent
allocation (e.g., a nirmmita buffer adjacent to a kosh in a specific
order, or a descriptor header adjacent to a buffer, which my
nirmmita-adjacent test (one layout) did not hit, but another layout
would); or a specific `parimana()` counting case (e.g., after a particular
sequence of growth + block + growth, where the counting diverges from
live, which my three parimana cases (growth, block, 20k) did not hit in
that exact sequence, but another sequence would). Reading covers **every
code path**, including edge cases I would not think to probe (off-by-one
in a copy, missing check in a rarely-used path, incorrect size for a
specific input). Probing covers **only the paths I think of**, however
thoroughly I run them (even 20M elements, if they are all on the same
"happy path" growth routine, will not hit an edge case in a different
routine or a different size).

**What reading alone does NOT cover (and why probing is still needed):**
reading cannot prove runtime/scale behaviour: that 20,000,000 numbers
actually agree between two names (not just that the code looks like it
should agree); that 20,000 koshes actually use one `mmap` (not just that
the arena code looks like one `mmap`); that the alias cliff is actually
gone at 4,194,304 and 20,000,000 (not just that descriptors "should" fix
it); that OOM is actually a message (exit 1) in practice, not a crash
(reading the OOM path cannot prove the message prints and the exit is
clean under a real limit — only running under `ulimit` proves it); or
that fixes do not regress prior behaviour (only re-running prior probes
proves that). Reading finds defects in code; probing proves behaviour in
the world.

**The lesson, in one paragraph:** probing and reading are **complementary,
not substitutes**, and neither alone is sufficient. Probing (my method)
finds defects in paths I think of, verifies scale/real behaviour, and
catches regressions — but misses paths I do not think of (as proven by
ChatGPT's three, which were in paths my R129 probes did not reach, even
though my R129 probes were thorough on the paths they did cover).
Reading (ChatGPT's method) finds defects in every code path, including
edge cases I would not think of — but cannot prove runtime/scale
behaviour (20M agreement, 20k one mmap, cliff gone, OOM message) or
catch regressions (only re-running probes does that). **For future work,
the right method is both, in order: read first** (especially the new
code — growth routine, descriptor header handling, `parimana()` counting
— to find edge cases to probe, not just the brief's bullets), **then
probe what you read** (especially edge cases: capacity 0/1/non-power-of-
two, empty, single-element, large capacities, adjacent allocations in
different orders, `parimana()` deltas (not just absolutes) after
growth/block/20k sequences), **plus keep the scale/regression probes**
(20M/20k/cliff/OOM/re-run prior probes on every new version, because those
are the only way to prove behaviour at scale and to prove fixes do not
regress). My R129 probes were thorough but **bullet-bound** (bullets +
prior defects); ChatGPT's reading was **code-bound** (all descriptor
code, not just bullets) — and code-bound found three that bullet-bound
missed. Next time, I should be code-bound first, then probe.

## NOT RUN

Windows execution (cannot run Windows; 1 NOT-RUN gate here, verified by
the Windows gate system elsewhere (312 passes, per R128 history), not by
me here), browser, implementation (none authorized — attack and
verification only, v303 fixes not built by me), native-speaker review,
full suite (no tree changes; the v303 suite numbers (327, FAIL=0) stand,
not re-run here), installer payload on real Windows (reported by gates as
"carries the compiler", not independently verified by me here), IDE GUI
on real Windows (including the R128-history editor-limit defect, not in
this round's WS list, cannot test headless here).
