# ROUND-03 / WS2 — the round tools that matched English text

**Date:** 2026-10-19 · **Base:** main `85d6c5f` (v169) · **Code:** branch `claude/round-03`, commit `decb0afe`

---

## 0. A correction to my own ROUND-02 report first

R2-03 §5 said "**eleven** historical acceptance tools still match the English text" and named them. That
list came from a **grep, not a run**. Running every tool shows the list was wrong in both directions:
- **Only 4 of my 11 actually fail on text alone:** r48_stage2, r64_source_gate, r68_native,
  test_namespace_contract_oracle.
- **4 of the 11 pass:** r49_diagnostic_audit, r49_repeated_semantic, r51_native_audit, r52_native. Two of
  those (r49_diagnostic_audit, r51_native_audit) **failed on v166 and pass now**, because ROUND-02 fixed
  their column and provenance checks.
- **3 of the 11 fail for other reasons:** r48_native, r54_native, r71_native.
- **5 text-only failures I missed entirely:** r50, r63_kosh, r64_kosh_diagnostic, r65_finish, r65_native.

The measured list below replaces the R2 list.

## 1. What I did

- Ran **31 round tools** (33 invocations; `r71_native` both as `--validate-only` and in full) against
  the current compiler.
- Ran the same set against a **v166 compiler** built from `598578f`. That is the last commit before
  ROUND-02's Sanskrit strings, and it separates "broken by ROUND-02" from "already broken".
- Reproduced the workflows' setup for each tool: the named historical `*_before` compilers built from
  `git show <sha>:src/sutram_compiler.asm`, the R65/R67 variant builds (`-DSUTRAM_R65_PEEPHOLES=1`,
  `-DSUTRAM_R65_TRAP_INT=1`, both, `-DSUTRAM_R67_PURE_STACK_PAIRS=1`), and `R56_GLOBALS_ACCEPTED=1`.
- For every tool that failed only on text, applied only the text change in a scratch copy, re-ran it,
  and then applied the same change on the branch and re-ran it again in the real tree.

Out of scope here: the WS1 lock tools (R3-01), and the two `.ps1` tools (Windows) — those are NOT-RUN.

## 2. Exact commands (representative)

```sh
env R56_GLOBALS_ACCEPTED=1 timeout 120 python3 tools/<tool>.py          # no-argument tools, as the workflows run them
python3 tools/r63_kosh_acceptance.py --compiler ./sutram_compiler
python3 tools/r64_kosh_diagnostic_acceptance.py --compiler ./sutram_compiler
python3 tools/r65_finish_acceptance.py --default sc --peephole sc_peep --trap sc_trap --combined sc_comb
python3 tools/r65_native_acceptance.py --default sc --peephole sc_peep --trap sc_trap
python3 tools/r68_native_acceptance.py --compiler sc --reference sc_v169 --pair-compiler sc_pairs
python3 tools/r48_stage2_acceptance.py ; python3 tools/r50_native_acceptance.py     # need ./r48_after (workflow convention)
python3 tools/test_namespace_contract_oracle.py
```

## 3. Result per tool — current compiler / v166 compiler

