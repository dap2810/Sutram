# R101-00 — Memory, measured by the kernel. The block holds `nirmmita` flat at 10 million; it does NOT hold `kosh`: about 100 MB. Growth costs at most about 2x. My recommendation is a region per `kosh`, after v1.0, not a forwarding pointer.

- **Commit on `main`:** this round's commit (parent `cee703c`). It adds a measuring tool (NASM + Python), a gate, a test-timeout fix, docs and evidence. No compiler change.
- **Compiler: `Sutram 1.0 (v283)` — unchanged.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=270`, FAIL=0.** Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 59 PASS / 1 FAIL / 1 NOT-RUN.** There is one new gate, `R101 memory` (5 checks). The FAIL is `installer version` (v243 against v283); the NOT-RUN is Windows execution.
- **The guard, origin/main → this tree: Linux ELF and Linux PE — 680 programs, 549 byte-identical, 131 refused identically, 0 DIFFER.** **NOT RUN: the Windows compiler under Wine** — its `.exe` is byte-identical.

## WS1 — the harness, and the four numbers (and two more)

**`tools/peak_rss.py PROGRAM`** prints `peak_rss_kb N exit E`. It forks, `execve`s the program and calls `wait4`, then
reads the child's `ru_maxrss`, which the kernel keeps for the whole life of the process, however short. The forking
part is **`tools/peak_rss.asm`** (NASM, ~140 lines; the script assembles it once).

**Why not Python:** `ru_maxrss` survives `execve`. My first version forked from Python, and every program then
measured 5.4 MB: the interpreter's memory, carried into the child. GNU `time` has the same effect at 264 KB. The NASM
measurer adds almost nothing. For `/bin/true` it reads 1,252 KB, exactly what `time` reads, and for `loop_without`
both give exactly 62,464 KB.

| | peak RSS |
|---|---|
| **1M `nirmmita(64)`, a `mandapa` per pass** | **0 KB** (below what the kernel records; an empty program reports 0 too) |
| **1M, no block** | **62,464 KB** (64 B × 1M = 61 MB: every allocation stays) |
| **10M, a `mandapa` per pass** | **0 KB: flat** |
| 10M, no block | 624,896 KB |
| 100K and no block | 6,272 KB (the scaling is linear without the block and flat with it) |

**So the claim holds for `nirmmita`, measured: flat at 10 million.** It was already measured every round by gate
`R73 scratch` (`/usr/bin/time -f %M`: 264 KB against 62,464 KB, which it prints). It was never true that there was
"only speed evidence", but it wasn't easy to see. Now there are two independent measurers, and they agree.

**A `kosh` grown 100,000 times, and what is abandoned:**

| pushes | grows in place | an allocation between pushes, so it moves at every doubling | abandoned |
|---|---|---|---|
| 100,000 | 768 KB | 1,792 KB | **about 1 MB, i.e. 1.3x the kosh** |
| 1,000,000 | 7,808 KB | 16,000 KB | about 8 MB, 1.05x |
| 10,000,000 | 78,080 KB | 209,280 KB | about 130 MB, 1.7x (the 10M obstacles' arena pages count too) |

Capacity doubles, so the copies left behind add up to about one more `kosh`: **bounded, at most about 2x, not
unbounded.** A single growing `kosh` doesn't leak without limit.

**What the four numbers didn't ask, and the one that matters:**

| | peak RSS |
|---|---|
| **a `mandapa` run 100,000 times that makes a `kosh` of 100 numbers** | **104,576 KB** |
| the same without the block | 101,504 KB |
| one `kosh` made before the loop, `kosh_clear` each pass | **0 KB** |

**The block bounds `nirmmita` and does not bound `kosh`.** A `kosh` made inside a `mandapa` is kept after the block
(the R82 generation check needs it dead, not reused). So a loop that makes one per pass grows by its full size each
time, block or not. **This is the real gap in "a block bounds memory".** The reference already says "Not yet: the
block does not take the `kosh`'s memory back"; it now gives the 100 MB and the `kosh_clear` workaround (§19).

**Gate `R101 memory`** (`tests/r101/test_memory_claims.py`) pins all of it:

- 1M and 10M in a block stay under 1 MB;
- 1M without a block is over 32 MB;
- a moving `kosh` is under 3x one that grows in place;
- **a `kosh` made in a block is NOT reclaimed (over 8 MB).** If someone fixes that, this check fails, and the
  reference must change with it.

## WS2 — the growth leak: what each option costs per push

The measurement changes the question. A growing `kosh` abandons at most about one more `kosh`, which is bounded.
**The unbounded case is a `kosh` made repeatedly**, inside a block or not.

**Option A: a region per `kosh`.** Each `kosh` gets its own `mmap` reservation of virtual address space
(`MAP_NORESERVE`, say 64 MB), and grows in place inside it, always.

- **Per push: nothing.** It is today's in-place path: 10M pushes take 0.05 s, about 5 ns a push.
- **Per `kosh` made:** one `mmap`, about 1 µs (measured with Python's overhead included, so less in assembly). The
  smallest `kosh` costs one 4 KB page once touched; a 100-number `kosh` is 800 B of data.
- **It never moves**, so nothing is abandoned. The block can `munmap` the `kosh`s it made, which closes the
  100 MB gap.
- **The cost:**
  - a capacity cap per `kosh` (the reservation);
  - 4 KB minimum per touched `kosh`;
  - Windows needs its own `VirtualAlloc` reserve/commit in the PE runtime.
- About 3–4 days, Linux and Windows.

**Option B: free the old buffer when it's provably unreachable.**

- **Per push: nothing.**
- **But it needs two things that don't exist:**
  - a **forwarding pointer**, so an alias can't read the freed buffer;
  - a **free list in the arena**: today's arena is a bump allocator and can't free in the middle.
- About a week, and it still doesn't touch the per-block gap.

**A is cheaper, and it fixes more.**

## WS3 — the alias: priced, and what I would ship

- **Forwarding pointer:** +3 instructions per `kosh` read, **8–16% on read-heavy loops** (your R85 figure).
  It is needed only by Option B.
- **Option A makes it unnecessary:** if a `kosh` never moves, `vitti a = k` never diverges. The alias stays an
  alias (two names for one `kosh`, as documented in §16), but the "after it grows, `a` reads the old data" failure
  disappears. **The fix for memory reuse and the fix for aliasing are the same change.**

**What I'd ship:**

- **v1.0: neither.** Growth is bounded at about 2x, measured. The per-block gap is documented with its number and
  its workaround. The alias is documented and pinned (example 288), and the R100 blockers come first.
- **v1.1: Option A**, region per `kosh`, Linux and Windows. It needs no read-path cost; it ends the divergence and
  lets a block return its `kosh`s.
- **I wouldn't ship the forwarding pointer.** It costs every read, and only buys a reuse scheme that A makes
  unnecessary.

## Also fixed: the intermittent `guard pages` failure, found and closed

It failed once each in R87, R90 and this round, and passed when run alone. This round I kept its output: **example
`268_r73_return_value` timed out.**

The guard-page build has no arena: every `nirmmita` is its own `mmap` with a guard page, and a block can't rewind.
So 268, which calls a block a million times, runs in **4.9–5.0 s and 4 GB** there. **The suite's limit was 5 s.**
That is why it passed alone and failed under load.

- **Fix:** `tests/run_tests.py` takes its per-test limit from `SUTRAM_TEST_TIMEOUT` (default still 5).
- `tools/guard_page.py` sets 60 for its build.
- The full gate run after the fix is 59/1/1, and guard pages pass with 270/0.

## Not done

- **Option A:** recommended, not built. It is a v1.1 change, and the R100 blockers come first.
- **Windows memory:** not measured. `ru_maxrss` is Linux; the PE runtime doesn't use the arena anyway (per-call
  `mmap`/`VirtualAlloc`, R65).
- **The 4 GB that 268 uses in the guard-page build** is a property of that test build, never shipped. I noted it,
  not changed it.
- **Not run:** real Windows.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.
