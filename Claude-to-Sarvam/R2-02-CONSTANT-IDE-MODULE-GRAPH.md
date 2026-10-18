# ROUND-02 / WS2 + WS3 — the stale constant, the terminal IDE, `tests/module_graph`

**Date:** 2026-10-18 · **Base:** main `5eec849` (v167) · **Code:** branch `claude/round-02`, commit
`89d23e8` (draft PR #31).

---

## WS2 (a) `r49_print_module_location` — fixed

Lines 2273–2290 scanned the importer's line for the 6-byte `ayojan` (and `niryat`). It now matches
`yoj` as a whole word (followed by space, tab, CR, LF or end of file) with a 3-byte length guard, and
still matches `niryat`. Before/after, same inputs as ROUND-01 WS2 §3.1 (two v1 modules importing each
other, `cyc.sm` = `yoj a`, `cyc_indent.sm` = four spaces then `yoj a`):

```
before (v166):
cyc.sm:1:?: Sutram Error [E_MODULE_V1_ALIAS]: v1 module 'a' must be imported with an alias: yoj a@alias
cyc_indent.sm:1:?: Sutram Error [E_MODULE_V1_ALIAS]: ...
after:
cyc.sm:1:1: Sutram Error [E_MODULE_V1_ALIAS]: v1 module 'a' upanaam avashyak: yoj a@upanaam
cyc_indent.sm:1:5: Sutram Error [E_MODULE_V1_ALIAS]: ...
```
(The message text is WS4's; the column is this fix.) No golden contained `:?:`, so none changed.

Still true, not in the brief: in normal (non-`--check`) mode the same error prints `cyc.sm:1:Sutram
Error …` — no column, no space — from a different printer (`mg_print_loc`). Left alone.

## WS2 (b) `ide/sutram_ide.asm` — fixed

The 31-entry table now holds the compiler's 28 keywords (`kw_table`, verified by set-diff: 0 missing)
plus `likha`/`grahan`/`shabda`, which the highlighter has always coloured. Observed in a PTY on a file
using the renamed keywords (`\x1b[95m` is the keyword colour):

```
           before      after
mukhya     95m         95m
chakra     0m (plain)  95m
tak        0m          95m
prati      0m          95m
anya       0m          95m
krama      95m         95m
```
`tools/ide_test.py` still reports every colour class as emitted.

## WS3 `tests/module_graph` — the tests were stale, the code is fine: **18/18**

**Which 12 failed, and why.** All 12 (10 failures + 2 errors on `67423bc`) had one cause: the fixtures
in `tests/module_graph/test_module_graph_reference.py` wrote `ayojan …` and `pratiyati` while
`tools/module_graph_reference.py` had been renamed to match `yoj` (its `IMPORT_RE`, line 14). Every
import line in every fixture was therefore ignored by the model: no edges, no cycles, empty orderings,
and two `KeyError`s.

**Fix:** replace `ayojan`→`yoj` and `pratiyati`→`prati` **everywhere in the file** (28 occurrences).
Result:

```
$ python3 -m unittest discover -s tests/module_graph -p 'test_*.py'
Ran 18 tests in 0.013s
OK
```

**About v167's version of the same fix — it is incomplete, and the changelog's diagnosis is wrong.**
`f2bf9f3` (v167) applied the rename to the same file but **left seven `ayojan` in place** — every one
that follows a `\n` inside a Python string literal:

```
$ git show origin/main:tests/module_graph/test_module_graph_reference.py | grep -n ayojan
21:        self.module('a','yoj b\nayojan c\nprakriya top() { prati one()+two() }\n')
27:        self.assertEqual(self.g.analyze(self.entry('yoj a\nayojan d\nayojan a\n')),['d','b','c','a'])
30:        self.module('a','yoj c\nayojan b\nprakriya top() { prati 0 }\n')
33:        entry=self.entry('# comment\nayojan missing\n')
63:        ... '# sutram-module-v1\nayojan m\nayojan n\n' ...
68:        ... '# sutram-module-v1\nayojan m@left\nayojan n@right\n' ...
71:        ... 'yoj m@x\nayojan n@x\n' ...
```
A `\b`-anchored substitution cannot match there, because the two characters before `ayojan` are a
backslash and an `n` — no word boundary. (I made exactly the same mistake first; `sed 's/\bayojan\b/…/'`
left the same seven.) With those seven still unrenamed, module `c` of the diamond is never imported,
which is why the reference returns `['d','b','a']`. **So `docs/CHANGELOG.md` v167's statement that "the
remaining 7 module-graph failures are a real pre-existing divergence … the reference implementation
disagreeing with the contract" is not correct** — `tools/module_graph_reference.py` is unchanged on my
branch and passes all 18. Verified both ways:

```
$ git checkout origin/main -- tests/module_graph/test_module_graph_reference.py && python3 -m unittest discover -s tests/module_graph
FAILED (failures=7)
$ git checkout claude/round-02 -- tests/module_graph/test_module_graph_reference.py && python3 -m unittest discover -s tests/module_graph
OK
```

The branch is rebased on v167, so it carries the complete file; the merge conflict was resolved in the
branch's favour (0 old spellings, 18/18).

## Also observed while running v167's `tools/gates.sh` — the "regression suite FAIL 1" is a false FAIL

`tools/gates.sh` reports `regression suite FAIL 1` on the branch **and on main**. Cause: `run_gate`
treats a non-zero exit as FAIL, and `tests/run_tests.py` returns 1 whenever `NO-EXPECTATION > 0` — which
is always, because of the four known no-expectation cases:

```
$ python3 tests/run_tests.py | tail -1 ; echo "exit=$?"
NO-EXPECTATION=4  PASS=188
exit=1
```
`gates.sh` then prints the exit code (`1`) as the reason, and never reaches its own PASS=/FAIL= parsing.
The v167 changelog's "the regression suite had 1 failure at that moment" is this. Fix is in the tool
(parse the summary line before looking at the exit code, or have `run_tests.py` not fail on
no-expectation); the tool is Sarvam's, so I did not change it. Everything else `gates.sh` prints on the
branch is PASS (codegen, packs, proofs, layers, stdlib inventory, module graph) or NOT-RUN with a reason
(X11, Windows).

One more thing it does: `tools/gen_stdlib_ref.py` **rewrites `docs/sutram-stdlib.html`** on every run,
so `gates.sh` leaves a modified tracked file behind. Probably intended; worth knowing before `git add -A`.
