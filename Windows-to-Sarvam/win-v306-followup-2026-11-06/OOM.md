# v306 follow-up: the failing range extends below 512 MiB

Tested the installed v306 compiler, SHA-256
`d3f3dc157baddec973947a4d5f5b1760203542b6576b11c15aab6a757f48df77`,
against repository source `da349daf` (the compiler bytes are unchanged from the
previous v306 round). No product code or original examples were changed.

## A1 — B3 boundary, three executions per limit

`1` below means a clean refusal: exit 1, empty stdout, and the exact diagnostic
on stderr. `FD` means exit **3221225725 / 0xC00000FD**, the observed
`STATUS_STACK_OVERFLOW` outcome, despite the complete diagnostic.

| Limit | Run 1 | Run 2 | Run 3 | Message complete? | Abnormal exits |
| ---: | --- | --- | --- | --- | ---: |
| 448 MiB | 1 | FD | FD | Yes, 3/3 | **2/3** |
| 480 MiB | FD | FD | FD | Yes, 3/3 | **3/3** |
| 512 MiB | FD | FD | FD | Yes, 3/3 | **3/3** |
| 544 MiB | 1 | 1 | 1 | Yes, 3/3 | 0/3 |
| 576 MiB | 1 | 1 | 1 | Yes, 3/3 | 0/3 |
| 608 MiB | 1 | 1 | 1 | Yes, 3/3 | 0/3 |
| 640 MiB | 1 | 1 | 1 | Yes, 3/3 | 0/3 |

**This is not a 512-MiB-only failure.** It also occurs at 480 MiB and is mixed
at 448 MiB in this sample. The three passing 544-MiB observations do not establish
a universal exact threshold. No timing or allocation mechanism is inferred from
this small boundary map alone.

## A2 — debugger availability

No ProcDump, WinDbg/WinDbgX or CDB was found through PATH, the checked SDK/common
tool locations, Windows application aliases, or the Microsoft.WinDbg package
query. No debugger was installed. **Stack capture skipped as instructed.** There
is no captured fault address or thread stack, and no observed repeated-frame
evidence supporting a recursion claim. See [debugger-inventory.json](debugger-inventory.json).

## A3 — redirected stderr is complete

The unchanged Job runner redirects stderr directly to a binary file before
starting each child. After exit, this round additionally read the file as raw
bytes, rather than relying on decoded console text. All **31/31** files are
exactly **32 bytes**, end in `0A`, and contain precisely:

```text
Sutram truti: smritih na labdha
```

Every run's JSON includes byte count, hex encoding, exact-match and final-LF
checks, exit code, executable hash, configured/queried Job limit and elapsed time.
The raw stderr files are in [streams/](streams/). Stdout was empty in every run.

This establishes complete message output before the final abnormal termination.
It does **not** establish that the handler finished, that `WriteFile` returned,
or which later instruction faulted. Source inspection shows optional console-codepage
restoration and `ExitProcess` following the write in `win/winrt_blob.asm`; those
are investigation points, not a localized fault or proven mechanism.

## A4 — mandapa, ten executions at 64 MiB

**10/10 crashed with `0xC00000FD`; 0/10 refused cleanly.** Every one produced the
complete 32-byte stderr message including its LF. No test timed out.

Combined requested runs: **31 total; 13 clean refusals; 18 abnormal exits; 31
complete messages.** A message alone still does not count as a passing refusal.

[All measurements](oom.json), [runner](job_runner.py), [execution script](oom.py),
[B3 probe](B3.sm), [mandapa probe](A3-mandapa.sm), [commands](COMMANDS.md).
