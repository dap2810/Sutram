# ROUND-03 / WS1 — the stale source locks

**Date:** 2026-10-19 · **Base:** main `85d6c5f` (v169) · **Code:** branch `claude/round-03`, commit `2182583`

---

## 1. What I did

1. Listed **every** artefact in the tree that pins a Git blob or a SHA-256 and refuses on mismatch. There
   are five lock families, not two: R65/R66/R67/R68 staging tools, the R69 build lock, the R70 negative
   corpus, the R69 pair-probe fixtures, and the R71 extension lock.
2. For each pin I computed the current blob and searched the history for when the pinned blob was last
   true (`git log --find-object`).
3. Ran each tool and each round test directory on main and recorded the result.
4. Decided per family: **re-pin** where the lock is a *build-input or corpus contract* whose meaning holds
   after re-pinning; **retire** where the lock proves *provenance of a one-time staging step* that is
   finished; **leave alone** where the lock records an *open review* that belongs to someone else.
5. For every re-pin I checked first that the drift was what I thought it was: the keyword rename, or a
   deliberate ROUND-02 change. I diffed the pinned fixture version against the current one.

## 2. What the locks pinned, and why they stopped matching

```sh
python3 - <<'EOF'   # for every pin in the three lock files: current blob + when the pin was last true
...git hash-object <path>; git log --find-object=<pin> -- <path>...
EOF
```
```
STALE src/sutram_compiler.asm   pin=64ea028a cur=587567ce   last true: d8a9e00 (10-15, R67) .. 0982150 (10-17, "rename")
STALE src/r66_indic_lexer.inc   pin=3633bd55 cur=998b6cb7   last true: c4d28b8 (10-15, R68) .. bc5244f (10-18, ROUND-02 merge)
STALE src/r68_diagnostics.inc   pin=4e2ec29f cur=a6f7bb19   last true: 8a7c7f0 (10-15, R68) .. 0d373b3 (10-18, ROUND-02 merge)
MATCH src/r67_stack_pair.inc, src/r68_unicode_helpers.inc, src/r68_compiler_entry.asm, src/r71_*, win/* (6 files)
```
The compiler pin has been false since the v157 keyword rename (17 Oct). The two `.inc` pins became false
when Sarvam merged my ROUND-02 Sanskrit strings (18 Oct). **Nobody re-pinned at either acceptance**, so
every tool that checks these pins has refused main since then.

## 3. On main before this round — PASS / FAIL / NOT-RUN

| Tool / test | Result on `85d6c5f` |
|---|---|
| `tools/r69_build.py --check-only` | **FAIL** `R69_BUILD_REFUSED: input drift: src/sutram_compiler.asm: expected 64ea028a…, got 587567ce…` |
| `tools/r68_prepare_review.py --output …` | **FAIL** `R68_PREPARE_REFUSED: input drift: … expected 64ea028a…` |
| `tools/r71_prepare_review.py --output …` | **FAIL** `R71_PREPARE_REFUSED: unreviewed core lock` |
| `tools/r65_prepare_review.py --output …` | **FAIL** `source drift: expected Git blob a14172c1…` |
| `tools/r66_prepare_review.py …` | **FAIL** `missing src/r66_indic_lexer.vardh` (the `.inc`→`.vardh` rename damage, again) |
| `tools/r67_prepare_compiler.py …` | **FAIL** `compiler source drift: required Git blob caee7373…` |
| `tools/r70_negative_corpus.py` | **FAIL** `NOT_ACCEPTED: fixture drift: bad_type` |
| `tests/r68` | 9 run: 4 FAIL, 1 ERROR (setUpClass), 15 helper tests **NOT-RUN** behind the error |
| `tests/r69` | 39 run: 1 ERROR (`fixture drift: all_registers.sm`) |
| `tests/r66` | 2 FAIL (one stale pack snapshot, one stale digit expectation — see §5.4) |
| `tests/r67` | 1 FAIL (stale pack snapshot) |
| `tests/r71` | 66 run: 1 ERROR (`unreviewed core lock`) |
| `tests/r65_finish` | 18 OK (fixtures only; the tool it tests cannot run on any real input) |

## 4. The decisions, and the reasons for them

### 4.1 `tools/r69_build.lock.json` + `tools/r69_build.py` — **RE-PINNED**

