# ROUND 60 handoff: real Windows IDE and installer verification

Date: 2026-10-14. **Outcome: verified partial, NOT ready for release.**

Review source in draft PR #18: https://github.com/dap2810/Sutram/pull/18
Test run: https://github.com/dap2810/Sutram/actions/runs/38562501834
Review real-host screenshots from Actions artifact `r60-windows-desktop-evidence` (ID 11892492523).
See `ChatGPT-to-Sarvam/ROUND-60-OBSERVED.txt` for detailed real Windows observations and `ChatGPT-to-Sarvam/ROUND-60-SHA256.txt` for genuine source SHA256 hashes.

## Verified

- The native Windows GUI was rebuilt with NASM and linked as PE64 on a real Windows runner. Both IDE and installer opened.
- Seven menu names verified via Windows APIs: File, Edit, Shell, Debug, Options, Window, Help. Editor, output, shell, and Run controls had real native HWNDs.
- The 28 GUI source tests passed on Windows with PYTHONUTF8=1, correcting a default character-decoding issue in the test environment.
- GUI source now creates the Unicode RichEdit class using CreateWindowExW; all user-approved highlighting color values are preserved.
- Original installer crashed when Install was clicked, with exit 0xC0000005. The install and uninstall source had reversed arguments for GetTempPathW; both are corrected.
- Rebuilt the installer with a freshly hashed manifest for 210 files. The Windows build produced an 856,853-byte native setup test executable (SHA256 f3cfce0ddb0e1c9795d584ab733e3e827c90a1d79b63186f5e1d65b3af8254f3).

## Confirmed blockers

- The uploaded win/sutram.exe compiler did not exit while compiling a trivial native Windows program within a bounded 12-second test. It was tested independently of the IDE; therefore editor Run and shell execution remain unverified.
- The rebuilt installer did not reproduce the immediate crash but still failed to complete installation within a bounded 45-second test. GUI, icon and Start Menu shortcut were absent. Inspect install logs before claiming a root cause.
- Screenshots were captured on Windows, but no actual screenshot image was visually reviewed. Accurate token colors and canonical window/shortcut icon appearance are NOT established. The supplied canonical icon file hash is b48aeb52516433c3cce51ffe436fa04355cb938aa0b5188c60fe7c02f2923ec1.

## Sarvam instructions

Independently review draft PR #18 and the actual Windows screenshots/logs. Keep changes isolated until acceptance. Investigate the Windows native compiler hang in its own authorized scope before rerunning editor Run, shell, and installer. After the compiler works, verify real screenshot colors, correct icon, per-user no-UAC install, shortcut target/icon, HKCU uninstall entry, and installed GUI launch. Do not present this as a completed Windows release.

The Round 59 compiler optimization and evidence were already handed off separately under draft PR #17. Round 60 did NOT edit the compiler, libraries or approved syntax-color constants. Shared main receives these three Round 60 handoff documents only; source remains on draft PR #18.
