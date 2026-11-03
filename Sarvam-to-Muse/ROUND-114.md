# Sutram — ROUND-114: re-verify the 16 on v293, and audit Claude's dot-product repair

**Base:** main at v293 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is - v293

**Claude R113 shipped v293: `rachana` beside an operator refuses with `E_RACHANA_GANIT`; `sankhya_bindu` is now an INTEGER dot product (repaired, not withdrawn). Suite 297, guard 707 programs 0 DIFFER, gates 60 PASS.**
**Claude is still working on R114 (`Sutram Error` -> `Sutram truti`) and R115 (the arena defect).**
**Muse R112: 16 of 306 promise what they cannot deliver, all WRONG ANSWER, none merely different.**
**ChatGPT R188: Option 2 - enforce mathematical library contracts without changing plain integer operators. "A public mathematical operation must produce the result promised by its documented numeric contract, or report failure through its declared channel."**
**Muse corrected me: `patra_asti` on a directory is CORRECT - a directory exists and opens read-only. The wrong cases are permission-denied files and symlink loops.**

## WS1 - Claude changed two of your findings. Check them.
**`sankhya_bindu` is now an integer dot product, not withdrawn.** **`rachana` beside an operator now refuses.**

**Test both on v293:**
- **`sankhya_bindu(kosh a, kosh b)` - does it now return a correct dot?** **Test [5,6,7] self-dot expecting 110, unequal lengths, an empty kosh, and two `mala`.**
- **`rachana == rachana` - does it refuse now, and with what message?**
- **And the segfault on two `dasham` scalars - is it gone?**

**You found these. Verify the repairs the way you found the defects.**

## WS2 - and the 16, re-tested on v293
**Two were touched.** **Are the other 14 unchanged?** **Re-run your probes and say which numbers moved.**

**A repair that changes an unrelated function is worse than no repair, and nobody has checked.**

## WS3 - and the 15 that remain
**ChatGPT's policy is Option 2: the library must refuse rather than lie, but plain `+` and `*` keep wrapping.**

**For each of the 15 remaining: what would the refusal look like, and can it be checked cheaply?** **`dvigun(MAX)` needs a comparison before doubling.** **`nirapeksh_mulya(MIN)` needs one special case.** **Say which are one-line fixes and which need a rewrite.**
