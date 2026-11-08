# Sutram — four first-run paths, testable on v312

**Copy this whole file to the Windows AI.**

**v313 does not exist yet, and you were right to stop.** **But these four tests do not need v313 — they are installer and shell behaviours, not compiler behaviours.**

**You can run all four on the v312 you already have.**

---

## 0. Where these came from

**An independent reviewer was asked: name the first-run defects a fresh install would show that nobody has looked at.**

**Its answer, and it was careful about what it is:**

> ***"These are places to look, not four newly discovered bugs."***

**So these are four paths with an edge case in each, and nobody has walked them.**

**None of them depends on the compiler version, so v312 is fine to test them on.**

---

## 1. Task A — "Add to PATH" unchecked

**The installer offers "Add to user PATH". A user can decline it.**

**What happens then?**

### A1 — install with PATH declined

**Preserve and remove the current installation first, as you have been doing.** **Then install, and clear the "Add to PATH" option if the wizard offers it.**

**Record: what the option is called, and whether it is checked by default.**

### A2 — and then open the Start-menu terminal

**The installer creates a Start-menu entry. Open it.**

**Then run:**

```
sutram --version
```

**Record exactly what happens.**

**Three possible outcomes, and each is a different finding:**
- **the terminal sets its own PATH and the compiler is found** — good, and worth saying
- **the terminal does not find it, and says so** — a defect, but an honest one
- **the terminal opens and the user has no idea what to type** — a usability finding

### A3 — and can the user recover?

**Without reinstalling, can a user run the compiler?**

**Look for whether the installer tells them how — a README, a shortcut, a note on the Finish page.** **Record what a user would find.**

**A user who declines PATH and is then stuck has been given a choice they cannot undo.**

---

## 2. Task B — a `.sm` file opened through the shell

**The installer registers `.sm` files so they open in the IDE. The open command is the GUI plus a quoted `"%1"`.**

**The quote suggests the path is meant to survive spaces.** **Let us find out what it actually survives.**

### B1 — a path with spaces

**Create a folder with spaces in the name, for example `C:\Users\<you>\Documents\My Sutram Files\`, and put `hello.sm` in it.**

**Then open the file from Explorer by double-clicking.**

**Record: does the IDE open with the file loaded?**

### B2 — a path with a non-ASCII character

**Create a folder with a Devanagari or accented character in its name, and put `hello.sm` in it.**

**Open it from Explorer.**

**Record what happens.**

**This matters more than it looks: this is a language for India, and a path with a Devanagari folder name is ordinary.**

### B3 — and a path with a `&` or a `%`

**Create a folder containing `&` and one containing `%`, and open a file from each.**

**A `%` in a path is the classic command-line expansion failure.** **Record both.**

### B4 — and right-click → Open with

**If `.sm` is not the default handler, use right-click → Open with and pick the IDE.**

**Record whether the file loads or the IDE opens empty.**

---

## 3. Task C — desktop shortcut collision

**The installer preserves a pre-existing `Sutram IDE.lnk` that it does not own.**

### C1 — create a shortcut with that exact name

**Before installing, create a shortcut on the Desktop named `Sutram IDE` that points somewhere harmless — for example to `notepad.exe`.**

**Then install.**

**Record:**
- **how many shortcuts named `Sutram IDE` exist after install?**
- **what does each point to?**
- **does the installer say anything about preserving it?**

### C2 — and what a first-time user sees

**From the Desktop, with no other information: which shortcut would a user click, and what would happen?**

**If two shortcuts sit side by side and one opens Notepad, that is a real first-run confusion.**

**Record the screenshot.**

---

## 4. Task D — the documentation shortcut

**The installer creates a documentation link only when the English book exists in the payload.**

### D1 — does the shortcut exist after a normal install?

**Look on the Start menu and the Desktop for a documentation or book shortcut.**

**Record whether it is there, and what it opens.**

### D2 — and if the English book is absent

**Check the installed folder for the book file.** **If it is present, say so and skip D2.**

**If it is absent, then the installer created no shortcut — and a user has no documentation.** **Record whether anything else points them to it.**

---

## 5. What NOT to do

- **Do not wait for v313.** **None of these four depends on it.**
- **Do not modify the installer or the compiler.**
- **Do not claim release acceptance.**
- **Do not delete anything.** **Preserve and move aside, as you have been doing.**
- **If a test needs a fresh install and you already have one, preserve it first and record what you preserved.**

---

## 6. What to commit

**Push to `Windows-to-Sarvam/win-firstrun-paths-<date>/`:**

1. **`PATH-DECLINED.md`** — A1 to A3, with what the Start-menu terminal actually does.
2. **`SHELL-OPEN.md`** — B1 to B4, with the exact folder names used.
3. **`SHORTCUT.md`** — C1 and C2, with a screenshot of the Desktop.
4. **`DOCS.md`** — D1 and D2.
5. **`RESULTS.md`** — the table below.
6. **The version string you tested.**

### The table

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A1 — the PATH option, and its default | recorded | | |
| A2 — Start-menu terminal finds the compiler | found | | |
| A3 — a declined-PATH user can recover | yes | | |
| B1 — a path with spaces opens | opens | | |
| B2 — a path with a Devanagari character opens | opens | | |
| B3 — a path with `&` opens | opens | | |
| B3 — a path with `%` opens | opens | | |
| B4 — right-click → Open with | loads the file | | |
| C1 — shortcut count after install | one | | |
| C2 — a user is not confused | not confused | | |
| D1 — a documentation shortcut exists | exists | | |
| D2 — a user can find the docs | can | | |

---

## 7. Why these four are worth a round

**A user who declines PATH and then cannot run the compiler has been given a choice they cannot undo.**

**And a path with a Devanagari folder name is ordinary in India — if `.sm` files fail to open from one, that is a defect in a language built for this audience.**

**None of these is a compiler bug.** **All four are what a first-time user meets before they write a line of code.**

**And the reviewer was clear that these are places to look, not confirmed defects — so "it works" is a perfectly good result for any of them.**
