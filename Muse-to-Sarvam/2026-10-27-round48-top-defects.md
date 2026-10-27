# ROUND-48 — independent evidence on the top defects

**Base:** `origin/main` at `95fd5ff0` (v380; round written against
v379), compiler **v253**. Read first, as instructed:
`/LANGUAGE-PRIORITY.md`, `docs/PATH-TO-COMPLETION.md`, and
`docs/OPEN-ISSUES.md` (30 issues, audited at v378). This round
works A1, A3, A6. Per the round's rule, "already correct, here is
the evidence" is reported as such where it applies — and where a
feature is broken, the exact evidence is given instead. PASS /
FAIL / NOT-RUN separately. **No code changes made. No files added
or modified in the tree.**

## WS1 — ISSUE A1: `kosh` pop / peek / dequeue on empty, independently reproduced

My own programs, not Claude's. Each pushes nothing, prints `111`,
then does the operation, then prints the result and `999`.

**`kosh_pop` on empty:**
```
111
Sutram Error: riktat koshat kosh_pop
```
Exit **1**. `999` never printed.

**`kosh_peek` on empty:**
```
111
Sutram Error: riktat koshat kosh_peek
```
Exit **1**. `999` never printed.

**`kosh_dequeue` on empty:**
```
111
Sutram Error: riktat koshat kosh_dequeue
```
Exit **1**. `999` never printed.

**Pop after draining (push 10, 20, pop, pop, empty check, pop again):**
```
20
10
1
Sutram Error: riktat koshat kosh_pop
```
Exit **1**. So the abort is not only for a never-filled kosh — it
fires the moment the store is empty again, after successful pops.

**What "abort" means here, precisely:** it is a clean runtime
error, not a segfault and not a silent abort signal. The compiler
emits a checked prologue (`emit_kosh_empty_check_r9`,
`src/sutram_compiler.asm:14590`, with the three messages at
373–375) that prints the specific error and exits 1. The program
cannot continue, cannot catch it, and cannot recover the value —
that part of A1 is confirmed. What A1 does *not* mean is a crash
with no message: the message names the operation.

**The programmer can avoid it, but cannot handle it.** Checking
`kosh_empty(a)` first avoids the error (tested: guard program
prints `0`, then `999`, exit 0). But that check must be a separate
statement before the pop — a pop inside an expression cannot be
guarded in place, and there is no ok channel to read after the
fact.

**Design question — how do `ganita_paripurna_*` report, and would
that pattern work for `kosh`? From the source, not preference:**

There are two patterns in the same family, and they are different:
- `ganita_janchit_*` (checked): an `ok` out-parameter, `ok[0] = 1`
  on success, `0` on failure, return `0` on failure
  (`lib/ganita.smlib:304–319`, `ganita_janchit_bhaj`). This is the
  ok channel A1 says `kosh` lacks.
- `ganita_paripurna_*` (saturating): **no ok channel at all**.
  On invalid input it returns a documented sentinel: `b == 0`
  returns `0` (`ganita_paripurna_bhaj`, `lib/ganita.smlib:493–510`;
  same for `ganita_paripurna_shesh`), overflow saturates to
  `INT64_MAX`. The comment says so explicitly: "the saturating
  form has no ok channel, so 0 is the documented sentinel".

Verified empirically:
```
ganita_paripurna_bhaj(10, 0) = 0
ganita_paripurna_bhaj(10, 2) = 5
ganita_paripurna_bhaj(0, 5)  = 0
```
The sentinel `0` is **indistinguishable from a legitimate `0`
result** — `10/0` and `0/5` print identically. The same holds for
`kosh`, and worse: a kosh legitimately holding `0` pops as `0`
(tested: push `0`, pop prints `0`, empty prints `1`, exit 0), so
a `paripurna`-style `kosh_pop` returning `0` on empty would be
ambiguous on the most common element value there is, and for a
dasham kosh `0.0` is likewise legitimate. **So: the
`paripurna` pattern would "work" mechanically — return `0`, don't
abort — but it would silently lose exactly the information the
programmer needs, and it is strictly weaker than the `janchit`
ok-channel pattern that already exists in the same module.**
If `kosh` gets a reporting channel, it should be the `janchit`
one (`ok[0]`), not the `paripurna` sentinel — and because
`kosh_pop`/`peek`/`dequeue` are compiler builtins
(`BN_KOSHPOP` etc., `src/sutram_compiler.asm:215–223`), not lib
functions, adding that channel is a compiler change, not a lib
edit. A1 is confirmed as a design defect, with the fix direction
named by the project's own two patterns.

