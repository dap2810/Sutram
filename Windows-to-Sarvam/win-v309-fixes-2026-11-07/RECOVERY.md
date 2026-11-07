# Native recovery after the fix

The real rebuilt wizard/engine were used, without changing security settings. Initial upgrade, early-stop retry, late-stop retry and two same-folder confirmations reached Finish with engine exit 0. Only captured test wizard/child handles were stopped; all 18 processes are closed.

**Early stop:** after 0.371 s, engine age 0.358 s, before any payload file or pending transaction. Retry finishes in 26.51 s. There is no previous-attempt notice because no state had yet been written. [Stop](d1-stop.json), [retry](d1-retry.json), [log](d1-retry-engine.log).

**Late stop:** after 25.40 s, all 657 payload files exist and the pending record remains. Retry logs **657 Already installed**, **0 START/DONE staging copies**, then completes in 22.30 s. It still extracts/verifies the incoming package and rechecks ownership. [Stop](d2-stop.json), [journal](d2-stop-journal.txt), [retry](d2-retry.json), [log](d2-retry-engine.log). This catches the last-file/pending-record boundary, not a torn journal write.

**Owner edit:** interrupted with 57 published files, appended `\nV309 OWNER-EDIT RECOVERY PROBE: preserve this line.\n` to BUILDING.md, and retried. The engine exits 1 before replacing it, naming the file and giving recovery instructions in the [log](d3-retry-engine.log). The [dialog](d3-retry-error.png) gives a generic failure/log notice. Edited SHA-256 before and after: `ecf1de53b67cb8cdfc1550aaabb17cba074173b32fa3a356102574aa31c9bcd9`. [Recorded edit check](d3-edit-result.json).

The edited tree and transaction remain intact at:

```text
C:\Users\dmech\AppData\Local\Programs\Sutram-v309-fix-after-d3-20261107-113327
C:\Users\dmech\AppData\Local\Programs\Sutram-v309-fix-after-d3-20261107-113327.transaction
```

The known-good candidate backup was restored and verified ([inventory](restore-after-d3.json)). Final installed manifest/uninstaller exactly match the candidate, not merely a compiler with the same v309 version. [Final identity](handoff-identity.json).

## Observer fixes and honest visual evidence

Next/Install/Finish/error-OK clicks are posted asynchronously; waiting for a closing dialog to return a synchronous message no longer raises the previous observer error. D3 has `ERROR_DIALOG`, engine 1, no `observer_error`, and cleanup closes the wizard. The historical JSON field `dialog_closed` actually measures whether the **wizard process** exited during the five-second post-click wait; False there does not describe the dialog's visibility. The wizard subsequently exits on the cleanup close message.

PrintWindow still produced a partial client-area capture in [D2's retained image](d2-retry-finish.png), despite visible Finish controls and a completed engine. The helper was changed to capture the actual foreground owned window rectangle with DPI-aware coordinates. An initial confirmation ran before that edit was applied (a local optional image-library import failed); its successful install remains [recorded separately](final-upgrade.json). No dependency was installed. The corrected helper then captured [the full completed wizard](capture-confirmation-finish.png), and that confirmation finished in 22.15 s with 657 reused targets and 0 staging copies. The previous helper is archived as [ui-helper-before-capture-fix.ps1](ui-helper-before-capture-fix.ps1).

No unattended PowerShell/setup processes or pending installation state remain. No 15-minute timeout, general security-product behavior or IDE acceptance is inferred from these finite successful runs.
