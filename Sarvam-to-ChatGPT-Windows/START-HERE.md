# Sutram — one archive, everything inside

**ChatGPT: open this folder and read `for-chatgpt/INSTRUCTIONS-FOR-CHATGPT.md` first.** That is the brief.
It has ten sections and ends with exactly how to package your return.

## What is in this archive

| File | What it is |
|---|---|
| `for-chatgpt/INSTRUCTIONS-FOR-CHATGPT.md` | **the brief** — build the Windows installer and the IDE |
| `sutram-complete.zip` | the **complete project** — source, docs, images, history, mockups |
| `sutram-windows-test.zip` | the **Windows binaries**, ready to run, with a test script |

## What you are being asked for

One `.exe`. A user on Windows runs it and ends up with the Sutram language installed and a working IDE —
**no toolchain, no admin rights, nothing to configure.**

The IDE must **feel like Python's IDLE but not be a copy of it**, and must be **colourful with a distinct
colour per language element**. The colour scheme the owner wants is in
`sutram-complete.zip → images/README-IMAGES.md`, with the mockups beside it.

## Inside `sutram-complete.zip`

```
project/    the full source tree — compiler, IDE, library, packs, tests, tools, Windows sources
docs/       every HTML page — six book editions, language reference, stdlib, scorecard, philosophy,
            keyword words, audit, performance, design parameters, project status
images/     the icon set, the IDE mockups (including the colour-scheme legend), the installer mockup
progress/   the CHANGELOG (every version), README, PROJECT-OVERVIEW, ROADMAP
for-chatgpt/ the brief, the design charter, the project status page, and a prebuilt Windows test folder
```

## Inside `sutram-windows-test.zip`

`sutram.exe` (176,486 B, console PE32+) and `sutram-ide.exe` (34,581 B, GUI PE32+), cross-built on Linux.
**They compile and link. Neither has ever been executed.** `TEST-ME-FIRST.txt` gives the commands.

## The standard

**A verified partial beats a claim.** Every number in these documents is meant to be measured, and
anything untested is labelled untested. Do not claim the installer works, or the IDE is finished, or
Windows is supported, unless you ran it and saw it work.
