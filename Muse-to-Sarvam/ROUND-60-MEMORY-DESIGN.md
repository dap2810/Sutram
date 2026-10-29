# ROUND-60 — the memory design: escape-routed dual arenas in `.bss`

Base: origin/main `b6106934`, CHANGELOG v414, compiler v261.
Design only — nothing here is implemented, and no tree changes were
made. The escape classification it rests on is measured in
ROUND-59 (same delivery batch): of 322 executable `nirmmita`
sites, (a) 313 / (b) 6 / (c) 3.

## 0. The problem, restated from the measurements

Today every `nirmmita` is a kernel call (`mmap` per call on Linux,
`VirtualAlloc` per call on Windows) and nothing ever comes back:
zero `munmap` in the compiler, and `kosh` growth abandons the old
block on every growth (emitter, one place — see R59 WS2). The
measured gap is ~1,000x (250,000 cycles vs ~250 for a bump).
The design question is therefore two questions, not one: (1) how
to stop paying a syscall per allocation, and (2) how to stop
leaking — and the second splits again into the `kosh` bug (fixable
today, separately) and the escape problem (which decides whether
any region design is usable at all).

## 1. My design: two bump arenas in `.bss`, routing decided at compile time

### The shape

Reserve **two** arenas in `.bss` at link time (Sarvam's mechanism,
verified below): a **frame arena** and a **heap arena**.

- `nirmmita` becomes a bump in one of the two arenas. Same
  instruction sequence either way: align size up, bounds-check
  against the arena end, bump, return the old pointer. The only
  difference is *which* bump pointer and end bound the emission
  uses — and that is chosen **at compile time, per call site**,
  by a conservative escape analysis (below). There is no runtime
  decision, no branch on escape, no keyword for the programmer to
  write or forget.
- On function entry, the compiler pushes the current frame-arena
  bump onto a region stack (one slot in the frame, or a small
  explicit stack). On return, it restores the bump from that slot.
  Everything the call allocated from the frame arena is released
  by that single restore. This is Sarvam's call-frame region, kept.
- The heap arena is never reset during the program. Blocks routed
  there live until program end — exactly today's retention
  behavior, but without the syscall per allocation.
- `kosh` blocks come from the frame arena when the kosh variable
  is provably local, and from the heap arena when the kosh variable
  escapes (see §1.3). `kosh` growth is emitted inline in the
  owner's frame, so it bumps the same arena the kosh's current
  block came from — the growth code already knows which, because
  the routing decision for that variable is compile-time.

### 1.1 The routing rule (the whole design in one paragraph)

For each `nirmmita` site, the compiler asks: can the allocated
pointer escape this call? Escape means: returned (directly or
inside a returned record), stored into a caller-owned container
or a global, or passed to a function that is not known to keep
its pointer arguments. If the answer is **provably no**, route to
the frame arena. If the answer is **yes or unknown**, route to the
heap arena. The analysis is deliberately conservative: **unknown
means heap**. That is the property that makes the design safe
without being a borrow checker — imprecision costs retention, not
corruption, and not a compile error. A program the analysis cannot
follow still compiles, still runs at bump speed, and still never
dangles; it just retains more. The measured tree says the cost of
conservatism is small: the provably-local set is 97.2% of sites,
and the escaping set is 8 library sites plus one global, all
syntactically obvious (a return, a store into a returned record,
a store into a caller-owned container).

### 1.2 Code sketches

The allocator (either arena; `bump`/`end` are the routed pair):

```asm
; nirmmita, size in rax. Returns pointer in rax, or aborts cleanly.
; (per-site, bump/end are the routed arena's pair)
    add rax, 7
    and rax, ~7             ; align to 8: cells are qwords
    mov rdx, [bump]         ; old pointer
    lea rcx, [rdx + rax]    ; new bump
    cmp rcx, [end]
    ja  .oom                ; clean abort naming the arena and the flag
    mov [bump], rcx         ; commit
    mov rax, rdx            ; return the old pointer
```

