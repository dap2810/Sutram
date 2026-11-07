# v307 native Windows OOM boundary — still fails

6 November 2026, Windows x64. The installed compiler, SHA-256
`0444b43552f6140147ee4701aeac857d585086681bbe4e5bd71d8f90bedd3f7b`,
compiled every probe. The process-local Job Object runner is unchanged from the
v306 follow-up. Each row is three sequential native executions; no Wine/WSL.

`FD` below means decimal `3221225725`, hexadecimal `0xC00000FD`
(`STATUS_STACK_OVERFLOW`), a failure. `1` means a clean refusal: exit 1,
the exact expected stderr, empty stdout, and no timeout.

| B3 limit | Run 1 | Run 2 | Run 3 | Message complete? |
| ---: | --- | --- | --- | --- |
| 448 MiB | 1 | FD | FD | Yes, all three |
| 480 MiB | FD | FD | FD | Yes, all three |
| 512 MiB | FD | FD | FD | Yes, all three |
| 544 MiB | 1 | 1 | 1 | Yes, all three |
| 576 MiB | 1 | 1 | 1 | Yes, all three |
| 608 MiB | 1 | 1 | 1 | Yes, all three |
| 640 MiB | 1 | 1 | 1 | Yes, all three |

`A3-mandapa.sm`, 64 MiB: **10/10 FD**, zero clean refusals.
`A3-nirmmita-touch-pages.sm`, 64 MiB: **exit 1, PASS** (one control run).
Total: **32 runs, 14 clean refusals, 18 abnormal exits, no timeout**.

All 32 stderr files contain exactly 32 bytes:
`b'Sutram truti: smritih na labdha\n'`. Every one ends with LF; stdout is empty.
Raw bytes are retained under [streams](streams), protected from Git newline
conversion by [.gitattributes](.gitattributes). [oom.json](oom.json) records
every exit, timeout flag, message length/hex, command, executable hash and timing.
[oom.py](oom.py), [job_runner.py](job_runner.py), and the three `.sm` probes
are included unchanged except for the diagnostic version/hash selection.

**Correction to REQUEST A4:** complete stderr proves that the complete bytes
were observed after process termination. It does not prove that the exception
handler finished, that WriteFile returned to its caller, or where the later
stack overflow occurred. No fault stack was captured in this round.

The v307 source checks the return from `AddVectoredExceptionHandler`; this is
not evidence that registration was absent in v306. The measured v307 boundary
still has 512 MiB failing and 544 MiB passing. Handler-registration checking
does not close the reported crash-after-message defect. Root cause and a
runtime fix remain for independent investigation; no compiler/runtime code was
changed here.
