# ROUND-75 — the nested-store gap (disproven), the fourth gap (found), the library check

Base: origin/main `020879a3` (compiler v272).
No tree changes. All probes compiled and run
on v272.

## WS1 — the nested-store gap: DISPROVEN

ChatGPT's report — the store check only
inspects root statements — does not survive
contact with the language, because Sutram has
no assignment-expressions:

1. `out = (m[0] = buf) + 1` — **does not
   parse** (grammar error, not a check miss).
   Assignment is a statement, never a value.
2. `yadi (m[0] = buf) > 0` — **does not
   parse** (assignment in a condition).
3. `likha(m[0] = buf)` — **does not parse**
   (a store as an argument).
4. `m[0] = buf[0]` — **compiles, prints 42**
   (a DATA copy, allowed as required).
5. `k[i] = buf` with variable `i` —
   **refused** (E_SCRATCH_ESCAPE). The check
   is index-insensitive; a variable index does
   not hide the store.

And the shapes the brief's five do not cover
— the genuinely nested ones — are all
refused too: a store inside an `yadi` inside
a `mandapa`, inside a `yavat` inside a
`mandapa`, and inside a nested `mandapa`
(all E_SCRATCH_ESCAPE). The check walks
nested blocks. There is no nested-store gap
in any form the language can write. No
missed shape exists here to corrupt memory
at run time, so no corruption demo applies.

The remaining escape family is the one from
R74 (globals + calls as conduits), not
nesting.

## WS2 — the fourth gap: size arithmetic overflow

### What the size domain actually does

| Size | Compiles? | Runtime |
|---|---|---|
| `nirmmita(0)` | yes | returns **0** (NULL); untouched, harmless; any read/write faults (SIGSEGV, exit 139, no diagnostic) |
| `nirmmita(1)` + 8-byte write | yes | harmless: the bump rounds to a **16-byte** slot, so the 8-byte write stays inside it; writes past 16 bytes would corrupt silently (C-like) |
| negative at run time (`0 - 8`) | yes | returns **0**; same fail-stop-on-use as zero |
| `nirmmita(-1)` (literal) | yes (as Sarvam confirmed) | returns **0**; same as above |
| huge (`2^63` bytes) | yes | returns **0** — the allocator refuses beyond the arena rather than jumping |
| **wrapped small-positive** (`(2^44 + 8) × 1024 × 1024`) | yes | **silent adjacent corruption (below)** |

### The gap, proven

`n = 17592186044424` (2^44 + 8);
`b = nirmmita(n * 1024 * 1024)`. The product
is 2^64 + 8 MB, which wraps in 64-bit
arithmetic to exactly 8 MB. The allocator,
correctly by its contract, hands out an 8 MB
buffer. The program, believing it has ~2^64
bytes, writes at cell 1048576 (offset 8 MB):
`b[1048576] = 55`. The next allocation `c`
sits exactly 8 MB after `b` (addresses
verified: 8,388,608 apart), and `c[0]` reads
**55** — the write silently corrupted the
adjacent buffer. No fault, no diagnostic.

This is the fourth gap, and its shape matters:
it is **not** an allocator bug (the allocator
bounds-checks huge requests to NULL and
returns NULL for 0/negative — fail-stop).
It is **unchecked size arithmetic**: the
compiler computes sizes in wrapping 64-bit,
so a huge intended size can wrap to a small
allocated size, and nothing downstream can
tell. The fix direction is checked or
saturating size arithmetic (the R26–R28
checked/saturating work, applied to size
expressions — saturation would pin the size
to huge, the allocator would return NULL,
and the failure would be fail-stop instead of
silent). Constant-foldable cases (a literal
`n` whose product overflows) are even
diagnosable at compile time.

The other size-domain outcomes are not gaps:
zero/negative/huge fail stop (loudly, if
without a message), and the 1-byte case is
absorbed by alignment rounding.

## WS3 — the library check: the block CAN be used with the library

Counts first, with rules stated (Sarvam's
"371 write sites" does not reproduce under
either natural rule on this tree: index/field
writes in `lib/` = **265**; all assignments =
918; functions = **305**, matching).
The audit below uses the 265 memory writes.

Two readings of "called inside a `mandapa`",
both answered:

**(a) If a lib function's own body were wrapped
in a `mandapa`: 6 of 305 refused** (strict
rule: returning a fresh block, or storing a
fresh block itself — not a read from it —
into memory): `avali_pravesh`, `avali_srij`,
`nighantu_srij`, `nighantu_vardh`,
`suchi_srij`, `suchi_vardh`. All are
constructors/growth functions — persistent
allocation by design, correctly refused if
wrapped. Wrapping a constructor in a
`mandapa` is a category error, not a false
positive.

**(b) If a lib function is called FROM inside
a `mandapa` with a scratch argument: 15
retaining + 1 pass-through = 16 of 305
(5%) need care; the other ~289 are safe**
(they read args, compute numbers, copy data,
or write data into caller buffers — all
fine, as the data-copy principle allows):

- `suchi_khip`, `suchi_sangrah`,
  `suchi_nivesh`, `avali_pravesh` — store an
  arbitrary value (including a pointer) into
  a persistent container.
- `nighantu_khip` — stores its VALUE into
  the table. Nuance: its KEY is safe —
  `nighantu_koshtha_likh` copies key BYTES
  into the slot and never stores the key
  pointer — so scratch keys are fine, scratch
  values are not.
- `phal_siddhi`, `phal_se_siddhi`, and the
  eight `phal_janchit_*` writers — store `v`
  into the caller's result buffer.
- `phal_mulya_va` — pass-through: returns
  `def` when the result is a failure, so a
  scratch default escapes through the return
  (needs a lib summary; the check sees
  through direct calls but lib summaries are
  K1 work).

Probed live: `suchi_khip(l, b)` with `b`
scratch, called from a `mandapa`, **compiles**
and the list holds the scratch pointer after
the block (`h[0]` reads 42) — the lib-call
hole is the R74 call hole, not a new one.
The check as built refuses builtin retaining
calls (`kosh_push`) but has no summaries for
lib functions, so these 16 are live holes
when called with scratch pointers.

**Verdict: "most of them" is wrong.** The
block works with ~95% of the library as-is.
The contract surface is the 16-function
retaining/pass-through list above — those
need summaries (or a documented "do not pass
scratch pointers" rule) before `mandapa`
code calls them with pointers. Everything
else — including the formatters, the
splitters, the math, and the map's key path
— is already safe.

## NOT RUN

- Windows / WSL: no Windows component in this round.
- Browser automation: no browser component in this round.
- Implementation: no code was changed; the
  size-arithmetic fix and the 16 lib summaries
  belong to their owners' briefs.
