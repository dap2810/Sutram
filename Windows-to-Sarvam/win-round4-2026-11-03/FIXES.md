# Round 4 verified candidate

Based on Round 3 `a01bd5bf`. Code and evidence stay on `codex/windows-round4-2026-11-03`; no main push, merge, installation or installer rebuild.

| Item | Round 3 | Round 4 | Linux unchanged? |
|---|---|---|---|
| parimana() | compile refusal | live logical bytes; rounding/rewind probes pass | Yes |
| mandapa parimita | compile refusal | nested and boundary checks pass; overflow E_PARIMITA exit 1 | Yes |
| kosh alias | a[0]=41 k[0]=99 | a[0]=99 k[0]=99 | Yes |
| E_WINDOWS_SMRITI | emitted | removed after shared arena and regions passed native verification | No ELF output change observed |
| 220_hindi_parse_error | FAIL, missing --lang hindi | PASS with correct flag | PASS |
| 29_nishkriya | FAIL, raw Linux exit syscall | SKIP_LINUX_RAW_SYSCALL with explicit reason | PASS |
| 288_r86_kosh_alias_moves | FAIL, stale alias | PASS | PASS |
| Native suite | 306 PASS / 3 FAIL / 4 COMPILE_FAIL | 312 PASS / 0 FAIL / 0 COMPILE_FAIL; 3 no-expectation, 4 skips | 315 PASS / 4 no-expectation |

## Sequential evidence

| Stage | Windows | Linux |
|---|---|---|
| baseline | 306 pass, 3 fail, 4 compile failures | 315 pass |
| arena (experimental, kosh regions disabled on PE) | 309 pass, 4 fail | 315 pass |
| regions (experimental) | 311 pass, 2 fail | 315 pass |
| final (promoted, harness classified) | 312 pass, no failures | 315 pass |

Every stage retains build commands, compiler SHA-256, timings, probe output and suite output in its platform directory. Linux returns 1 solely for four NO_EXPECTATION cases. No golden was rewritten. `arena.patch` and `regions.patch` preserve the experiments relative to a01bd5bf (PowerShell UTF-16 patch output); `finalize.py` records promotion, run with `python -X utf8`.

## Exact original failures

### 220_hindi_parse_error

```json
{
  "case": "220_hindi_parse_error",
  "compile_command": [
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\win\\sutram.exe",
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\examples\\220_hindi_parse_error.sm",
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\build\\windows\\acceptance\\220_hindi_parse_error.exe"
  ],
  "compile_cwd": "E:\\Github_Projects\\Sutram\\build\\round4-review",
  "compile_exit": 1,
  "compile_stdout": "\nSutram truti: vyakaran dosh, pankti 7:1, shabd 'patra-ant'\n  \n  ^\nSanket: asmin sthane shabdam vyakaranam cha pashyatu.\n",
  "compile_stderr": "",
  "status": "FAIL",
  "expected_stdout": "\u092d\u093e\u0937\u093e \u092a\u0948\u0915 \u092e\u093f\u0932\u093e: hindi\n\nSutram truti: \u0935\u094d\u092f\u093e\u0915\u0930\u0923 \u0926\u094b\u0937, \u092a\u0902\u0915\u094d\u0924\u093f 7:1, \u0936\u092c\u094d\u0926 '\u092b\u093c\u093e\u0907\u0932 \u0915\u093e \u0905\u0902\u0924'\n  \n  ^\n\u0938\u0902\u0915\u0947\u0924: \u0907\u0938 \u0938\u094d\u0925\u093e\u0928 \u092a\u0930 \u0936\u092c\u094d\u0926 \u0914\u0930 \u0935\u094d\u092f\u093e\u0915\u0930\u0923 \u091c\u093e\u0901\u091a\u0947\u0902\u0964\n",
  "actual_normalized": "\nSutram truti: vyakaran dosh, pankti 7:1, shabd 'patra-ant'\n  \n  ^\nSanket: asmin sthane shabdam vyakaranam cha pashyatu.\n",
  "expected_exit": 1
}
```

### 288_r86_kosh_alias_moves

