# R36-00 — Hand-back to Sarvam: the first lines

- **Code pushed to `main`: `57287133`.** The delivery documents are in the commit directly on top of it. Pushed
  with git: not file by file, and not `--force`.
- **Compiler on main: `Sutram 1.0 (v244) - sampurna sutra`, unchanged.** The work is in the standard library.
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux).
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux). No golden changed; one new stdlib test.
- **The fuzzer:** `fuzz_r23` 1000 programs, 35,938 values, 0 differ · `fuzz_valid --capabilities` 500 / 500 ·
  `fuzz_robust` 5000, 0 crash, 0 hang. **The fuzzers do not reach huge capacities;** the net is the stdlib tests.
- **`tools/gates.sh`: 32 PASS / 0 FAIL / 1 NOT-RUN (Windows).** Library proofs **222 / 222** under a 4 GB address
  limit and unlimited; property proofs 86 / 86.

## WS1, first: the positive wrap ChatGPT named was fixed in R35

**ROUND-36 says ChatGPT "found something you did not": that `sz = c * 8` followed by `sz < 0` lets a positive wrap
through.** That is the defect my R35 fixed, for the same value. R35-00's table starts with
`suchi_srij(2^61 + 1)`, "`c * 8` = 8 … a handle; SIGSEGV on the second push … now 0". **The fix is on main since
`46540309`:** `suchi_srij`, `avali_srij` and `mala_nava` refuse `c > (2^63 − 1) / 8` **before** multiplying, and
`nighantu_srij` refuses `c > (2^63 − 17) / 56`. **ChatGPT's own post-R35 reconciliation**
(`ChatGPT-to-Sarvam/ROUND-101-POST-R35-RECONCILIATION.md`) records the same: *"AGREES and IMPLEMENTED for the
constructors."* The two readings found the same hole independently. Neither found something the other missed in the
constructors.

**What ChatGPT did add, in that reconciliation, is the growth paths.** That is your second request ("check every
other place that multiplies before it allocates"), and it is this round's work.

**Which fix, and why: divide first.** I used a constant bound on the count, `count > (2^63 − 1) / bytes`, rather
than `ganita_checked_mul`:
- **no new dependency.** `ganita_checked_mul` lives in `ganit`, so `suchi`, `mala` and `nighantu` would have to `yoj`
  it, and every program that uses a list would carry it. That matters: see the finding below;
- **it is checked before the multiply,** so no wrapped value ever exists;
- **the bound is exact** for each formula (`8`, `16`, `56` bytes per element).

## WS1, the audit: every place in `lib/` that multiplies a count and then allocates

**Full table: `evidence-r36/audit-multiply-then-allocate.txt`** (every `nirmmita(` with a `*`, plus the four
`sz = …` constructors).

| Site | Verdict |
|---|---|
| `suchi_srij`, `avali_srij`, `mala_nava`, `nighantu_srij` | **guarded, R35** |
| **`suchi_vardh`** (a full list doubles: `cap × 16` bytes) | **guarded now:** `cap > (2^63 − 1) / 16` gives 0, and the list is unchanged, as its comment promises |
| **`avali_pravesh`** (a full queue doubles) | **guarded now**, the same |
| **`nighantu_vardh`** | **a real defect on a correct call, fixed.** It called `nighantu_srij(newcap)` and read `newm[0]` without checking for 0. A capacity over the bound, or one the machine will not grant (`10^15`), **SIGSEGVed**. It now returns 0, as its comment says it does when it cannot grow; the scratch allocation is checked too |
| `nighantu_mil`, `sangrah`'s 6 functions (11 sites) | **cannot wrap for a real map or set:** the capacity is at most the `nighantu_srij` bound, so `cap × 33 + 1 ≤ 5.4e18` |
| `aadhar` `brihat_ank_tak`, `brihat_shesh`, `brihat_ghatmod`, `shreni` `mil_shreni` | **the caller's own array length:** a wrap needs an array of more than 2⁵⁸ elements, which cannot exist |

**The growth wrap cannot be reached by a real list** (no list of 2⁵⁹ elements can be allocated). So the test forges
a full header to exercise the arithmetic. **With the old library that forged list crashed (bus error), and with the
new one the push returns 0 and the list is unchanged.** `nighantu_vardh` needs no forging: `nighantu_vardh(m,
10^15)` crashed on any machine.

**`tests/stdlib/r36_growth_guard.sm`** (new): both growth paths, `nighantu_vardh` past the bound and past the
machine, and ordinary growth (100 pushes; `nighantu_vardh(m, 64)`) still working. **It fails on the old library and
passes on the new; under Wine too.**

**What remains is a different class, listed rather than taken:** `nighantu_mil`, `sangrah`, `aadhar`, `brihat`
and `shreni` do not check that `nirmmita` succeeded, so under memory exhaustion they write through 0. Those
functions' failure conventions differ (some return counts), so each needs a decision about what failure means. That
is a library round for Muse.

## Found on the way: the containers are 1 KB from the source limit

**My first version of this fix added about 600 bytes of comments to `suchi` and `nighantu`. A property proof that
uses `nighantu`, `sangrah` and `suchi` together then stopped compiling**: `vistarit srot seema atikram`, the 64 KiB
limit on a program plus every module it `yoj`s. The comments are now one line each and it compiles, but
`tests/stdlib/r11_sets_lists.sm` reaches **64,422 of 65,536 bytes**, and three more are within 3.3 KB.
**Every comment added to the container modules spends that headroom.** This is also why I did not pull in
`ganita_checked_mul`. Evidence: `evidence-r36/finding-source-limit-headroom.txt`.

## WS2: what fits next, in one sentence

**Unchanged from R35: the printing of a large `dasham`, a silent wrong answer, waits on the owner because it changes
what existing programs print. The `yoj` scanner fix waits on the owner the same way. So the next thing that needs
no decision is the unchecked-allocation class above, if Muse does not take it. After this round, a container
module will need its comments moved to docs first to make room.**

## WS3: the guard

- **The compiler did not change** (v244): its ordinary path is what it was.
- **The library did, on purpose.** Same compiler, main's library against this one, 565 programs:
  - **440 byte-identical, 92 refused identically;**
  - **32 differ: exactly the 32 that reach `suchi` or `nighantu`.** Nothing else differs, and all 32 pass their
    goldens and proofs;
  - 1 is new.

  Evidence: `evidence-r36/library-change-guard.txt`.
- **Your 476 / 0 DIFFER** is the Windows session's measure on its program set, of the compiler. For the compiler, in
  my counting, it is 0 differ again.

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 32 PASS / 0 FAIL / 1 NOT-RUN |
| library proofs, 4 GB limit · unlimited | Linux | 222 / 222 · 222 / 222 |
| property proofs | Linux | 86 / 86 (85 / 86 with my first, longer comments: the source limit) |
| the new test on the old library (check the check) | Linux | fails (bus error), as it must |
| the library change, 565 programs | Linux | 440 identical, 92 refused identically, 32 differ = exactly the module users |
| suite · corpus | Linux | PASS=218 · 227 + manifest, 0 failed |
| fuzzers (3) | Linux | 0 differ · 500/500 · 0 crash |
| `tests/r66 … r70` | Linux | all OK |
| the new test | **Wine** | matches |
| Windows | — | **NOT-RUN** |

## What I did NOT do, and why

- **The unchecked `nirmmita` results** in `nighantu_mil`, `sangrah`, `aadhar`, `brihat`, `shreni`: listed, not
  changed (above).
- **The installer was not rebuilt.** It carries `lib/` and the v243 compiler: stale since R34. It needs the owner's
  PC.
