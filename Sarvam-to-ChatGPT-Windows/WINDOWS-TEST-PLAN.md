# Sutram — Windows test plan (for you)

You test Windows yourself. This is the order to try things in, with the result to expect at each step.
If a step fails, note **the exact command and the full output** — that is what makes a report useful.

## Step 0 — before anything

Confirm you are on a **normal user account**, not an administrator, so a wrong installer design shows
itself immediately. If a step ever raises a UAC prompt, **stop** — that is a design failure, not a
step to click through.

## Step 1 — the compiler, uninstalled (5 minutes)

Unzip `sutram-windows-test.zip` (or the `windows/` folder from the project) anywhere and open a command
prompt in that folder.

    sutram.exe --version
    sutram.exe --help
    sutram.exe examples\01_hello.sm hello.bin
    hello.exe

**Expect:** a version line, a help page, then `Namaste, Sutram!`

**Watch for the encoding bug.** In the earlier screenshot the version line read
`Sutram 1.0 (v29) ĞÖ the complete thread` — a mangled em-dash. If you still see mojibake, that is the
console-encoding defect and worth reporting exactly as it appears.

## Step 2 — the installer (10 minutes)

Run the built installer `.exe` as a **normal user**.

**Expect:** no UAC prompt. It installs under `%LOCALAPPDATA%`, adds itself to the **user** PATH, and
offers Start-menu and desktop shortcuts.

Then **open a NEW command prompt** (PATH changes need a fresh shell) and from any directory:

    sutram --version

**Expect:** it works from anywhere.

## Step 3 — the IDE (10 minutes)

Launch the IDE from the Start menu, then from the desktop shortcut.

**Expect:** a colourful editor that feels like IDLE but does not look like a copy of it — menus, a run
button or shortcut, an output pane, and **distinct colours for keywords, builtins, strings, numbers,
comments and the danda**.

Then double-click a `.sm` file in Explorer.

**Expect:** it opens in the IDE.

## Step 4 — actually write something (5 minutes)

In the IDE, type:

    mukhya
        likha("Namaste, Sutram!")
    samapt

Press the run shortcut.

**Expect:** `Namaste, Sutram!` in the output pane. Try a deliberate mistake too — a missing semicolon or
an undefined variable — and check the error names a **file and line** rather than crashing.

## Step 5 — a Sanskrit-keyword program (5 minutes)

Open `examples\218_sanskrit_devanagari.sm` in the IDE and run it.

**Expect:** `योगः = 15`. **This also tests that Devanagari survives the Windows console and the IDE** —
the most important non-ASCII path in the project.

## Step 6 — uninstall (5 minutes)

Uninstall from Windows Settings. Then check:

- `sutram --version` **fails** (it is gone).
- Your own `.sm` files and any `.bin` files you made are **still there**.
- The user PATH no longer contains the install folder.
- `HKCU\Software\...` has no leftover Sutram keys.

**Expect:** clean removal, your files untouched.

## What is NOT expected to work yet

- **Nothing Windows has ever been executed by this project before.** You are the first. Some things
  will likely fail — that is useful information, not a wasted test.
- No memory-safety claim, no performance claim, no OS/kernel capability yet.
- The Windows GUI sources are unbuilt; if the installer ships no IDE, that is the thing being built.

Report back with the step number, the command, and the output.
