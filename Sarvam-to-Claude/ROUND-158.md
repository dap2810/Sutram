# Sutram — ROUND-158: doc currency becomes a gate, not a habit

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**This is a standing instruction from the owner, and it should be enforced by a gate rather than remembered by anyone:**

> **"The docs should be up to date as we progress."**

---

## Why a gate and not a habit

**Every other durable property in this project is a gate.** **The guard compiles 783 programs and compares bytes.** **The slice gate builds deliberately-broken compilers.** **The package gate recomputes hashes.**

**Docs have been a habit, and the audit shows what a habit produces: a book whose chapter 14 says "New Features: v22", and no chapter at all on the memory model that took two weeks to build.**

**So: make it a gate.** **A habit that depends on someone remembering is a habit that lapses the week they are busy.**

---

## WS1 - and the gate has to be specific enough to fail
**A gate that says "docs are current" is not checkable.** **These are:**

1. **Every doc that names a version names the current one, or says which version it describes.** **`docs/CHANGELOG.md` is the record and may name old versions; a tutorial may not.**
2. **Every named symbol a doc cites exists in `src/`.** **I invented `r157` and `r23_check_call` in briefs and a partner caught both by grepping.** **A doc that names a symbol a reader cannot find is the same defect.**
3. **Every code example in the books compiles on the current compiler.** **Extract them, compile them, fail if any fails.**
4. **Every command a doc tells a reader to run is accepted by the current binary.** **`--analysis-steps=N` is in the reference; is `--analysis-steps` with a space? A doc that teaches a rejected form is worse than silent.**
5. **The memory chapter exists in the English and Sanskrit books and covers the seven topics in ROUND-157.**

**Build those five as a gate. Name it. And make it fail on v315 as it stands, so we know it works.**

**A gate that passes on first run has not been tested.**

## WS2 - and the changelog
**`docs/CHANGELOG.md` carries the 20 newest entries and an archive for the rest.** **Is every version from v309 to v315 present with what it changed?**

**And does each entry name the version, who did it and the round number?** **If a reader cannot tell what changed between v313 and v314 from the changelog alone, the changelog is a log rather than a record.**

## WS3 - and the standing rule, written where it will be read
**Put the rule in `AGENTS.md` or `PROJECT-MASTER.md`, whichever a new contributor reads first:**

> **Docs are part of the change, not a task after it. A round that changes behaviour updates the reference, the changelog and any book chapter that describes that behaviour. The gate checks it; do not rely on the gate to remember what you forgot.**

**That last sentence matters: the gate catches a missing version number, not a paragraph that is now false.**

## WS4 - and then ROUND-157's work stands
**The memory chapter in English and Sanskrit, then the prune, then the four paused-language books.**

**This round is about making it stay true afterwards.**
