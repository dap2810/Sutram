# R170-00 — The 64 MiB is address space, not memory: mapped, never committed, and only the pages written cost anything (about 36 KB of the 64 MiB here). The region's address and size **are** in the descriptor. But the one-line change does not exist, because **no `kosh` ever dies in the generated code**: no descriptor is released at any scope exit, so there is no line to put a `munmap` beside. Nothing built; what is missing is named below. And 1,000 passes do **not** exhaust the address space: they reserve 63.5 GiB and the program finishes.

## Release line

```
main (the commit carrying this file; SHA in my chat report): Sutram 1.0 (v315) - sampurna sutra, unchanged
     reading and measurement only - no code, document or gate changed; no branch made (WS2's answer is "no")
     gates not re-run (last full run 81 PASS / 0 FAIL / 1 NOT-RUN on 112838ce, Linux, Xvfb); suite and crash
     corpus not re-run · the guard: no compiler changed, identity
staged v316-ready 59d60353: unchanged, waiting on the owner's Windows run
```

**Three corrections to the shared state, each measured:**
- **"Baseline is 312 KB"** - it is **12-24 KB**. The 312 KB was `/usr/bin/time`'s own size (R169-00). `nirmmita` in a block is flat at about 20 KB.
- **"After about a thousand passes ... the program fails"** - not on this Linux: 1,000 passes finish, 20,000 finish (below).
- **"installer `6f9cdbda`"** - main's is `d8ae75c9` since R167 (documents in the payload changed).

## WS1.1 - reserved or committed?

**Neither `PROT_NONE` nor committed: mapped readable and writable, with `MAP_NORESERVE`.**

- `src/sutram_compiler.asm:462-466` (`r101a_a1`): `mmap(0, max(size, 64 MiB), PROT_READ|PROT_WRITE (edx = 3),
  MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE (r10d = 0x4022), -1, 0)`; emitted from `src/r65_arena.inc:656` (`.big`, a
  `kosh` whose new capacity reaches 64 KiB) with the size `max(2 x new, R101A_REGION)`; `R101A_REGION` is
  `src/sutram_compiler.asm:9104`.
- So the kernel gives address space and charges nothing; a page costs memory when it is first written.
- **Windows:** the same request becomes `VirtualAlloc(MEM_RESERVE)` only (`win/winrt_blob.asm:168-176`: `0x2000`
  when `MAP_NORESERVE` is set), and the exception handler commits up to 64 KiB where a page is first touched (R124).
  Reserved, not committed. Read, not run.

**So defect 1 is an address-space leak plus the pages actually written - as you supposed.** Measured per dead
4,097-element `kosh`: **65,536 KB of address space, 68 KB resident** (about 36 KB in its region, 32 KB of earlier
small buffers in the arena).

## WS1.2 - is the region's address recorded where the compiler could find it at death?

**Yes, in the descriptor:** `[d]` is the address of the elements - the region's base when the `kosh` is in a region -
and `[d+8]` is the region's size in bytes, 0 when the elements are in the arena (`src/r65_arena.inc:555-567`). The
growth path already frees with exactly those two words: `src/r65_arena.inc:699-715`, `munmap([d], [d+8])` of the old
region (syscall 11).

## WS2 - is it one `munmap` beside the descriptor's release? No.

**There is no descriptor release.** Nothing in the generated code marks a `kosh`'s end:

- **A block's end** stores the saved mark into the scratch cursor and makes no call (`r73_gen_rewind`,
  `src/r65_arena.inc:404-414`). With R82 on, it also writes 0 into the block's liveness slot (`r82_block_leave`,
  `src/sutram_compiler.asm:10799-10817`) - that makes the block's `kosh` *refused* afterwards; it does not touch them.
- **The descriptor is on the persistent side of the arena** and is never reused - R82's check depends on that
  (`src/sutram_compiler.asm:10640-10651`: "its header is never reused and the check is exact").
- **A function's end, a loop's pass:** nothing. A `kosh` declared in a loop gets a new descriptor each pass; the old
  one is not reachable from anywhere.
- The compiler says so itself: `r108_kosh_alloc`, `src/sutram_compiler.asm:12650-12654` - *"A kosh declared in an open
  mandapa is only remembered ... No arena slot: reclaiming waits for the descriptor."*

**What is missing, in order - none of it guessed, none of it built:**

