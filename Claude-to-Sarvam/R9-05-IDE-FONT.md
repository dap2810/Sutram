# R9-05 — WS5: the IDE's font for the eleven scripts

**Commit `6f63fe36`.** This changes `windows/gui/sutram_gui.asm`; `windows/gui/` is shared, see R9-08.

## What changed

**Before:** the editor and the output asked for `Consolas`, which has no glyph in any of the nine Indic
scripts. They showed only through Windows' per-glyph fallback.

**Now:**

- After each highlight pass, the editor applies **`Nirmala UI`** (the face Windows 10 and 11 ship for all
  of them) to every run of Indic text: U+0900–U+0DFF, plus ZWJ and ZWNJ.
- **Latin stays `Consolas`,** so code still lines up in columns.
- **The output pane gets the same treatment** after each run.
- **The face is used only if Windows really has it.** At startup the IDE creates the font, selects it into
  a screen DC, and reads back the face Windows chose (`GetTextFaceW`). If that is not exactly
  `Nirmala UI`, nothing is forced, and Windows' own fallback stays as it was.

**Fixed on the way:**

- **After a run, the output pane's text was dark grey on the dark background.** RichEdit gives replaced text
  the default colour. The v188 IDE does the same under Wine, so it is not new. The output colour is now
  re-applied after every run.
- **The keyword table held 384 entries, but the eleven packs have 392,** so the last 8 Telugu keywords were
  never highlighted. It now holds 512.
  - The GUI test that pinned `384` now pins `512`.
  - I added a test that the capacity holds every pack entry, which would have failed on v188.

## How it was tested: rendering the same text in all eleven packs

**The test file:** `evidence-r9/eleven.sm` has one line per pack, with `mukhya`, `likha` and `yadi` in that
pack's own words.

**The setup:**

- **Wine has no Nirmala UI.** So I built a **stand-in font named "Nirmala UI"** by merging the nine Noto Sans
  Indic fonts with fontTools.
- I registered it in the Wine prefix and ran the committed v188 IDE and the branch's IDE on the same file.

| Screenshot (Wine 9.0) | IDE | Result |
|---|---|---|
| `wine/ws5-v188-ide-standin-font.png` | main's `sutram-ide-gui.exe` | **empty boxes on every Indic line, all eleven** |
| `wine/ws5-new-ide-standin-font.png` | this branch's | **letters on every line: Devanagari (sanskrit, hindi, marathi), Bengali, Gujarati, Kannada, Malayalam, Odia, Gurmukhi, Tamil, Telugu** |

**What this shows:** the IDE asks for the face, finds it, and applies it to every Indic run.

**What it does not show:**

- **How real Nirmala UI looks on Windows.** The stand-in is Noto's glyphs, and Wine's shaping of conjuncts is
  imperfect: some Odia and Kannada vowel signs sit wrongly in the screenshot. That is Wine plus a merged
  font, and should not be read as the IDE's behaviour on Windows.
- **Windows: NOT-RUN.** The owner's test is the real one. `windows/gui/MANUAL-WINDOWS-GUI-TEST.md` items
  29–31 say what to look for.

## Known limit, not fixed: the line-number gutter drifts on Indic lines

**The defect:**

- Indic lines are taller than Consolas lines, and the gutter is a plain EDIT control in Consolas.
- So on a file with many Indic lines, the numbers fall behind the text. The screenshots show it.

**This is not new:** Windows' own fallback to a taller Indic font did the same in v188.

**Two fixes I tried, and why I left them out:**

- **Exact line spacing** (`PFM_LINESPACING`): Wine ignored it, so I could not verify it.
- **Shrinking the Indic text** to Consolas' line height: verified, but the letters became too small to read.

**The real fix:** paint the gutter numbers at each line's actual position (`EM_POSFROMCHAR`). That is a
small, contained change for a later round, if the owner's test shows the drift matters.
