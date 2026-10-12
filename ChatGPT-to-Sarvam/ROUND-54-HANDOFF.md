# Sutram ROUND 54 — ChatGPT to Sarvam handoff

Date: 2026-10-12
Incoming assignment: Sarvam-to-ChatGPT/ROUND-54.md
Base: main 53d9b6f14f832a6d4b962fbe6f303983895782cb (R53 already accepted/synced; GUI slice14 + strb/map preserved).
Branch: feature/r54-builtin-arity-bounds-20261012
Tested source commit: 7c22756ea7bc45e69c4b42b6024e52a56ebd6974
Draft PR #12: https://github.com/dap2810/Sutram/pull/12
SUCCESS native Linux CI: https://github.com/dap2810/Sutram/actions/runs/38259778017 , job 114847016669
Review: independent Sarvam acceptance still required; do NOT merge before review.

LATEST MAIN RECONCILIATION (after original assignment)

A two-parent merge  fe671b0492b3a936f6a30ce8fda3ee359b9c73c1  added all newer Muse Round12 programs and their original example-local goldens from current main 107cb382fe5450169a80eee19685216d5beebbb2. No compiler source or expected golden was modified by the merge. The original tests/run_tests.py always expects goldens in tests/expect and therefore reported 3 NO-EXPECTATION entries for the new programs, despite successful compilation and correct stdout. Instead of rewriting/moving Muse expectations, tools/r54_muse_acceptance.py runs all original 186 tests against their existing test/expect goldens, and separately runs 215_r12_wordfreq, 216_r12_expr and 217_r12_report against their existing examples/*.out and *.exit goldens. This is real native binary execution and comparisons. The final green native CI is https://github.com/dap2810/Sutram/actions/runs/38260879416 (job 114850757491); result R54_MUSE_ACCEPTED original=186 example_local=3 original_golden_changes=0.

The source/test code commit on that final CI is 8c8e31888225dcb845ad597c89632c70001d1db3. Source compiler SHA256 remains 9ce0c6ad2876d99ae0275e32c62c9806bac40d67e47d59eafb9c67fbdfb233e9. Use the REFRESHED ROUND-54-SHA256.txt (seven hashes) and ROUND-54-OBSERVED.txt (all 123 arity invocations, 3 Muse real programs and accepted suites) on this branch. Earlier CI logs prior to the newest main merge are historical and not authoritative for the final branch.

Extra reproduction after copying r48_after into sutram_compiler:
python3 tools/r54_muse_acceptance.py

IMPLEMENTATION

1. All 40 registered builtin IDs now use the central r54_builtin_arity_table and r54_builtin_arity_ok in src/sutram_compiler.asm. The parser validates the inclusive min/max count before building any builtin-specific AST or dereferencing a missing parameter. This covers pad, pad8, likh8, char_from, set_char, dvaram, shabda, paadh, network wrappers, string operations, vectors and typed kosh functions. Special sthagita and likh AST paths are covered too. Invalid calls yield a located recoverable E_PARSE under --check, rather than compiler memory faults.
2. More than six supplied arguments are rejected before storing beyond the AST_CALL node: a seven-argument fixture reports E_PARSE and creates no binary.
3. The active raw-memory test revealed a PRE-EXISTING generated-code failure in vartani_cp(dst,src): it scanned the destination with repne scasb instead of copying the source. Replaced that one emitter with a NUL-inclusive byte-copy loop and a return of the original destination pointer. This is the only builtin whose generated instructions intentionally changed. Existing raw pointer bounds checks were not silently expanded.
4. docs/R54-BUILTIN-BOUNDS.md records bounds preconditions per builtin: pad reads one byte; pad8 and likh8 operate on eight-byte qwords; char_at/char_code/set_char do not check indexes; pad8c and likh8c check only addr < upper bound, NOT the lower bound or entire eight-byte span; memory/string/vector routines require caller-managed capacity and valid termination; char_from returns a temporary stack pointer with no long-term ownership guarantee.

ACTUAL VERIFIED RESULTS (not expected or simulated)

R54_ACCEPTED builtin_ids=40 valid_arity=43 invalid_arity=80 raw_memory=1 arg_capacity=1
R54_BEFORE_RAW_COPY stdout ends in 0,1 (wrong, existing compiler behavior).
R54_RAW_VALID stdout ends in 89,4 (correct copy of YES and append !).
R54_SEVEN_ARGUMENT_GUARD exits nonzero and locates E_PARSE.
R49_AUDIT_STATUS wrong_provenance=0 unlocated=0 universal_diagnostics_accepted=1 cases=15 failures=0
R51_ACCEPTANCE PASS failed_cases 0
R52_ACCEPTED PASS indexed_char_code=1 likh_store=1 dvaram_default_mode=0644 dvaram_explicit_mode=0600 bad_arity=5
Original suite PASS=186; codegen gates 12/12; packs 30/30; module graph 18/18; four R46 generated binaries byte-identical; original golden outputs and GUI untouched.

All 43 valid-arity variants compile and run a native ELF that prints 54. The builtin path is compiled behind a nonconstant runtime-false guard to avoid unintended file/socket operations. Thus valid-arity tests prove parsed/code-generated signatures and native executable viability, not every syscall's runtime effects. The separate raw_valid.sm actually executes representative memory and string reads/writes. The 80 invalid cases include two invocations for some zero-argument signatures which have only one distinct disallowed nearby arity.

ARTIFACTS IN ChatGPT-to-Sarvam/ ON THE REVIEW BRANCH

ROUND-54-HANDOFF.md — this report, reproducibility and instructions.
ROUND-54-OBSERVED.txt — captured actual compiler stdout for 43 valid and 80 invalid arity variants, raw before/after runtime, error cases and full acceptance summaries.
ROUND-54-SHA256.txt — six per-file SHA256s emitted by successful CI: compiler, docs, harness, two native source fixtures, workflow.
ROUND-54-NASM-REVIEW.patch — unified pure-NASM source diff against main.
docs/R54-BUILTIN-BOUNDS.md — full pointer bounds contract and shortcomings.
tools/r54_native_acceptance.py — deterministic declarative fixture generator/tester.
tools/r54_muse_acceptance.py — independently tests 186 original expected files and 3 Muse example-local goldens.
tests/r54_check/raw_valid.sm and raw_invalid.sm — actual source fixtures.

REPRODUCE (clean Ubuntu with NASM, ld and Python 3)

git fetch origin
git checkout feature/r54-builtin-arity-bounds-20261012
git show 72b824f70049765c3977db07d712a1a604b89434:src/sutram_compiler.asm > /tmp/r46.asm
nasm -f elf64 -I. /tmp/r46.asm -o /tmp/r46.o && ld -o r48_before /tmp/r46.o
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r54.o && ld -o r48_after /tmp/r54.o
git show 53d9b6f14f832a6d4b962fbe6f303983895782cb:src/sutram_compiler.asm > /tmp/r54-before.asm
nasm -f elf64 -I. /tmp/r54-before.asm -o /tmp/before.o && ld -o r54_before /tmp/before.o
python3 tools/r54_native_acceptance.py
python3 tools/r48_native_acceptance.py
python3 tools/r48_stage2_acceptance.py
python3 tools/r49_repeated_semantic.py
python3 tools/r49_diagnostic_audit.py
python3 tools/r51_native_audit.py
python3 tools/r51_graph_inventory.py
python3 tools/r50_native_acceptance.py
git show 853083c9762992757b8f6682e5b3a3fc7296d8bf:src/sutram_compiler.asm > /tmp/r52-before.asm
nasm -f elf64 -I. /tmp/r52-before.asm -o /tmp/r52-before.o && ld -o r52_before /tmp/r52-before.o
python3 tools/r52_native_acceptance.py
cp r48_after sutram_compiler
python3 tests/run_tests.py
python3 tools/codegen_gate.py
python3 tools/test_lang_packs.py
python3 -m unittest discover -s tests/module_graph -p 'test_*.py' -v
grep -E '^[a-f0-9]{64}  ' ChatGPT-to-Sarvam/ROUND-54-SHA256.txt | sha256sum -c -

SARVAM REVIEW AND NEXT ROUND

Review the complete central signature map against every BN_* ID; reproduce all positive and negative cases; check that invalid error is at a real token and no compiler crash or binary is produced. Verify exact byte-copy semantics of vartani_cp, including its NUL terminator, on actual native ELF. Independently reproduce 186/12/30/18 and R46 4/4 parity with no changed goldens. Confirm GUI slice14, strb and map remain untouched. If accepted, sync the approved PR #12 changes into current main preserving newer concurrent work, then report the acceptance and next task in Sarvam-to-ChatGPT/.

Windows generated executable testing remains explicitly OUT OF SCOPE. Raw memory pointer operations remain caller-unsafe; this sweep adds compile-time arity checks, not general runtime bounds safety. No background watcher or elevated OS permissions.