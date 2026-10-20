# R13-04 — WS4: the Gujarati corrections

**None have arrived.** I checked main at `465c202f`:

- **`lang/gujarati.sandesh`** has no commit since the R11 merge.
- **`Claude-to-Sarvam/review-r12/gujarati.md`** has no commit since my R12 delivery.
- No new file holds corrections.

**So nothing was changed.** The only edit to `lang/gujarati.sandesh` this round is the version placeholder
(`{ver}` in `msg_version`, R13-01). It does not change any wording.

**When the corrections arrive:**

1. **What I will accept:** the sheet, edited, or a list of `number: correction`. The numbers are the
   sheet's (1–128).
2. **What I will do:**
   - apply each one to `lang/gujarati.sandesh`
   - run `tools/sandesh.py --write` and `--check`
   - re-record `tests/sandesh/expect/gujarati/`
   - regenerate the sheet
3. **What I will report:**
   - every message that changed, before and after
   - any correction the checks refuse, for example one that drops a `[E_CODE]` tag, with the reason

**If the owner corrects only the wording and keeps the identifiers and punctuation, no check will refuse
anything.**

**One thing he may want to know while reviewing:** the case suffix after a quoted name is printed after a
space (`'f' ને`). If Gujarati should attach it (`'f'ને`), say so. It needs one rule of the check relaxed
for four messages (R12-01).
