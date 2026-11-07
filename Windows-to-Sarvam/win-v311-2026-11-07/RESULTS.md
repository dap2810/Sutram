# v311 repair verification — 7 November 2026

**Verified the upstream repair of the recovery defect found during v310 testing. v311 is installed and working; no release acceptance is claimed.** v311 arrived while the v310 evidence was being prepared. The owner's brief explicitly permits a later version. Both candidates have separate full native evidence; no product code/library/example/golden/installer changes were made by this verification round.

Source: `fae5319d2abf6dc1368d683b1aa4b80a8831ab5d`. Exact version: `Sutram 1.0 (v311) - sampurna sutra`.

| Artifact | SHA-256 |
|---|---|
| Setup | `134fae95dc9d79a0cc7e563bbf59e6fc69983eae950c2c2799e20dea911a286b` |
| Compiler | `9740b045ef19ebcf0300010724803d61ecd8e4d3a1e0e23523b558d1dac974fb` |
| Embedded engine | `b08e8fcd14611f8e80385b4fc26b43189918a760a4318d2ca6da3083175f1820` |
| Manifest | `710e90b5fdd9bbac9655e45e45935a442902209062eb82a90da44f41e217300d` |

Embedded and installed payloads: 657/657 file hashes match; embedded compiler equals the tested repository compiler; exact engine source bytes occur inside the setup. Final uninstaller hash equals the setup. [Identity](handoff-identity.json), [package checks](candidate.json).

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A direct global kosh | Refuse | Exit 1, E_KOSH_DVARA, no executable | Yes |
| A global kosh + zero | Refuse | Exit 1, E_KOSH_GANIT, no executable | Yes |
| A1 scalar global | 7 | 7, exit 0 | Yes |
| A2 two globals without main | Syntax error | EOF error; with main prints 3 | Literal yes; class inference unsupported |
| A2 record literal | Syntax error | At colon | Yes |
| A2 default argument | Syntax error | At vitti; extra untyped probe fails at = | Yes |
| B nesting | No crash/hang | 0–1022 compile; 1023 clean refusal | Yes |
| C1 superseded suffix | Exact preservation | Matching full hash in suffixed backup | Yes, seeded fixture |
| C2 concurrency | One refuses, no corruption | Actual engines 1/0, 657 matching hashes | Yes |
| C3 live edit | Survives/reported | Exact edit survives | Yes |
| C4 unequal backup | No lost bytes | Refusal names differing copies; both preserved | **Yes: v310 reproduction fixed** |
| C4 ordinary retry | No lost file | Only pending pathname removed; bytes in final manifest | Yes |
| D identity | One canonical path/version | v311, registry 1.0.311, 657/657 hashes | Yes |
| D suite | 322+ PASS, no failure | 322 PASS, 0 FAIL/COMPILE_FAIL/TIMEOUT | Yes |
| E add/XOR | Refuse | Brief/original cases: E_VIBHAG_ANKA, exit 1 | Yes |
| E length | 2 | 2, exit 0 | Yes |

Native installer reached Finish in 23.722 seconds, child exit 0, closed after Finish; [viewed screenshot](initial-finish.png). Suite separately records 3 NO_EXPECTATION and 6 skipped platform/side-effect cases. Additional native fixtures: 19 boundary + 14 reuse + 7 lock assertions, all pass. All 12 full-install test wizard/engine processes are closed; final lock/pending state absent. Original installations and test trees are preserved.

Detailed reports: [INITIALIZER](INITIALIZER.md), [BUDGET](BUDGET.md), [OWNERSHIP](OWNERSHIP.md), [ARITHMETIC](ARITHMETIC.md), [commands](COMMANDS.md). Every probe, raw result, source hash, inventory and relevant screenshot is retained. Evidence hashes are in EVIDENCE.sha256.

Remaining limits: full-hash-then-delete still has an arbitrary-writer race; this test closes the stable unequal-copy defect only. No new OOM claim (not rerun in this requested round), expression-budget exhaustion, gate-mutation validation, IDE/full uninstall acceptance, or cross-platform package reproducibility claim. Historical results keep their own artifact identities. Sarvam must acknowledge and independently review the exact candidate and remaining scope. No CI run was launched.
