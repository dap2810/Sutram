# Sutram — R209: the last two conditions, and one question about method

**Base:** main at v309 · **Deliver into:** `ChatGPT-to-Sarvam/`

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

## WS1 - your C1 is confirmed and being fixed
**You found the module-level initializer path by reading.** **Claude's R140 first said it was the only path outside a statement, then corrected itself: *"that path is reachable today - a `kosh` from a call becomes a number there (ChatGPT's C1, confirmed on v309)."***

**So your reading was right and the implementation agreed with you.**

**Now: is there an eleventh path?** **You have found direct call, function value, untyped storage, arithmetic, and the module initializer.** **What is the next one you would look for?**

**And the question underneath, which is the useful one: if the check runs where a value is WRITTEN, every place that is not a statement is a hole. If it ran where a value is BOUND, would that close the class?**

**Say which shape is right. That answer is worth more than another path.**

## WS2 - and the ownership findings, by name
**Claude is asked to answer each of your R207-followup ownership findings individually.** **So: list them again, numbered, with the exact check each one needs.**

**Not "resolve ownership" - the specific conditions, so they can be verified rather than interpreted.** **You have been doing this well; keep doing it.**

## WS3 - and the release verdict, which is now close
**Your conditions were four. Against v309:**
1. **Class-level slice rule** - done, 59 gate checks, natively verified 7/7
2. **Installer ownership in the final journal engine** - credited, not closed
3. **One exact package, deterministic bytes, manifest verified against the embedded ZIP** - **done**: `text eol=lf` over 560 files, gate `R140 package`, and the proof is *"the same bytes when built from a CRLF copy of the tree dated 400 days earlier"*; 657/657 embedded integrity
4. **Release notes that do not overclaim** - written

**So: with the module initializer fixed and ownership closed by name, is v310 a YES?**

**And if yes - what exactly must the release notes say is NOT included?** **Your list, not mine. You have corrected four of my claims and been right each time.**
