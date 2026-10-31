# Sutram — ROUND-88: reorganise `docs/` into four folders, in one commit

**Base:** main at v278 · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour

**`docs/` holds 75 `.md` files, 2.1 MB.** The changelog alone is 672 KB - a third of the folder. **Eleven files are round work-products named `R50-`, `R54-`, `R58-`, `R63-`, `R64-`, `R65-`, `R67-`, `R68-`, `R69-`, `R71-`, `R72-`.** **Four are views of one vocabulary.**

**I cannot do this round: I cannot run `git mv`, and a move of 75 files across folders without git is a hundred API calls and a guaranteed broken link.**

## WS1 - the four folders

**`docs/` keeps the documents a person actually needs:**
`LANGUAGE-REFERENCE.md`, `SPECIFICATION.md`, `MEMORY-MODEL.md`, `NUMERIC-CONTRACT.md`, `OBJECT-FORMAT.md`, `ERROR-CONVENTION.md`, `WHATS-LEFT.md`, `OPEN-ISSUES.md`, `CHANGELOG.md`, `AI-WORK-DIVISION.md`.

**`docs/vocabulary/` - merge `VOCABULARY-TABLE` + `VOCABULARY-SHORT` + `VOCABULARY-COMPLETE` + `VOCABULARY-RULE` into ONE `VOCABULARY.md`.** They are four views of one subject and the duplication is the reason none of them is authoritative.

**`docs/decisions/` - the reasoning behind choices already made:**
`MEMORY-DECISION`, `MEMORY-UNIQUE-HYBRID`, `ALIAS-DESIGN`, and the other design records.

**`docs/rounds/` - every `R*-*.md` and every other round work-product.** **Move, do not delete.** The repo convention is that every round is kept, and `R64-00-STEP0-STOPPED.md` is the reason the memory design was redone correctly - an old round file is not junk.

## WS2 - and split the changelog

**672 KB means nobody opens it.** `CHANGELOG.md` keeps the last 20 entries. The rest goes to `docs/rounds/CHANGELOG-ARCHIVE.md`, with a line at the top of each saying where the other half is.

## WS3 - and the check that matters

**After the move, grep the whole tree - not just `docs/` - for links to every moved path.** `README.md`, `PROJECT-MASTER.md`, `ROADMAP.md`, `CONTRIBUTING.md`, `tools/*.py`, `tests/*.py` all reference docs by path.

**Report: files moved, links updated, and any link that pointed at something that no longer exists.** If a link is broken and the target genuinely should be gone, say so rather than inventing a replacement.

**One commit.** `git mv` throughout, so history follows the file.
