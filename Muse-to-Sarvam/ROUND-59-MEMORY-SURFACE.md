# ROUND-59 — the memory change surface: every site, counted

Base: origin/main `b6106934`, CHANGELOG v414, compiler v261.
(The brief said v412; main moved to v414 since. The delta is memory
docs, Claude's R58 application, and the guard tool — no `lib/`,
`examples/`, or `tests/` code change affects these counts. Everything
below was measured on current main.)

Measurement only. No tree changes.

## WS1 — every `nirmmita` site

Counting rule: one textual `nirmmita(...)` call = one site, in
`.sm` / `.smlib` source and in Sutram programs embedded as strings
in Python test harnesses (those programs execute when the test runs,
so they count). Prose mentions in docs are counted separately and
are NOT call sites. Commented-out occurrences are excluded from the
call-site counts and noted. `tests/negative/` is counted separately:
those are SHA-pinned historical crash inputs, DO-NOT-TOUCH, not live
code.

### Totals

| Directory | Call sites | Of which |
|---|---|---|
| `lib/` | 36 | fixed 10, computed 26 |
| `examples/` | 27 | fixed 27, computed 0 |
| `tests/` (`.sm`, excl. negative) | 230 | fixed 229, computed 1 |
| `tests/` (`.py` program strings) | 29 | fixed 29, computed 0 |
| **Executable total** | **322** | **fixed 295, computed 27** |
| `tests/negative/` (separate) | 19 | fixed 19 |
| `docs/` (mentions, not sites) | 11 | 4 fixed-form, 6 computed-form, 1 prose mention without a parseable call |
| Comments containing `nirmmita(` | 3 | 1 in `lib/`, 2 in `tests/` |
| **All occurrences** | **355** | |

### Shapes

- **Fixed** = the size is a pure numeric literal expression
  (`nirmmita(64)`, `nirmmita(8 * 8)`, `nirmmita(300 * 40 * 8)`).
  A bump allocator handles these trivially — the size is known
  without running anything.
- **Computed** = the size depends on a value (`nirmmita(c * 8)`,
  `nirmmita(oldcap * 33 + 1)`, `nirmmita(sz)`). A bump allocator
  handles these equally well — the size is computed at runtime and
  the bump just adds it. The fixed/computed split matters for
  static analysis (a fixed size can be checked against a region
  ceiling at compile time), not for bump feasibility.

Distinct argument expressions: `lib/` 26 distinct (nearly every
computed site is unique); `examples/` 27 sites but only a handful
of distinct sizes (64, 128, 8, 16, 32 dominate — beginner buffers);
`tests/` dominated by the same small set (8, 64, 128, `N * 8`).

The single computed site in `tests/*.sm` is
`tests/stdlib/r8_list_model.sm:51`,
`nirmmita((avali_maap(q) + 1) * 8)` — a size derived from a live
queue length. The `lib/` computed sites are the interesting set:
growth buffers (`ncap * 8`, `oldcap * 33 + 1`), container backing
stores (`sz`), and scratch of input-dependent size (`c * 8`,
`c * 4 * 8`, `s[0] * 33 + 1`).

## WS2 — every `kosh` growth point

**Answer first: `kosh` growth is in the compiler emitter, in one
place — and the old block is abandoned there. The same abandonment
pattern also exists in three library growth helpers, which need a
separate fix.**

### Emitter: one place

`kosh` is a compiler builtin type (growable qword array, `KW_KOSH`,
`src/sutram_compiler.asm:172`), not a library type. `kosh_push`
is emitted by `.ge_call_koshpush` (`src/sutram_compiler.asm:15651`).
When length == capacity, the emitted code:

1. computes `newcap = cap ? cap * 2 : 4`;
2. calls `emit_nirmmita_from_rax` (`:15799`) — a fresh `mmap`
   for the new block;
3. writes the new header (`[rax] = len`, `[rax + 8] = newcap`);
4. copies the old elements one by one into the new block;
5. updates the kosh variable to point at the new block.

There is **no `munmap` anywhere in the compiler** (grep over `src/`
and `win/` returns zero). The old pointer is preserved across the
allocation only as a copy source. After the copy, nothing releases
it. **The old block is abandoned on every growth. That is the
leak, and it is one place, so the fix is small:** emit a `munmap`
of the old block after the copy (old pointer and old capacity are
available in the emitted sequence; old byte size = `oldcap * 8 +
16` for the header).

Note the asymmetry this creates for any region design: `kosh`
growth is emitted inline in the *owner's* frame (it is not a call),
so a frame-region design handles `kosh` growth naturally — the new
block is allocated in the frame that owns the kosh variable. The
library containers below do not have this property, because their
growth happens inside a callee.

### Library: the same pattern in three helpers

- `suchi_vardh` (`lib/suchi.smlib:67`): allocates `nd`, copies,
  writes `lst[2] = nd`. The old data block is dropped, never freed.
- `avali_pravesh` (`lib/suchi.smlib:404`, grow branch): same —
  `qu[2] = nd`, old block dropped.
