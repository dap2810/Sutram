# R61-00 — The `kshetra` block: two flaws that must be fixed, one that must be accepted, and the prices

- **Base:** `main` at `2553ee4`, compiler v261. **No source change.** Everything measured is in `evidence-r61/`,
  `evidence-r59/` and `evidence-r60/`; everything priced is an estimate, calibrated on this compiler's own code.
- **Verdict first: the block is the right carrier for a lifetime. The design as written is unsafe in two places that
  are fixable, and incomplete in one place that is not. With the two fixes and the honest limit, I would build it.**

## 1. Is the scope rule complete? No. The fourth case is the region itself, not a pointer.

**The flaw: the region is dynamic, the rule is lexical.** As designed, there is one bump pointer. The block takes the
mark, and *every* `nirmmita` executed before the block ends allocates from it, including the ones inside library
functions called from the block. The rule, by contrast, sees only the block's own text.

**Case 4a — a constructor called inside the block:**
```
mukhya()
    vitti m = 0
    kshetra
        m = suchi_srij(8)        # passes the rule: the right-hand side is a call, not nirmmita
    suchi_yuj(m, 1)              # m points into rewound memory
```
`suchi_srij` allocates with `nirmmita` inside its own body and returns the result. **13 of the library's 25
allocating functions hand their allocation to the caller** (7 return it, 6 store it through an out-parameter;
`evidence-r60/library-escapes.txt`), and 36 programs in the tree call them. The rule cannot see any of them.

**Case 4b — an outer `kosh` grows inside the block:**
```
mukhya()
    kosh k[1]
    kshetra
        kosh_push(k, 7)          # k is full: growth allocates the new buffer FROM THE REGION
        kosh_push(k, 8)
    likha(k[0])                  # k's buffer was rewound
```
No pointer is assigned anywhere. The escape is a container that lives outside and grows inside.

**The fix for both: make the region lexical too.** Two bump pointers, two ranges:
- a `nirmmita` **emitted while the compiler is inside a `kshetra` block** uses the region bump;
- every other `nirmmita` — outside blocks, inside library bodies, and `kosh` growth of a `kosh` declared outside the
  block — uses the permanent bump, which is never rewound.

Since `yoj` splices library text into the source, "inside the block" is a compile-time flag at
`emit_nirmmita_from_rax` (`src/sutram_compiler.asm:19889`): is `kshetra_depth > 0` right now? **About 10 lines, at
one place, and the guard cannot see it.** For 4b, the growth site (`:15799`) compares the `kosh`'s variable index
with the block's watermark (below) and picks the bump: **~10 lines.**

**What lexical costs:** scratch allocated *inside* a library function called from the block is no longer reclaimed
by the block. Muse's 313 sites are mostly that scratch. **I think that is the right trade:** the library is where the
programmer cannot see the allocation, so it is where a silent rewind does the most damage. Reclaiming library scratch
is a later round, done inside the library with blocks of its own.

**After the fix, what still escapes:**

| Route | Caught? |
|---|---|
| `outer = p` | yes: the rule |
| `outer = p + 8`, `outer = p * 1` | **only if the kind follows arithmetic.** Today's slice rule does not: `vitti t = s + 0; nivartanam t` compiles (`evidence-r61/slice-rule-probes.txt`). Make the new kind propagate through `AST_BINOP`. ~15 lines. |
| `nivartanam p`, `prasar` out of the block | yes, same check at the return sites |
| `outer_mala[i] = p`, `outer.field = p`, `likh8(anything, p)`, `kosh_push(anything, p)` | yes, if every store of a region-kind value through memory is refused. **Today's slice rule misses all four.** |
| `likh8(cell_inside_block, p)` then `outer = pad8(cell_inside_block)` | **no. A pointer stored into memory and read back is an integer.** |
| `f(p)` where `f` keeps its argument | **no.** Refusing region pointers as arguments would also refuse `varna_maap(buf)`, which is the whole point of a scratch buffer. |

**So the rule is a lint with two known holes, exactly like the slice rule the language already ships.** The question
is what happens when a hole is hit, and that is point 7.

