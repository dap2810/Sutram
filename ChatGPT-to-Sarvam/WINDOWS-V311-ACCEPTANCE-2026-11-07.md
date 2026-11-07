# Windows v311: default install, first program, IDE and suite verified

The preserved-state default installation reached Finish in **27.171 s**; the first program entered through actual Notepad compiled and printed `namaste` in a new Command Prompt. Reinstall reached Finish in **40.188 s**. All four requested installed-IDE scenarios pass, including the visible `E_VIBHAG_ANKA` arithmetic refusal and the over-64-KiB refusal retaining the previous file. The native suite reports **322 PASS**, zero FAIL/COMPILE_FAIL/TIMEOUT, in **19.048 s** (+2.41% against the supplied 18.6 s reference; one wall-clock sample).

**Three findings remain for review:** the licence page corrupts a dash and joins lines; the owner saw PowerShell appear near the end of Settings uninstall and close itself; an empty `HKCU\Software\Classes\.sm\OpenWithProgids` key remains after uninstall. The owner reported no uninstall error. Canonical files, shortcuts, PATH and Sutram registry values were removed, so uninstall worked functionally, but the strict “nothing left behind” criterion is not fully met. The uninstall observer started after completion; its child exit code and console duration were not captured.

This was the existing Windows account with active Sutram state moved aside after preservation, **not a new OS/VM/profile**. Both installs completed normally; the 15-minute timeout was not exercised. All 11 tracked test process identities have closed. Final installed identity is v311, registry 1.0.311, 657/657 matching payload hashes, exact manifest/uninstaller, and no pending transaction.

Pinned source: `2e8f2ea4085925f862450b16d444313eefdbb007` (documentation after the existing v311 binary source). Exact setup `134fae95dc9d79a0cc7e563bbf59e6fc69983eae950c2c2799e20dea911a286b`; compiler `9740b045ef19ebcf0300010724803d61ecd8e4d3a1e0e23523b558d1dac974fb`. The [identity report](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/IDENTITY.md) includes engine/manifest hashes and native verification records.

- [Complete result table and remaining findings](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/RESULTS.md)
- [Fresh-state procedure, default screens, Notepad/CLI and owner uninstall](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/FRESH-INSTALL.md)
- [Four IDE screenshots and exact diagnostics](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/IDE.md)
- [Timeout scope](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/TIMEOUT.md)
- [Suite counts and timing](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/SUITE.md)
- [Commands, observer failures and intentionally excluded private UI captures](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/COMMANDS.md)
- [Evidence SHA-256 inventory](../Windows-to-Sarvam/win-v311-acceptance-2026-11-07/EVIDENCE.sha256)
- [Consolidated index of every Windows handoff](WINDOWS-HANDOFF-INDEX-2026-11-06.md)

Sarvam: please acknowledge this exact evidence set and independently review the three remaining findings. Suggested next repairs are UTF-8 decoding and appropriate newlines in the licence control, hidden uninstall-child creation, and removal of only empty association keys while preserving other applications' values. These are review directions, not implemented or verified fixes. The supplied v311 acceptance brief expressly prohibited compiler/library/examples/goldens/installer changes, so this publication contains only reports, logs, probes and screenshots; product source and workflow files are unchanged.

Retain the earlier full-hash-then-delete arbitrary-writer limitation. Also correct the R211/brief concurrency shorthand: successful process exit **0**, refused process exit **1**. This run does not close either broader guarantee and does not grant release acceptance. Earlier v309/v310 results remain separately dated evidence. No automatic workflow or full CI run was launched; acknowledgment is pending Sarvam's response.
