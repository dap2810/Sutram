# Commands, provenance and evidence boundaries

The supplied Downloads brief is preserved as REQUEST.md. PROJECT-MASTER.md and the design charter were read before work; the v312 project-status changes were read after fetching. The worktree was pinned with:

```powershell
git fetch origin
git worktree add --detach build/windows-v312 06324cef
python build/prepare-v312.py
```

Within that worktree, the evidence directory is `Windows-to-Sarvam/win-v312-2026-11-08`. The preparation script adapts the prior round's UI, package, identity and suite helpers without changing product code. The executed original preparation script lives at the parent checkout's `build/prepare-v312.py`; the copied script is retained as provenance of that workspace-specific operation.

```powershell
python Windows-to-Sarvam/win-v312-2026-11-08/pin-fix-package.py
& Windows-to-Sarvam/win-v312-2026-11-08/state.ps1 -Name before-install
& Windows-to-Sarvam/win-v312-2026-11-08/install.ps1 -Phase licence -Name initial
& Windows-to-Sarvam/win-v312-2026-11-08/licence-details.ps1
& Windows-to-Sarvam/win-v312-2026-11-08/install.ps1 -Phase licence -Name capture-retry
# All relevant screenshots were inspected before continuing.
& Windows-to-Sarvam/win-v312-2026-11-08/install.ps1 -Phase complete -Name capture-retry
python Windows-to-Sarvam/win-v312-2026-11-08/budget.py
python Windows-to-Sarvam/win-v312-2026-11-08/inventory.py before-uninstall
& Windows-to-Sarvam/win-v312-2026-11-08/state.ps1 -Name before-uninstall
& Windows-to-Sarvam/win-v312-2026-11-08/start-uninstall-observer.ps1
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action open
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action search
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action menu
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action uninstall
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action confirm
python Windows-to-Sarvam/win-v312-2026-11-08/inventory.py after-uninstall
& Windows-to-Sarvam/win-v312-2026-11-08/state.ps1 -Name after-uninstall
& Windows-to-Sarvam/win-v312-2026-11-08/settings.ps1 -Action inspect
& Windows-to-Sarvam/win-v312-2026-11-08/install.ps1 -Phase licence -Name reinstall
# Reinstall licence capture also inspected before continuing.
& Windows-to-Sarvam/win-v312-2026-11-08/install.ps1 -Phase complete -Name reinstall
python Windows-to-Sarvam/win-v312-2026-11-08/time-suite.py
& Windows-to-Sarvam/win-v312-2026-11-08/final-check.ps1
python Windows-to-Sarvam/win-v312-2026-11-08/report.py
```

## Observational/harness issues, preserved rather than promoted to product failures

- The first wizard advanced and closed outside the scripted actions. Its initial three licence captures are valid; the five `licence-line-*.png` supplemental captures show Location, not licence. Those invalid images remain only in the local worktree. The supplemental JSON's font/text queries are retained, with this limitation. The retry captures explicitly checked the licence control was visible.
- An exploratory `identity.py --name observed-current-identity` call after that closure failed because there was no installation/manifest. No identity success was claimed; the complete later install passed identity before tests.
- A Settings menu disappeared between tool calls; the first uninstall-menu invocation stopped with `Uninstall menu item missing` before invoking anything. The helper was changed to reopen and invoke the scoped Sutram menu in one operation. The confirmation button's actual UI Automation ID was read before invocation.
- The first final Settings screenshot was occluded by the pre-existing Codex Terminal. It is retained locally as `settings-uninstall-final.png`, excluded from publication. The helper now foregrounds Settings immediately before capture; `settings-uninstall-final-recheck.png` is the inspected result.
- The reinstall Finish screenshot was skipped when the intended window could not be foregrounded; reinstall-install.json records finish_screenshot as null. Completion is supported by the observed Finish label, engine exit 0, wizard closure and subsequent identity check. The first successful installation's Finish screenshot was captured and inspected.
- Full Settings UI dumps contain unrelated account/application information and remain only under local `build/native-v312/settings-*.json`. Published screenshots capture just the Apps content region, excluding account identity. The exact capture method is in settings.ps1.
- The initial final-check CIM query was denied in the sandbox; the same read-only check succeeded with approved host access. Host access was also approved for GUI and native installation operations. The final Windows token was not elevated to administrator.
- A convenience console print of Settings timing failed on CP1252's inability to print U+200E; its JSON file was intact. This is a reporting-shell encoding issue, not a Sutram result.
- Report validation caught a helper encoding defect: install.ps1 reloaded its UTF-8 JSON without an explicit encoding when continuing the wizard, so Windows PowerShell 5.1 corrupted the duplicated licence_text field in capture-retry-install.json and reinstall-install.json when saving the completion record. The direct `*-licence.txt` captures and screenshots were never changed and are the authoritative text/rendering evidence; the direct capture exactly equals LICENSE.txt with CR LF. Original JSON records are retained unchanged to expose this defect. The helper now explicitly reads UTF-8; this correction does not change native observations or require another installation. A diagnostic print also hit the reporting console's CP1252 limit. No product encoding defect is inferred from those helper errors.
- WSL distributions were listed while considering the literal-shape discrepancy, but no Linux comparison was executed. No additional test result is inferred from that listing.
- No manual cleanup, registry clearing, backup movement or file deletion was performed for this round. Existing backups and registry archives stayed in place. The setup's own temporary staging cleanup and uninstall's own removals are the product behavior under test.

The generator asserts the reported identity, suite counts, licence text, registry/PATH cleanup and process exits against saved JSON. `.gitattributes` disables line-ending conversion for this evidence directory. EVIDENCE.sha256 covers every published file except itself. Product acceptance remains for the release review.
