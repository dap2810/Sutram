# Round 98 WS3 — Gate 0: a five-minute preflight before any benchmark number is printed

**This is a future checklist**, not a benchmark run and not proof of universal superiority. The owner has deferred performance work until language development is further along. The complete seven-workload acceptance thresholds remain in [ROUND-97-WS3-BENCHMARK-ACCEPTANCE.md](ROUND-97-WS3-BENCHMARK-ACCEPTANCE.md). Gate 0 means **COMPARABLE + CORRECT**, or the timing is **INVALID**.

## Five-minute implementer checklist (five checks, no new tool infrastructure)

Run from the **clean benchmark project** with a pre-existing, exact-source `gates.sh`/regression/fuzz receipt. For any missing input/receipt, **STOP** and mark `NOT_READY`; five minutes is a quick preflight, *not* permission to skip the full gate suite.

- [ ] **1. Pin the exact binaries and environment (≈1 min):** `git rev-parse HEAD`; `sha256sum bench/input.bin bench/sutram.bin bench/c.bin bench/zig.bin`; capture `uname -a`, compiler/linker versions and **full build flags** for all three. If any binary, source input, target ISA, safety profile, or build recipe is unidentified: **INVALID**. Do not silently compare Zig ReleaseFast to a checked Sutram build.
- [ ] **2. Check equal work (≈1 min):** confirm all three use the **same input bytes/seed/N, data-structure capacity growth, buffering, thread count, integer overflow and bounds/error policy**. Require externally visible output/checksums, no optimised-away computations. A different algorithm or unaligned safety semantics: **INVALID**, not a loss.
- [ ] **3. Actually run each program (≈1 min):** `./bench/sutram.bin < bench/input.bin > /tmp/r98-s.out`; `./bench/c.bin < bench/input.bin > /tmp/r98-c.out`; `./bench/zig.bin < bench/input.bin > /tmp/r98-z.out`. Record **each exit code individually** (do not lose it in a combined shell command). Then `sha256sum /tmp/r98-*.out` and `cmp -s /tmp/r98-s.out /tmp/r98-c.out && cmp -s /tmp/r98-s.out /tmp/r98-z.out`. Output hashes, process exits, errors or validated error-code semantics differ: **INVALID**. Record whether a program was cached/warmed; no timing recorded yet.
- [ ] **4. Confirm current regression evidence (≈1 min):** verify a full `tools/gates.sh`, suite, crash corpus, fuzz and applicable real-OS gate **PASS receipt tied to this exact Git commit/flags**. `Wine` is *not* native Windows acceptance. If the receipt is stale/missing, **NOT_READY**; run the full suite before any claim. A current gate failure is **INVALID**. The five-minute preflight cannot itself make a full suite pass.
- [ ] **5. Authorize timing/report label (≈1 min):** record `GATE0=PASS` with three exit codes, three output hashes, exact SHA/version/flags, fairness notes and receipt IDs. **Only then** collect ≥30 independently launched, randomly ordered timing runs/profile, paired bootstrap CI and a second host as required by R97. Until statistical acceptance is met, label individual timings **MEASUREMENT ONLY**; never `FASTER IN ALL ASPECTS`.

## Minimal decision table

| State | What may appear in the report? |
|---|---|
| `GATE0=PASS` on an exact pinned source and comparable semantics | Raw per-run measurements may be recorded, **not** an automatic speed victory |
| Missing environment, outputs, comparable work or PASS receipts | `NOT_READY` / **no leaderboard number** |
| Different outputs/exit/error-policy or known regression failure | `INVALID` / **exclude from comparison**, disclose cause |
| Valid measurements but speedup less than R97 threshold | `NOT_MET` — honest benchmark loss |

**Positive smoke example (not an actual result):** `SHA/flags pinned; outputs sha256 identical; exit 0/0/0; matching safety; full-gate receipts current → GATE0 PASS`. **Negative example:** `Zig uses unchecked wrap, Sutram traps on overflow → INVALID` even if Zig's wall clock looks faster.

**Status:** checklist **DELIVERED**; new comparative benchmark, gate suite and Windows native run **NOT_RUN** in Round 98. Gate 0 is actionable in five minutes only when required artifacts already exist.
