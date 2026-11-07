# v306 OOM result: two crash-after-message cases remain

The installed v306 compiler generated every executable in this table. The
runner and three probes are byte-for-byte copies from the v305 diagnostic round;
[probe-identity.json](probe-identity.json) records both copies' hashes. The runner
assigns each new child to its configured process-memory Job before resuming it.
Each record includes the queried limit, executable hash, exact streams, exit
code, timeout status and elapsed time. No source or runtime changes were made.

Every refusal row produced empty stdout and exactly this stderr, with one LF:

```text
Sutram truti: smritih na labdha
```

| Probe | Job limit (MiB) | Exit | Stdout | Seconds | Result |
| --- | ---: | --- | --- | ---: | --- |
| B3 100 million pushes | 64 | 1 | empty | 0.0774 | PASS |
| B3 | 128 | 1 | empty | 0.0688 | PASS |
| B3 | 256 | 1 | empty | 0.1484 | PASS |
| B3 | 512 | **3221225725 / 0xC00000FD** | empty | 0.3099 | **FAIL** |
| B3 | 640 | 1 | empty | 0.4180 | PASS |
| B3 | 768 | 0 | `100000000\n` | 0.4878 | PASS; stderr empty |
| B3 | 1024 | 0 | `100000000\n` | 0.4724 | PASS; stderr empty |
| B3 | 2048 | 0 | `100000000\n` | 0.4682 | PASS; stderr empty |
| mandapa 64 MiB budget, 2 million allocations | 64 | **3221225725 / 0xC00000FD** | empty | 0.1789 | **FAIL** |
| Raw 100 MB allocation, one write per page | 64 | 1 | empty | 0.0829 | PASS |

[Initial raw results](oom.json). Initial OOM and native-suite runs overlapped.
To check that these failures were reproducible without that overlap, both failed
cases and two passing controls were run serially five more times after the suite
and IDE had finished:

| Case | Five additional runs |
| --- | --- |
| B3, 512 MiB | **5/5 `0xC00000FD`**, each after the exact stderr refusal |
| mandapa, 64 MiB | **5/5 `0xC00000FD`**, each after the exact stderr refusal |
| B3, 640 MiB | 5/5 exit 1, exact stderr refusal |
| Page-touch, 64 MiB | 5/5 exit 1, exact stderr refusal |

[Repeat raw results](oom-repeats.json), [repeat script](repeat_oom.py).
Neither failed case timed out. Including the first run, each failed **6/6**.
Windows SDK 10.0.26100.0 `shared/ntstatus.h:4410` names this exit status
`STATUS_STACK_OVERFLOW`. The exact mechanism producing it has not been diagnosed.
The generic message now appears, but that alone does not close the OOM defect.

The previously measured successful 768 MiB boundary remains successful in this
run. Runtime numbers are observations from this machine, not performance gates.
No source fix, additional runtime change, repinning or release acceptance is
proposed without Sarvam's independent review.
