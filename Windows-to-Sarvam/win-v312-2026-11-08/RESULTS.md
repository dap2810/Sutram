# Sutram v312 — Windows first-contact verification, 8 November 2026

**Devanagari, em dashes, licence line breaks, silent uninstall, the empty Classes key cleanup, the variable-based walk refusal, and all 322 native suite cases are verified on this Windows account. Two product findings remain: clipped licence-page instructions and uninstall's temporary script/log residue.** The illustrative literal sum also reaches a different diagnostic before the walk budget. No release acceptance is claimed.

Pinned source: `06324cefc5c50a3c50fb68b6a2a43f50b800d339`. Windows 11 Home build 26300, non-elevated token, existing account. The canonical installation was absent at the start; older backups and Explorer history were present. No compiler, installer, library, example, golden or workflow changes were made. No CI workflow was launched.

| Test | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| A2.1 — em dash is one character | one | Single U+2014 displayed correctly | PASS |
| A2.2 — lines are broken, not joined | broken | CR LF; text exactly matches licence source | PASS |
| A2.3 — Sanskrit renders as Devanagari | renders | Actual Sanskrit and Hindi lines visibly render | PASS |
| A2.4 — no text truncated at edge | none | Body wraps; instruction label clips “the terms to continue.” | **FAIL** |
| B1 — no console or PowerShell window | none | No new uninstall window detected; pre-existing Codex terminal separately identified | PASS within observed scope |
| B2 — `.sm\OpenWithProgids` gone | gone | Classes key and empty parent removed | PASS |
| B2 — PATH entry removed | removed | Baseline user PATH restored; `where sutram` exit 1 | PASS |
| B3 — nothing survives uninstall | nothing | New temporary directory with script and log survives; pre-existing history/backups separately listed | **FAIL** |
| C1 — 10,000 terms compile | exit 0 | Literal, variable, global all compile and print 10000 | PASS |
| C2 — 20,000 terms refused | E_VAKYA_SEEMA | Variable/global: exact code and 65536, exit 1, no file; literal: earlier tree-capacity refusal | **PASS gate shape; FAIL literal example's exact expectation** |
| D — identity | v312, one path | One canonical path; v312; 657/657 hashes | PASS |
| D — suite | 322 PASS, no FAIL | 322 PASS, 0 FAIL/COMPILE_FAIL/TIMEOUT; 3 NO_EXPECTATION, 6 explicit skips | PASS |
| D — suite elapsed time | compare to 18.6 s | **23.128 s**, +4.528 s / **+24.34%** | RECORDED; materially slower single sample |

Exact first version line: `Sutram 1.0 (v312) - sampurna sutra`. Second line: `Samskrita-mukhya bhasha -> x86-64 yantra-bhasha`.

| Artifact | SHA-256 |
| --- | --- |
| Setup / installed uninstaller | `5cca529c3569d4558cce3243becffea72c0eb2745ea345d8c049bb7177cb3c1b` |
| Installed / repository compiler | `7ac8347032b6d9f754b4706d48c20f32f1a43f58324e4432d5463751031b6f93` |
| Payload manifest | `14673c941e7b76c750d96c5725d121ef71a85bcc9d461b572a494dcaacdb1643` |

Native installation reached Finish in 27.910 seconds; reinstall in 35.512 seconds. Both engines exited 0 and the wizards closed after Finish. v312 remains installed. [Fresh-shell identity and full installed hash comparison](reinstall-identity.json); [embedded payload checks](candidate.json). The native suite used the repository compiler, whose hash equals the installed compiler; [all case records](native-cases.json), [timing](suite-timing.json). The timing includes harness and process startup overhead. One sample is insufficient to attribute the slowdown to the walk budget.

Details: [LICENCE](LICENCE.md), [UNINSTALL](UNINSTALL.md), [BUDGET](BUDGET.md), [survivors](SURVIVORS.md), [commands and evidence limitations](COMMANDS.md). All generated probes and their generator are included. Evidence integrity: EVIDENCE.sha256.

All seven tracked wizard/engine/observer process identities are gone; no Sutram-named process remains in [final-check.json](final-check.json). The user's existing Terminal and Settings were left open. No independent release verdict, broad regression rerun, race-safety proof, font coverage across machines, whole-machine cleanup guarantee, or Linux/Windows literal-shape comparison is claimed.
