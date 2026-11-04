# ROUND-119 — What in the repository is worth keeping?

Base: v297 (worktree at `c803cc07`, current main). All counts below were measured on this tree, not carried from the brief (the brief's numbers differ — see the note at the end — and the measured ones are the ones to use).

## WS1 — which evidence is load-bearing? (the keep-list)

**104 of the 108 `evidence-*` directories are cited by name in a round record or a doc, and all 104 are cited as FILE PATHS** (`evidence-r116/guard.txt`, `evidence-r15/proofs/...`, etc. — the citing record points to a file inside the directory, so deleting the directory breaks the reference). The keep-list is therefore 104 directories, 10.5 MB. The full list is in `r119_keeplist.txt` (one directory per line, sorted).

**Only 4 directories are never cited anywhere** — not by name in any `.md` round record or doc, not by basename in any other file type (scripts, logs, JSONs were also checked), and not as a file path. Those four are the deletable set, 0.3 MB total:

| Directory | Contents | Size |
|---|---|---|
| `Claude-to-Sarvam/evidence-r42-windows` | README + a run-transcripts file | 12 KB |
| `Claude-to-Sarvam/evidence-r44` | gate/guard logs (xvfb, linux-elf, linux-pe, wine) + pairguard.py | 92 KB |
| `Claude-to-Sarvam/evidence-r47` | gate/guard logs (xvfb, linux-elf, linux-pe) | 88 KB |
| `Claude-to-Sarvam/evidence-r52` | gate/guard logs (xvfb, linux-elf, linux-pe, wine) + test_r52 | 116 KB |

**The headline for WS1: deleting "old evidence" saves almost nothing (0.3 MB).** Round records systematically cite their evidence directories as file paths, so nearly every directory is load-bearing by the brief's own criterion. If storage is the goal, the savings are in WS2 (duplicates), not in deleting cited evidence — and deleting the 4 uncited directories is safe but small (they are orphan gate/guard logs whose rounds never cited them).

## WS2 — the duplicate check (byte-identical, by SHA-256, all 6,191 files)

**171 duplicate groups, 1,169 files, total recoverable 3.37 MB** (3,529,924 bytes — the sum over groups of (copies − 1) × size). The full group list (hash → files) is in `r119_duplicates.json`.

| Category | Groups | Files | Recoverable |
|---|---|---|---|
| Evidence guard logs (same output saved under ELF/PE/Wine names) | 92 | 321 | 2.58 MB |
| Binaries (`sutram.exe` = `win/sutram.exe`) | 1 | 2 | 0.49 MB |
| Images (`ide-open.png` × 3) | 1 | 3 | 0.22 MB |
| Other (mostly small files; includes 66 empty `.compile_fail` markers, 0 bytes) | 72 | 766 | 0.08 MB |
| Windows acceptance (tiny text files) | 5 | 77 | 491 bytes |

Two corrections to the brief's hypothesis: (a) the "duplicate binary in three folders is 3x" case does not occur — the installer binaries in different folders are DIFFERENT versions (different hashes: `Sutram-Setup.exe` 1.5 MB, `Sutram-Setup-v297.exe` 1.9 MB, `Sarvam-to-ChatGPT/Sutram-Setup.exe` 0.6 MB); the only identical binary pair is `sutram.exe` = `win/sutram.exe` (2x, not 3x, 0.49 MB recoverable). (b) The real duplicate mass is guard logs: when the ELF, PE, and Wine guard outputs match (which they do for most rounds), the same log was saved 2–6 times under different platform names (e.g. `evidence-r52/guard-v256-v257-linux-pe.txt` = `...-wine.txt` = `evidence-r53/...-linux-pe.txt` = `...-wine.txt` = `evidence-r54/...-linux-pe.txt` = `...-wine.txt`, 6 copies, 34953 bytes each). Deduplicating those (one canonical log + platform notes, or symlinks) is where the 2.58 MB sits — but note that many of those logs live inside KEEP-list evidence directories (WS1), so deduplication must preserve the cited paths (replace copies with links, not delete cited files, or the WS1 references break).

## WS3 — the docs audit (file + line; living docs only)

Scope note: CHANGELOG, decisions, and `docs/reports/*` are historical records (dated, version-pinned) — they correctly quote old names/messages as they were then, and rewriting them would destroy the record. They are NOT counted as stale below. Only living docs (the reference, the memory model, the vocabulary table, open issues, the tutorial chapter) are judged as current.

**Stale (present the old language as current):**

- **`docs/MEMORY-MODEL.md` — the whole file.** It contains ZERO mentions of `parimita` (the v285 budget) or `parimana`, and it describes the PRE-region kosh growth path (lines 53, 178: "new capacity is doubled or replaced... copies the cells" — the v283 behavior, not the v284+ region behavior of growing in place) using the OLD names throughout (lines 53, 178, 185: `kosh_push/pop/len/cap/clear/empty/peek/enqueue/dequeue` as the API, with no mention of the Sanskrit primaries). This is the most stale living doc: old mechanism + old names + missing parimita.
- **`docs/LANGUAGE-REFERENCE.md:958, 961`** — the §16 aliasing example uses `kosh_push(k, 41)` and `kosh_push(k, 42)` as current code, without noting it is the old alias. Example 288 itself (the same program) uses `kosh_kship` on v297. The example should use `kosh_kship` (or note the alias). Same doc, lines **1162, 1195, 1227** — the escape-rule prose uses `kosh_push` as the name (`kosh_push(k, buf)`, `kosh_push(outer, k)`) rather than as an alias. Contrast with the correct lines in the same doc: 202 (the warning), 207 (the alias table: `kosh_kship` primary, `kosh_push` alias), 919 (`kosh_kship(k, v)` (was `kosh_push`)).
- **`docs/_newchapter_en.html:21, 22, 34, 35`** — a chapter whose header says "What is new — the current language" and "Everything in it is part of the language TODAY", using `kosh_push(xs, 10)`, `kosh_push(xs, 20)`, `kosh_push(temps, 36.6)`, `kosh_push(temps, 37)` in examples. A living tutorial presenting the old name as current.
- **`docs/vocabulary/VOCABULARY-TABLE.md:108`** — presents `sankhya_bindu` as the CHANGE for `sankhya_dot` ("bindu is 'point'") with NO withdrawal note. The table is pre-v295 (it contains zero mentions of "withdrawn") and pre-v292-final in other rows too (`kosh_aayam` for `kosh_len`, but the actual v292 name is `kosh_gan`; `likha_roop` for `likha_fmt`, but the actual name is `likha_rup`). As a proposal table it should carry a "superseded by v292/v295" note, not silent edits — but as a current reference it is stale.
- **`docs/OPEN-ISSUES.md:86` (section C, C1/C2)** — lists the English kosh names (`kosh_push`, `kosh_pop`, `kosh_cap`, ...) and `pankti_len` as an OPEN issue ("English still in the language"). v292 resolved this (Sanskrit primary, English alias) — the issue is closed but still listed as open.

**NOT stale (correctly historical, do not rewrite):**

- `docs/CHANGELOG.md` (including line 190, which quotes v285's `Sutram Error [E_PARIMITA]` message as it was in v285 — historically correct, since v285 predates the v294 Error→truti change). The CURRENT message is correctly given in the reference §19:1333 (`Sutram truti [E_PARIMITA]`).
- `docs/LANGUAGE-REFERENCE.md:225, 233` ("v293 it was `Sutram Error`", "A program built by v293 or earlier still prints `Sutram Error`"), `docs/SANDESH.md:6` ("The token was `Sutram Error` up to v293"), `docs/WHATS-LEFT.md:52, 68` (struck-through items marked "Done in v294"), `docs/decisions/R114-SUTRAM-TRUTI.md` (the decision that made the change), `docs/decisions/MEMORY-DECISION.md:68` (quotes the pre-v294 message in a decision record).
- `docs/reports/*` (KOSH-BUILTINS, KOSH-REUSE, LAGHU-EXAMPLE, NEGATIVE-CORPUS) — dated reports pinned to specific versions (e.g. "verified on compiler v253"); their old-message quotes are evidence, not specs.

**And the positive result for the other two checks: NO living doc presents `Sutram Error` as the current token** (the reference uses `truti` throughout), and the reference's memory section DOES mention `parimita` (§19, lines 1315–1359, plus line 442) — it is only `MEMORY-MODEL.md` whose memory section omits it.

## Counts note (measured vs brief)

Brief: "52 MB, 6,158 files. 37.5 MB of it is the four collaboration folders. `Claude-to-Sarvam/` alone is 15 MB with 214 `evidence-*` directories." Measured on this tree: **74 MB working tree, 6,191 files; collaboration folders (Claude 18 MB + ChatGPT 7.0 MB + Muse 5.3 MB + Sarvam 0.5 MB) ≈ 31 MB; `Claude-to-Sarvam/` has 108 `evidence-*` directories** (all of them in that folder; none in the other three). The brief's 214 does not match any count I can reproduce (108 directories; the files inside them number in the thousands). The WS1/WS2/WS3 answers above use the measured numbers.

NOT RUN: Windows, browser, implementation (none authorized — this is an audit, not deletions or doc edits; nothing was deleted or rewritten), full suite (no tree changes).
