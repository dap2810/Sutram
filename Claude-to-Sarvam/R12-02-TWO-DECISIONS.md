# R12-02 — WS2: the two decisions, with their costs

**Nothing was changed for either.** Each can be answered in one line.

## A correction of my own first

**In R11 I wrote that "about 15" default messages use Hindi grammar. That was an undercount.**

- **The real count:** a scan for Hindi function words (`se`, `me`, `hai`, `nahi`, `ke liye`, `ko`, `dein`,
  `dekho`, `chahiye` and others) finds **42**: 31 in the compiler and 11 in the IDE.
- **Some carry one word** (`rikta kosh se kosh_pop`), **others a whole Hindi sentence**
  (`utne hi tark dein jitne prakriya ki paribhasha me hain`).
- **The list:** `evidence-r12/default-hindi-grammar.json`.

## Decision 1: should the romanised default (no `--lang`) use Sanskrit grammar?

**Today:**

- **The default is Sanskrit vocabulary with Hindi grammar** in 42 messages.
- **`--lang sanskrit` is already Sanskrit in grammar, in Devanagari,** and the IDE passes it as soon as
  Auto sees Devanagari.
- **So the question is only what a user sees without `--lang`.**

| Option | What it means | Cost |
|---|---|---|
| **A. Keep as it is** | the default stays as the project has had it since before R1 | nothing |
| **B. Sanskrit grammar, romanised** | generate the default from the Devanagari Sanskrit set, romanised in the project's plain ASCII style (`agyatam nama`, not `agyat naam`). The default and `--lang sanskrit` then say the same thing. | **about one round.** 42 default messages change, and with them the tests below. |

**What option B moves, measured on main `068afb26`:**

| What | How many |
|---|---|
| goldens in `tests/expect` | **17** |
| default goldens in `tests/sandesh/expect` | 9 |
| R70 corpus expectations | 3 cases, in one manifest |
| tests and tools that quote the text | `tests/r68/test_r68.py`, `tools/r48_stage2_acceptance.py`, `tools/r64_source_gate.py`, `tools/r68_native_acceptance.py` |
| docs | 10: the six books, the two kosh docs, `NEGATIVE-CORPUS.md`, `CHANGELOG.md`; and `windows/gui/MANUAL-WINDOWS-GUI-TEST.md` |
| pinned files | `src/r68_diagnostics.inc` holds 2 of the 42 (`r68_utf8_tail`, `r68_value_tail`). It is pinned by ChatGPT's tools, so it must be re-pinned too. |

**Two risks with B:**

1. **The romanised Sanskrit set inherits every wording doubt of the Sanskrit sheet** (R12-01),
   unreviewed. Doing B before the Sanskrit review means doing it twice.
2. **Users who learned the old text must relearn it.** The text is all that changes: the `[E_CODE]`
   tags stay, so scripts that match on them keep working.

**My suggestion:** B, but after the Sanskrit review sheet comes back, so the romanised default is made
from reviewed text once.

**One line for the owner:** "A: keep" · "B: Sanskrit grammar, after the Sanskrit review" · "B now".

## Decision 2: should the Linux IDEs follow the pack?

**There are two Linux IDEs, and they are in very different states:**

| IDE | What it shows today | Can it show Indic script? |
|---|---|---|
| **terminal IDE** (`ide/sutram_ide.asm`) | **English:** `Sutram IDE - the complete thread`, `Output`, `[modified]`, `Shell`, and the key help `Ctrl-R Run … Ctrl-Q Quit`. It runs the compiler without `--lang`. | **Yes,** if the terminal's font has the script. The terminal shapes the text, not the IDE. |
| **X11 GUI** (`ide/sutram_gui_linux.asm`) | **Romanised Sanskrit** labels (`patra`, `sampad`, `anwesh:` …). But five console messages are **English** (`Sutram GUI: connected to X, window created.`, `cannot open that file`, …), and the About text has `yantra-code`. | **No.** It speaks the raw X11 protocol and draws with `ImageText8`, 8-bit core fonts: no Devanagari or any other Indic script, and no shaping. |

**The options, cheapest first:**

| Option | What it means | Cost |
|---|---|---|
| **A. No English, no packs** | replace the English in both Linux IDEs with romanised Sanskrit, about 12 strings | **small:** part of a round. Some `tools/test_x11_*.py` may read the console lines. |
| **B. The terminal IDE follows the pack** | a pack setting, `--lang` passed to the compiler, and its ~7 strings in each pack through the same `.sandesh` files and generator | **about one round.** The full-screen layout counts columns, and Indic text is wider in bytes than on screen, so the status-line layout needs work and testing in real terminals. |
| **C. The X11 GUI follows the pack too** | a Unicode text path in a raw-protocol X11 client: either the X Render extension with glyphs it rasterises itself, or ISO 10646 core fonts with `ImageText16`. The latter gives no conjunct shaping, so Devanagari and Tamil would render wrongly. | **large: several rounds.** It is the X11 equivalent of a text engine. **I would not start it before v1.0.** |

**My suggestion:** **A now** (the "no English" rule should hold in every IDE). **B** if Linux users matter
before v1.0. **Not C** before v1.0.

**One line for the owner:** "A" · "A + B" · "A + B + C".
