# Sutram — WINDOWS ROUND: acceptance for v326. Fifteen versions since the last real run.

**For:** the Windows machine · **Deliver into:** `Windows-to-Sarvam/`

**The last real acceptance was v311 on 7 November.** **v313 was a preflight, not a result.** **Nothing since.**

**The chain is now v326.** **Fifteen versions of changes have never run on real Windows**, including the entire memory work, the lexer refusal, reading a line of text, and the file examples.

---

## 1. What is under test

**`Sutram 1.0 (v326)`.**
**Installer SHA-256: `c47936ca009e62c35503d64afd7d777ab9b22c26953335948ae698a93e7b8ef3`**

**Verify the hash before anything else.** **`certutil -hashfile <path> SHA256`.** **If it does not match, stop — every result below would be about the wrong artifact.**

**And record the starting state the way v311 did: `where sutram`, `sutram --version`, the LocalAppData Programs listing, and both PATH hives.** **v311 preserved and hashed the existing installation before touching it. Do the same.**

---

## 2. The three checks that make this run necessary

**Most of the chain is covered by 93 gates, 332 suite tests and 788 guard programs on Linux.** **Three things are not, because they have only ever run under Wine.**

### A. Outputs never overwrite inputs (v316)
```
copy hello.sm self.sm
sutram self.sm self.sm
type self.sm
```
**Expected: a refusal, and `self.sm` still contains the source.** **If it is a binary, that is data loss — stop and report immediately.**

### B. An unknown character is refused (v321)
**A program containing a curly quote, copied not retyped.**
**Expected: a refusal naming the character and its code point, with line, column and a caret.**
**Absent the fix it would compile and say `agyat naam 'hello'` — pointing at the text instead of the quote.**
**And an en dash: `vitti a = 5 – 2` must be refused. If it compiles and prints `5`, the fix is not present.**

### C. Reading a line of text (v322 to v326)
**`vartani_grahan()` — a line, uncut, without its newline.**
**Test three inputs: a word, an empty line, and Ctrl-Z.**
**Expected: the word echoes back; the empty line prints nothing and does not crash; Ctrl-Z ends input without hanging.**

---

## 3. And the seven that prove the rest still works

1. **Install.** **UAC must not appear** — if it does, that breaks the least-privilege rule and is a defect. **Record the version string the welcome screen shows.**
2. **`sutram --version`** must print `Sutram 1.0 (v326)`. **In a fresh terminal** — PATH changes do not reach an open one.
3. **Compile and run `hello.sm`.** **Expected `namaste`.**
4. **Memory: 800,000 passes with a `kosh` made each pass.** **Watch commit size in Task Manager.** **Expected: under 30 MB and done in a second or two.** **Absent the fix it would climb past 500 MB.**
5. **A `mandapa` still runs** — one that takes a `nirmmita(64)` and exits. **No crash.**
6. **The IDE.** **Does it open, is the menu English, does it run a program, does it show the refusal with a caret, and does Sanskrit render or show boxes?** **A Sanskrit error that renders as boxes is not an error message.**
7. **Uninstall.** **Does it remove the program, the shortcut, and the PATH entry — and leave your `.sm` association and your own files intact?** **Create `mine.sm` in Documents before uninstalling and check it after.** **This installer once deleted a user's whole `.sm` registry key at install time.**

---

## 4. The recording format

**One line per check:**
```
CHECK <n> — <PASS|FAIL|SKIP> — <what you saw, quoted>
```

**And a footer:**
```
WINDOWS EDITION: <winver>
ARCHITECTURE: <...>
INSTALLER SHA-256: <verified value>
CHECKS: <n> PASS, <n> FAIL, <n> SKIP
PEAK COMMIT SIZE, memory test: <...> MB
SANSKRIT RENDERS IN THE IDE: <yes|no>
UNINSTALL LEFT .sm ASSOCIATION: <intact|broken>
UNINSTALL LEFT MY FILES: <yes|no>
```

---

## 5. What not to do

- **Do not merge. Do not push a branch. Do not edit `src/`, `lib/` or `docs/`.**
- **Do not fix a failure to make the run pass.** **A recorded failure is worth more than a green run that hid one.**
- **Do not report PASS unless you saw the expected output.** **"It seemed to work" is not a result.**
- **If a check cannot run, mark SKIP and say why.** **A blank is honest; a guess is not.**

**Two failures should stop you immediately: `self.sm` becoming a binary, or the installer asking for elevation.** **Everything else: record, continue, report.**

---

## 6. And the evidence standard

**v311 set it and this run should meet it:** **the existing installation copied and every preserved file hash verified before anything was moved; the real Start Menu shortcut resolved rather than a copy; screenshots visually inspected, not just captured; and a `state.ps1 -Action clear` that refuses a second execution.**

**Do the same.** **An evidence file per check, hashes where a file changed, and screenshots for anything visual.**

---

## 7. What happens after

**If every check passes, the eleven branches merge in one go and v326 becomes 1.0.**

**If some fail, the failures become the next round and the merge waits.** **Eleven branches have waited rather than shipped for exactly this reason.**
