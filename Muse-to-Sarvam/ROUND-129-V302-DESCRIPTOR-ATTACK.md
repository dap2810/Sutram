# Muse Round 129 — Attack v302's descriptor. Find the tenth defect.

- **Base:** main at v302 (`2841fd23`, "v302 descriptor built: rebuild
  installer payload, attack the new code, write the memory reference").
  Compiler changed (`src/sutram_compiler.asm`, `src/r65_arena.inc`,
  `src/r32_ffi.inc`, `src/r23_capabilities.inc`, `src/r11_sandesh.inc`).
  Version string is v302. `kosh` is now a 24-byte header that never moves;
  growth moves elements and every name sees it via the descriptor.
- **Ordinal note:** the brief's title says "Find the tenth defect" but WS1
  says "Find the ninth" — the brief disagrees with itself on the count, so
  I report what I found (and did not find) and let Sarvam number it. My
  count: I found 8 defects in R127 (all fixed and verified in R128); this
  round finds **no crash or silent-wrong defect** in the descriptor (see
  WS1), and **one gap** (parameter growth, refused, safe, not a crash or
  silent wrong) — which is the next finding, whether it is numbered ninth
  or tenth.
- **Installer note:** the only gate FAIL left (`installer version`, payload
  inside `Sutram-Setup.exe` still v243) is **not** in this round's WS list,
  so I do not take it on (rebuilding the installer payload is a
  Windows/maintainer step, not a Muse audit task in this round).
- **Test and analysis only.** No code was changed.

## WS1 — Attack the descriptor: no crash, no silent wrong. One gap (parameter growth, refused).

All seven bullet cases plus extras, on v302:

| Case | Result | Verdict |
|---|---|---|
| Kosh grown to exactly the capacity boundary, one element either side (4 elements, then 5th = growth to 8) | At capacity: `k[0..3] = 11,22,33,44`, alias `a[0]=11, a[3]=44`; after 5th push: `k[4]=55, a[4]=55, a[0]=11` | **Works** — boundary growth correct, alias agrees |
| Two aliases, one grown, the other read (`vitti a = k; vitti b = k`; grow via `k` to 5 elements) | `a[0]=11, a[4]=55, b[0]=11, b[4]=55, k[0]=11, k[4]=55` | **Works** — all three names agree after growth |
| Kosh inside a kosh, grown at the inner level (`outer[0] = inner`; grow `inner` to 5) | **Compile-refused** `E_KOSH_DVARA` (kosh 'inner' in cell/region/memory, same as v301 O3) | **Not a defect, continued refusal** — kosh-in-kosh remains refused on v302 (descriptors did **not** relax the "kosh goes only by its own name" rule for cells), so there is no outer to see (the program does not compile) |
| Kosh passed to a `prakriya` that grows it (`grow(kosh k) { kosh_kship(k, …) }`; caller reads `kk`) | **Compile-refused**: `Sutram truti: kosh-tarke kosh_push asamarthitam` (kosh_push unsupported for kosh parameters; **diagnostic nit:** message says `kosh_push` (old name) even though the program used `kosh_kship` (current name) — message should say `kosh_kship`) | **GAP (the next finding), but NOT a crash or silent wrong** — parameter growth is refused (safe), so the caller cannot see growth via a parameter because the program does not compile. This is the most significant gap found: the descriptor design does not support growing a kosh inside a callee (parameters are shared for reading — see below — but growth via parameters is unsupported, likely because parameters are passed by value (copy of the descriptor) so growth would update the copy, not the caller's descriptor, leading to a stale caller descriptor — so v302 refuses it rather than allowing stale). If "defect" means crash/silent wrong, this is **not** one (it refuses safely). If "defect" includes design gaps (refused patterns that should work), this **is** the ninth/tenth. |
| Kosh grown inside a `mandapa` block, read after the block closes (kosh declared outside, grown inside to 5, read after) | `k[0]=11, k[4]=55` after block closes | **Works** — mandapa growth visible after block (kosh outlives block, growth inside block persists) |
| 20,000 `kosh` objects, then grow one (loop creating 20,000 via `make_kosh()` + global counter, keep first/mid/last, grow last by 5) | `first[0]=0, mid[0]=10000, last[0]=19999, last[1]=999, last[5]=1003` | **Works** — 20,000 koshes distinct and correct, grown one correct, others unaffected. **Probe lesson (not a v302 defect):** my first attempt declared `vitti first = 0` then `first = k` (kosh), which v301/v302 correctly refuses (`E_VITTI_PRAKAR`, type-fixed vittis) — fixed by initializing `first/mid/last` with `dummy()` (empty kosh, same type) then assigning koshes (same type, allowed) |
| Out-of-memory path: exhaust the arena (push 20M elements into a kosh under `ulimit -v 65536` (64 MB)) | **Message, not crash**: `Sutram truti: kosh vardhayitum smritih na labdha - kosh yatha asit tatha eva` (kosh growth: memory not obtained — kosh remains as it was), **exit 1** (confirmed without pipes, 1 line, no segfault) | **Works** — OOM is a message (exit 1, clean abort, not SIGSEGV), as claimed. (Without the ulimit, 20M pushes succeed (160 MB), exit 0, `k[0]=0` — so OOM only triggers when memory is actually exhausted, not spuriously) |

### Extras (beyond the bullets, to be sure there is no ninth crash/silent wrong)

- **Multiple growths** (100,000 elements, 4→8→…→131072, alias held):
  `k[0]=0, k[99999]=99999, a[0]=0, a[99999]=99999` — **works**, alias agrees
  after many growths.
- **Interleaved growth** (two koshes, grown alternately to 100 each):
  `a[0]=0, a[99]=99, b[0]=1000, b[99]=1099` — **works**, no cross-corruption.
- **Dasham growth, whole** (100 elements, 2→…→128): `m[0]=0.000000,
  m[99]=99.000000, a[99]=99.000000` — **works**.
- **Dasham growth, fractional** (0.5, 1.5, …, 99.5, 100 elements, growth):
  `m[0]=0.500000, m[99]=99.500000, a[99]=99.500000` — **works**, fractional
  floats survive growth (not truncated to integers), alias agrees.
- **Parameter indexing** (re-run of R127 `ws1_param` on v302):
  `k[100]` in a callee still runtime-refuses (`mala ank seema atikram`,
  exit 1) — **works**, parameters are shared for reading (bounds-checked),
  only **growth** via parameters is refused (above).

**WS1 verdict: no crash or silent-wrong defect found in the descriptor.**
Every bullet case either works correctly or refuses safely at compile time
(kosh-in-kosh, parameter growth) — no segfault, no silent `0`, no stale
alias, no cross-corruption, no float truncation, no OOM crash. The only gap
is parameter growth (refused, safe, not a crash/silent wrong) — which is the
next finding, whether numbered ninth or tenth. If "defect" is restricted to
crash/silent wrong, then **there is none, and I believe it because** I tested
all seven bullets plus multiple growths, interleaved growth, dasham (whole
and fractional), parameter indexing, 20,000 koshes + grow one, and OOM — all
work or refuse safely, with no crash or silent wrong observed in any case.

## WS2 — Verify the two headline numbers yourself: both reproduced (and one strengthened).

### "20,000,000 numbers, two names agree" — REPRODUCED, with a full comparison (not just spot checks)

Program (`r129_ws2_20m_agree.sm`): `kosh k[4]`; `vitti a = k` (alias); push
`0..19999999` (20M elements); then loop over all 20M indices, counting
mismatches where `a[i] != k[i]`.

**Result (0.3 s, exit 0): `a[0]=0, k[0]=0, a[19999999]=19999999,
k[19999999]=19999999, bad=0`.** All 20,000,000 elements agree between the
two names (0 mismatches out of 20M, full comparison, not just endpoints or
a sum). Headline verified, and stronger than Claude's measurement (which
reported agreement, but I verified every element, not just a sample).

### "20,000 `kosh`, one `mmap`" — REPRODUCED

Program (`r129_ws2_20k_maps.sm`): create 20,000 koshes via `make_kosh()` +
global counter, then pause at `grahan()` (waits for input) while I inspect
`/proc/<pid>/maps` and `/proc/<pid>/status`, then send a newline to finish.

**Result while paused (20,000 koshes live): 8 mappings total, 1 large
(≥16 MB) mapping of exactly 1024 MB (1 GiB arena, one `mmap`, shared for all
kosh buffers, not per-kosh regions), `VmSize: 1048816 kB` (~1,024 MB +
binary/stack overhead), `VmRSS: 1276 kB` (~1.2 MB, only touched pages,
lazy). Final output after resume: `ready` + `last[0]=19999` (correct,
20,000th kosh), exit 0.**

So: 20,000 koshes work, they use **one** `mmap` (1 GiB arena, shared), not
20,000 × 64 MB regions (which would have been 20,000 mappings, ~1.28 TB VSZ,
and would have crashed at the 16th under a 1 GiB limit on v300). The 64 MiB
per-`kosh` region is **gone** (replaced by one shared arena + 24-byte
descriptors), and RSS stays tiny (1.2 MB, lazy) despite 20,000 live koshes.
Headline verified.

## WS3 — The cliff number, third time asked: verified GONE at both 4,194,304 and 20,000,000. It closes.

Program (`r129_ws3_cliff302.sm`; naming: `a` is the **alias** (`vitti a =
k`), `k` is the **original** kosh, same as R127/R128): `kosh k[4]`; push `41`
(1 element); `vitti a = k` (alias); push 4,194,305 more (total 4,194,306,
past the 4,194,304 → 4,194,305 point); post-relocation write `k[0] = 99`;
read `a[0]`; then push 15,805,695 more (total 20,000,001, past 20,000,000);
post-write `k[0] = 88`; read `a[0]` and `k[0]`.

**Result on v302 (0.2 s, exit 0): at 4,194,306 elements, `a[0] = 99`
(correct, alias sees new value — cliff GONE at 4.2M, vs `41` stale on
v300/v301); at 20,000,001 elements, `a[0] = 88` (correct), `k[0] = 88`
(control) — cliff GONE at 20M too.**

The brief asks "report what `a[0]` gives at each": **`a[0]` gives `99` at
4,194,304+ (past the old cliff), and `88` at 20,000,000+ (past 20M)** — both
correct, both agree with the original, so the alias does **not** break at
either point. History: measured on v298 (R124, live: `41` stale), v300 (R127,
live), v301 (R128, live), now v302 (R129, **gone**). The brief says "third
time I have asked" and "if it is verified, it closes" — **it is verified
gone on v302 at both points, so the cliff thread closes.**

## NOT RUN

Windows execution (cannot run Windows; v302's descriptor is Linux/PE shared
code, but these results are Linux only — PE descriptor behaviour not tested
here), browser, implementation (none authorized — attack and verification
only, descriptor not built by me), native-speaker review, full suite (no tree
changes; the v302 suite numbers (327, FAIL=0) stand, not re-run here).