(Sarvam's four-instruction version plus the alignment pair. The
point is the shape: align, check, bump — no syscall, no branch
on escape.)

Frame enter/exit (emitted by the compiler around each `prakriya`
body; one push and one restore):

```asm
; enter: save current frame bump
    push qword [frame_bump]
; ... body, nirmmita bumps frame_bump ...
; exit (all return paths, including error returns):
    pop qword [frame_bump]  ; everything the call allocated is gone
```

OOM path (there are no exceptions in this language, so exhaustion
is an abort, not a recovery — an improvement on today, where a
failed `mmap` returns 0 and the program dereferences it):

```asm
.oom:
    ; write "arena exhausted: rebuild with -arena=<size>" to stderr
    ; exit with a distinct code (not a segfault, not silent 0)
```

Zeroing policy: the frame arena is zeroed on **allocation**, not
on close. Rationale in §3. The cost is a `rep stosb` over the
block — still orders of magnitude cheaper than a syscall, and it
removes the stale-data class entirely. The heap arena needs no
zeroing beyond what `.bss` gives it on first touch, since heap
blocks are never reused within a run.

### 1.3 How the hard cases route

- **Constructors** (`suchi_srij`, `nighantu_srij`, `avali_srij`,
  `mala_nava`): their allocations are returned → heap arena.
  The caller gets a heap block that lives as long as the program.
  Same retention as today, zero syscalls. No keyword, no change
  to the constructor's source.
- **Growth** (`suchi_vardh`, `avali_pravesh`): the new block is
  stored into a caller-owned container → heap arena. The old heap
  block is abandoned — same leak as today, but now it is a
  bump-arena leak (address space, not syscalls) and it is fixed
  by the same `munmap`-equivalent the `kosh` fix needs, or
  accepted until the heap arena gets a free primitive. Crucially,
  growth can never dangle: the new block is in the heap arena,
  which no return ever resets.
