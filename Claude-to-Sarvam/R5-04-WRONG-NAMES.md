# R5-04 — WS4: the undefined-name change, extended

## 1. Did any program in the tree rely on the old behaviour?

**No program that is run or tested relied on it.** One sample doc and one reference page did, and the pages
are the bigger story (§1.2).

### 1.1 Every `.sm` file in the tree: 510 files

**What I ran.** I compiled each `.sm` with `--check`, first with the v172 compiler (read-as-0) and then with
the branch. Each file was compiled from the repo root, and again from its own folder when the root failed.
Programs that need a pack were retried with every `--lang`. The R71 profile examples were built with
`-DSUTRAM_R71_UNSAFE_BOUNDARY=1`.

| v172 → branch | Files | What they are |
|---|---|---|
| OK → OK | 430 | unchanged |
| FAIL → FAIL | 76 | negative tests, error goldens, module-error fixtures, and pack programs run without their pack. All 13 pack programs compile on both compilers with their `--lang`; the R71 examples compile with the R71 profile (`boundary_bad` fails as intended). |
| OK → **E_UNDEFINED_NAME** | 3 | `222`, `223`: the R4 goldens, meant to fail. `tests/negative/r70/cases/misplaced_keyword.sm`: it only compiled without its pack; the corpus runs it with `--lang sanskrit` and expects `E_ABBREVIATION_VALUE`, which still holds (R70 6/6). |
| FAIL → FAIL, now also showing E_UNDEFINED_NAME | 1 | `examples/r71/boundary_good.sm` without the R71 profile. With the profile it compiles. |

**Result: zero programs changed. No program was edited for WS4.**

The extensions in §3 were checked the same way, branch-before against branch-after: 430 / 76 / 4. Same
result, no file changes status.

### 1.2 Code samples in the documents: 70 unique blocks, from 23 `.md` / `.html` / `.txt` files

**Two samples relied on read-as-0.** v172 compiled them only because a wrong name read as 0.

1. **`docs/R56-MODULE-GLOBALS.md:13`** used `pratiyati counter`, the pre-v157 return.
   - **Changed** to `prati counter` (commit `a7e48882`).
   - It now prints the documented `5 / 6 / 0`. Prose mentions of old names are left alone, by the standing
     rule.
   - `ChatGPT-to-Sarvam/ROUND-55-HANDOFF.md` has the same `pratiyati`. It is a historical handoff, so I left
     it.
2. **`docs/sutram-stdlib-reference.html`, which is the bigger find:**
   - **All 26 of its samples use `samapt`,** styled as a keyword, to close `mukhya` or a block.
     **`samapt` is not a keyword and never was.**
   - **12 of the 26 compiled on v172 only because `samapt` was read as an undefined name (0).** Since R4
     each one stops at `agyat naam 'samapt'`. Deleting the `samapt` lines makes 12 samples compile and
     print their commented values (e.g. `6 / 12 / 120`).
   - **The other 14 do not compile even on v172,** for reasons unrelated to R4:
     - `;` used as a comment
     - braceless `yadi … samapt` blocks
     - prose inside the code, e.g. `shabd 'weight'`, `'own'`, `'only'`
     - names used before declaration
   - **The page teaches a syntax that is not Sutram.** I **did not change it.** It is your page, and fixing
     it is a rewrite of 26 examples, not a word swap.
   - **Ask:** shall I rewrite all 26 next round, each compiled and its output checked?

The other 20 blocks that fail on both compilers are pre-existing; R3-03 listed most of them.

## 2. Plainly: are there other places where a wrong name silently succeeds?

**Yes. After R4 there were five; this round closes three of them and reports two.** All were probed on the
branch compiler (Linux). The probe programs are in `evidence-r5/probes/`.

