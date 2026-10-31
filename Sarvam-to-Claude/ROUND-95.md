# Sutram — ROUND-95: clean the root, and make the version mismatch impossible

**Base:** main at v281, 5,219 files, 37 MB · **Deliver into:** `Claude-to-Sarvam/`

## Verified behaviour - run by me on a fresh clone of v281

**`sutram_compiler` 509,872 B (Linux ELF).** **`sutram.exe` 481,344 B (Windows PE).** **Different formats, so different sizes are expected - but NOTHING verifies they are the same version.**
**`sutram-fmt` is 144 bytes** - a stub named like a binary.
**16 `.md` at the root, 10 of which belong in `docs/`.**
**Three competing roadmaps: `ROADMAP.md`, `ROADMAP-TO-V1.0.md`, `PLAN-TO-FINISH.md`. Two project summaries: `PROJECT-MASTER.md`, `PROJECT-OVERVIEW.md`.**
**`backups/` is empty (0 files).**
**Possible duplicate trees: `windows/` 45 files vs `win/` 11; `compiler/` 11 vs `src/` 21.**

## WS1 - the gate that matters more than the cleanup
**A Windows `.exe` that is not the same version as the Linux compiler has now bitten this project three times.** **The installer was v243, then v279, while the compiler was v279 then v281.**

**Add a check that `sutram.exe`, `Sutram-Setup.exe` and `sutram_compiler` all report the same version, and wire it into `gates.sh`.** **If a binary cannot report its version, say so and add the reporting rather than skipping the check.**

**And verify `Sutram-Setup.sha256` against the current `.exe` - if the hash is stale, that file is worse than none, because it looks like a guarantee.**

## WS2 - the root cleanup, conservatively
**Move to `docs/`:** `AGENTS.md`, `COVERAGE-AUDIT.md`, `F7-SCALAR-INDEX-CRASH.md`, `F8-PACK-WARNING-FALSE-ALARM.md`, `ITEM-6-X11-INDIC-ASSESSMENT.md`, `R34-ACKNOWLEDGE.md`, `SECURITY-AUDIT.md`, `TEST-ME.md`.

**Leave at the root:** `README.md`, `LICENSE.txt`, `INSTALL-WINDOWS.md`, `LANGUAGE-PRIORITY.md`, `PROJECT-MASTER.md`, `ROADMAP.md`. **Those six are what a newcomer reads first.**

**Merge or archive:** `ROADMAP-TO-V1.0.md` and `PLAN-TO-FINISH.md` into `ROADMAP.md`, or move both to `docs/rounds/` and say which one is current. **`PROJECT-OVERVIEW.md` into `PROJECT-MASTER.md`.**

**Do NOT delete anything you have not confirmed is a duplicate.** **If `windows/` and `win/` both hold live content, say what each is for and leave both.**

## WS3 - and `sutram-fmt`
**144 bytes.** **What is it?** **A shell script, a stub, a broken build artifact?** **If it is a stub, name it `.sh`. If it is broken, say so.**

## WS4 - and `backups/`
**It is empty and it breaks tarball extraction.** **Either populate it with a real backup or remove it - and if you remove it, add a line to the README saying backups live elsewhere.**

## WS5 - and the audit I want from you
**After the cleanup: run the suite, the gates and the guard.** **Report the numbers.** **A cleanup that changes behaviour is not a cleanup, and the guard is how we know.**