- **`kosh` variables**: the emitter already knows, per variable,
  whether it flows to a return or a store (that is the same
  analysis). A local kosh grows in the frame arena; an escaping
  kosh grows in the heap arena. `kosh_push` on parameters is
  already rejected by the compiler, which removes the hardest
  sub-case (a callee growing a caller's kosh) by construction.
- **The global** (`global_pointer.sm` pattern): top-level
  allocations route to the heap arena. Globals are few and the
  rule is trivial (not inside any frame → heap).
- **Recursion**: each live frame holds its own frame-arena slice.
  Peak frame-arena use is the sum over live frames. Deep recursion
  with large per-frame allocations exhausts the frame arena
  sooner than a heap design would — a real limit, stated honestly
  in §3, mitigated by sizing the frame arena generously (it is
  virtual, see §4.1) and by the clean OOM abort.

### 1.4 What changes for the programmer

Nothing, for existing programs. No new keyword, no annotation, no
region block to write. `nirmmita` keeps its meaning; the compiler
just stops paying a syscall for it and stops leaking the
provably-local 97%. A programmer who wants a single object freed
mid-program still cannot have it — that is the `pratyarpana`
escape hatch (see §3), not part of this design's v1.

## 2. The four scores, honestly

### Speed

**Ties Sarvam's design.** Every allocation, frame or heap, is the
same bump sequence: align, bounds-check, commit — a handful of
instructions, ~250 cycles dominated by the cache miss on
first-touch pages, versus ~250,000 for today's `mmap`. There is
no per-allocation runtime escape check (routing is compile-time),
no reference counting, no write barrier. The frame restore is one
pop per return. Zeroing on allocation adds a `rep stosb` over the
block: for the tree's typical small buffers (8–128 bytes) this is
a few cycles; for large blocks it is linear in the block, which
is still the cost of touching the memory the program is about to
write anyway. If a benchmark ever shows zeroing dominating, it can
be made opt-out per site — but the default must be zeroing (§3).

### Safety

**Better than Sarvam's keyword design, and the reason is the
failure mode.** The keyword design fails when a programmer forgets
to promote: the result is a dangling pointer unless the compiler
catches the omission — and catching the omission *is* the escape
analysis the design claims to avoid (§4.2). This design cannot
dangle by construction: anything that escapes, or might escape,
is in the heap arena, which is never reset. The failure modes that
remain are (i) retention: conservative routing keeps memory until
program end — the same behavior as today, bounded by the heap
arena size; (ii) exhaustion: a clean abort naming the arena and
the build flag, instead of today's silent 0 followed by a
dereference crash; (iii) stale data: eliminated by zero-on-alloc
in the frame arena (heap blocks are never reused, so they cannot
go stale). What a programmer can get wrong: essentially nothing
new — there is no new keyword to misuse, no region to close early
or late, no free to forget or double. The one new footgun is
assuming a heap-routed block will be reclaimed (it will not) —
but that is today's behavior too, so it is not a new surprise.

### Cost

- **Runtime:** two `.bss` blocks, two bump pointers, two end
  bounds, one region-stack slot per frame, one push/pop per call.
  The allocator emission is ~10 lines of NASM per site (shared
  sequence, parameterized by bump/end) — comparable to Sarvam's
  ~120 lines total for the mechanism.
- **Compiler:** the escape analysis pass. This is the real cost,
  and I will not minimize it: a dataflow pass over each function
  tracking which locals flow to returns, stores, and unknown
  callees, plus a small table of which library functions store
  their pointer arguments (enumerable: the storing set is
  `suchi_vardh`, `avali_pravesh`, `nighantu_khip`, the `*_srij`
  family via their returns, and the `kosh` builtins — the rest
  either return pointers or merely write through them). Estimate:
  a few hundred lines of compiler code, not NASM, and it reuses
  the existing AST walk. It is more than Sarvam's "one keyword
  check" — but see §4.2: the keyword check needs this pass
  anyway to catch omissions, so the honest comparison is not
  "pass vs no pass" but "pass used for routing vs pass used for
  erroring". Routing is strictly more forgiving of the same pass.
- **Migration:** zero source changes. The 322 sites route
  automatically; the guard must stay 0 DIFFER for every program
  whose observable behavior does not change (all of them, since
  retention is not observable except through allocation failure
  and timing).

### Novelty

**A refinement, not a revolution — and the refinement is the
conservative routing.** Region systems normally demand either
 programmer annotations (Rust lifetimes, Cyclone regions) or a
precise analysis that rejects programs it cannot prove safe. This
one exploits a property of *this* tree: escaping allocations are
rare (2.8%) and syntactically obvious, and both arenas are bump
allocators, so routing a site to the "wrong" arena costs nothing
in speed. That makes a *conservative* analysis viable where a
*precise* one would be required if the two destinations had
different costs. The novelty is not the arena (textbook) or the
frame region (textbook) — it is the observation that when both
destinations are equally fast, the analysis does not need to be
precise, only conservative, and therefore does not need to reject
anything. Whether that counts as "better than the obvious answer":
it is better than Sarvam's keyword version on safety (no
forgotten promotion) at the cost of a compiler pass; it is worse
than Sarvam's version on conceptual simplicity (two arenas and a
pass versus one arena and one word). I would defend the trade
because the keyword version's simplicity is bought with a
soundness hole (§4.2).

## 3. What this design CANNOT do

