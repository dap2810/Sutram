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

**You read source and write reports.** **So: check your own reports and the files you cite for personal paths, and name any you find in another partner's folder so its owner can fix it.**

**And when you review a fix that normalises paths, check the one thing that would break silently: a path inside a SHA-256 preimage.** **The hash stops matching the file it describes, and nothing else would notice.**
