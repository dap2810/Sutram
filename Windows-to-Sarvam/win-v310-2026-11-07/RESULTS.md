# v310 native Windows verification — 7 November 2026

**Historical candidate:** v311 subsequently arrived and the same defect was retested. See the [separate v311 repair verification](../win-v311-2026-11-07/RESULTS.md) for the final installed machine state.

**Completed the requested verification. Release acceptance is not granted: C4 reproduces a recovery data-loss defect with controlled test bytes.** Compiler/library/examples/goldens/installer sources and shipped binaries were not changed. The specific [v310 brief](REQUEST.md) overrides the standing repair workflow for this verification-only round.

Tested source: `300c3ee5777d02b609fdbe4db83571e2c53af6cd`. Native version:

```text
Sutram 1.0 (v310) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

| Artifact | SHA-256 |
|---|---|
| Setup | `bb134603d70d49c4abd08112b77a5309ff447280f8754cb4e6e24cb4626bba47` |
| Compiler | `303d6eaca05ae01a1c8ac0a825d81a51965932cda003b0d9e9421e3df63f126c` |
| Embedded engine | `3c0af42def985190f7faeba8aad45566803c9dd4edab3e29dd9cdf30c5c9285e` |
| Embedded manifest | `eb7e29272129507e162ec9d858662be514dc58650e325faedeba340b9b84f643` |

The embedded ZIP contains 657 manifest-listed payload files, all verified; its compiler equals the repository compiler byte-for-byte. The exact engine source bytes occur inside the setup. See [candidate.json](candidate.json).

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A — direct global kosh | Refusal | Exit 1, E_KOSH_DVARA, no executable | Yes |
| A — global kosh + zero | Refusal | Exit 1, E_KOSH_GANIT, no executable | Yes |
| A1 — scalar global | 7 | Native output 7, exit 0 | Yes |
| A2 — two globals without main | Syntax error | End-of-file syntax error; adding main prints 3 | Literal input yes; class inference unsupported |
| A2 — record literal | Syntax error | At colon, exit 1 | Yes |
| A2 — default argument | Syntax error | At vitti; additional untyped case fails at = | Yes |
| B — nesting | Compile or clean refusal | 0–1022 compile, 1023 refuses; no crashes/timeouts | Yes |
| C1 — suffix preservation | Preserved exact bytes | Exact full hash in suffixed backup in seeded recovery fixture | Yes, scoped |
| C2 — concurrent processes | One refuses, no corruption | Engines exit 0/1; lock message; 657 matching hashes | Yes, scoped |
| C3 — edit during copying | Survives or reported | Edit survives; engine exit 0 | Yes |
| C4 — preservation of overwritten content | No lost bytes | Unequal prefix-name backup causes old target bytes to vanish from tree/transaction | **FAIL** |
| C4 — ordinary interrupted retry | No unexplained disappearance | Completes; only pending manifest pathname removed, same bytes in final manifest | Yes |
| D — identity | One path, expected version | Canonical v310, registry 1.0.310, 657/657 hashes | Yes |
| D — native suite | 322+ PASS, no failures | 322 PASS, 0 FAIL/COMPILE_FAIL/TIMEOUT | Yes |
| E — add/XOR | Refusal | Both brief and original cases exit 1, E_VIBHAG_ANKA, no executable | Yes |
| E — length | 2 | Native output 2, exit 0 | Yes |

Suite exclusions: 3 NO_EXPECTATION, 1 SKIP_LINUX_RAW_SYSCALL, 5 SKIP_SIDE_EFFECT_OR_INLINE_ASM. [All cases](native-cases.json). OOM, IDE workflows, uninstall, cross-platform payload determinism and gate-mutation checks were not rerun or newly accepted. Prior reports retain their own artifact identities and counts.

Native setup reached Finish in **15.678 seconds**, engine exit 0, and closed after Finish. [Viewed completion screenshot](initial-finish.png) shows the success page; the helper unchecked Launch IDE after capture. Both interruption tests intentionally stopped only their own wizard/engine. C1/C4 controlled rename failures are explained in OWNERSHIP.md, not mislabeled as ordinary installation failures.

The final ordinary retry leaves a working canonical v310 installation; all 657 payload hashes, manifest and uninstaller match, fresh shell resolves exactly one compiler, and all **12 recorded installer/wizard processes** are closed with no lock or pending transaction. [Final identity](handoff-identity.json), [process closure](final-processes.json). Original v309 and each test installation/transaction remain preserved; see `backup-*.json`, `vacate-*.json`, `restore-*.json`.

Detailed reports: [INITIALIZER](INITIALIZER.md), [BUDGET](BUDGET.md), [OWNERSHIP](OWNERSHIP.md), [ARITHMETIC](ARITHMETIC.md), [commands](COMMANDS.md). Raw observations are retained, including the three corrected harness expectations explained in INITIALIZER.md. Per-file evidence hashes are in `EVIDENCE.sha256` (excluding the manifest itself).

Sarvam action: acknowledge the exact candidate and native results; reproduce/fix C4; retain the class-inference correction and the existing gate/atomicity review limitations; verify the final rebuilt candidate independently. Source fixes belong in a review branch. No CI workflow or automatic run was changed/launched.
