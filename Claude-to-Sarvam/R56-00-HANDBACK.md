# R56-00 — Hand-back to Sarvam: the 20 library names that described the wrong operation

- **Commits on `main`, three, as asked:**
  - `d01059ac` (1/3, v259);
  - `1acb1654` (2/3, v260);
  - `9903e73c` (3/3, v261);
  - then this hand-back's commit.
  - Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v261) - sampurna sutra`.**
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0, after each of the three commits.**
- **Library proofs: 226/226 after each commit. Property proofs: 86/86 after each.**
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb), at `9903e73`: 48 PASS / 0 FAIL / 1 NOT-RUN.**
  - The NOT-RUN is Windows execution.
  - **"keyword packs built in" is green, and so is the R70 corpus, natively** (below).
- **The guard, after EACH commit, against the commit before it: 577 programs, 486 byte-identical, 91 refused
  identically, 0 DIFFER.**
  - Nine runs in all: three commits × Linux ELF, Linux PE, and the Windows compiler under Wine.
  - **A library name never reaches the executable, so 0 DIFFER is what a correct rename must give, and it does.**

## Why each commit is a compiler version

**A rename in `lib/` changes the compiler.** `src/r52_lib_index.inc`, the index behind R52's *"`yoj <module>`"* hint,
is generated from `lib/` and built into the compiler. **So each commit regenerates it, rebuilds both compilers, bumps
the version, and moves the pins.**

**v259 also fixes what I reported after R55.** It is the first binary built since the owner regenerated
`src/r22_lang_builtin.inc` in `c4051f6`. **The committed v258 refused अन्य, अग्रिम, माला and चक्र.** v259 and later accept
them, with output byte-identical to the Latin spelling.

**I also moved the R70 manifest's `lang/sanskrit.lang` pin** to the pack as the owner fixed it. **The R70 corpus now
runs natively on main again: 6 passed, 0 failed.** In R55 it refused, with "source drift".

## WS1 + WS2 — the 20, in the three groups

**The names are the owner's choice, made this session.** I put a table to the owner before renaming. It took
ChatGPT's R129 name in 11 cases and a shorter standard term in 9, and the owner chose that table.
- **All 20 bodies were read first.** Each does what R129 says.
- **Every new name was checked:** it is not a keyword, a builtin, another library function, or a name anywhere in the
  tree.

### Commit 1 (v259): nine with no caller in `examples/`

| Old | New | | Length |
|---|---|---|---|
| `anukram_maap_ashtak` | `anukram_maap_aayam_purva` | R129 | 19 → 24 |
| `anukram_khip_ashtak` | `anukram_khip_aayam_purva` | R129 | 19 → 24 |
| `anukram_grah_ashtak` | `anukram_grah_aayam_purva` | R129 | 19 → 24 |
| `brihat_shesh_tr` | `brihat_shesh_sahaya` | R129 | 15 → 19 |
| `roop_ank_aadhar2` | `roop_ank_aadhar_saral` | R129 | 16 → 21 |
| `roop_varg_mool` | `roop_varg_sahaya` | **mine** | 14 → 16 (R129: 20) |
| `antargam` | `antarveshan` (interpolation) | **mine** | 8 → 11 (R129: 17) |
| `util_chinha` | `ank_chihna` | R129 | 11 → 10 |
| `samanvaya_akar_na` | `samanvaya_akar_ayogya` | R129 | 17 → 21 |

**Strictly by the brief, only three are called by nothing outside their own module:** `brihat_shesh_tr`,
`roop_varg_mool` and `samanvaya_akar_na`. **The other six are also called from `tests/` and `tools/`,** but not from
`examples/`. Their callers were updated in the same commit.

### Commit 2 (v260): nine called from `examples/`

| Old | New | | Length |
|---|---|---|---|
| `asti_vilom` | `asti_viparyay_sam` | R129 | 10 → 17 |
| `mahattam` | `mahattam_samapavartak` (महत्तम समापवर्तक, GCD) | **mine** | 8 → 21 (R129: 23) |
| `laghuttam` | `laghuttam_samapavartya` (लघुत्तम समापवर्त्य, LCM) | **mine** | 9 → 22 (R129: 24) |
| `pravan2` | `dvitiya_pravan` | **mine** | 7 → 14 (R129: 17) |
| `pehchan` | `ekaka_matrika` | R129 | 7 → 13 |
| `nishan` | `karna_yog` | R129 | 6 → 9 |
| `nirnaya2` | `saranik2` (सारणिक, determinant; the digit stays the order) | **mine** | 8 → 8 (R129: 18) |
| `nirnaya3` | `saranik3` | **mine** | 8 → 8 (R129: 18) |
| `bindu` | `bindu_gunan` (dot product) | **mine** | 5 → 11 (R129: 12) |

### Commit 3 (v261): the two worst, last

**Call sites, counted before touching them:**
- **`sadish_yoga`: 1** (`tests/stdlib/samanvaya_sadish_yoga.sm`).
- **library `dviguna`: 5** (2 in `examples/88_pingala_chandas.sm`, 3 in `tests/stdlib/chandas_dviguna.sm`).
- **Neither is near 30.**

| Old | New | | Length |
|---|---|---|---|
| `sadish_yoga` | `adish_gunan` (अदिश गुणन, the scalar product) | **mine** | 11 → 11 (R129: 19) |
| `dviguna` | `dwi_ghat` (2^n; `ganit.ghat` is this library's power) | R129 | 7 → 8 |

**Three tests define their own `prakriya dviguna(n)`, which returns `n * 2`:** `tests/r45`, `r46` and `r53`. **That is
a user function, not the library's, and it is unchanged.**

**Worth knowing:** `ganit.dvigun` (doubling) and `chandas.dviguna` (2^n) were one letter apart and meant different
things. They no longer look alike.

## Names longer than what they replace (your added rule)

**Longer: 16 of the 20. The same length: 3** (`saranik2`, `saranik3`, `adish_gunan`). **Shorter: 1**
(`ank_chihna`).

Of the 16 longer names:
- **10 are R129's own,** kept where I found no shorter exact word. `dwi_ghat` is one of them, one letter longer than
  `dviguna`.
- **6 are mine, and each is shorter than R129's suggestion for the same function:** `mahattam_samapavartak`,
  `laghuttam_samapavartya`, `dvitiya_pravan`, `roop_varg_sahaya`, `antarveshan` and `bindu_gunan`.

The ones longer by the most:
- **`mahattam` and `laghuttam`:** the bare words say only "greatest" and "least". The exact terms are the textbook
  महत्तम समापवर्तक and लघुत्तम समापवर्त्य. **I used them, and they are shorter than R129's coinages.**
  - ChatGPT's R130, which landed during this round, reached the same two terms independently. It found no exact name
    under 15 letters.
- **The anukram three (+5):** I found no shorter name that says "length-prefixed".

**The two names I did not take, and why:**
- **R130's `asti_viloma_sam` (15) instead of `asti_viparyay_sam` (17).**
  - R130 arrived after the owner had approved the table.
  - `asti_viparyay_sam` pairs with `viparyay_ank` in the same module: the test asks *"is n equal to its
    `viparyay_ank`?"*.
  - **It is one string if you prefer R130's.**
- **R129's `antar_gunana` for `bindu`.** I used `bindu_gunan`, which is shorter, keeps the existing prefix, and
  matches the module's own comment, *बिंदु गुणनफल*. **R130 recommends the same name.**

## WS3 — each renamed function is covered by a proof that already exists

**No new tests, as asked.** Each renamed function's existing proofs are below (`evidence-r56/proof-coverage.txt`).

| Function | Proofs that call it |
|---|---|
| `anukram_maap_aayam_purva` | `serial29` + 1 property |
| `anukram_khip_aayam_purva` | `r11_misc_edges`, `r37_bounds`, `serial29` + 4 properties |
| `anukram_grah_aayam_purva` | `r11_misc_edges`, `r37_bounds`, `serial29` + 3 properties |
| `roop_ank_aadhar_saral` | `fmt_int_base`, `fmt_min` + 5 properties |
| `antarveshan` | `util_lerp` |
| `ank_chihna` | `util_sign`, `r18_sign_digits_kramgun` |
| `asti_viparyay_sam` | `num_is_palindrome`, `r8_number_edges` + 2 properties |
| `mahattam_samapavartak` | `math_gcd`, `math_gcd_lcm_edge` + 10 properties |
| `laghuttam_samapavartya` | `math_lcm`, `math_gcd_lcm_edge` + 8 properties |
| `dvitiya_pravan` | `kalana_slope2`, `r11_kalana_edges` + 1 property |
| `ekaka_matrika` | `samanvaya_pehchan` |
| `karna_yog` | `samanvaya_nishan` |
| `saranik2` | `samanvaya_nirnaya2` |
| `saranik3` | `samanvaya_nirnaya3` |
| `bindu_gunan` | `sankhyiki_bindu` |
| `adish_gunan` | `samanvaya_sadish_yoga` |
| `dwi_ghat` | `chandas_dviguna` |

**The three private helpers are covered through the functions that call them:**

| Helper | Called by | Proofs |
|---|---|---|
| `brihat_shesh_sahaya` | `brihat_shesh`, `brihat_ghatmod` | `r11_brihat_guards`, `r11_page_edges`, `bigint_powmod`, `bigint_divzero` |
| `roop_varg_sahaya` | `roop_varg_bharatiya`, `roop_varg_vishwa` | `fmt_group` |
| `samanvaya_akar_ayogya` | `matrika_yoga`, `skalar` | `r37_bounds`, `samanvaya_mat_yoga`, `samanvaya_skalar` |

**The test file names are unchanged,** for example `samanvaya_sadish_yoga.sm`. They are stable identities in the
suite and the guard, and renaming a file would change which programs the guard compares.

## What was renamed, and what was deliberately not

**Renamed, as whole words:**
- the definitions and every call in `lib/`, `examples/` and `tests/`;
- `tools/proof_props.py`;
- the keys of `tools/lib_gap_reviewed.json`. They name `module.function`, and a stale key would silently drop a hand
  verdict;
- **the three live references**, as identifier replacements, not prose (the R47 precedent):
  - `docs/LANGUAGE-REFERENCE.md`;
  - `docs/sutram-stdlib-reference.html`;
  - `docs/sutram-vocabulary.html`. There only the "Becomes" column took the new name, and "Was" keeps the old one.
- **`docs/sutram-stdlib.html`** was regenerated, not edited.

**Not renamed:**
- **`util_chinha` where it is not the function.** An old blind rename of "sign" left `util_chinha` as an ordinary
  **variable** in `lib/madhava`, three examples, `tools/proof_props.py` and one negative-corpus input. It is also a
  **word** on 22 comment lines, for example *"a leading '-' is kept as a util_chinha"* in `lib/roop`.
  - **Only calls, `util_chinha(`, were renamed.**
  - **The variables and comments mean "sign".** Rewriting them is a cleanup for someone, not a rename. They are
    reported here, and their output is unchanged.
- **`tests/negative/`**: pinned inputs, never edited.
- **History:**
  - the CHANGELOG;
  - the vocabulary proposals (`VOCABULARY-*.md`);
  - the books in every language;
  - round-era documents (`NUMERIC-CONTRACT`, `EDGE-COVERAGE-30`, `PROPERTY-NET`, `OVERFLOW-SAFETY`, and others).
  - **They still say the old names.** That is docs prose, not mine.

**One tool repaired: `tools/chakravala_model.py`.** It had crashed since `8071ad5`, where the same blind rename turned
Python's `math.gcd` into `math.mahattam`. **It is `math.gcd` again, and the tool runs.**

## One thing for Muse

**Muse's `ROUND-56-patchA.patch` and `patchB.patch` (the English variables) no longer apply to main.**
- patchA rejects in **2 of its 36 files**, and patchB in **13 of 47** (`evidence-r56/muse-r56-patches-on-main.txt`).
- **They were made at `8236bdd`, and my renames changed the same example lines,** for example
  `bindu(u, v)` → `bindu_gunan(u, v)`.
- **On their own base they apply.** They need regenerating on `9903e73`. **I did not hand-edit them.**

## What I did NOT do, and why

- **No compatibility aliases.** A program outside this tree that calls `mahattam` now gets *agyat prakriya* instead of
  the old name. R130 mentions aliases, and the brief does not ask for them. **It would be one `prakriya` per old name
  if you want a transition period.**
- **No new tests**, as asked.
- **The `util_chinha` variables and comments, and the history documents**, as above.
- **Not run:** real Windows (Wine only).
- **Not touched:**
  - `backups/`, `Windows-to-Sarvam/` and `lang/`;
  - **the frozen packs;**
  - **Muse's patches.**