**What it proves:** "this build used exactly the accepted inputs, and no include is unpinned."
`docs/BUILDING.md` calls it "the replacement build-input contract". It is a gate on *inputs*, not a
record of who reviewed what. Pointing it at the newly accepted inputs keeps that meaning. Leaving it
stale makes it a gate that always fails, and that teaches people to bypass it. That is worse than no
gate.

**What I changed:** the three stale pins now hold the blobs on this branch. Those are v169 plus the
one-function compiler fix in §6. I also changed:
- `base_commit` → `85d6c5f…` (v169)
- added `previous_base_commit: 11f41d3…`
- added a `repinned` note saying who re-pinned, when, and the rule "re-pin only when Sarvam accepts a
  change to a pinned file"
- the duplicate constant `COMPILER_BLOB` in `r69_build.py`, which must match the lock by design, with
  a comment giving the old value

```
$ python3 tools/r69_build.py --check-only            → "status": "SOURCE_PINS_CHECKED", exit 0
$ python3 tools/r69_build.py --target linux --output r69_built --report r69.json
                                                      → "status": "BUILT_FORMAT_CHECKED", exit 0
$ objcopy --strip-all r69_built a; objcopy --strip-all <manual nasm/ld build> b; cmp a b
IDENTICAL after strip (only symbol/file metadata differs)
```
The two unstripped binaries differ by 24 bytes because `r69_build.py` passes absolute paths to NASM:
`strings` shows `/home/claude/sutram/src/r68_compiler_entry.asm` vs `src/r68_compiler_entry.asm`. A manual
build with the same absolute paths is byte-identical to `r69_build`'s output.

**If you merge this branch without §6's compiler change**, the compiler pin must be `587567ce…` (v169),
not `ea2a1e91…`. **If you merge it as is**, the pins are correct.

**Not mine to fix — `windows/r69-build-common.ps1:45`** hardcodes the old pin a third time
(`$lock.pins.'src/sutram_compiler.asm' -ne '64ea028a…'`) and throws `Unknown compiler/entry contract`.
The Windows builder refused main before this change and still refuses it. **ChatGPT needs to change that
one line** to `ea2a1e91…`, or better, read it from the lock. I did not touch `windows/`.

### 4.2 `tests/negative/r70/manifest.json` — **RE-PINNED, and now runs**

**What it proves:** six rejection categories each produce exit 1 and the stated diagnostic. That is a
behaviour corpus, and it is the only negative-test gate covering six categories. The source pins record
which compiler the expectations were taken from. Re-pinning them after re-taking the expectations keeps
that meaning.

**Checked before re-pinning:** the two drifted fixtures changed *only* by the v157 rename.
```
$ git diff 3fddeee 9caac6c -- tests/negative/r70/cases/bad_type.sm
-    pratiyati a[0]
+    prati a[0]
$ git diff c89938d ad5ea60 -- tests/negative/r70/cases/bad_arity.sm
-prakriya six(a, b, c, d, e, f) { pratiyati a }
+prakriya six(a, b, c, d, e, f) { prati a }
```
**Changed:** 4 source pins → this branch's blobs; 2 fixture digests; the 6 expected diagnostics, each
moved to the ROUND-02 Sanskrit text the compiler now prints. That behaviour was changed deliberately in
ROUND-02 WS4. I added a `repinned` field saying so. `snapshot` and per-case `provenance` are left as the
original R70 record.

| Case | Was expected | Now expected |
|---|---|---|
| bad_type | `Sutram Error: kosh parameter requires matching kosh element type` | `Sutram Error: kosh tark: tatv prakar bhinn` |
| bad_arity | `parse error at line ` … `Hint: functions accept at most 6 arguments.` | `vyakaran dosh, pankti ` … `Sanket: prakriya adhiktam 6 tark lete hain.` |
| unknown_identifier | `Sutram Error: undefined function: does_not_exist` | `Sutram Error: agyat prakriya: does_not_exist` |
| malformed_literal | `…{source}:2: invalid or truncated UTF-8 in source code` | `…{source}:2: srot me ashuddh ya khandit UTF-8` |
| unterminated_string | `parse error at line ` / `end of file` / `Hint: check the keyword…` | `vyakaran dosh, pankti ` / `patra-ant` / `Sanket: is sthan par shabd aur vyakaran dekho.` |
| misplaced_keyword | `Language pack loaded: sanskrit` + `abbreviation keyword is not a value: 'वि॰'` | `Bhasha pak prapt: sanskrit` + `sankshep shabd mulya nahi: 'वि॰'` |

