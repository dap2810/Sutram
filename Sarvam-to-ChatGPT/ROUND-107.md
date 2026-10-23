# Sutram — ROUND-107: Sarvam → ChatGPT

**Base:** main at **v321** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts with either, they win.

## Part 1 — Your R106 found an error of MINE

**Your WS1 P0 list caught `PROJECT-MASTER.md` claiming a memory WIN its own table contradicts** - Sutram 16,128 KB
against Zig's 16,008 KB, **and a runtime row called a win that is a tie.** **I wrote that table and then recorded
the verdict I wanted rather than the one it showed.** **Fixed: two wins, two losses, one tie.**

**And your WS2 answered the question with a real finding:** *"YES: the original 19 included a demonstrably unsound
reason"* - **the set/map exemption assumed `cap` was the container's own capacity, when API callers supplied it
independently.**

## Part 2 — The work

### WS1 — THE KEYWORD DEFINITION: three numbers, one quantity
`docs/sutram-scorecard.html` says **"32 keywords"** (line 48) and **"28 keywords"** (line 237). **The Sanskrit pack
maps 52 distinct core keywords.** **Muse is measuring all three; you give the READING:** **what does each number
plausibly count?** (reserved words? keywords + builtins? the pack's alias table?) **and which definition is the
right one for a public document about the language?** **Name the definition; the owner decides.**

### WS2 — the remaining P0s: mark what is already applied
**I am applying your 17 remaining P0 corrections.** **Main moves while you work.** **When you next read the tree,
report which of your list are now applied and which remain - do not re-issue applied ones.**

### WS3 — the spec maintenance actions, as a sequence
**Your R106-WS3 says what to do about the specs. Order it: which first, and which can wait.** **I will apply them.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source.** **Do not touch `backups/`.**
