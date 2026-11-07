# Commands, probes and observation limitations

Pinned checkout: `E:\Github_Projects\Sutram\build\windows-v311-acceptance`, branch `codex/windows-v311-acceptance-2026-11-07`, source `2e8f2ea4085925f862450b16d444313eefdbb007`. Working artifacts: `build/native-v311-acceptance`. Every command below is relative to that checkout unless stated otherwise. GUI/state changes ran under the existing Windows user, outside the automation sandbox when required; no administrator account or security exclusions were used.

These are the commands used for evidence collection, not a request to rerun destructive state transitions automatically. `state.ps1 -Action clear` refuses a second execution; preservation must precede another fresh-state test. The setup snapshot was copied from the exact repository artifact by `pin-fix-package.py`, not rebuilt.

```powershell
python Windows-to-Sarvam/win-v311-acceptance-2026-11-07/pin-fix-package.py
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/state.ps1 -Action clear
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/default-install.ps1
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/open-app.ps1 -App notepad
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/notepad-first.ps1 -Phase type
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/notepad-first.ps1 -Phase save
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/first-program.ps1
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/open-app.ps1 -App settings
python Windows-to-Sarvam/win-v311-acceptance-2026-11-07/time-suite.py
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/watch-uninstall.ps1
# Owner performed Settings uninstall; stop-uninstall-observer.flag stopped only the observer.
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/state.ps1 -Action snapshot -Name after-uninstall
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/default-install.ps1 -Name reinstall
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/ide-acceptance.ps1
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/final-process-check.ps1
python Windows-to-Sarvam/win-v311-acceptance-2026-11-07/identity.py --name final-identity
& Windows-to-Sarvam/win-v311-acceptance-2026-11-07/state.ps1 -Action snapshot -Name final
```

`prepare-v311-acceptance.py` is the preserved bootstrap script as originally executed from the main checkout's `build/` directory; its relative paths assume that original location. It adapted prior evidence helpers and copied the owner-supplied brief. The finished helpers are all included directly, so running that bootstrap from this evidence directory is unnecessary and would use the wrong relative base. Per-case commands/return codes/stdout/stderr live in `native-cases.json`; actual compiler commands are also displayed in `first-cli.log` and the new Command Prompt screenshot. Installation command lines, exact page text, checkbox values, PIDs/start times and times are in the first/reinstall JSON files. No full CI or workflow was triggered.

## Observer failures retained

- Initial `WM_CHAR` typing into modern Notepad's RichEditD2DPT ignored bare carriage-return messages, joining the source into one line. `notepad-first-attempt1.ps1`, `notepad-type-observation.json` and its screenshot retain that failed approach. Guarded foreground keyboard input corrected it; the saved three-line file and successful compilation establish the final result.
- Foreground activation initially failed; the helper now verifies the exact intended foreground window before keyboard input. A UI Automation filename element was read-only, so the standard Save dialog filename keyboard accelerator was used. Desktop UIA/CIM calls denied by the sandbox were rerun outside it. None of these failures changes a Sutram product outcome.
- The first `first-program.ps1` approach inherited the hidden automation console: compilation/run succeeded but no visible shell screenshot was possible. `first-program.ps1.attempt1`, `first-program.json.attempt1` and `first-cli.log.attempt1` retain it. The second explicit conhost approach timed out without the intended visible command run; its script/JSON are preserved as `.attempt2`. The observer stopped its own test hosts. The final CREATE_NEW_CONSOLE approach produced the actual successful Command Prompt screenshot. No arbitrary user process was killed; final read-only checks found no remaining attempt-2 child.
- The first install's default-IDE screenshot and reinstall Finish/default-IDE screenshots were skipped because the capture guard could not confirm foreground ownership. The records contain explicit warnings and null screenshot fields. The first Finish screenshot and all four later IDE screenshots succeeded.
- The user completed uninstall before its observer started. Consequently no automated uninstall process/exit/dialog capture is claimed; the owner feedback, fresh engine log and subsequent state are the evidence.

## Privacy and artifact integrity

Four exploratory UI captures are retained only under the local working area's `private-local-observer/`: `notepad-save-dialog.png`, `notepad-save-dialog-ui.json`, `settings-initial-ui.json`, `settings-opened.png`. The Save dialog initially exposed unrelated folder/filename metadata, and Settings listed unrelated installed apps. These were moved out of the evidence directory and are intentionally **not uploaded**. `settings-opened.json` keeps its original screenshot field, but that referenced image is intentionally omitted. No unrelated file contents were opened. Relevant app-specific screenshots, required PATH/Programs inventories and exact source/test logs are included.

Screenshots are unretouched foreground-window captures. The reports distinguish visible UI observations, raw native control text, owner feedback and source-level inferences. A local `.gitattributes` uses `* -text` to preserve exact evidence bytes; `EVIDENCE.sha256` covers every published file in this folder except itself. The embedded `payload.manifest.sha256` is force-added despite the general repository ignore rule. Product-source diffs remain empty in the pinned checkout.