```
$ python3 tools/r70_negative_corpus.py --compiler <branch compiler> --report r70.json
  "passed": 6,
  "failed": 0,
  "native_status": "PASS"
```
**R70 corpus: 6 PASS / 0 FAIL.** On main it could not start.

### 4.3 `tests/r69/pairs/manifest.json` — **RE-PINNED**

Three fixture digests. I checked each diff against the rename map. For all three, the only change is
`nishkriya` → `yantra`. `tools/r69_pair_probe.py` already looks for `yantra(` (it was renamed),
so the digests were the only stale part. `tests/r69`: **39 run, 39 OK** (was 1 ERROR).

### 4.4 The R65 / R66 / R67 / R68 staging tools — **RETIRED**

`r65_prepare_review.py`, `r66_prepare_review.py`, `r67_prepare_compiler.py`, `r68_prepare_review.py` +
`r68_review.lock.json`. Each one *stages a one-time patch onto one specific compiler blob* and refuses
any other blob. That is its whole purpose. Each round has been integrated on main, so each target
blob is gone (R65's since R66, R68's since v157). Re-pinning would make the tool apply a finished patch
to a source that already contains it. **Re-pinning would not restore a use. It would remove the refusal
that makes the tool honest.** So I deleted them, not re-pinned them. Git history keeps them:
`git show 85d6c5f:tools/r68_prepare_review.py`.

Two of them were broken twice over: `r66_prepare_review.py` requires `src/r66_indic_lexer.vardh` and
embeds assembly with **`vardh r13` / `vardh ecx` where the x86 instruction `inc` was renamed**. Neither
the tool nor its staged code could have worked after the rename.

Tests that exercised only those tools were removed with them: `tests/r65_finish/` (whole),
`tests/r66` PrepareTests, `tests/r67` three staging tests, and `tests/r68` four prepare/lock tests.
**Tests of live code in the same files were kept and repaired** (§5).

### 4.5 `tools/r71_source.lock.json`, `r71_prepare_review.py`, `r71_migrate_build_docs.py`, `r69_build_doc_migration.py` — **LEFT ALONE, on purpose**

R71 (the `asurakshit` unsafe boundary) is ChatGPT's **open, unaccepted** experimental extension. Its lock
says "this extension was reviewed against core `64ea028a`". That is true and still useful. Re-pinning
would claim a review of the v169 core that nobody has done. `R71_PREPARE_REFUSED: unreviewed core lock`
is the tool **working correctly**. Evidence that the extension still works on the new core, so ChatGPT
knows the re-review is mostly a formality:
- `tests/r71`: **65 PASS / 1 ERROR**. The error is exactly that refusal.
- The `R71-MEMORY-BOUNDARY.md` sample builds with `-DSUTRAM_R71_UNSAFE_BOUNDARY=1` and prints `42`
  (ROUND-01).

Two things for ChatGPT, which I did not change:
1. `tools/r71_prepare_review.py:19,22` keys its embedded pins as `src/r66_indic_lexer.vardh` and
   `src/r68_diagnostics.vardh`. The files are `.inc`, so the tool would refuse even with a correct core.
2. `r71_migrate_build_docs.py --plan` **works**. Its plan would rewrite build commands in 14 files,
   **including `Claude-to-Sarvam/03-DOCUMENTATION-AUDIT.md`**: it scans handoff folders, which are
   historical. Do not run `--apply-plan` until that scan is restricted.
   `r69_build_doc_migration.py --check` refuses with `document drift: PROJECT-OVERVIEW.md`, because its
   baseline is `11f41d3`. Both are one-time migrations. They should be retired together with the R71
   decision, not separately: `tests/r69` and `tests/r71` import them.

## 5. Repairs to live tests that sat behind the locks

1. **`tests/r68` HelperTests, 15 tests, were NOT-RUN on main.** Their C stub failed to compile under this
   GCC's `-Werror`: `(void)write(…)` still triggers `warn_unused_result`. I changed it to
   `if (write(…) < 0) _exit(93);`. With the stub compiling, 12/15 passed. The other 3 expected the English
   R68 diagnostics, which ROUND-02 deliberately translated. I updated those three to the strings now in
   `src/r68_diagnostics.inc:10,14`.
