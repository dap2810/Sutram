## FIRM STANDING INSTRUCTION — from the owner, effective now

**Never write the owner's system details into this repository.**

**That means, in every file you create or edit:**

- **no home directory** — no `C:\Users\<anything>`, no `/home/<anything>`
- **no username**
- **no drive letter or absolute path outside the repository** — no `E:\`, no `D:\`
- **no machine name, no OS build number, no hardware detail**
- **no IP address, no MAC address**
- **no screenshot filename that encodes a path**

**Write `%USERPROFILE%`, `<repo>`, `%TEMP%`, and "Windows 11 Home, November 2026" instead.**

**A path is evidence; a username is not.** **`%USERPROFILE%\AppData\Local\Programs\Sutram\bin\sutram.exe` says exactly what the absolute path said, and identifies nobody.**

**This applies to reports, evidence, JSON, logs, transcripts, commit messages and code comments.**

**And it applies retroactively: if you find a personal path in a file you own, replace it and say you did.**

**The repository is public.** **There is no version of this where a path is harmless because it is only in evidence.**

**You also own the cleanup: ROUND-165 normalises the Windows folder, and `R159 no personal paths` gates it.**

**The gate must fail on the tree before your commit.** **A gate that passes first time has not been tested.**

**And put the rule in `AGENTS.md` where a new contributor reads it first, so it outlives this round.**