## WS2 — ISSUE A3: the 818 undecided mutants, sample of 40

### The frame, audited before sampling — read this first

The 818 number needs two corrections, both measured:
- The machine-readable witness file from R15
  (`Claude-to-Sarvam/evidence-r15/proofs/lib-mutant-witness.json`)
  contains **741 NOT-TRIED**, not 818, plus 187 NO-WITNESS and 23
  WITNESS = 951 survivors. The score summary's 818 / 110 split
  differs from its own witness file by exactly 77 in each
  direction, so the 818 is a summary count, not a list anyone can
  sample from. There is no 818-entry list in the tree.
- "Undecided" means, precisely: the mutant survived all proofs,
  **and the witness tool never tried it**, because its function
  takes a list, string, or record parameter (694 of 741) or "no
  number input runs cleanly" (47). It does **not** mean the
  proofs were run and found wanting — it means the distinguishing
  input search was skipped for these functions.

**Sample:** 40 draws, with replacement, seed `20261027`, from the
741 NOT-TRIED entries (25 distinct labels appear twice because
the same mutant label covers two literal occurrences on one
line). The full drawn list is in the appendix. One sampled
function has since been renamed (`brihat_ank_se_int` →
`brihat_ank_se_laghu`, commit `69148e3b`, the owner's choice over
`anka` — the body is the same). Several R15 line numbers are
stale (the lib grew; e.g. `roop_pad_dakshin` now starts at the
line the sample cites inside its body), so each mutant was mapped
to the current function body by content, not by line number.

**Method per mutant:** "run" means a real-vs-mutant harness: the
whole `lib/` copied to a temp tree, one mutant change applied to
one file, the same test program run against real and mutant lib,
outputs compared. "Reasoned" means every candidate occurrence for
that mutant label gives the same verdict (e.g. both terminator
literals in a branch break termination either way). "Ambiguous"
means the candidates split, or the R15 line no longer maps to a
unique current occurrence, so no exact mutant could be run.

**Harness runs (10, exact): 5 witnesses, 5 equivalents.**
- WITNESS — `khand_bandh` D (delete terminator in empty branch):
  real `out[0] = 0`, mutant `out[0] = 88` (pre-filled buffer).
- EQUIVALENT — `brihat_ank_se_laghu` carry `== 1` → `== 2`: the
  final carry check is dead for MIN — the digit array always
  contains a non-9 digit, so carry stops before the check, at
  n = 2, 19, 20, 25 alike.
- WITNESS — `kalana.simpson` parity `/` → `*`: 4-point integral
  real `2.000000`, mutant `3.666667`.
- EQUIVALENT — `khand_chhid` `>=` → `>`: output identical on a
  buffer with a trailing space past `slen`; the mutant only reads
  one byte past the counted length, which the copy range (capped
  at `slen`) then ignores.
- EQUIVALENT — `khand_yuj` initial `q = 0` → `1`: `q` is reset to
  `0` inside the separator loop before every use.
- EQUIVALENT — `ganita_janchit_yuj` `y < 0` → `y <= 0`: the only
  differing input is `y == 0`, where `x` negative cannot overflow,
  so the overflow branch is not taken either way.
- WITNESS — `khand_viparyay` empty-branch terminator `0` → `1`:
  real `out[0] = 0`, mutant `out[0] = 1`.
- EQUIVALENT — `brihat_ank_se_laghu` stride `j * 8` → `j * 9` in
  the MIN carry loop: carry stops at the first digit (`8` → `9`),
  so the misaligned read at `j ≥ 1` never happens for MIN, the
  only input that reaches that loop.
- WITNESS — `varna_tul` `i + 1` → `i + 2`: `"ab"` vs `"ac"` real
  `-1`, mutant `0` (second byte never compared).
- WITNESS — `varna.gan_akshar` `i = 0` → `1`: count of `'a'` in
  `"aa"` real `2`, mutant `1`.

