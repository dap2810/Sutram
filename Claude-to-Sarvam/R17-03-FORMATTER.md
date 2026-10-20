# R17-03 — WS3: `sutram-fmt`

**`tools/sutram_fmt.py`, with `./sutram-fmt` as the command.** Python 3, nothing else. **The tree is not
reformatted:** 24 files would change, and the diff for each is in `evidence-r17/fmt-verify-tree.txt`'s OK
lines; the change itself waits for a round of its own, as you asked.

```sh
./sutram-fmt FILE...            # print, formatted
./sutram-fmt --write FILE...    # in place
./sutram-fmt --check FILE...    # exit 1 and name the files that would change (for a gate)
./sutram-fmt --diff FILE...
./sutram-fmt --verify FILE...   # the proof below, per file
```

## The style, and why

- **Four spaces** per level; no tabs; no trailing spaces; one newline at the end; at most one blank line in a
  row, none right after `{` or before `}`.
- **K&R braces:** `{` ends its header's line (`yadi (x) {`, `prakriya f(a) {`, `mukhya() {`); `}` starts
  its own line; `} anya {` and, after `kuru`, `} yavat (c)` are one line.
- **Spacing:** one space around binary operators and every `=`; none after unary `-` or `!`; none inside
  `( )` and `[ ]`; none before `,` `;` `।` `॥`; one after `,`. A keyword is followed by a space before its
  parenthesis (`yadi (`, `prati (`); a call, `mukhya()`, `abhava(...)` and `yantra(...)` are tight. `.`
  and the ternary's `? :` as in C; a `bhavana 1:` label keeps its colon tight.
- **Comments and strings are never changed.** A line comment is indented like code; an inline comment keeps
  its column (at least two spaces before it); a multi-line block comment is kept exactly.
- **Braceless bodies** (`prakriya f(a)` then `prati a`; a braceless `mukhya()`; `yadi (c)` then one
  statement) are indented one level. **Braces are not added:** that is a change to the program's text that
  a formatter should not make unasked.
- **`yoj` lines are kept exactly** (a module path is not an expression).
- **Everything else is kept:** the statements, their order, the line breaks between them, the words.

**Why this one:** it is the style 477 of the tree's 606 Sutram files already have exactly, and the books
teach; and it is C's, which every reader of Sutram has seen. The one open choice, where `{` goes, went to the
header line because that is what the tree does. **If the owner wants `{` on its own line, it is one rule.**

## What makes it safe

**The formatter moves whitespace and brace lines only.** It tokenises the program (names, numbers, strings,
operators, comments, the dandas) and writes the same tokens back in the same order with the rules above. So
the compiler sees the same program. **It refuses a file it is not sure of** (an unclosed string or block
comment, more `}` than `{`) and leaves it untouched, saying why.

**`--verify` proves it for a file, two ways:**

1. formatting the formatted file gives the same bytes (idempotent);
2. the file compiles to **byte-for-byte the same binary** before and after (a `.sm` is compiled where it
   lives, with the `--lang` the test runner uses for it; a `.smlib` through `yoj <module>` in a private copy
   of `lib/`).

| Set | Files | Result |
|---|---|---|
| **every `.sm` and `.smlib` in `examples/`, `lib/` and `tests/`** (not the negative corpora) | 606 | **477 UNCHANGED, 24 OK** (would change; same binary), **0 FAIL**, 3 UNSURE, 102 SAME-ERR |
| 150 programs from `fuzz_valid.py` with their whitespace scrambled (random spaces and tabs between every two tokens, `{` moved to its own line, blank lines inserted) | 150 | **150 OK**: each comes back compiling to the same binary as the original |
| 300 programs from `fuzz_valid.py` as generated | 300 | 300 UNCHANGED (the generator already writes this style) |

- **SAME-ERR** means the file does not compile before or after, with the same first diagnostic line: they are
  the deliberate negative fixtures (cycles, duplicates, pending cases, `tests/r4x_check`). Formatting cannot
  be proven on them by compiling, and they are not touched.
- **UNSURE (3):** `examples/221_eof_location.sm` (an unterminated string, on purpose),
  `tests/r48_check/unclosed_block.sm` and `tests/r51_check/nested_braces.sm` (unbalanced braces, on
  purpose). Left as they are, as designed.
- **The 24 that would change:** blank lines that hold spaces (7 examples), `likha(mahattam(12,8))` →
  `likha(mahattam(12, 8))` (10 `tests/stdlib` files), `}` then `anya {` on two lines → `} anya {`
  (`lib/brihat.smlib`, 3 places), a trailing blank run (`lib/sadhan.smlib`), a mis-indented line
  (`tests/stdlib/containers23.sm`), a missing final newline (`tests/stdlib/strconv_overflow.sm`), and an
  inline comment one space from the code instead of two (`examples/42_block_comments.sm`, the two
  `all_registers.sm`).

**`evidence-r17/fmt-every-rule-before.sm` → `fmt-every-rule-after.sm`** is one file that exercises every
rule above.

## What it does not do

- **It does not add braces, split or join statements, or wrap long lines.** Line length is not a rule.
- **It does not align comment columns across lines;** it keeps each line's own column.
- **It does not know the packs' keywords beyond `lang/*.lang`:** a pack word for `yadi` gets its space before
  `(`; an unknown word is formatted as a call. The program is the same either way.
- **A Windows build of the formatter:** none; it is Python, like every other tool in `tools/`. The compiler
  stays dependency-free.
- **A gate:** not added. `./sutram-fmt --check` on the tree would fail today (24 files). **Once the tree is
  reformatted, one line in `gates.sh` makes it a gate.**

## Checks

| Check | Environment | Result |
|---|---|---|
| `sutram_fmt.py --verify` on the 606 tree files | Linux | 0 FAIL (above) |
| the same on 150 whitespace-scrambled programs | Linux | 150 OK |
| the same on 300 generated programs | Linux | 300 UNCHANGED |
| Windows | — | NOT-RUN (the tool is Python; the compiler it calls is the Linux one) |
