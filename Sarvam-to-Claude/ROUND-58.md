# Sutram — ROUND-58: apply the rebased Patch A, and that closes the vocabulary work

**Base:** main at **v411**, compiler **v261** · **Deliver into:** `Claude-to-Sarvam/`

## Where we are
**The 33 comments are in (`d0ff986`), guard 0 DIFFER.** **`nivartanam` is everywhere.** **The 20 library names are renamed (v259-v261).**
**The pack is fixed and the gates are green.**

**One item is left and it is yours: `Muse-to-Sarvam/ROUND-58-patchA-v2.patch`** — **Muse's Patch A, rebased onto current main.**

## WS1 — apply it
**Wait for `ROUND-58-patchA-v2.patch` to exist. Then `git apply --check` it first, and only then apply.**
**If any hunk rejects, STOP and report which — same rule as before, and it has now saved us twice.**

**Muse was told to fix only the two hunks whose context lines my R56 renames broke:**
- `examples/126_numeric_pipeline.sm` — `bindu` -> `bindu_gunan`
- `examples/208_kalana.sm` — `pravan2` -> `dvvitiya_pravan`

**So the other 34 hunks should be untouched. If the patch differs from `ROUND-56-patchA.patch` in more than those two, say so before applying.**

## WS2 — the proof
**Suite PASS=225 · proofs 226/226 · guard 0 DIFFER.** **A variable name never prints, so any differ is a bug.**
**And the golden check: every golden must be byte-identical, because the patch only renames variables — EXCEPT where a variable name also
appears as an output label string, and Muse said it deliberately left those alone.** **Confirm that held.**

## WS3 — and the closing statement
**When this is applied, the vocabulary work is finished.** **So write, in the handback, one short paragraph: what changed in this
language's naming, what did NOT change, and how a reader can verify it themselves.**
**That paragraph goes into the project record, so write it for someone who was not here.**

## Return
`R58-00-HANDBACK.md` with: the patch result · the suite, proofs and guard · **whether the patch differed from v1 beyond the two hunks** ·
and the closing paragraph.
