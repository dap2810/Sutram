# Sutram — ROUND-141: the module-level initializer, and the last ownership gap

**Base:** main at v309 · **Deliver into:** `Claude-to-Sarvam/`

## Where the project is - v309, and Windows has verified both fixes

**`gates: 75 PASS / 0 FAIL / 1 NOT-RUN` · `suite: PASS=327 (331 run)` · `Sutram 1.0 (v309)` · installer `ceb92682bc5faa7575a7f6b65efc05d4fe4c157a339ecb13fb5e5e4da67459a0`.**

**NATIVE WINDOWS VERIFICATION OF v309 - the two fixes only Windows could check:**
- **OOM: 32 of 32 cases exit 1 with the exact 32-byte Sanskrit diagnostic, no `0xC00000FD`, no timeout.** On v307, 18 of those 32 had crashed.
- **Arithmetic: 7 of 7** - six refusals, **and `pankti_gan(k[0:2])` still returns `2`.** The fix did not overshoot.
- **Installer:** clean 9.47 s; upgrade 21.20 s with 654 files unchanged; interrupt-then-retry 8.65 s; **a hand-edited file preserved with its exact bytes and the installer refuses**; identity one canonical path, registry `1.0.309`, **657/657 hashes match**.
- **Suite: 322 PASS, 0 FAIL / COMPILE_FAIL / TIMEOUT.**

**PAYLOAD DETERMINISM IS FIXED AND GATED.** `text eol=lf` now covers 560 files (`/README.md`, `/LICENSE.txt`, `docs/**/*.md|html|txt`, `examples/**/*.md|out|exit|txt`, `windows/native-installer/*.ps1|md`). Gate `R140 package` runs `git check-attr eol` over 560 of 560. **And the proof is the right one: *"the same bytes when built from a CRLF copy of the tree dated 400 days earlier."*** **Not "the hashes match" - corrupt the input and the output does not change.**

### STILL OPEN, and both are narrow
**1. A slice path outside any statement.** Claude's R140 first said "the one path outside a statement is module-level `vitti` initializers" and then corrected itself: **that path is REACHABLE TODAY - a `kosh` from a call becomes a number there (ChatGPT's C1, confirmed on v309).**
**2. Installer ownership in the final journal engine.** ChatGPT credits progress - *"Source fixes preserve ambiguous legacy partials, put the transaction lock outside its cleanup"* - but has not closed it.
**3. And late recovery restages all 657 files** - safe, but wasteful.

## WS1 - and this is the one confirmed reachable path
**Your own R140 correction: *"that path is reachable today - a `kosh` from a call becomes a number there (ChatGPT's C1, confirmed on v309)."***

**A module-level `vitti` initializer is not a statement, so `r137_check_stmt` never runs on it.**

**Fix it. And answer the question underneath: is "run the check on every statement" the right shape, or should the check run where a value is BOUND rather than where it is WRITTEN?**

**A binding check would cover statements and initializers with one rule.** **If that is a bigger change, say so and do the narrow fix first - but say which is right.**

**Then: what else is not a statement?** **A record field default, a `prakriya` default argument, a module-level `kosh` initializer, a constant.** **Name every one and say whether it is covered.**

## WS2 - and the ownership gap ChatGPT has not closed
**Its words: *"Source fixes preserve ambiguous legacy partials, put the transaction lock outside its cleanup"* - credited, not closed.**

**Read its R208 follow-up section on ownership and answer each finding by name.**

**If a finding is already fixed, say which and give the evidence.** **If one is not, fix it.** **Do not let "credited" stand as "closed".**

## WS3 - and the late recovery that restages 657 files
**Interrupted after the last file, the retry re-copies everything.** **Safe, but wasteful - and it is the case your journal was designed to handle.**

**Why does it not recognise completion?** **The journal should know the last file was written.**

**Fix it, or say why recognising completion is unsafe.**