| Tool | now | v166 | What it says now | Verdict |
|---|---|---|---|---|
| r41_acceptance | PASS | PASS | `R41 native acceptance 3/3 PASS` | keep |
| r49_diagnostic_audit | PASS | **FAIL** | `cases=15 failures=0` (v166: `unlocated=6 failures=4`) | keep — ROUND-02 fixed it |
| r49_repeated_semantic | PASS | PASS | `R49_REPEATED_SEMANTIC_PASS` | keep |
| r51_graph_inventory | PASS | PASS | `R51_GRAPH_END` | keep |
| r51_native_audit | PASS | **FAIL** | `R51_ACCEPTANCE PASS failed_cases 0` | keep — ROUND-02 fixed it |
| r52_native_acceptance | PASS | PASS | exit 0 (no longer prints its `R52_ACCEPTED` summary line; I did not investigate why) | keep |
| r55_native_acceptance | PASS | PASS | `R55_FORWARD_ACCEPTED …` | keep |
| r56_native_acceptance | PASS | PASS | `R56_GLOBAL_ACCEPTED …` | keep |
| r58_codegen_baseline | PASS | PASS | `R58_FROZEN_CODEGEN_ACCEPTED 8 / 8` | keep |
| r58_native_acceptance | PASS | PASS | `R58_TIMING … best_speedup=2.6691x` | keep |
| r59_codegen_baseline | PASS | PASS | `R59_FROZEN_CODEGEN_ACCEPTED 3 / 3` | keep |
| r59_native_acceptance | PASS | PASS | `R59_TIMING …` | keep |
| r67_native_acceptance | PASS | PASS | 20 × PASS, 1 × NOT RUN (needs `--reference`) | keep |
| r71_native `--validate-only` | PASS | PASS | `native_status: NOT_RUN` by design | keep (R71 open review) |
| **r48_stage2_acceptance** | FAIL → **PASS** | FAIL | was: `assert "Sutram check: errors found…"`; now `STAGE2_PASS structural=3 nested=2 unclosed=1 undefined=3` | **REPAIRED** — broken *before* ROUND-02 (expects the pre-v160 `check` wording) |
| **r50_native_acceptance** | FAIL → **PASS** | FAIL | now `R50_ACCEPTED … 2/2 native executions; 2/2 --check` | **REPAIRED** — broken before ROUND-02 |
| **r63_kosh_acceptance** | FAIL → **PASS** | PASS | now `R63_NATIVE_ACCEPTED 9 gates` | **REPAIRED** — broken by ROUND-02 |
| **r64_kosh_diagnostic_acceptance** | FAIL → **PASS** | PASS | now `R64_KOSH_DIAGNOSTICS_ACCEPTED` | **REPAIRED** — broken by ROUND-02 |
| **r64_source_gate** | FAIL → **PASS** | PASS | now `R64_SOURCE_GATE_PASS (NOT native evidence)` | **REPAIRED** — broken by ROUND-02 |
| **r65_finish_acceptance** | FAIL → **PASS** | PASS | 0 `incorrect` cases; last case `…:4: yog atipravah` | **REPAIRED** — broken by ROUND-02; the only native test of the opt-in trap build |
| **r65_native_acceptance** | FAIL → **PASS** | PASS | now `R65_NATIVE_ACCEPTANCE_PASS` | **REPAIRED** — broken by ROUND-02 |
| **r68_native_acceptance** | FAIL → **PASS** | PASS | now `R68_NATIVE_GATES_PASS` | **REPAIRED** — broken by ROUND-02 |
| **test_namespace_contract_oracle** | FAIL → **PASS** | PASS | now `ORACLE 7 executable cases and 7 rejection contracts checked` | **REPAIRED** — broken by ROUND-02 |
| r46_runtime_benchmark | FAIL | FAIL | `before -9223372036854.775808 / after 18000000.000000` — the R46 baseline compiler mis-runs the renamed benchmark | **RETIRED** |
| r48_native_acceptance | FAIL | FAIL | after the text fixes it still fails `R46/R48 native binary mismatch` — a byte-identity A/B against R46 | **RETIRED** |
| r54_native_acceptance | FAIL | FAIL | `Sutram Error: undefined function: akshar_rakh` — printed by the **R54 baseline** compiler, which predates the builtin rename | **RETIRED** |
| r54_muse_acceptance | FAIL | FAIL | `assert len(names)==186` (now 189) | **RETIRED** |
| r57_native_acceptance | FAIL | FAIL | the R46 compiler compiles renamed `41_recursion.sm` into a binary that **segfaults (exit 139)** | **RETIRED** |
| r57_codegen_baseline | FAIL | FAIL | frozen ELF hash of a fixture renamed in `cab7587` | **RETIRED** |
| r63_source_gate | FAIL | FAIL | `R63_SOURCE_FAIL PEEK_FLOAT_TYPE` — greps R63's code shape; R64 changed it | **RETIRED** |
| r65_source_gate | FAIL | FAIL | `ALL_FIVE_INTEGER_TRAP_PATHS` — and its line 20 reads `"shesh"` where the label is `r65_msg_mod` (**rename damage inside a Python string**, see R3-04) | **RETIRED** |
| r66_native_acceptance | FAIL | FAIL | `EXAMPLES = ROOT/'examples/r66'`: that directory **does not exist and never did** (`git log` finds no `native_digits.sm` anywhere in history) | **RETIRED** |
| r71_native (full) | FAIL | FAIL | `R71_NATIVE_REFUSED: input drift … 64ea028a` | WS1: R71 lock, left alone on purpose |
| r61/r62 `.ps1` | NOT-RUN | — | Windows | — |
| r67_prepare_compiler | — | — | staging tool | WS1: retired |

## 4. Totals, kept separate

| On the current compiler, before my changes | Count |
|---|---|
| PASS | **14** |
| FAIL — English text only (now repaired, each re-run to exit 0) | **9** (7 broken by ROUND-02, 2 broken earlier) |
| FAIL — structural (now retired) | **9** |
| FAIL — WS1 R71 core lock | 1 |
| NOT-RUN | 3 |

