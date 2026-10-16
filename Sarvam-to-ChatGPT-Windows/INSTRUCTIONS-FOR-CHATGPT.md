# Sutram — build the Windows installer and the IDE

**From:** Sarvam · **To:** ChatGPT · **Date:** 2026-10-16
**Repo:** `https://github.com/dap2810/Sutram` (public, owner `dap2810`, branch `main`)

This is a **delivery round**, not a feature round. The goal is one thing:

> **A user on Windows downloads one `.exe`, runs it, and ends up with the Sutram language installed
> and a working IDE — with no toolchain, no admin rights, and nothing to configure.**

Everything you need is in this archive. Read `README.md` in the archive root first, then this file.

---

## 1. What "installed" must mean

After running your installer, on a clean Windows 10/11 machine, **with a normal user account and no
administrator prompt**, all of these must be true:

1. **`sutram` works from any command prompt.** Typing `sutram --version` prints a version line.
   Typing `sutram prog.sm prog.bin` compiles a program, and the result runs.
2. **The IDE launches** — from the Start menu, and from a desktop shortcut — and is usable.
3. **The IDE is registered for `.sm` files**, so double-clicking a `.sm` file opens it in the IDE.
4. **Uninstall removes everything it added** and **leaves the user's own files alone.**

Per-user installation only: everything under `%LOCALAPPDATA%` or `%APPDATA%`, PATH appended to the
**user** PATH, registry only under **HKCU**. If your installer needs elevation, it is the wrong design.

## 2. The two deliverables

### Deliverable A — the installer (`.exe`)

The repository already has installer **sources** under `windows/native-installer/`, written in NASM and
producing a native PE executable that embeds a payload. **Build on that; do not start over, and do not
substitute an NSIS script.**

**A real defect you must fix first — two rounds have only written documentation about it.**
`windows/build-windows-setup.ps1` still references a folder called `windows-installer-native/`, but the
actual directory is `windows/native-installer/`. Its preflight also anchors paths to an older package
layout, requires `runas`, and looks for machine-PATH markers. **Repair the wrapper, the preflight, the
package layout and the integrity manifest together.** A one-string path change is not the fix, and
**bypassing the guard is not the fix** — the guard exists because the mismatch is real.

The legacy `windows/sutram-installer.nsi` **must not be used as a workaround.** It requests administrator
access and writes to HKLM and Program Files. That is out of scope for this project.

**Also remove any advice to disable antivirus or bypass PowerShell execution policy** from the guides.
If a user must weaken their own machine's security to install a language, the installer is wrong.

### Deliverable B — the IDE, better than Python IDLE

There is a working IDE today: `ide/sutram_gui_linux.asm` — one hand-written NASM file, an X11 client,
seven menus, syntax colouring, a line-number gutter, find, clipboard, and Ctrl-R to run. It is
**Linux-only**. The Windows GUI sources under `windows/gui/` exist and have **never been executed**.

Build the Windows IDE. The owner's requirements are specific:

- **It must feel like Python's IDLE** — a beginner opens it and immediately knows what to do: type code,
  press a key, see output. Not a bare text box.
- **It must NOT be a copy of IDLE.** Different layout, different feel. Do not reproduce IDLE's look.
- **It must be colourful, with different colours per function** — keywords, builtins, strings, numbers,
  comments, and the Sanskrit danda each visually distinct.
- **The GUI must be a real GUI** — menus, shortcuts, a run button, an output pane, error display.
- It should open a file given on the command line (`sutram-ide prog.sm`) — the Linux IDE does this and
  the Windows one should too.
- **It must not require the user to install anything else.** No Python, no runtime, no .NET.

A mockup of the intended installer and IDE look is in `images/` in this archive. **Treat those as
reference for the feel, not as pixel specifications to copy.**

## 3. A real bug visible in the existing Windows output

Look at the screenshot in `images/` showing `sutram.exe --help` on Windows. The version line reads:

```
Sutram 1.0 (v29) ĞÖ the complete thread
```

That `ĞÖ` is a mangled em-dash. The compiler writes UTF-8, and the Windows console is interpreting it
in a legacy code page. **This is a genuine Windows defect**, not a cosmetic one — it means any non-ASCII
output from the compiler is corrupted on Windows, which matters for a language whose keywords are
Sanskrit. Fix it properly: either set the console to UTF-8 explicitly, or write console output in the
console's active code page, or use the wide-character console API. **Do not paper over it by removing
non-ASCII characters from the messages.**

## 4. What to test, and how to report it

Windows is the one gate **nothing in this project has ever passed**. Nobody has run the Windows compiler,
the Windows GUI, or any installer. **You may be the first.** So:

- Test on a real Windows machine if you can. If you cannot, **say so plainly** and state exactly what
  remains unverified — do not describe source inspection as a test.
- Report **what you ran** and **what you observed**, not what you expect.
- For every claim, the evidence must be a command and its output.
- If a thing does not work, say it does not work. **A verified partial beats a claim** — that is this
  project's standard.

## 5. Hard constraints — these do not bend

- **Least privilege.** No UAC, no administrator, no HKLM, no Program Files writes, no machine PATH,
  no registry beyond HKCU. Per-user install only.
- **No credentials** anywhere — placeholders only, including tests, CI and commit messages.
- **No new network access.** The compiler and the language stay self-contained.
- **No push-triggered workflows.** `workflow_dispatch` only.
- **No antivirus or execution-policy bypass advice**, and no code that requires either.
- **Fail closed.** If an input does not match what a tool expects, refuse rather than guess.
- **Preserve the fundamentals:** Sanskrit keyword core · `.sm` extension · one pure-NASM compiler source ·
  native machine code · no runtime dependency · **the end user needs no toolchain**.

## 6. What is in this archive

```
sutram-complete/
  project/        the full source tree — compiler, IDE, library, packs, tests, tools, docs, Windows sources
  docs/           every HTML page: the six book editions, the language reference, the stdlib reference,
                  the scorecard, the philosophy, the keyword words, the audit, the performance report
  images/         the icon set at every size, plus the installer and IDE mockups and screenshots
  progress/       the CHANGELOG (every version), README, PROJECT-OVERVIEW, ROADMAP
  for-chatgpt/    this instruction, and a copy of the design charter
  MANIFEST.sha256 every file, so you can verify what you received
```

**Read `progress/CHANGELOG.md`** for the full history, and `project/docs/sutram-design-parameters.html`
for what the language is being built to be. The relevant part for you is **item 12, "Genuine freestanding
capability"** and **item 17, "Excellent developer tools"** — this round is the tooling half of item 17.

## 7. What to return

Deliver back into the repository, in a folder named `ChatGPT-to-Sarvam-Windows/`:

1. **`REPORT.md`** — what you built, what you ran, what you observed, and **what you could not verify**.
2. **The installer sources** — the repaired wrapper, preflight, layout and manifest.
3. **The Windows IDE sources.**
4. **A built installer `.exe`**, if you can produce one, with its SHA-256.
5. **`SHA256.txt`** covering every file you changed or added.
6. **A short test plan** the owner can follow on his own Windows machine, in the order he should try
   things, with the expected result at each step.

The owner tests Windows himself. **Give him a plan he can follow without asking you questions.**

---

**The standard, one last time.** Do not claim the installer works, or that the IDE is finished, or that
Windows is supported, unless you ran it and saw it work. State your measurements, keep failures and skips
separate from passes, and mark anything unverified as unverified. That is how this project has been built
so far, and it is how it stays trustworthy.
