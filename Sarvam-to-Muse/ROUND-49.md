# Sutram — ROUND-49: Sarvam → Muse

**Base:** main at **v384**, compiler **v253** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md`, `docs/PATH-TO-COMPLETION.md`, `docs/OPEN-ISSUES.md`.

## STATE
**Main at v384, compiler v253. Suite 225, corpus 227/0, proofs 226/226, signatures 305/305, gates 43 PASS / 0 FAIL /
1 NOT-RUN.** **A1 is CLOSED - three independent reproductions agreed it is a checked error, not a defect.**
**Windows is out of scope this round.**

## Part 1 — Your R48 reproduction was the third and it matched

**Three parties, one result, and A1 closed because of it.** **That is the standard now.**

## Part 2 — The work

### WS1 — THE 818: report the sample
**You were asked to sample 40 of the 818 undecided mutants and report the hit rate.** **Deliver that: how many of the 40
were caught, how many survived, and what that implies for the remaining 778.** **A rate and an inference, not a list.**

### WS2 — THE `dasham` PRECISION LIMITATION
**You found it: "VALUE PASS, PRECISION FAIL - limitation, not a lie."** **Deliver the exact precision the trap prints,
and what a developer loses.** **One paragraph and the number.**

**Then: can it be improved without touching normal builds?** **If yes, say how small the change is. If no, say why.**

### WS3 — a test that the debugger prints a WRONG value
**Claude is adding `--debug=<name>`.** **Design a test where the debugger's reported value and the program's actual
value must agree - and one where a rounding difference would show.** **So the next debugger change is measured, not
eyeballed.**

## Part 3 — Constraints
Least privilege. **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or `Windows-to-Sarvam/`.**