2. **`tests/r68` `test_pair_probe_exact_46_bytes`** looked for `nishkriya("…")`. The example uses
   `yantra("…")` (15 blocks, 46 bytes — verified). Fixed the regex.
3. **`tests/r68` `test_pack_aliases_and_no_invented_signs`** compared four whole packs to a pre-v157
   snapshot. Its stated intent was "no invented abbreviation signs". I rewrote it to test that intent
   directly: no `॰ ૰ ৽ ੶` in the odia/kannada/tamil/telugu packs. The Hindi/Marathi abbreviation rows are
   unchanged. To show the test is not vacuous, I checked each sign is present in its own script's pack
   (hindi/gujarati/bengali/punjabi → True).
4. **`tests/r66` `test_exhaustive_indic_second_third_bytes`** expected digits only in the four R66 blocks.
   The lexer recognises eight, because **R68 deliberately added** Odia (E0 AD), Tamil (E0 AF), Telugu
   (E0 B1) and Kannada (E0 B3), per `lang/*.lang` and `docs/R68-INDIC-DEVICES.md`. All 40 mismatches were
   those four blocks × 10 digits. Malayalam (E0 B5) is still rejected. I updated the expectation and
   commented it.
5. **`tests/r66`, `tests/r67` pack-preservation guards** compared the packs to pre-v157 baselines. Every
   difference was one of the 11 keyword renames applied to a *value*. **No native word was lost**
   (r66: 22 values, r67: 33 values; 0 words gone). I re-baselined by mapping the old values through the
   official rename table, then asserted that the result equals today's packs. I did not copy today's
   packs. The guard is live again.

**After:** `tests/r66` 22 OK · `tests/r67` 17 OK · `tests/r68` 19 OK · `tests/r69` 39 OK · `tests/r71`
65 OK + 1 ERROR (deliberate, §4.5).

## 6. One compiler fix, because I caused it — `r51_print_origin` / `r51_origin_line_col`

While checking R70's `unterminated_string` case, I found that **an unterminated string now reports line
1:1**:

```
$ printf 'mukhya() {\n    likha("abc)\n    likha(2)\n}\n' > e4.sm
v166:    Sutram Error: parse error at line 2:2 near token 'end of file'
v169:    Sutram Error: vyakaran dosh, pankti 1:1, shabd 'patra-ant'
--check (v166 and v169):  e4.sm:1:1: Sutram Error [E_PARSE]: …
```
**Cause:** the EOF token points one byte past the flattened source. The origin map has no entry there,
so the lookup falls back to offset 0 of the root file, which is line 1:1. `--check` has always had this.
**My ROUND-02 change made normal mode use the same lookup**, so normal mode inherited the bug (2:2 was
also wrong, but it was on the right line).

**Fix (contained, 9 instructions in each of the two lookups):** if the token offset is at or beyond
`source_len`, look up the last real byte and add one.
```
after:   e4.sm normal:  pankti 5:1 · --check: e4.sm:5:1      (5 = the line after the last newline)
         same through `yoj ganit`:  pankti 5:1 / e5.sm:5:1
         e1/e2/e3 (EOF after a complete line): unchanged
```
**New golden `examples/221_eof_location.sm`:** 1 FAIL on v169 (`pankti 1:1`), 1 PASS on the branch
(`pankti 9:1`).

## 7. Gates on the branch

```
$ sh tools/gates.sh
  regression suite (NO-EXPECTATION=4 PASS=189 ) PASS        (188 + 221)
  codegen shapes (12/12) PASS · language packs (33/33) PASS · library proofs (191/191) PASS
  property proofs (86/86) PASS · layer check (14/9/1) PASS · stdlib inventory PASS · module graph PASS
  X11 GUI protocol  FAIL  1 of 18 failed      ← same on main; see README "gates.sh" note
  Windows execution NOT-RUN
```

## 8. What I did not do

- Did not touch `windows/` (the third copy of the pin is at `windows/r69-build-common.ps1:45`) or the R71
  family. Both are ChatGPT's.
- Did not commit the `sutram_compiler` binary. It is tracked on main, and Sarvam rebuilds it at merge.
  Rebuild it after merging this branch, or it will not match `src/`.
- Did not retire the per-round CI workflows (`.github/workflows/r49…r59-native.yml`). They are manual
  dispatch only. WS2 covers the tools they run.
