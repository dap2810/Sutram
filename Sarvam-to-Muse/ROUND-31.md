# Sutram — ROUND-31: Sarvam → Muse

**Base:** main at **v246** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` at the repository root, and `READ-FIRST.md` in this folder.

**Sanskrit only until v1.0 is finished.** Gujarati, Hindi and the other eight packs are FROZEN - they stay in the
tree and keep working, but no new development goes into them. **A frozen-pack defect is REPORTED, not fixed.**
**The language must remain multi-language capable** - the pack mechanism, the packs, the fonts and the diagnostics
pipeline stay exactly as they are.

## Part 1 — Why you are being asked now

**Claude is unavailable until next Tuesday, and Claude was carrying the main-channel work.** **So its round comes
to you.** Muse has been idle since ROUND-30 (16 October); main has moved from there to v246.

**Where the project is, measured by Sarvam on a fresh clone:**

| Check | Result |
|---|---|
| main | **changelog v313, compiler v246** |
| crash corpus | **227 cases + manifest, 0 failed** |
| library proofs | **223 passed, 0 failed** (4 GB limit and unlimited) |
| layers | **14 core, 9 alloc, 1 std** |
| alloc bounds | **25 allocations, 6 bounded, 19 exempt, 0 failed** |
| gates | **34 PASS / 0 FAIL / 1 NOT-RUN** |

**And what has landed since you were last asked:** our own linker (`sutram-link`, NASM, no libc), the object
format, an ELF reader, separate compilation, module state, incremental rebuilds, **the C FFI on Linux and
Windows**, and a Windows installer + IDE that **passed 16 required checks on real Windows, not elevated.**

## Part 2 — The work (Claude's round, reassigned)

### WS1 — THE NUMBERS AUDIT: measure the counts
**Run `tools/doc_counts_gate.py`. Fix what it reports. REPORT WHAT IT DOES NOT CATCH.**
Check against the tree: `README.md`, `PROJECT-MASTER.md`, `PROJECT-OVERVIEW.md`,
`docs/sutram-scorecard.html`, `docs/sutram-project-status.html`, `docs/sutram-design-parameters.html`.

**You own the NUMBERS** (measurable). **ChatGPT owns the PROSE** (readable). Do not both do both.

### WS2 — THE FULL TEST RUN, and the suite line Sarvam could not capture
```
sh tools/gates.sh                 -> state the count, environment named
python3 tests/run_tests.py        -> Sarvam could NOT capture this line. Report it exactly.
python3 tools/crash_corpus.py --compiler ./sutram_compiler
python3 tools/proof_lib.py --compiler ./sutram_compiler
python3 tools/proof_props.py --compiler ./sutram_compiler
python3 tools/check_layers.py
python3 tools/check_alloc_bounds.py
unittest suites: r66 r67 r68 r69 r70 r22 r23 r25 r28 r29 r30 r31 r34 r35
```
PASS / FAIL / NOT-RUN separately. Name the environment per check.

### WS3 — THE GUARD
**476 byte-identical, 0 DIFFER on both platforms, held four rounds.** State this round's number.

### WS4 — your own capability work, one sentence of reasoning first
**Everything blocked by architecture is built.** Say what fits next.

## Part 3 — Constraints
Least privilege. **Push with git.** PASS / FAIL / NOT-RUN separately.

## Part 4 — What NOT to do
- **Do not touch `backups/`** - a deliberate full snapshot the owner asked for. Not build output, not a stray zip.
- **Do not develop a frozen language pack.**
- **Before reporting a finding as NEW, check the tree** - a later commit may already have fixed it.
