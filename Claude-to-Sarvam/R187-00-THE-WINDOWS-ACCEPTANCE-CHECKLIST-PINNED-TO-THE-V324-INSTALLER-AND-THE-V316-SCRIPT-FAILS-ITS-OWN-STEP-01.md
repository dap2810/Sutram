# R187-00 — The Windows acceptance checklist: `Claude-to-Sarvam/SUTRAM-WINDOWS-ACCEPTANCE.md`. **One file, ten steps, every step with an output to compare and what a different one means.** It is pinned to the v324 installer by its hash. Under Wine every expected output was produced by the very compiler the installer carries, so the expected text is measured, not written from memory. **Two traps found while writing it.** The one Windows script the chain has waited on since R167 fails its own step 01 on any version but v316. And downloaded from GitHub, that script arrives with the line ends R167 says cmd.exe can mishandle. The checklist handles both.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
the checklist is pinned to:
     r186-grahan-and-files e1f29f14b58be21e5b9eb8a09a2bc2f94fc22e65   Sutram 1.0 (v324) - sampurna sutra
     Sutram-Setup.exe c82bbca55125ae54c5107df7ebabc57473cd4a5a8143f1ce9125fe057bd99a3b
     the compiler in it 54e69d63f7d3712b0d4910ed71fff403e370ebcadc314c3708c23d2038fa347f
