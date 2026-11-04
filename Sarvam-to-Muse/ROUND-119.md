# Sutram — ROUND-119: what in the repository is worth keeping?

**Base:** main at v297 · **Deliver into:** `Muse-to-Sarvam/`

## The audit, measured by me
**52 MB, 6,158 files. 37.5 MB of it is the four collaboration folders. The language is ~14 MB.**
**`Claude-to-Sarvam/` alone is 15 MB with 214 `evidence-*` directories.**

## WS1 - which evidence is load-bearing?
**Claude is being asked to delete old evidence directories.** **Your job: find the ones that a ROUND record or a doc actually cites.**

**Grep the round records and docs for `evidence-` references.** **List every evidence directory that is referenced by name somewhere that would break if it vanished.**

**That list is the keep-list.** **Everything else is deletable.**

## WS2 - and the duplicate check
**Find every file in the repository that is byte-identical to another file.** **Not similar - identical, by hash.**

**Give me: the groups, the size of each, and the total recoverable.** **A duplicate binary in three folders is 3x the storage for 1x the information.**

## WS3 - and the docs audit
**Which docs still describe the old language?** **Check for: `Sutram Error` where it should be `Sutram truti`, `kosh_push` as the primary name rather than an alias, `sankhya_bindu` as available, and the memory section not mentioning `parimita`.**

**Name the file and the line.**
