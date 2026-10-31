# Sutram — ROUND-129: audit the 305 library names against their BODIES

**Base:** main at **v404**, compiler **v258** · **Deliver into:** `ChatGPT-to-Sarvam/`

**Read first:** `docs/vocabulary/VOCABULARY-TABLE.md`, `docs/reports/LIBRARY-ENGLISH-AUDIT.md`.

**This round REPLACES the earlier ROUND-129, which was about memory vocabulary.** **That work is deferred by the owner.**
**This is the vocabulary work, and it is the last deep piece of it.**

## Why this round exists
**`nishan` means "mark" and computes a matrix TRACE.** **`pehchan` is Hindi for identity.** **`samanvaya_akar_na` says "shape" and
checks whether m×n FITS.** **Every one of those was found by reading the BODY, not the name.**

**So the naming problem in this library is not English - it is names that are wrong about what the function does.** **A Sanskrit
name that describes the wrong operation is worse than an English name that describes the right one, because it looks finished.**

## WS1 — the audit, one function at a time
**All 305 library functions across the 24 modules in `lib/`.** **For each, read the body and answer: does the name describe
what the code does?**

**Output a TSV: `module | function | what the body actually does | name_accurate(Y/N) | why_not | better_name`**

**Only `N` rows need a better name.** **Do not propose a change for a name that is accurate - I want the failures, not a
rewrite of the whole library.**

## WS2 — the four I already know are wrong, as the calibration
**Start with these four and check my reading of them:**
- **`nishan`** - I say it computes the matrix trace (sum of the diagonal). **Is that right?**
- **`pehchan`** - I say it builds the identity matrix.
- **`samanvaya_akar_na`** - I say it checks whether m×n fits in a length.
- **`chay_*`** - I said `chay` was not a Sanskrit word; **you corrected me that चय means heap.** **So these four are FINE, and I was
wrong.** **Confirm that so I stop questioning them.**

**If my reading of any of the first three is wrong, say so - I have been wrong four times this session on names.**

## WS3 — and the 88 functions with no comment
**88 of 305 have no comment above them.** **Muse is writing them in ROUND-55.**
**For any function where the name is accurate but the body is surprising, say so** - **a comment saying "this looks like X but
does Y" is worth more than a rename.**

## Return
`ROUND-129-LIBRARY-NAMES.md` with the TSV, the four calibration verdicts, and the surprising-body list. **No code changes.**
