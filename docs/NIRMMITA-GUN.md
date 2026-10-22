# `nirmmita_gun(count, size)`: the checked allocation (R39)

```
vitti cells = nirmmita_gun(n, 8)     # n cells of 8 bytes, or 0
```

It returns `count × size` bytes from `nirmmita`, or **0** in each of these cases:

| Case | Result |
|---|---|
| `count < 0` | 0 |
| `size <= 0` | 0 |
| `count × size` greater than 2⁶³ − 1 | 0 |
| `count == 0` | 0 (the same as `nirmmita(0)`) |
| the system refuses the allocation | 0 (the same as `nirmmita`) |

## Why it exists

The library allocates by multiplying a count by an element size, then calling `nirmmita`. If the product
wraps, the allocation is small and the writes that follow run past it. Rounds R35–R37 put a bound on the count
before every multiply. Two checkers now look for those bounds: `tools/check_alloc_bounds.py`, and ChatGPT's
R103 allowlist. Both check the source, and both have limits that R38 and R39 measured.

`nirmmita_gun` moves the multiply into the code the compiler emits. The check (`imul`, then the overflow flag)
sits next to the allocation, so a wrapped size never reaches `mmap`, whatever the caller passed. Code that uses
it needs no bound and no exemption.

## What it changes

- **A program that does not call it compiles to the same bytes as before.** The evidence is
  `Claude-to-Sarvam/evidence-r39/`: 567 programs, 0 differ.
- **It is one builtin with two arguments.** A call with the wrong number of arguments is refused, the same as
  for every builtin.
- **`--fail-alloc N` counts it like any other allocation.**
- **It works on Linux and in a PE program.** The Windows run was under Wine, not real Windows.
- **`tools/check_layers.py` treats it as an allocator.** **`tools/check_alloc_bounds.py` counts it and does not
  ask it for a bound.**
- **The library does not use it yet.** Moving the 26 computed sites to it changes those programs' bytes, so that
  is a separate, reviewable step.

Source: `src/r39_nirmgun.inc`. Test: `tests/r39/test_nirmgun.py`.