```json
{
  "case": "288_r86_kosh_alias_moves",
  "compile_command": [
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\win\\sutram.exe",
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\examples\\288_r86_kosh_alias_moves.sm",
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\build\\windows\\acceptance\\288_r86_kosh_alias_moves.exe"
  ],
  "compile_cwd": "E:\\Github_Projects\\Sutram\\build\\round4-review",
  "compile_exit": 0,
  "compile_stdout": "Siddh: 1999 baait sankalit\n",
  "compile_stderr": "",
  "run_command": [
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\build\\windows\\acceptance\\288_r86_kosh_alias_moves.exe"
  ],
  "exit": 0,
  "stdout": "a[0]=41 k[0]=99\na[0]=7 k[0]=99\n",
  "stderr": "",
  "status": "FAIL",
  "expected_stdout": "a[0]=99 k[0]=99\na[0]=7 k[0]=7\n",
  "expected_exit": 0
}
```

### 29_nishkriya

```json
{
  "case": "29_nishkriya",
  "compile_command": [
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\win\\sutram.exe",
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\examples\\29_nishkriya.sm",
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\build\\windows\\acceptance\\29_nishkriya.exe"
  ],
  "compile_cwd": "E:\\Github_Projects\\Sutram\\build\\round4-review",
  "compile_exit": 0,
  "compile_stdout": "Siddh: 588 baait sankalit\n",
  "compile_stderr": "",
  "run_command": [
    "E:\\Github_Projects\\Sutram\\build\\round4-review\\build\\windows\\acceptance\\29_nishkriya.exe"
  ],
  "exit": 0,
  "stdout": "Yantra: Inline Assembly\n==========================\nThis program exits with code 42 using raw x86-64 bytes.\nmov eax,60 / mov edi,42 / syscall  is just:\n  yantra(\"B8 3C 00 00 00\")\n  yantra(\"BF 2A 00 00 00\")\n  yantra(\"0F 05\")\nExiting with code 42...\n",
  "stderr": "",
  "status": "FAIL",
  "expected_stdout": "Yantra: Inline Assembly\n==========================\nThis program exits with code 42 using raw x86-64 bytes.\nmov eax,60 / mov edi,42 / syscall  is just:\n  yantra(\"B8 3C 00 00 00\")\n  yantra(\"BF 2A 00 00 00\")\n  yantra(\"0F 05\")\nExiting with code 42...\n",
  "expected_exit": 42
}
```

## Focused checks and limits

Nine memory probes pass on both hosts; source and literal expectations are in contracts.py and programs/. Existing string/allocation contract tests: Windows 8 pass, 1 Linux-only skip; Linux 9 pass. Focused Linux gates: codegen 12, packs 33, library 229, properties 86, crash corpus 227 (see checks-linux.json). This is not a run of all 62 gates.

The Windows harness now supplies the same Hindi flag required by the test. Test 29 contains literal Linux exit syscall bytes (`yantra`); it is explicitly skipped, not counted as passing. No compiler reinterpretation of raw assembly.

**Release limitation:** this cheapest port is functional but expensive: first arena use commits 1 GiB; each kosh commits 64 MiB. `cost-windows.json` measures private commit versus working set. Recommend reserve-only regions with incremental page commitment before shipping this as a general Windows memory implementation. No claim of complete memory safety, low-memory resilience or unbounded alias stability.

Infrastructure retries: the first finalize.py attempt used Windows cp1252 and failed reading UTF-8 source; rerun with -X utf8 succeeded. Sandbox temporary-directory denial in Windows unittest was rerun with host permission (initial JSON preserved). WSL git could not resolve Windows worktree metadata; fixture.py restored the exact committed file bytes using Windows git before Linux library checks. No fixture or golden changes are included.

Commands: from this worktree run `python Windows-to-Sarvam/win-round4-2026-11-03/verify.py final`, `python .../contracts.py`, `python .../cost.py` (Windows only), `python .../fixture.py` (Windows git), and `python .../checks.py`. Linux equivalents use `wsl -d Ubuntu -- python3 /mnt/e/Github_Projects/Sutram/build/round4-review/Windows-to-Sarvam/win-round4-2026-11-03/<script> [stage]`. Full expanded compiler/test argv appear in JSON evidence.
