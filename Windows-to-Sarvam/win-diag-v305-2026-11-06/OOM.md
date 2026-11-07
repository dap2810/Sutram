# v305: first success at 768 MiB; failure affects shared lazy commitment

Diagnostic run on native Windows 11 build 26100, 6 November 2026 (local time).
Repository base `30be5ac8`; original v305 compiler and original B3 executable.
No candidate runtime from PR #66 or v306 was used. See [commands](COMMANDS.md),
[machine-readable results](oom.json), and [the requested round](REQUEST.md).

**Measured boundary bracket: 640 MiB fails, 768 MiB succeeds.** The requested
ordered sweep stopped at its first exit 0, at 768 MiB. This is a bracket, not an
exact byte threshold. No Sanskrit OOM refusal appeared at any failing B3 limit.

AV means exit `3221225477` (`0xC0000005`), with empty stdout and stderr.
Success numbers below are stdout, followed by a newline; stderr is empty.

| Per-process commit limit | B3 exit | B3 output | 2M elements | First-page nirmmita | 64 MiB mandapa budget |
| ---: | --- | --- | --- | --- | --- |
| 64 MiB | AV | empty | exit 0, `2000000` | exit 0, `1` | AV, empty |
| 128 MiB | AV | empty | exit 0, `2000000` | not run | not run |
| 256 MiB | AV | empty | exit 0, `2000000` | not run | not run |
| 384 MiB | AV | empty | exit 0, `2000000` | not run | not run |
| 512 MiB | AV | empty | exit 0, `2000000` | not run | not run |
| 640 MiB | AV | empty | exit 0, `2000000` | not run | not run |
| 768 MiB | 0 | `100000000` | exit 0, `2000000` | not run | not run |
| 1024 MiB | not run: stopped | — | not run | not run | not run |
| 1536 MiB | not run: stopped | — | not run | not run | not run |
| 2048 MiB | 0, previous round | `100000000` | not run | not run | not run |

The 2048 MiB entry is explicitly prior evidence for the same executable hash,
from [the original v305 run](../win-v305-2026-11-06/oom-B3-2048MiB.json); it was
not rerun after the stop condition. All other executed entries above are fresh.
The child starts suspended, is assigned to a Windows Job with the stated
`JOB_OBJECT_LIMIT_PROCESS_MEMORY`, then resumes. The runner queries the Job to
verify the limit; timeout is 60 seconds, with kill-on-job-close cleanup.

## What A2 and A3 establish

The exact two-million-element probe succeeds under 64 MiB and every other tested
limit. That demonstrates a successful small case; it does not make OOM behavior
at small budgets generally safe.

The requested 100,000,000-byte `nirmmita` probe touches only `p[0]`. It succeeds
under 64 MiB because reserving a range and committing all its pages are different
operations. Success here does not establish a graceful raw-allocation OOM path.

To distinguish that, the additional [page-touch control](A3-nirmmita-touch-pages.sm)
requests the same 100,000,000 bytes and writes once per 4096-byte page. At the
same 64 MiB limit it **crashes with AV and no output**. The requested
[mandapa probe](A3-mandapa.sm), whose language budget is 67,108,864 bytes, also
**crashes with AV and no output** at that Job limit.

A second control reduces only the language budget to 16,777,216 bytes. At the
same 64 MiB Job limit it **refuses correctly**, exit 1, with stdout:

```text
Sutram truti [E_PARIMITA]: pankti 3 - mandape parimitat adhikam nirmmitam na sambhavati (parimitih 16777216 baait)
```

Thus the known defect is **not confined to kosh growth**. Kosh, touched raw
allocation, and mandapa all exhibit the same silent AV under commit pressure;
the language-budget refusal still works when reached before that pressure.
This is consistent with the shared lazy-commit handler identified in PR #66.
The diagnostic round did not capture a debugger fault address or prove every
allocation site correct/incorrect.

The handoff's suggestion that the limit boundary alone identifies a particular
allocation size or a missing null check is too strong. Limits constrain the
process's total commitment; reserved capacity, touched pages, and other process
commitment differ. In particular, the successful payload writes 800,000,000
element bytes (about 762.94 MiB), consistent with success near 768 MiB without
proving the exact source of every committed byte.

## Identity

- Compiler SHA-256: `db5eda53871aafa4749d593ddef2d29e2841e3eb4d3cb7cdf680223fb45a073c`.
- B3 executable SHA-256: `61c3928c8c34a5612ee5fcb6873f56710b5a92869b6510b0f6062e3913c0dcf2`.
- B3 is the same retained executable used in the previous 64/128/256/2048 MiB
  tests. Its source is retained as [B3.sm](B3.sm).
- Every new source, compile command, binary hash, exit, output and elapsed time
  is retained in this folder or `oom.json`. Timings are single-run observations.
