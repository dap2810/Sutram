# Commands and limits

The user's Downloads brief is preserved as REQUEST.md. Required project documents were read first. `git fetch origin` required approved host access because the sandbox denied .git/FETCH_HEAD. Latest candidate source was pinned to 108301e2155b7c48e3e6d88103910148662fd191; a later final fetch was unchanged. The GitHub main-ref API returned the same commit.

From the parent repository:

```powershell
python build/preflight-v313.py
python build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08/budget-boundary.py
& build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08/label-capture.ps1
& build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08/label-layout-model.ps1
python build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08/temp-inspect.py
python build/windows-v313-preflight/Windows-to-Sarvam/win-v313-2026-11-08/report.py
```

The preparation script saves the available setup and extracted compiler only under `build/windows-v313-preflight/artifacts`; neither binary is duplicated in the evidence commit. Native compiler identity was measured before any installation. The screenshot helper was approved to open the available installer, capture only its licence page and close it. No install/uninstall cycle occurred.

The screenshot and crop are direct screen captures of the intended foreground wizard and its instruction control. The filenames use `prefixed-` as “pre-fix evidence”; they do not indicate a repaired build. No image reconstruction or text replacement was used.

The original cross-process GDI size result is rejected because font selection was not validated and its result contradicts the screenshot. The replacement source-layout model creates its own font and checks font selection; it is explicitly not proof of a repaired GUI. Neither measurement substitutes for the missing v313 default/narrow captures.

Only the new budget-boundary measurements are reported. The literal-expression shape and previous v312 suite/passes were not repeated. Raw 15-probe data includes exits, no-output checks, runtime verification and exact source hashes. Its generator refuses stale output files.

The temp inspection is read-only and records newest entries, exact known staging contents and hashes. It is a preflight inventory, not a new post-uninstall test. No manual cleanup was performed.

Scripts retain their original workspace paths for provenance. The copied preflight/report scripts were run from the build locations shown above. `.gitattributes` preserves raw evidence bytes. EVIDENCE.sha256 covers every published file except itself.
