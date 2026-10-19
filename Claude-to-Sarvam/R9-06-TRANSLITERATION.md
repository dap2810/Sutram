# R9-06 — WS6: type Latin on an English (US) keyboard, get the script

**Commit `6f63fe36`.** This changes `windows/gui/sutram_gui.asm` and adds `windows/gui/r9_translit.asm`,
`windows/gui/r9_translit_data.inc` (generated), `tools/translit.py` and `tests/translit/`.

## What the owner gets

1. **Choose the language.** `Language` now lists **all eleven packs**: Auto, Core, sanskrit, then bengali,
   gujarati, hindi, kannada, malayalam, marathi, odia, punjabi, tamil and telugu.
   - Run (F5) passes `--lang <pack>`.
   - **Before, the IDE could only run Latin or Sanskrit:** a Tamil program typed into it failed with
     name errors.
2. **Press Ctrl+T**, or choose `Language > Type Latin, get the script`. The status line adds
   `lipi: <pack>`, and the menu item is ticked.
3. **Type on the English keyboard.** Each word converts when it ends, at a space, punctuation, Enter or
   Tab:
   - **A keyword becomes the pack's own word.** The table is the pack's `.lang` file, read at startup, so it
     always matches what `--lang` compiles. In Hindi, `vitti` becomes `चर` (the pack's word), not a spelling
     of "vitti".
   - **Any other word is spelled phonetically** in the pack's script: `yoga` becomes `योग`, and in Tamil
     `யோக`.
   - **Left alone:**
     - text inside `"strings"` and after `#` or `//`
     - a word glued to letters of another script
     - a word typed while text is selected
4. **Ctrl+Z undoes one conversion. Ctrl+T again turns it off.** It never opens Windows Settings and needs
   no IME.

When Language is Auto or Core, Ctrl+T writes Devanagari (the Sanskrit pack).

## The phonetic scheme, which is the part to learn

**Simple Harvard-Kyoto style, on the keys of a US keyboard:**

| Kind | Letters |
|---|---|
| vowels | `a aa/A i ii/I u uu/U Ri e ai o au` |
| consonants | `k kh g gh ~N · c/ch chh j jh ~n · T Th D Dh N · t th d dh n · p ph/f b bh m · y r l L v/w sh Sh s h` |
| conjunct | `x` or `kSh` = क्ष |
| signs | `M` (anusvara), `H` (visarga) |

**Rules:**

- Two consonants in a row join (virama between them): `mukhya` → मुख्य.
- **A final consonant keeps its virama, so type the vowel you want:** `kamala` → कमल, `yavat` → यवत्.
  What you type is what you get. There is no guessing at the inherent `a`.
- All nine scripts share one Unicode layout, so one table serves all of them.
- **Where a script has no such letter, the nearest one is used:**
  - aspirate → plain
  - voiced → unvoiced (Tamil)
  - ṣa → śa → sa (Gurmukhi)
  - Vocalic ṛ is dropped in Tamil.
  - The substitutions are computed from the Unicode database by `tools/translit.py`, not typed by hand.

## How big it is, and what it covers

**Size:**

- **The engine** (`r9_translit.asm`): about 150 lines of NASM.
- **Its data:** 57 Latin tokens and a 128-byte substitution row for each of the 11 packs, about 2 KB.
- **No external data table is needed.** The keyword half reuses the packs the IDE already loads.

| Covered | Not covered |
|---|---|
| every keyword of every pack (exact table lookup) | idiomatic spelling of ordinary words. Hindi `kamal` → कमल् (with virama) unless typed `kamala`; there is no schwa deletion. |
| identifiers, spelled phonetically, in all 11 packs | nukta letters (क़ ज़ फ़): `q`, `z` and `f` give क, ज and फ |
| digits, `_` and punctuation, kept as typed | native digits (the compiler takes ASCII digits) |
| undo, strings and comments left alone | conversion of text already typed or pasted (only the word at the caret, when it ends) |
| | the Linux X11 IDE (`ide/`): this round is Windows only |

## How it was tested

**1. The engine against the reference, on Linux.**

- `tests/translit/test_translit.py` assembles `r9_translit.asm` into a Linux harness.
- It feeds it every keyword of every pack, every token, every consonant–vowel pair and every
  consonant–consonant–a triple, for all 11 packs.
- It requires **byte-identical UTF-16** to `tools/translit.py`:

```
24761 cases (2251 words x 11 packs), 0 differ
```

**2. The whole IDE, under Wine 9.0 (not Windows).**

- `xdotool` typed on the X keyboard into the committed `sutram-ide-gui.exe`: chose the language, pressed
  Ctrl+T, typed the program, ran it with F5, and saved it.
- The program typed, character for character, was:

```
mukhya() {⏎vitti yoga = 3⏎yadi (yoga > 2) {⏎likha(yoga + 2)⏎likha("ok")⏎}⏎}
```

| Pack | Saved file (`evidence-r9/wine/ws6-typed-<pack>.sm`) | F5 in the IDE | `sutram_compiler --lang <pack>` on Linux |
|---|---|---|---|
| sanskrit | `मुख्य() {` / `वित्ति योग = 3` / `यदि (योग > 2) {` / `लिख(योग + 2)` / `लिख("ok")` | `5`, `ok` | `5 ok` |
| hindi | `मुख्य() {` / `चर योग = 3` / `यदि …` / `लिखो(योग + 2)` | `5`, `ok` | `5 ok` |
| tamil | `முதன்மை() {` / `மாறி யோக = 3` / `எனில் …` / `எழுது(யோக + 2)` | `5`, `ok` | `5 ok` |
| gujarati | `મુખ્ય() {` / `ચલ યોગ = 3` / `જો …` / `લખો(યોગ + 2)` | `5`, `ok` | `5 ok` |

- The screenshots are `wine/ws6-typed-*.png`.
- The string `"ok"` stayed Latin in all four files.

**3. Source-level tests** in `tests/gui/`: the menu ids, `--lang <pack>`, Ctrl+T, the Unicode
`EM_REPLACESEL` and the capacity. **35 / 35.**

**Not tested:**

- **Windows itself.**
- **A Windows IME or a non-US layout running at the same time.** The mode only acts on ASCII letters, so it
  should not interfere, but that is not verified.
- **The menu's native-script labels under Wine.** Wine's menu font has no Indic glyphs, so the labels show
  boxes there. Windows' menu font links to Nirmala UI.
