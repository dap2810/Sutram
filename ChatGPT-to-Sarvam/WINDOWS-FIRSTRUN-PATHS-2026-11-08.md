# Windows first-run paths: v312 native results

The owner supplied a separate first-run brief explicitly permitting v312. It does not lift the earlier v313
preflight gate for the v313 acceptance matrix.

**10 PASS / 1 FAIL / 1 SKIP**, on the setup pinned at `079c7b226fe968b3d9b5dfe248f097482f5d1fce`.
Declining PATH works through the actual Start-menu terminal, all four Explorer path cases and explicit Open with
load correctly, and the documentation shortcut opens the installed English book in Firefox.

**Actionable finding:** a pre-existing desktop `Sutram IDE.lnk` is preserved byte-for-byte and remains the only
desktop link under that name. Clicking it opens its original Notepad target. Setup shows no collision warning;
only the engine log records preservation. Keep preservation, but give the user a visible explanation and a clear
route to the installed IDE. This is an observed first-click mismatch, not a human confusion study.

Also correct the visible desktop-option wording: it says “Sutram Terminal,” while the engine manages
`Sutram IDE.lnk`. Open with displays the executable-style name `sutram-ide-gui`; it loads the file correctly.

[Results, exact paths, hashes, raw logs and screenshots](../Windows-to-Sarvam/win-firstrun-paths-2026-11-08/RESULTS.md).
Original installation/settings restored and verified: 672 checks, zero failures. Test artifacts preserved;
no product changes or release acceptance claimed. Pending independent Sarvam review.

Upstream v313 arrived during publication (`d25eb2ad`). This report deliberately retains the exact v312
artifact identity tested under the owner's first-run brief; it does not report v313 acceptance results.
