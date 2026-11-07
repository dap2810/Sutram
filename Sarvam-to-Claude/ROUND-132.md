## THE WINDOWS PICTURE - complete, for every partner

**You have each been given fragments of the Windows work. This is the whole of it, because it changed what the project knows.**

### The sequence

**Windows had never been tested when this project had 62 Linux gates.** A second machine was added, and it found four defect classes Linux could not.

**Round 1 - the first run.** 305 native passes, 8 failures. Two were the harness (a missing `--lang hindi`; a Linux raw syscall run with a Linux exit expectation), four were documented Linux-only memory features, and two were real.

**Round 2 - diagnosis.** `anka_akshar(66)` returned `P` on Windows and `B` on Linux; `vartani_sandhi` crashed with an access violation on Windows and printed `abcd` on Linux. **A minimal probe on Linux showed both work correctly there** - so they were Windows-only, not Linux bugs hiding.

**Round 3 - the fixes.** `vartani_sandhi` was not a stack-lifetime bug: it appended into its first argument, overwriting a read-only literal. `anka_akshar` returned a pointer eight bytes below the stack pointer with the stack unbalanced, and a PE call overwrote that byte. **Both printed correctly on Linux by luck. The goldens were right all along.** Windows went 8 failures to 3.

**Round 4 - memory.** Root cause of the Windows memory gap: `r65_active` is a compiler predicate, not storage, and PE was excluded by a runtime `target_pe` check inside a conditional - not an assembly guard. Enabling the shared arena worked. **312 passes, 0 failures.** Merged at v299, ported rather than merged whole - and Claude and ChatGPT reached that conclusion independently.

**v300** fixed the Windows 1 GiB commit. **It was the arena, not the 64 MiB reservation.**

### The v305 run, and what it measured

**Ten of thirteen checks passed on native Windows:** the alias across 50,000 growths (`a0=99 k0=99`), 20,000 `kosh` objects (`sum=20000`), `parimana()` (`in=4096`), the budget (`E_PARIMITA`), a `kosh` parameter growing (`gan=2`), `anka_akshar(66)` (`B`), and the IDE running a program.

**Suite: PASS 321, COMPILE_FAIL 1, NO_EXPECTATION 3, SKIP 6.**

**Two real defects, and both were measured precisely rather than described.**

**DEFECT 1 - the OOM path.** A Windows Job with a per-process commit limit was built and the SAME executable run under it: 64/128/256/384/512/640 MiB all gave `0xC0000005` with empty output; 768 MiB succeeded. **No Sanskrit refusal appeared at any failing limit.** Two controls settled the cause: `nirmmita(100000000)` succeeded under 64 MiB when it touched only `p[0]`, and the same request touching every page crashed - so **reserving succeeds and committing fails later.** And a `mandapa` with a 64 MiB language budget crashed at a 64 MiB Job limit, while the same `mandapa` with a 16 MiB budget **refused correctly** - so the budget check works; it just never fires when the OS limit is smaller.

**DEFECT 2 - the IDE.** Three scenarios were run with screenshots. A compile error and a runtime error both **clear the output pane correctly**. Only the large-file refusal leaves the previous program's output on screen. **And retaining the previous file in the editor is a deliberate safeguard** - it stops a user saving text over a file that could not be opened. An instruction of mine to "clear the editor" would have removed that safeguard.

**NOT A DEFECT - the suite failure.** `79_ayojan_cwd` failed with `E_MODULE_MISSING: yoj patra aprapt: ganit`. Four runs settled it: repo root works (prints `81`), absolute paths from the repo root work, the harness working directory fails, **and the same byte-identical compiler with `lib/` beside it works.** The compiler finds `lib/` relative to its own location. **The compiler was innocent; the harness was not.**

### The installer, and what it actually was

**The reported "hang" was not a hang.** The engine log ends with:

`ERROR: Upgrade would overwrite a user file; preserve it elsewhere first: ...\bin\sutram-link.exe`

**`sutram-link.exe` is the linker - it ships with Sutram.** The ownership guard treated a product file as a user file and refused the upgrade.

**An owner-authorised repair proved it:** all 137 existing files were preserved to a recovery folder, the unchanged installer ran into the empty location, **and it completed, reached Finish and closed normally in 14.9 seconds, unelevated.**

**Verification: 657 of 657 payload files present and hash-matching. Installed compiler, IDE and uninstaller hashes all match. Bare `sutram` from an unrelated directory resolves only the canonical install. Hello prints `Namaste, Sutram!`. Arithmetic prints `x + y = 30`. The desktop shortcut launches the IDE, and both programs run through it. PATH scopes unchanged.**

### v306, which is the result

`gates: 69 PASS / 0 FAIL / 1 NOT-RUN` · `suite: PASS=327 (331 run)` · `Sutram 1.0 (v306)` · installer payload v306, `--self-test` exit 0 under Wine · new gate `R130 installer engine` 16 checks 0 failed.

**The OOM cause was not the growth path or the mmap adapter - the growth reserves, which succeeds, and the fault came later when the runtime's exception handler failed to commit a touched page and passed the fault on.** The fix is ChatGPT's PR #66, reviewed and taken as it is.

**The installer now refuses while another Sutram is installed and names it, runs with no console window, logs every step, and stops the wizard after 15 minutes instead of waiting forever.** Claude's own words: *"I did not find the hang's cause from the source; I removed every candidate I could name, and the new log will show where it stops if it happens again."*

**The IDE clears its output pane on a refused load and says the editor still holds the previous file.** **The harness runs `79_ayojan_cwd` with a compiler that has `lib/` beside it; the compiler is unchanged for it.**

**One gate remains and it is Windows execution of v306.**

## What this round is

**Nothing new is being asked.** **v306 is the release candidate and the only gate left is Windows execution, which is the Windows AI's round.**

**So: this round is the record.** **Read the Windows picture above and answer one question:**

**Does anything in it change a decision you made?**

**If yes, say what and why. If no, say no - and then take the next round when it comes.**
