# R147-00 — v313. Task 4: all fourteen slice shapes are refused at compile time on v313 - the ten old ones and the four new ones, with the release compiler, the Windows compiler under Wine, and both mutant compilers. On v307, eleven of the same fourteen programs compiled: eight read the old elements, one crashed, one leaked an address, and one printed the result of comparing an address. No failure, so I did the rest. Task 1: I changed my answer. ChatGPT is right about generated code, so the budget is now a stop that no statement the syntax tree can hold reaches, and its message says so. Task 2: both findings fixed. Task 3: the scope sentences. Task 5: the gate now holds all fourteen.

## Release line

```
gates: 77 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v313) - sampurna sutra
```

- **Commit:** the one carrying this file (SHA in my chat report). Base: `108301e` (v312 + ROUND-147).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `Sutram-Setup.sha256` = `85364c159c15d348818b6c187f12260a18bfa899abe007c474eb03b80806b465`, `PASS payload v313 = compiler v313`, self-test exit 0 under Wine, gate `R140 package` 7/0.
- **THE GUARD, v312 (`108301e`) → v313, 782 programs, compiled the ordinary way before and after, bytes compared:**
  - **Linux ELF: 587 identical, 181 refused identically, 0 DIFFER.** The other 14 are this round's new probes, which v312's tree does not have; both compilers refuse them.
  - **Linux PE: 587 identical, 181 refused identically, 0 DIFFER.**
  - **The 181 refusals print v312's exact messages.**
  - **No existing program changes or is newly refused.** The runtime and `sutram-link.exe` are byte-unchanged.
  - **The Windows compiler (v313) under Wine:** = the Linux PE output for all 782 (587 identical, 195 refused by both - the 181 and the 14 new probes), 0 differ.

**Not done:** **no native Windows run of v313.**

## Task 4 - fourteen shapes, one table

Each program keeps a slice of `kosh k` past a growth and then reads through it. An escape prints **7** (the old elements) where `k[0]` is 99. The programs are in `tests/r147/slices/`.

| # | shape | **v313** (Linux ELF; Windows compiler under Wine: the same) | v307, the same program |
|---|---|---|---|
| 1 | stored in a fixed-size array cell (`box[0] = k[0:1]`), then grow | **rejected** `E_KOSH_VIBHAG` | compiled; **outdated value** 7 |
| 2 | passed to an untyped parameter of a prakriya that grows `k` | **rejected** `E_KOSH_VIBHAG` | **outdated** 7 |
| 3 | returned as an untyped result, then grow | **rejected** `E_KOSH_VIBHAG` | **outdated** 7 |
| 4 | passed to a prakriya called through a variable, which grows `k` | **rejected** `E_KOSH_VIBHAG` | rejected (`E_KOSH_DVARA`) |
| 5 | stored in a module-level `vitti` | **rejected** `E_KOSH_VIBHAG` | **outdated** 7 |
| 6 | stored in a record (`rachana`) field | **rejected** `E_KOSH_VIBHAG` | **outdated** 7 |
| 7 | written into raw `nirmmita` memory | **rejected** `E_KOSH_VIBHAG` | **outdated** 7 |
| 8 | passed through a `dasham` parameter of a prakriya that grows `k` | **rejected** `E_KOSH_VIBHAG` | **crash** (segmentation fault) |
| 9 | used in arithmetic (`k[0:1] + zero`) and kept | **rejected** `E_VIBHAG_ANKA` | **outdated** 7 |
| 10 | a module-level initializer binds a `kosh` (`vitti g = make_kosh()`) | **rejected** `E_KOSH_DVARA` | compiled; prints the descriptor's address |
| 11 | *new:* a slice inside a comparison, used as an index (`box[k[0:1] > zero]`) | **rejected** `E_VIBHAG_ANKA` | compiled; prints 5 (an address comparison) |
| 12 | *new:* passed through two prakriyas in sequence, the inner one growing `k` | **rejected** `E_KOSH_VIBHAG` ("outer may grow kosh") | rejected |
| 13 | *new:* stored in a `kosh` element (`k2[0] = k[0:1]`) | **rejected** `E_KOSH_VIBHAG` | **outdated** 7 |
| 14 | *new:* at an inline-assembly boundary (`yantra(s)`) | **rejected** - `yantra` takes only a literal string of machine bytes, so a value cannot be given to it (syntax error) | the same |

**Plainly: all fourteen are rejected at compile time on v313.**
- **None compiles, so none gives a correct, outdated or crashing value.**
- **On v307, eleven of the fourteen compiled:** eight read the old elements, one crashed, one leaked an address, one compared an address. **So the probes are real.**
- **The Windows compiler under Wine gives the same fourteen refusals.**

**Shape 14 needs a sentence.** `yantra` inserts raw machine bytes. Bytes that read the stack can read a slice's descriptor, and nothing can stop them. **That is outside the memory model by its own statement** (`docs/MEMORY-MODEL.md`: *"`yantra` permits inline bytes. No checked ownership, valid-address, object-provenance, alignment or race guarantee is established."*). The boundary that can be checked is whether a value can be handed to it, and it cannot. **I do not claim a guarantee across machine code.**

**Not run:** these fourteen on native Windows.

## Task 5 - does the gate cover them?

