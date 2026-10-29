# R59-00 — The real `nirmmita` path, measured in Sutram, and the three options priced

- **Base:** `main` at `b610693`. Compiler **v261**, the committed binary. **No source change this round.**
- **Machine:** Linux x86-64 cloud VM (Firecracker), 2 cores, Intel Xeon @ 2.10 GHz, 7 GB RAM, `vm.overcommit_memory = 0`.
- **Every number below was measured here, and the programs are in `evidence-r59/`.** Where a figure is an estimate,
  it says so.

## The answer first

| | per allocation | 100,000 × 64 B | memory for 100,000 × 64 B (6.4 MB of data) |
|---|---|---|---|
| **`nirmmita` today**, one call each, each touched | **4,600–8,200 cycles** | 464–822 M cycles | **400,000 KB** |
| **one `nirmmita` + manual offsets** (a region's work) | **50–62 cycles** | 5.2–6.5 M cycles | **6,272 KB** |
| **ratio** | **87× – 157×; typically about 110×** | | **64×** |

**The real path is about 110× slower than a bump, not 1,000×.** **And it uses 64 times the memory, which nobody had
measured.**

**Where the 6,000 cycles go** (`evidence-r59/ws1-breakdown.txt`):

| | cycles |
|---|---|
| **the `mmap` call itself** (same loop, block not touched) | **~1,200** |
| **the first touch: a page fault, and the kernel zeroing a 4 KiB page** | **~5,000** |
| a trivial syscall here, `getpid`, for scale | ~230 |

**Every `nirmmita`, whatever its size, costs a whole page.** That page has to be faulted in and zeroed, and it stays
resident. **The cost is page granularity much more than the syscall.**

## WS1 — measured inside Sutram

**The language has no clock.** None of its ~45 builtins reads the time, and no library function does. **So I read
the CPU's cycle counter with the inline machine code the language already has:**

```sutram
yantra("0F 31")         # rdtsc
yantra("48 C1 E2 20")   # shl rdx, 32
yantra("48 09 D0")      # or rax, rdx
yantra("48 89 C3")      # mov rbx, rax   - rbx is where the compiler keeps t0
```

**This is not a benchmark in another language.**
- **The loop, the allocation and the touch are ordinary Sutram,** compiled by v261 the ordinary way.
- **Only the two clock reads are inline bytes.**
- **I checked in the disassembly that `t0` and `t1` live in `rbx` and `r12`, and that nothing in the loop touches
  either register.** The programs also print the last value read back: 99999 in both.

**The two programs** (`evidence-r59/per_call.sm`, `one_block.sm`) do the same work: 100,000 blocks of 64 bytes, each
touched with `likh8(p, i)`.
- **(a)** has one `nirmmita(64)` per block.
- **(b)** has one `nirmmita(100000 * 64)` and `p = base + i * 64`. **No region exists yet, so this is the manual
  form you asked for.**

**Five runs at 100,000** (`ws1-runs.txt`): ratios 105.9, 105.5, 90.5, 95.5 and 87.3.

**Scaling** (`ws1-scaling.txt`), one run each:

| n | `nirmmita` per call | one block | ratio |
|---|---|---|---|
| 10,000 | 6,358 cycles | 50 | 125× |
| 100,000 | 8,221 | 52 | 157× |
| 200,000 | 6,355 | 57 | 110× |
| 1,000,000 | 7,006 | 62 | 113× |

**The cost does not grow with the number of live mappings.** **1,000,000 separate `mmap`s succeed** although
`vm.max_map_count` is 65,530, because the kernel merges adjacent anonymous mappings.

**Why my number differs from v414's 250,000 cycles: almost certainly the machine.**
- The mechanism here is the same: `mmap` per call, never freed.
- A trivial syscall costs about 230 cycles here, which is an ordinary VM.
- A sandbox that intercepts syscalls makes each one tens of times dearer, and the page faults with them.
- **So the ratio is a property of the machine, not only of the language.** On bare metal I would expect something
  close to this VM. Under a syscall-intercepting sandbox, nearer v414. **The direction never changes.**

**The memory figure is the more important one, and it does not depend on the machine** (`ws1-rss.txt`):
- **100,000 × 64 B is 400,000 KB resident with `nirmmita`, against 6,272 KB with one block.**
- **1,000,000 × 64 B is 4,000,000 KB, 4 GB, against 62,464 KB.**
- **A program that makes a million small allocations needs 4 GB today.**

## WS2 — the three options priced

**How the prices are estimated (NOT BUILT):**
- They are calibrated on this compiler's own code.
- **An emitted machine-code sequence costs about 2 lines of NASM per byte:** `r38_nirm_seq` is 97 lines for 45
  bytes, at `src/sutram_compiler.asm:19889-19988`.
- **A counted allocation variant was 108 lines** (`src/r38_fail_alloc.inc`).
- **A feature with its own statement, generator hooks and output was 813 lines** (`src/r45_debug.inc`).

**Two facts shape every option:**
1. **`nirmmita` is emitted inline at every use.** There is no allocator function in the binary, and
   `emit_nirmmita_from_rax` is called from 4 places:
   - the `kosh` declaration, `:12947`;
   - the `mala` declaration, `:13027`;
   - `kosh` growth, `:15799`;
   - the builtin, `:17042`.
2. **On Windows, the runtime adapter knows six syscalls only**: 0, 1, 2, 3, 9 and 60 (`win/winrt_blob.asm:66-77`).
   **Any other returns ENOSYS.**
   - So `munmap`, `mprotect` and `madvise` do not exist on Windows.
   - Adding one means a new Windows import in `win/pe_imports.inc`. **That table is in every `.exe`, so the guard
     would show every PE program as DIFFER.**
   - **Every option that releases memory has this Windows cost.**

### Option 1 — explicit free: `munmap` plus a keyword

| Part | Where | Lines (est.) |
|---|---|---|
| builtin name, id, table entry, arity | `:191`, `:270`, `:540`, `:759` (as `nirmmita`) | ~6 |
| dispatch and emitter: evaluate the arguments, `mov rdi`, `mov rsi`, `mov eax, 11`, `syscall` | beside `.ge_call_nirm`, `:17038` | ~50 |
| Windows: adapter case 11 → `VirtualFree(p, 0, MEM_RELEASE)`, and the import | `win/winrt_blob.asm`, `win/pe_imports.inc` | ~16 |
| **total** | | **~70–80** |

**It must take the size as well as the pointer, `‹free›(p, n)`.** A plain `nirmmita` block has no header, so nothing
knows its length; `munmap` needs it. Adding a header changes the layout of every allocation.

**What it touches:** on Linux, nothing existing. It is a new builtin, and the guard cannot see it. On Windows, every
`.exe`.

**What goes wrong:**
- **Double free, wrong size and use-after-free are all possible.**
- **Use-after-free is silent,** because `mmap` reuses freed address ranges for the next allocation.

### Option 2 — a region: stack, bump pointer, one `mmap` per region, `munmap` at close

| Part | Where | Lines (est.) |
|---|---|---|
| keyword (Latin and Devanagari) and its `kw_table` entry | `kw_table`, `:473` | ~6 |
| parse a block statement, and an AST node | modelled on `.ps_for`, `:9327` | ~40 |
| a bump allocator replacing the inline `mmap` inside regions: fast path, slow path (a new chunk), and the 4 call sites | `emit_nirmmita_from_rax`, `:19889` | ~150 |
| region enter and exit: save and restore the bump, the region stack as hidden globals (the R46 mechanism, `r56_register_global`, `:22716`), `munmap` at close | the new statement's generator | ~120 |
| **every way out of a region runs its close:** `nivartanam` (`AST_RETURN`, generated at `:12605`), `krama` / `agrim`, break and continue (the patch lists, `:977-980`) and `sthagita` | existing return, break and continue generation | ~60 |
| zero on reuse. **Required** (see below). | the exit sequence | ~20 |
| Windows adapter and imports | `win/` | ~40 |
| **total, without the escape check** | | **~430–500** |

**You asked me to be honest if Option 2 is much larger than Option 1. It is: about 6×, before the escape check, and
it touches existing code paths.** Return, break and continue must close the region.
- That change can be confined to code inside a region, so programs without a region stay byte-identical.
- **But it is a change to the paths every program uses, and it is the riskiest part.**

**Zeroing on reuse is not optional.** I built a throwaway compiler, in a scratch copy only, whose `nirmmita` returns
memory filled with `0xAA` instead of zeros, and ran every library proof on its own:
- **4 of the 226 depend on zeroed memory.** `r39_scratch_from_set` and `r9_guard_cells` give wrong answers.
  `r11_brihat_guards` and `r11_page_edges` hang.
- The suite's 225 programs all still pass.
- A fifth proof, `file_read`, also failed, but it fails the same way under my harness with the normal compiler, so it
  is not counted.
- **A region that hands back memory without zeroing it breaks those four.**

### Option 3 — the escape check, on its own

**First the fact that decides its size: in Sutram a pointer is an integer.** A `nirmmita` result is a `vitti`. It
can be:
- added to (`p + 8`);
- stored with `likh8(cell, p)`;
- put in a `mala` cell, passed to a function, kept in a global.

**A compile-time check therefore cannot be complete.** Once a pointer is stored into memory or mixed into
arithmetic, the compiler no longer knows it is a pointer.

| Version | What it catches | Lines (est.) |
|---|---|---|
| **sound** | everything | **not possible without a pointer type.** That is a language change, Option C in `MEMORY-DESIGN.md`. |
| **conservative lint** | inside one function: track variables assigned from an allocation inside the region, through plain assignment and `+`/`-`. Flag returning one, assigning it to a variable from outside the region or a global, storing it with `likh8` or `x[i] =`, or passing it to a call. | **~250–350.** The compiler has no data-flow pass to extend; the debugger's variable collection is the nearest thing. |
| **dynamic fail-stop** (my R60 proposal) | at runtime: a pointer used after its region closed **faults at the use**, every time, instead of reading reused memory | **~40.** `mprotect` + `madvise` at close, and the addresses are never reused. |

**The lint would be about as large as the region itself and would still miss the escapes through memory and calls.
The dynamic version is a tenth of the size and misses nothing, but reports at run time, not compile time.**

## WS3 — the `kosh` leak

**Measured:** 1,000,000 pushes onto `kosh k[1]` take 16,000 KB. The same pushes onto `kosh k[1000000]`, which never
grows, take 7,808 KB.
- **About 8.2 bytes per item are abandoned in old blocks,** roughly the size of the final block, as doubling
  predicts.
- The 15.3 in the brief is the whole footprint per item, including the 8 live bytes. **The leak itself is about 8.**

**Can it be fixed by `munmap`-ing the old block when `kosh` moves? No, not safely, in the current design.**
- **Use-after-free is possible today, three ways,** all compiled and run with v261 (`evidence-r59/kosh-aliases.txt`):
  - **A** — `vitti a = k`, then grow `k`, then read `a[0]`;
  - **B** — `m[0] = k`, into a `mala` cell, then grow, then read through `m[0]`;
  - **E** — pass `k` to a function that keeps it in a global, then grow, then read the global.
- **Today each prints 7 from the old block: stale but readable. With `munmap` on move, each reads unmapped memory or
  another allocation.**
- **Two things the compiler already prevents:**
  - `kosh_push` on a parameter is refused (`.ge_call_koshpush`, `:15651`), so a callee never grows its caller's
    `kosh`;
  - a module-level `kosh` cannot be grown inside a function.
- **So the only way to the old block is a copy of the pointer, and A, B and E make one.**

**What does fix it, safely: a `kosh` that never moves.**
- **Reserve address space for it at declaration with `MAP_NORESERVE`, and grow by updating the capacity field, with
  no copy.**
- I tested the mechanism: one `MAP_NORESERVE` mapping of 16 TiB succeeds here. Touching its first and last byte
  leaves the process at 392 KB resident (`evidence-r60/noreserve.txt`).
- **The old pointer stays valid, so A, B and E stay correct.** Nothing is abandoned, and the O(n) copy disappears.
- `kosh_cap` can keep reporting the doubled capacity, so no program's output changes.

| Part | Where | Lines (est.) |
|---|---|---|
| declaration: reserve R bytes, flags `0x4022` | `:12900-12973` | ~10 |
| growth: within R, update capacity only; beyond R, today's copy | `:15720-15900` | ~40 |
| Windows: `MEM_RESERVE`, then `MEM_COMMIT` as it grows | `win/winrt_blob.asm` | ~25 |

**What could go wrong:**
1. **Address space per `kosh`.** With R = 64 MiB, a program could hold about 2 million live `kosh`. A `kosh`
   declared inside a loop allocates a new one every pass, today and after; with R reserved each time, that ceiling
   arrives far sooner than today's.
2. **`--fail-alloc`.** Growth would no longer allocate, so the fault-injection numbering in `tests/r38` changes and
   must be re-baselined.
3. **Windows needs `MEM_COMMIT` as it grows,** so it changes every `.exe` (above).
4. **Beyond R, it falls back to today's move** and keeps today's stale-copy behaviour. It is never worse than now.

## What I did not do

- **No implementation.** The prices are estimates calibrated as stated. The 0xAA compiler was a scratch build,
  deleted after the run.
- **No measurement on Windows.** The adapter facts are read from `win/`, not run.
- **Not touched:** `src/`, `lib/`, `tests/`, `lang/`, `backups/` and `Windows-to-Sarvam/`.
