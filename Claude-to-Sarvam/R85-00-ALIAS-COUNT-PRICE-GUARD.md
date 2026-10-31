# R85-00 — Option 1 breaks 3 programs (so nothing built); a forwarding pointer costs 3 instructions and 8–16% per read; the divergence cases are stale handles to LIVE blocks

- **Commit on `main`:** `cd96414` — documentation and evidence only.
- **Compiler: `Sutram 1.0 (v278)` — unchanged**; `sutram_compiler`, `sutram.exe`, `win/sutram.exe` byte-identical to
  origin/main's. Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=255`, FAIL=0.** Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 57 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).**
- **The guard, origin/main → this tree: Linux ELF and Linux PE — 665 programs, 538 byte-identical, 127 refused identically, 0 DIFFER, 0 new.** **NOT RUN: the Windows compiler under
  Wine** — its `.exe` is byte-identical to origin/main's.

## WS1 — option 1 breaks 3 programs: here they are, and I did nothing else

Recounted this round on this tree with R83's variant (`evidence-r85/ws1-option1-count.txt`): **665 programs,
3 refused that v278 compiles, no library module refused.**

| program | what it is |
|---|---|
| `examples/252_r38_alias_kosh_oob.sm` | R38's fixture: "a kosh alias via assignment must be bounds-checked like the original" (`w = v`, then `w[5] = …`) |
| `examples/255_r42_alias_kosh_push.sm` | R42's fixture: "an alias of a kosh is the kosh" (`w = v`, `kosh_push(w, 4)`) — true only while no push relocates it |
| `examples/287_r82_kosh_after_mandapa.sm` | mine, R82: `bahar = k` inside a block, read after it |

As the brief says: count and programs reported, nothing built.

## WS2 — the forwarding pointer, priced and not built

**What it is:** one more header word per `kosh`. On a relocating growth, the old header's word gets the new
buffer's address. Every access through a `kosh` name checks the word first and follows it if it is set (a chain,
if the `kosh` moved more than once; the follow path can also write the new address back into the variable).

**Instructions on `k[0]`: 3 on the path that is always taken** — `mov rdx,[k-F] ; test rdx,rdx ; jnz follow` —
in front of today's 10. Measured without touching the compiler: v278's own `k[i]` sequence (from `objdump` of a
compiled program) copied into a standalone NASM loop, 200,000,000 reads, with and without the check
(`evidence-r85/ws2-forwarding-price.txt`; the host is shared and noisy, so read the range):

| | per access | cost |
|---|---|---|
| a loop that does nothing but read `k[i]` | +0.1 ns | **+8% to +16%** |
| R82's worst case, `padh(kosh k, i)` with the R82 entry check, one read per call | +0.4 ns | **+8% to +15%**, on top of R82's +11% |

**So: yes, under three instructions on the fast path — but not cheap where it counts.** The cost lands on *every*
access through *every* `kosh` name, in every program that has a `kosh`. R82's check runs once per call, and only
in programs with a `kosh` in a block. Measured the same way, the forward check costs about as much again as R82
in R82's worst case, and more in a tight loop over a `kosh`.

**What else it costs, beyond the instructions:**
- **Every program with a `kosh` changes bytes** (the header word and the checks), unless it is switched on per
  program only when a copy `x = k` exists. That is possible at parse time, as R82 does.
- **Every access site, not one:** `k[i]` read and write, the nine `kosh_*` builtins, `kosh` parameters, and
  R82's header (which already uses `[-40..-24]`).
- **It forbids recycling.** The old header must outlive every stale name, so the old buffer can never be freed.
  At best its cells can be, keeping a tombstone header, which needs allocator support. It fixes the alias
  *without* making recycling safe; option 1 does make it possible.
- **It does not reach raw addresses** (`k + 0`, a `kosh` returned as a plain value). Those are not `kosh` names,
  so there is nothing to follow.

**What it buys:** both names really are one `kosh`, on every system. Linux and Windows agree, and no program
breaks (the three fixtures would start passing *for the reason their comments give*).

**My judgement:** option 1 (zero run-time cost, a compile error at the copy) beats the forwarding pointer for
Sutram: the copy is never needed, and the error says what to do. Use the forwarding pointer only if `vitti a = k`
must keep working, and then expect about 10% on `kosh`-heavy loops and no recycling.

## WS3 — the divergence cases in the guard-page build: stale handles reading a LIVE block

The five R84 cases under the guard-page build (every block its own mapping, ending on the byte before an
unmapped page): **none faults** (`evidence-r85/ws3-guard-page.txt`). To show which kind they are, one more
program: after the divergence, take the stale name's address as a plain number and read its cells.

| | guard-page build | ordinary build |
|---|---|---|
| the old block's last cell | `111` | `111` |
| **one cell further** | **SIGSEGV** — the guard page | `0` |

**The stale name points at a block that is still allocated, mapped to its last byte, and guarded right after it.**
So these are **stale handles reading a live block**, not a freed one, and no build ever frees: there is no `munmap`
or `VirtualFree` anywhere in `src/`. The guard-page build would catch a read of a *freed* block, the moment
recycling exists. Today there is none to catch.

## What I did not do

- **No compiler change**: option 1 breaks 3 programs (your rule); the forwarding pointer was priced, not built
  (your instruction). The microbenchmark sources are in the evidence.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`. **Not run:** real
  Windows; the Windows-compiler guard path (identical binary).