**It did not:** before this round, gate `R137` had the arithmetic shapes, the walk-stack cases and the initializer cases. Its door shapes (1-8) lived in another gate (`R134 one predicate`), and 11-14 were nowhere.
- **Now all fourteen are in `R137 slice is not a number`** (89 checks), read from `tests/r147/slices/`. A check also fails the gate if that folder and the table disagree.
- **Both mutant compilers** (an entry point that forgets the check) **also refuse all fourteen.** Shapes 1-8 and 12-13 are refused by the doors, not the walk, so the mutants do not touch them. That is expected, and it is now measured.
- **On v307 the new cases fail 12 of 14** (`evidence-r147/slice-gate-on-v307.txt`): the eleven that compile, and shape 4, which v307 refuses with another code. Shapes 12 and 14 are refused by v307 too.

## Task 1 - the budget, as a rule: I changed my answer

**ChatGPT's point is the right one.** A margin over the corpus says nothing about generated code. An expression of 10,000 terms from a code generator is legitimate, and v312 refused one of 8,200 that the compiler could otherwise hold. **A size limit belongs where the compiler actually runs out, not below it.**

**The rule (v313):**
- **A program meets one size limit: its syntax tree.** That is 3 MiB, at most 43,690 nodes for the whole program including what `yoj` brings in. Past it, the existing refusal *"vakya-vriksh seema atikram"* (the tree is full). One `z + z + …` expression of 21,829 terms fits, and **it compiles on v313.**
- **The check's budget is a stop, not a limit: 349,521 steps.** That is 8 fields for each of the 43,690 nodes, plus one - the most any statement the tree can hold can take.
  - **The gate reads `AST_HEAP_CAP`, `AST_NODE_SIZE` and the walk's field loop from the source,** and fails if the budget is not that bound.
  - **So no statement that compiles can reach it.** If it fires, the walk visited something no tree has: a compiler defect.
- **The message says exactly that, and what to do:** *"Sutram truti [E_VAKYA_SEEMA]: antarika seema - vakyasya parikshanam 349521 padeshu na samaptam; vakya-vrikshe sthitam vakyam etavat na bhavati, ato'yam sankalakasya doshah"*. In English: an internal limit; the check did not finish in 349,521 steps; no statement in the tree is that large, so this is the compiler's defect. The hint: *report it (line, program); meanwhile split the statement into smaller ones.*
- **Tested, as ChatGPT proposed:** a `-DR143_WALK_BUDGET=64` build refuses 40 terms with that message, on every gate run. With that build, every example and library compiles unchanged: **the margin stays measured** (largest real statement 52 steps).
- **The language reference** now has a "Size limits" paragraph: the tree is the limit, the budget is not, and what each message means and what to do.

**Why not 200,000?** It is also unreachable, by measurement (the widest statement takes 87,316 steps), **but not by construction.** 349,521 follows from the tree's capacity, and moves with it if the heap is ever made larger.

## Task 2 - the two findings

**1. The instruction label clipped.** The label was 26 px high - one line - and its text wraps to two lines at 530 px. The native screenshot shows the second line gone.
- **Fixed:** the label is 52 px high, and the licence box starts below it (y 118, 192 px high, still above the radio buttons).
- **Checked at two text widths** under Wine (`evidence-r147/`):
  - with Wine's default font, the label breaks after *"You must"*;
  - with a Devanagari-capable serif font linked, it breaks after *"accept the"*.
  - **Both show "the terms to continue." in full.**
- The window is fixed-size and not DPI-aware, so Windows scales it as a whole and the wrap does not change with scale.
- **The gate** counts the label's lines with a font wider than Segoe UI, at the label's width and at 85% of it (2 and 2). It requires 25 px a line, and the label to end above the box.
- **The same count found one more tight label:** the welcome page's second paragraph needs three lines in a wider font and had 72 px. It has 78 now.

**2. Uninstall left `%TEMP%\STM7C1C.tmp`** with its script and log.
- **Fixed:** on success the uninstaller removes that folder, **only when** all of these hold:
  - it is directly in TEMP;
  - its name is the wizard's (`STM` + hex + `.tmp`, from `GetTempFileNameW`);
  - it holds exactly `uninstall-core.ps1` and `uninstall.log`;
  - the log is this run's.
- The files are removed by their exact paths and the folder by a **non-recursive** delete, so anything else in it keeps it.
- **A failed uninstall keeps both,** and the message box names the log.
- **Gate:** `R143 installer first contact` (12 checks).
- **NOT RUN natively.** The older `STM1E91.tmp` from an earlier round is not removed: it is not this run's.

## Task 3 - the evidence scope

**In the release notes:**
- **v313** - *passed the Linux gates, the byte-for-byte guard against v312 and the Windows compiler under Wine; it has not been installed, run or uninstalled on Windows, and untested guarantees remain unclaimed*. Then what it does not claim.
- **v312 on Windows** - *passed the reported first-contact checks on one existing user account (Windows 11 Home 26300, not elevated)*. Each check is named. Then *two acceptance findings recorded (both fixed in v313), and untested guarantees remain unclaimed*.
- **The licence rendering:** **verified on native Windows** (Sanskrit and Hindi visibly drawn). **Not under Wine,** which draws those lines in the licence box as empty boxes - a Wine font limitation. **My R144 "nobody has seen it" is out of date.**
- **Not established by the v312 run:**
  - a new machine or user profile;
  - fonts on other machines;
  - the suite time - 24% slower than v311, one sample, not attributed;
  - whole-machine cleanup;
  - out-of-memory;
  - the race.

## For Windows, v313

1. **The licence page:** both lines of the instruction.
2. **Uninstall from Settings:** afterwards no new `%TEMP%\STM*.tmp` folder remains.
3. **The fourteen probes** in `tests/r147/slices/`: each refused with the code in the table.
4. **The widest statement compiles:** 21,829 terms of `z + …`, generated by `tests/r143/test_walk_budget.py`.

Evidence: `Claude-to-Sarvam/evidence-r147/`.
