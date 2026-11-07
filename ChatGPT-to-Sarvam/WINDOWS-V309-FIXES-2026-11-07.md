# Windows v309 remaining issues fixed and verified

**Earlier same-day packaging/recovery candidate. Superseded by the [final fix handoff](WINDOWS-V309-FINAL-FIXES-2026-11-07.md), which additionally reproduces/fixes C1/I2 and re-verifies the rebuilt compiler and final package.** The identities/results below remain dated evidence for the earlier candidate.

**Implemented the remaining payload/recovery fixes, verified them natively, and installed the rebuilt candidate.** Source is in **[draft PR #68](https://github.com/dap2810/Sutram/pull/68)**, review head `5da6318f002875929a2b684d14523fd0f29b7f21`; product package built from `4536cc36a083a64a0382cfff14a78a298a5bae1b`. Independent Sarvam acknowledgement/acceptance is pending. This main commit contains evidence/instructions only.

The owner explicitly requested **fix the issues, verify, then hand off**, rather than another diagnostic-only handoff. Retain that workflow for subsequent Windows work. Product changes stay on review branches until independently accepted.

| Issue / validation | Result |
| --- | --- |
| Markdown checkout/package mismatch | Fixed by LF attributes plus staged UTF-8 normalization; all three fresh Windows samples match |
| Platform manifest ordering | Fixed; native Windows and native Linux builds have **657 identical payload files and a byte-identical manifest** |
| Late retry restages every file | Fixed; actual retry reuses **657/657**, makes **0 staging copies**, reaches Finish in **22.30 s** |
| File changes after reuse check | Refuses before moving a file without a staged replacement; tested edit, removal and successful restaging |
| Relocated Windows linker libraries | Builder now locates adjacent import libraries; native build and self-test pass |
| Dialog-click observer exception | Asynchronous click avoids false closing-window failure; native edited-file refusal completes observation |
| Partial Finish screenshot | Corrected foreground-window capture; full successful Finish page recorded |
| Native upgrade / early retry | Finish **21.81 s / 26.51 s**, engine 0 |
| Edited file after interruption | Exact edited bytes preserved; engine 1 and explicit refusal log |
| Regression checks | **14/14** native staging/publication fixture, **16/16 R130**, **24/24 R134** |
| Installed bundle | Both bin/win compiler layouts compile an imported library from another directory and print 81 |
| Final installed identity | Canonical v309, **657/657 hashes**, exact candidate manifest/uninstaller |
| Final process state | **18/18 recorded wizard/engine processes closed**, no installer lock or pending transaction |

Candidate setup SHA-256: `9dfe6b5ea185a6915918bb1d76abff474cec7d0d2c34d8a82d76e8850e00886f`.
Payload manifest SHA-256: `0523ff8050787c529777727998aaffd3d1c144e2fd8ed31100c0e220b559d096`.
Compiler remains unchanged: `05b23d56d40aaa4b71c6d67d13996d75da6e4d2e2b2ac47fbf4960a1a52fb481`.

The working candidate is installed; original, working and edited interrupted trees remain preserved. The runnable setup is retained locally at `E:\Github_Projects\Sutram\build\windows-v309-fixes\build\native-v309-fix\Sutram-Setup.exe`. Generated setup binaries/source-integrity release pins were not promoted to main. Sarvam should review/rebuild and update release artefacts through the established acceptance process.

Read [full results](../Windows-to-Sarvam/win-v309-fixes-2026-11-07/RESULTS.md), [payload comparison](../Windows-to-Sarvam/win-v309-fixes-2026-11-07/PAYLOAD.md), [recovery/preservation](../Windows-to-Sarvam/win-v309-fixes-2026-11-07/RECOVERY.md), [commands and initial failures](../Windows-to-Sarvam/win-v309-fixes-2026-11-07/COMMANDS.md), and [the completed native wizard screenshot](../Windows-to-Sarvam/win-v309-fixes-2026-11-07/capture-confirmation-finish.png). All exact scripts, per-entry hashes, native exit records and raw logs are in that evidence folder.

The fix removes unnecessary transaction staging, not payload extraction/integrity checks. Timing did not demonstrate a speedup versus the earlier 21.25 s late retry. Complete ZIP/setup byte reproducibility, a torn-journal-write test, general security-product compatibility and release/IDE acceptance are not claimed. The unchanged compiler's prior arithmetic/OOM/suite results remain dated evidence, not rerun totals. No workflow changed or full CI ran.

Please acknowledge PR #68 and this verified fix handoff, then independently review the source and rebuild before promoting a release. The [consolidated index](WINDOWS-HANDOFF-INDEX-2026-11-06.md) retains every earlier handoff and the failures that led here.
