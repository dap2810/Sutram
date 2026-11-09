# Windows first-run paths — v312, 8 November 2026

**10 PASS, 1 FAIL, 1 SKIP.** PATH declined, all five shell-opening checks, and documentation access worked.
The desktop collision preserves the user's shortcut correctly, but clicking the only desktop item called
**Sutram IDE** opens **Notepad**; setup gives no visible collision warning. Confusion is an inference
from that observed first-click mismatch, not a human usability study.

Tested on Windows 11 Home, build (redacted), standard non-elevated account, 2026-11-08.
Pinned repository commit: `079c7b226fe968b3d9b5dfe248f097482f5d1fce`.
Setup SHA-256: `2356014dc0e66b1de1dabe3f868e55b7b73b1c3e17ad231802b2dbb5592643d6`.
Compiler SHA-256: `7ac8347032b6d9f754b4706d48c20f32f1a43f58324e4432d5463751031b6f93`.
The extracted and installed compiler reports:

```text
Sutram 1.0 (v312) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

All 658 embedded file entries match the installed bytes (657 payload files plus the manifest).
This is first-run testing of v312, not release acceptance. No installer/compiler source or binary was changed.


| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A1 — the PATH option, and its default | recorded | “Add Sutram to my user PATH (recommended)”; checked by default, cleared for this install | PASS |
| A2 — Start-menu terminal finds the compiler | found | Launch prints v312; typed `sutram --version` also prints v312; `where` resolves canonical installed compiler | PASS |
| A3 — a declined-PATH user can recover | yes | Start-menu terminal works without reinstall; full-path invocation succeeds; book §17.6 explains it | PASS |
| B1 — a path with spaces opens | opens | Exact unique fixture content loaded from `My Sutram Files` | PASS |
| B2 — a path with a Devanagari character opens | opens | Exact unique fixture content loaded from `सूत्रम्` | PASS |
| B3 — a path with `&` opens | opens | Exact content loaded from `Ampersand & Files` | PASS |
| B3 — a path with `%` opens | opens | Exact content loaded from literal `Percent %USERNAME% Files` | PASS |
| B4 — right-click → Open with | loads the file | `Open with → sutram-ide-gui` loaded the file | PASS |
| C1 — shortcut count after install | one | One desktop `Sutram IDE.lnk`, preserved byte-for-byte and still targets Notepad | PASS (count/preservation only) |
| C2 — a user is not confused | not confused | Desktop “Sutram IDE” opens Notepad; Finish does not warn | FAIL (observed target mismatch) |
| D1 — a documentation shortcut exists | exists | Start-menu “Sutram Documentation” opens installed English book in Firefox | PASS |
| D2 — a user can find the docs | can | Book is present; absent-book branch skipped as instructed; access demonstrated in D1 | SKIP |

Details: [PATH declined](PATH-DECLINED.md), [shell opening](SHELL-OPEN.md),
[desktop collision](SHORTCUT.md), [documentation](DOCS.md), [preservation and evidence notes](PRESERVATION.md).

An additional visible wording mismatch: the desktop checkbox says **“Create a desktop shortcut
(Sutram Terminal)”**, while the actual managed shortcut is **Sutram IDE.lnk**.

Original installation/settings restored: **672 checks, zero failures**; fresh-shell version succeeds.
The tested installation and collision fixture are preserved, with locations in [PRESERVATION.md](PRESERVATION.md).
No full compiler suite, v313 acceptance, missing-book simulation, uninstall cycle, or release acceptance was performed in this round.

Publication note: upstream advanced to `d25eb2ad` with a v313 package while this v312 evidence was being finalized.
The results above remain tied to the pinned v312 artifacts; they are not measurements of that newer package.
