# R11-01 — WS1: the diagnostics follow the language pack (option E)

**Branch `claude/round-11`, commit `15fa8176`, draft PR #46.** Base: main `d3325b13` (v201). Every source
file was read from that commit before it was changed.

## What it does now

| How it is run | Messages |
|---|---|
| `sutram prog.sm out.bin`, no `--lang` | the **romanised Sanskrit default**, as before, with its English words removed |
| `sutram --lang sanskrit …` | **Sanskrit in Devanagari** (new: before R11 this gave the romanised default) |
| `sutram --lang hindi …`, and the nine others | **that language, in its own script** |
| the Windows IDE | the pack its next run passes: the chosen pack. Auto gives the detected pack; Core gives the default. |

**What changes with the pack:**

- every compiler message
- the program's own run-time errors (an index past the end, `kosh_pop` on an empty kosh, the `trap`
  build's overflow messages): they are chosen at compile time, so they follow `--lang`
- the IDE's status line and its output-pane messages

**What stays the same in every pack:**

- `Sutram Error` and the `[E_CODE]` tags, as you asked
- names, numbers, the source line and the caret
- the pack name the compiler echoes (`hindi`), because it is the `--lang` argument

**English: none, in any pack, as a default or as a fallback.**

- A pack that lacked a message would print the romanised Sanskrit default for it, never English.
- `--check` refuses an incomplete pack, so that cannot ship.

## All eleven packs are complete

| Pack | Compiler messages | IDE messages | New goldens | Existing goldens moved |
|---|---|---|---|---|
| default (romanised Sanskrit) | 105 (23 edited: English removed) | 23 (4 edited) | 11 | **11** (`tests/expect`) |
| **sanskrit** (Devanagari) | **105 / 105** | **23 / 23** | 11 | **1** R70 case · 2 checks in `tools/test_windows_gui.py` |
| **hindi** | **105 / 105** | **23 / 23** | 11 | **1** (`220_hindi_parse_error`) |
| marathi | 105 / 105 | 23 / 23 | 11 | 0 |
| gujarati | 105 / 105 | 23 / 23 | 11 | 0 |
| bengali | 105 / 105 | 23 / 23 | 11 | 0 |
| punjabi | 105 / 105 | 23 / 23 | 11 | 0 |
| odia | 105 / 105 | 23 / 23 | 11 | 0 |
| tamil | 105 / 105 | 23 / 23 | 11 | 0 |
| telugu | 105 / 105 | 23 / 23 | 11 | 0 |
| kannada | 105 / 105 | 23 / 23 | 11 | 0 |
| malayalam | 105 / 105 | 23 / 23 | 11 | 0 |
| **total** | **1,155** | **253** | **132** | **13** goldens · 2 Windows checks |

**What the counts are:**

- **The 105** are every message the compiler can print. Fragments that are only punctuation or an
  identifier (`'\n`, `: Sutram Error [`) are not counted: there is nothing in them to translate.
- **The 23 in the IDE:**
  - the status line: `pankti`, `stambh`, `bhasha`, `akshara`, `lipi`, `sanchit`, `asanchit`, the find
    result, and `swayam` / `mool`
  - 12 output-pane messages
  - The status line now shows **each language's own name** (`भाषा: हिन्दी`, not `bhasha: hindi`).
- **The menus and buttons are unchanged:** they are English by the owner's R5 decision, which is not a
  diagnostic. Say if that decision should change too.
- **All 11 packs are complete,** so there was no need to stop in pack order.

**Every moved golden moves by exactly the intended words:**

- In `tests/expect`: 11 by the English words below, and the Hindi parse golden. The Hindi golden now
  starts with `Sutram Error:`, which the old v27 Hindi text did not have.
- The R70 `misplaced_keyword` case: it runs under `--lang sanskrit`, so its expected text is now the
  Sanskrit pack's.
- **No accepted golden was re-recorded to make a failing test pass.** Each diff is in
  `evidence-r11/logs/goldens-moved.txt`.

## The romanised default: English out, nothing else

**Removed from the default text:**

