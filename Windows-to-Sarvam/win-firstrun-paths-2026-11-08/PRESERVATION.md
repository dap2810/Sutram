# Preservation, restoration and evidence boundaries

The explicit first-run brief permits v312 and supersedes the earlier v313-only preflight stop for these tests.
The exact brief is [REQUEST.md](REQUEST.md). No product files were changed.

Before installing, the existing canonical installation's **663 files** were hashed and moved to
`C:\Users\dmech\AppData\Local\Programs\Sutram-before-firstrun-20261108`.
The current Start-menu folder and any existing desktop link were preserved; the three Sutram HKCU registry
keys (`Classes\.sm`, `Classes\Sutram.Source`, `Uninstall\Sutram`) were renamed with a
`-FirstRun20261108` suffix, retaining their complete contents. User PATH was recorded and its canonical
Sutram entries removed for the test; machine PATH was read only. No uninstall or deletion command was used.
Only the dedicated, validated canonical installation and test paths were moved; older preserved installs and
previous uninstall temp residue were left untouched.

After testing:

- The tested installation was moved, with all 663 files verified, to
  `C:\Users\dmech\AppData\Local\Programs\Sutram-firstrun-tested-20261108`.
- The original installation was moved back and all original files verified.
- Original registry keys, Start-menu shortcuts and user PATH were restored. The test registry keys remain
  under `-TestedFirstRun20261108` names. Test shortcuts, including the harmless desktop collision fixture,
  remain in `E:\Github_Projects\Sutram\build\firstrun-2026-11-08\preserved\`.
- **672 restoration checks passed**, including 663 original file hashes, original shortcut hashes,
  the complete three registry trees, and PATH comparisons. A fresh shell finds the canonical compiler and v312.
- All five IDE instances and the setup wizard closed normally. The two test terminals were sent `exit`.
  Seven test Explorer windows and the Notepad window were closed; the book test tab was closed.
  No installed Sutram process remained at restoration.

Records: [preservation](preserve.json), [restoration](restore.json),
[original registry/shortcut baseline](restoration-baseline.json), [final verification](restoration-verified.json),
[window cleanup and OS/token](finish.json).

## Checks of the testing harness

The first terminal screenshot already showed successful `sutram --version`, but the initial redirect capture
accidentally concatenated three commands because of PowerShell array-expression precedence. The raw
`terminal-initial-capture-error.json` is retained. Parenthesized command entries fixed the harness, and a second
actual shortcut launch produced separate raw version/where/PATH files. The corrected version bytes equal the
extracted compiler's version output exactly. No failed capture is used as product-failure evidence.

Explorer's first Open-with attempts encountered stale windows and duplicate invisible menu entries. Selecting
the newly opened Explorer window and the visible menu entry completed the actual menu test. Only the completed
IDE-load record is used as its result. The default double-click tests were successful on their first recorded runs.

The desktop list exposed no icon items through UI Automation. The icon's position was visually verified in
a private desktop capture before the real double-click. Only the icon region is published. Full desktop and
Explorer screenshots/UI dumps include unrelated user content and remain private under `build/`.

The initial documentation observer assumed a Chromium window; the actual default was Firefox. A later viewport
capture was occluded after a long UI read. Both are harness limitations, not documentation failures. The final
capture checks Firefox's foreground status immediately before and after capture, and its address matches the
installed book. The occluded capture is excluded and retained privately.

The first independent restoration check compared raw `REG_EXPAND_SZ` machine PATH against .NET's expanded PATH
and flagged a representation mismatch. The raw check record is retained. Expanding `%SystemRoot%` for a like-for-like
comparison produces the final 672/672 result; no machine PATH change was made.

Raw binary evidence and text are byte-preserved by `.gitattributes`. `EVIDENCE.sha256` covers all published files
except itself. Helpers are evidence of the executed procedure, not production code or a supported installer.
Review their fixed test paths and guards before any reuse. No CI workflow or full compiler regression suite was
changed or launched for this observational round.
