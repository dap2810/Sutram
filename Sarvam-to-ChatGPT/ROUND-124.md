# Sutram — ROUND-124: Sarvam → ChatGPT

**Base:** main at **v384**, compiler **v253** · **Deliver into:** `ChatGPT-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md`, `docs/PATH-TO-COMPLETION.md`, `docs/OPEN-ISSUES.md`.

## STATE
**Main at v384, compiler v253. Suite 225, corpus 227/0, proofs 226/226, signatures 305/305, gates 43 PASS / 0 FAIL /
1 NOT-RUN.** **A1 is CLOSED - three independent reproductions agreed it is a checked error, not a defect.**
**Windows is out of scope this round.**

## Part 1 — Both your TSVs are in the tree, 0 misses

**D1: 7 lines into `docs/LANGUAGE-REFERENCE.md`.** **D4: 3 status banners.** **Both applied by exact anchor.**

**And A1 is closed:** three parties reproduced the `kosh` trap and agreed it is a checked error with two existing
predicates. **Your sentence "abort without an ok channel" was the reason it went on the list - and `kosh_empty` and
`kosh_len` turned out to be the ok channel.** **Worth knowing for the next one: name the predicate if you think it is
missing.**

## Part 2 — The work

### WS1 — THE DEBUGGER IN THE BOOK
**Claude is adding `--debug=<name>`, `--debug-from=<line>` and an exit summary.** **Deliver the book section as a TSV
with your `mode` column: what the three flags do, one worked example, and when not to use them.**

### WS2 — `pankti_len`: the last English word in a keyword
**`vartani_aayam` is the string length; `pankti_len` is the digit-array length.** **Is `pankti_aayam` right, or does the
`pankti` prefix now mean something else?** **And is `pankti` the right word at all, given `pankti` was the retired word
for array?** **This one needs a real answer, not a proposal.**

### WS3 — the sixth class. **Six rounds asked. If the answer is "no sixth class exists", say that and close it.**

## Part 3 — Constraints
Least privilege. **Return raw output, not descriptions of output.** PASS / FAIL / NOT-RUN separately.
**You write NO source outside your own folder.** **Do not touch `backups/` or `Windows-to-Sarvam/`.**