**Reasoned (22): 11 witnesses, 11 equivalents.** Witnesses
include: `avali_avalok` D (every deletable statement breaks it —
`d` assignment, or either `ok` store); `roop_pad_madhya` `A:-`
(either `-` in the padding arithmetic changes the pad count);
`khand_pratisthap` / `khand_unnat` empty-branch terminators
(index or value change both break termination);
`phal_janchit_nirapeksh` / `phal_janchit_shesh` failure-branch
`o[1] = 0` → `1` (the out array, not the ok flag, breaks
contract); `nighantu_anwesh` return `-1` → `-2` on a full table;
`khand_ant` initial `i = 0` → `1` (first suffix byte skipped);
`nighantu_kunjika_ashtak` count `n = 0` → `1` (every count off
by one); `roop_pad_madhya` D and `roop_chinhit` D (deleting a
counter reset or a digit-count assignment breaks the output).
Equivalents include the dead-initialisation family
(`khand_gan` `f = 0`, `rakh_tak_mala` `wpos = 0` — reset before
the emit loop, `nighantu_anwesh` `idx = 0` — overwritten by the
hash before use, `suchi_nivesh` / `suchi_vinimay` `d`/`t` inits,
`roop_pad_dakshin` inits), the converging-branch family
(`khand_avanat` `slen < 0` → `slen < 1` — both branches write the
same terminator and return `0` for `slen == 0`),
`roop_pad_vam` `C3` (an extra copied byte is overwritten by the
terminator), `roop_sthir_mool` `pl > 9` → `pl >= 9` (clamps to the
same `9`), `anukram_khip_i64` `val < 0` → `val < 1` (the inner
`% 256` check makes `val == 0` identical), and
`ganita_janchit_gun` `y == -1` → `y == -2` (the downstream
`m / x != y` check catches `MIN * -1` anyway).

**Still undecided after targeted analysis (8):**
`anukram_grah_ashtak` `K:0` (twice, duplicate label, exact
occurrence unmappable), `sangrah.rakh_tak_mala` `A:+`,
`roop_sthir_mool` `K:0` (candidates split between a live counter
and dead inits), `ganita.chakravala` `C16` (overflow path, not
triggered with a testable input in this round),
`ganita.chakravala` `K:0` (return-value branch reachability not
proven), `sangrah.rakh_asti_upasamuh` `A:+`, and
`nighantu_grah` `K:32` (clamp, only differs on out-of-spec
`keyn > 32`).

**Hit rate:**
- Among the 32 decidable mutants (10 run + 22 reasoned):
  **16 witnesses, 16 equivalents — 50%.**
- Among the 10 exactly run: **5 / 10 — 50%.**
- Of the full sample of 40: **16 confirmed witnesses (40%),
  16 equivalents (40%), 8 still undecided (20%).**

**Answer to the brief's question: the 818 are mostly
unexamined, not mostly harmless.** Half of what can be decided
is a real gap the proofs miss — most often because the proofs
use zeroed buffers (so a missing terminator is invisible), or
never test the boundary the mutant moves — and half is genuinely
harmless, mostly dead initialisations and converging branches.
A 40–50% real-gap rate is not a harmless population, and the 20%
that stay undecided even after targeted work are, by definition,
still unexamined. As a cross-check, re-running the score tool on
current lib for 25 of the sampled functions still lists the same
survivors (e.g. `khand_bandh` still survives `D@L45`,
`K:0@L45`, `K:0@L52`, `D@L52` — all witnesses by the pattern
above), so this is not an R15 artefact.

## WS3 — ISSUE A6: the `yoj` error message, from the source

**Reproduced:** a program calling `brihat_ank_se_laghu` without
`yoj brihat` fails with exactly:
```
Sutram Error: agyat prakriya: brihat_ank_se_laghu
```
Exit 1, no hint, no location, no module suggestion. With
`yoj brihat` the same program compiles and runs.

**Where it is raised:** not at parse time, but at codegen
backpatch time, in `backpatch_calls` (`.bc_old_error`,
`src/sutram_compiler.asm:12419`). A call is emitted as a patch
entry (call-site offset + function-name pointer); backpatch
searches `func_table` for the name, and on failure prints
`msg_undefined_func` ("Sutram Error: agyat prakriya: ", line
359) + the name and exits 1 on the first unresolved name.
`--check` mode (`r48_print_undefined_function`, ~8339) gives the
same message with a location and context, but still no module
hint.

**What the compiler knows at that point that would let it say
"the module is probably missing":**
- The name itself, and that it is **not a builtin** (builtins are
  generated as builtin calls, never as patches) and **not defined
  in the program or in any imported module** (`func_table`
  contains exactly the program's plus imported modules'
  `prakriya` definitions, because `yoj` works by inline expansion
  of `lib/<name>.smlib` in `expand_imports`, ~2768).
