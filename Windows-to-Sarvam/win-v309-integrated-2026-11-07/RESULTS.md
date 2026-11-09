# Final integration with concurrent main changes

Publication note: subsequent upstream v310 (`1cfab051`) arrived after this validation. This report describes the pinned v309 repair, not v310 execution; the final handoff on main records the newer upstream context. The merge described below resolved conflicts against `3adae819`, before v310.

**Current source/review head: `7ab8c439075b91278dd0e96bf000140a0ed26cf5`, [draft PR #68](https://github.com/dap2810/Sutram/pull/68). Current installed setup: `ffed7a486b0b3eab86c5a76afea32bc606e6b8b24feca4d8bc546cac99c9f0d7`.** Independent acceptance remains pending.

Main advanced to `3adae819` while the [full final-candidate validation](../win-v309-final-fixes-2026-11-07/RESULTS.md) was completing. Its R140 packaging work overlapped this branch. The merge preserves upstream fixed Linux ZIP metadata, timestamp-free Linux linking, payload-scoped LF attributes, release documentation and the extra R140 staging gate. It retains our matching ordinal manifest order, strict UTF-8 normalization, linker-relative imports, payload-only mode and all verified compiler/installer safeguards. Duplicate normalization/reuse blocks were reconciled. An attribute-edit mistake was caught during merge validation and corrected before the merge was pushed or this package built; final attribute validation has no warnings.

[Source equivalence](unchanged-product-code.json) proves the compiler, installer engine, uninstaller, wizard and IDE Git bytes are unchanged from tested `664ff188`. The Windows compiler binary remains `bcb33e6dbb58c1e8556d29057c2f20128cc00f54e48cf860c7ea5496c0972532`. The engine's checkout bytes now follow upstream's LF rule, so the embedded engine hash changes, without changing script semantics. [Payload delta](integration-check.json) contains only four documentation files and their manifest; all executable/runtime/icon bytes match the extensively tested candidate.

Verification after resolving the merge:

- Native setup build and embedded self-test pass.
- R130 **16/16**, R134 **29/29** (the extra upstream reuse gate is retained).
- Native reuse/publication **14/14** and two-process lock/snapshot **7/7** pass again.
- Real Linux payload build and Windows comparison: **657 files plus manifest byte-identical**.
- All **560** payload text source paths report `eol=lf`; every Linux ZIP entry has the fixed 1980 date.
- Native upgrade reaches Finish with engine **0**; fresh PATH/version and **657/657 installed hashes** match this exact candidate.
- Both integration wizard/engine processes are closed; no pending transaction or installer lock. The earlier run separately verified closure of all 21 recorded processes.
- The successful Finish screenshot was visually inspected. No native acceptance claim rests on PE format checks alone.

The 322 example, 7 arithmetic, 32 OOM, 42/59/21 Windows+Linux compiler checks, forced-budget checks, IDE Run/Save/refusal and full early/late/edited recovery results remain pinned to `664ff188` in the previous evidence folder. They were not re-counted as new runs after this packaging/documentation merge. The product-code and payload-binary equivalence above connect those results to this installed integration; this folder records the new build, payload, fixture and upgrade checks. No full Linux setup was linked here because the Linux cross-linker is absent; no full R140 package gate is claimed for the Windows ZIP, whose dates remain native build dates. No frozen release source pins or generated release binaries were promoted.

Exact current identities:

| Component | SHA-256 |
| --- | --- |
| Setup | `ffed7a486b0b3eab86c5a76afea32bc606e6b8b24feca4d8bc546cac99c9f0d7` |
| Compiler | `bcb33e6dbb58c1e8556d29057c2f20128cc00f54e48cf860c7ea5496c0972532` |
| Embedded engine | `b78783ddbc62a1e9676f2b34c4b40236c8046362eb2153b33e832831d12bf08b` |
| Manifest | `a534c832d00c1052e95d1d3577e2bcdb2c548bc6a3ee041d3facb5a90163943f` |

Local runnable setup: `<repo>\build\windows-v309-fixes\build\native-v309-integrated\Sutram-Setup.exe`. The previous fully tested install was hash-verified and preserved before the upgrade; see [backup record](backup-before-v309.json). The final exact [machine identity](handoff-identity.json), [phase record](initial.json), [screenshot](initial-finish.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*, [payload comparison](payload-comparison.json), and [closed process record](final-processes.json) are retained unchanged.

Commands ran from the review worktree, with `C:\Program Files\mingw64\bin` prepended to process-local PATH:

```powershell
python build/prepare-v309-integration.py
& windows/native-installer/build-installer.ps1
& tests/windows/test_installer_lock.ps1
& tests/windows/test_installer_reuse.ps1
python tests/r130/test_installer_engine.py
python tests/r134/test_install_transaction.py
python Windows-to-Sarvam/win-v309-integrated-2026-11-07/pin-fix-package.py
wsl -d Ubuntu -- git -C /mnt<repo>/build/windows-v309-linux-checkout fetch /mnt<repo> codex/windows-v309-fixes
wsl -d Ubuntu -- git -C /mnt<repo>/build/windows-v309-linux-checkout checkout --detach 7ab8c439
wsl -d Ubuntu --cd /mnt<repo>/build/windows-v309-linux-checkout python3 tools/build_installer_linux.py --payload-only --work build/linux-payload-integrated
python Windows-to-Sarvam/win-v309-integrated-2026-11-07/compare-payloads.py
python Windows-to-Sarvam/win-v309-integrated-2026-11-07/check-integration.py
& Windows-to-Sarvam/win-v309-integrated-2026-11-07/initial-install.ps1
& Windows-to-Sarvam/win-v309-integrated-2026-11-07/verify-saved.ps1
```

The preparation script is included here as `prepare-v309-integration.py`; its executed location was `build/`. It derives the retained harness scripts from the previous evidence folder with separate backup/package paths and verifies unchanged product Git blobs. The same reviewed PE input remains in the Linux checkout. All previous limitations and preserved failures remain visible in the earlier reports. No CI was launched, no security settings changed, and no new round's design questions were treated as permission to broaden this repair.