- `nighantu_vardh` (`lib/nighantu.smlib:279`): returns a *new* map
  built by `nighantu_srij`; the caller's old map block is abandoned
  when the caller replaces its handle. (Its own `tmp` scratch
  buffer is a separate, dropped-inside-the-function allocation.)

`nighantu_khip` does NOT grow: when the table is full it returns 0
and leaves the map unchanged. Growth for maps is explicit via
`vardh`, not implicit in insert.

These three need a free primitive to fix — a `munmap` emission the
library can call (the `pratyarpana` escape hatch from the design
doc, or equivalent) — because library code cannot emit syscalls
directly. The emitter fix and the library fix are separate changes;
the emitter one can land without the other.

### Leak size, checked structurally

Growth doubles capacity, so the abandoned capacities sum to
approximately the final capacity. For 1,000,000 pushes: live block
2^20 × 8 B = 8 MB, abandoned blocks ≈ 8 MB, total footprint
≈ 16 MB ≈ 16 bytes/item. The design doc's "~15.3 bytes per item"
matches total footprint per item; the leaked share is about half
of it, ≈ 8 bytes/item. I measured a 1,000,000-push program at
16.0 MB total, consistent with that bound. (A precise independent
rate from RSS deltas is not available in this sandbox: every
Sutram binary, even hello-world, reports an ~8.5 MB RSS floor I
cannot attribute, so I report the structural bound rather than
pretending to a precise measurement.)

## WS3 — how many `nirmmita` results ESCAPE

Classification rule, stated so it can be re-checked: a site is
classified by what happens to **its own** allocation. (b) = the
allocated value, or a container holding it, is returned from the
enclosing function (`nivartanam var`, or `var` stored into a record
that is itself returned). (c) = the pointer itself is stored
somewhere that outlives the call without being returned (into a
caller-owned container, or at global scope). (a) = everything else:
used locally and dropped — including buffers passed to callees
that write into them but do not keep them, and temporaries passed
directly as arguments. Element copies (`dst[i] = rev[i]`) do NOT
count as storing the pointer; only `X[...] = var` with `var`
itself on the right-hand side does. Every site was classified by
reading the enclosing function at the site; the (b) and (c) lists
below are exhaustive, and the (a) count is the remainder.

### Counts (322 executable sites)

| Class | Sites | Share |
|---|---|---|
| (a) allocated and released inside one function | 313 | 97.2% |
| (b) allocated and RETURNED | 6 | 1.9% |
| (c) allocated and stored beyond scope | 3 | 0.9% |

### The (b) sites — all six are in `lib/`, all are constructors

| Site | What escapes |
|---|---|
| `lib/mala.smlib:16` `mala_nava` | `nivartanam nirmmita(sz)` — direct return |
| `lib/nighantu.smlib:116` `nighantu_srij` | the map block itself, returned |
| `lib/suchi.smlib:55,57` `suchi_srij` | header returned; data block stored into `l[2]` of the returned header |
| `lib/suchi.smlib:390,392` `avali_srij` | header returned; data block stored into `q[2]` of the returned header |

No example and no test program returns an allocation. (One
near-miss checked and rejected: `examples/216_r12_expr.sm`
`eval` allocates a parser-state array and passes it to
`parse_expr`, but returns the *result*, not the array — (a).)

### The (c) sites — all three

| Site | What happens |
|---|---|
| `lib/suchi.smlib:75` `suchi_vardh` | new data block stored into the caller-owned list (`lst[2] = nd`) |
| `lib/suchi.smlib:417` `avali_pravesh` | new data block stored into the caller-owned queue (`qu[2] = nd`) |
| `tests/r56_check/global_pointer.sm:1` | `vitti buf = nirmmita(16)` at top level — a genuine global, read by `fill()` and `mukhya()`; it outlives every call by construction |

### What this decides

**Most are (a) — overwhelmingly.** A region is a clean win for
97.2% of call sites. But the (b) and (c) cases are concentrated
exactly where it matters: the standard library's own constructors
and growth. Every list, map, and queue in every program flows
through those 8 library sites (6 returned + 2 stored). A pure
call-frame region breaks them all: `suchi_srij` allocates in its
own frame, the frame closes on return, and the caller's list
points at released memory. So the classification does NOT say
"regions are a trap" — it says regions work for nearly everything
and the design must solve exactly the constructor/growth case.
That case is small (8 sites) but foundational, and it is where
the R60 design below spends its effort.

## Recommendation (one paragraph, as asked)

A region is usable here, and the numbers say so — 97.2% of
allocations never leave their function — but not as a pure
call-frame region with a single promotion keyword, because the
standard library's constructors and growth (8 sites that every
program depends on) escape by design and growth inside a callee
cannot promote to the caller's region with a word alone; adopt
the region with the escape-routing design in ROUND-60 (frame arena
for the provably-local 97%, a separate never-reset heap arena for
the escaping 3%, routing decided conservatively at compile time
so imprecision costs retention rather than corruption), and fix
the `kosh` emitter leak first since it is a bug today and a
one-place change.

## NOT RUN

- Windows / WSL (no Windows environment here; the `.bss`
  reservation behavior on Windows is unmeasured — see R60).
- Browser automation (no browser component in this round).
- The guard was not re-run: this round made no tree changes.
