# Windows round 3: tested fixes and remaining boundary

Date: 2026-11-03. Both `SUTRAM-WINDOWS-ROUND3.md` and `SUTRAM-WINDOWS-ROUND3-FINAL.md` were applied; copies accompany this report. Code is proposed on review branch `codex/windows-round3-2026-11-03`, commit `a01bd5bf`. Base: `5d7d21cbdf4093bb4374a408752a25422631f0ab` (v297). Draft PR: [#64](https://github.com/dap2810/Sutram/pull/64). The version banner was not reassigned: these are v297 review builds, not a numbered accepted release. Main’s compiler, installed compiler, installer and goldens are not replaced.

## What changed and why

1. **Concatenation first:** the stack hypothesis was refuted for `vartani_sandhi`. Its old emitter returned the first argument and appended into it, overwriting a read-only literal in the crashing example. It now reuses the existing allocating string-join emitter, returns a new buffer and leaves both inputs unchanged. One allocation requests `strlen(a)+strlen(b)+1` bytes; bytes are copied once per input. This intentionally changes the old in-place semantics: callers must use the returned pointer. Old `vartani_cat` remains a byte-identical alias. No code pages are made writable.
2. **Character storage second:** `anka_akshar` formerly returned a pointer eight bytes below the current stack pointer and left the stack unbalanced by eight bytes. A PE runtime call overwrote that byte. The P-versus-B observation was corruption, not an arithmetic off-by-14: 97 also printed P. It now preserves the input code on a balanced stack and returns an independent two-byte allocation containing its low byte and NUL. Results survive later calls and other character conversions. Old `char_from` remains a byte-identical alias.
3. **Memory decision before implementation: Option B.** The counter and budget depend on the Linux arena/region implementation (`r65_active` excludes PE); there is no Windows allocation accounting already available to expose with a small switch, and this is not an OS memory query. PE compilation now rejects `parimana()` and valid `mandapa parimita N` with `E_WINDOWS_SMRITI`, a source location and a Linux-only support hint. The same refusal applies to PE cross-compilation from Linux. Invalid budgets retain their existing validation. No zero-answer program or unenforced-budget program is emitted by these accepted syntax paths.

**Allocation cost and lifetime:** the string allocations use the ordinary persistent allocator and last for the program lifetime, including when called inside a mandapa. Linux rounds to its 16-byte arena alignment; Windows VirtualAlloc has OS page/region overhead, so a two-byte character is not a two-byte OS allocation. There is no new reclamation mechanism. This is a correctness fix with an explicit memory cost, not a performance improvement. Allocation failure emits `E_VARTANI_SMRITI` and exits 1 before a null write. Fault injection was executed on ELF; the existing fault-injection flag does not support PE.

**Remaining gap — kosh aliases:** Windows growing kosh still moves its backing storage, so the old alias diverges. This was not ported or broadly prohibited. The reference explicitly retains the single-name guidance. Source inspection shows raw aliases and region-dependent growth, not an existing Windows counter or stable handle that can simply be enabled. A sound fix needs stable storage/handles or broader alias restrictions; a check for one direct assignment would not establish general alias safety. No speculative partial alias fix was attempted. Therefore this round does not claim to close the entire Windows memory-model gap.

## Requested evidence table

| Item | Before | After | Linux still OK? |
|---|---|---|---|
| vartani_sandhi crash | Windows 0xC0000005; Linux loop prints once then SIGSEGV | abcd; repeated joins pass; inputs unchanged | Yes, including loop and nested/empty cases |
| anka_akshar(66) | P on Windows; B immediately on Linux | B | Yes |
| anka_akshar(97) | P on Windows; a immediately on Linux | a | Yes |
| Retained characters | Corrupt bytes on both platforms | Ba across another call | Yes |
| parimana() | Windows always 0 | Compile refusal E_WINDOWS_SMRITI | Linux accounting still works |
| parimita budget | Windows executes reached | Compile refusal E_WINDOWS_SMRITI | Linux E_PARIMITA still enforced |
| kosh alias | a[0]=41 k[0]=99 | Unchanged, unresolved/documented | Linux behavior unchanged |
| Native suite | Published 305 PASS / 8 FAIL | After builtins: 307 PASS / 6 FAIL. Final: 306 PASS / 3 FAIL / 4 COMPILE_FAIL | Linux 315 PASS / 4 NO-EXPECTATION |

## Per-change suite verification

The original harness and all goldens were preserved. Counts below are raw results, not reclassified passes. Each stage built a native compiler, ran the probes and then the full native suite. Linux was independently built/run through Ubuntu WSL2 as the existing non-root user.

| Stage | Windows raw counts | Linux raw counts |
|---|---|---|
| baseline | COMPILE_FAIL=1, FAIL=8, NO_EXPECTATION=3, PASS=304, SKIP_SIDE_EFFECT_OR_INLINE_ASM=3 | suite: COMPILE-FAIL=1  NO-EXPECTATION=4  PASS=314  (319 run) |
| concat | FAIL=8, NO_EXPECTATION=3, PASS=305, SKIP_SIDE_EFFECT_OR_INLINE_ASM=3 | suite: NO-EXPECTATION=4  PASS=315  (319 run) |
| characters | FAIL=6, NO_EXPECTATION=3, PASS=307, SKIP_SIDE_EFFECT_OR_INLINE_ASM=3 | suite: NO-EXPECTATION=4  PASS=315  (319 run) |
| explicit-memory | COMPILE_FAIL=4, FAIL=3, NO_EXPECTATION=3, PASS=306, SKIP_SIDE_EFFECT_OR_INLINE_ASM=3 | suite: NO-EXPECTATION=4  PASS=315  (319 run) |

**Initial baseline setup issue:** this fresh worktree lacked the adjacent lib/lang folders normally copied by the Windows build script, and the staged Linux compiler also lacked its lib folder. `79_ayojan_cwd` therefore failed in the first baseline run. The verification driver was corrected to copy these unchanged folders beside each compiler. The original baseline record is retained; the concatenation stage returns to the published 305/8 baseline apart from its targeted probe changes.

**Final delta:** 322 and 323 now match their existing goldens, including B42 and abcd. 220 remains the unchanged harness’s missing Hindi flag; 29 remains its Linux-syscall assumption; 288 remains the Windows alias gap. 303, 317 and 318 now refuse explicitly instead of producing misleading unsupported behavior. 304, a budget that would have fit, is also intentionally refused under Option B: Windows cannot enforce even a small declared budget. That is one deliberate compatibility change, not an unexplained regression; it accounts for 307 becoming 306. No other previously passing native example regressed. All counts retain the three Windows NO_EXPECTATION and three SKIP cases. The full Linux suite retains four NO-EXPECTATION cases; its process exits 1 for those, not for a failed golden.

## Additional checks

- Hand-derived regression tests: Windows 7 PASS, 2 Linux-only SKIP; Linux 9 PASS. These check repeated literals, preserved inputs/results, character lifetimes across procedure calls, 10,000 conversions, old/new byte parity, PE rejection before output creation, Linux memory behavior, and allocation-failure diagnostics. No expected result was recorded from the new compiler.
- Code-generation shape gate: PASS (12 cases).
- Language packs: 33/33 PASS; frozen pack sources unchanged.
- Library proofs: 229/229 PASS after restoring the fixture to its exact committed bytes.
- Property proofs: 86/86 PASS.
- Crash corpus: 227 cases plus manifest, 0 failures.
- R111 vocabulary: 57 checks, 0 failures.

The library proof initially reported 228 PASS / 1 FAIL: Windows checkout converted `tests/fixtures/file_hello.txt` from 13 LF bytes to 14 CRLF bytes. The unchanged baseline compiler also printed 14. `fixture-checkout.json` records both byte strings; restoring the exact Git blob produced no tracked diff and no golden edit. The corrected library proof log is separate. The new Windows unittest first failed in temporary-directory setup under the sandbox; authorized host execution passed. A first Linux unittest command resolved the wrong absolute compiler path; the corrected command passed. These harness failures are not hidden or attributed to the compiler.

This is a focused compiler regression run, not a claim that the complete 62-gate release pipeline or GUI/install/uninstall acceptance passed. Integrity locks, frozen baselines and old evidence were not repinned. No workflow was changed or manually launched.

## Changed files and review

- `src/sutram_compiler.asm`: **77 added, 134 removed** lines (git diff --numstat against the base). The fixes remain in the single pure-NASM compiler; no runtime language/toolchain dependency was introduced.
- `docs/LANGUAGE-REFERENCE.md`: **17 added, 5 removed** lines; allocation semantics/cost and PE refusal boundary.
- `tests/windows_round3/test_contract.py`: **88 new lines**, independent contract tests.
- Evidence and reproduction helpers live in this report folder. Generated executables and libraries are local build artifacts and are excluded from the review/source commit.

The draft PR is the acceptance boundary. Do not treat its compiler as merged/released, and do not replace the existing installer until Sarvam reviews the behavior changes and release evidence.

## Exact commands and evidence

Each `<stage>-<platform>/build.json` contains the exact NASM and ld argv and output. `probes.json` contains compilation/runtime argv, output, output hex, exits, timing and compiler hash. `suite.json` contains the exact suite command and stdout/stderr; Windows `native-cases.json` preserves every example result. Stages are baseline, concat, characters, explicit-memory. `regression.json` records all broader gate commands and initial outputs. The scripts are reproducible from the review worktree; Windows build tools used the existing NASM/GNU ld, Linux used /usr/bin/nasm and /usr/bin/ld. Timing samples are single runs, not benchmarks.

Stage labels name the source state at the time of that run; verify.py does not check out or recreate older source versions. The untouched baseline corresponds to the base commit, and the final stage to the review commit. Intermediate outputs record the one-change-at-a-time verification.

Host invocation patterns:
```text
python Windows-to-Sarvam/win-round3-2026-11-03/verify.py <stage>
wsl -d Ubuntu -- python3 /mnt/e/Github_Projects/Sutram/build/round3-review/Windows-to-Sarvam/win-round3-2026-11-03/verify.py <stage>
SUTRAM_COMPILER=<final native compiler> python -B -m unittest discover -s tests/windows_round3 -v
wsl -d Ubuntu -- python3 /mnt/e/Github_Projects/Sutram/build/round3-review/Windows-to-Sarvam/win-round3-2026-11-03/regression.py
wsl -d Ubuntu -- python3 /mnt/e/Github_Projects/Sutram/build/round3-review/tools/proof_lib.py --compiler /mnt/e/Github_Projects/Sutram/build/round3-review/build/round3/explicit-memory-linux/compiler
```

## Before and after probe output

### baseline / windows

Compiler SHA-256: `40026244b972a603d1601262fe130b84df3bea1c4d49418b4b489939a307cd14`.

**concat_literal** — run exit 3221225477
```text
(empty stdout)
```

**concat_loop** — run exit 3221225477
```text
(empty stdout)
```

**concat_inputs** — run exit 3221225477
```text
(empty stdout)
```

**concat_empty** — run exit 3221225477
```text
(empty stdout)
```

**char66** — run exit 0
```text
P
```

**char97** — run exit 0
```text
P
```

**char_kept** — run exit 0
```text
B�
```

**char_loop** — run exit 0
```text
10000
```

**memory_query** — run exit 0
```text
0
```

**memory_budget** — run exit 0
```text
reached
```

### baseline / linux

Compiler SHA-256: `a9868449a047482bd480ebc6ce05e73ebec57ce6aea1c691974aab8b17b25855`.

**concat_literal** — run exit 0
```text
abcd
```

**concat_loop** — run exit -11
```text
abcd
```

**concat_inputs** — run exit 0
```text
abcd|cd|abcd
```

**concat_empty** — run exit 0
```text
cdab
```

**char66** — run exit 0
```text
B
```

**char97** — run exit 0
```text
a
```

**char_kept** — run exit 0
```text
BhU�c�
```

**char_loop** — run exit 0
```text
10000
```

**memory_query** — run exit 0
```text
0
```

**memory_budget** — run exit 1
```text
Sutram truti [E_PARIMITA]: pankti 1 - mandape parimitat adhikam nirmmitam na sambhavati (parimitih 1 baait)
```

### concat / windows

Compiler SHA-256: `1346a5db927c15dc39e30d7c9be7a5b06e8311d99139df1df3d81329a3122a40`.

**concat_literal** — run exit 0
```text
abcd
```

**concat_loop** — run exit 0
```text
abcd
abcd
abcd
```

**concat_inputs** — run exit 0
```text
ab|cd|abcd
```

**concat_empty** — run exit 0
```text
cdab
```

**char66** — run exit 0
```text
P
```

**char97** — run exit 0
```text
P
```

**char_kept** — run exit 0
```text
B�
```

**char_loop** — run exit 0
```text
10000
```

**memory_query** — run exit 0
```text
0
```

**memory_budget** — run exit 0
```text
reached
```

### concat / linux

Compiler SHA-256: `ab917a495553145627ca1d7362f248fa867a273eb799560f70994a5a9469e816`.

**concat_literal** — run exit 0
```text
abcd
```

**concat_loop** — run exit 0
```text
abcd
abcd
abcd
```

**concat_inputs** — run exit 0
```text
ab|cd|abcd
```

**concat_empty** — run exit 0
```text
cdab
```

**char66** — run exit 0
```text
B
```

**char97** — run exit 0
```text
a
```

**char_kept** — run exit 0
```text
B(����
```

**char_loop** — run exit 0
```text
10000
```

**memory_query** — run exit 0
```text
0
```

**memory_budget** — run exit 1
```text
Sutram truti [E_PARIMITA]: pankti 1 - mandape parimitat adhikam nirmmitam na sambhavati (parimitih 1 baait)
```

### characters / windows

Compiler SHA-256: `fc59e7602625e1d656bbceb0e7c805f5743f6f26b2a65a688926e4cbfea214bb`.

**concat_literal** — run exit 0
```text
abcd
```

**concat_loop** — run exit 0
```text
abcd
abcd
abcd
```

**concat_inputs** — run exit 0
```text
ab|cd|abcd
```

**concat_empty** — run exit 0
```text
cdab
```

**char66** — run exit 0
```text
B
```

**char97** — run exit 0
```text
a
```

**char_kept** — run exit 0
```text
Ba
```

**char_loop** — run exit 0
```text
10000
```

**memory_query** — run exit 0
```text
0
```

**memory_budget** — run exit 0
```text
reached
```

### characters / linux

Compiler SHA-256: `1428d8624f45bbc0e40aedd802c715437d3a06879878ab5cfb501543c7742aba`.

**concat_literal** — run exit 0
```text
abcd
```

**concat_loop** — run exit 0
```text
abcd
abcd
abcd
```

**concat_inputs** — run exit 0
```text
ab|cd|abcd
```

**concat_empty** — run exit 0
```text
cdab
```

**char66** — run exit 0
```text
B
```

**char97** — run exit 0
```text
a
```

**char_kept** — run exit 0
```text
Ba
```

**char_loop** — run exit 0
```text
10000
```

**memory_query** — run exit 0
```text
0
```

**memory_budget** — run exit 1
```text
Sutram truti [E_PARIMITA]: pankti 1 - mandape parimitat adhikam nirmmitam na sambhavati (parimitih 1 baait)
```

### explicit-memory / windows

Compiler SHA-256: `1c83fda14d7b946585cba9bad374d4a3e627c7e103fcc54b60784aa1e4ff6627`.

**concat_literal** — run exit 0
```text
abcd
```

**concat_loop** — run exit 0
```text
abcd
abcd
abcd
```

**concat_inputs** — run exit 0
```text
ab|cd|abcd
```

**concat_empty** — run exit 0
```text
cdab
```

**char66** — run exit 0
```text
B
```

**char97** — run exit 0
```text
a
```

**char_kept** — run exit 0
```text
Ba
```

**char_loop** — run exit 0
```text
10000
```

**memory_query** — compile exit 1
```text
memory_query.sm:1:18: Sutram truti [E_WINDOWS_SMRITI]: Windows lakshye parimana smriti-gananam na samarthitam
  mukhya() { likha(parimana()) }
                   ^
Sanket: ayam prayogah Linux ELF lakshye eva samarthitah
```

**memory_budget** — compile exit 1
```text
memory_budget.sm:1:20: Sutram truti [E_WINDOWS_SMRITI]: Windows lakshye mandapa parimita smriti-seema na samarthita
  mukhya() { mandapa parimita 1 { vitti p = nirmmita(64) likha("reached") } }
                     ^
Sanket: ayam prayogah Linux ELF lakshye eva samarthitah
```

### explicit-memory / linux

Compiler SHA-256: `36cbf6737ec16071c39779db6d9286fff2f7df0923c573643463a120019b8fb4`.

**concat_literal** — run exit 0
```text
abcd
```

**concat_loop** — run exit 0
```text
abcd
abcd
abcd
```

**concat_inputs** — run exit 0
```text
ab|cd|abcd
```

**concat_empty** — run exit 0
```text
cdab
```

**char66** — run exit 0
```text
B
```

**char97** — run exit 0
```text
a
```

**char_kept** — run exit 0
```text
Ba
```

**char_loop** — run exit 0
```text
10000
```

**memory_query** — run exit 0
```text
0
```

**memory_budget** — run exit 1
```text
Sutram truti [E_PARIMITA]: pankti 1 - mandape parimitat adhikam nirmmitam na sambhavati (parimitih 1 baait)
```
