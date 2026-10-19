# R10-04 — WS4: what the typing mode does NOT cover, and what extending it would cost

**Nothing was extended.** This is the list, with a cost for each, so you can choose.

## What it covers today (R9-06)

- **Keywords:** in the selected pack, every keyword typed in Latin becomes that pack's own word (from
  `lang/<pack>.lang`). `vitti` becomes `चर` in Hindi.
- **Identifiers:** yes, phonetically, in all 11 packs. `yoga` becomes `योग` (Devanagari) or `யோக`
  (Tamil). The same Latin spelling always gives the same name, so a program stays consistent.
- **Words end** at a space, punctuation, Enter or Tab. Ctrl+Z undoes one conversion.

## What it does not cover

| Not covered | Today | To extend | Cost |
|---|---|---|---|
| **Text inside `"strings"`** | left in Latin, on purpose | a second toggle (or Ctrl+Shift+T) that also converts inside strings, so messages can be typed in the script | **cheap:** about 10 lines; the string check already exists |
| **Comments (`#`, `//`)** | left in Latin, on purpose | the same switch as strings | **cheap:** shares the change above |
| **Text already typed or pasted** | only the word at the caret, when it ends | a "Convert selection" command: run the engine over each Latin word in the selection | **moderate:** about 60 lines, plus a menu item |
| **Native digits** (०१२…) | ASCII digits stay ASCII | convert digits too; the compiler already reads Indic numerals (R66) | **cheap:** a 10-entry offset per script, about 15 lines; on by choice only, since ASCII digits work everywhere |
| **Hindi-style spelling** (`kamal` → कमल, not कमल्) | what you type is what you get; the final virama is kept | drop a final virama for hindi, marathi and the other non-Sanskrit packs | **cheap to do, but it is guessing:** it is right for most nouns and wrong for some words; I would not do it without your say |
| **Nukta letters** (क़ ज़ फ़) | `q`, `z` and `f` give क, ज and फ | map them to consonant + nukta (U+093C and equivalents) where the script has one | **cheap:** data only, in `tools/translit.py`; regenerate |
| **The Linux X11 IDE** (`ide/`) | not covered; Windows only | port the engine (it is ABI-neutral NASM) and the hooks | **moderate to large:** the X11 editor has its own input path |
| **Reading back** (script → Latin) | not covered | show the Latin spelling of the word at the caret, in the status line | moderate; probably not needed |

## My suggestion, if you want any of it

**Strings and comments as an option, native digits as an option, and nukta.** All three are cheap:

- each is a few lines or data only
- each is testable with the existing engine-against-reference test

**Leave Hindi-style spelling alone** unless the owner asks: predictability matters more to a beginner.

**Say which, and I will do them in one round.**
