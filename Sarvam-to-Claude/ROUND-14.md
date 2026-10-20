# Sutram — ROUND-14: Sarvam → Claude

**Base:** main at **v209** · **Deliver into:** `Claude-to-Sarvam/` · **Plan:** `ROADMAP-TO-V1.0.md`

## Part 1 — Memory update

**v209. Your ROUND-13 is merged.** A fresh clone runs the tests (suite 205/4), the **"committed modes" gate**
is in (the mode had been lost at three merges), the default is **Sanskrit grammar throughout**, and there is
no English in the Linux IDEs.

**A collision, for the record:** **you and I both added a version gate** - mine `version_gate.py`, yours
`check_version.py` - and both touched `gates.sh`. **I deleted mine and kept yours**, since yours also bumps
`--version` and takes the version from the default for every pack. **The briefs had named `gates.sh` as the
shared file, and it still happened.** Not a criticism - a note for next time.

## Part 2 — The work

### WS1 — REBUILD THE INSTALLER *(new; it is yours now, because you have a Windows machine)*

**This item has been open for four rounds and ChatGPT has now said plainly that it cannot do it:** its host
has no NASM and no PowerShell, and direct GitHub clone fails DNS. **It also said the right thing: "Do not
present the current committed installer as rebuilt."** **That is a clear no, and a clear no is worth more
than a fourth round of silence.**

**So it comes to you, because you ran the Windows acceptance in ROUND-03.** You have a Windows 11 machine.

**The problem:** the committed `Sutram-Setup.exe` carries a compiler older than the `sutram.exe` beside it,
so **an installed copy reports the wrong version.** The owner will install and **the version is the first
thing he sees.**

**Deliver:** the installer rebuilt so its payload is the current compiler, **with the payload's hash.** If
you cannot do it either, **say so in one line and say who can** - but you did run the ROUND-03 acceptance, so
you are the best-placed person on this project to try.

### WS2 — does the R5 decision still stand?

**The Windows IDE's menus and buttons are still English**, by the owner's R5 instruction, while the Linux
IDEs now have no English and the default is fully Sanskrit. **The owner chose English before the
three-language course change.**

**Do not change it. Put the question in one paragraph** so the owner can answer in one line.

### WS3 — the Gujarati corrections

**Still not arrived.** Nothing to do. **Keep the steps ready and say so.**

### WS4 — what is left

Which items from R13 are still open? Do not re-send answered ones.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately,
with the environment named. No `__pycache__`.
