# The images in this folder

## The IDE target — what to build

- **`sutram-idle-mockup.png`** — the light "Sutram Shell 1.0": menus (File, Edit, Shell, Debug, Options,
  Window, Help), a `>>>` REPL prompt, a status bar showing `Ln: / Col:` and `Sutram Shell - native x86-64`.
- **`sutram-idle-colour.png`** — the **colourful** version, and the one that matters most. It carries the
  colour-scheme legend along the bottom:

  | Role | Colour |
  |---|---|
  | keyword | orange |
  | builtin | teal |
  | function | yellow |
  | string | green |
  | number | purple |
  | comment | grey |
  | output | pale green |

  This is the owner's requirement made concrete: **"colourful, different colours per function"**.
- **`sutram-setup-mockup.png` / `.html`** — the installer wizard as it is meant to look.
- **`sutram-ide.html`** — the IDE design page.

**Treat these as the feel to aim for, not as pixel specifications to copy.** The owner's instruction is
explicit: it must feel like Python's IDLE but must **not** be a copy of it.

## Note the dash

In `sutram-idle-mockup.png` the version line reads `Sutram 1.0 (v29) – the complete thread` with a proper
en-dash. In the real Windows console it renders as `Sutram 1.0 (v29) ĞÖ the complete thread`. **The
mockup is right and the console is wrong.** That is the encoding bug to fix.

## The icons

`sutram-16/20/22/24/32/48/64/128/256/512/1024-master.png` and `sutram.ico` — the full icon set, usable
directly for shortcuts, the window icon and the installer.
