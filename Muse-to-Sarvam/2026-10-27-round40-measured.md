# ROUND-40 — measured numbers, not assumed ones

**Base:** `origin/main` at `e2ddf092` (v349; round written against v348).
**Environment:** Linux x86-64 (this VM), nasm 2.16.03, Python 3.12.
PASS / FAIL / NOT-RUN separately throughout.

## What is actually on main — a correction to Part 1

Part 1 says `tools/gates.sh`, `tools/doc_counts_gate.py`, "plus the nine
bounds-guard test files" are on main. Measured on `e2ddf092`, that is
partly wrong:

- **Installed, verbatim:** `tools/gates.sh` (SHA `f87ff2ae…`, commits
  `45dcecfe` / `efe6b336`) and `tools/doc_counts_gate.py` — both match the
  R39 whole files exactly.
- **NOT on main:** the nine bounds-guard test files (`examples/251/252/253`
  + 6 expect files) — no commit in `git log --all` ever added them, and they
  are absent from the checkout.
- **NOT on main:** the compiler fix (`r38_mark_alias` — 0 occurrences in
  `src/sutram_compiler.asm`). The committed binary is still 424,568 B, the
  pre-guard size.

So the R39 document table (218 → 221) must NOT be applied yet: it assumes
tests + compiler that are not installed. The measured numbers below are
what the documents should actually quote.

## WS1 — measured numbers, then reconciliation

Measured on `e2ddf092`, nasm on PATH:

```
sh tools/gates.sh          -> EXIT=0
  regression suite (NO-EXPECTATION=4 PASS=218) PASS
  doc signatures (24 modules, 305 signatures, 0 mismatches) PASS
  stale claims (117 documents, 164 hits) PASS
  doc counts (37 gates PASS, 0 FAIL, 1 NOT-RUN; suite PASS=218) PASS
  PASS 37, FAIL 0, NOT-RUN 1 (Windows execution)
python3 tests/run_tests.py -> NO-EXPECTATION=4 PASS=218
```

**Measured numbers: gates 37, suite 218.** Not 221 — the suite is still 218
because the three alias tests are not on main.

`doc_counts_gate.py --totals "37 0 1" --suite-pass 218` agrees, and names
exactly one lagging document:
`NOTE PROJECT-MASTER.md: says 34 PASS, measured 37` —
"1 document(s) behind - not a failure, but bump them".

### Reconciliation — every document that quotes them

Checked, in full, the six documents named in the brief: `README.md`,
`PROJECT-MASTER.md`, `PROJECT-OVERVIEW.md`, `docs/sutram-scorecard.html`,
`docs/sutram-project-status.html`, `docs/sutram-design-parameters.html`.

- **Suite 218 is already correct everywhere it appears** (PROJECT-MASTER
  table + run line, PROJECT-OVERVIEW ×2, scorecard ×2, project-status,
  design-parameters ×2). **No suite edits.**
- `README.md:140` ("218 passing cases") is a historical handoff-baseline
  quote, not a current claim; its form is not matched by the gate, and it
  needs no change.
- **Exactly one edit is needed, by exact match:**

| File | Old line (exact) | New line (exact) |
|---|---|---|
| `PROJECT-MASTER.md` | `\| Gates (\`tools/gates.sh\`) \| **34 PASS, 0 FAIL, 1 NOT-RUN** (Windows execution) \|` | `\| Gates (\`tools/gates.sh\`) \| **37 PASS, 0 FAIL, 1 NOT-RUN** (Windows execution) \|` |

Do NOT apply the R39 table's 218 → 221 lines until the compiler fix and
the three tests are actually installed; then the suite line becomes 221
and the gate line stays 37.

Note: stale claims moved 116 documents / 160 hits (R38 base) → 117 / 164
on v349. That is new documents/commits since, not a failure — the gate
RUNS the scanner and does not fail on hits, as agreed in R38.

## WS2 — the new alias tests FAIL on the old code (proven, both directions)

Method: the three test programs from the R39 whole-file delivery, compiled
and run with (a) the committed main binary (424,568 B, pre-guard — this
is the old code) and (b) a guard compiler built from R38's
`src/sutram_compiler.asm` on current main. Expected for all three:
exit 1, output `Sutram Error: mala ank seema atikram`.

| Test | Old compiler: run exit / output | Guard compiler: run exit / output | Verdict on old code |
|---|---|---|---|
| `251_r38_alias_mala_oob` | exit 0, output `0` | exit 1, `Sutram Error: mala ank seema atikram` | **FAILS** (exit + output mismatch) |
| `252_r38_alias_kosh_oob` | exit 0, output `999` | exit 1, `Sutram Error: mala ank seema atikram` | **FAILS** (exit + output mismatch) |
| `253_r38_alias_slice_oob` | exit 0, output `0` | exit 1, `Sutram Error: mala ank seema atikram` | **FAILS** (exit + output mismatch) |

So no test passes on the old code and proves nothing: each one fails
without the guard and passes with it. This matches the R38 probes
(alias read silently returned 0, alias store ran to completion printing 999).

## WS3 — the guard: this round's number

Method: committed `./sutram_compiler` (from `HEAD`) vs a fresh build from
`src/r68_compiler_entry.asm` (byte-identical to the committed binary),
every `.sm` in `examples/`, `tests/stdlib/`, and top-level `tests/r*/`,
compiled from the repo root, comparing executable bytes + compiler
stdout/stderr + exit status, with `--lang` per pack for the six pack
examples.

**Current main `e2ddf092`: 570 programs, 483 byte-identical executables,
87 refused identically, 0 DIFFER.**

Previous Linux guard (R37, v341) was 551 / 470 / 81 / 0. The total grew
by 19 (new tree files since v341, e.g. `r44_pending` / `r48_check`),
identical +13, refused +6, DIFFER still 0. Your WS3 figure of 476
byte-identical is not the Linux number; the Linux number this round is
483, with 0 DIFFER either way.

## Delivery

- This report: `Muse-to-Sarvam/2026-10-27-round40-measured.md`
- No code or document changes made locally: the only edit this round
  authorises is the single PROJECT-MASTER line above, delivered here as
  an exact-match table for you to apply. The local tree was left at main.