no code, no merge, no branch: this round writes one document. Gates and guard: as in R186-00.
```

Sanskrit only; no pack touched; `backups/` untouched. `R159 no personal paths`: 0.

## WS1 - what the checklist contains, against your eight items

| your item | where | how it is checked |
|---|---|---|
| 1. the installer, pinned by hash | the table at the top; step 1 downloads it **by commit SHA** and prints its SHA-256 | the hash must equal `C82BBCA5...`. **Downloaded from GitHub here and hashed: it does** |
| 2. what the installer prints at each step | step 2: the seven pages, each title and the text it must show, **read from the wizard's source** | which button to press; and **the License page opens on "I do not accept"** - a tester who clicks Next at once is stuck |
| 3. commands after install, exact output | step 3: `sutram --version` -> **`Sutram 1.0 (v324) - sampurna sutra`** and its second line; the path it runs from; **the installed compiler's SHA-256** | the hash ties the installed file to the tested one |
| 4. a program exercising what changed | step 5, `accept.sm`: `vartani_grahan` reads a name, `grahan` reads `-5`, a `kosh` made 800,000 times in a loop, a `mandapa` | four exact lines; a table says which wrong line means which version is missing |
| 5. the memory test, 800,000 passes | step 6, `smriti.sm` prints `parimana()` | **`smriti: 64`** - and v315/v316 print **`smriti: 51200000`** (measured). One number decides it |
| 6. the lexer test, a curly quote | step 7, `curly.sm` = `likha(“namaste”)` | the exact refusal, exit 1, no `.exe` written; and what v315-v320 say instead (`agyat naam 'namaste'`, column 12) |
| 7. what each failure means | a table after every step: what you see, what it means, **fatal or not** | 29 rows |
| 8. a record of what was seen | step 10: a block to fill in | asks for what the screen showed, never "as expected" unless it matched |

**And two steps you did not list:**

- **Step 8, v316's own acceptance script.** It was the condition set in R167, and nothing above checks v316's
  change (outputs never overwrite inputs). It runs 18 steps from four files downloaded by pinned URL, each hashed.
- **Step 9, uninstall.** It checks that the program folder and the PATH entry are gone, **and that the tester's
  own `accept.sm` is still there.** The installation contract says uninstall must keep user files.

## WS2 - the honest part

### Every expected output was produced, not written

The programs were compiled by **`win/sutram.exe` of the pinned commit** - the file the installer carries (same
SHA-256) - and run under Wine (`evidence-r187/wine.txt`). That covers `--version`, the `Siddh` byte counts, all
program output, the refusal, its exit code, the absent `.exe`, and all 19 lines of step 8. **Wine is not
Windows.** These are the outputs Windows *should* give, not outputs Windows *gave*.

**The three program files are written by a PowerShell block,** because a curly quote pasted from a web page or
typed in Notepad can arrive as other bytes. The block prints each file's SHA-256. **I cannot run PowerShell
here** (and AGENTS.md rules out downloading one). So I rebuilt the three files from the block's text the way
PowerShell joins it, and compared them with the tested files: the same bytes. **The block itself is NOT RUN;**
if PowerShell builds them differently, the tester sees a different hash at step 4, and the page says to stop.

### The two traps

1. **`accept_v316.cmd` fails its own step 01 on v324.** Step 01 checks that the version line says `(v316)`.
   Run on the v324 tip under Wine: **17 passed, 1 failed - the one is 01, on the version text alone.** A tester
   told "run the script; any FAIL is fatal" would stop the merge on a non-defect. The page names 01 as expected,
   says why, and says any other FAIL is fatal. **I did not change the script** (no code); a `(v3` check, or an
   `accept_v324.cmd`, is a one-line change if you want the script to read clean.
2. **Downloaded from GitHub, the script has LF line ends.** `.gitattributes` makes it CRLF only when it is
   checked out (`tests/windows/*.cmd text eol=crlf`, with R167's reason: "cmd.exe can lose a label in an LF
   file"), and the blob GitHub serves is LF. **Downloaded here: its hash is `D5C0DDBA...`, not the tested
   `3E78CDBE...`.** Step 8 rewrites it with CRLF, and that gives the tested bytes, checked. **Without that line
   the run would have tested a file nobody tested.**

**And why step 8 downloads four files, not the repository:** unpacked under `%TEMP%`, three paths in
`Windows-to-Sarvam/` pass 260 characters (the longest is 184 characters, the prefix about 96), and
`Expand-Archive` stops. The script needs `win\sutram.exe`, `sutram-link.exe`, `lib\ganit.smlib` and itself, and
nothing else. **Run from exactly those four under Wine: 17 passed, 1 failed (01).**

### What a step cannot verify from output, said where it occurs

- **Step 2, the wizard** is checked by eye against page titles. There is no output file. A different page is
  recorded, not judged.
- **Step 2, SmartScreen.** The page says it is expected for an unsigned download, that the hash is what
  identifies the file, and that going on is the owner's decision. **A UAC prompt or an antivirus block is fatal.**
  The page says not to turn the antivirus off.
- **Step 6, memory as Windows reports it** (Task Manager) is not asked for. `parimana()` is the program's own
  count, and that is what the memory work claims. **A Task Manager number has no expected value to compare.**
- **Step 7's quotation marks** show according to the console's code page. The compiler writes UTF-8 bytes;
  PowerShell may show `â€œ`. **I could not see what a Windows console shows,** so the page says which parts must
  match and which may not.
- **Step 9's Start-menu entries** are checked by eye.
- **The IDE** is installed and not tested. The page says so.

### Fatal or not - how I decided

**Fatal:** the wrong artifact (any hash), a request for administrator rights, the compiler or a program not
starting, any output line that means a version's change is missing, an uninstall that leaves the program or
deletes a user file. **Not fatal:** a different `Siddh` byte count by itself, wording that differs on a wizard
page, an existing older Sutram (uninstall it and start again), SmartScreen, a skipped hard-link step.

## WS3 - scope

**No code, no merge, no branch.** The checklist is a document in my folder. Its programs live inside it, so the
tester needs nothing from the repository but the five files it downloads by pinned URL.

**Why v324 and not v323** (the brief names `Sutram 1.0 (v323)`): v324 is the top of the chain, so one run covers
v316 to v324. Nothing but `grahan`'s sign separates it from v323. **If v324 is not accepted, the same page for
v323 changes the hash lines and one line of step 5** (`sankhya: 5` - v323 loses the sign). I can reissue it.

## Not done, and why

- **Not run on Windows** - it is the checklist for that run.
- **The PowerShell blocks are NOT RUN** - there is no PowerShell here; the file bytes they write are checked.
- **What a Windows console shows for a UTF-8 quotation mark is not known** - stated in step 7.
- **`accept_v316.cmd` is not changed** - offered above.
- **Four of my own hand-back names on main pass the same 164-character mark** (R179-00, R180-00, R184-00, R185-00)
  - not renamed, because other records cite them by name. **This round's two are 130 and 131.** The checklist
  never unpacks main, so step 8 is not affected.
