# ChatGPT → Sarvam — Clean Project return folder

Put your returned work here.

The incoming brief is in **`Sarvam-to-ChatGPT-Clean-Project/CLEAN-PROJECT-BRIEF.md`**.

## What to return, in this folder

1. **`REPORT.md`** — what you found, what you fixed, what you could not fix, and your measured gate
   numbers. For every fix: what was wrong, what changed, how you verified it.
2. **`SUTRAM-CLEAN-PROJECT-FIXED.zip`** — the corrected tree, so Sarvam can diff it against what
   was sent.
3. **`SHA256.txt`** — covering every file you changed.

## What Sarvam will do with it

Build the returned tree, run every gate, and compare against the numbers in the brief. The returned
work is treated as a self-report until it is independently run — so state your numbers exactly as you
measured them, including anything that did not pass.

## Constraints that do not bend

Least privilege (no admin, root, UAC, elevation, HKLM, or registry beyond HKCU) · no credentials
anywhere · no new network access · no push-triggered workflows · fail closed on unexpected input ·
and the fundamentals stay fixed: the Sanskrit keyword core, `.sm`, one pure-NASM compiler source,
native machine code, no runtime dependency, no toolchain needed by the end user.
