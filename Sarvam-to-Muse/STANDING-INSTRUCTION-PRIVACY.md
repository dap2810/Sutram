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

**You read the whole tree.** **So: list every file that still carries a personal path, with file and line, so the owner of that folder can fix it.**

**You did this for the wrong reference figures and the list was usable in one pass.** **This is the same task, and it matters more.**

**And one thing only a reader would catch: a personal path inside a FILENAME.** **The file itself would need renaming, and every link to it would break.**
