# Windows v311 acceptance observations — 7 November 2026

The default installation, first Notepad program, reinstall, four native IDE scenarios and 322 expected-output suite cases pass. **The strict “nothing left behind” uninstall criterion is not fully met:** an empty `.sm\OpenWithProgids` registry key remains. The owner also saw PowerShell appear near the end of uninstall and close itself. The licence page visibly corrupts the dash and joins lines. These observations require follow-up; this report is **not release acceptance**.

This was the existing Windows account with active Sutram installation, registration, shortcuts and PATH moved aside or cleared after preservation. It was **not a new machine, VM or user profile**; intentional backups and unrelated machine state remained. No compiler, library, examples, goldens, installer or workflow was modified. The supplied [brief](REQUEST.md) explicitly prohibits those edits in this round.

| Test | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| A2 — no sutram resolves after removal | not found | where exit 1; INFO: Could not find files for the given pattern(s). | PASS; existing-account scope above |
| A3 — install to Finish | Finish, no console | 27.171 s; engine exit 0; no new console sampled; closes after Finish click | PASS for completion; licence presentation issue below |
| A4 — version in a new shell | v311 | Sutram 1.0 (v311) - sampurna sutra | PASS |
| A4 — first program compiled and run | namaste | namaste; compile/run exit 0 | PASS |
| A5 — uninstall clean, nothing left behind | clean | Canonical install, shortcuts, PATH and Sutram values removed; empty extension key remains; owner reports brief PowerShell window, no error | PARTIAL; strict no-residue criterion FAIL |
| A5 — reinstall | working v311 | Finish 40.188 s, engine exit 0, 657/657 hashes | PASS |
| B1 — IDE runs 01_hello.sm | Namaste, Sutram! | exact expected output | PASS |
| B2 — syntax error, old output cleared | diagnostic, cleared | Sanskrit diagnostic, pankti 2:11; hello output absent | PASS |
| B3 — IDE refuses k[0:1] + 0 | refusal | E_VIBHAG_ANKA; previous diagnostic replaced | PASS |
| B4 — IDE refuses over-64-KiB file | refused, cleared | 81,000 bytes refused; previous editor/title retained; output replaced by refusal | PASS |
| C — timeout observed, or nothing stalled | either | Neither installation stalled | NOT EXERCISED; expected normal path |
| D — native suite | 322 PASS, no FAIL | 322 PASS; zero FAIL/COMPILE_FAIL/TIMEOUT; 3 no expectation and 6 explicit skips | PASS |
| D — elapsed time | compare to 18.6 s | 19.048 s, +0.448 s / +2.41% | RECORDED; one wall-clock sample |

## Findings for Sarvam

1. Licence rendering: [the actual screenshot](first-install-licence.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)* shows a corrupted dash and joined words such as `ThreadCopyright`, `ProjectPermission`, `rightsto` and `sellcopies`. The raw page text is in [first-install.json](first-install.json). Source review finds byte-by-byte widening in `license_to_utf16`, despite UTF-8 licence content, and no LF-to-CRLF normalization. A future repair should decode UTF-8 and supply appropriate multiline edit text, then verify the rendered multilingual page. No repair was made in this verification-only round.
2. Uninstall console: [the owner's observations](owner-uninstall-observation.json) establish a transient PowerShell window that closed on its own, with no error. The late observer did not capture its lifetime or exit status. Native `do_uninstall` launches its PowerShell child with creation flags 0, unlike the install path's CREATE_NO_WINDOW; this is a source-level explanation to review, not a separately measured child trace.
3. Registry cleanup: [after-uninstall-state.json](after-uninstall-state.json) records an empty `HKCU\Software\Classes\.sm\OpenWithProgids`, with no Sutram values. Cleanup should only remove empty keys and preserve other applications' associations.

## Evidence and scope

- [A1–A5, exact screens, CLI and user uninstall](FRESH-INSTALL.md)
- [B1–B4, exact diagnostics and four screenshots](IDE.md)
- [Timeout observation](TIMEOUT.md)
- [Native suite and timing comparison](SUITE.md)
- [Exact candidate identity](IDENTITY.md)
- [Commands, observer failures and omitted private UI captures](COMMANDS.md)
- [Per-file SHA-256](EVIDENCE.sha256)

All 11 tracked application/installer/observer-test process identities are gone in the [final read-only check](final-process-check.json); no child of the failed conhost attempt or test-titled window remains. This count excludes the user-run uninstall, whose PID was not captured. Existing user Settings was left open. The reinstall ended at 15:13:18; the shortcut IDE test began at 15:13:21, so those operations did not overlap.

The suite uses the repository compiler, whose hash equals the installed compiler. The existing full-hash-then-delete race under arbitrary external writers remains outside this round; do not promote earlier fixes to atomic writer safety. The R211/brief concurrency shorthand should read **one process succeeds with exit 0, one refuses with exit 1**, not the reverse. Prior v309/v310 cases were not rerun or presented as new evidence.
