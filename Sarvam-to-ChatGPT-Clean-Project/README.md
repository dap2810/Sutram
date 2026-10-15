# Sarvam → ChatGPT — Clean Project handover

This folder is a **whole-project audit handover**. It is a temporary change of role: instead of
authoring the next feature slice, you are asked to take the entire project, build it, audit it for
mistakes, fix them, and bring every file up to date.

## What is in this folder

| File | What it is |
|---|---|
| `CLEAN-PROJECT-BRIEF.md` | **read this first** — the full instruction |
| `SUTRAM-CLEAN-PROJECT.zip` | the complete current project tree, collaboration folders removed |
| `SHA256.txt` | checksums for the files in this folder |

## Return your work to

`ChatGPT-to-Sarvam-Clean/` — see the brief for exactly what to return.

## The short version

1. Build the compiler and the IDE from the archive.
2. Audit the whole project: stale test assertions, stale doc numbers, contradictory claims,
   unreadable HTML, anything that does not work.
3. Fix what you find. Do not rewrite accepted goldens — report them instead.
4. Bring every *current* claim up to date. Leave the CHANGELOG alone; its old numbers are history.
5. Report honestly, including what you could not do.

**The defect that started this round:** `tests/r66/test_prepare_review.py` asserts the Gujarati pack
has 45 entries, but R67's fix left it at 44. One round changed the pack; another round's test still
asserts the old count. Find that one's siblings.
