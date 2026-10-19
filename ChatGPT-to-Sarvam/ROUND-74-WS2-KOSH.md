# Round 74 WS2 — kosh reclamation

**Status: NOT_RUN for native integration.** No compiler changes were made in this round.

Incoming requirement: integrate reclaimed `kosh` backing storage into current compiler, execute integer/float growth, and compare retained mappings A/B.

Verified contextual facts:
- `main` is at v176, while R73's staging helper exists in the still-open draft [PR #36](https://github.com/dap2810/Sutram/pull/36), not at `tools/r73_reclaim_prepare.py` on `main`.
- Previous R73 staging verified source anchors only; Sarvam needs a current-source pin and full NASM build before use.
- Linux `munmap` reclamation does not justify Windows semantics. Raw element addresses may become invalid after growth; this needs explicit aliasing and tests.

**NOT_RUN:** applying staging to v176, building patched compiler, running integer/float .sm programs, measuring /proc/self/maps or retained bytes, Windows memory release, regression acceptance.

Reason: no complete local checkout and no NASM on this host. Do not copy the old R71 source patch onto current v176 or claim a fixed leak.

Sarvam next: reconcile PR #36 against current v176, confirm unique growth anchors, stage on a source-locked branch, compile the actual NASM entry, execute controlled growth and A/B retained-map measurements, verify output and aliases, and hold Windows separately. No `lib/*.smlib` or production compiler files were altered here.
