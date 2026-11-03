# R115-00 — The silent wrong answer: `chain40_reuse.sm` should be refused when compiled, and on the arena branch it ran and printed **99** - another block's number. Fixed on the branch (`3a6292e`), still not merged. A `dasham` into a `mala` converts on main. And the addendum: `sankhya_bindu` is withdrawn (v295) - my R113 version was wrong too.

**The program, the expected output, the actual output:**

| | |
|---|---|
| **program** | `evidence-r109/programs/chain40_reuse.sm` - a block makes `kosh k`, pushes **11**, and passes `k` out through a chain of 40 `prakriya`s (`f1` → `f2` → … → `f40`, which returns it) into the outer `bahar`. A second block then makes `kosh j` and pushes **99**. After both, `likha(bahar[0])`. |
| **expected** | **refused at compile time** - `E_KOSH_MANDAPA`, "the block's kosh goes to a prakriya that keeps it" - as main has done since v291. (Had it been allowed, the one defensible answer would be 11.) |
| **actual on `claude/r108-arena-review` (`0e71e54`)** | **compiled, ran, printed `99`, exit 0.** |

- **Commit on `main`:** `2c74c45` (the withdrawal; on top of R114, `c97a862`). **Review branch:**
  `claude/r108-arena-review`, now **`3a6292e`** (the fix), **not merged**.
- **Compiler on main: `Sutram 1.0 (v295) - sampurna sutra`** (was v294) - the addendum's withdrawal is the only code.
- **`crash corpus: 227 cases + manifest, 0 failed`.** **Suite: `suite: NO-EXPECTATION=4  PASS=297  (301 run)`**, FAIL=0
  (golden 329 is now the withdrawal's refusal). **The `R111 vocabulary` gate: 57 checks, 0 failed.**
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 60 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, `payload v243`; NOT-RUN: Windows execution).**
- **The guard, origin/main (v294) → v295, 707 programs:** **ELF, PE and Wine each 564 byte-identical, 142 refused identically, 1 DIFFER, 0 new** - the one DIFFER is example 329, whose source I rewrote into the withdrawal's refusal (it compiled on v294, it refuses on v295). Nothing else in the tree called the builtin. Wine's 1129 outputs are byte-identical to the Linux PE outputs (`evidence-r115/guard.txt`).
- **The branch after the fix:** its suite **288 / 0, as before**; Muse's 15 R105 attack probes and its `outer_grow2`,
  `cond2`, `cond_alias2` **behave exactly as before**; the 33- and 40-link chains are refused.

## WS1 - the diagnosis (run, not assumed)

It is **neither** of ChatGPT's two candidates by itself - not an alias seeing stale data after growth (the branch
refuses a second name), and not a reference surviving the arena by any path the branch checked. **It is the
outlives analysis giving up early, and the arena turning that into a wrong answer.**

1. **Where it starts** (`evidence-r115/chain-on-the-branch.txt`): on the branch, a chain of **32** keeping
   `prakriya`s is refused; **33** compiles; 40 compiles. The analysis, `r108_compute_esc`, is a fixpoint that marks
   one more link each round when the functions are defined in this order - and it **stopped after 32 rounds**, so
   `f1`'s parameter stayed marked "does not keep" and the call `bahar = f1(k)` was allowed.
2. **Why it prints 99** (`chain40_reuse_addr.sm`, printing addresses): `k`, `j` and `bahar` are **the same address**.
   The branch reclaims a block's `kosh` slots at block exit; the next block's `kosh` is given the same slot; the
   escaped `bahar` now reads `j`'s first element.
**A second source:** Muse's R110 ran my program on the branch binary independently - *"it compiles, runs, and prints
99 - the next block's number, not the original 11 - with exit 0"* - and reached the same cause (the 32-round cap)
and the same verdict on the two other shapes (a `vitti` second name and a ternary are both refused on the branch).

