# Windows v303: stop at version gate, installation incomplete

**Not accepted.** The native Windows run requested by
`SUTRAM-WINDOWS-V303.md` stopped at its mandatory version gate.

The canonical installed binary at `%LOCALAPPDATA%\Programs\Sutram\bin\sutram.exe`
executes and reports `Sutram 1.0 (v303) - sampurna sutra`. Its SHA-256 is
`4c05d5cbad99b32be1a38459f1b4b794e00f8b34f89a662ef1ca363c92ec1603`.
But a fresh cmd process using persisted machine/user PATH resolves bare `sutram`
first to `%LOCALAPPDATA%\Sutram\bin\sutram.exe`, which prints `Sutram 1.4.0`.
Thus payload identity is correct while the requested terminal experience fails.

Installer automation timed out awaiting completion. Its engine log ends at
`Copying Sutram files.`; the owner reported manually closing the remaining
PowerShell process. The harness killed its own wizard after the timeout, so
this does not isolate an installer bug from automation interference. Installation
must be treated as incomplete, not accepted from the copied binary alone.

**M1-M5, D1-D2, native suite, IDE execution, oversized-file behavior, and IDE
screenshot: NOT RUN**, honoring the explicit stop rule. No release approval and
no native-suite pass count are claimed. Product sources and goldens are unchanged.

Pinned candidate: `27f4fa74d22d6b246d955941b6e375a7a073c782` (v303). Main had already
advanced to v305; no v305 execution is claimed. Resolve PATH precedence and finish
installer acceptance before repeating the version gate for the chosen candidate.

[Full report and evidence](../Windows-to-Sarvam/win-v303-2026-11-06/RESULTS.md).
Automation is kept separately on review branch
`codex/windows-v303-2026-11-06`, pending independent acceptance.
