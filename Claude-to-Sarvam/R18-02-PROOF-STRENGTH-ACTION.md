# R18-02 — WS2: the proof-strength review, and the action taken

## Plainly: which of the 303 proofs are decoration

**None.** For every one of the 303 library functions, the proofs kill the smoke-test mutant (the whole body
replaced) **and at least one mutant shaped like a real bug** (an off-by-one result, a moved boundary, a
negated condition, a wrong operator, a changed literal, a deleted statement). **No proof is decoration, and
none should be deleted.** (R15-03, measured with `tools/lib_mutant_score.py`: 6,247 mutants, 84% killed.)

**What is weak, in one line each:**

- **1 WEAK:** `ganita.chakravala` (49%); the boundaries of its candidate search are not pinned.
- **60 PARTIAL** (50–79%); the worst are five constructors whose initialisation no proof reads.
- **818 surviving mutants are undecided** (functions that take lists, strings or records; the witness tool
  cannot feed those). A hand-read sample of 30: 3 clear misses, 4 equivalent, 23 undecided.

## The action I took this round

**The 15 mutants that survived every proof although an input told them apart now have a proof each:**

| Proof file (`tests/stdlib/`) | Functions | The inputs the proofs lacked |
|---|---|---|
| `r18_madhava_reduction.sm` | `madhava_sin`, `madhava_cos`, `madhava_atan` | `x` below −π (the lower half of the argument reduction: −18, −4); `atan` of −20 and −1.5 (the negative branch for `|x| > 1`); `atan(20)` for symmetry |
| `r18_sign_digits_kramgun.sm` | `util_chinha`, `ank_gan`, `ganita_paripurna_kramgun` | `util_chinha(1)`; `ank_gan(-9)`, `ank_gan(-1234)`; the saturating factorial of 10⁹ (the early exit) and of 21 |
| `r18_srij_overflow_guard.sm` | `suchi_srij`, `avali_srij` | a capacity whose byte size wraps (3037000499, MAX): the documented guard returns 0 |

**Every expected value was checked against Python's `math`** (`sin(-18) = 0.750987…` and so on) **before it
was recorded.**

**Re-scored after adding them** (`tools/lib_mutant_score.py --function …`, Linux):

| Function | Killed before → after | The witnessed mutants |
|---|---|---|
| `madhava_sin` | 20/28 → **23/28** | all 3 killed |
| `madhava_cos` | 20/28 → **23/28** | all 3 killed |
| `madhava_atan` | 38/47 → **41/47** | all 3 killed |
| `util_chinha` | 5/6 → **6/6** | killed |
| `ank_gan` | 20/23 → **21/23** | killed; its twin survives |
| `ganita_paripurna_kramgun` | 14/15 → 14/15 | **not killed, and rightly:** the mutant (`maxv` = MAX + 1, which wraps) only removes the early exit; it computes the same saturated value, slower. The witness tool's 1-second limit had called that a crash. Equivalent in value. |
| `suchi_srij` | 18/33 → **19/33** | killed |
| `avali_srij` | 18/36 → **20/36** | both killed; one twin survives |

**"Twin":** two mutants on one line carry the same tag (`K:0@L16` is both `x < 0 → x < 1` and
`0 - x → 1 - x`). The proofs kill the one the witness found; the other is equivalent (`x < 1` and `x < 0`
differ only at `x = 0`, where `0 - 0` is `0` either way).

**So the 15 are closed: 13 killed, 2 equivalent on inspection.** `tools/proof_lib.py`: 220 / 220.

## What I did not do, and would next

- **The constructors and `chakravala`:** one proof each that reads the object straight after construction,
  and one that pins the search window. **A round.**
- **The 818 undecided:** a list-and-string input generator for the witness tool. **Half a round.** Not before
  the above.
