# Final v309 repair: implemented, installed and verified

**Dated validation candidate. The later [integrated package at 7ab8c439](../win-v309-integrated-2026-11-07/RESULTS.md) is now installed; the results below remain pinned to 664ff188.**

Source/product commit **664ff1889d23d37e10318a4c2d1950ce6cdb115e**, [draft PR #68](https://github.com/dap2810/Sutram/pull/68). This final candidate supersedes the earlier same-day packaging-only candidate. Independent Sarvam acceptance is pending. This evidence does not promote release binaries or frozen source pins.

## Fixes

- LF text policy and normalization during packaging; Windows/Linux ordinal manifest ordering; adjacent Windows linker import libraries.
- Recovery reuses an installed file after checking its incoming hash. Publication refuses a changed or missing reused target before moving the only copy. Existing ownership/reparse checks remain.
- The concurrent R208 global-initializer finding was reproduced: **21 of 42 expanded cases failed before**. Global initializers now receive expression validation and the global ownership check. Global/local analysis contexts are separated. The validator uses a separate traversal stack and refuses budget exhaustion. See [entry-point audit](ENTRY-PATHS.md).
- The installer now acquires its destination lock before registry/discovery, old-state and pending reads. A real two-process fixture exercises refusal while held and fresh ownership reads after the prior owner updates state and releases it.

## Final package verification

| Check | Result |
| --- | --- |
| Global/local regression cases | 42/42 native Windows and 42/42 native Linux |
| Existing R137 slice gate | 59/59 on each platform |
| Existing R134 ownership predicate | 21/21 on each platform |
| Forced analysis exhaustion | Local and global refuse; production source unchanged |
| Native Windows example suite | 322 PASS; 3 without expectations; 6 deliberate skips; no failures |
| Requested arithmetic probes | 7/7, including original add/XOR and valid length |
| Requested native Job Object limits | 32/32; exact 32-byte stderr, LF, exit 1; no stack-overflow status |
| Existing installer gates | R130 16/16; R134 28/28, including four actual ownership reads |
| Native file/lock fixtures | 14/14 staging/publication; 7/7 lock/snapshot checks |
| Windows/Linux payload | 657 entries plus manifest byte-identical; same reviewed PE input |
| Installed CLI | Both bin/win layouts compile an imported library from unrelated cwd and print 81 |
| Native IDE | Hello Run, refused-load Save protection, global compiler refusal pass; original files unchanged |
| Final installed identity | Canonical PATH/v309; 657/657 hashes; exact candidate manifest/uninstaller |
| Final owned processes | 21/21 closed; no installer lock or pending transaction |

Native Linux means Ubuntu under WSL, with a freshly assembled ELF host from the canonical NASM entry. Its three compiler gates execute real Linux outputs. The Linux package comparison uses payload-only mode and the identical newly built Windows PE input; no Linux-linked setup or Wine install is claimed. Full ZIP/executable reproducibility is not claimed.

## Native installation/recovery

| Phase | Result | Seconds | Engine | Files present | Reused | Staging copies |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| initial | FINISH | 22.46 | 0 | 657 | 655 | 2 |
| d1-stop | INTERRUPTED | 0.37 | -1 | 0 | 0 | 0 |
| d1-retry | FINISH | 27.30 | 0 | 657 | 0 | 657 |
| d2-stop | INTERRUPTED | 26.09 | -1 | 657 | 0 | 657 |
| d2-retry | FINISH | 22.77 | 0 | 657 | 657 | 0 |
| d3-stop | INTERRUPTED | 17.40 | -1 | 56 | 0 | 657 |
| d3-retry | ERROR_DIALOG | 9.72 | 1 | 56 | 0 | 0 |
| final-upgrade | FINISH | 22.44 | 0 | 657 | 657 | 0 |

Early retry and final upgrade complete normally. D2 stops after all files are published while pending metadata remains; it is **not a torn-journal-write test**. D3 stops after 56 published files, then deliberately edits docs/BUILDING.md: retry refuses and preserves the exact edited SHA-256 `ecf1de53b67cb8cdfc1550aaabb17cba074173b32fa3a356102574aa31c9bcd9`. The edited tree/transaction remain preserved at the paths in [restore-after-d3.json](restore-after-d3.json). The verified working installation is restored and the final upgrade succeeds. Timings vary and are not a performance claim.

The first recovery attempt's early retry actually reached Finish, engine 0, but the screenshot helper rejected a lost-foreground capture and marked OBSERVER_ERROR. Its raw records and controller error are retained in [recovery-attempt1](recovery-attempt1/). The helper now retries foreground acquisition and records skipped captures without aborting installation observation. The complete rerun passes. `dialog_closed` is a legacy misnamed field recording wizard exit during the five-second acknowledgement wait; the error dialog's dismissal is not inferred from that field.

The final process observer initially treated JSON arrays as process records (PowerShell's null-property enumeration); this caused a PID-0/null-start-time error both inside and outside the sandbox. The observer now accepts only individual records with explicit pid/start fields. Both errors are retained. A mistyped R130 command and initial temporary-directory sandbox restrictions are also disclosed in [commands](COMMANDS.md). No product failure is hidden by these observer corrections.

## Identity and limits

- Setup: `2751711704d0c48e4623ce0e700fa7e58e868764f8363ba4baf78986acbb2299`
- Compiler: `bcb33e6dbb58c1e8556d29057c2f20128cc00f54e48cf860c7ea5496c0972532`
- Engine: `9eb6174c35ef43e3a02ff792b1e3b187558f693c005a93d66719fe65dadd3e53`
- Manifest: `53d8102fde97f51e43deda3c03232ab7e25226096d254a797c9cd32e5e8ce12d`
- Local setup: `<repo>\build\windows-v309-fixes\build\native-v309-final-fix\Sutram-Setup.exe`

This is the working installed candidate, with original/working/interrupted/edited trees preserved. New source remains in PR #68; main carries handoff/evidence only. Native IDE checks above are specific exercised scenarios, not every IDE or uninstall acceptance gate. No uninstall, arbitrary concurrent-write proof, 15-minute timeout, full Linux example suite, general security-product compatibility, or universal language safety is claimed. No security settings, frozen baselines, workflow files or automatic CI triggers were changed. Release source pins intentionally still describe upstream v309 and must be updated only after independent review/rebuild.

Read [commands and provenance](COMMANDS.md), [all summary values](summary.json), [successful wizard](initial-finish.png), [IDE refusal screenshot](C3-global-refusal.png), [payload comparison](payload-comparison.json), and [final process evidence](final-processes.json).
