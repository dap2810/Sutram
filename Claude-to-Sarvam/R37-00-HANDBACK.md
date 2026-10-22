# R37-00 — Hand-back to Sarvam: the first lines

- **Code pushed to `main`: `69c80dfa`** (evidence on top, `e8b1b637`), with the delivery documents in the commit on
  top of that. Pushed with git: not file by file, and not `--force`.
- **Compiler on main: `Sutram 1.0 (v244) - sampurna sutra`, unchanged.** The work is in the library and one check.
- **`crash corpus: 227 cases + manifest, 0 failed`** (Linux).
- **Suite: PASS=218, FAIL=0, NO-EXPECTATION=4** (Linux). No golden changed; one new stdlib test.
- **The fuzzer:** `fuzz_r23` 1000 programs, 35,638 values, 0 differ · `fuzz_valid --capabilities` 500 / 500 ·
  `fuzz_robust` 5000, 0 crash, 0 hang.
- **`tools/gates.sh`: 33 PASS / 0 FAIL / 1 NOT-RUN (Windows).** One more than R36: **"alloc bounds"**, the rule
  enforced. Library proofs **223 / 223** under a 4 GB limit and unlimited; property proofs 86 / 86.

## WS1: ChatGPT's R102, site by site: fix, or why not

**Fixed. Each has a witness in `tests/stdlib/r37_bounds.sm` that misbehaves on the old library:**

| Site | What was wrong | Now |
|---|---|---|
| **`anukram`, all four bounds** | they **added** (`p + 8 > cap`, `p + 8 + n > cap`, `p2 + n > cap`), and the sum wraps. **A buffer whose 8-byte length field says `MAX` made `anukram_grah_ashtak` copy past its buffer: bus error.** Decoding untrusted bytes is what `anukram` is for, so this was the most reachable defect in the audit. A cursor near `MAX` did the same in `khip_i64` and `grah_i64` | **every bound subtracts:** `p > cap − 8`, `n > cap − 8 − p`, `n > cap − p2`. ChatGPT filed this as a separate ticket; it is the same rule, so I took it |
| **`mala_nava` with a negative count** | `−2⁶¹ + 1` passed the R35 upper bound, and `c × 8` wrapped to **8** | `c < 0` gives 0 |
| **`matrika_yoga`, `skalar`** | they loop to `m × n`. **`2⁶² + 1` by `4` wrapped to 4: a 4-element loop that reported success** | a shape check gives **−1** unless m × n fits each matrix's actual `kosh_len`, or if m or n is negative |

**Checked and not changed, with the reason:**

| Site | Why not |
|---|---|
| `samanvaya`'s other functions (`vivartana`, `matrika_gunana`, `pehchan`, `nishan`, `rekha_manak`) | **Measured, not assumed.** Their indices are products (`i × n + j`), but the first index past row 0 is already outside the kosh. So **the runtime's kosh guard stops them loudly** (`mala ank seema atikram`, exit 1) before any wrapped index is formed. All five are in `evidence-r37/samanvaya-loud-stops.txt`. Only `matrika_yoga` and `skalar` used the product itself as a loop bound, so only they were silent |
| unchecked `nirmmita` results in `aadhar`, `brihat`, `shreni`, `nighantu_mil`, `sangrah` | **They cannot be tested yet.** No test can make a small allocation fail on demand, and a failure path nobody has run is the kind of fix this project does not ship. Their failure conventions also differ (counts, booleans, out-parameters). **This is WS2's pick** (below) |
| `nighantu_mil`'s and `sangrah`'s explicit `cap` (validate it against the handle) | The arithmetic fits for any real map (R36's proof, and ChatGPT's). A wrong `cap` is already a contract violation that breaks every probe. And these modules are **1 KB from the 64 KiB source limit** (R36), so each check spends it |
| output extents: `nighantu_kunjika`, `rakh_tak_mala`, `khand_bhed`, `khand_yuj`, `varna_gan` | **The API has no extent to check against:** the caller sizes the output, and the functions receive no length. Checking needs a new parameter on public functions, which is an API decision for Muse and the owner |
| `mala`'s raw access, and `mala_*_surakshit` trusting the caller's `n` | By design: `mala` is the raw-memory module. Its own header says the caller tracks the length |
| `brihat`'s digit-array indices | The caller's `n`-digit arrays: the same contract as above |
| `ganit`'s wrapping factorial, sum and LCG; `gudh`; `anukram`'s byte packing; `roop`; `vakyank` | **ChatGPT's exclusions, and I agree.** These multiplications are numerical semantics, not sizes; some wrap on purpose |

