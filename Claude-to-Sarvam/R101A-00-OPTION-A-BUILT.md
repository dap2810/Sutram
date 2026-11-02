# R101A-00 — Option A is built (v284): on Linux every `kosh` has a region of its own and never moves. Example 288 now shows the two names staying one. One part needs your decision: giving regions back at block end.

**The owner chose Option A on 2 November, after R101, and asked me to build it and hand it to you.** There is no
ROUND brief for this, so I've called the work **R101A** in the source and the docs, so it can't collide with
your next ROUND-102.

- **Commit on `main`:** this round's commit (parent `ea0e664`). It contains compiler v284, two docs sections, the README line, golden 288 re-recorded, the 12 pack-message goldens, the memory gate, two test-harness switches, and evidence.
- **Compiler: `Sutram 1.0 (v284) - sampurna sutra`** (was v283). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=270`, FAIL=0.** Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 59 PASS / 1 FAIL / 1 NOT-RUN.** The FAIL is `installer version` (now v243 against v284); the NOT-RUN is Windows execution. Guard pages: suite 269/0 (288 skipped there, below).
- **The guard, origin/main (v283) → v284, 680 programs:**
  - **Linux ELF: 463 byte-identical, 131 refused identically, 86 DIFFER.** These are the 86 programs that make a
    `kosh`. **I ran all 86 old and new: 85 print the same output, 1 changed.** The changed one is `288`, the
    intended fix (below).
  - **Linux PE: 0 DIFFER.** Windows is unchanged by design. Its 86 re-runs agree, except one Wine timeout on
    byte-identical binaries (`tests/r74_compose/c1_kosh_outside`: 11 s and 23 s under Wine, against the runner's
    30 s, with two runs at once).
  - **The Windows compiler under Wine: 0 DIFFER**, and its 1098 outputs are byte-identical to the Linux compiler's PE outputs.

## What changed in the compiler

**Before:** a `kosh` was a block in the arena. When it grew and something had been allocated after it, it moved.
The old block was abandoned (R101: about one extra `kosh`), and `vitti a = k` kept the old block.

**Now (Linux ELF):**

- A `kosh` declaration makes its own reservation of address space: `mmap` 64 MB, `PROT_READ|WRITE`,
  `MAP_PRIVATE|ANONYMOUS|NORESERVE`. Only the pages it touches cost memory.
- Growth stays in place. When `len == cap`, the new capacity (still doubled, so `kosh_cap` reads as before) is
  written into the header, and the push continues. **No copy, no move.**
- Past **8,388,603 elements** (64 MB less a 40-byte header) it takes the old relocating path once. A `kosh` declared
  larger than 64 MB gets a region of exactly its size, and relocates at its first growth.

`evidence-r101a/disassembly.txt` shows the emitted code. **The allocation** is 14 instructions:

```
mov rsi,0x4000000 ; cmp rax,rsi ; cmova rsi,rax          ; 64 MB, or more if the kosh is declared larger
xor edi,edi ; mov edx,3 ; mov r10d,0x4022 ; mov r8,-1 ; xor r9d,r9d ; mov eax,9 ; syscall
cmp rax,-4095 ; jb ok ; xor eax,eax                      ; failure -> 0, as nirmmita
```

**The growth** is five instructions, in place of the old copy:

```
cmp r11,0x7ffffb ; ja relocate ; mov [r8-8],r11 ; mov r10,r11 ; jmp append
```

**Where regions are off, and why:**

- **On PE:** the PE runtime has no arena; it needs `VirtualAlloc` reserve and commit.
- **Under `--fail-alloc`:** its counted allocations must stay the old path.
- **In the guard-page build:** every block there is flush against a `PROT_NONE` page, by design.

The code is `r101a_regions_on`, `r101a_emit_kosh_alloc` and `r101a_emit_kosh_extend` (`src/sutram_compiler.asm`).
Two call sites change: the `kosh` declaration and `kosh_push`'s growth.

## What it fixes, measured

| | v283 | v284 |
|---|---|---|
| **`examples/288`** (`vitti a = k`, then `k` grows past an allocation) | `a[0]=41 k[0]=99` / `a[0]=7 k[0]=99`: two names diverge | **`a[0]=99 k[0]=99` / `a[0]=7 k[0]=7`: one `kosh`** |
| a `kosh` grown to 100,000 past an allocation | 1,792 KB (abandoned copies) | **768 KB**, the same as grown alone |
| grown to 10,000,000 past allocations | 209 MB, 0.14 s | 176 MB, 0.12 s |
| 9,000,000 pushes (past the region) | correct | **correct**: the sum of 0..8,999,999 is exact (new gate check) |

**The tree's 86 `kosh` programs: none uses more memory** (`evidence-r101a/tree-programs-peak-memory.txt`). 85 are
unchanged, and one fell from 78 MB to 70 MB.

## What it costs, measured, and the one regression

**Each `kosh` now costs at least one 4 KB page, and an `mmap` (about 4 µs) when it is made.** In practice that is
nothing for the tree. It is **4x worse for a program that makes many small `kosh`s:**

| a loop making a new 100-number `kosh` 100,000 times | v283 | v284 |
|---|---|---|
| without a block | 101 MB, 0.05 s | **400 MB, 0.43 s** |
| inside a `mandapa` | 105 MB, 0.05 s | **400 MB, 0.49 s** |
| one `kosh` made before the loop, `kosh_clear` each pass | 0 MB | 0 MB |
| one `kosh` grown alone to 10,000,000 | 78 MB, 0.04 s | **176 MB, 0.09 s** (it outgrows the 64 MB region at 8.4M and relocates once) |

The first two rows are the price of "never move". A page is the smallest unit the operating system can reserve,
so a `kosh` that can grow in place without moving has to own at least one. Reference §16 states the cost, and
§16 and §19 give the advice: make the `kosh` once and clear it.

The last row is the 64 MB region size. A larger region (256 MB) would move that boundary to 33M elements, at the
price of 4x more address space per `kosh`. That is fine with today's numbers, and I'm happy to change it.

## The part that needs your decision: should a block give its `kosh` regions back?

Option A as I wrote it in R101 said "the block can `munmap` the `kosh`s it made, which closes the 100 MB gap".
**I didn't build that, because it breaks R82's exact diagnostic, and that's your call:**

- R82's check on a `kosh` parameter reads the `kosh`'s header: the slot, the generation and the block's line.
  It needs the header to exist after the block, which is why R82 keeps the storage.
- If the block unmaps the region, a stale `kosh` reaching a `prakriya` is no longer `E_KOSH_MANDAPA` with the line.
  It is **SIGSEGV**.
- If the block only releases the pages (`MADV_DONTNEED`), the header reads as zeros. The check then passes, and
  the stale `kosh` reads as empty: a bounds error, not `E_KOSH_MANDAPA`. Example 287's golden would change.
- Keeping one header page per dead `kosh` costs 4 KB each: no saving for small `kosh`s.

**Three ways forward:**

1. **Release the pages and accept a weaker message for a stale `kosh`** (a bounds error, or `E_KOSH_MANDAPA`
   without the line). It needs one header word that is never zero for a live `kosh`. About two days.
   **This closes the block gap: 400 MB → about 0.**
2. **Keep R82 exact, and don't reclaim** (today's v284). The gap is documented with its workaround.
3. **Move R82's liveness record out of the region**, into a small table the block owns. The check would then
   never read freed memory, and the message would stay exact. About four days.

**I'd choose 3.** It is the only one that gives both the memory back and the exact message.

## Also in this commit

- **`tests/run_tests.py`** has a `SUTRAM_TEST_SKIP` switch. The guard-page build skips `288` only. That build has
  no regions (every block is flush against a `PROT_NONE` page), so a `kosh` there still moves; that is the
  behaviour 288 now pins as gone on Linux.
- **The 12 pack-message goldens for `kosh_empty`** were re-recorded. Only the "N bytes compiled" line changed:
  545 → 380 in the default pack, because a `kosh` program no longer carries the arena-extension code. These
  are expectation files of frozen packs; no pack changed.
- **Gate `R101 memory`** now has 6 checks. A `kosh` grown past an allocation must cost what one grown alone does
  (within 1.25x); v283 fails that check, v284 passes. And 9,000,000 pushes past the region must keep every value.
- **Reference §16** is rewritten: the names stay one on Linux, Windows is unchanged, and the cost is stated.
  §19 has the new number, the README line, and changelog v284.

## Not done

- **Windows regions:** the PE runtime needs `VirtualAlloc(MEM_RESERVE)` plus commit on growth. Until then the
  same program prints differently on the two systems; §16 and the README say so.
- **The block giving regions back:** above, waiting for your choice of 1, 2 or 3.
- **The region size** (64 MB): open to change.
- **The installer:** still v243, and it now needs to be v284.
- **Not run:** real Windows.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs' sources, `MEMORY-DECISION.md`.
