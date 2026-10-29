# ROUND-61 — the `kshetra` block, critiqued

Base: origin/main `2553ee43`, CHANGELOG v414, compiler v261.
Read first: `docs/MEMORY-UNIQUE-HYBRID.md` (the synthesis),
`ChatGPT-to-Sarvam/ROUND-133-MEMORY-DESIGN.md` (ChatGPT's alias
argument and Track A/B), `Claude-to-Sarvam/evidence-r60/` (page
costs, `.bss` limits, library escapes, unzeroed-memory proofs).

Measurement only, plus design analysis. No tree changes. The lens
numbers below were measured on current main; the escape
classification they extend is ROUND-59's (322 executable sites:
(a) 313 / (b) 6 / (c) 3).

## Headline

The block is the right shape and the wrong sufficiency claim.
The loop pattern is real, the syntax is well chosen, and the
direct scope check works for the case in the brief. But the
one-sentence scope rule is **not** complete, and the incompleteness
is not marginal: it misses exactly the two mechanisms by which
real programs move pointers — **through containers** and
**through callees** — and both are visible in this tree's own
library. The block is shippable with five fixes (§8); as stated,
it is unsound for ordinary code. The most valuable single
sentence of this report is §1.2: **the rule checks where the
`nirmmita` text is, but lifetime is about where the allocation
happens, and those differ whenever a callee allocates.**

## 1. Is the scope rule COMPLETE? No. Two more escapes, and one of them is structural

Sarvam's three holes are real and I confirm all three from the
tree. But there are two more, and the second one defeats the
rule's premise rather than just extending it.

### 1.1 The three confirmed holes (no new argument needed)

- **Passed to a storing function.** Confirmed: `nighantu_khip`
  stores its value argument into map slots; `suchi_khip` /
  `avali_pravesh` / `kosh_push` store their value argument into
  the container. Passing a block pointer as a *value* to any of
  these retains it past the block. (Passing it as a *buffer* the
  callee writes through does not retain it — the distinction
  matters for the lens numbers in §7.)
- **Stored through an outer pointer.** Confirmed as a pattern:
  `*outer_ptr = kshetra_ptr` writes through indirection; a
  syntactic check on the assignment target's declared scope does
  not see the outer variable at all.
- **Returned from the enclosing `prakriya`.** Confirmed: any
  `nivartanam kshetra_ptr` escapes, and the rule as stated does
  not mention returns.

### 1.2 Fourth escape: a locally-built container that is returned (or stored)

No assignment to an outer variable happens, and no pointer is
directly returned — yet the pointer escapes:

```
prakriya banav() {
    kshetra
        vitti l = nirmmita(3 * 8)      # header, block-local
        vitti d = nirmmita(80)         # data, block-local
        l[2] = d                       # store into a LOCAL record
        nivartanam l                   # return the record, not the pointer
}
```

The rule checks assignments to variables declared outside the
block. `l` is declared inside. The store `l[2] = d` passes. The
return `nivartanam l` passes — the rule does not mention returns
of containers. The caller now holds a list whose backing store
was rewound. This is not hypothetical: it is exactly the
`suchi_srij` pattern (`lib/suchi.smlib:46-62`: header returned,
data stored into `l[2]` of the returned header), transplanted
into a block. Every constructor in the library wraps a pointer in
a record this way, so any block-local use of the constructor
pattern escapes the rule. The fix is not a second sentence about
variables — it is a **taint** rule: a container that holds a
block pointer is itself block-tainted, and a tainted value may
not escape either. Once the rule is taint, it is no longer "one
scope check over the AST"; it is the escape analysis, applied to
values rather than variables.

### 1.3 Fifth escape, and the structural one: a callee allocates, the block pays

```
mukhya()
    vitti l = 0
    kshetra
        l = suchi_srij(10)     # NO rule violation: no block pointer
                               # is assigned anywhere in this text
    likha(l[0])                # dangling (see below)
```

The `nirmmita` text is inside `suchi_srij`, not inside the
block, so the syntactic rule sees nothing to forbid: the
assignment target `l` is outer, but the assigned *value* is a
call result, not a block pointer as far as the block's text is
concerned. Dynamically, though, `srij` executed *during* the
block, and its allocations land above the block's mark (if the
bump is shared, which the mark/rewind sketch implies) — so the
block's rewind frees the list the caller just stored. Under the
alternative implementation (per-function bumps), the same code
dangles *earlier*: `srij`'s own frame rewind frees the list on
return, before the block even ends. Either implementation
dangles; the rule catches neither, because the rule is syntactic
and allocation is dynamic.

