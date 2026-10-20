# R14-03 — WS3: the Gujarati corrections

**None have arrived. Nothing was changed.** I checked main at `a82968d1`:

- **`lang/gujarati.sandesh`:** the only commit since R11 is the R13 merge. It changed the default's
  reference comments (`# "…"`) and `{ver}` in `msg_version`. **No Gujarati wording changed.**
- **`Claude-to-Sarvam/review-r12/gujarati.md`:** no commit since my R12 delivery.
- No other file holds corrections.

**The steps are ready, as in R13-04:**

1. **I accept** the sheet, edited, or a list of `number: correction` (the sheet's numbers, 1–128).
2. **I will:** apply each one to `lang/gujarati.sandesh`, run `tools/sandesh.py --write` and `--check`,
   re-record `tests/sandesh/expect/gujarati/`, and regenerate the sheet.
3. **I will report:** every changed message, before and after, and any correction a check refuses, with the
   reason.

**One thing the owner should know while he reviews: the sheet's "Default" lines are out of date.**

- The sheet was made in R12. **R13 then rewrote the default in Sanskrit grammar** (R13-02).
- So in **41 of the sheet's "Default (romanised Sanskrit), as printed" lines**, the default shown is the old
  Hindi-grammar one. Example, at line 237 of the file: `Sanket: 'x' pahle se ghoshit hai; …`, now
  `Sanket: 'x' purvam eva ghoshitam; …`.
- **The Gujarati lines he is reviewing are unchanged,** and so are the numbers. The only other difference is
  the version in `msg_version`, v182 then, v208 now.
- **I did not regenerate the sheet,** because he may be editing it. A regenerated sheet would conflict with
  his edits. **The Default lines are a reference only; the Gujarati is what he is correcting.** When his
  corrections come back, I will regenerate it.
- The Hindi and Sanskrit sheets have the same 41 stale lines. They should be regenerated before those
  reviews start. Say when, and I will do it in that round.