## 2. Nesting, interleaving, and `nivartanam` inside the block

- **Nested blocks:** the inner mark is above the outer mark; inner rewinds first. Correct, nothing to do.
- **Inner allocates, outer's pointer used inside:** safe; the outer object outlives the inner block.
- **Inner pointer assigned to a variable of the outer block:** the rule must refuse it. The variable is "declared
  outside *that* block", and it would dangle from the inner rewind until the outer rewind. The rule as worded
  already covers it; the implementation must test against the innermost enclosing block's watermark, not the
  function's.
- **`nivartanam` inside the block:** yes it can contain one, and as designed the rewind is skipped. **The same is
  true of `krama`, `agrim` and `prasar`** — I count four early exits in the generator: `.gs_return` (`:14440`),
  `.gs_break` (`:14063`), `.gs_continue` (`:14085`) and `r25_gen_prasar` (`src/r25_phal.inc:178`), which emits an
  inline `lea rsp,[rbp-8]; pop; pop; ret`. `sthagita` is process exit and needs nothing.
  - **The leak is bounded, not unbounded:** the skipped memory is reclaimed by the next enclosing rewind, or never
    if there is none. In a loop that `agrim`s out of a block every iteration, it is a leak per iteration — the exact
    case the block exists for.
  - **The fix:** each exit rewinds to the mark of the *outermost* block it leaves. For `krama`/`agrim` that is the
    outermost block inside the current loop; for `nivartanam`/`prasar` the outermost block in the function. Inner
    marks are above it, so one store covers them all. **~12 lines per site, 4 sites, emitted only when
    `kshetra_depth > 0` — so the guard sees nothing for programs without a block.**
  - **Where the mark lives matters:** not in a global (a recursive function would overwrite its own caller's mark;
    the result rewinds too little, never too much, so it leaks rather than corrupts, but it is wrong). **A hidden
    local, `alloc_var` with a name a program cannot write, as R46 did with `0shodhan_vakya`.** Recursion-safe, and
    the early exits read it like any variable.

## 3. What the block costs in emitted code

| | bytes emitted | cycles |
|---|---|---|
| entry: load bump → hidden local | ~10 | ~2 |
| exit: hidden local → bump | ~10 | ~2 |
| each early exit crossing a block | ~10 | ~2 |
| **`nirmmita` inside the block:** load, add, align, compare, store, return | ~40, in place of today's 45 | **~55 measured** for a 64 B block with its first touch (`evidence-r59`) |
| **zeroing the block** (below) | ~12 | **~10–15 for 64 B**: writing all eight qwords measured 55–75 cycles against 50–62 for one (`evidence-r61/zeroing-cost.txt`) |

**Zeroing is not optional, and it is the first thing the "two instructions" claim leaves out.** Rewinding reuses
memory, so the second allocation at an address is dirty. `nirmmita` memory has always been zero, and I measured what
depends on that: **with unzeroed allocation, 4 of the 226 library proofs fail** (two wrong answers, two hangs;
`evidence-r60/unzeroed-memory-proofs.txt`). A `kshetra` `nirmmita` must therefore `rep stosb` its block, or the
rewind must clear the used extent. Per allocation is simpler and, for small blocks, in the noise.

## 4. The range: size, and what happens when it runs out

**With rewind, the region arena holds the peak live set, not the cumulative total.** My 16 TiB figure was for a
design that never reused addresses; it is unnecessary here. A few hundred MiB is plenty for a region arena.

**Two different exhaustion questions, and they have different right answers:**

1. **Layer 1, the permanent arena that every existing `nirmmita` moves into.** Existing programs allocate more than
   any fixed arena — the 1,000,000 × 64 B program takes 4 GB today and works. **So Layer 1 must fall back to today's
   `mmap` when its range is exhausted, or constraint 3 is broken.** Fallback is the predictable choice *for
   correctness*: the program's behaviour is unchanged, only its speed varies.
2. **The `kshetra` arena.** A region that outgrows its arena is a genuine out-of-memory inside a bounded scope.
   Here I would **return 0, which is `nirmmita`'s failure contract today**, not fall back: a fallback allocation
   would not be rewound, so the block's one promise — "this is gone at the `}`" — would silently stop holding.
   Returning 0 keeps the contract the programmer already knows.

