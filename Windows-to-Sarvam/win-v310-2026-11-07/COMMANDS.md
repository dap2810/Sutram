# Commands and scope

Test checkout: `E:\Github_Projects\Sutram\build\windows-v310-acceptance`, pinned to candidate.json's source commit. It was created after `git fetch origin`, `git merge --ff-only origin/main`, and `git worktree add -b codex/windows-v310-2026-11-07 build/windows-v310-acceptance origin/main`.

Preparation: `python build/prepare-v310.py` from the original repository; a copy of that script is included here. It adapts prior observation/preservation helpers into this evidence folder without touching product source.

From the pinned checkout (PowerShell, ordinary user):

```powershell
python Windows-to-Sarvam/win-v310-2026-11-07/pin-fix-package.py
python Windows-to-Sarvam/win-v310-2026-11-07/compiler-probes.py expressions
python Windows-to-Sarvam/win-v310-2026-11-07/compiler-probes.py nesting
$env:SUTRAM_EVIDENCE=Join-Path (Get-Location) 'Windows-to-Sarvam/win-v310-2026-11-07'
python tools/test_windows_native.py
& Windows-to-Sarvam/win-v310-2026-11-07/initial-install.ps1
python Windows-to-Sarvam/win-v310-2026-11-07/ownership.py concurrency
& Windows-to-Sarvam/win-v310-2026-11-07/ownership-controller.ps1
python Windows-to-Sarvam/win-v310-2026-11-07/supplemental.py
python Windows-to-Sarvam/win-v310-2026-11-07/ownership.py ordinary
& Windows-to-Sarvam/win-v310-2026-11-07/verify-saved.ps1
python Windows-to-Sarvam/win-v310-2026-11-07/report.py
```

Compiler and suite work ran concurrently with the independent initial install; all ownership tests ran sequentially. Engine launches, complete arguments, fixtures, process IDs/exits and hash inventories are in ownership/*.json. GUI argv/child identities/screenshots/logs are in initial.json, c1-stop.json, ordinary-stop.json and accompanying files. Every compiler probe, including every nesting depth, is retained with argv/output in the corresponding results.json.

Safety guards: original installation copied and hash-verified; later trees/transactions moved to verified direct-child destinations under per-user Programs; no security configuration changes or arbitrary process kills; only owned process handles stopped; background PowerShell engines launched without visible windows. The GUI observer bounds runs to 240 seconds; native engines have a 180-second observation deadline; compiler/run probes have 15-second deadlines. The suite uses its existing 15/5-second compile/run deadlines. No timeout fired.

Fresh identity reconstructs Machine + User registry PATH and starts a new cmd process outside the compiler directory, then runs `where sutram` and `sutram --version`. It also checks all installed hashes and registration. Process closure is checked using recorded GUI PID/start pairs and terminal status of owned engine process handles.

The fixture test deliberately supplies known-owned journal entries and synthetic backup bytes, and holds one later staged compiler open without delete sharing. Those inputs are essential to reproduce C1/C4; they are documented fixture state, not evidence of a naturally corrupted installation. The engine/ZIP/setup bytes are unchanged and hash-pinned.

Reproduction needs a fresh evidence/output directory and controlled installation state: stale-output and duplicate-backup guards deliberately refuse accidental reruns. The final report generator never reruns product tests. Native raw logs and the complete Git publication diff are the reviewable record. No product source diff exists in this round.
