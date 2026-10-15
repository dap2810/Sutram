# Sutram — Round 66 handoff: Sarvam → ChatGPT

**Date:** 2026-10-15
**Base:** main — R64 merged. Suite 187/3, codegen 12/12, packs 33/33, proofs 172/172 and 62/62,
R58 8/8, R59 3/3, R63 9 gates, R64 diagnostics accepted.
**This SUPERSEDES ROUND-65** — that round was never started, so do not work it. This is the bigger brief.

## The working rule (unchanged, and important)

You have reported no NASM / no Windows / no Wine / no PowerShell for several rounds. **That is fine.**
**You do source work and static reasoning. I do all native execution and Windows testing.**
- Do **not** spend a round declining an execution task. Note it in one line and move to the source work.
- **Ship the source even when you cannot test it.** An unverified implementation I can build and test
  is worth far more than another "NOT IMPLEMENTED". State your uncertainty; I will resolve it.

## This is a big round — six workstreams. Each is independently acceptable; partial credit is real.

### WS1 — the two peepholes (deferred three times; implement them this time)
At the **emission site only**, never by deleting emitted bytes:
- cancelling `push`/`pop` pair (same register, nothing between);
- adjacent store/reload (store to a slot then an immediate reload, no intervening write).
Guard each so it is inert if the pattern does not match. Do not measure — **I will run the before/after
instruction counts.** If you reject a pattern as unsafe, implement the safe one and say which and why.

### WS2 — the opt-in overflow trap
**Default OFF**, behind a flag or mode. Emit `jo`/`jno` after integer `+ - *`, and a zero-divisor guard
before `idiv`, aborting with a diagnostic naming **file:line and the operation**. Default-mode output
must stay byte-identical. **I will run the before/after and the golden-identity check.**

### WS3 — complete the Devanagari keyword surface
`lang/sanskrit.lang` has the 31 core keywords. Extend to the **remaining recognised keywords**
(`kosh`, `pankti`, `rachana`, `srijana`, `kuru`, `nishkriya`, `parigrah`, `grahan`, `niryat`, …).
**Lexer care:** `is_alpha` claims the `0xE0` lead byte (all nine Indic scripts share it), so a
multi-byte token must be consumed as a unit, never byte-by-byte. Also add Devanagari digits `०–९`
and the abbreviation sign `॰`.

### WS4 — roll the Indic device set to the next script: Gujarati
Sanskrit proved the pattern. Now do the **second** language properly, as the template for the rest:
- `lang/gujarati.lang` (the core keywords in Gujarati script — check the existing pack for the words);
- Gujarati numerals `૦–૯`;
- the abbreviation sign `૰` (U+0AF0) — Gujarati has its **own**, unlike the danda which is shared;
- confirm the shared danda `।`/`॥` still terminates statements under this pack;
- an example program written in Gujarati.
**This is the template** — document what is script-specific vs shared, so the remaining seven scripts
are mechanical.

### WS5 — the Windows GUI: Devanagari shaping
The GUI draws text with a fixed 8-pixel advance per byte, so Devanagari **mis-renders** (matras,
conjuncts, the shirorekha). Write the source-level plan and, if you can, the shaping routine: cluster
the 3-byte sequences and give each grapheme cluster one advance. **Source only** — I will test it.
If the full shaping is too large for this round, ship the clustering half and say what is left.

### WS6 — the legacy installer, documented honestly
The legacy `.nsi` path writes HKLM. Document exactly what it does, what the least-privilege
`install-core.ps1` does instead, and which one ships. **Documentation only.**

---

## Safety constraints — hard requirements
- **Least privilege.** No UAC, no admin, no HKLM, no registry beyond HKCU, no disabling safeguards.
- **No credentials** anywhere — placeholders only, including tests, CI and commit messages.
- **No new network access.** **No push-triggered workflow** — `workflow_dispatch` only.
- Do not change accepted colour values, touch `lib/*.smlib` (Muse's side), or rewrite accepted goldens.
- If a step appears to need elevated rights, stop and report instead of doing it.

## Definition of done
- Each workstream implemented or documented, **source shipped even if untested**.
- One honest line per workstream on what you could not verify.
- A patch or branch I can build. I run the gates; a source-level partial is expected and accepted.

## Explicitly NOT this round
Do not decline a workstream because you cannot execute it. Do not substitute another static-only audit
for implementation.
