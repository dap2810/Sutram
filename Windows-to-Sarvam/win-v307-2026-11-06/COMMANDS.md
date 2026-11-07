# v307 commands and provenance

Working directory: `E:\Github_Projects\Sutram`; non-Administrator Windows user
`dmech`. Requested scope: [REQUEST.md](REQUEST.md). Source under test:
`75586a754371dc27f9ed850f592df6194b8e11a6`, which contains v307 implementation
`60ce554d` and the later Muse probe reports. Product files stayed pinned during
testing. No compiler, library, original example, golden, installer or workflow
was edited, and no CI run was launched.

| Artifact | SHA-256 |
| --- | --- |
| `Sutram-Setup.exe` | `cbbfd0a66c0a9728c3fd88096631462430c0185cd8c6738964d5b885253e7481` |
| Installed `bin/sutram.exe`, root and `win/sutram.exe` | `0444b43552f6140147ee4701aeac857d585086681bbe4e5bd71d8f90bedd3f7b` |
| Installed IDE | `635c276b354c672925d460eaf6717c69333ed347eaa6084eda08ae6b40a55ad0` |

Native GUI tests require the interactive desktop and write the user's installation
folder. The tool permissions were approved for those scripts; the scripts reject
an elevated Administrator token. Backups are verified before moving the canonical
installation. Every recursive move validates the absolute parent and rejects
reparse points. No broad `Stop-Process -Name Sutram*` command was used.

Commands run in order (all paths relative to the repository):

```powershell
& .\Windows-to-Sarvam\win-v307-2026-11-06\run-install.ps1 -Phase clean
python Windows-to-Sarvam/win-v307-2026-11-06/identity.py
python Windows-to-Sarvam/win-v307-2026-11-06/oom.py
& .\Windows-to-Sarvam\win-v307-2026-11-06\finish-clean.ps1
python Windows-to-Sarvam/win-v307-2026-11-06/slice.py
python Windows-to-Sarvam/win-v307-2026-11-06/suite.py
& .\Windows-to-Sarvam\win-v307-2026-11-06\run-install.ps1 -Phase upgrade
python Windows-to-Sarvam/win-v307-2026-11-06/normalize-clean.py
python Windows-to-Sarvam/win-v307-2026-11-06/security-log-read.py
& .\Windows-to-Sarvam\win-v307-2026-11-06\finish-phase.ps1 -Phase upgrade
& .\Windows-to-Sarvam\win-v307-2026-11-06\retry-upgrade.ps1
python Windows-to-Sarvam/win-v307-2026-11-06/security-log-read.py
& .\Windows-to-Sarvam\win-v307-2026-11-06\capture-dwm.ps1
python Windows-to-Sarvam/win-v307-2026-11-06/provenance.py
& .\Windows-to-Sarvam\win-v307-2026-11-06\finish-installer-tests.ps1
& .\Windows-to-Sarvam\win-v307-2026-11-06\log-reader-check.ps1
& .\Windows-to-Sarvam\win-v307-2026-11-06\repeat-recovery.ps1
& .\Windows-to-Sarvam\win-v307-2026-11-06\defender.ps1
python Windows-to-Sarvam/win-v307-2026-11-06/audit-handoff.py
python Windows-to-Sarvam/win-v307-2026-11-06/audit-handoff.py --staged
```

`oom.py` exits 1 because 18 executions failed. `slice.py` exits 1 because three
escape paths still return incorrect values. `suite.py` exits 0: **322 PASS**, no
FAIL/COMPILE_FAIL/TIMEOUT, three NO_EXPECTATION and six deliberate skips. It
executes the unchanged repository `tools/test_windows_native.py`, which uses
the hash-identical repository compiler (root compiler for the unrelated-CWD
library case). [native-cases.json](native-cases.json) contains every case and
command. [suite.json](suite.json) records the harness hash and 59.972 s duration.

The OOM tests ran sequentially, before the suite. Slice execution and the suite
also ran sequentially. The GUI observer remained open during those checks, but
its installer engine had already completed. Timing is machine-specific.

Diagnostic issues and their limits:

1. Clean-install `Get-Content` output retained PowerShell provider properties;
   JSON serialization expanded them to 111,258,037 bytes and delayed observing
   Finish. The original bytes and hash are retained locally under `build/`;
   `normalize-clean.py` removes only those extraneous properties from the
   published observation. The actual engine log shows start/completion timestamps.
   `finish-clean.ps1` captured the successful Finish screen, stopped only the
   identified faulty observer, and closed the wizard through Finish. The precise
   moment when Finish first appeared and the departed child's exit code were not
   captured in this attempt.