3. **Why main never printed a wrong number:** main never reclaims a block's `kosh` - v290 read the still-valid 11, and
   since v291 (R109, from ChatGPT R178's finding) main refuses the chain. **The bound was in code main and the branch
   share; main got the fix, the branch predates it.** Muse's R105 design attack confirmed the same bound in the
   source and called it unmeasured; this is the measurement.

## WS2 - the decision: fixed, and left unmerged (outcome 2)

**The defect is fixed on the branch, cheaply:** the same three changes main got in v291, ported - the fixpoint runs
to convergence (at most 128 × 6 + 1 rounds), a walk that overflows its stack counts as "keeps", and a full table
of block `kosh`s refuses instead of making the next one persistent and unchecked (Muse's correction: worse than
R178 said). **Cost: nothing at run time; compile time unmeasurable on the tree.** Pushed as `3a6292e` with rebuilt
binaries and a README note, so the branch no longer carries a known defect.

**It is not inherent to the arena (so not outcome 3):** the arena only made a wrong analysis visible.

**But I would not merge it, and it is not a cheap merge (outcome 2):**

- **It is not the design that was accepted.** It relocates slots on growth and refuses every second name for a block
  `kosh`; ChatGPT R178 specifies stable descriptors that keep aliases instead, and Muse's R105 attack, finding the
  descriptor core sound, lists eight gaps to settle before that is built. Merging the branch would ship the design
  R178 replaced.
- **It is four versions behind** (v290; main is at v294): the outlives fix, the vocabulary aliases, the `rachana`
  refusal and the `truti` token all touch the same file, and a merge needs its own rebase and a full guard - and it
  changes how every block `kosh` is stored, so the R101 memory gate's pinned "not reclaimed" result would flip.
- **The one benefit it has is available more cheaply on main** - next section.

## WS3 - if the arena were sound, would returning regions at block exit be small or large?

**With a sound arena there is nothing to return:** a block's `kosh`es are slots of the block's arena, and the block
already gives the arena back at its end (kb1, 100,000 blocks each with a 100-number `kosh`: 0 KB on the branch).
The region return is the other road - main keeps its regions and gives them back - and **on main it is a small
change**:

- each `kosh` on main is its own 64 MB `mmap` reservation (`R101A_REGION`, user pointer 40 bytes past the start);
- the compiler already knows **which `kosh`es belong to an open block** (R108's registry, which the outlives rule uses)
  and **every way a block is left** (R82 and R73 already instrument the block end and the early exits);
- so it is **one `munmap(ptr - 40, R101A_REGION)` per block `kosh` at each block exit** - roughly a day, with its gate.

**What it costs and risks:** one more system call per block `kosh` (kb1 has 100,000 `mmap`s already, so this pairs
each with a `munmap`; I estimate it, I did not measure it), and **safety then rests on the outlives rule** - after
v291 I know no path out, but any path it misses becomes a SIGSEGV instead of a read of stale-but-valid memory. That
is louder than the branch's failure (a silent 99), which is the better way to fail. The R106 reason for not doing it
(the R82 run-time check reads a dead `kosh`'s header) no longer applies, because since v291 no program in the tree or
in the R82 gate can reach that check.

**Not built**, as you asked.

## WS4 - `dasham d = 3.0; mala m[4]; m[0] = d` on v292: it converts

(`evidence-r115/dasham-into-mala-v292.txt`, the v292 compiler, Linux ELF)

| stored into `m[0]` | prints | exit |
|---|---|---|
| `dasham d = 3.0`, `m[0] = d` (your case) | **`3`** | 0 |
| `-7.0` | `-7` | 0 |
| `1.5 * 2.0` (computed) | `3` | 0 |
| into `vitti m[4]`, and `kosh_kship(k, d)` | `3`, `3` | 0 |
| `2.5` | `Sutram Error [E_DASHAM_VITTI]: dashama-phalam purnanka-seemayam na bhavati` | 1 |
| `10000000000000000000.0` (past the integer range) | the same `E_DASHAM_VITTI` | 1 |

**It does not store the bits any more, and it has not since v288** - R106 fixed Muse's trap 8 ("converted exactly,
as into a `vitti`"); your `4613937818241073152` is v286's behaviour. A whole-valued `dasham` becomes its integer; a
fraction or an out-of-range value stops the program. Not run on Windows.

## The addendum - `sankhya_bindu` / `sankhya_dot` withdrawn (v295), and a mistake of mine in R113

**My R113 "fix" was wrong for one container, and the addendum is right to withdraw it.** In R113 I replaced the
32-bit-float body with an integer dot product of 8-byte cells, reasoning that a `mala` or `kosh` cell holds an
integer. **That is false for a `kosh dasham`**, which holds 8-byte floats (reference §16) - I had tested `dasham m[3]`
and an untyped `kosh`, not the typed one. Running Muse R111's shapes against v293: two `kosh dasham` holding 2.5, 1.5
dot to **0** (the float bits multiplied as integers), where 8.5 is right (`evidence-r115/withdrawal.txt`). So v293
shipped a silent wrong answer for that input, and it is withdrawn now.

**The withdrawal is cheap** - the one code change this round - so it is done, as ChatGPT R187 designed it (a reserved,
refused name, not a missing one):

```
w.sm:4:11: Sutram truti [E_PRATYAHRITA]: sankhya_bindu (sankhya_dot) pratyahrita - asyah phalam ashuddham, sanshodhanam pratiksate
      likha(sankhya_dot(a, a, 1))
            ^
Sanket: dvayoh kosh dasham bindu-gunanaya: yoj sankhyiki, bindu_gunan(a, b) - laghutara dirghata eva pathyate
```

- **Both spellings**, keyed on the builtin, not the spelling: refused when the name is read, with file, line and
  column, **before** the old-name warning - nobody is told to switch from `sankhya_dot` to a withdrawn name.
  No output file is written.
- **The alternative it names works:** `yoj sankhyiki`, then `bindu_gunan(a, b)` on two `kosh dasham` gives **8.500000**
  for the same input. It reads the shorter length (ChatGPT R187's caveat, in the hint: *laghutara dirghata*).
- **The reference** (§4 and §4b) and the vocabulary page say it is withdrawn and why; example 329 is now that refusal;
  the `R111 vocabulary` gate checks both names refuse on ELF and PE with no warning and no output (its other 21
  pairs unchanged).
- **What it breaks in the tree:** nothing calls it (ChatGPT R187's census; the guard below).
- `E_PRATYAHRITA` (प्रत्याहृत, withdrawn) and its text need native-speaker review.

## Not done

- **Merging the arena** (WS2) and **the region return** (WS3): not built, as above.
- **Exception handling** (your status line: 55 error codes, no raise or recover): not in this brief's work.
- Not touched: `backups/`, `Windows-to-Sarvam/`, every pack file outside R114's token, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
