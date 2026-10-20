# R15-03 — WS3: how strong are the 303 library proofs?

**All 303, with one measure, on main's compiler, Linux.** Every number below is from
`evidence-r15/proofs/lib-mutant-score.md`, which has one row per function, ranked.

## The short answer

- **No proof is decoration.** For all 303 functions, the proofs kill the smoke-test mutant (the whole body
  replaced), **and at least one mutant shaped like a real bug.**
- **But 61 functions are only partly proven:** the proofs kill under 80% of the bug-shaped mutants that are
  not known to be equivalent.
  - **1 is WEAK:** `ganita.chakravala`, 49%.
  - **60 are PARTIAL:** 50–79%.
- **105 are STRONG (80–99%). 137 are COMPLETE.**
- **15 bug-shaped mutants pass every proof although I can show an input that tells them apart** (below), in
  8 functions. 8 more witnessed mutants differ only on inputs outside the function's contract, or where the
  contract says nothing.
- **818 surviving mutants are undecided.** They are in functions that take lists, strings or records, or
  whose effect is in memory or a file. My witness tool cannot feed those. **The ranking counts them against
  the proofs,** so it is pessimistic for those functions.

## The measure

`tools/lib_mutant_score.py` makes **mutants shaped like real bugs**, one change each. Every proof that can
reach the function is run against each mutant: the `tests/stdlib` goldens, the example goldens, and the
`proof_props.py` properties, with the same rules as `lib_proof_gaps.py`.

**6,247 mutants; every one compiled.**

| Kind | The change | Killed |
|---|---|---|
| **S** | the whole body becomes `prati 7777777`: the smoke test | **303 / 303** |
| R | `prati e` becomes `prati (e) + 1` | 288 / 295 (98%) |
| C | one comparison flipped (`<` `<=`, `>` `>=`, `==` `!=`) | 677 / 872 (78%) |
| N | one `yadi (c)` becomes `yadi ((c) == 0)` | 462 / 479 (96%) |
| A | one arithmetic operator replaced (`+` `-`, `-` `+`, `*` `+`, `/` `*`, `%` `/`) | 1,044 / 1,157 (90%) |
| L | `&&` and `\|\|` swapped | 17 / 18 (94%) |
| K | one integer literal `n` becomes `n + 1` | 1,793 / 2,299 (78%) |
| D | one statement deleted (an assignment, a store, a call) | 712 / 824 (86%) |
| **all but S** | | **4,993 / 5,944 (84.0%)** |

**This widens R8–R11's measure.**

- **Then:** R and C only, at most 12 C mutants per function; 935 of 1,119 killed.
- **Now:**
  - C is uncapped.
  - N, A, L, K and D are new, sampled to at most 40 per function, from a seed fixed per function.

**A surviving mutant is one of two things:**

- **a bug the proofs would let through**
- **equivalent:** no input can tell it apart, as with `a > best` vs `a >= best` in a maximum

**So every survivor was then given to a witness search** (`evidence-r15/proofs/witness_r15.py`). It reuses
R8's `lib_mutant_witness.py`: it runs the real function and the mutant side by side, on 300–600 inputs, and
reports the first input where they differ.

| Result | Survivors | What it means |
|---|---|---|
| **WITNESS** | **23** | an input tells it apart, and no proof uses it |
| **NO-WITNESS** | 110 | no input in the set told it apart: **likely equivalent**, not proven |
| **NOT-TRIED** | 818 | undecided (see below) |

**NOT-TRIED covers three cases:**

- **a parameter is a list, string or record** (694 survivors)
- **no number input runs cleanly,** because the parameters are addresses (47)
- **the function's effect is in memory or a file,** where comparing return values sees nothing. A
  constructor returns the same handle whether or not it initialised the memory behind it. That applies to
  `nighantu_srij`, `suchi_srij`, `avali_srij`, `mala_nava` and both `patra` functions. **I first counted
  those as NO-WITNESS; that was wrong, and is corrected.** (77 survivors)

**The score of a function** is: killed ÷ (mutants − NO-WITNESS survivors). **Likely-equivalent survivors are
not held against a proof; undecided ones are.**

| Verdict | Score | Functions |
|---|---|---|
| **DECORATION** | S killed, nothing else | **0** |
| **WEAK** | under 50% | **1** |
| **PARTIAL** | 50–79% | **60** |
| STRONG | 80–99% | 105 |
| COMPLETE | 100% | 137 |

## The weakest ten

| | Function | Killed | Score | Survivors: witness / likely equivalent / undecided |
|---|---|---|---|---|
| 1 | `ganita.chakravala` | 31 / 63 | 49% | 0 / 0 / 32 |
| 2 | `suchi.avali_srij` | 18 / 36 | 50% | 2 / 0 / 16 |
| 3 | `nighantu.nighantu_kunji_gudh` | 3 / 6 | 50% | 0 / 0 / 3 |
| 4 | `sangrah.rakh_yuj` | 1 / 2 | 50% | 0 / 0 / 1 |
| 5 | `roop.roop_pad_dakshin` | 17 / 33 | 52% | 0 / 0 / 16 |
| 6 | `nighantu.nighantu_srij` | 21 / 40 | 52% | 0 / 0 / 19 |
| 7 | `suchi.suchi_srij` | 18 / 33 | 55% | 1 / 0 / 14 |
| 8 | `khand.khand_bandh` | 9 / 16 | 56% | 0 / 0 / 7 |
| 9 | `patra.patra_likh_sarv` | 17 / 30 | 57% | 0 / 0 / 13 |
| 10 | `mala.mala_nava` | 4 / 7 | 57% | 0 / 0 / 3 |

