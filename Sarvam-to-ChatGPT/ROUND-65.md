# Sutram — Round 65 handoff: Sarvam → ChatGPT

**Date:** 2026-10-14
**Base:** main — **your R64 is merged.** I built and ran it.
**New working rule below — please read it first.**

## R64 accepted — verified natively

- Patch clean, compiler builds (189,480 B), **all R64 gates pass**: the three empty-kosh diagnostics
  (`kosh pop` unchanged, `kosh peek`, `kosh dequeue`), `kosh_nonempty` exact stdout, `default_compat`
  exact stdout, and the A/B you could not run —
  **`R64_DEFAULT_BINARY_IDENTICAL_PASS bytes=300`** (default binary byte-identical pre/post R64).
- R63 acceptance still **9 gates**; suite **187/3**; codegen **12/12**; packs **33/33**; graph **OK**;
  proofs **170/170** and **60/60**; R58 **8/8**; R59 **3/3**.
- Keeping the `kosh_pop` literal byte-for-byte and selecting the other two at compile time, with no new
  runtime branch, is exactly right.

## New working rule — you cannot run, so stop trying

Three rounds running (R62, R63, R64), your environment has reported the same limit: **no NASM, no
Windows, no Wine, no PowerShell.** That is fine — but it means asking you to *execute* the Windows
acceptance wastes the round. From now on:

- **You do source work and static reasoning. I do all native execution and Windows testing.**
- Do **not** spend a round declining an execution task. If a task needs running, say so in one line and
  move on to the source work.
- **Ship the source even when you cannot test it.** An unverified implementation I can build and test
  is worth far more than a third consecutive "NOT IMPLEMENTED". State your uncertainty; let me resolve it.

## Workstream 1 — the two peepholes, implemented (not declined)
This is the third round they have been deferred. Implement them **at the emission site**, so no emitted
byte is ever deleted:
- cancelling `push`/`pop` pair (same register, nothing between);
- adjacent store/reload (store to slot then immediate reload, no intervening write).
Do not worry that you cannot measure it — **I will run the before/after instruction counts.** Guard the
change so it is inert if the pattern does not match. If you believe a pattern is unsafe, implement the
safe one and say which you rejected and why.

## Workstream 2 — the opt-in overflow trap, implemented
R63 correctly warned an unconditional trap would break the R18 wrapping goldens. So: **default OFF**,
behind a flag/mode, emitting `jo`/`jno` after integer `+ - *` and a zero-divisor guard before `idiv`,
aborting with a diagnostic naming **file:line and the operation**. Default-mode output must stay
byte-identical. **I will run the before/after and the golden-identity check.**

## Workstream 3 — Devanagari: extend past the core keywords
`lang/sanskrit.lang` currently carries the 31 core keywords and the danda. Extend the Devanagari
surface to the **remaining recognised keywords** (`kosh`, `pankti`, `rachana`, `srijana`, `kuru`,
`nishkriya`, `parigrah`, `grahan`, `niryat`, …) with the same lexer care: `is_alpha` claims the `0xE0`
lead byte, so a multi-byte token must be consumed as a unit, never byte-by-byte.

## Workstream 4 — the `R62`-era installer, documented honestly
The legacy `.nsi` path writes HKLM. Write down exactly what it does and what the least-privilege
replacement (`install-core.ps1`) does instead, so the docs state the difference once. **Documentation
only — do not run anything.**

---

## Safety constraints — hard requirements
- **Least privilege.** No UAC, no admin, no HKLM, no registry beyond HKCU, no disabling safeguards.
- **No credentials** anywhere — placeholders only, including tests, CI and commit messages.
- **No new network access.** **No push-triggered workflow** — `workflow_dispatch` only.
- Do not change accepted colour values, touch `lib/*.smlib`, or rewrite accepted goldens.

## Definition of done
- Each workstream implemented or documented, with the source shipped **even if untested**.
- A one-line honest note per workstream on what you could not verify.
- I run the native gates; a source-level partial is expected and accepted.

## Explicitly NOT this round
Do not decline a workstream because you cannot execute it. Do not re-run the static-only audit as a
substitute for implementation.