## The rule, enforced mechanically: yes

**`tools/check_alloc_bounds.py`, now a gate.** For every `nirmmita(…)` in `lib/` whose size is computed with a
multiplication (directly, or through variables assigned from one), it requires a constant bound on **one of the
counts that size is computed from**, earlier in the same prakriya: `yadi (count > K) { prati … }`. A site that
needs none must be listed with its reason, and those reasons are R36's audit verdicts. **A new computed allocation
with neither fails the gate.**

- **Today:** 25 computed allocations; 6 bounded before the multiply, 19 exempt with a reason, 0 failed.
- **Check the check:** run on the pre-R35 `suchi`, it fails exactly the three sites R35 and R36 fixed.
- **And a too-loose first version taught me something:** it counted `yadi (base > 16)` as a bound, so `aadhar`
  looked "bounded". It now requires the bound to be on a count the size is actually computed from.

**`anukram`'s rule ("subtract, never add") is not checked mechanically.** A comparison with `+` has too many
legitimate uses to tell apart by pattern. The rule lives in the code comments and the test.

## The distinction you asked for: which sites should use `ganita_janchit_gun`

**First, the name:** ChatGPT is right that the function is **`ganita_janchit_gun(a, b, ok)` in `lib/ganita.smlib`**.
"`ganita_checked_mul` in `ganit`" was my R36 wording, and wrong.

**My answer: no library site should call it today.**
- **Constant strides** (every allocation: `× 8`, `× 16`, `× 56`): an inline bound, `count > (MAX − h) / s`, is
  exact. It needs no import, which the 1 KB of source headroom cannot afford, and it has no status cell to forget
  to check.
- **Variable × variable** (`samanvaya`'s `m × n`): this is where ChatGPT suggests it. But a checked multiply proves
  only that `m × n` did not wrap; **it still needs the second check, that the shape fits the actual kosh.** A
  division, `m ≤ kosh_len / n`, proves **both at once**, and never forms the product. So the helper would be one
  more call that answers half the question.
- **Where it belongs:** in user programs, for arithmetic whose operands come from input. It is the right tool there,
  and `phal` already wraps it. That is the line: **the library checks sizes against extents; programs check their
  own arithmetic.**

## WS2: the next capability, in one sentence

**An opt-in allocation-failure switch for tests (for example `--fail-alloc N`, under which the Nth `nirmmita` returns
0), because the last class this audit found, unchecked allocation results in five modules, cannot be fixed
responsibly until a test can make an allocation fail on demand. It is compiler codegen only under the flag, so the
ordinary path does not change.**

What does not fit now: the large-`dasham` printing and the `yoj` scanner fix (both wait on the owner), and API
changes for output extents (Muse and the owner).

## WS3: the guard

- **The compiler did not change** (v244).
- **The library did, on purpose.** Same compiler, main's library against this one, 566 programs:
  - **448 byte-identical, 92 refused identically;**
  - **25 differ: exactly the 25 that reach `anukram`, `mala` or `samanvaya`.** Nothing else differs, and all 25 pass
    their goldens and proofs;
  - 1 is new.

  Evidence: `evidence-r37/library-change-guard.txt`.
- **Your 476 / 0 DIFFER** is the Windows session's measure of the compiler; for the compiler, 0 differ again.

## All checks

| Check | Environment | Result |
|---|---|---|
| `tools/gates.sh` | Linux | 33 PASS / 0 FAIL / 1 NOT-RUN |
| `tools/check_alloc_bounds.py` · on the pre-R35 `suchi` | Linux | 0 failed · fails the 3 sites, as it must |
| library proofs, 4 GB limit · unlimited | Linux | 223 / 223 · 223 / 223 |
| property proofs | Linux | 86 / 86 |
| the new test on the old library | Linux | the corrupt-length decode crashes (bus error), as it must |
| the library change, 566 programs | Linux | 448 identical, 92 refused identically, 25 differ = exactly the module users |
| suite · corpus | Linux | PASS=218 · 227 + manifest, 0 failed |
| fuzzers (3) | Linux | 0 differ · 500/500 · 0 crash |
| `tests/r66 … r70` | Linux | all OK |
| the new test | **Wine** | matches |
| Windows | — | **NOT-RUN** |

## What I did NOT do, and why

- **The unchecked allocations, the output-extent API, the explicit-`cap` validation:** each is in the table, with
  the reason.
- **The installer was not rebuilt** (it carries `lib/` and the v243 compiler: stale since R34; it needs the owner's
  PC).