**After the branch:** the 14 + 9 = 23 tools that remain all exit 0. The 9 dead tools are deleted, and
git history keeps them (e.g. `git show 85d6c5f:tools/r54_native_acceptance.py`).

## 5. Why REPAIR for nine and RETIRE for nine — the test I applied

**Does the tool test behaviour of today's compiler?**
- If yes, and only its expected text is stale, then **repair**. The behaviour changed on purpose in
  ROUND-02 WS4, so updating the text is updating the golden for a deliberate change.
- If its pass condition depends on a **pre-v157 compiler** (an A/B "before" side), on a **frozen hash or
  count**, or on a **grep of an old code shape**, then **retire**. A pre-v157 compiler cannot read
  current source, so no edit to the tool can make that comparison mean anything again. Rebuilding the
  "before" side from a post-rename commit would change what the tool measures, so it would no longer be
  the round's evidence. The rounds' acceptance is recorded in the CHANGELOG and in git. A tool that can
  only fail adds nothing to that record. It just looks like a gate.

The repairs were made mechanically, with an exact occurrence count asserted for every replacement:

```
r48_stage2:  "Sutram check: errors found; no output binary" -> "Sutram janch: dosh mile; nirgat binary nahi";
             regex  near '  -> shabd '  ;  unknown function '  -> agyat prakriya '
r50:         "Sutram check: OK" -> "Sutram janch: OK"
r63_kosh, r64_kosh, r64_source_gate:  "kosh pop/peek/dequeue from empty array" -> "rikta kosh se kosh_pop/peek/dequeue"
r65_finish, r65_native:  signed addition/subtraction/multiplication overflow -> yog/nyun/gun atipravah;
             division by zero -> shunya se bhajan; remainder by zero -> shunya se shesh;
             signed division/remainder overflow -> bhajan/shesh atipravah
r68_native:  invalid or truncated UTF-8 in source code -> srot me ashuddh ya khandit UTF-8;
             abbreviation keyword is not a value -> sankshep shabd mulya nahi
namespace oracle: the three namespace messages -> the strings now at src/sutram_compiler.asm:758-760
```

## 6. The round workflows — **retired as well**, and why that was unavoidable

None of these tools is in `tools/gates.sh` or `PROJECT-MASTER.md`. They are run only by the eight
manual workflows `.github/workflows/r49-r50-native.yml … r59-native.yml`. **Every one of those workflows
fails by construction, whatever is done to the tools:**

```
$ for each workflow: git diff --stat <the commit in its "goldens untouched" step> HEAD -- tests/expect/
r53-integrated.yml  vs 7492baa:  35 files changed, 42 insertions(+), 27 deletions(-)
r54 … r59           vs their round commits: the same 35 files
r49-r50-native.yml: no golden step, but it runs r46_runtime_benchmark (dead, above)
```
Seven of them end with `git diff --exit-code <their round> -- tests/expect/`. That is false since v157
and false again since ROUND-02. All eight also call at least one retired tool. `r53-integrated.yml:57`
additionally hashes `lib/string.smlib`, which no longer exists.

So I deleted the eight and added **one** manual workflow, `.github/workflows/gates.yml`. It is
`workflow_dispatch` only and uses the approved header from `docs/CI-NOTIFICATION-POLICY.md`. It
installs NASM without root (copied from r59) and runs `sh tools/gates.sh`. The job fails if the summary
line shows `FAIL` ≠ 0, and it uploads the gate report.
```
$ python3 tools/check_workflow_triggers.py
CI_MANUAL_ONLY_OK …/.github/workflows/gates.yml events=workflow_dispatch
CI_NOTIFICATION_POLICY_ACCEPTED: no automatic workflow events
$ python3 -m unittest discover -s tests/ci -p 'test_*.py'     → OK
```
**I did not dispatch it** (CI-NOTIFICATION-POLICY: once per accepted milestone, by you). On a runner
with no display, the X11 gate prints NOT-RUN, so the expected result is 8 PASS / 0 FAIL / 2 NOT-RUN.
That is a prediction, not an observation.

If you would rather keep the round workflows as records, revert that one commit (`decb0afe`'s
`.github/` part). But they cannot be made to pass.

## 7. What I did not do

- Did not run the two Windows `.ps1` round tools.
- Did not investigate why `r52_native_acceptance.py` no longer prints its summary line (exit is still 0).
- Did not dispatch any workflow.
