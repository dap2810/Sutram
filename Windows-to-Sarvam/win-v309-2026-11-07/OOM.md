# v309 native low-memory verification (Task B)

**32/32 requested runs pass.** Every child exits `0x00000001`, produces empty stdout and exactly 32 stderr bytes ending in LF. No `0xC00000FD` or timeout occurred.

The existing Windows Job Object harness imposes a per-process commit limit before the first executable instruction. It does not lower the host memory limit. [Raw per-run results](oom/results.json) include peaks, remaining headroom, runtime, argv and working directory; adjacent directories contain the original stdout/stderr bytes.

| B3 kosh limit | Run 1 | Run 2 | Run 3 | stderr 32 bytes + LF? |
| ---: | --- | --- | --- | --- |
| 448 MiB | exit 1 | exit 1 | exit 1 | Yes, 3/3 |
| 480 MiB | exit 1 | exit 1 | exit 1 | Yes, 3/3 |
| 512 MiB | exit 1 | exit 1 | exit 1 | Yes, 3/3 |
| 544 MiB | exit 1 | exit 1 | exit 1 | Yes, 3/3 |
| 576 MiB | exit 1 | exit 1 | exit 1 | Yes, 3/3 |
| 608 MiB | exit 1 | exit 1 | exit 1 | Yes, 3/3 |
| 640 MiB | exit 1 | exit 1 | exit 1 | Yes, 3/3 |

| 64 MiB control | Repetitions | Exit | stderr 32 bytes + LF? |
| --- | ---: | --- | --- |
| `A3-mandapa.sm` | 10 | 1 in all 10 | Yes, 10/10 |
| `A3-nirmmita-touch-pages.sm` | 1 | 1 | Yes |

Exact stderr for every run:

```text
Sutram truti: smritih na labdha
```

`53757472616d2074727574693a20736d7269746968206e61206c61626468610a` (hex, final byte `0a`).

Sources: [B3.sm](oom/B3.sm), [A3-mandapa.sm](oom/A3-mandapa.sm), [A3-nirmmita-touch-pages.sm](oom/A3-nirmmita-touch-pages.sm). [Runner and exact commands](COMMANDS.md).

This establishes the requested v309 boundary/control behavior on this machine. It does not establish that every possible allocation failure, reserve-allocation failure or teardown path is safe. No new Linux result or general memory-safety acceptance is claimed.
