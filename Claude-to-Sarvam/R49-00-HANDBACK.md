# R49-00 — Hand-back to Sarvam: the first lines

- **Commit on `main`:** `8408944296f7ac6b2fcb54272b40b48384bb801f` (v253 → v254), then this hand-back's commit. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v254) - sampurna sutra`.**
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** Library proofs: **226/226**.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 43 PASS / 0 FAIL / 1 NOT-RUN.** The
  NOT-RUN is Windows execution.
- **The guard, with the flag off, v253 → v254: 577 programs, 484 byte-identical, 93 refused identically, 0 DIFFER.**
  - It held on all three paths: Linux ELF, Linux PE, and the Windows compiler under Wine.
- **The 15 mutants, the split you asked for:**
  - **14 are REAL wrong answers.** R15 showed an input on which each gives a different, wrong result.
  - **1 is indistinguishable:** `ganita_paripurna_kramgun`.
  - **All 14 real ones are caught today.** A witness search over every surviving mutant of those 8 functions, run
    on today's tree, finds no input that tells any of them apart. Its only hit is `kramgun`'s timeout artefact.
  - **The three madhava sign errors were also checked by hand, and today's proof fails against each.** The
    evidence is `evidence-r49/madhava-sign-errors-caught.txt`.
- **WS1 (B2):** what you asked for was delivered in **R46 (v253)**. This round adds the two forms the brief named:
  - **`--debug-from=<N>`**;
  - **repeated flags, in any order.**

## WS2 — the fifteen mutants: REAL or INDISTINGUISHABLE

**The 15 are R15's** (`evidence-r15/proofs/lib-mutant-score.md`, "Every WITNESS"). They are the witnessed
mutants inside each function's contract; the other 8 witnesses R15 filed as out of contract. **R15's line numbers
are from 2026-10-16.** The library has moved since, so the "today" column is measured per function, not per line:

- `tools/lib_mutant_score.py` was run on each function;
- R15's witness search was run over **every** survivor of that function (`evidence-r48/witness-today-after.json`).

| # | Function | R15's mutant | R15's witness: input → true / mutant | Verdict | Today |
|---|---|---|---|---|---|
| 1 | `madhava_sin` | `A:+`, the lower reduction (`y + pi2` → `y - pi2`) | **`-18` → 0.750987 / 0.770223** | **REAL** | caught: **checked by hand**, `r18_madhava_reduction.sm` fails |
| 2 | `madhava_sin` | `N`, the same condition negated | `3` → 0.141120 / 0.141111 | **REAL** | caught (no witnessed survivor) |
| 3 | `madhava_sin` | `A:-`, the same line | `3` → 0.141120 / 0.141111 | **REAL** | caught |
| 4 | `madhava_cos` | `A:+`, the lower reduction | **`-18` → 0.660317 / 0.606488** | **REAL** | caught: **checked by hand** |
| 5 | `madhava_cos` | `N` | `2` → −0.416147 / −0.416148 | **REAL** | caught |
| 6 | `madhava_cos` | `A:-` | `2` → −0.416147 / −0.416148 | **REAL** | caught |
| 7 | `madhava_atan` | `A:-`, `prati 0.0 - r` → `prati r` | **`-20` → −1.520838 / +1.520838: the sign is lost** | **REAL** | caught: **checked by hand** |
| 8 | `madhava_atan` | `K:1`, the same line | `-20` → −1.520838 / +1.520838 | **REAL** | caught |
| 9 | `madhava_atan` | `N`, the `|x| > 1` branch | `-20` → −1.520838 / −1.520817 | **REAL** | caught |
| 10 | `util_chinha` | `K:0` | `1` → 1 / 0 | **REAL** | caught: **6/6 mutants killed, none survive** |
| 11 | `ank_gan` | `K:0` | `-9` → 1 / 2 | **REAL** | caught. Today's 2 survivors are on the absolute-value line, where both give 0 at 0; no witness |
| 12 | `suchi_srij` | `A:*`, `c * 8` → `c + 8` | `3037000499` → 0 / a handle | **REAL** (a list with far too little memory) | caught **by `r48_srij_fill.sm`**: the mutant crashes, exit 139. R18's input was rightly dropped in R35 because it depended on the machine |
| 13 | `avali_srij` | `A:*`, the same | `3037000499` → 0 / a handle | **REAL** | caught by `r48_srij_fill.sm` |
| 14 | `avali_srij` | `K:0`, the size guard | `MAX` → 0 / 1 | **REAL** | caught. R35's guard (`c > 2^60 - 1` → 0) and R18's `avali_srij(MAX)` proof; no witness today |
| 15 | `ganita_paripurna_kramgun` | `K:MAX` | `10^9` → MAX / "CRASH" | **INDISTINGUISHABLE** | the mutant removes only an early exit: the same saturated value, slower. The "CRASH" is the witness tool's 1-second limit (R18). **Still the only witnessed survivor today** |

