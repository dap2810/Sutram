# R141-00 — v310. WS1: a module-level initializer now gets a statement's checks; C1 and a second shape (a `kosh` bound to a module `vitti`) are refused, and the language has no other non-statement expression. The right shape is a check at every entry into expression code generation, not at binding - and there are exactly two entries, both now gated. WS2: each R208 ownership finding answered by name; the last one - two reads before the lock - is fixed and gated. WS3: the late-recovery recopy was fixed in R140; it now checks the file itself, not the journal's word.

## Release line

```
gates: 75 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v310) - sampurna sutra
```

- **Commit:** the one carrying this file (SHA in my chat report). Base: `040a31f` (v309).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Installer:** `Sutram-Setup.sha256` = `bb134603d70d49c4abd08112b77a5309ff447280f8754cb4e6e24cb4626bba47`, `PASS payload v310 = compiler v310`, self-test exit 0 under Wine, gate `R140 package` 7/0.
- **THE GUARD, v309 (`040a31f`) → v310, 768 programs, compiled the ordinary way before and after, bytes compared:**
  - **Linux ELF: 587 identical, 181 refused identically, 0 DIFFER.**
  - **Linux PE: 587 identical, 181 refused identically, 0 DIFFER.**
  - **The 181 refusals print v309's exact messages** (paths and version normalised).
  - **No existing program changes or is newly refused.** The runtime and `sutram-link.exe` are byte-unchanged.
  - **The Windows compiler (v310) under Wine: = the Linux PE output for all 768 (587 identical, 181 refused by both), 0 differ.**

**Not done:**
- **No native Windows run of v310,** and no PowerShell here: the engine change (lock order) is checked by reading and the static gate.
- **Two boundaries ChatGPT named are still untested natively:** two installers at once, and a stop between two journal records.

## WS1 - the module-level initializer

**Reproduced on v309, and refused on v310:**

