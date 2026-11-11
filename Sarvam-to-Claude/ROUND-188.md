# Sutram — ROUND-188: clean up, bring the docs current, and prove it with the gate.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**This round is documentation and cleanup only. No compiler change.**

**And it starts from an audit I did myself, so the findings are named rather than searched for.**

---

## 1. What I found, and it is worse than a stale sentence

### A. `docs/WHATS-LEFT.md` does not exist. It is at `docs/rounds/WHATS-LEFT.md`.
**Every brief issued for weeks has said "read `docs/WHATS-LEFT.md`".** **A partner following that instruction finds nothing.** **It has been filed into the archive, where a live document is invisible.**

**Fix: a live `docs/WHATS-LEFT.md`, current, at the path the briefs name.** **And the archived copy either deleted or clearly marked as history.**

### B. The CHANGELOG stops at v315. Nine staged versions are missing.
**v316 through v324 are in the tree as branches and in no document.**

**Missing: outputs never overwrite inputs · a list in a loop made once · a fixed array too · anywhere in a loop · memory cleared at a block's exit · the unknown character refused · reading a line of text · the file examples and `grahan`'s sign and last line.**

**That is the entire week's work, undocumented in the changelog.**

### C. And the audit found more than I could check from the outside.
**So: run `R158` and report what it says.** **It has 23 checks and it was built to catch exactly this.** **If it passes on this tree, that itself is a finding — and it would mean the gate has a gap, because A and B above are true.**

---

## 2. WS1 - and this is the round: bring everything current

**Not "update the docs" — these specific things:**

1. **A live `docs/WHATS-LEFT.md`** — every open item, in order, with the tier and the reason. **The nine-item plan as it now stands: all closed except generics, which is 1.1.**
2. **The CHANGELOG entries for v316 to v324**, in the project's format, each naming the round, the change, the gate, and the guard.
3. **`docs/RELEASE-NOTES.md`** — if it names a version, it should name the tip.
4. **`docs/PATH-TO-COMPLETION.md`** — if it still lists memory as open, it is wrong.
5. **`ROADMAP.md` and `PROJECT-MASTER.md`** — if either says memory is unfinished, or names a version older than v315, fix it.
6. **`README.md`** — does it describe what the language does today? **It should mention reading a line of text, because that is new and it is the first thing a beginner wants.**
7. **And the three reference errors ChatGPT found** — `likh8`/`pad8` as bits, `likh8c`/`pad8c` as the terminal, and the braces section calling a valid indented function invalid.

## WS2 - and the books
**The memory chapter landed two days ago and says what a block does not give back.** **But a block now clears its memory on exit — that is v320.** **So the chapter may already be wrong.**

**Check both books against v324's behaviour, and fix what is false.**

**And: does either book mention `vartani_grahan`?** **If a student cannot find the function that reads a line, the function may as well not exist.**

## WS3 - and the cleanup
**This project has 11,354 files and 85 MB. Some of it is history that nobody reads and some of it is noise.**

**So:**

1. **Name every file in `docs/` that is superseded** — a document describing a design that was replaced, a round summary in the wrong place, a duplicate.
2. **Name every file at the root that should be in `docs/`.**
3. **And say what could be deleted without losing a record.** **The rounds stay — that rule has not changed.** **But a file that is a duplicate of a round, or a design that was rejected and superseded, is not a record of anything.**

**Do not delete anything yet.** **Name it, and let the owner decide.**

## WS4 - and the proof
**Every documentation change must leave the gate clean.**

1. **Run `R158` before and after.**
2. **Run `R159 no personal paths`.**
3. **And the guard: documentation cannot change compiled output, so it must read 0 DIFFER.** **If it does not, something else changed.**

**Report the three, before and after.**

## WS5 - and the one thing to be careful about
**A documentation gate that passes on a tree with a missing live document and a nine-version-old changelog is a gate with a gap.**

**So: if `R158` passes on this tree as it stands, say so, and say which check should have caught A and B.** **That is a finding about the gate, and it is worth more than the fixes.**
