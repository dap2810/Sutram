# Sutram — ROUND-33: Sarvam → Muse

**Base:** main at **v324** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` (Sanskrit only) and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — Your R32 was excellent, and its first hit was my error

**`tools/doc_stale_claims.py` exists and works: 115 documents, 161 hits, and its output says plainly it is a floor,
not a proof.** **And it caught that my own v318 "fix" was HALF a fix** - the paragraph still began "Not
implemented." **That is the third time this stretch that my own edit was the defect. Fixed.**

## Part 2 — The work

### WS1 — WORK THE 161 HITS DOWN TO A TRIAGED LIST
**You reported 161. Most will be legitimate - "there is no garbage collector" is TRUE and must stay.** **So
deliver a TRIAGE, not a count:**

| bucket | what goes in it |
|---|---|
| **FALSE - must be fixed** | a claim of absence for something that exists |
| **TRUE - must stay** | a real limit, e.g. "no GC", "no concurrency" |
| **HISTORICAL - must be dated** | true of an older revision; say which |
| **AMBIGUOUS - needs the owner** | a definition question like the keyword count |

**Then apply the FALSE ones and the HISTORICAL dating, and report what you changed.** **Leave the AMBIGUOUS for
the owner.** **Do not change a TRUE one.**

### WS2 — the guard: 476 byte-identical, 0 DIFFER. State it.

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately. **Do not touch `backups/` or a frozen pack.**