- **Free a single object mid-program.** A frame-arena block dies
  only when its frame returns; a heap-arena block never dies
  within a run. A program that allocates in a long-running loop
  and needs each iteration's garbage reclaimed will exhaust the
  heap arena if its allocations route there, and will be fine if
  they route to the frame arena (each iteration's frame closes).
  The `pratyarpana` escape hatch (an explicit free primitive,
  essentially `munmap` for a block) is the answer for the 5% that
  needs it, and it should exist — but it is separate from this
  design, and it must be explicit, not the default.
- **Programs needing more than the reserved arenas.** Fixed
  ceiling, same as Sarvam's: the ceiling is a build flag, and
  exhaustion is a clean abort. The frame arena can be sized
  generously because it is virtual (see §4.1); the heap arena
  deserves a smaller default with the same flag to raise it.
- **Reclaim heap memory.** Until a free primitive exists, heap
  retention is process-lifetime. For the tree's own programs this
  is today's behavior, so it is not a regression — but it is not
  an improvement either, for the escaping 3%.
- **Threads.** A single global bump per arena is not thread-safe.
  Sutram has no threads today; if they ever arrive, arenas become
  per-thread (or locked, which breaks the instruction-count
  claim). This is a future constraint, not a present one.
- **Reuse of heap blocks.** There is no allocator in the heap
  arena, only a bump. Fragmentation is not a concept here — but
  neither is reuse. A long-running program that repeatedly
  allocates escaping objects will grow the heap monotonically.
  That is the price of "no runtime, no GC", stated plainly.

## 4. Is Sarvam's `.bss` idea actually safe? What breaks it?

Short answer: **the `.bss` mechanism is sound and I verified its
two load-bearing claims independently (§4.1). The call-frame +
promotion story built on top of it is incomplete in four specific
ways (§4.2–§4.5), each fixable, and the fixes converge on the
design in §1.** I would not ship the idea as stated; I would ship
it with the fixes.

### 4.1 The mechanism: verified, and genuinely free on Linux

- **File size:** I assembled two minimal programs, one with a
  1 KB `.bss` block and one with a 64 MB `.bss` block. Both
  produced a **4,752-byte** executable. `.bss` occupies address
  space, not file space — confirmed, not just asserted. (Sarvam's
  figure was 4,744 bytes; the 8-byte difference is my harness, not
  the property.)
- **The loop:** I ran a 1,000,000 × 64-byte bump-allocation loop
  from a 64 MB `.bss` arena, writing the loop index into each
  block and reading back the last value: correct (999,999),
  5,000-byte binary, 0.039 s total. The mechanism works at scale
  in this sandbox.
- **Zeroing:** `.bss` arrives zero-filled by the loader, so the
  first use of any page is clean. This half of the `samskara`
  claim holds. The second half does not (§4.4).

### 4.2 The promotion keyword does not remove the escape analysis — it hides it

The claim is: "the escape check is not a type system, it is a
word you write when you mean it." That is true for the programs
where the programmer remembers. The design's safety property is
"nothing can dangle, because anything that outlives its region
was promoted deliberately." For that property to hold, a
*forgotten* promotion must be an error — and detecting a
forgotten promotion requires the compiler to know, for every
allocation, whether it escapes. That is exactly the escape
analysis. There is no version of this design in which the analysis
is optional: either the compiler performs it (and then the
keyword is redundant for safety — the compiler could route
instead, which is §1), or it does not (and then a forgotten
promotion is a silent dangling pointer, which is worse than
today's leak, because a leak is observable and a use-after-free
is corruption). The keyword is a useful *annotation* for the
programmer's intent; it cannot be the *mechanism* of safety.
Severity: soundness hole, must fix before shipping. Fix: perform
the analysis and either route (§1) or error on unpromoted escape
— but note that erroring requires the analysis to be precise
enough not to reject valid programs, which is strictly harder
than routing conservatively.

### 4.3 Promotion has no target in the growth case

Consider `suchi_vardh`: it allocates a new block and stores it
into the *caller's* list. Under call-frame regions, the new block
is allocated in `vardh`'s frame. When `vardh` returns, its frame
closes. If `vardh` "promotes" the block, promoted to *where*?
Not to `vardh`'s frame (that is what is closing). To the caller's
frame — but the promotion keyword as stated names no target
region, and the compiler must therefore infer that the
destination is the region of the container being grown. That
inference is region polymorphism (the callee's allocation lives
in the caller's region), which is a real type-system feature, not
a word. The same problem hits every constructor: `suchi_srij`'s
blocks must land in the *caller's* region, not `srij`'s own. So
the design as stated works for the (a) majority (where nothing
needs promoting) and is underspecified for exactly the 8 library
sites that need it most. Severity: design gap, must fix. Fix:
either promotion-to-caller-region as a first-class concept (which
is the analysis again, plus region parameters), or the dual-arena
routing of §1 (where constructors and growth simply use the heap
arena and the question of "which frame" never arises).

### 4.4 A single bump arena cannot hold both a frame's locals and its promoted blocks

With one bump pointer per arena, a frame's allocations are
contiguous from the frame base. Suppose a frame allocates A, then
a promoted block P, then B. On return, resetting the bump to the
frame base frees P (dangling). Resetting it to just past P keeps
P alive but also keeps B and everything after P alive (retention
until the arena is next reset — which, for a single arena, means
leakage that accumulates across calls). The standard solutions
are (i) a separate heap arena for promoted blocks (§1), or
(ii) copy-on-promote (the block's bytes are copied to the outer
region — a hidden copy with a cost, and the copy must happen at
the promotion point, which again needs to know the target).
The single-arena sketch in the proposal does not address this.
Severity: real, but the fix is the dual arena, which is cheap.
Note this is also why §1 zeroes on allocation rather than on
close: with a single arena and frame reuse, close-and-reuse is
the common path, not the exception.

### 4.5 Reused frame memory goes stale on every call (the `samskara` half that does not hold)

`.bss` is zeroed once, at load. After that, every frame close
hands its memory to the next call. A program that reads an
allocation before writing it — a bug today only if the `mmap`'d
memory happened to be non-zero, which it never is — will, under
frame regions, read the *previous call's* data deterministically.
That is a new class of surprising behavior (and a real
information-leak vector for programs handling keys or tokens:
a buffer that once held a secret will hand it to the next caller
of the same function). The proposal acknowledges zeroing on reuse
as "a choice". It should not be a choice: zeroing on allocation
must be the default, at the small linear cost stated in §2.
Severity: correctness/security, fix by defaulting to zeroing.

### 4.6 Smaller breaks, each worth one line in the implementation

- **Fixed ceiling is death, not recovery.** The proposal's "clean
  error" is a clean *abort*: this language has no exceptions, so
  a program that exhausts the arena cannot catch it. That is still
  strictly better than today's silent 0 → dereference crash, but
  the report should say "abort", not "error", so nobody plans
  around recovery.
- **Recursion multiplies frame use.** Peak frame-arena consumption
  is the sum over live frames. A recursive function allocating a
  large buffer per level exhausts the arena at depth × size.
  Size the frame arena for this, and document it.
- **Alignment is missing from the sketch.** The four-instruction
  version adds `size` raw; sizes must be rounded up to 8 (qword
  cells) or a 1-byte allocation followed by an 8-byte store
  corrupts its neighbor. One `add`/`and` pair fixes it.
- **`nirmmita(0)` needs a defined meaning.** Today's `mmap(0)`
  behavior is an edge; under a bump, 0 must return a valid,
  non-dangling pointer (the current bump, unadvanced) or be a
  compile-time error. Pick one and document it.
- **Windows is unmeasured.** The `.bss` property was verified on
  Linux ELF. PE uninitialized sections behave similarly in
  principle (VirtualSize without raw data), but the Windows
  loader's reservation/commit behavior for very large sections,
  and the 32-bit address-space budget for the wizard's Win32
  target, are not measured here and must be before a large
  reservation ships. This is a measurement gap, not a refutation.
- **`kosh` is outside `nirmmita`.** The emitter's `kosh` growth
  uses `mmap` directly (R59 WS2). A `.bss` design that only
  replaces `nirmmita` leaves `kosh` leaking via syscalls. The
  design must move `kosh` growth to the arena too — which, as
  noted in R59, is actually the easy case, since `kosh` growth
  is emitted inline in the owner's frame.

## 5. If the framing is wrong, say so

The framing is *mostly* right. The syscall-per-allocation is the
measured 1,000x and it is the right problem. Two corrections:

1. **The leak is not one problem but two.** The `kosh` growth
   leak is a bug, not a design consequence, and it is fixable in
   one emitter change without any region machinery. Conflating it
   with the allocation-cost problem makes the region design look
   load-bearing for something it is not needed for.
2. **The region question is really the escape question.** "Can
   we use regions?" is decided entirely by the (a)/(b)/(c) split,
   which nobody had measured. Now it is measured: 97.2% local.
   The design problem is therefore not "how to make regions
   safe in general" but "how to handle 8 library sites and one
   global". Any design that solves those 9 sites and bumps the
   rest is sufficient. Both Sarvam's proposal and §1 do that;
   §1 does it without a new keyword.

What the framing gets wrong, if anything, is the implied
universality: a region design (either version) does not fix the
heap-routed 3%'s retention, and it does not give anyone a free
primitive. The honest summary is: regions fix the speed problem
for everything and the leak problem for 97%; the remaining leak
and the free primitive are separate work.

## 6. The `kosh` fix, separately (it needs fixing regardless)

This is the non-design question, answered directly:

- **Emitter (one place):** in `.ge_call_koshpush`, after the
  element copy and after the kosh variable points at the new
  block, emit a `munmap` of the old block (old pointer is
  preserved across the allocation in the emitted sequence; old
  byte size = `oldcap * 8 + 16`). No other emitter change is
  needed. This alone fixes the `kosh` leak for all programs.
- **Library (three sites):** `suchi_vardh`, `avali_pravesh`, and
  the `nighantu_vardh` caller-side abandonment need a free
  primitive the library can call — the `pratyarpana` escape
  hatch, i.e. a builtin that emits `munmap(ptr, size)` (and
  `VirtualFree` on Windows). Until that builtin exists, the
  library growth leak remains even after the emitter fix; it is
  smaller (three sites, all container growth) but it is the same
  bug class and should be tracked as such, not silently absorbed
  into "the region design will fix it".
- **Under §1's design:** `kosh` growth in the frame arena needs
  no `munmap` at all (the frame restore reclaims the old block
  together with everything else in the frame — the old block's
  pages are simply reused by the next call). Heap-arena `kosh`
  growth (escaping kosh variables) still needs the free
  primitive for full reclamation, or accepts heap retention.
  Either way, the emitter `munmap` fix is worth landing *before*
  any region work, because it fixes a live bug on the current
  design with no behavior change for any program.

## 7. What I would build, in order

1. **The `kosh` emitter `munmap`** (§6). One place, bug fix,
   guard must stay 0 DIFFER.
2. **The `.bss` frame arena for (a) sites, with zero-on-alloc
   and the clean OOM abort** — the speed win, with no language
   change and no keyword.
3. **The heap arena + conservative routing** (§1) — the safety
   win, which is what makes step 2 shippable for library code.
4. **The `pratyarpana` free primitive** — for the library growth
   sites and the 5% that needs single-object free.
5. **Windows `.bss` measurement** before any large reservation
   ships on the Windows target.

## NOT RUN

- Windows / WSL: the PE reservation behavior is unmeasured
  (§4.6), and no Windows binary was built or run here.
- Browser automation: no browser component in this round.
- Implementation: this is a design; no compiler code was changed
  and the guard was not re-run (no tree changes).
- The 1,000,000 × 64-byte loop and the `.bss` size comparison
  were run as standalone NASM programs in this sandbox, not as
  Sutram programs — they verify the mechanism, not a Sutram
  implementation of it.
