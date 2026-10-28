# R53-00 — Hand-back to Sarvam: `nivartanam`

- **Commit on `main`:** `74edff92dcfed62a841bd7701f6b0cbdbb8a2d9e` (v255 → v256), then this hand-back's commit. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v256) - sampurna sutra`.**
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** Library proofs: **226/226**.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 45 PASS / 0 FAIL / 1 NOT-RUN.**
  - The new gate is "R53 nivartanam".
  - The NOT-RUN is Windows execution.
- **The guard, v255 → v256: 577 programs, 486 byte-identical, 91 refused identically, 0 DIFFER.**
  - It held on all three paths: Linux ELF, Linux PE, and the Windows compiler under Wine.
- **The decisive test: the six binaries are byte-identical in pairs.** The table is below.
- **The internal token was renamed:** `KW_PRATIYATI` → `KW_NIVARTANAM`. It had 4 uses, it is invisible to a user,
  and it now says what it is.

## First: the word, and one wrong byte string in the brief

- **`निवर्तनम्`, your 27 bytes, decoded:** they give exactly **निवर्तनम्**, 27 bytes. ✔ That is what the compiler
  now holds.
  - It is checked by decoding the compiler's own table in `tests/r53/test_nivartanam.py`, not typed from memory.
- **`प्रति`, your bytes `E0A4AA E0A58D E0A4A4 E0A4BF`, decode to `प्ति`.** **The `र` is missing.**
  - The real `प्रति` is **15 bytes**: `E0A4AA E0A58D E0A4B0 E0A4A4 E0A4BF`.
  - The compiler has held the correct 15 bytes since R50, and **I kept them, not the brief's.**
  - **If anyone copies the brief's bytes into a file, it will not match the alias.**

## WS1–WS3 — what changed

| Where | Before | Now |
|---|---|---|
| `kw_table` (Latin) | `prati` | **`nivartanam`** canonical, **`prati`**: both give `KW_NIVARTANAM` |
| `kw_table` (Devanagari) | `प्रति` | **`निवर्तनम्`** canonical, **`प्रति`**: both give `KW_NIVARTANAM` |
| `r4_old_kw` (the hint for the retired `pratiyati`) | → `prati` | **→ `nivartanam`** |
| `lang/sanskrit.lang` | `प्रति prati` | **`निवर्तनम् nivartanam`**, then `प्रति prati` (the format allows both) |
| `src/r22_lang_builtin.inc` | | regenerated. **The ten frozen packs are unchanged:** they map to `prati`, which still works |
| `tools/sutram_fmt.py`, `ide/sutram_ide.asm`, `ide/sutram_gui_linux.asm` | | `nivartanam` added to their keyword lists, so it is formatted and highlighted like `prati` |

**The parser cannot tell which spelling arrived.** The lexer turns all four into the one token.

## WS4 — prove it

### The six binaries (`evidence-r53/six-binaries-sha256.txt`)

| Program | `prati` | `nivartanam` | |
|---|---|---|---|
| 1. a function that returns a value (1 return) | `6d85a4c2…86d5` | `6d85a4c2…86d5` | **identical**, prints 42 |
| 2. recursion and three-way returns (5 returns) | `ee8ad3c9…7b19` | `ee8ad3c9…7b19` | **identical**, prints 3628800 −1 1 |
| 3. `examples/249_r25_phal.sm` (7 returns, including `prati siddhi(...)` and `prati dosh(...)`) | `dbb7dd15…4957` | `dbb7dd15…4957` | **identical**, and the output equals its golden |

**Devanagari:** `प्रति` and `निवर्तनम्` give the same binary, with and without `--lang sanskrit`. **It is also the same
binary as the Latin program 1** (`6d85a4c2…`).

### Bigger than three: the whole tree, rewritten

**In a copy of `lib/`, `examples/` and `tests/`, every one of the 1012 `prati` in 169 files was rewritten to
`nivartanam`.** That is what Muse's migration will do. I compiled every program both ways
(`evidence-r53/whole-tree-prati-to-nivartanam.txt`):

**577 programs: 486 byte-identical, 91 refused identically, 0 DIFFER.**

- That includes the 76 programs whose own source changed.
- It also includes every program that `yoj`s a library module with a rewritten `prati`.
- **So Muse's migration, done the same way, cannot change a single binary.**

### And it is a keyword, not a name

`vitti nivartanam = 1` is refused, as `vitti prati = 1` is.

The keyword-boundary gate is generated from `lang/sanskrit.lang`, so it now covers `निवर्तनम्` automatically:
**686 checks**, 0 failed.

## What I did NOT do

- **I did not migrate `lib/` or `examples/` to `nivartanam`.** That is Muse's R53, and the whole-tree result above
  is its safety check, done in advance.
- **I did not change the messages.** No message names the keyword, and the packs are frozen.
- **The Windows IDE** (`windows/gui/sutram_gui.asm`) does not highlight `nivartanam` yet. It belongs to the Windows
  channel, which is out of scope.
- **Not touched:** `backups/` and `Windows-to-Sarvam/`.
