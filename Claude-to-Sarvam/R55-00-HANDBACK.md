# R55-00 — Hand-back to Sarvam: the last two patches, and the reference

- **Commit on `main`:** `fac7b1b21d4cdc34c5c8a76ae5c97a1da58ea163`, then this hand-back's commit. Pushed with git, not `--force`.
  **No compiler change this round.**
- **Compiler: `Sutram 1.0 (v258) - sampurna sutra`,** the R54 build. The committed binaries are byte-identical to it.
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** Library proofs: **226/226**.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 47 PASS / 2 FAIL / 1 NOT-RUN.**
  - **Both FAILs come from the owner's pack commits `e1fd04b` and `7fb43c6`, not from this round,** and they fail the
    same way on main before it. I reported this in R54.
    - **"keyword packs built in":** `src/r22_lang_builtin.inc` was not regenerated after `lang/sanskrit.lang` changed.
    - **"doc counts":** it fails because of the first. PROJECT-MASTER quotes 48 PASS, and only 47 pass while that gate
      fails. **I did not lower the number to 47:** that would make a broken gate look like the normal count.
  - **The NOT-RUN is Windows execution.**
- **The guard: the tree before this round against the tree after it, the same v258 compiler: 577 programs, 486
  byte-identical, 91 refused identically, 0 DIFFER.**
  - It held on all three paths: Linux ELF, Linux PE, and the Windows compiler under Wine.
  - **Every rewritten test program compiles to the same bytes as before.**

## WS1 — Muse's two patches

**Applied with `git apply`, 0 rejected hunks, nothing edited by hand** (`evidence-r55/patches-applied.txt`):

| Patch | Files |
|---|---|
| `ROUND-54-tests.patch` | 57 |
| `ROUND-54-docs.patch` | 16 |

**Did any negative test's expected output change? NO.** (`evidence-r55/rename-check.txt`)
- **No file under `tests/negative/` was touched,** and no `.out`, `.exit` or `.err` anywhere.
  - **`tests/negative/` still holds 108 `prati`**, all as input: the alias is still fed to the compiler.
- **The patches change 233 lines in 73 files. Every one is a plain `prati` → `nivartanam`, except two:**
  - **the Devanagari column of the reference's pack row,** प्रतियाति → निवर्तनम्, where the old word was already wrong;
  - **the Devanagari column of the vocabulary page,** प्रति → निवर्तनम्.
  - **In the reference row, the 10 frozen-pack columns are unchanged, byte for byte.**
- **The one test that checks an error message containing `prati` was left as it is.** That is
  `tests/r25/test_phal.py`, checking `phal-prakriya: prati siddhi va dosh bhavet`. The compiler still prints that
  message, so the test still passes.
- **The alias tests still use `prati` as their input:**
  - r53 (`prati` against `nivartanam`, 13);
  - r43 (the keyword boundary, 6);
  - r50 (`प्रति`, 3).

**The negative corpus (R70): 6 passed, 0 failed, but only in a scratch copy** (`evidence-r55/r70-negative-corpus-pinned-lang.json`).
- **On main it refuses to run:** `source drift: lang/sanskrit.lang`. Its pin was set before the owner's pack commits.
  - The same refusal happens on the tree before this round (`evidence-r55/r70-negative-corpus-as-is.json`).
- **The scratch copy holds this round's tests with the pinned `lang/sanskrit.lang` put back.** That changes nothing
  the compiler sees: it uses the built-in copy and does not read the `.lang` file.
- **The R70 unit tests pass on main.**

## WS2 — R127 and R128: what form they came in, and what I applied

**Both came as exact-insertion TSV, with four columns.** **So I applied them as given, by a script that
replaces or inserts only where the anchor line occurs exactly once.** Each row's result is in
`evidence-r55/tsv-r127-rows.txt` and `tsv-r128-rows.txt`.

**Before inserting anything, I ran every program the two documents quote** (`evidence-r55/reference-programs-run.txt`):
- **All 9 print exactly what the documents say:** 42; `x = 42`; `x = 42, y = 7`; the raw write `raw`; `2.500000|`;
  `likha_fmt` giving `x = 42`; both loop forms giving 0 to 4; and `nivartanam a + b` giving 5.
- **The claims made in prose also hold:**
  - `likha` of a string variable prints its address (4194454), while `shabda(s)` prints `abc`;
  - `arabhya` without `paryantam` is refused;
  - `likha_fmt` does not substitute `{0}`;
  - `format_demo`'s golden does carry the blank lines.
- **The source line numbers cited are still right at v258.** R54 changed lines without adding any.