**The full ranking of all 303, with each function's surviving mutants by line, is in the evidence file.**

**How to read it:**

- **`chakravala` is the weakest by a margin.**
  - 32 survivors, mostly the boundaries of its candidate search (lines 108–122).
  - Some of those are surely equivalent. For example, `f < 0` versus `f <= 0` before `f = 0 - f` gives the
    same result.
  - **But the boundaries of the search window (`m >= 0 && m <= 3037000499`, line 115) are not pinned by any
    proof.**
- **`nighantu_kunji_gudh` and `suchi_vardh` are reached only through a caller.** No proof names them.
- **Five of the ten are constructors:** `avali_srij`, `nighantu_srij`, `suchi_srij`, `mala_nava`,
  `khand_bandh`. **Their surviving mutants change how the new object is initialised.** The proofs then use
  the object in ways that hide it.
  - **Example: `suchi_srij`'s overflow guard,** for a capacity so large that `cap * 8` wraps. Its
    documentation says it returns 0. **A mutant that breaks the guard survives, with a witness:**
    `suchi_srij(3037000499)` should give 0, and the mutant gives a handle.

## The 23 witnesses

**Clear defects the proofs would let through (8 functions, 15 mutants).** The input is within what the
function promises, by its documentation or by what it obviously computes:

| Function | Mutant | Input | Real | Mutant |
|---|---|---|---|---|
| `sadhan.util_chinha` | `K:0@L44` | `1` | 1 | 0 |
| `ank.ank_gan` (digit count) | `K:0@L16` | `-9` | 1 | 2 |
| `ganita.ganita_paripurna_kramgun` | `K:MAX@L565` | `1000000000` | MAX (saturated) | crash |
| `suchi.suchi_srij` | `A:*@L52` | `3037000499` | 0 (documented overflow guard) | a handle |
| `suchi.avali_srij` | `A:*@L383`, `K:0@L384` | `3037000499`, `MAX` | 0 | a handle / 1 |
| `madhava.madhava_sin` | `N@L56`, `A:-@L56`, `A:+@L56` | `3`; `-18` | 0.141120; 0.750987 | 0.141111; 0.770223 |
| `madhava.madhava_cos` | `N@L76`, `A:-@L76`, `A:+@L76` | `2`; `-18` | -0.416147; 0.660317 | -0.416148; 0.606488 |
| `madhava.madhava_atan` | `N@L98`, `A:-@L104`, `K:1@L104` | `-20` | -1.520838 | -1.520817; **1.520838 (sign lost)** |

**The madhava ones matter most.**

- **No proof takes the lower half of the argument reduction:** `yadi (y < 0.0 - pi)`, line 56 in `sin`,
  line 76 in `cos`.
- **No proof reaches `atan`'s negative branch for `|x| > 1`** (`neg == 1`, line 104).
- **So a sign error there passes every proof.**
- `sin(-18)` is within the documented range ("exact for |x| <= ~1e15").

**Outside the contract, or where the contract says nothing (5 functions, 8 mutants), not counted as defects:**

- **`ank.seemit` and `ganit.ganit_seemit` with `lo > hi`.** `ganit_seemit` documents "requires lo <= hi".
- **`chandas.meru` with negative or overflowing arguments** (3 mutants). It has no documented range.
- **`ganita.kuttaka` where `mahattam(a, b)` does not divide `c`.** Its contract requires it (2 mutants).
- **`ganita.brahmagupta_kshetr` with sides that form no quadrilateral** (16, 5, 4, 1000). What it returns
  then is not documented.

**All 23, with inputs, are in the evidence file.**

## What a reader should not conclude

1. **"COMPLETE" is not "proven correct."** It means every bug-shaped mutant was killed, or no input from a
   fixed set told it apart. **These eight kinds are not every bug.**
2. **The 818 undecided survivors are the real open question.**
   - I drew 30 at random (seed 15) and read each against its source.
   - **Clearly a missed defect: 3.**
     - `khand_gan_swar` stops counting `i`, or stops counting `u`, and no proof notices.
     - `brihat_gun`'s top-digit carry is subtracted instead of added, and no proof notices. Probably the
       proofs multiply numbers too small to carry into the top digit.
   - **A loop that runs once more, writing one cell past the end: 2.**
   - **Only the 0 written after the output changes: 3.**
   - **Equivalent: 4.**
   - **Undecided without reading the callers: 18.**
   - **So the undecided pool holds real gaps, but not mostly.** A generator of list, string and record inputs
     for the witness would decide most of them. That is the next step if you want these numbers to be firmer.
3. **A function's score is only as good as its proofs' inputs.** Some functions are reached only through a
   caller. **For those, a low score can mean the caller never passes the input that matters.** That is still
   a gap, but the fix is a new proof of the function itself.

## Tools and checks

| What | Environment | Result |
|---|---|---|
| `python3 -B tools/lib_mutant_score.py --jobs 2` (about 40 minutes) | Linux | 303 functions, 6,247 mutants, run `lib-mutant-score-run.txt` |
| `python3 -B Claude-to-Sarvam/evidence-r15/proofs/witness_r15.py SCORE.json OUT.json` | Linux | 23 / 110 / 818 |
| `python3 -B Claude-to-Sarvam/evidence-r15/proofs/make_report.py SCORE.json WITNESS.json OUT.md` | Linux | `lib-mutant-score.md` |
| baseline: every golden and property passes on the unmutated library first (the tool stops otherwise) | Linux | PASS |
| Windows | — | NOT-RUN |