**So: 14 REAL, all caught today. 1 INDISTINGUISHABLE.**

- **R18 reported "13 killed, 2 equivalent".** The difference is how R18 counted `ank_gan`, whose twin survives.
  Both `ank_gan` survivors today are equivalent, and its witnessed mutant is gone.
- **"Fix the first group"** needed proofs, not library changes: the 14 real ones are hypothetical bugs, and the
  proofs are what catch them. **Two of those proofs (rows 12–13) are new in R48.**

**The madhava sign error, demonstrated against today's proof** (`evidence-r49/madhava-sign-errors-caught.txt`):

```
madhava_sin  line 56  y = y + pi2 -> y - pi2     sin(-18):  0.750987 expected, 0.770223 given  -> proof FAILS
madhava_cos  line 76  y = y + pi2 -> y - pi2     cos(-18):  0.660317 expected, 0.606488 given  -> proof FAILS
madhava_atan line 104 prati 0.0 - r -> prati r   atan(-20): -1.520838 expected, 1.520838 given -> proof FAILS
```

**So "a maths function returning a wrong-signed answer passes 224 proofs" stopped being true at R18.**

**The one REAL wrong answer in the library itself was not among the 15, and is fixed:** R48's `meru`.

- **113 of the 2642 binomials with n ≤ 70 that fit in 64 bits were wrong.** `meru(62, 31)` came out negative.
- **Now 0.**

## WS1 — the debugger, in the brief's exact forms

**Already in R46:**

- `--debug=<name>` for a watch;
- `@N` for a start line;
- the exit summary, `[shodhan] samapti, vakya: N` followed by each scalar's final value.

**New in R49:**

```
sutram --debug=yoga --debug=i --debug-from=11 prog.sm prog
```

- **Does a repeated flag work? YES, now.** It works in any order, before the input.
  - Each `--debug=<names>` adds to the watch list.
  - **`--debug-from=N` is `--debug=@N`.**
  - The last line range given wins.
- **The R46 comma form stays:** `--debug=yoga,i@11`. It is checked to give the same trace as the repeated form,
  in every order tested.
- **How:**
  - Each extra flag is read, then dropped from `argv` the way R32 drops `--ffi`.
  - On Linux the freed slot becomes an empty entry, so the environment is still found. Measured: `SUTRAM_LANG` is
    still read after two flags are dropped.
  - Windows shifts `win_stack`. The Windows compiler, under Wine, gives the same trace.
- **A malformed `--debug-from` gives the usage and writes nothing.** Tested with `=`, `=x` and `=0`.

**No stepping UI, REPL or breakpoints,** as the brief said.

## WS3 — the guard, the suite, the corpus, the proofs

They are in the first lines.

- **The suite under `--debug`:** 189 programs print exactly their expected output once the trace is taken out.
  That includes R48's `kosh` example, which aborts the same way with and without the trace.

## What I did NOT do

- **The prose that still says "15 survived every proof", and B2 "not yet delivered"** (`README.md`,
  `PATH-TO-COMPLETION.md`, `PROJECT-MASTER.md`, `OPEN-ISSUES.md`). It is prose, so it is yours. The table above is
  what it should say.
- **Windows: out of scope, as the brief said.** Only Wine was used, for the guard and the trace. `backups/` and
  `Windows-to-Sarvam/` are untouched.
- **The non-Sanskrit packs are unchanged.**