**R127, all 6 rows applied:**
- the three replaced table rows (`likha`, `lkhb`, `likha_fmt`);
- **§4a "Output"**, 81 lines, before §4b;
- **§6a "Counted loops"** and **§6b "Is Sutram speakable Sanskrit?"**, 36 lines, before §7.

**R128 has 33 single-line rows and one block. 31 of the rows were already done by Muse's docs patch:**
- **29 of the 31 give the same line Muse produced.**
- **Two differ:**
  - **the vocabulary row:** R128 keeps प्रति in the Devanagari column. Muse's निवर्तनम् is correct, and stays.
  - **WHATS-LEFT F4:** that file was rewritten in `22b22c1` and already says it.
- **Applied, 3 rows:**
  - README and PROJECT-OVERVIEW: the keyword table now says `nivartanam`.
  - **The reference's keyword row, R128's wording:**
    `` | `nivartanam` (निवर्तनम्; legacy alias: `prati`) | return / returning / turning back (नि + √वृत्) | ``
  - **This is the one place I went beyond exact anchors.** Its anchor `` | `prati` | return | `` was gone, because Muse
    had already made it `` | `nivartanam` | return | ``. I replaced Muse's line with R128's, because R128's names the
    alias, which the brief lists as critical.

**NOT applied: R128's 21-line block before §3, "Return keyword — `nivartanam`". It no longer tells the truth.**
- It says **"implementation pending exact-head verification"**.
- It says **"After the canonical keyword … have been integrated and verified"**.
- It says **"NOT RUN - no toolchain"**.
- It says **"For a presently supported equivalent, use `prati a + b`"**.

**All four are false at v258.** The keyword landed in R53, and its example compiles and prints `5`, measured. The
form is fine. **It is the content that is stale, so I report it rather than edit ChatGPT's prose.** The derivation
paragraph (नि + √वृत्) and the example are correct as they stand, if you want them with the stale sentences removed.

**Your five critical points, against the reference as it now stands:**

| Your point | What the reference now says |
|---|---|
| `likha("x = ", x)` works and no example uses it | **The reference shows it, with its exact output.** **But "no example uses it" is no longer true:** after the R52 patch, **102 calls in 36 examples** use it (counted). R127 says so too. |
| `likha(fd, buf, len)` is the raw write | **Said**, and **"Do not assume all three-argument `likha` calls print three values"** |
| `lkhb(x)` on a `dasham` prints raw bits until R52's fix | **R52's fix has landed** (v257). **The reference says `lkhb(2.5)` prints `2.500000`**, measured. |
| `chakra i = 0 tak 10 { }`, and `tak` is Hindi/Urdu | **Said** in §6a, beside `arabhya … paryantam` |
| `nivartanam` the keyword, `prati` the alias | **Said** in the keyword row |

**One label in R127's heading is a version behind: "(compiler v257)".** Every statement under it holds at v258. I left
the heading as written.

## WS3 — the numbers

**From the first lines:** suite 225, proofs 226/226, crash corpus 227/0, the guard 0 DIFFER on three paths.

**`prati` remaining** (`evidence-r55/prati-count.txt`, whole word, git-tracked files):

| Area | Before | After | What is left |
|---|---|---|---|
| `lib/` | 0 | 0 | |
| `examples/` | 1 | 1 | the comment in `examples/256` |
| `tests/negative/` | 108 | 108 | inputs, pinned by SHA-256 and the manifest |
| the rest of `tests/` | 213 | 33 | the alias tests, one error message, pack snapshots, 2 comments, and the R54 test's own text |
| `docs/` | 157 | 66 | CHANGELOG 50, four vocabulary and lexer records, SPECIFICATION's `प॰` row, the alias in the keyword row, WHATS-LEFT 1 |
| README + PROJECT-OVERVIEW | 2 | 0 | |

## What I did NOT do, and why

- **I did not regenerate `src/r22_lang_builtin.inc`.** So the two gates stay failing, and the R70 pin stays drifted.
  It is a compiler change (v259: re-pin and the guard), and the R70 manifest's `lang/sanskrit.lang` pin needs moving
  with it. **No round has asked for it.** I said so in R54 and say it again.
- **I did not apply R128's §3 block** (above), **nor rewrite its stale sentences.**
- **I did not fix `tests/r66/test_prepare_review.py`.** It expects 57 pack rows, and the pack has more. Muse reported
  it, and it fails the same way before this round. It is not a gate.
- **Not run:**
  - **real Windows** (Wine only);
  - **the native R70 run on main,** because of the pin drift (the scratch-copy run is above).
- **Not touched:**
  - `backups/`, `Windows-to-Sarvam/`, `lang/`, `src/`, `lib/` and the compiler;
  - **the frozen packs' columns.**
