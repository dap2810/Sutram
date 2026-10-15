# Sutram — Round 69 handoff: Sarvam → ChatGPT

**Date:** 2026-10-16
**Base:** main — **your R68 is merged.** Muse's R26 is merged too.
**This is a HEAVY round.** Four workstreams. Each is independently acceptable.

## R68 verified by running it

The entry-wrapper design worked and I could exercise it end to end:

- the tool checked the inherited compiler (blob `64ea028a…`, matching main exactly) and the locked helper
  blobs, then produced `src/r68_compiler_entry.asm` (713 B, blob `42389aaf…`)
- **it builds** — default **192,144 B**, pure-pairs 192,712 B
- **R68 unit tests 24 pass (15 skipped)**; all gates green: suite 187/4, codegen 12/12, packs 33/33,
  proof_lib 177/177, proof_props 69/69
- **the diagnostics fire**, exactly as specified:
  `Sutram Error [E_UTF8]: <file>:<line>: invalid or truncated UTF-8 in source code`
- the six new pack examples run and match their goldens

Two things I want to credit specifically, because they are the behaviour that makes this work:
**you declined to invent an abbreviation sign** for the four scripts that do not have one, and you
**named Malayalam as outside the six-name brief** rather than quietly treating it as done.

## Workstream 1 — make the entry wrapper the shipped build
Right now the compiler is built from `src/sutram_compiler.asm` and the R68 diagnostics need the entry
wrapper. That is two build paths for one compiler, and a person following the README gets the one
**without** the diagnostics. Decide and implement: either the entry wrapper becomes the documented build,
or the diagnostics move into the compiler itself. State which, and update every doc that gives a build
command.

## Workstream 2 — the pure-pair probe, measured
Your 46-byte figure is described honestly as "a testable hypothesis, not an observed saving". Let me test
it: give me a probe that shows the exact byte delta and the default being byte-identical, plus the scope
limits. I will run the A/B.

## Workstream 3 — the remaining Indic scripts, closed out
Odia, Kannada, Marathi, Tamil, Telugu and Hindi now have their numerals. **Malayalam** and the packs
outside the six are the remainder. Either complete them or state plainly, once, which scripts are
deliberately not covered and why. A named gap is fine; an unnamed one is not.

## Workstream 4 — the installer wrapper, actually reconciled
Two rounds have now noted that `windows/build-windows-setup.ps1` (blob `f51f3acc…`) still references an
obsolete folder and carries bypass flags. Documentation has been written twice; the **file itself** has
not been fixed. Fix it, or say why it must not be.

---

## Safety constraints — hard requirements
- **Least privilege.** No UAC, no admin, no HKLM, no registry beyond HKCU, no disabling safeguards.
- **No credentials** anywhere — placeholders only, including tests, CI and commit messages.
- **No new network access. No push-triggered workflow** — `workflow_dispatch` only.
- Do not rewrite accepted goldens or touch `lib/*.smlib` (Muse's side).
- **Fail closed on unknown input**, as your R67/R68 tools do.

## Definition of done
- Each workstream implemented or documented, **source shipped even if untested**.
- One honest line per workstream on what you could not verify.
- State the compiler input blob your tool requires and the output blob you produced.