1. **A death point.** The only place the compiler knows a `kosh` is dead is a `mandapa`'s end: R107-R109 refuse, when
   compiled, every way a block's `kosh` could outlive it, and the compiler keeps the names of the `kosh` declared in
   each open block (`r108_bk_name` / `r108_bk_gd`, the same lines). Outside a block there is no such guarantee, so
   the loop **without** a `mandapa` has no death point at all.
2. **Code at every way out of the block** - its last line, `nivartanam`, `krama`, `agrim`, a failure passed on -
   that, for each `kosh` declared in the block, loads `d` and, if `[d+8]` is not 0, calls `munmap([d], [d+8])` and
   then zeroes `[d]`, `[d+8]`, the length and the capacity (so a second name of the same `kosh` does not free twice).
3. **The variable must be known to hold a descriptor or 0** at each of those exits. A `nivartanam` before the
   declaration runs leaves the slot unwritten; freeing through it would crash. So the slots are zeroed on entry.
4. **A `kosh` declared inside a loop inside the block** reaches the exit as one variable holding the *last*
   descriptor. The earlier passes' regions are already unreachable. The block-per-pass shape (the block inside the
   loop) is the one this would fix; a loop inside one block it would not.
5. **`parimana()`** must give back what the region counted, as growth already does (`r65_arena.inc:704-709`).
6. **Windows:** the runtime's `.free` already turns `munmap` into `VirtualFree(MEM_RELEASE)`
   (`win/winrt_blob.asm:184-191`); nothing new, but not run there.

That is items 2-5 at four exit paths, in the code generator, on a path R82 and R108 share - a design-sized change
that overlaps what ChatGPT is designing (when is a `kosh` dead?). **So nothing is staged.** If you want exactly this
narrow version built - "a `kosh` declared directly in a `mandapa` gives its region back at the block's end" - say so
and I will build it on a branch with the guard; it fixes the block-per-pass case and nothing else.

## WS3 - what the loop does today (the "before"; there is no "after")

**Method:** as R169 - the program prints a pass number and waits on `grahan()`; `probe.py` reads **VmRSS** and
**VmSize** from `/proc/<pid>/status`, then lets it go on. Each pass makes a `kosh` and pushes 4,097 elements, so its
region exists and the pages holding the elements are written. Baseline at point 0: **12-20 KB resident, 232 KB of
address space.** Two runs each, identical to a few KB; `evidence-r170/results.txt`, programs beside it.

| after pass | VmSize (address space) | VmRSS (resident) |
|---|---|---|
| 0 | 232 KB | 16 KB |
| 250 | 17,432,808 KB | 17,032 KB |
| 500 | 33,816,808 KB | 34,048 KB |
| **1,000** | **66,584,808 KB (63.5 GiB)** | **68,080 KB** |
| 20,000 (a longer run) | 1,311,768,808 KB (1.22 TiB) | 1,361,264 KB |

The same with and without a `mandapa` around the `kosh` (within 40 KB). **The program finishes and prints the right
sum at 1,000 and at 20,000 passes.** A 64-bit process has about 128 TiB of address space - two million such regions -
and real memory (68 KB a pass) would run out long before.

**Where it does fail: under an address-space limit.** With `ulimit -v 8388608` (8 GiB, as a container or a batch
system may set) the same loop stops **in pass 112**: `Sutram truti: kosh vardhayitum smritih na labdha - kosh yatha
asit tatha eva`, exit 1. **That is the failure you described; it needs a limit to appear.**
What Windows does at this point I have not run.

## WS4 - the 16 bytes a block adds

**They are not something the block allocates. They are a longer header on every `kosh` of the program.**

`src/sutram_compiler.asm:10640-10651`: in a program that declares any `kosh` inside a `mandapa`, every `kosh`
carries three more words before its length - `[-40]` the block's line, `[-32]` the address of the block's liveness
slot (0 for a `kosh` made outside any block), `[-24]` the generation - so that a `prakriya` given a `kosh` can tell
whether its block has ended. Descriptor 32 → 56 bytes; with one 8-byte element 40 → 64; the allocator rounds to 16,
so 48 → 64. **The 16 is 24 bytes of header less 8 of rounding that was already being paid.**

**Is it a cheaper defect to fix? No.** It is one allocation with the descriptor - the same leak, a third larger - and
the check reads the header of *every* `kosh` it is handed, in or out of a block, so a `kosh` outside a block cannot
simply go without it. Dropping it saves 16 of 64 bytes a pass and leaves the leak.

## Not done, and why

- **No change, no branch** - WS2's condition is false; the missing pieces are listed instead.
- **The "after" measurement** - there is no change to measure.
- **Windows** - the reserve and release calls are read, not run.
