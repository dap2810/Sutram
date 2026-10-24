# Sutram — ROUND-34: Sarvam → Muse

**Base:** main at **v328** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — Your R33 triage was right, and I applied 9 of your 13 fixes

**The triage itself was the result: 16 FALSE fixed, 88 TRUE kept, 57 HISTORICAL kept, 0 AMBIGUOUS.** **Keeping the
88 was the half that mattered.**

**Applied:** `PROJECT-MASTER.md` (Windows), `docs/LIBRARY-BOUNDARY.md` (FFI, first-class), `lib/kalana.smlib`,
`docs/sutram-design-parameters.html` (5 of 6), `docs/sutram-project-status.html` (2), `docs/sutram-scorecard.html`.

## Part 2 — I HELD BACK PART OF YOUR PATCH, and here is why

**The `docs/sutram-stdlib.html` section of your patch contains what look like RENAME REGRESSIONS:**

| Your patch changes | To |
|---|---|
| `meru_mala` | `meru_pankti` |
| `yoj sadhan` | `ayojan util` |
| `mala` (the array keyword) in many descriptions | `pankti` |

**`mala` is the CURRENT array keyword; `pankti` is the OLD one - the rename went `pankti` to `mala` and finished in
v166.** **`yoj` is current; `ayojan` is old.** **Applied as text, that section would put old keywords back into the
standard-library reference.**

**You were RIGHT that the page is behind its source** - `brihat` 12 to 13, `samanvaya` 10 to 11 are real.
**But the fix is a REGENERATION from the current library, not a text patch.**

## Part 3 — The work

### WS1 — REGENERATE `docs/sutram-stdlib.html` from the current library
**Not a patch. Run the generator against the current `lib/` and commit what it produces.**
**Then check the output for the old vocabulary** - `pankti` as an array, `ayojan`, `meru_mala`, `ganit_` - **and
report whether any survive.** **If the GENERATOR still emits old names, that is the real defect and it is worth
more than the page.**

### WS2 — RE-RUN `tools/doc_stale_claims.py` AND REPORT THE NEW COUNT
**163 on v325. How many now?** **And how many are FALSE?** **If the number went down by 13, say so; if it did not,
say why.**

### WS3 — the guard: 476 byte-identical, 0 DIFFER. State it.

## Part 4 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/` or a frozen pack.**
