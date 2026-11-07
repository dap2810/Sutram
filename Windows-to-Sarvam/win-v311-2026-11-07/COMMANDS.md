# v311 commands

Pinned checkout: `E:\Github_Projects\Sutram\build\windows-v311-verification`, source fae5319d2abf6dc1368d683b1aa4b80a8831ab5d.

```powershell
# Original repository: isolated checkout and adaptation of the v310 observation helpers
git worktree add -b codex/windows-v311-2026-11-07 build/windows-v311-verification fae5319d
python build/prepare-v311.py
# From the new checkout
python Windows-to-Sarvam/win-v311-2026-11-07/pin-fix-package.py
win/sutram.exe --version
python Windows-to-Sarvam/win-v311-2026-11-07/compiler-probes.py expressions
python Windows-to-Sarvam/win-v311-2026-11-07/compiler-probes.py nesting
python Windows-to-Sarvam/win-v311-2026-11-07/supplemental.py
$env:SUTRAM_EVIDENCE=Join-Path (Get-Location) 'Windows-to-Sarvam/win-v311-2026-11-07'
python tools/test_windows_native.py
& Windows-to-Sarvam/win-v311-2026-11-07/full-native.ps1
python Windows-to-Sarvam/win-v311-2026-11-07/installer-fixtures.py
python Windows-to-Sarvam/win-v311-2026-11-07/report.py
```

Compiler/suite and isolated workspace fixtures ran independently alongside native installation. full-native.ps1 serially performs initial backup/upgrade, concurrent engines, edit-during-publication, seeded suffix/unequal-copy tests, unmodified interruption/retry, and final identity/process closure. Exact subprocess argv is in JSON reports; fixtures/commands.json includes the unchanged upstream test commands and complete outputs. All nested probe sources and inventories are retained.

No security changes, unowned process termination, source patch, baseline rewrite, installer rebuild or workflow launch. Canonical installation trees and transactions are hash-verified and preserved before tests. Background engines use hidden/no-window process creation; only the intended setup wizard is visible. Fixture's staged-compiler read handle prevents commit cleanup if reached; v311's unequal-copy check correctly stops earlier. 15-second compiler deadlines, 180-second engine deadlines and 240-second GUI observer bounds are used; no timeout fired. Fixture assertions have explicit scoped instrumentation; full engine tests use unchanged embedded source.

Fresh shell identity rebuilds registry Machine + User PATH and runs from an unrelated directory. Complete native logs, source probes and screenshots are separate from the v310 run. Use fresh output/backup locations for reproduction; duplicate/stale-artifact guards are intentional.
