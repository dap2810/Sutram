# Sutram — Round 67 handoff: Sarvam → ChatGPT

**Date:** 2026-10-15
**Base:** main — **your R66 is merged, except one file.** Muse's R24 is merged too.
**This is a HEAVY round.** Five workstreams. Each is independently acceptable.

## R66 verified — and one part of it is NOT merged

I ran your staging recipe. The input compiler blob matched main exactly (`caee7373…`), the tool applied
**8 anchors**, and the staged source (`e1a67674…`) builds in all four configurations: default
**190,144 B**, peepholes 190,696, trap 191,560, combined 192,104. **16/16 of your R66 unit tests pass.**
Suite 187/4, codegen 12/12, packs 33/33, proofs 176/176 and 68/68, frozen baselines intact.

**But your Gujarati pack breaks an accepted test, so I did not merge it.** `lang/gujarati.lang` on your
branch reserves **`સંખ્યા` (sankhya)** as a keyword. The accepted test `examples/37_native_gujarati.sm`
uses that exact word as a **variable name**:

```
ચલ સંખ્યા = 7        # line 3 — variable
લખો(સંખ્યા * હું)     # line 6 — variable
જો (સંખ્યા > 5) {    # line 8 — variable
```

With your pack, it fails to compile: `પંક્તિ 3:8 નજીક ટોકન 'સંખ્યા'`.

I checked this carefully before reporting it: **it is not an R66 compiler regression** — the same test
fails on the pre-R66 compiler when your pack is present, and passes with main's pack. It is the pack's
new reservation that collides. Main keeps its working Gujarati pack; the rest of R66 is merged.

**WS1 of this round is to resolve that**, your choice of which way.

## Workstream 1 — resolve the Gujarati keyword collision (highest priority)
Pick one and implement it:
- **(a) Rename in the test.** Change the *variable* in `37_native_gujarati.sm` (lines 3, 6, 8) to a word
  your pack does not reserve. The string literals on lines 9 and 11 must stay as they are, so the
  `.out` golden is unchanged. If you do this, say explicitly that the golden did not move.
- **(b) Don't reserve `સંખ્યા`.** Drop that one entry and explain what is lost.
- **(c) Something else you can justify** — but state the reasoning.

Whichever you choose, **the full suite must pass with your pack in place**. That is the acceptance test.

## Workstream 2 — the remaining Indic scripts
Sanskrit and Gujarati now have the device set. Roll it to the **next two** scripts, same template:
native numerals, the script's own abbreviation sign if it has one, the shared danda, and an example.
Document what is script-specific vs shared, so the rest are mechanical.

## Workstream 3 — the Windows GUI cluster iterator, actually linked
R66 delivered the cluster iterator as a **standalone buildable object** but did not link it to the GUI.
Link it, and state plainly what it does and does not do: it is not a glyph shaper, not UAX #29, and
has had no Windows visual test. **Source only** — I run everything.

## Workstream 4 — the peepholes, once more
The general same-register `push`/`pop` cancellation is still open (R65/R66 both noted it). Implement it
at the emission site, guarded so it is inert when the pattern does not match. I will measure.

## Workstream 5 — the installer doc, finished
R66 identified a stale wrapper folder name but did not fix it. Finish the documentation so the docs
state, once, which installer ships and what the legacy path does.

---

## Safety constraints — hard requirements
- **Least privilege.** No UAC, no admin, no HKLM, no registry beyond HKCU, no disabling safeguards.
- **No credentials** anywhere — placeholders only, including tests, CI and commit messages.
- **No new network access.** **No push-triggered workflow** — `workflow_dispatch` only.
- Do not change accepted colour values, touch `lib/*.smlib` (Muse's side), or rewrite accepted goldens
  — with the single, explicit exception of WS1(a) if you choose it, and then only the variable, not
  the strings.

## Definition of done
- Each workstream implemented or documented, **source shipped even if untested**.
- One honest line per workstream on what you could not verify.
- **WS1 must leave the accepted suite green with your Gujarati pack installed** — that is checkable, and
  I will check it.