| Was | Now | Where |
|---|---|---|
| `module` | `ghatak` | 14 module-system messages (R34–R56) |
| `byte` | `baait` (the Sanskrit book's बाइट्, romanised) | `Siddh: N baait sankalit`, the alias-length message |
| `OK`, `binary` | `shuddh`, `patra` | `--check` |
| `folder` | `nirdeshika` | the missing-module hint |
| `AST`, `data`, `yantra-code` | `vakya-vriksh`, `mulya`, `yantra-bhasha` | three limit messages, `--version` |
| `Ready. Run (F5) compiles…`, `shell history is full…`, `pipe`, `Latin shabda` | romanised equivalents | the IDE's output pane |
| `Windows API load` | `Windows ke karya-sutra` | the IDE's start-up error box (ANSI, shown before any pack is known) |
| `Error: parse error at token` (never printed) and an orphan `Run 'sutram -i' and type 'sahayata' for help.` | **deleted** | compiler data |

**One existing bug fixed on the way:** the shell help printed `likha("Namaste` on one line and `")` on
the next, because the string was a NASM backtick string (it turned `\n` into a newline).

**Kept on purpose:**

- `Sutram Error` and the `[E_CODE]` tags (your rule)
- file names and flags (`lib/`, `naam.smlib`, `--lang`)
- `UTF-8` and `x86-64`
- the key labels `Enter` and `F5`
- The shell still **accepts** `exit`, `quit` and `help` as input. They are input aliases, not messages.
  Say if they should go.

## A decision for you: the default's grammar

**The romanised default is Sanskrit vocabulary with Hindi grammar in about 15 messages:**

- **Examples:** `' pahle se ghoshit hai; naya man dene ke liye:`, `utne hi tark dein jitne…`,
  `… hona chahiye`, `se`, `me`, `nahi`
- **I did not rewrite them.** That changes 30-odd more goldens, the ChatGPT acceptance tools that quote
  them, and the books.
- **The Devanagari `--lang sanskrit` set is written in Sanskrit grammar** (`पूर्वमेव घोषितम्`, …). So
  Sanskrit as grammar already exists, under `--lang sanskrit`.
- **The IDE passes `--lang sanskrit`** as soon as Auto sees Devanagari.
- **Say if the no-`--lang` default should be the same Sanskrit, romanised.** It is one round's work:
  generate it from the Devanagari set and re-record.

## The translations need a native speaker. All eleven, Sanskrit and Hindi included.

**I wrote them.** The checks below prove the form, not the wording. My own confidence, roughly:

| Confidence | Packs |
|---|---|
| Highest | Hindi, Sanskrit, Marathi |
| Then | Gujarati, Bengali, Punjabi |
| Lower | Odia, Tamil, Telugu, Kannada, Malayalam |

**Loanwords, written in each pack's own script:**

- **Where that language's computing usage has them, I used them:**
  - **byte** (बाइट, as the Sanskrit book has it), **pack** (पैक) and **second** (सेकंड): in every pack
    except Tamil, which has native words for the second and the pack
  - **file:** a loan in Hindi, Marathi, Gujarati, Bengali, Punjabi, Odia and Malayalam (फ़ाइल / ফাইল / ഫയൽ …)
  - **module:** a loan in Hindi (मॉड्यूल, as the Hindi book has it), Bengali, Punjabi and Odia
- **Otherwise, a native term:**
  - **file:** Sanskrit पत्रम्, Tamil கோப்பு, Telugu దస్త్రం, Kannada ಕಡತ
  - **module:** "component" or "part" in Sanskrit, Marathi, Gujarati and Kannada (घटक / ઘટક / ಘಟಕ),
    Malayalam (ഘടകം), Tamil (கூறு) and Telugu (భాగం)
- **The packs' own keywords are used as the words for their concepts.** The function is फलन / कार्य /
  செயல், as each pack spells `prakriya`.
- **A hint that shows code shows the pack's keyword:** `चर y = ...` in Hindi, `மாறி y = ...` in Tamil.
  It comes from `lang/<pack>.lang` through `{kw:vitti}`, so it cannot drift from the pack.
- **Each entry in a `.sandesh` file has the default above it as a comment,** for the reviewer.

## How it works

- **`lang/<pack>.sandesh`**, eleven files: `key<TAB>"text"`. The key is the compiler's label for the
  message.
- **`tools/sandesh.py --write`** generates two files:
  - `src/r11_sandesh.inc` (1,155 strings)
  - `windows/gui/r11_ide_sandesh.inc` (253 strings, and each language's own name)
- **The compiler: one lookup, `r11_tr`,** by the message's address:
  - from `print_str_z`, which every message goes through
  - and from the three places that put a message into the program (the bounds check, the empty-kosh
    checks, the R65 trap messages)
  - **No print site names a language,** and a new message needs one key and no code.
  - The five v27 per-pack messages are folded in, and their tables are gone.
- **Selecting the pack:**
  - `--lang <pack>` selects the messages as soon as the pack is named, so the "pack not found"
    warning is in that language too.
  - `sanskrit` is now pack id 11.
- **The IDE: the same lookup** (`r11_ide_tr`):
  - for the status line, and through `output_append` for its messages
  - "Clear shell" now goes through it too (it used `SetWindowTextA`)
  - **The status line takes the Nirmala UI face** when its language is Indic and the face is installed
    (R9's check). Segoe UI had no Indic glyphs under Wine.
- **Size:**
  - the Linux compiler: 202,320 → 353,368 bytes
  - `win/sutram.exe`: 188,318 → 335,547 bytes
  - the IDE: 110,344 → 140,948 bytes
  - The cost is the 1,408 strings, most of them three-byte UTF-8.
- **The reference, for whoever edits a pack:** `docs/SANDESH.md`.

## The checks

**Mechanical, on every entry of every pack** (`tools/sandesh.py --check`, in `tests/sandesh/` and in a
new gate, "pack messages"):

- `Sutram Error` and the `[E_CODE]` tags are present and unchanged
- the punctuation at both ends is kept: the opening quote the compiler closes after the name, the
  newlines, the IDE's brackets
- every Latin word is code the default also has, so English cannot enter through a translation
- every other letter is in the pack's own script
- every pack has every key, and both generated files are current
- none of the removed English words may return to a default

**The checker's own test:** it must refuse each of these:

- an English word
- a dropped tag
- a translated `Sutram Error`
- a dropped quote
- a Tamil word in the Hindi pack

**Goldens:** `tests/sandesh/` compiles nine programs (and runs the two `--check` cases) for the default
and each pack: **132 goldens.** Each program raises one of:

- undefined name
- parse error
- arity
- duplicate
- unknown field
- missing module
- out of bounds, at run time
- empty kosh, at run time
- or none

| Check | Environment | Result |
|---|---|---|
| suite, proof_lib, proof_props, pack messages, translit, tests/gui | Linux, **fresh clone** | **205/4** · 217 · 86/86 · OK · 24,761/0 · 35 OK |
| R70 corpus · `r69_build.py --check-only` · every `r69_build` mode | Linux | **6/6** · SOURCE_PINS_CHECKED · default, peepholes, trap, combined, pairs and windows build |
| `tests/r70` | Linux | **now OK** (it failed on main; see R11-03) |
| `tests/r66 r67 r68 r72 module_graph ci windows_accept r65_finish` | Linux | OK |
| `tests/r69` | Linux | 2 FAIL, the same two as on main (ChatGPT's) |
| `gates.sh` | Linux | **PASS 10 / FAIL 1 / NOT-RUN 1**. FAIL: the pre-existing X11 `edscroll` timeout. NOT-RUN: Windows. |
| the `trap` build, overflow under `--lang hindi` | Linux | `Sutram Error [E_INTEGER_TRAP] …:3: जोड़ में अतिप्रवाह` |
| `win/sutram.exe` with no `--lang`, and with sanskrit, hindi and tamil, a compile error and a run-time error | **Wine 9.0** | each in its language (`evidence-r11/wine/wine-compiler.txt`) |
| the IDE: Hindi, Tamil, Core, Sanskrit by Auto, a run-time error, then Clear shell | **Wine 9.0** | status line and output pane in the pack's language (`evidence-r11/wine/*.png`). The Wine prefix's "Nirmala UI" is a stand-in font. |
| `cross_build_windows.py --check` | Linux | **MATCH** for both compilers and the IDE; DIFFERS for `Sutram-Setup.exe` only |
| Windows | — | **NOT-RUN** |

**Locks:**

- The compiler is re-pinned `5ade34ed` → `8625095a` in `r69_build.py` and its lock, in the R70
  manifest, and in `docs/BUILDING.md` and `NEGATIVE-CORPUS.md`.
- `src/r11_sandesh.inc` is pinned with it: `r69_build` refuses an unlocked include.
- The reason is in each lock's `repinned` text.

**In `windows/`:**

- **Touched:** `windows/gui/sutram_gui.asm` (the lookup, the status face, Clear shell, five default
  strings) and the new generated `windows/gui/r11_ide_sandesh.inc`.
- **Not touched:** the installer and the wizard, and **`Sutram-Setup.exe`**, which is ChatGPT's.
- **The setup must be rebuilt after this merges.** Its payload will then also carry the eleven
  `.sandesh` files. That is harmless: nothing reads them at run time.
