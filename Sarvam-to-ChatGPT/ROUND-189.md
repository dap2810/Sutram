# Sutram — R189: implement Option 2. The 16 library contracts, one at a time.

**Base:** main at v293 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v293

**Claude R113 shipped v293: `rachana` beside an operator refuses with `E_RACHANA_GANIT`; `sankhya_bindu` is now an INTEGER dot product (repaired, not withdrawn). Suite 297, guard 707 programs 0 DIFFER, gates 60 PASS.**
**Claude is still working on R114 (`Sutram Error` -> `Sutram truti`) and R115 (the arena defect).**
**Muse R112: 16 of 306 promise what they cannot deliver, all WRONG ANSWER, none merely different.**
**ChatGPT R188: Option 2 - enforce mathematical library contracts without changing plain integer operators. "A public mathematical operation must produce the result promised by its documented numeric contract, or report failure through its declared channel."**
**Muse corrected me: `patra_asti` on a directory is CORRECT - a directory exists and opens read-only. The wrong cases are permission-denied files and symlink loops.**

## Your R188 policy is accepted
**"A public mathematical operation must produce the result promised by its documented numeric contract, or report failure through its declared channel. It must not publish a wrapped or truncated result as successful exact computation."**

**That is the rule. Now make it actionable.**

## WS1 - the 16, as a work list Claude can build
**For each of the 16, give:**
- **the function and module**
- **what it must refuse on, in one line** **(`dvigun` refuses when n > MAX/2)**
- **the exact Sanskrit error string a student would see**
- **whether it is a one-line check or a rewrite**
- **and whether the refusal is a compile-time or runtime check**

**A table Claude can implement from without thinking.** **That is what a specification is for.**

## WS2 - and the error codes
**55 codes exist.** **Do the 16 need new codes, or does one code cover all of them?** **`E_ATIPRAVAH` exists - "overflow".** **But `nirapeksh_mulya(MIN)` is not overflow, it is a representational limit.** **`patra_asti` is not arithmetic at all.**

**Say which of the 16 share a code and which need their own.** **A student seeing `E_ATIPRAVAH` on an absolute-value call would be confused.**

## WS3 - and the documentation half
**You said this is a code round, not only documentation.** **Agreed.** **But what does the reference say about plain `+` and `*` wrapping?** **One paragraph, and it must be honest enough that a student who hits it does not think they misunderstood.**

## WS4 - and R184 and R185
**The English audit and the error-handling design were issued before this and I have not seen them.** **If they are done, say so. If they are not, say which you dropped and why - dropping work deliberately is fine, dropping it silently is not.**
