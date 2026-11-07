# Diagnostic commands and reproduction

Test base: `30be5ac8` on main. The two commits fetched since the previous round
changed only assignments to Claude and Muse. Original v305 compiler/IDE hashes
were checked before execution. Product sources, library, examples, and goldens
were not edited. No installer, v306 build, candidate fix, or CI was executed.

From `E:\Github_Projects\Sutram` in PowerShell:

```powershell
python Windows-to-Sarvam/win-diag-v305-2026-11-06/diagnose.py
& .\Windows-to-Sarvam\win-diag-v305-2026-11-06\ide.ps1
```

`diagnose.py` uses the retained previous B3 executable, checks its exact hash,
compiles the five new allocation probes with `win/sutram.exe`, then runs native
children with these commit limits:

```text
B3: 64, 128, 256 (recheck); 384, 512, 640, 768 MiB (stop on exit 0)
2M: 64, 128, 256, 384, 512, 640, 768 MiB
first-page nirmmita: 64 MiB
64 MiB-budget mandapa: 64 MiB
page-touch nirmmita control: 64 MiB
16 MiB-budget mandapa control: 64 MiB
```

One MiB is 1,048,576 bytes. `job_runner.py` uses Win32 Job APIs, not shell memory
settings: create child suspended and without a console window, assign Job,
resume, wait at most 60 seconds, capture stdout/stderr, then close handles.
The Job has PROCESS_MEMORY and KILL_ON_JOB_CLOSE flags; limits are queried back.
No host-wide limit, registry, PATH, execution policy, or installed files change.

All exact compiler commands and binary SHA-256 values are in `oom.json`. All
exact per-process limits, executable commands, and output paths are in its runs.
All Task C commands and working directories are in `harness.json`.

On a fresh checkout without the previous B3 artifact, compile the retained
`B3.sm` using the original v305 compiler into a scratch directory and run that
binary with `job_runner.run_limited`. Record its hash and provenance; do not
silently substitute the PR #66 candidate or call it the retained executable.
The current script deliberately refuses a missing/different B3 artifact.

`ide.ps1` opens a normal visible IDE for the requested screenshots, reads native
control text, and captures only that application's window via PrintWindow.
It closes the process it launched in a finally block. Screenshots are converted
from captured BMPs to PNG without modifying their content. `ui-helper.ps1`
was reused from review branch `codex/windows-v305-2026-11-06`; `job_runner.py`
was reused from PR #66's native test helper. Neither imports its candidate runtime.

The new probe sources are eight `.sm` files in this folder. The unchanged
`01_hello.sm`, `02_arith.sm`, `105_block_nesting_capacity.sm`, and
`79_ayojan_cwd.sm` are existing repository examples, not duplicated or edited.
The original owner handoff is retained as `REQUEST.md`. `verification.json`
records evidence consistency and the post-run no-product-change check.
