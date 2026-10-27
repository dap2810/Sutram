# Sutram ROUND-121 WS1 — two exact debugger-documentation insertions

**Read pin:** `7ef38a2fbfec33ba9d78dd62c5f5ae55ff3cce8c` (changelog v370, compiler v252). **Delivery:** [ROUND-121-WS1-DOC-INSERTIONS.tsv](ROUND-121-WS1-DOC-INSERTIONS.tsv), an exact-line, source-anchored UTF-8 TSV. No canonical docs or book files were edited in this round.

## Target and insertion points

| Target | Source blob | Anchor | Position | Insert lines |
|---|---|---|---|---:|
| `docs/LANGUAGE-REFERENCE.md` | `00f06311551de90714e00999d96fafdae8de9d17` | line **263** exactly `\| `sutram --version` \| version \|` | **AFTER** this line in the command-line section | **37** |
| `docs/sutram-book-sanskrit.html` | `b181c74f87543df7244624eae592d269d3b62862` | line **279** exactly the closing `Sanket: ...</code></pre>` error example | **AFTER** this line in chapter 12, before its closing `</div>` | **19** |

**Mechanical application:** Read TSV header and group by `file`. Check `anchor_exact` appears **exactly once** in the current file (abort on zero or multiple). Sort group by numeric `sequence`, replace `<BLANK>` with an empty output line, and insert those source lines directly AFTER the anchor. The `anchor_line_at_pin` is an extra receipt, **not** permission to insert at that line on a later tree where content moved. A source SHA mismatch must trigger a fresh exact-text read and review, not blind application. Preserve original newline style and UTF-8 bytes; do not interpret Markdown as HTML or convert HTML to Markdown. Do **not** apply twice; the new headings already present after the anchor should be treated as `ALREADY_APPLIED`.

## Current behavior explained in the proposed book/reference sections

- **Compile with the flag, then run the generated file**: `./sutram_compiler --debug demo.sm demo.bin` followed by `./demo.bin`. `--debug --lang sanskrit` syntax is supported when source uses the Sanskrit pack.
- The debug trace is emitted at runtime from code **in the compiled binary**. It prints `[shodhan] pankti N` and currently visible scalar locals/parameters **before** traced statements, then automatically continues.
- Trace uses the **same stdout as `likha`**, **not** a separate stderr/debug panel. The human-facing example intentionally labels the shown four output lines as an illustrative excerpt, not a complete exact transcript of the five-line program.
- **No interactive stepping, `s` / `c` commands, breakpoints or named watches** in v252. These were proposals in R120, not implemented features to document.
- The compiler's own `src/r45_debug.inc` explicitly excludes imported module statement bodies, `yantra` inline-machine-code stops, `mala`, `kosh`, slice inspection, globals, and no expansion of raw pointer contents.
- `--debug` off is a normal compiler run. Debug binaries are larger and can flood stdout in loops; do not use for normal production output, benchmarking, or publishing potentially sensitive scalar values.

## Direct source and partner-reported receipts

`src/r45_debug.inc` Git blob `544db02c2141107e7254441b27565ad4ac6dec88`, exact introductory comments and `r45_gen_trap`; `src/sutram_compiler.asm` Git blob `3df625fe6d38e4529bfd6181afa54b71fa5a756e`, `:2207-2240` flag routing. The fresh-clone debugger output and normal-build contrast come from `docs/CHANGELOG.md` v370, reported by **Sarvam**, not retested by ChatGPT.

**STATUS:** PASS — 2 unique exact insertion anchors inspected on pinned source; 56 non-destructive insert lines provided. **NOT APPLIED** — authorized docs owner must insert. **NOT RUN - no toolchain** — native debugger, complete example, Windows, regressions. The guide is documentation, not a compiler change.