| # | Program | Before R5 | After R5 | Silent wrong answer? |
|---|---|---|---|---|
| 1 | `likha(zz[0])`, with `zz` never declared | compiles, **segfaults at run time** | **E_UNDEFINED_NAME 'zz'** | it crashed with no diagnostic. **Closed.** |
| 2 | `a[0] = 1`, undeclared `a` | compiles, **segfaults** | **E_UNDEFINED_NAME 'a'** | **Closed.** |
| 3 | `p.w` where no `rachana` has a field `w` | compiles, **reads field offset 0**: printed `10` (the value of `p.x`) | **E_UNKNOWN_FIELD 'w'** | **yes, a wrong answer. Closed.** `p.q = 5` likewise wrote into `p.x`. |
| 3b | `n.x` on a plain number (no rachana anywhere) | compiles, segfaults | E_UNKNOWN_FIELD | **Closed.** |
| 4 | Fields `position_x` and `position_y` | **only the first 8 bytes were compared** ("more than 8 chars - assume match"), so they were one field: printed `2 2` | compared in full: prints `1 2` | **yes, a wrong answer. Closed.** |
| 5 | `totl = 10` (typo for `total`), then `likha(total)` | compiles, prints **3** | **unchanged**: still compiles, prints 3 | **yes, open.** A bare assignment declares a new variable. Making assignment need `vitti` is a language decision (R4-04 §8, still yours). |
| 6 | `yadi (c == 1) { vitti b = 7 }` then `likha(b)` outside the branch | compiles, prints **0** | **unchanged** | **yes, open.** Names are function-scoped, not block-scoped. Block scope would be a language change. |
| 7 | A global initializer reading a later global (`vitti a = b + 1` / `vitti b = 5`) | `a` = 1 | unchanged | documented behaviour (R56: "sees its default zero"). Not a wrong name. |

**Already errors, checked and unchanged:**

- `k += 2` / `j++` on an undeclared name
- a keyword typo used as a statement (`agrm`)
- an argument name (`f(y)`)
- a local of another function
- an undefined function, including a misspelled library function (`mahatam` → `agyat prakriya`)
- an undeclared global

### What changed in the compiler — commit `f1025a72`

**The bases of `a[i]` and `p.f` are now checked.** They go through the same `r4_check_read` as a bare read.
R4 had hooked only bare reads, which was a gap in my own R4.

**An unknown field is now a compile error.** It is reported at the field, with the source line and a caret:

```
224_unknown_field.sm:7:13: Sutram Error [E_UNKNOWN_FIELD]: agyat kshetra 'w'
      likha(p.w)
              ^
Sanket: 'w' kisi rachana ka kshetra nahi
```

New words: `agyat kshetra`, `kisi rachana ka kshetra nahi`. Please confirm them along with R4's.

**Field names are compared in full.** The eight unrolled byte compares are replaced by `strcmp`.

**Nothing was restructured.** Field resolution is still the same global search over all `rachana`, and code
generation is unchanged.

**New goldens.** All three FAIL on v173 and PASS on the branch:

- `224_unknown_field` (error)
- `225_undeclared_array` (error)
- `226_long_field_names` (prints `1`, `2`)

**Tests.**

- Suite **194 / 4**
- proof_lib 191/191
- proof_props 86/86
- codegen 12/12
- packs 33/33
- R70 6/6
- Under Wine, `sutram.exe` gives the same output and exit codes (`evidence-r5/logs/ws4-wine.txt`).

**Locks, re-pinned with the reason recorded.** The compiler blob went from `4b137114` to `185b7f06` in:

- `tools/r69_build.lock.json`
- `COMPILER_BLOB` in `tools/r69_build.py`
- `tests/negative/r70/manifest.json`
- `docs/BUILDING.md`
- `docs/NEGATIVE-CORPUS.md`

`r69_build --check-only` → `SOURCE_PINS_CHECKED`; `--output` → `BUILT_FORMAT_CHECKED`.

**Coordination point, read this before ChatGPT's ROUND-73 WS1.**

- ChatGPT's "four mismatching pins" (`docs/R72-BASELINE-OBSERVED.md`) were measured on **v172**.
- My R4 re-pin, merged in v173, already set three of them to exactly the blobs ChatGPT recorded as current:
  `win/rtblob.inc f855c01e`, `win/winrt.inc 9e73bd45` and `win/winrt_blob.asm 69a46180`.
- It set the compiler to the R4 build. **On main v173, `r69_build --check-only` already prints
  `SOURCE_PINS_CHECKED`. I ran it on a clean worktree of `c504e3c6`.**
- So ChatGPT's WS1 blocker no longer exists on main.
- **This branch moves the compiler pin once more.** If ChatGPT re-pins in parallel, one of us will be
  stale. Please merge one before the other.

## 3. Not done / not verified

- **#5 and #6 above are open.** Both are language decisions.
- **The stdlib reference page is not rewritten** (§1.2).
- **`--check` stops at the first unknown field,** like other parse errors. Only undefined *names* are
  collected (up to 8).
- **A field of a `rachana` declared *after* its use is now an error.** Before, it silently read offset 0.
  Nothing in the tree does this.
- **NOT-RUN on Windows.** Wine only.
