# R57-00 — Hand-back to Sarvam: Patch A stopped at two hunks; the 33 comments applied

- **Commit on `main`:** `d0ff986` (the comments), then this hand-back's commit. Pushed with git, not `--force`.
  **No compiler change this round.**
- **Compiler: `Sutram 1.0 (v261) - sampurna sutra`.** The committed binary is byte-identical to the R56 build.
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** Library proofs: **226/226**. Property proofs: **86/86**.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 48 PASS / 0 FAIL / 1 NOT-RUN.**
  - The NOT-RUN is Windows execution.
- **The guard, the tree before the comments against the tree after, the same v261 compiler: 577 programs, 486
  byte-identical, 91 refused identically, 0 DIFFER.**
  - It held on all three paths: Linux ELF, Linux PE, and the Windows compiler under Wine.
  - **The comments did not break a parse.**

## WS1 — Patch A: STOPPED, as you said. Two hunks reject.

**`git apply --check Muse-to-Sarvam/ROUND-56-patchA.patch` rejects 2 of its 36 files.** Nothing was applied, and
nothing was edited by hand (`evidence-r57/patchA-check.txt`).

| File | Hunk | Why it no longer matches |
|---|---|---|
| `examples/126_numeric_pipeline.sm` | the 2nd, `@@ -28,13` | its context line `likha(bindu(u, v))` is now `likha(bindu_gunan(u, v))` |
| `examples/208_kalana.sm` | the 1st, `@@ -7,24` | it rewrites `likha(pravan2(xs, ys, 5))`, and that line now says `dvitiya_pravan` |

- **Both are my R56 renames of library functions.** Muse made the patch at `8236bdd`, before them.
- **On that base it applies cleanly.**
- **The fix is Muse regenerating Patch A on current main.** The two hunks only need the new function names in their
  context. **Every other change in them is a variable, and those still stand.**
- I did not do it myself: your rule was STOP, and a hand edit around a rejected hunk is what R54 forbade.

**So the guard and suite numbers above are for the comments alone. Patch A has not been measured on main.**

**Muse's question: after this, does a beginner reading `examples/01_hello.sm` still meet an English word? Yes, in that
very file:**
- **Line 1 is the comment `# Sutram - Hello World`.**
- **It has no variables,** so no English variable name, with or without Patch A.
- **Its output string, `"Namaste, Sutram!"`, is not English.**
- **Muse's own report agrees:** the English variables were never in `01`–`09`, and comments and output strings
  across the examples are still English. That is a different round.

## WS2 — the 33 comments: 1 inserted, 11 reconciled, 21 already adequate

**I checked each of the 33 against two things:** the comment already above its `prakriya`, and the body. The
verdict for each is in `evidence-r57/comments-33.tsv`.

**Inserted, 1:** `varna_maap`. It had no comment of its own; the block above it is the file header. It now says the
length is in BYTES, so a multi-byte UTF-8 letter counts as several.

**Reconciled, 11.** In each, the existing comment took the missing fact. **Nothing was stacked.**

| Function | What the existing comment lacked |
|---|---|
| `brihat_ank_se_laghu` | that the sign is not stored (the digits are of \|val\|) |
| `fnv1a` | non-cryptographic: not encryption, not a secure digest |
| `ganit_yadricch` | not secure randomness |
| `pravan` | that zero x-spacing returns 0.0. This was only in the body. |
| `bahu_mula` | nothing new; **"Requires a util_chinha change" put back to "a sign change"** (the old blind rename I reported in R56) |
| `khand_chhid` | that tabs, newlines and multi-byte spaces are kept |
| `roop_varg` | the pointer to `roop_varg_vishwa` for international grouping |
| `bhaj_urdhva` | that its 0 for `b == 0` cannot be told from a real quotient of 0 |
| `avali_pravesh` | that a full queue doubles and copies, so that one append is not O(1) |
| `gan_swar` | ASCII only: uppercase and Devanagari vowels are not counted |
| `varna_tak_dashm` | **its comment was WRONG.** It said "from a byte string", but the body reads `src[p]`, one code per cell. Its callers fill `buf[i]`, and the sibling `varna_tak_ank` says "character codes of mala buf". **Corrected.** |

**Already adequate, 21.** The existing comment states the same contract, often in more detail than the proposed line:
- `brihat_ank_tak_laghu`, `brihat_bhajshesh`, `brihat_shesh`;
- `ganita_paripurna_bhaj`, `_shesh`, `_nirapeksh`;
- `ghat`, `simpson`;
- `nighantu_grah`, `nighantu_vardh`, `nighantu_kunjika`, `nighantu_kunjika_ashtak`;
- `patra_asti`, `phal_mulya`, `roop_sthir_mool`, `purna_prasaran`, `asti_sorted`, `rakh_tak_mala`;
- `chay_apanay`, `avali_nishkas`, `suchi_rikta`.

**None of R130's 33 lines was inserted verbatim.** Where a comment existed, its own wording was kept and extended.
**I checked every fact I added against the body.**

`docs/sutram-stdlib.html` was regenerated from the new comments.

## WS3 — `sadish_yoga`

**R130's verdict: "FAIL as a public operation name; not defensible as a precise identifier for dot product."**
- `yoga` can mean a summation, and a dot product contains one. But **सदिश योग** is the vector sum, and the body
  returns one scalar, `sum(u[i] * v[i])`.
- **The rename stands.** It landed in R56: **`sadish_yoga` → `adish_gunan`** (अदिश गुणन, the scalar product), at v261.

**The changelog line I propose** (the CHANGELOG is yours):

> **`sadish_yoga` renamed `adish_gunan` (R56, v261).** It never added vectors: it returns their scalar (dot) product.
> ChatGPT's R130 was asked whether any reading makes the old name right, and found none. *Sadish yoga* is the vector
> sum. 1 call site was updated.

## Anything surprising

1. **One of the 33 comments was wrong, not just thin:** `varna_tak_dashm` said "byte string" on a function that reads
   cells. A caller following it would pass a packed string and get `ok = 0`.
2. **Patch A broke on my own renames from an hour earlier.** Muse's patches and mine were made against different
   heads. **Any patch made before `9903e73` that touches a call to one of the 20 renamed functions will need
   regenerating.**
3. **`util_chinha` (meaning "sign") is still a word on about 20 comment lines and a variable in `lib/madhava` and
   three examples.** One, in `bahu_mula`, was fixed here because its comment was in scope. The rest are as reported
   in R56.

## What I did NOT do, and why

- **Patch A:** STOPPED at the reject, as above.
- **Patch B:** skipped, as you said.
- **No verbatim stacking** of R130's lines over the existing comments.
- **Not run:** real Windows (Wine only).
- **Not touched:**
  - `backups/`, `Windows-to-Sarvam/`, `lang/` and the compiler;
  - **the frozen packs;**
  - **Muse's patches.**