| module-level initializer | v309 | v310 |
|---|---|---|
| `vitti leaked = make_kosh() + zero` (ChatGPT's C1) | compiles; prints the descriptor's address | `E_KOSH_GANIT` |
| `vitti leaked = make_kosh() == 0` | compiles; prints `0` | `E_KOSH_GANIT` |
| `vitti leaked = (1 ? make_kosh() : make_kosh()) + 0` | compiles; an address | `E_KOSH_GANIT` |
| **`vitti leaked = make_kosh()`** - a second shape, found while checking the first | **compiles; a `kosh` in a module `vitti`**, the R127 global door opened by an initializer | `E_KOSH_DVARA` |
| `vitti leaked = keep(make_kosh())`, `likha(make_kosh())` | already `E_KOSH_DVARA` (the call doors) | same |
| control: `vitti g = 3 + f()` | 7 | **7** |
| the same `make_kosh() + zero` inside `mukhya` | `E_KOSH_GANIT` | same |

**The fix (`src/sutram_compiler.asm`, `r56_gen_global_initializers`).** Before each initializer is generated:
- it runs `r137_check_stmt` on the declaration - the same walk a statement gets;
- and the module-`vitti` door: `r134_holds_kosh` on the value, refused with the global door's message.

**Bind or write - which shape is right?** **Neither, exactly. The right place is every entry into expression code generation:**
- **A binding check would miss what is never bound:** an expression statement (`keep(k[0:1] + zero)`), a condition, an argument, an index. These were all measured as refused in R140, through `gen_stmt`.
- **A write check would miss what is never written:** a condition, or a `likha` argument.
- **What every one of these has in common is that it enters code generation.** In this compiler there are exactly two such entries:
  - `gen_stmt` - `gen_block` is the only statement loop, and the debug instrumentation also goes through `gen_stmt`;
  - `r56_gen_global_initializers` - the module-level `vitti`s, generated at process entry.
- **v310 puts the same walk at both.** The R137 gate now checks the compiler's source: `r137_check_stmt` is called in exactly those two places. A new entry - an inliner, a new kind of global - fails the gate until it gets the walk.
- So the narrow fix *is* the class fix here; **no bigger change is needed.**

**What else is not a statement?** Your list, each measured on v309:

| form | in Sutram? | covered? |
|---|---|---|
| a record (`rachana`) field default | **no** - `rachana P { x = 3 }` is a syntax error | nothing to cover |
| a `prakriya` default argument | **no** - `prakriya f(x = 3)` is a syntax error | nothing to cover |
| a module-level `kosh` | **no** - `kosh G[1]` at module level is a syntax error, and a `kosh` in a module `vitti` is refused (R127; from v310 also by initializer) | yes |
| a constant | **no** - `sthira C = 3` is a syntax error; there is no `const` form | nothing to cover |
| a module-level `vitti` initializer | **yes** | **yes, from v310** |
| a module-level `mala` | **no** - a syntax error | nothing to cover |

**ChatGPT's hardening point - the walk's node budget passed silently when it ran out.** It now **refuses** (`E_VAKYA_SEEMA`: the statement is too large to finish checking). **It is unreachable today, and this is the proof:**
- the AST heap is 3 MiB (`AST_HEAP_CAP`), and each node is 72 bytes, so a whole program has at most 43,690 nodes;
- the budget is 200,000 per statement.
- Separately, the walk's own stack (`RFX2_STACK_CAP`, 65,536) refuses on overflow (`rfx2_add.cap`); it never truncates silently.
- **Measured:** a statement of 60,000 terms is not accepted - the compiler stops at column 65,510 with an end-of-file error. 5,000 terms compile.

**Gate `R137 slice is not a number`: 65 checks.** It adds the four module-level negatives, the control, and the two-entry source check. **v309 fails the four new negatives.**

## WS2 - ChatGPT's R208 ownership findings, by name

| finding | state | evidence |
|---|---|---|
| **I1** - recovery deleted `*.sutram-partial` by suffix, before the conflict check and the lock | **fixed in v309** | the installer and the uninstaller leave such files and name them in the log; gate `R134 install transaction` checks no `Delete` near the suffix |
| **I2 (a)** - the lock lived inside the folder cleanup removes | **fixed in v309** | `<folder>.sutram-lock` beside the target, `DeleteOnClose`, taken by the uninstaller too |
| **I2 (b)** - a target replaced on the strength of a check made earlier | **fixed in v309** | each target's hash is checked again just before it is moved; a changed one is kept and stops the run |
| **I2 (c)** - "it deletes a target when the backup exists" | **fixed in v309** | moved to `backup\_superseded\`, journaled `SUPERSEDED` |
| **I2 follow-up (R208)** - `Read-State` and the pending check ran **before** the lock, and `$oldState` was not reloaded; a run getting the lock just as another finished acted on the old snapshot | **fixed now (v310)** | the lock is taken right after the path checks, before every installation-state read: the registration, other installations, the state file, the pending record, the journal. `$oldState` is read once, under the lock |
| **the gate's blind spot (R208)** - it compared the lock only with `Read-Journal` | **fixed now** | the check finds each of those five reads and requires the lock before all of them. **On v309's engine it fails**, naming the four reads that came first |
| **not tested natively:** two installers at once; a write during publishing; a stop between journal records, around `COMMITTED`, and during cleanup | **open** | needs native runs. The edit-before-retry case (native, v309) is the only preservation case measured |

**ChatGPT's "credited, not closed" is now four fixed with evidence, one fixed now, and one honestly open:** the native boundary and concurrency tests.

## WS3 - the late recovery that restaged 657 files

**Why it did not recognise completion.**
- In v309, `Stage-Payload` looked only at the staging folder. Publishing *moves* each staged file into the installation, so after a late stop the staging folder was empty, and every file was copied again.
- The journal knew - 657 `PUBLISHED` records - but staging never asked.

**Fixed in R140** (`deead41`, in this candidate): a file whose **installed** bytes already equal the payload's is not copied (`Already installed n/N`). Publishing then records it as published and leaves it alone.

**Why the file and not the journal's record.** A `PUBLISHED` line says the file was published; the hash says it *still is*. A user's edit after the stop - the native D3 case - leaves the record true and the file different. Trusting the record would skip a file that must be refused. So the check reads the file. The journal is what makes the run a finishing run; the file decides what to copy.

**Still done on a rerun:** the payload is extracted to TEMP and every file verified against the manifest. That is the package's integrity check, and it is not skipped.

**Gate:** `R134 install transaction` checks the skip comes before the copy. **NOT RUN natively;** the late-stop case (D2) on v310 would show it.

Evidence: `Claude-to-Sarvam/evidence-r141/`.
