# R4-01 — WS1: an undefined name is a compile error

**Commit `33374793` on `claude/round-04`** (draft PR, not on main). Base: main `6ebe973f` (v172).
Condition 3 (stop if it needs restructuring the compiler) **did not trigger**: the change is 280 added lines in
`src/sutram_compiler.asm`, all in the parser. Code generation and `lookup_var` are unchanged.

## What it does now

```
$ ./sutram_compiler pratiyati.sm p.bin            # branch compiler
pratiyati.sm:2:20: Sutram Error [E_UNDEFINED_NAME]: agyat naam 'pratiyati'
      yadi (n > 3) { pratiyati 1 }
                     ^
Sanket: 'pratiyati' purana kunjishabd (v157 se purv); navin: 'prati'
exit=1
```

The same file on v172: `Siddh: 237 byte sankalit`, exit 0, and the program prints **2** (the right answer is 1).
That was the R3 finding. It is now a compile error, at the token, with the line and a caret.

A plain typo gets the general hint:

```
223_undefined_name.sm:5:11: Sutram Error [E_UNDEFINED_NAME]: agyat naam 'totl'
      likha(totl)
            ^
Sanket: prayog se purv ghoshana avashyak: vitti totl = ...
```

`--check` reports up to 8 such errors and then its usual summary line, `Sutram janch: dosh mile; nirgat binary nahi`.
Normal mode stops at the first one, like every other compile error. Full output:
`evidence-r4/logs/ws1-before-after.txt` and `ws1-extra.txt`.

**Condition 2 (Sanskrit):** the message follows the R2 shape. It keeps `Sutram Error [E_…]`, which every
merged message keeps, uses the file:L:C origin from `r51_print_origin`, and puts the hint on a `Sanket:` line.
New words: `agyat naam`, `prayog se purv ghoshana avashyak`, `purana kunjishabd`, `navin`. Please confirm or
replace them (R4-04 §2).

## How it works

- **The parser records every name a function declares, in source order:** each `vitti` (`AST_DECL`, all seven
  places it is built), the `chakra` loop variable, parameters, and the target of a plain assignment. The
  assignment target is recorded *after* its right-hand side is parsed, so `x = x + 1` with no earlier `x` is still
  an error.
- **Each `prakriya` gets its own scope.** That includes a `prakriya` inside a braceless `mukhya`.
- **A read of a name not yet recorded is queued, not reported.** At the end of `parse_program`, a queued
  name that turns out to be a module-level global (`r56_global_index`) is accepted, because globals may be
  declared below the function that uses them. Anything else is reported at its own token.
- **Old keywords get a better hint.** An 11-entry table maps each pre-v157 keyword to the current one
  (`anyatra punaravartana pratiyati uddeshya pankti srijana nishedha ayojan parigrah nishkriya to`), so the hint
  names the new keyword. The table points at the compiler's own `kw_*` strings, so a later rename cannot leave it
  stale.

## Condition 1 — did anything rely on read-as-0?

**No program in the tree did.** Measured with `SUTRAM_COMPILER=<branch build> python3 tests/run_tests.py`:

| Compiler | Suite |
|---|---|
| v172 | FAIL=2 NO-EXPECTATION=4 PASS=189 (the 2 FAIL are the new goldens 222, 223, as they should be) |
| branch | **NO-EXPECTATION=4 PASS=191** (the 4 are the same pre-existing four: 215, 216, 217, 219) |

Also unchanged on the branch:

- `proof_lib` 191/191 (all 24 library modules compile under the check)
- `proof_props` 86/86
- codegen 12/12
- packs 33/33
- R70 corpus 6/6
- `tests/r66` 22, `r68` 19 and `module_graph` 18 OK

No test asserted read-as-0, so **no test was changed for WS1.**

**The new check also found a mistake of mine.** I wrote `phal x * 2 + h` for "return", but `phal` is not a
keyword (`prati` is). v172 compiled it silently and, by luck, printed the same 117. The branch rejects it with
`agyat naam 'phal'` (`ws1-extra.txt`). This is exactly the case the change exists for.

**Forms checked to still compile and give the right answer (117, same as v172):**

- a global declared after the function that uses it
- `a = a + 1`
- loop-variable use
- the same `vitti b` declared in both branches of `yadi … anya`
- a parameter use

## Locks

`tools/r69_build.lock.json`, the `COMPILER_BLOB` constant and `tests/negative/r70/manifest.json` were
re-pinned to the new compiler blob (`ea2a1e91` → `4b137114`), with the reason recorded in the lock's `repinned`
field.

**Five `win/*` inputs needed re-pinning too.** The v171 Windows merge (accepted, mine) had changed or added
`win/rtblob.inc`, `win/winrt.inc`, `win/winrt_blob.asm`, `win/pe_layout.inc` and `win/pe_imports.inc`
without re-pinning them, so `r69_build --check-only` refused main before my change. This is the third
acceptance without a re-pin; see R4-04 §1.

```
$ python3 tools/r69_build.py --check-only            → "status": "SOURCE_PINS_CHECKED", exit 0
$ python3 tools/r70_negative_corpus.py --compiler <branch> --report r70.json → passed 6, failed 0, native_status PASS
```

## Windows

The Windows compiler cross-builds from the branch:

```
nasm -f win64 -DWINDOWS=1 -I. src/r68_compiler_entry.asm
ld -mi386pep --subsystem console --entry=_start
```

**Under Wine** it gives the same diagnostic and exit 1, and compiles and runs the valid program (117)
(`evidence-r4/logs/ws1-wine.txt`). The IDE shows it too: `evidence-r4/screens/ide-after-run-222.png` is
`udaharan khol` → 222 → `chal`, under Wine.

## What I did not do, and what I could not verify

- **NOT-RUN on native Windows.** Wine only.
- **No new error for a call to an undefined function.** That already had its own error (`r48`). I did not
  touch it.
- **Capacity, not exercised.** The tables hold 8192 declared names and 256 pending reads per program.
  - Past 256 pending reads, the extra reads go unchecked, i.e. the old behaviour.
  - Past 8192 declarations, later declarations are not recorded, so a later read of one of them would be
    reported falsely.
  - Neither limit is reached by anything in the tree (the largest program declares far fewer). I did not
    build a program at the limit.
- **Undeclared assignment is still allowed.** Assigning to a never-declared name (`y = 5` with no `vitti y`)
  still declares it. The brief asked about *reads*. Whether bare assignment should need `vitti` is a separate
  language decision; I did not make it.
- **I did not commit a rebuilt `sutram_compiler`.** The tracked binary is now stale against `src/`; please
  rebuild it at merge, as in R2/R3.
- **Observation, not changed:** the compiler has no `-o` flag. `sutram_compiler f.sm -o x` silently wrote a
  binary named `-o` into the working directory, which I found and deleted. A one-line usage check would catch
  this.
