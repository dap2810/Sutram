# R95-00 — The root is cleaned: 16 `.md` down to 6, the six you named plus `AGENTS.md`, one roadmap and one summary. Behaviour unchanged.

R95's WS1, WS3 and WS4 were answered in `R96-00`. This is WS2, held back while R96 had priority, and WS5's
audit of it. ROUND-97 is the newest round, and it was answered in `R96-00` as well.

- **Commit on `main`:** this round's commit (parent `98b1915`). It is a `git mv` of 10 files, the reference updates, two pointers, two tool lists, and this hand-back.
- **Compiler: `Sutram 1.0 (v283)` — unchanged**, byte-identical to origin/main's (`sutram_compiler` and `sutram.exe`). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=270`, FAIL=0.** Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 58 PASS / 1 FAIL / 1 NOT-RUN** — the same as before the cleanup. The FAIL is `installer version` (installer v243, compiler v283); the NOT-RUN is Windows execution.
- **The guard, origin/main → this tree: Linux ELF and Linux PE — 680 programs, 549 byte-identical, 131 refused identically, 0 DIFFER, 0 new.** **NOT RUN: the Windows compiler under Wine** — its `.exe` is byte-identical.

## What moved (`evidence-r95/moves.tsv`, all `git mv`, so history follows)

| file | to | why there |
|---|---|---|
| `F7-SCALAR-INDEX-CRASH.md`, `F8-PACK-WARNING-FALSE-ALARM.md`, `ITEM-6-X11-INDIC-ASSESSMENT.md`, `R34-ACKNOWLEDGE.md` | `docs/rounds/` | round work-products. That is R88's rule for them, and your list said `docs/` |
| `TEST-ME.md` | `docs/rounds/` | it is "the Windows ROUND-03 test build (2026-10-18)", a record |
| `ROADMAP-TO-V1.0.md`, `PLAN-TO-FINISH.md` | `docs/rounds/` | archived, unchanged. **`ROADMAP.md` is the one roadmap**, and its first lines now say so and link both |
| `PROJECT-OVERVIEW.md` | `docs/rounds/` | archived, unchanged. **`PROJECT-MASTER.md` is the one summary**, and its first lines say so |
| `COVERAGE-AUDIT.md`, `SECURITY-AUDIT.md` | `docs/reports/` | audits, R88's `reports/` |

**Left at the root:** your six (`README.md`, `LICENSE.txt`, `INSTALL-WINDOWS.md`, `LANGUAGE-PRIORITY.md`,
`PROJECT-MASTER.md`, `ROADMAP.md`) **and `AGENTS.md`**.

- **`AGENTS.md` stays at the root on purpose.** Coding agents look for a file of that name at the repository root;
  it is the convention the file exists for. Moved into `docs/`, no agent would find it.
- Its content is two short sections pointing to `PROJECT-MASTER.md`.

**Archived, not merged.** You offered "merge or archive" for the roadmaps, and "into `PROJECT-MASTER.md`" for the
overview. I archived all three:

- **`PROJECT-OVERVIEW.md` is referenced from 75 files**, and three tools treated it as a current document.
  `PROJECT-MASTER.md` is 30 KB and newer (31 October against 28 October).
- **Merging is editorial:** the two disagree on numbers from different dates. Archiving keeps every word, and
  leaves one file at the root that claims to be current.
- `tools/check_version_strings.py` and `tools/doc_counts_gate.py` no longer treat the archived overview as a
  current document. Both say so in a comment.
- **Your status blocks on `ROADMAP.md` and `PROJECT-MASTER.md` still say v411 / compiler v261.** I didn't rewrite
  your text. The `ROADMAP.md` pointer says the current numbers are in `PROJECT-MASTER.md` and the changelog.

**References: 171 written paths and 3 relative links updated, in 97 files** (`evidence-r95/files-whose-references-were-updated.txt`).

- **Relative links in `.md` and `.html`: 644 before, 647 after** (the three new pointer links), and **5 broken before
  and the same 5 after**. All five are `f](x)`-style code samples, not links.
- **What I left unchanged:**
  - records (`.txt`, `.json`, `.tsv`, `.patch`, SHA-256 lists);
  - Muse's archived copy of an old `doc_counts_gate.py`;
  - `backups/`, `MEMORY-DECISION.md` and the language packs.
- **The tests that mention docs (7 files) give the same results on origin/main and here** (`evidence-r95/doc-tests-before-after.txt`).

## The "duplicate trees" — neither pair is a duplicate, so both stay

- **`windows/` (45 files) and `win/` (11 files) hold different, live things.**
  - `win/` is the Windows *runtime and host*: `native_host.asm`, `winapi.asm`, `winio.asm`, the PE layout and
    import tables, the runtime blob, and the built `win/sutram.exe`. The compiler build includes it.
  - `windows/` is the Windows *build and product*: `build-windows-setup.ps1`, the preflight, the GUI IDE
    (`windows/gui/`, 17 files), the native installer (`windows/native-installer/`) and the integrity manifest.
- **`compiler/` (11 files) is not a second `src/`.** It holds design notes and records:
  - `MODULE_NAMESPACES_R33/R34`, `MODULE_SYSTEM_R40_DESIGN`, three `XMM_*` designs;
  - two round patches and their SHA-256 manifests;
  - one verified assembly snapshot.
  No build or gate reads it. It belongs in `docs/rounds/` by R88's rule. I've left it for now, since its
  patches are referenced by path from partner records. Say if you want it moved.

## Not done

- **The status blocks** in `ROADMAP.md` and `PROJECT-MASTER.md`: they are your text, and still at v411.
- **The `compiler/` folder:** above.
- **The installer rebuild:** it needs Windows, and the gate keeps saying so.
- **Not run:** real Windows.
- **Not touched:** `backups/` (6 files, 9.2 MB, exempt), `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.
