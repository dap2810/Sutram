# ROUND-38 — three approved changes, reported separately

**Base:** `origin/main` at `19c75f88` (R113; round written against v340).
**Environment:** Linux x86-64 (this VM), nasm 2.16.03, Python 3.12. No Windows.
PASS / FAIL / NOT-RUN separately throughout.
**Delivery:** patch + this report in the outbox (NOT direct to main), for a reason
stated at the end. `git push` has no credentials here; the patch is the atomic unit.

## WS1 — wire the five doc checks into `gates.sh` — DONE

**Finding first:** two of the five were already wired — `check_version` (as
"version string") and `check_alloc_bounds` (as "alloc bounds"). The three
missing ones are now added:
- `check_doc_signatures` → gate "doc signatures": PASS iff `RESULT: PASS`.
- `doc_stale_claims` → gate "stale claims": PASS iff the scanner completes
  and reports a count. Hits are review items, NOT failures (the tool's own
  docstring: "Exit 0 always"), so FAILing on hits would permanently break the
  build at 160 hits. This gate makes the scanner RUN in every build; it does
  not pretend a hit is a verdict.
- `doc_counts_gate` → gate "doc counts", LAST. The recursion problem is real:
  `doc_counts_gate` runs `gates.sh` itself when `--gates` is absent. Fix, in
  `tools/doc_counts_gate.py`: a new `--totals "PASS FAIL NOT-RUN"`
  `--suite-pass N` mode, which checks documents against authoritative totals
  without running `gates.sh` or the suite. `gates.sh` passes its final totals,
  counting this gate itself as a pass — exact when this gate passes, moot
  when it fails (a failed build is not trusted). Labelled-count checks are
  skipped in this mode; the standalone `--gates` run still covers them.
- **Also fixed in `doc_counts_gate.py`:** it did NOT check PROJECT-MASTER's
  "N PASS, 0 FAIL" format, only N/N pairs and 3-digit suite counts. A fake
  "99 PASS" document passed the gate until now. Added a check for that format:
  quoting more gates than exist is FAIL, quoting fewer is NOTE.

**New gate count: 34 → 37 PASS, 0 FAIL, 1 NOT-RUN** (Windows execution).
Suite rises with WS3's tests (see below): **221 pass, 4 no-expectation**.
Documents updated to 37 / 221 (PROJECT-MASTER, PROJECT-OVERVIEW, scorecard,
project-status, design-parameters).

**Proof a doc regression FAILs the build:** with PROJECT-MASTER temporarily
quoting "99 PASS", `gates.sh` exits 1 with `doc counts FAIL — quotes 99 PASS
but only 37 gates exist`, PASS 36 / FAIL 1. Document reverted afterwards;
final run is green.

## WS2 — peephole optimiser, measured — DONE, REVERTED (finding, not failure)

Built with `-DSUTRAM_R65_PEEPHOLES=1` (compiler 425,120 B vs default 424,568 B).
- Guard, default vs peephole, all 551 programs: **258 byte-identical,
  212 byte-differ but run-identically, 81 refused identically, 0 run-differ.**
  The peephole is behaviour-preserving, but it moves bytes on 212 programs.
- Benchmark (`tools/bench_gate.py`, repeat 3, this machine): essentially flat
  — e.g. bench_arith 16.24 → 16.29 ms, bench_loop 6.63 → 6.68 ms,
  r46_hotcall_array 23.51 → 21.40 ms (the only notable move, within noise on
  the other benches). No consistent gain.
- **Decision: NOT enabled by default.** The guard is absolute (0 differ), and
  212 differ, for ~no measured gain. Default build stays OFF. No code change
  ships for WS2.

## WS3 — universal bounds guard on mala and kosh — DONE, alias gap fixed

**What was already guarded (probed, not assumed):** local mala/kosh load and
store, kosh parameters (typed and untyped), slices — all fire
`mala ank seema atikram` on overrun. Globals cannot be mala/kosh (syntax
error at top level), and call-result indexing is a syntax error, so neither
is a case.

**What was NOT guarded (the gap):** indexing through an ALIAS. `vitti b = a`
or `b = a` left b unmarked (only the declared name was marked), so `b[5]` on
a 3-cell mala silently returned 0, and a kosh alias store silently wrote
past the end. Same for slice reassignment (`t = s`).

**Fix, in `src/sutram_compiler.asm`:** new helper `r38_mark_alias`
(target name, source name) — slice → mark slice, float kosh → mark kosh +
float kosh, kosh → mark kosh, array → mark array; already-marked targets
left alone; raw `nirmmita` pointers NOT marked (they have no header, so a
check would read heap metadata — their unchecked path is deliberate and
unchanged). Called from `.gs_decl` (declaration alias, before the fast
paths) and `.gs_assign` local scalar path (assignment alias, before the
fast paths).

**After the fix, all alias probes fire the error:** mala decl alias load,
mala assign alias load, kosh decl alias load, kosh assign alias store,
slice reassign alias load. In-bounds alias load/store still work and write
through to the original. Raw-pointer overrun still silently succeeds, by
design (see above).

**Suite overrun tests: NONE.** Full suite with the new compiler:
**NO-EXPECTATION=4, PASS=221** (218 + 3 new tests below), no FAIL, no
golden changed. Proof_lib 224/224, proof_props 86/86, crash corpus 227 +
manifest 0 failed, doc signatures 305/305.

**New tests (in the patch):** `examples/251_r38_alias_mala_oob.sm`,
`252_r38_alias_kosh_oob.sm`, `253_r38_alias_slice_oob.sm`, each with
`.out` = `Sutram Error: mala ank seema atikram` and `.exit` = 1. All 3 pass
with the new compiler and would fail (return 0 / 999) with the old one.

**Guard:** old programs unchanged — default vs alias compiler on the 551
pre-existing programs: **470 byte-identical, 81 refused identically,
0 DIFFER** (no existing program uses alias indexing). With the 3 new
programs, the new tree's guard is **554 programs, 473 byte-identical,
81 refused identically, 0 DIFFER** (fresh alias build vs working-tree alias
binary, byte-identical).

## Delivery note — why a patch, not direct to main

The three workstreams are atomic: the new tests FAIL with the old compiler,
and the new compiler's binary cannot be uploaded safely through the text
API used here (binary content would corrupt). Direct-delivering the text
files without the binary would break main's suite; direct-delivering a
corrupted binary would be worse. So the patch (17 files, 22,295 B) is the
unit to apply via git, then `gates.sh` rebuilds the binary — the rebuilt
binary here is **424,920 B** (was 424,568 B) and fresh-build byte-identical
to the working-tree binary. The patch does NOT contain the binary; rebuild
it, do not copy it through the API. Verified on a pristine checkout:
patch applies cleanly, gates EXIT=0, suite PASS=221, rebuilt binary
SHA-256 `0637d9aee1b2b00d29fe0bf3436cc7dbc63bff0a0618e11e5b4f63788326ea66`,
identical to the working-tree binary.

## Files in the patch

`tools/gates.sh`, `tools/doc_counts_gate.py`, `src/sutram_compiler.asm`,
`PROJECT-MASTER.md`, `PROJECT-OVERVIEW.md`,
`docs/sutram-scorecard.html`, `docs/sutram-project-status.html`,
`docs/sutram-design-parameters.html`, 3 new examples + 6 expect files.
