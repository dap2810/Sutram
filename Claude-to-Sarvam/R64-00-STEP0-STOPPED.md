# R64-00 — Step 0: STOPPED before building. Both invariants are false in this compiler.

- **Base:** `main` at `2bc54c3`, compiler v261. **No source change. Nothing was built.**
- The brief: *"If either invariant is false in this compiler, STOP and report it — the design depends on both."*
  Both are, measured on the committed v261 (`evidence-r64/invariants.txt`, programs beside it).

## Invariant 2 — "`kosh` capacities are always powers of two": FALSE

| Declaration | after 9 pushes, `kosh_cap` |
|---|---|
| `kosh k[1]` | 16 |
| `kosh k[3]` | **12** |
| `kosh k[5]` | **10** |
| `kosh k[1000000]` | **1000000** |
| `kosh k[6]`, no push | **6** |

The capacity is whatever the program declares, and growth doubles it (`src/sutram_compiler.asm:15729`,
*"newcap = cap ? cap*2 : 4"*). **In the tree: 131 `kosh` declarations carry a literal capacity, and 33 are not a
power of two** (3 ×20, 5 ×5, 6 ×4, 9 ×4). Rounding declared capacities up would make it true, but **10 programs
print `kosh_cap`**, so that changes goldens — and the `.sm` programs that declare `kosh k[3]` would stop meaning what
they say.

**What it breaks in the design:** the power-of-two bins are indexed by size class. A 12-cell block has no bin; a
10-cell request cannot pop a 16-cell block without a size field the block does not have. The bins would need a
first-fit search or a header, and either is no longer "three instructions".

## Invariant 1 — "a `kosh` owns its backing buffer privately, so the old array is dead after growth": FALSE

```
kosh k[1]
kosh_push(k, 7)
vitti a = k            # the compiler marks a as a kosh variable too (the R38 kind propagation)
kosh_push(k, 8)
kosh_push(k, 9)        # k grows: a new buffer; a still points at the old one
a[0] = 99
likha(a[0])            # 99
likha(k[0])            # 7     - two live buffers
kosh_push(a, 5)
likha(kosh_len(a))     # 2     - the old buffer is still a working kosh
likha(kosh_len(k))     # 3
```

**The old buffer is not dead; it is a second `kosh`.** R59 (`evidence-r59/kosh-aliases.txt`) found the same through
a `mala` cell and through a global. Today the consequence is a stale copy, which is odd but harmless. **With the
freelist bins, the old buffer is handed to the next `kosh` of that size class, and `a` then reads and writes another
`kosh`'s header and data — a silent use-after-free, exactly the failure R59 WS3 warned the `munmap`-on-move fix would
create.** The bins are that fix under another name.

## A third problem, not an invariant: mechanism 1 cannot exist in Step 0

*"If `old_ptr + old_capacity == persistent_cursor`, extend the cursor."* **There is no persistent cursor until Step 1
or 2 exists.** Today every `kosh` buffer is its own `mmap` and there is nothing to compare against. The brief forbids
touching `nirmmita` or adding a cursor in this round, so the in-place extension — the half of Step 0 that is safe —
is not buildable here.

## What I did not do

- **Nothing was built.** No `src/`, `lib/`, `tests/` or binary change.
- **No measurement after,** because there is no after. The measurement before is in
  `evidence-r64/append-1M-before.txt`: 1,000,000 appends onto `kosh k[1]` peak at 16,000 KB against 7,808 KB for a
  `kosh` that never grows, about 8.2 bytes abandoned per item (R59's figure; the brief's 15.3 is the whole footprint).

## How I would reshape Step 0, for the owner to decide

**Keep the half that is alias-safe, drop the half that is not, and move Step 0 after Step 2.**

1. **In-place extension only.** When the `kosh`'s buffer is the topmost persistent allocation, extend it; the buffer
   never moves, so every alias stays valid, and the leak is zero for the common case — one `kosh` grown in a loop.
   When something else sits above it, fall back to today's copy-and-abandon: no worse than now, and never a reuse.
   **It needs the persistent cursor, so it belongs right after Step 2**, where it is ~20 lines at the growth site
   (`:15720-15900`).
2. **No bins.** Reuse of an abandoned buffer is unsafe while `vitti a = k` is legal, and bin indexing needs invariant
   2. If reuse is ever wanted, the compiler must first refuse `vitti a = k` for a `kosh` (it already refuses
   `kosh_push` on a parameter for a related reason, `:15651`) — a language change, not a Step 0.
3. **The alternative that is buildable today without a cursor** is the one R59 WS3 priced: reserve the `kosh`'s
   growth room at declaration with `MAP_NORESERVE` and grow by updating the capacity field. It is alias-safe and
   removes the leak and the copy, ~50 lines. **But it allocates per `kosh`, which does not fit the single arena of
   Step 2, so it would be rebuilt one round later.** I would not spend a round on it.

**The invariant to write into `MEMORY-DECISION.md` instead of the two false ones:** *a `kosh` buffer never moves to
an address another allocation can receive while the program can still name the old one.* In-place extension keeps
it; bins break it; the current copy-and-abandon keeps it by leaking.

## Also seen, not touched

- `--fail-alloc N` counts `kosh` growth allocations; any Step 0 changes the numbering that `tests/r38` baselines.
- The `kosh` and `mala` declaration paths still write their header through an untested pointer (ChatGPT's R131,
  my R62 §3.5). Independent of Step 0, reported again.
