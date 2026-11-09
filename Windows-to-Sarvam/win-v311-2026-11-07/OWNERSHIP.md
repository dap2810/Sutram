# v311 ownership — independently verified repair

**The C4 unequal-backup defect reproduced on v310 now refuses safely on v311.** The test ran the complete unchanged engine and ZIP extracted from setup `134fae95dc9d79a0cc7e563bbf59e6fc69983eae950c2c2799e20dea911a286b` at the canonical per-user installation. No product source was edited.

## C1 — suffix preservation

The actual setup GUI was interrupted after 58/657 target files. An ordinary clean interruption has no superseded file; absence is not a pass. A documented synthetic journal-owned intermediate and older backup were then seeded to exercise replacement. The engine preserved the exact intermediate bytes at `transaction/backup/_superseded/docs/BUILDING.md.707D163BD76C`, SHA-256 `707d163bd76c4aa94e9b0c7ef56a25187645b35969a8d0bf589d644cf23e6ec8`. A non-delete-sharing read handle on the later staged compiler deliberately stops its rename and keeps the transaction inspectable. C1 exit 1 is that controlled fixture boundary.

## C2 — simultaneous installer engines

Two complete embedded engine processes launched 0.015584 seconds apart. Exits: [1, 0]. Exactly one proceeds; the other refuses:

```text
[2026-11-07 13:28:58] ERROR: Another Sutram installer or uninstaller is working on %USERPROFILE%\AppData\Local\Programs\Sutram. Let it finish, then run this one again.
[2026-11-07 13:29:19] Installation complete: %USERPROFILE%\AppData\Local\Programs\Sutram
```

All 657 payload hashes match afterward. No target pathname disappeared; only install log/journal/state metadata changed. This is actual engine concurrency, not two wizard windows. The separate lock fixture below tests delayed acquisition/fresh reads with stubbed registry/discovery functions.

## C3 — edit while publishing

A line appended to already-published `docs/BUILDING.md` survived with SHA-256 `4b655917541c30ab4e0304fb5fda2352315356c4c37bb7a25b2bf486a997f8ee`. The observer recorded the engine running, the final compiler not yet published, and that compiler still staged. Installer exit 0. The edited installation was preserved, then a hash-verified baseline restored. [Exact edit and timing observations](ownership/c3-result.json).

## C4 — differing bytes at the expected prefix-name

Same construction as the v310 defect: target bytes declared owned by an interrupted journal; an older backup; the expected 12-hex-prefix filename precreated with unequal bytes. No hash collision is needed. v311 refuses before moving/deleting the target:

```text
[2026-11-07 13:31:06] Not removed - the copy kept as %USERPROFILE%\AppData\Local\Programs\Sutram.sutram-transaction\backup\_superseded\docs\BUILDING.md.31C7B5E5F5BD (BB8F7F7405C17B55C3B8CE2ADBC99B82AC39060A6D3931A8AA70CD7E55295F95) is not this file (31C7B5E5F5BD5DECAD64B3E34C9939E4F5C33C73149B22762BBDFEBC249D4DCE): %USERPROFILE%\AppData\Local\Programs\Sutram\docs\BUILDING.md
[2026-11-07 13:31:07] ERROR: A file was not moved aside, because the copy already kept under its name differs: %USERPROFILE%\AppData\Local\Programs\Sutram\docs\BUILDING.md and %USERPROFILE%\AppData\Local\Programs\Sutram.sutram-transaction\backup\_superseded\docs\BUILDING.md.31C7B5E5F5BD. Nothing was deleted. Move one of them elsewhere, then run this installer again.
```

- Original target hash remains `31c7b5e5f5bd5decad64b3e34c9939e4f5c33c73149b22762bbdfebc249d4dce` at `target/docs/BUILDING.md`.
- Unequal existing backup remains `bb8f7f7405c17b55c3b8ce2adbc99b82ac39060a6d3931a8aa70cd7e55295f95`.
- Engine exit 1; no preexisting target pathname disappeared and no preexisting target file changed bytes.
- The later staged-compiler lock was never reached in this case; the unequal-copy check refused earlier.

[Result](ownership/c4-unequal-existing-result.json), [fixture construction](ownership/c4-unequal-existing-fixture.json), [complete log](ownership/c4-unequal-existing-engine.log), [before/after inventories](ownership/c4-unequal-existing-before.json), [journal](ownership/c4-unequal-existing-after-journal.txt). This closes the reproduced stable unequal-copy case. It does not establish atomicity against an arbitrary writer between a successful equal-hash comparison and deletion: v311 still uses hash-then-delete in the equal-copy branch. Keep that source-level limitation open; moving to a unique backup avoids the deduplication deletion.

## Ordinary interrupted retry: every disappearance

A separate unmodified setup was interrupted after 56/657 files, then completed by retry (exit 0, observed 23.713 seconds). Before/after:

- `payload.pending.sha256`: 710e90b5fdd9bbac9655e45e45935a442902209062eb82a90da44f41e217300d; same bytes at target/payload.manifest.sha256

No other target pathname disappeared; 0 existing target files changed bytes. Final 657/657 installed hashes match. Raw comparisons enumerate both lost pathnames and changed contents; pathname-only checks would have missed the v310 failure.

## Additional upstream native fixtures

The unchanged v311 tests ran in isolated workspace trees: **19 boundary assertions, 14 reuse assertions, 7 lock assertions**, all successful. Boundary coverage includes 18 injected interruption points, 36 stopped-and-rerun upgrades with whole/torn records, absent/equal/unequal superseded copies, suffix preservation, and selected publication-edit windows. These execute AST-extracted actual engine code with deliberate injected boundaries; they are distinct from the full-engine canonical tests above. Lock tests use real child processes but stub registry/discovery reads. Fixture files and full stdout/stderr are under [fixtures](fixtures/commands.json).

Backups and edited/partial trees remain preserved at paths in backup/vacate/restore JSON. Final installation is v311, one fresh-shell compiler, no pending transaction/lock, and all 12 full-install wizard/engine processes closed. Fixture child processes also completed before their successful test exits. No full GUI uninstallation, IDE acceptance, arbitrary-writer safety, or release acceptance is implied.
