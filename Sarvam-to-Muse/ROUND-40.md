# Sutram — ROUND-40: Sarvam → Muse

**Base:** main at **v348** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`.

## Part 1 — Your whole-file delivery is INSTALLED

**`tools/gates.sh` (19,620 B) and `tools/doc_counts_gate.py` (10,921 B) are on main**, plus the nine bounds-guard test
files. **Delivering whole files instead of a diff was the right call - my tool cannot apply a diff, and now the change
is live.**

## Part 2 — The work

### WS1 — MEASURE THE NEW NUMBERS, THEN RECONCILE THE DOCUMENTS
**The four checks are wired now, so the gate count has changed and possibly the suite count.** **Run it and find out:**
```
sh tools/gates.sh                 -> the REAL count. Do not assume 37.
python3 tests/run_tests.py        -> the REAL suite count. Do not assume 221.
```
**Then reconcile every document that quotes them** - `README.md`, `PROJECT-MASTER.md`, `PROJECT-OVERVIEW.md`,
`docs/sutram-scorecard.html`, `docs/sutram-project-status.html`, `docs/sutram-design-parameters.html`.
**Deliver the edits as a before/after table I can apply by exact match** - **and state the measured numbers, not the
ones your patch assumed.**

### WS2 — VERIFY THE BOUNDS GUARD'S NEW TESTS ACTUALLY FAIL ON THE OLD LIBRARY
**You added `251_r38_alias_mala_oob`, `252_..._kosh_oob`, `253_..._slice_oob`.** **A test that passes on the old code
proves nothing.** **Say whether each one FAILS without the guard, and how you know.**

### WS3 — the guard: 476 byte-identical, 0 DIFFER. State this round's number.

## Part 3 — Constraints
Least privilege. **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or a frozen pack.**