This is the deepest hole because it is not a missing case in the
rule — it is a category the rule cannot express. A syntactic
scope check can only see allocations whose `nirmmita` text is
inside the block. Every library constructor allocates elsewhere
and is *called* from inside blocks. Since the standard library's
constructors are exactly the functions every program calls, a
block that contains any constructor call is suspect until the
callee rule exists. The fix options are: (a) callees allocate
from a different arena than any open block (then blocks never
reclaim callee scratch — the block's benefit shrinks to direct
`nirmmita` only); (b) interprocedural analysis of which callees
allocate escaping values (the analysis again); or (c) the
dual-arena routing of ROUND-60, where constructors route to the
heap arena by analysis and blocks never touch them. Note that
(a) is a semantic fork the programmer must know about ("blocks
reclaim direct allocations but not helper allocations"), which
is exactly the kind of invisible behavior the block was designed
to avoid.

### 1.4 A sixth, smaller hole: derived pointers

`vitti q = kshetra_ptr + 8; nivartanam q` — `q` is a different
variable holding a pointer derived from the block pointer. A
scope rule tracking the original variable misses it; a taint rule
catches it (taint flows through arithmetic). I list it separately
because it shows the fix direction: whatever the rule becomes,
it must track **values**, not **variables**. Pointer arithmetic
is common in this tree (buffers are indexed and offset
throughout `lib/`), so this is not exotic.

### 1.5 What the rule DOES catch, fairly

The direct case in the brief (`kept = nirmmita(64)` inside a
block, `kept` declared outside) is caught, as are assignments
from a block to any outer local, and uses of block-declared
variables after the block (ordinary block scoping, which the
language already has). The rule is a good *first* check. It is
not a safety property.

## 2. Nested and interleaved blocks; `nivartanam` inside a block

### 2.1 Nesting works in the safe direction, and the brief's worry is backwards

Inner rewinds first: correct with a LIFO mark stack, since
inner allocations sit above the inner mark. The brief asks about
"the inner allocates and the outer's pointer is used inside" —
that direction is **safe**: an outer pointer used inside an inner
block points below the inner mark, so the inner rewind cannot
free it. The dangerous direction is the reverse (inner pointer
used in outer scope), which ordinary variable scoping catches
*unless* the pointer is smuggled via an outer variable (caught
by the rule), a container (§1.2), or a callee (§1.3).

True interleaving (two blocks' lifetimes overlapping without
nesting) cannot arise lexically — blocks nest like `yadi` /
`chakra`, and Sutram has no goto across blocks. Dynamic
interleaving arises only through calls, which is §1.3 again.
Two *sequential* blocks are safe: the first block's rewind
completes before the second block's mark, so the second reuses
the first's memory — except for smuggled pointers, which are
§1's holes, not a nesting problem.

### 2.2 `nivartanam` inside a block: the rewind must run on every exit edge

If the compiler emits the rewind only at the block's lexical
end, a `nivartanam` inside skips it, and the block's memory
leaks until the enclosing block (or function) ends. That is the
brief's note, and it understates the problem in two ways:

- **The leak compounds in loops.** A `nivartanam` inside a
  block inside a loop is a function exit, so it also skips every
  iteration's rewind — but that is a single leak at function
  exit, not per iteration. The per-iteration leak is the
  `krama` / `agrim` case (§3), not the return case.
- **A tainted return must be an error, not a leak.** If the
  return value contains a block pointer (container case, §1.2),
  rewinding before returning frees memory the caller now holds
  — dangling, not leaking. So the rule for returns is: compute
  the value, check it is untainted, rewind, then return. The
  rewind-before-return is correct for untainted values (the value
  is already computed); for tainted values the compiler must
  refuse. And a return must rewind **all** open blocks, not just
  the innermost: restoring to the outermost open mark frees
  everything above it in one restore, so the cost is one restore
  per return edge, not one per block — but the compiler must
  track the block stack at every exit, which is a real (if
  small) compiler change, not "two instructions emitted once".

## 3. Cost in emitted code; `krama` and `agrim`

### 3.1 The instruction count, corrected

- Entry: **one store** (mark = current bump, pushed to the mark
  stack or a frame slot).
- Each exit edge: **one restore** (bump = mark). Exit edges are:
  fall-through, each `nivartanam`, each `krama` that exits the
  block, each `agrim` that restarts an enclosing loop from inside
  the block.
- So a block costs 1 store + (number of exit edges) restores.
  The common case (straight-line block, one exit) is 2
  instructions, as claimed. A block with early returns and loop
  jumps costs more — still a handful of instructions, but the
  claim "two instructions, emitted once" is true only for the
  simplest shape. The compiler change is tracking the mark stack
  at every jump target, which is straightforward but not free.

### 3.2 `krama` / `agrim` MUST rewind, and the continue case is load-bearing

- `krama` (break) out of a loop containing a block must restore
  to the mark of the outermost block the jump exits (one restore
  suffices, since marks nest). If it does not rewind, the block's
  memory leaks until the enclosing block/function ends.
- `agrim` (continue) from inside a block must rewind the block.
  **This is the case that decides whether the loop pattern works
  at all.** The loop pattern's whole point is per-iteration
  release. If `agrim` skips the rewind, each continued iteration
  leaves its block's memory live, and the loop accumulates
  exactly the leak the pattern exists to prevent. A loop whose
  iterations mostly `agrim` would grow without bound — the web
  server leaks again, through the edge case. So the rewind on
  `agrim` is not an optimization or an edge case; it is the
  mechanism. Any implementation must test it explicitly (a loop
  with `agrim` inside a block, asserting bounded memory).
- A `krama` / `agrim` that stays *inside* the block (jumping
  within it, or out of an inner loop but not out of the block)
  needs no rewind. The compiler must distinguish these by the
  jump's target depth, which it knows statically.

### 3.3 Reuse semantics: zeroing is now per-iteration, not theoretical

Claude's unzeroed-memory experiment (`evidence-r60/
unzeroed-memory-proofs.txt`) is directly relevant: with
`nirmmita` returning 0xAA-filled memory, 4 of 226 library proofs
break (2 wrong answers, 2 hangs). A block *guarantees* reuse:
every iteration reuses the previous iteration's memory. So a
program that reads a block allocation before writing it will
read the previous iteration's data, deterministically. ChatGPT's
rule (R133) stands: either define block allocations as
uninitialized (callers must write before read — a new
correctness obligation on every block user) or zero each
allocation at O(size) cost. My ROUND-60 position stands too:
zero by default. The block makes the stale-data case the common
case, so "zeroing on reuse is a choice" is no longer tenable —
for blocks, it is the default or the design is incorrect for
existing programming habits (4 proofs' worth of them, measured).

## 4. Range size, 16 TiB, and exhaustion

### 4.1 16 TiB cannot be a `.bss` reservation — Claude measured the failure

Claude's `bss-limits.txt` is decisive and it corrects the
synthesis doc's Layer 1: on a 7 GB machine with the default
overcommit heuristic, `.bss` of 8 GB or more **fails at execve**
(ENOMEM, SIGSEGV before `_start`), even touching only byte 0.
Under `ulimit -v 4 GiB`, 8 GB fails too. The loader's reservation
*is* accounted, so link-time `.bss` is not a way to reserve more
than the machine can account for. By contrast, Claude's
`noreserve.txt` shows a runtime `mmap(MAP_NORESERVE)` of 16 TiB
succeeding (exit 0, RSS 392 KB for touching first and last
byte). So: **large ranges must be reserved at runtime with
`MAP_NORESERVE`, not at link time in `.bss`.** The synthesis
doc's "fallback to `mmap` if the reservation fails" is therefore
not an edge case — for any reservation above ~available RAM, it
is the *only* path, and the design should say so and use it
primarily. Small reservations (Claude showed 64 MB and 1 GB
`.bss` working) can stay in `.bss`; the boundary must be a
build-time decision, not a hope.

### 4.2 A 16 TiB reservation does not give clean exhaustion on Linux

With `MAP_NORESERVE`, the kernel does not guarantee backing.
Touching a page when RAM + swap are exhausted delivers SIGSEGV
at fault time, in arbitrary code — not a clean error. The bounds
check (`cmp` before the bump) only helps if the checked end is
below what the machine can back. A 16 TiB arena whose check
allows bumps to 16 TiB will SIGSEGV at ~RAM + swap, long before
the check fires. So "reserve huge, check at the end" does not
deliver the promised clean exhaustion on Linux. Two honest
options: (a) a modest arena size (at or below expected RAM), so
exhaustion hits the check first — the check then genuinely is
the limit; or (b) explicit commit (chunked reservation + commit,
as on Windows, §5), where commit failure is a clean allocator
error. What does not work is huge + NORESERVE + check and a
claim of clean exhaustion. The reservation size and the checked
limit should be distinguished in the design: reserve address
space generously, but set the checked limit to something the
machine can back, or commit explicitly.

### 4.3 Exhaustion: clean error, not `mmap` fallback — and the reason is semantic, not aesthetic

Fallback to `mmap` on exhaustion is wrong for this language
because it forks the lifetime semantics mid-program: a block
that falls back survives the rewind (it is a separate mapping,
not arena memory), while its siblings are freed. Identical
source, different lifetime, depending on load — that breaks the
"the syntax says the lifetime" promise that is the design's
whole point, and it breaks it silently (the programmer cannot
tell from the source which blocks fell back). It also changes
the cost model mid-program (sudden 1,000x slowdown for later
allocations). If a fallback is ever wanted, it must be an
explicit build mode (`-arena=fallback`), documented as changing
the lifetime semantics, not a silent runtime switch. The default
must be a clean abort naming the arena and the flag to raise it.
Note this is consistent with the language having no exceptions:
exhaustion is death, but it should be a *diagnosed* death
(message + distinct exit code), which is strictly better than
today's silent 0 followed by a dereference crash.

### 4.4 Portability notes on the 16 TiB number

- `ulimit -v` counts reserved address space: under a virtual
  memory limit (common in containers and sandboxes), a 16 TiB
  reservation fails at startup regardless of mechanism. The
  default must be modest; 16 TiB can only ever be a flag.
- 32-bit targets cannot express 16 TiB at all (4 GB address
  space). The Windows Win32 target (§5) needs a small default
  and a validation that the flag fits the target.
- Multiple arenas multiply the reservation: frame arena + heap
  arena + block arena at 16 TiB each is 48 TiB of a 128 TiB user
  space — tolerable alone, but it constrains other large
  mappings and it is another reason the default should be small.

## 5. Windows: `MEM_RESERVE` without `MEM_COMMIT` is the right analogue, with two behavioral differences

Yes, it is the closest analogue, and it is usable — but it is
not identical, and the differences cut in Windows' favor on
exhaustion and against it on syscall count:

- **Commit is explicit.** Touching a reserved-but-uncommitted
  page is an access violation, not an auto-commit. So the
  allocator must `VirtualAlloc(MEM_COMMIT)` the pages it bumps
  into, in chunks (64 KB granularity; commit e.g. 1 MB at a
  time as the bump advances). The cost is amortized — one
  syscall per chunk, not per allocation — but the "zero
  syscalls ever" claim does not survive to Windows. The honest
  Windows claim is "zero syscalls per allocation, one per
  chunk".
- **Commit failure is a clean allocator error.** If the pagefile
  is full, `MEM_COMMIT` returns NULL *at commit time, inside the
  allocator*, where the error path lives. That is strictly
  better than Linux `MAP_NORESERVE`, where the failure appears
  later as a fault-time SIGSEGV (§4.2). So Windows gives the
  clean exhaustion Linux NORESERVE does not — provided the
  allocator checks commit results, which must be specified.
- **Under memory pressure**, committed pages are pagefile-backed
  and can be paged out (slow, not fatal); reserved-but-uncommitted
  pages cost nothing. The design degrades gracefully: it fails
  cleanly at commit time rather than being killed.
- **The `.bss` question is separate and still open.** PE
  uninitialized sections have VirtualSize without raw data, so
  the file-size property should hold in principle — but the
  loader behavior for huge VirtualSize on Windows is unmeasured
  (ROUND-60's flag stands), and the Linux execve failure (§4.1)
  warns that loader reservations are not free. Measure a large
  PE `.bss` on Windows before relying on it there; the
  `MEM_RESERVE` path does not need that measurement.
- **32-bit Windows** (the wizard's Win32 target): 2 GB user
  space, 4 GB with `/LARGEADDRESSAWARE`. A large default
  reservation is impossible; the default must be small and the
  flag must be validated against the target.

## 6. A different structural answer — and the synthesis I would actually ship

### 6.1 The candidates, against the language's own values

- **The loop as the region (implicit per-iteration rewind).**
  This is Gemini's insight with no new syntax: allocations inside
  a loop body are released at each iteration's end. It directly
  addresses the long-running-program leak, and it needs no
  keyword, no block, no mark. Its cost is invisibility: the
  language's stated value is that "a programmer must be able to
  see what their code does to the machine", and an implicit
  loop rewind is invisible — a reader cannot tell from the loop
  that its allocations die each iteration. It also does not help
  sub-function lifetimes outside loops, and loop-carried
  allocations (accumulators) must be hoisted outside the loop,
  which is the same "where you write it is the lifetime" logic
  made implicit. Verdict: the best *automatic* carrier, but it
  trades away the explicitness the block was invented to provide.
- **The function call as the region (ROUND-60 frame regions).**
  No new syntax, covers the measured 97.2% automatically, needs
  no source changes. Its gaps are the mirror image of the
  block's: it does not give the loop-iteration case without
  extracting the loop body into a helper, and it needs the
  conservative routing analysis (which, see §6.2, is not the
  impossibility the synthesis doc claims).
- **The struct (`rachana`) as the owner.** An arena per struct:
  freeing the struct frees its members' blocks (the typed-arena
  / RAII shape). But Sutram's `rachana` are value records with
  no destructors, and adding ownership to them is a larger
  language change than a block — plus it reintroduces "who
  frees" (no destructors means manual free again, or
  reference counting, both refused). Verdict: the wrong layer.
- **The module as the region.** A module arena is just the
  program-lifetime heap (ROUND-60's heap arena). It is not a
  lifetime construct at all. Verdict: not an answer.

### 6.2 The correction to the synthesis doc's table

The table says the implicit frame region "needs escape analysis,
and it cannot work". That is imprecise in a way that matters.
What cannot work is **precise** analysis for **automatic
release** — ChatGPT proved that for the general case (aliases,
containers, callees). What **can** work is **conservative**
analysis for **routing** (ROUND-60): unknown means heap, so
imprecision costs retention, not corruption and not a compile
error. And the block's "no escape analysis" holds only for its
narrow syntactic rule; §1 shows that soundness for containers
and callees needs a taint table that *is* an escape analysis,
just a smaller one. So the honest table row is: frame regions
need a conservative analysis (works, costs retention on
imprecision); blocks need a taint analysis for soundness (works,
costs implementation); the difference is not "analysis vs no
analysis" but "what imprecision costs".

### 6.3 The synthesis: blocks complement frame regions; neither alone is enough

Ship **both**, with distinct jobs:

- **Frame regions by default** (automatic, invisible): every
  call's provably-local allocations are reclaimed on return, with
  conservative routing to the heap arena for anything escaping
  or unknown. This covers the 313 (a) sites with no source
  changes and no new syntax, and it is what makes the *library*
  safe (constructors and growth route to the heap).
- **`kshetra` blocks as the explicit opt-in** for sub-function
  lifetimes the programmer wants to control — above all the loop
  body, where frame regions alone accumulate across iterations.
  A block inside a function rewinds to its mark (inside the
  frame's slice); a function return rewinds the whole frame,
  including any open blocks (return edges rewind all open
  blocks, §2.2). The block's scope rule becomes a *check* on top
  of routing (direct assignments to outer variables are errors,
  as stated) rather than the sole safety mechanism, and the
  taint/callee extensions (§1) apply to it as well.

The block alone is insufficient (§1); the frame alone is
insufficient for loops. Together they cover everything, and each
covers the other's gap. If only one can ship, ship frame regions
— they help existing programs with no source changes, while
blocks help only programs rewritten to use them.

## 7. The lens: how many of the 313 would a block actually fit?

### 7.1 Method (so the numbers can be re-checked)

For each of the 313 (a) sites, I read the enclosing function and
asked whether the allocated variable is passed as a **bare**
argument to any call — bare meaning the variable itself (or a
derived pointer like `var + 8`), not merely the base of an index
(`var[i]`) or field access (`var.field`), which does not pass
the pointer. Control keywords (`yadi`, `yavat`, `chakra`) were
excluded as callees. A site that never passes its pointer bare
fits the scope rule with **no additional analysis**. A site that
passes it bare fits only if the callee is known not to retain
pointer values — which requires the callee-retention table.
Retaining positions are: the *value* argument of `suchi_khip`,
`avali_pravesh`, `nighantu_khip`, `kosh_push` / `kosh_enqueue`
(the container argument of those same functions is not a
retaining position — the container is mutated, not copied).
Passing a key *buffer* to `nighantu_khip` (argument 2) copies
bytes, not the pointer, so it is not retaining either.

### 7.2 The numbers

| Class | Sites | Share of 313 |
|---|---|---|
| Never passed bare — fits the scope rule alone | 42 | 13.4% |
| Passed bare, only to non-retaining callees | 271 | 86.6% |
| Passed bare to a retaining callee | **0** | 0% |

Breakdown of the 42: 32 in `.sm` files (lib scratch buffers
that are used purely locally, e.g. `roop_ank`'s `rev`,
`brihat_ank_tak`'s `rev`, `rakh_tak_mala`'s `ptrs`/`lens`,
plus record-object sites in examples) and 10 in `.py` test
programs (record instances used via field access and method
receiver, never as a bare argument — with the receiver caveat
below — plus 4 test temporaries that are only compared, never
passed: the THREE-program buffers and the loop temporary).
The 271 passed-bare sites go to a long tail of
buffer-only callees (`likha`, `akshar` / `akshar_rakh`,
`brihat_*`, `roop_*`, `vakyank_*`, `khand_*`, `anukram_*`,
`nighantu_grah` / `anwesh` / `kunjika`, `ganita_janchit_*` —
all read/write through the pointer without keeping it). The
retaining-position count is **zero**: no (a) site in the tree
passes a pointer as a *value* to a storing function. The only
`nighantu_khip` passes are argument 2 (key buffer), which is
not retaining. (A comparison-only occurrence, e.g.
`likha(a == 0)`, does not count as passing the pointer — the
callee receives a boolean, not the pointer; the counts above
use that rule.)

### 7.3 What the numbers mean — and the honest reading

The brief asks: "If it is 313, the block is the right shape. If
it is 80, the block solves a quarter of the problem." The
measured answer is **42 by the rule as written, 313 with the
retention table**. Both numbers are true and they answer
different questions:

- **42 (13.4%)** is how far the one-sentence scope rule alone
  goes, with certainty and no additional machinery. If the block
  ships with only that rule, it is sound for about an eighth of
  the tree's sites — and, critically, the rule gives no answer
  at all for the other 271 (they are not *errors* under the
  rule, they are *uncovered*: the rule permits passing to any
  callee, including a retaining one, so a future program passing
  a block pointer to `suchi_khip` as a value would compile and
  dangle).
- **313 (100%)** is how far the block goes *if* the compiler
  knows which callees retain pointer values. That table is small
  for this library (four functions' value positions, above) —
  but it is an analysis, and for user code with unknown callees
  the rule must be conservative (unknown callee = assume
  retaining), which means currently-valid programs that pass
  buffers to user helpers would be rejected unless the table
  covers those helpers too. That is the real cost of extending
  the rule, and it is the same table ROUND-60's routing needs —
  which is why §6.3 proposes sharing it rather than building it
  twice.

Two caveats on the 42: (i) **method receivers** — a record
object allocated in a block and used as a method receiver
(`b.badha(4)`) is not a bare argument pass, so it counts as
strict-fit here, but a method that stores its receiver (`swa`)
is a retaining callee through the receiver, not through an
argument. The receiver case needs the same table, keyed on
methods. It does not occur in the tree's (a) sites (test methods
do not store `swa`), but it must be specified. (ii) The 42
includes sites whose pointer is never passed anywhere — the
purest block candidates, and the natural first users of the
syntax.

### 7.4 How many `nirmmita` calls are inside loops today? One.

Two independent methods (a loop-stack walk per function, and a
whole-file loop-body range computation) agree: **0 of the 284
`.sm` (a) sites are inside a loop body**, across 48 files that
contain loops. The tree's loops *use* allocations made before
the loop; they do not allocate inside it. Checking the 29 `.py`
program strings the same way finds exactly **one** in-loop site
in the whole tree:

```
tests/r38/test_fail_alloc.py — mukhya() {
    vitti i = 0
    yavat (i < 6) {
        likha(nirmmita(8) == 0)     # temporary, alloc-failure probe
        i = i + 1
    }
}
```

So the loop count is **1 of 322 executable sites (0.3%)**, and
it is a test temporary, not a server loop. This does not
invalidate the loop pattern — the pattern is for future
long-running programs, and Gemini's phase insight is about
programs the tree does not yet contain. But it does reframe the
priority: a `kshetra` block in a loop helps **future** code
first, and converts **almost no existing** code. The block's
first users will be new programs written with it, not the
existing 313 sites — which is another reason to ship frame
regions (which help existing code with no rewrites) alongside
blocks, rather than blocks alone.

## 8. The fixes, in order — what would make the block shippable

1. **Taint, not scope.** Track block-ness through values:
   containers holding block pointers are tainted; tainted values
   may not be returned, stored outside, or passed to retaining
   callees. Derived pointers (`ptr + k`) carry the taint.
2. **A callee rule.** Specify what happens when code inside a
   block calls an allocating function: either callee allocations
   use a separate arena (and blocks never reclaim them), or the
   compiler knows which callees allocate escaping values. Do
   not leave it unspecified — it is the common case (every
   constructor call).
3. **Rewind on every exit edge.** Returns rewind all open blocks
   after computing an untainted value; `krama` / `agrim`
   rewind to the target's mark (one restore per edge). Test the
   `agrim`-in-block loop explicitly for bounded memory.
4. **Zero by default.** Block allocations are zeroed on
   allocation (Claude's 4 broken proofs are the evidence that
   reuse without zeroing breaks real code). Document it as the
   contract, not a choice.
5. **Modest default reservation, runtime `MAP_NORESERVE` for
   large ranges, explicit chunked commit on Windows, clean abort
   (never silent `mmap` fallback) on exhaustion.** Separate the
   reservation size from the checked limit (§4.2).

## 9. Is the whole idea wrong? No — but its claim is

"The lifetime should not be expressed in the syntax at all"
would be the ROUND-60 answer: the compiler routes, the
programmer writes nothing new, and the 97% are reclaimed
automatically. That answer is better for existing code and
worse for the loop case and for visibility. The block is not
wrong; it is **incomplete as a complete memory story** and
**oversold as needing no analysis**. As an explicit lifetime
construct for the cases the programmer wants to control — above
all the loop body — it is well designed, well named (`kshetra`
is attested and untaken; `kosa` would have collided with `kosh`,
correctly avoided), and it composes with frame regions rather
than competing with them. Ship both (§6.3), with the five fixes
above, and the block earns its place. Ship the block alone with
only the one-sentence rule, and the first program that builds a
list inside a block via a helper will dangle — with no rule
violated and no diagnostic to explain why.

## 10. The two tests, and the two more tests they imply

- **1,000,000 × 64 B in a block in a loop:** cannot run yet (no
  `kshetra` syntax exists). When it can, the pass condition is
  bounded memory *including* an `agrim` variant (§3.2) — a loop
  that only tests the fall-through rewind proves half the
  mechanism. Expected result if the design works: a few MB,
  flat with iteration count. Failure mode to watch: growth with
  iteration count means a jump edge is skipping its rewind.
- **Assign-to-outer-variable must fail to compile, with a line
  number:** the direct case is checkable syntactically and
  should be the first negative test. But it is not sufficient:
  add the **container negative test** (§1.2: return a record
  wrapping a block pointer — must fail) and the **callee
  negative test** (§1.3: assign a constructor's result to an
  outer variable inside a block — must fail or the callee rule
  must explain why it is safe). If either of those compiles
  under the narrow rule, the rule is not working, and that is
  the most valuable signal the tests can give.

## NOT RUN

- Windows / WSL: the PE `.bss` behavior for large sections and
  the `MEM_RESERVE` + chunked-commit behavior are analyzed from
  documentation and the Linux measurements, not run on Windows.
- Browser automation: no browser component in this round.
- Implementation: no compiler code was changed and no `kshetra`
  program was run (the syntax does not exist yet); the guard was
  not re-run (no tree changes).
- The `.bss` and `MAP_NORESERVE` figures cited are Claude's
  measurements (`evidence-r60/`), re-checked for consistency
  with my own ROUND-60 `.bss` experiment (1 KB vs 64 MB →
  identical file size), not re-run here.
