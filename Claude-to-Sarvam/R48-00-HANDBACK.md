# R48-00 — Hand-back to Sarvam: the first lines

- **Commit on `main`:** `13a148284e09a90fbe33b234bb82b06ebcbf1266`, then this hand-back's commit. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v253) - sampurna sutra`, UNCHANGED.** One library function and three test programs
  changed.
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** That is 224 plus the `kosh` example.
- **Library proofs: 226 / 226.** That is 224 plus 2 new proofs. Property proofs: 86/86.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 43 PASS / 0 FAIL / 1 NOT-RUN.** The
  NOT-RUN is Windows execution.
- **The guard, pairwise** (each program's old and new source, the same compiler): **577 programs, 470
  byte-identical, 93 refused identically, 11 DIFFER, 3 new.**
  - **The 11 DIFFER are exactly the 11 existing programs that `yoj chandas`,** because `meru` changed. I checked
    that every one of them imports `chandas`, and that no other program differs.
  - All 11 still print their expected output (suite and proofs PASS).
  - It held on Linux ELF and on Linux PE.

## WS1 — A1, the empty `kosh`: reproduced, and it is a checked error, not a defect

```
kosh_pop on an empty kosh:     exit 1, output: Sutram Error: riktat koshat kosh_pop
kosh_peek on an empty kosh:    exit 1, output: Sutram Error: riktat koshat kosh_peek
kosh_dequeue on an empty kosh: exit 1, output: Sutram Error: riktat koshat kosh_dequeue
```

**It aborts, with its own diagnostic, exactly like an index out of bounds.** **The programmer CAN handle it:**

- **The ok channel already exists:** `kosh_empty(k)` and `kosh_len(k)`.
- **Ask first, then pop.** `examples/257_r48_kosh_empty.sm` pops in a loop with `kosh_empty`, never aborts, and
  then shows the abort once on purpose. It is now in the suite.

**So I made no code change, and here is why the smallest "fix" would be worse:**

- **A sentinel cannot work.** Any value, 0 included, can be stored in a `kosh`, so no return value can mean
  "empty". `ganita_paripurna_*` can use 0 because its results have a documented range; a `kosh` element does not.
- **An ok-channel variant would duplicate `kosh_empty`.**

**If the owner wants a non-aborting pop anyway, the right shape is the existing error type.** For example,
`kosh_pop_phal(k)` would return a `phal` (R25: `siddhi`/`dosh`). **That is a language decision, not built.**

**One documentation defect found:**

- `docs/LANGUAGE-REFERENCE.md` (line ~410) quotes the diagnostic as `rikta kosh se kosh_pop`.
- **The compiler prints `riktat koshat kosh_pop`.**
- It is for ChatGPT or you to correct.

## WS2 — A2, the fifteen survivors: re-measured today, and a real defect found behind them

**First, a correction to the record.**

- `README.md`, `PATH-TO-COMPLETION.md`, `PROJECT-MASTER.md` and `OPEN-ISSUES.md` say "15 survived every proof".
- **R18 (my round) gave the 15 a proof each: 13 killed, 2 equivalent.** That text has been stale since R18.

**Then I re-measured, because a later change could have reopened them.** I used `tools/lib_mutant_score.py` on 13
functions: the R18 ones, plus the 5 functions of R15's other 8 witnesses. Then I ran R15's witness search over all
73 of their survivors. **One had reopened, and one hid a real bug.**

| Group | Mutants | Verdict |
|---|---|---|
| **`madhava_sin`, `_cos`, `_atan` (9)**, `util_chinha`, `ank_gan` | 11 | **still killed** by R18's proofs. The sign error in the lower half of the reduction is among them |
| **`suchi_srij`, `avali_srij` `A:*`** (`c * 8` → `c + 8`: a list given far too little memory) | 2 | **reopened.** R35 rightly dropped R18's 24 GB input, whose answer depended on the machine, and that left this mutant alive. **Fixed by a proof:** `tests/stdlib/r48_srij_fill.sm` fills a 1000-cell list and queue. The mutant crashes (exit 139); the real function gives 499500 and 999 |
| `ganita_paripurna_kramgun` `K:MAX` | 1 | **equivalent in value** (R18): it removes only an early exit. The "CRASH" is the witness tool's 1-second timeout |

**The real defect: `meru(n, k)` itself was wrong**, not a mutant.

- R15 filed `meru`'s witness `(100, 16)` as "outside the contract".
- **But C(100, 16) = 1345860629046814650 fits in 64 bits.** It is a valid input with a valid answer, and
  `meru(100, 16)` returned **192939124439967674**.
- **The cause:** `res * (n - r + i)` passed 2^63 before the division, even when the answer fits.
- **I measured every `n` from 0 to 70 against Python's `math.comb`** (`evidence-r48/meru-all-compare.txt`):

| | Answers that fit in 64 bits | Wrong |
|---|---|---|
| **before** | 2642 | **113**, e.g. `meru(62, 31) = -129627907186982512` (negative!), true 465428353255261088 |
| **after** | 2642 | **0** |

- **The fix** is exact and standard. It divides out `g = gcd(res, i)` before multiplying. `i / g` then divides
  `(n - r + i)`, and no step is larger than C(n−r+i, i) ≤ the answer.
- **Proof:** `tests/stdlib/r48_meru_bada.sm`, with values from `math.comb`.

**What remains, each checked** (`evidence-r48/witness-today-after.json`):

- **Outside the documented contract, 7 mutants in 4 functions.** I re-read each, and **each documents its range**:
  - `seemit` and `ganit_seemit` with `lo > hi` ("requires lo <= hi").
  - `meru` with a negative `k` (it returns 0 by its first line), and `meru(3037000499, 3037000499)`, whose answer
    is 1 but whose `A:-` mutant overflows. That mutant is out of range for any proof that keeps the real answer.
  - `kuttaka` without `gcd | c` (its contract).
  - `brahmagupta_kshetr` with sides that make no quadrilateral.
- **No witness, 62 survivors.** The search found no input that tells them apart. That is evidence of equivalence,
  not proof. Most are boundary flips at exactly ±π, or one more series term, which is invisible at the printed
  precision.

**So the honest summary: of R18's 15, 13 still hold; the size mutant had reopened and has a proof again;
`kramgun` stays equivalent. And one of R15's "out of contract" 8 was a real wrong answer, now fixed.**

## WS3 — B2, the debugger usable: ALREADY DONE in R46 (v253)

Every item asked for was delivered and is in the gates (`R46 debug usable`, 14 checks; `R45 debug`, 8 checks):

- **Named watches:** `--debug=yoga,i`.
- **A start line:** `--debug=...@N`, or a range, `@N-M`.
- **A one-line exit summary:** `[shodhan] samapti, vakya: <statements run>`, then every scalar.

**`OPEN-ISSUES.md` B2 ("not yet delivered") is stale.** Evidence: `Claude-to-Sarvam/R46-00-HANDBACK.md` and
`evidence-r46/`, including the sign error found with it. The guard, flag off: 0 DIFFER (R46).

## WS4 — the guard, the suite, the crash corpus

These are in the first lines. **Not rerun this round:** Wine, because the compiler is unchanged. The changed library
code is compiled by the same v253 compiler that R46 measured under Wine.

## What I did NOT change, and why

- **The prose that says "15 survived every proof"** (`README.md:190`, `PATH-TO-COMPLETION.md:59`,
  `PROJECT-MASTER.md:319`, `OPEN-ISSUES.md` A2/B2). It is prose, so it is yours. The numbers above are what it
  should say.
- **The 818 undecided** (A3). They are not in this round; they need a list and string input generator.
- **`kosh_pop_phal`.** It is a language decision.
- **Not touched:** `backups/`, `lang/` and `windows/`. **The non-Sanskrit packs are unchanged.**
