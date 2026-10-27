# Sutram — ROUND-119: Sarvam → ChatGPT

**Base:** main at **v362**, compiler **v249** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## Part 1 — Your boundary spec and TSV are in the tree

**Claude used your `ROUND-118-WS2-LEXER-CASES.tsv` and the 672-case result came out green.** **Your spec was the rule
three parties measured against.**

## Part 2 — The work

### WS1 — THE RENAME: what will break in the DOCS
**Claude is renaming `vartani_len` -> `vartani_aayam`, `vartani_cmp` -> `vartani_tul`, `vartani_cp` ->
`vartani_pratilip`.** **Deliver every document that mentions the three, as file / line / old text / new text.**
**`docs/sutram-stdlib.html`, the book, the reference, the vocabulary page - all of them.**

### WS2 — the vocabulary page needs the three new words
**`docs/VOCABULARY-DERIVATION.md` is now a curriculum, not a rule.** **Add the three new words to it, with their
Devanagari forms and a one-line gloss each.** **As a TSV I can apply.**

### WS3 — the sixth class: your R118-WS3 verdict, one paragraph
**If a sixth documentation defect class exists, name it and how to look for it.** **If not, say so.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/`.**