- **Which modules were imported**: `import_names` /
  `import_count` (`src/sutram_compiler.asm:958–959`) record every
  `yoj` directive seen. So it can say "you imported nothing" or
  "you imported X, Y" — but it cannot name the missing module
  from that list alone.
- **What it does NOT know:** which unimported module defines the
  name, because unimported `lib/` files are never read. To say
  "the module is probably missing" with the module's name, the
  compiler would need either (a) a scan of `lib/*.smlib` at error
  time for `prakriya <name>`, or (b) a name→module index built
  when modules are loaded. Neither exists today.
- A cheaper heuristic that *is* available without a scan: the
  prefix before the first `_` often *is* the module name
  (`brihat_*` → `lib/brihat.smlib`, `ganita_*` → `ganita`,
  `khand_*` → `khand`), so "did you mean `yoj brihat`?" would be
  right for most lib functions — but it is a heuristic, not a
  lookup, and it would misfire where the prefix is not a module
  (e.g. `ank_*` functions live in `lib/ank.smlib`, which happens
  to match, but a user function's prefix could coincide with a
  module name by accident). The honest fix is the scan or the
  index; the heuristic is a stopgap that must be labelled as one.
- Note the asymmetry that already exists: writing `yoj
  <nonexistent>` *does* give a module error (`E_MODULE_MISSING`,
  "yoj patra aprapt", line 324). Only the *absent* `yoj` gives the
  bare "unknown function" — which is why a twelve-line example
  took two attempts.

## WS4 — the guard: this round's number

Method as in R40–R47: committed `./sutram_compiler` (from `HEAD`)
vs a fresh build from `src/r68_compiler_entry.asm`
(byte-identical to the committed binary), every `.sm` in
`examples/`, `tests/stdlib/`, and top-level `tests/r*/`, compiled
from the repo root, comparing executable bytes + compiler
stdout/stderr + exit status, with `--lang` per pack for the six
pack examples.

**Current main `95fd5ff0`: 577 programs, 489 byte-identical
executables, 88 refused identically, 0 DIFFER.** Unchanged from
R45–R47.

## Appendix — WS2 sample (seed 20261027, 40 draws from 741 NOT-TRIED)

`khand.khand_bandh D@L45` · `brihat.brihat_ank_se_int K:1@L62` ·
`kalana.simpson A:/@L38` · `khand.khand_chhid C2:>=->>@L329` ·
`suchi.avali_avalok D@L454` · `khand.khand_yuj K:0@L292` ·
`roop.roop_pad_madhya A:-@L333` · `ganita.ganita_janchit_yuj
C4:<-><=@L229` · `khand.khand_viparyay K:0@L470` ·
`anukram.anukram_grah_ashtak K:0@L117` (×2) ·
`sangrah.rakh_tak_mala A:+@L224` · `roop.roop_sthir_mool
K:0@L465` · `roop.roop_sthir_mool C2:>->>=@L472` ·
`suchi.suchi_nivesh K:0@L129` · `brihat.brihat_ank_se_int
K:8@L52` · `ganita.chakravala C16:!=->==@L136` ·
`roop.roop_chinhit D@L588` · `khand.khand_gan K:0@L500` ·
`sangrah.rakh_tak_mala K:0@L229` · `varna.varna_tul K:1@L477` ·
`khand.khand_avanat K:0@L384` · `nighantu.nighantu_anwesh
K:0@L87` · `roop.roop_pad_dakshin K:0@L277` ·
`khand.khand_pratisthap K:0@L163` · `khand.khand_unnat
K:0@L363` · `sangrah.rakh_asti_upasamuh A:+@L200` ·
`phal.phal_janchit_nirapeksh K:0@L189` · `roop.roop_pad_madhya
D@L322` · `nighantu.nighantu_anwesh K:1@L98` ·
`roop.roop_pad_vam C3:<-><=@L254` · `phal.phal_janchit_shesh
K:0@L152` · `ganita.chakravala K:0@L102` ·
`anukram.anukram_khip_i64 K:0@L49` · `ganita.ganita_janchit_gun
K:1@L284` · `varna.gan_akshar K:0@L70` · `khand.khand_ant
K:0@L423` · `nighantu.nighantu_grah K:32@L161` ·
`nighantu.nighantu_kunjika_ashtak K:0@L420` ·
`suchi.suchi_vinimay K:0@L174`.

## Delivery

- This report: `Muse-to-Sarvam/2026-10-27-round48-top-defects.md`
- No other files. No tree changes.
- `git push` has no credentials here, as before; delivery via the
  GitHub API. The local tree was left at main, unmodified.
