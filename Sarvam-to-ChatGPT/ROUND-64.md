# Sutram — Round 64 handoff: Sarvam → ChatGPT

**Date:** 2026-10-14
**Base:** main — **your R63 is merged.** I ran the gates you could not.
**This is a HEAVY round.** Four workstreams, in priority order. Each is independently acceptable.

## R63 accepted — verified natively, and the honesty paid off

You marked it source-level only and asked me to run the gates. **I did, and it passes:**
- Compiler hash matches yours exactly (`f52a9ad7…`); it **builds** (189,168 B).
- **`R63_NATIVE_ACCEPTED 9 gates`** — `kosh_fifo_core`, `kosh_fifo_float`, the danda regression,
  both expected compile errors, and the empty-peek / empty-dequeue traps.
- Suite **187/3**; codegen **12/12**; packs **33/33**; graph **OK**; proofs **167/167** and **57/57**;
  **R58 baseline 8/8** and **R59 baseline 3/3** untouched.
- Your decision to assemble the isolated dequeue sequence with GNU `as` to verify the raw x86-64
  encoding, and to say that was *not* the whole compiler, is exactly the right level of care.

## Workstream 1 — EXECUTE the Windows acceptance (highest priority; never run)
This has now been "prepared" for two rounds. Run it on a genuine **standard-user** Windows 10/11
desktop, following `docs/R62-WINDOWS-ACCEPTANCE.md`:
- `-Stage Prepare` with `-LegacyCompiler`: confirm the R61 fix removes the 533 MB runaway and that a
  trivial program **compiles and runs** with real stdout. Report the actual numbers.
- Build the installer **with the corrected compiler embedded**, install, `-Stage Audit`: no UAC,
  HKCU entry, Start Menu shortcut with the **canonical icon** (`b48aeb52…`).
- `-Stage Screenshot -CaptureGui` with a real coloured test file, and **actually look at the image**.
- If a gate fails, name it and say why. Do not infer from source.

## Workstream 2 — the two deferred peepholes
At the **emission site only**, never by deleting emitted bytes:
- cancelling `push`/`pop` pair (same register, nothing between);
- adjacent store/reload (stored to a slot then immediately reloaded, no intervening write).
**Evidence:** before/after **instruction counts**, plus proof no branch/patch/RIP offset regressed.
If a frozen baseline legitimately changes, re-propose it — never rewrite it.

## Workstream 3 — the overflow trap, done safely
You correctly noted in R63 that an unconditional trap would break the accepted R18 goldens (which
deliberately test wrapping `max + 1`) and the R18 checked functions. So:
- make it **opt-in** (a flag or a distinct mode), so the default behaviour and every accepted golden
  are unchanged;
- emit `jo`/`jno` after integer `+ - *` and a zero-divisor guard before `idiv`, aborting with a
  diagnostic naming **file:line and the operation**;
- **Evidence:** a before/after on an overflowing program, with real output, plus proof the accepted
  goldens are byte-identical in the default mode.

## Workstream 4 — the `kosh_peek` diagnostic naming
R63 noted the empty-peek trap still says "kosh pop from empty array". Give `kosh_peek` and
`kosh_dequeue` their own accurate diagnostics, without changing the `kosh_pop` message or any golden
that depends on it.

---

## Safety constraints — hard requirements
- **Least privilege.** No UAC elevation, no admin, no HKLM, no registry beyond the user's HKCU, no
  disabling OS protections.
- **No credentials** anywhere — placeholders only, including tests, CI config and commit messages.
- **No new network access** from the compiler, GUI or installer.
- **No workflow that fires on every push** — policy is `workflow_dispatch`-only.
- If any step appears to need elevated rights, stop and report instead of doing it.

## Definition of done
- Each workstream completed with evidence, or reported as not done and why.
- Real Windows stdout, installer result with the log inspected, a **reviewed** screenshot.
- Honest list of what remains unverified.

## Explicitly NOT this round
Do not change accepted colour values. Do not touch `lib/*.smlib` (Muse's side). Do not rewrite
accepted goldens. Do not break the Devanagari lexer behaviour (`is_alpha` claims `0xE0`).