**On `.bss` for the reservation:** measured in R60, an executable whose `.bss` is 8 GiB or more does not start on
this 7 GB machine — `execve` fails with ENOMEM and the kernel kills it before `_start`, with no message. Under
`ulimit -v 4194304` the same happens at 8 GiB. So the `.bss` arena must stay modest (hundreds of MiB), which is fine
for regions and is one more reason Layer 1 needs the `mmap` fallback.

## 5. Windows — NOT RUN, read from the adapter and from the Windows API's documented contract

- **The analogue is right: `VirtualAlloc(MEM_RESERVE)` reserves address space with no commit charge, then
  `VirtualAlloc(MEM_COMMIT)` on parts of it.** `MEM_RESERVE|MEM_COMMIT` of the whole range, which is what the
  adapter does today for every call (`win/winrt_blob.asm:143-151`), would charge the whole arena against the commit
  limit (RAM plus pagefile) and fail for a large one.
- **The behaviour under memory pressure differs in one way that matters for the fast path.** On Linux, a
  `MAP_NORESERVE` page is committed lazily at first touch. On Windows, touching reserved-but-uncommitted memory is an
  access violation. **So the Windows bump allocator needs a commit frontier:** `cmp bump, committed_end`, and a slow
  path that commits the next chunk (say 1 MiB). The compare can be the same one the Linux path already needs
  (`cmp bump, limit`), so the fast path stays identical; only the slow path differs per OS.
- **Where failure shows:** Windows refuses at `MEM_COMMIT` time, returning NULL, which maps cleanly to `nirmmita`'s 0.
  Linux overcommit fails at first touch, by the OOM killer. Windows is the more predictable of the two here.
- **A large `.bss` in a PE** is committed at load, so I would expect the same "will not start" failure as Linux shows
  at 8 GiB, at a lower threshold set by the pagefile. **Not verified.**
- **Cost:** adapter cases for reserve, commit, and `VirtualFree`/`MEM_RESET` if the rewind ever returns pages: ~40
  lines in `win/winrt_blob.asm`, plus imports in `win/pe_imports.inc`. **Every `.exe` changes**, because the import
  table is in all of them. Linux first.

## 6. Is there a different structural carrier?

I looked at the four the language has.
- **The loop body:** the block inside the loop already is this. Making every loop body a region would be automatic
  release, which ChatGPT ruled out.
- **The module:** too coarse; it is the program's lifetime.
- **The `rachana` struct:** a lifetime per object is ownership. Option C, not v1.0.
- **The function call:** the only real alternative. Muse's 313 sites argue for it, and my R60 found the reason it
  cannot be the default: 13 of 25 allocating library functions return their allocation. **But as an opt-in spelling
  it is sound and cheap:** `kshetra prakriya f(...)` would mean "this function's body is one block", with the rule
  applied at its `nivartanam`. Same mechanism, same checker, one more parse path (~20 lines). It would let a
  programmer mark the library's scratch-heavy helpers one by one later. **I would ship the block first and add this
  spelling if the library wants it.**

**So no: the block is the right carrier, because it is the one that already has a watermark.** `parse_block`
pushes `r4_seen_count` on entry and `r7_close_block` pops it (`:8718`, `:7818`): the parser already knows which
names a block declared. The scope rule is that mechanism, read one more time.

## 7. Is the whole idea wrong? No — but reuse without fail-stop is.

The design rewinds and *reuses*. That makes every hole in point 1 a **silent read of another object's bytes**,
the worst failure a language can offer. My R60 design avoided it by never reusing addresses and protecting rewound
pages, at the price of two syscalls per close; you chose reuse for speed, and the block makes that defensible.

**The improvement I would insist on: the two behaviours are a build flag, not a choice.**
- **Release build:** rewind and reuse, as designed.
- **`--debug` build (the flag exists, `src/r45_debug.inc`):** the region bump never rewinds, and at each block exit
  the block's pages are `mprotect`ed `PROT_NONE`. **A pointer that escaped through any hole faults at its first use,
  at a line the debugger already knows.** ~40 lines, all inside the debug path, invisible to the guard.

