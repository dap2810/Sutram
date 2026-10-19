# Kosh growth-avoidance (R30 WS2)

The compiler-side kosh growth leak is real and unfixed (R29):
`kosh_push` growth allocates a new buffer, copies the old cells, and
never releases the old buffer. The language has no free primitive.
Every growth event retains a superseded buffer forever.

This page documents the harm-reduction pattern that caps the damage.
It does not fix the leak.

## The pattern: reserve up front, clear, reuse

```sutram
kosh v[100000]          # capacity reserved up front: the max ever needed
yavat (round < 50) {
    vitti i = 0
    yavat (i < 100000) {
        kosh_push(v, i)  # never grows: cap is already 100000
        i = i + 1
    }
    ... use v ...
    kosh_clear(v)       # len -> 0, capacity RETAINED
}
```

Rules:

1. **Reserve the maximum.** Declare the kosh with the largest
   capacity it will ever need. If it never grows, no superseded
   buffer ever exists.
2. **Reuse one kosh across rounds.** Declare it once, outside the
   loop. A fresh kosh per round (even with `kosh_clear`) still pays
   one allocation per round — and if it grows, one leak per round.
3. **`kosh_clear` retains capacity.** After `kosh_clear`, `kosh_len`
   is 0 and `kosh_cap` is unchanged. The buffer is reused, not freed.
   (Clear is not erase: old bytes can remain in the allocation.)

## Why there is no fill-helper function

A helper taking a kosh parameter cannot push to it: the compiler
rejects `kosh_push` on a kosh parameter at compile time
(`Sutram Error: kosh tark par kosh_push asamarthit`,
see `examples/120_t18_kosh_param_mismatch.sm`). The reason is
sound: growth replaces the callee's pointer, which would not update
the caller's pointer-by-value view, leaving the caller with a stale
kosh. A function that takes a kosh may only READ it (indexing,
`kosh_len`, `kosh_cap`) — as `kalana`'s `pravan` does.

So the reuse helper is the pattern itself, not a function. Do not
try to work around the rejection by passing a raw pointer to the
kosh storage: raw addresses into a collection are not stable across
growth (see `docs/MEMORY-MODEL.md` §3).

## Measured effect

`tools/kosh_reuse_measure.py`, 50 rounds x 100000 pushes, same work
both ways (measured 2026-10-16, this machine):

| Pattern | Peak RSS | Over baseline |
|---|---|---|
| Baseline (empty program) | 8.5 MB | — |
| A. Fresh `kosh v[4]` per round, grown to 100000 | 91.0 MB | +82.5 MB |
| B. One `kosh v[100000]`, cleared and reused | 8.5 MB | +0.0 MB |

Pattern A retains ~2x the final buffer per round (growth doubles from
4, every superseded buffer kept): 50 x 2 x 100000 x 8 bytes ≈ 80 MB,
matching the measurement. Pattern B retains one 0.8 MB allocation,
below the measurement noise — retention is flat in the round count.

## What this does NOT fix

- The growth path still leaks for any kosh that does grow.
- The reused kosh's one allocation is retained for the process
  lifetime (there is no free). Reuse caps retention at one
  allocation; it does not reclaim it.
- `kosh_clear` does not erase contents and does not shrink capacity.

The compiler-side fix remains: release (munmap) the old buffer in
the growth path, or add a free primitive. Until then, reserve +
reuse is the way to keep kosh retention bounded.

## Test

`tests/stdlib/kosh_reuse.sm` demonstrates the pattern: one kosh,
capacity 5, three rounds of fill / verify / clear, with `kosh_cap`
constant throughout.