2. The first upgrade observer encountered a sharing violation on the active log;
   its error handler also failed to copy that log. The engine then was absent and
   the wizard showed an error, captured by `finish-phase.ps1`. Its synchronous OK
   click timed out, so `retry-upgrade.ps1` later stopped only that identified wizard.
   Causality is not established. All evidence is retained as
   `upgrade-observer-failed*`, including the partial tree's preservation path.
   The next reader used explicit `FileShare.ReadWrite | FileShare.Delete` and
   tolerated read errors. This still did not guarantee writer compatibility:
   a later isolated fixture demonstrated that Windows PowerShell 5.1's
   `Add-Content` fails while even this fully shared reader is open. Closing the
   reader immediately restores successful appends. See
   [log-reader-check.json](log-reader-check.json). The engine uses `Add-Content`
   with stop-on-error, including inside its error-reporting path. This is a
   separate logging fragility for Sarvam to review, not a compiler change here.
3. The first interrupted-install retry copied all 657 payload files and reached
   shortcut creation, then produced an error dialog. Its synchronous OK click
   also timed out. This attempt used the live reader and cannot establish a
   recovery failure independent of reader interference. It is retained under
   [reader-interference](reader-interference), with its partial tree preserved
   and all 662 backup files restored and verified. `install-with-live-log-reader.ps1`
   preserves the observer version used in that attempt.

The final `install.ps1` never opens a running engine's log. It observes the native
UI and process lifetime, and reads the log after exit. For deliberate interruption,
it counts complete payload filenames (excluding pending/partial files), then
terminates only its captured process handles; the preserved log is inspected
after both exit. This avoids causing a log-writer sharing failure while still
proving that several payload files were copied before interruption.

The repeated upgrade's Acronis suspension is independent direct vendor evidence.
Its locked log cannot always be snapshotted while the suspended writer holds a
handle; the last successfully observed line is retained and the raw log is copied
after test cleanup closes the owned process handles. This does not resume a
security-suspended process. No protection setting or exclusion was changed.

`provenance.py` checks the tested executable hashes, the unchanged Job Object
runner and native harness, the six copied Muse probes, and all 32 stderr byte
records. All 44 comparisons pass. The extracted engine and repository engine
have different byte hashes due to text encoding/newline representation; their
text is identical after UTF-8 BOM/newline normalization, including the log-before-
copy ordering. The exact hashes are recorded in [provenance.json](provenance.json).

`finish-installer-tests.ps1` waits for the existing upgrade observer to save its
completed result. If unsuccessful it invokes `restore-after-test.ps1 -Phase upgrade`,
then runs `run-install.ps1 -Phase interrupt`, saves the pending manifest, and runs
`run-install.ps1 -Phase recovery`. It restores the preserved v307 copy if recovery
fails, then checks final identity and recollects the relevant security records.
It never ends the 15-minute observation early. Its first interruption used the
live log as a trigger. After the reader-conflict finding, `repeat-recovery.ps1`
preserved that attempt, restored and verified the backup, and repeated a fresh
partial install with the final reader-free observer. It then verifies the fresh
shell, all manifest hashes, registry version, absence of pending/partial files,
and absence of all test-owned installer/engine processes.

`capture-dwm.ps1` uses the existing wizard's DWM thumbnail in a short-lived preview
and captures that responsive preview. It does not send input to or resume the
installer. The resulting image was visually inspected. This is the same method
documented in the [v306 follow-up](../win-v306-followup-2026-11-06/COMMANDS.md).

Raw stderr is preserved with `streams/*.stderr -text`. PowerShell files were
parsed before executing them. Diagnostic programs write only evidence/build
outputs except the explicitly requested native installation, preservation and
restoration steps. The installation cannot be treated as a release acceptance.

The two raw pending manifests also use `-text` to preserve their original CRLF
bytes. The ordinary Git whitespace check flags those retained CR characters;
`git -c core.whitespace=cr-at-eol diff --cached --check` passes without changing
repository settings or raw evidence. `audit-handoff.py --staged` verifies the
staged stderr and pending-manifest blobs byte-for-byte and confines the staged
paths to this evidence package and the two Sarvam handoff documents.