With that, the lint catches what it can at compile time, and what it misses is a crash in the debug build rather
than corruption in the release build. **That is the design I would build.**

## The two deciding tests

1. **1,000,000 × 64 B inside a `kshetra` in a loop.** It will pass, with two conditions. If the block is inside
   the loop and allocates per iteration, the live set is 64 bytes and memory does not grow — this is what the design
   promises, and nothing I found stops it. If all million allocations are inside one block, the live set is 64 MB,
   so the arena must be at least that or the allocation returns 0 by point 4. **And the measured baseline is right:
   4,000,000 KB today** (`evidence-r59/ws1-rss.txt`).
2. **A `kshetra` pointer assigned to an outer variable must fail to compile with a line number.** It will fail to
   compile. **The line number is the part that needs work:** the slice rule's refusal prints no line
   (`Sutram Error: vibhag prakriyayah na pratyarpaniyah`, verified), because it goes through `capacity_fail`. The
   new check must take the `r48` path that prints `pankti N`. The statement's source position is already recorded
   for the debugger (`r45_map`, `src/r45_debug.inc:73`), so it is plumbing, ~20 lines.

**A third test I would add:** case 4b above, an outer `kosh` grown inside a block, then read after it. Under the
design as written it reads rewound memory; under the lexical fix it is correct. It is the test that distinguishes
the two.

## Your lens: lines, locations, and what the guard cannot see

**Is the scope check one pass over the AST? Yes, and it is not a new pass.** `gen_stmt` already walks every
statement once; `r23_check_return` does its slice check inside that walk. The new check does the same, and needs
two things the compiler already has:
- **a per-function kind list** — `r23_slice_vars` is the template (`src/r23_capabilities.inc:415-470`, ~60 lines
  for mark, test, and expression test);
- **"declared outside this block"** — the variable table is append-only per function, so a variable's index
  compared with the index recorded at block entry is one compare.

| Part | Where | Lines | Touches an existing path? |
|---|---|---|---|
| keyword, Latin + Devanagari, and `KW_` constant | `kw_table` `:473`, `lang/sanskrit.lang` | ~8 | table only |
| parse `kshetra` + body, AST node | beside `.ps_if` `:9053`, reusing the braces-optional body path | ~30 | no |
| generate: hidden local, mark, body, rewind; depth stack | beside `.gs_assign` `:13074` | ~60 | no |
| rewind at the 4 early exits | `:14440`, `:14063`, `:14085`, `r25_phal.inc:178` | ~50 | **yes, but emits only when inside a block** |
| region bump path in `emit_nirmmita_from_rax`, with zeroing; permanent-bump path for Layer 1 with `mmap` fallback | `:19889` | ~180 | **Layer 1 changes the 248 allocating guard programs' bytes; the region path emits only inside a block** |
| outer-`kosh` growth picks the permanent bump | `:15799` | ~10 | only inside a block |
| escape check: kind list, propagation through assign and `BINOP`, refusal at assign-to-outer, store-through-memory, `likh8`, `kosh_push`, return, `prasar` | new `src/r61_kshetra.inc`, hooks beside `r23_mark_slice_decl` `:12822` and `:20885` | ~200 | hooks are no-ops when no block is open |
| error with line number | the `r48` message path | ~20 | no |
| `--debug`: no rewind, `mprotect` on exit | `src/r45_debug.inc` | ~40 | debug builds only |
| Windows adapter and imports | `win/` | ~40 | **every `.exe`** |
| **total** | | **~640** | |

**Guard-invisible:** everything except Layer 1 (by design: it changes how 248 programs allocate, and their output
must not change) and Windows (every `.exe`). **A program with no `kshetra` block compiles to the same bytes as today
on Linux**, provided every hook is gated on `kshetra_depth > 0` — that gate is the thing to test first, with the guard.

**Order:** the two fixes of point 1 are decided before a line is written, because they change what the bump pointer
is. Then the block with release as a plain rewind, the guard at 0 DIFFER for the 577, then the checker, then the
debug fail-stop, then Windows.
