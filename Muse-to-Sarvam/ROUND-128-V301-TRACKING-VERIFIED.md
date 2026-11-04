# Muse Round 128 — Your eight defects are fixed. Verify it, then attack the descriptor.

- **Base:** main at v301 (`34dc7cf7`, "full Windows history + v301 tracking
  fixed; now build the descriptor"). Compiler changed significantly
  (`src/sutram_compiler.asm` +1218/−182, `src/r11_sandesh.inc` for new
  diagnostics, including `E_KOSH_DVARA` and `E_VITTI_PRAKAR`). Version string
  is v301.
- **Windows history received:** Rounds 1–4 + IDE test (305→8→3→0 failures,
  312 Windows passes / 315 Linux, IDE 307/335 correct + 18 review + 1 editor
  limit leaving previous output on screen). No WS in this round asks for
  Windows or IDE work, so I note the history and its lesson (Windows as a
  second pair of eyes) but do not take on the IDE editor-limit defect here —
  it is a separate subsystem, not assigned in this round.
- **Descriptor note:** the descriptor is **not** in v301 (commit title says
  "now build the descriptor" — future work for Claude/ChatGPT, not built
  yet). This round verifies the tracking fix that precedes it; there is no
  descriptor to attack in this round.
- **Test and analysis only.** No code was changed.

## WS1 — My own 20 probes, on v301: every one is refused or bounds-checked. The fix covers all eight.

Claude's report is **confirmed**. I re-ran all 20 R127 probes unchanged on
v301 (`r127_ws1_*.sm`, `r127_ws2_smallest.sm`, `r127_ws3_cliff.sm` — already
on main from R127, not re-staged here). **No probe still segfaults, and no
probe still returns a silent `0`.** Results by class:

### The 8 defects, all fixed

| Defect (R127) | v300 | v301 | How it is fixed |
|---|---|---|---|
| S1 kosh → raw reassignment (`a = k; a = p; a[0]`) | Segfault 139 | **Compile-refused** `E_VITTI_PRAKAR` ("'a' kosh asti; sankhya tasyam na sthapyate" — 'a' is a kosh; a number/memory place cannot be placed in it; hint: one vitti's type is fixed — kosh, mala, division, or number; for a different type, declare another vitti) | Type-changing reassignment refused at compile time (vitti types are fixed) |
| S2 kosh → mala reassignment (`a = k; a = m; a[100]`) | Segfault 139 | **Compile-refused** `E_VITTI_PRAKAR` (same, "'a' kosh asti") | Same (type-fixed vittis) |
| S3 loop reassignment (`a = k`; loop `{ a = p }`; `a[0]`) | Segfault 139 | **Compile-refused** `E_VITTI_PRAKAR` (same) | Same, and it holds inside loops too (not just straight-line) |
| O1 call result (`vitti a = make_kosh(); a[100]`) | Silent `0`, exit 0 | **Runtime-refused** (`mala ank seema atikram`, exit 1, confirmed true exit 1 without pipes) | Definite-kosh call results are now tracked and bounds-checked at runtime (not compile-refused — valid uses still allowed, invalid ones refuse) |
| O2 mala cell (`m[0] = k; vitti a = m[0]; a[100]`) | Silent `0`, exit 0 | **Compile-refused** `E_KOSH_DVARA` ("kosh 'k' koshthe, kshetre athava smritau na likhyate" — kosh 'k' is not written into a cell, region, or memory; hint: kosh goes only by its own name — `vitti b = k`, kosh parameters, `kosh_*` functions; values via `k[i]`) | Kosh-to-cell stores refused at compile time |
| O3 kosh cell (`outer[0] = inner; vitti a = outer[0]; a[100]`) | Silent `0`, exit 0 | **Compile-refused** `E_KOSH_DVARA` (same, "kosh 'inner' koshthe…") | Same |
| O4 global, both forms (`holder = k` in another function, and in the same function; `holder[100]`) | Silent `0`, exit 0 (both) | **Compile-refused** `E_KOSH_DVARA` (both, "kosh 'k' vaishvika-vittau na sthapyate" — kosh 'k' is not placed in a global vitti; same hint) | Kosh-to-global assignment refused at compile time (matches Claude's claim exactly, both forms) |
| O5 ternary (`vitti a = c ? k : p`; `a[100]`) | Silent `0`, exit 0 | **Compile-refused** `E_KOSH_DVARA` ("'kadachit kosh' kadachit kosh dadati kadachit na (?: athava prakriya-phalam) - tat na sthapyate" — 'maybe-kosh' sometimes gives a kosh and sometimes not (ternary or function result) — that is not stored; same hint) | Maybe-kosh values (ternary) refused at compile time (cannot be tracked as definitely-kosh, so refused rather than allowed to silently over-read) |

### The not-defects, unchanged (still refused or bounds-checked, as before)

Redeclaration (both directions) still `E_DUPLICATE_NAME`; scope (both
directions) still `E_DUPLICATE_NAME`; kosh parameter still runtime-refused
(`mala ank seema atikram`, exit 1, confirmed true exit 1); `vitti` parameter
still a compile error (not a valid parameter type).

### Two behaviour changes to note (safe, but breaking for previously valid uses — owner's decision, not defects)

1. **Ternary in-bounds now refuses.** On v300, ternary `a = c ? k : p`
   with `a[0]` worked correctly (`11` for `c = 1`, `77` for `c = 0`). On
   v301, **any** ternary kosh assignment refuses at compile time
   (`E_KOSH_DVARA`, maybe-kosh), even for in-bounds reads that were correct.
   This is safe (no silent over-read possible) but it rejects valid programs
   that used ternary kosh values in-bounds. The design is coherent
   (definite-kosh sources like call results are tracked and bounds-checked;
   maybe-kosh sources like ternary are refused), but the breakage for valid
   ternary uses should be a conscious owner decision, not a silent side
   effect.
2. **Mala → kosh assignment now refuses at compile time, not runtime.** On
   v300, `a = m; a = k; a[100]` runtime-refused (assignment marked it as
   kosh, so the out-of-bounds read refused). On v301, it compile-refuses
   (`E_VITTI_PRAKAR`, type-fixed). Same outcome (refusal, not silent/crash),
   just earlier (compile time instead of runtime) — stricter, not a
   regression.

**WS1 verdict: the fix covers all eight.** No still-segfault, no still-silent
`0` among the 20 probes. (Note on exit codes: compile-refused probes produce
no binary, so there is no run exit to report; runtime-refused probes
(`ws1_param`, `ws1_callresult`, `ws2_smallest`) were re-run without pipes
and confirmed true exit 1, not 0.)

## WS2 — The global door, and the ways around it: no bypass found. All eight attempts refuse.

Claude's claim is **confirmed**: both global forms (inter-function and
same-function) refuse with `E_KOSH_DVARA` on v301 (see WS1, O4). The three
brief bypasses plus five of my own all refuse at compile time (new probes
`r128_ws2_*.sm`):

| Bypass attempt | v301 result | Why it does not bypass |
|---|---|---|
| Global assigned in two functions (`set_a()` assigns `holder = k`; `set_b()` assigns `holder = k2`; read in `mukhya`) | `E_KOSH_DVARA` (kosh 'k' in global vitti, at the first assignment) | First assignment already refuses, so the program never compiles; second assignment moot |
| Global assigned a mala after a kosh (`holder = k`; `holder = m`; `holder[100]`) | `E_KOSH_DVARA` (kosh 'k' in global vitti, at the kosh assignment) | Kosh assignment refused first, so the mala reassignment never matters (cannot clear a check that already refused the program) |
| Global assigned a mala, then a kosh (`holder = m`; `holder = k`; `holder[100]`) | `E_KOSH_DVARA` (kosh 'k' in global vitti, at the kosh assignment) | Global-door check fires before the type-fixed check (which would have been `E_VITTI_PRAKAR` for the type change) — kosh-to-global is refused regardless of the global's prior type |
| Global via call result (`holder = make_kosh()`; `holder[100]`) | `E_KOSH_DVARA` (kosh '' in global vitti) | Refuses (no bypass). **Cosmetic nit:** the error shows an empty kosh name (`kosh ''`) because the kosh comes from a call result, not a named variable — the refusal holds, but the diagnostic should name the function or the result instead of an empty string |
| Global via mala cell (`m[0] = k`; `holder = m[0]`; `holder[100]`) | `E_KOSH_DVARA` (kosh 'k' in cell/region/memory, at the `m[0] = k` store itself) | Refused even earlier (at the cell store, O2 fix), so the global assignment is never reached |
| Global via kosh cell (`outer[0] = inner`; `holder = outer[0]`; `holder[100]`) | `E_KOSH_DVARA` (kosh 'inner' in cell/region/memory, at the `outer[0] = inner` store itself) | Same (at the cell store, O3 fix) |
| Global via ternary (`holder = c ? k : p`; `holder[0]` in-bounds) | `E_KOSH_DVARA` (maybe-kosh, at the ternary assignment) | Refused even for in-bounds reads (ternary to global refused, same as ternary to local) |
| Global in-bounds read (`holder = k`; `holder[0]`) | `E_KOSH_DVARA` (kosh 'k' in global vitti, at the assignment) | **The fix is "refuse kosh-to-global assignment entirely"** (not "track and bounds-check") — so even valid in-bounds global kosh reads refuse on v301 (they worked on v300 in-bounds). Safe, but a breaking change for valid uses, like ternary in-bounds above — owner's decision |

**WS2 verdict: the global door is closed on v301 for all tested paths**
(bare variable, call result, mala cell, kosh cell, ternary, two functions,
mala-after-kosh, mala-then-kosh, in-bounds). No bypass found. One cosmetic
diagnostic nit (empty kosh name for call-result globals), not a bypass.

## WS3 — The 4.2M cliff, still live on v301 (and the brief's "never measured" is wrong a third time)

**Correction first (third time):** the brief says "The alias cliff past
~4,194,304 elements has been quoted from a report and never independently
measured." **That is wrong (stale, as in R127).** Round 124 independently
measured it on v298 (commit `69a03fc7`), Round 127 re-verified it on v300
(commit `df55c9de`), and this round re-verifies it on v301 — so it has now
been measured **three times, on three versions, with the same result**.

Program (`r127_ws3_cliff.sm`, unchanged from R127; naming: `a` is the
**alias** (`vitti a = k`), `k` is the **original** kosh): `kosh k[4]`; push
`41` (1 element); `vitti a = k` (alias); push 4,194,305 more via `k` (total
4,194,306 elements, past the 4,194,304 → 4,194,305 relocation point, where
capacity doubling 4,194,304 → 8,388,608 exceeds MAXCAP 8,388,603 and
relocates); then post-relocation write `k[0] = 99` (via the original); then
read both.

**Result on v301 (0.1 s, exit 0): `a[0] = 41` (stale, broken — should be
`99`), `k[0] = 99` (correct).** The brief asks "report what `a[0]` gives":
**`a[0]` gives `41`** (the stale value, not the current `99`) — proving the
alias broke. The tracking fix did **not** touch the relocation path (as
expected: tracking is about bounds-checking/marking, relocation is about
updating aliases on growth, a different mechanism), so the MAXCAP cliff is
**still live on v301**. Fixing it (updating aliases on relocation, or
refusing aliased growth past 4,194,304) is separate work from the tracking
fix, and is not in v301.

## NOT RUN

Windows execution (cannot run Windows; v301's Windows memory work does not
affect these Linux tracking results — the compiler is the same v301 for
these behaviours, verified by re-running R127's probes on current main),
browser, implementation (none authorized — verification and attack only,
tracking fix not built by me), native-speaker review, full suite (no tree
changes; the v301 suite numbers stand, not re-run here).
