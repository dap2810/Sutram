# R23-03 — WS3: slices

**Same branch and commit (`705742c2`, PR #62).** Environment: **Linux**, and **Wine** for the example and
the bounds failure.

## What works

```
prakriya yog(vibhag s) {                 # a slice parameter
    vitti t = 0
    chakra i = 0 tak pankti_len(s) - 1 {
        t = t + s[i]
    }
    prati t
}
likha(yog(a[2:5]))     # elements 2, 3, 4 of a mala: no copy
vitti s = a[1:7]       # s[0] is a[1]; s[0] = 9 writes a[1]
likha(yog(s[2:]))      # a slice of a slice; a[lo:], a[:hi], a[:]
likha(yog(a))          # a whole mala (or integer kosh) passes as a[:]
```

- **The bases:** a `mala`, an integer `kosh`, or another slice.
- **A slice is a view, so nothing is copied.** It is a (pointer, length) pair: a 16-byte descriptor in a
  frame slot of the function that makes it. Passing it to a function passes one qword, the descriptor's
  address. That is the one-qword ABI the compiler already uses for everything.
- **Checked twice at run time, with the existing bounds diagnostic (exit 1):**
  1. when it is made: `0 <= lo <= hi <= length of the base`. This check is unsigned, so a negative bound
     fails too;
  2. when it is indexed: `s[i]` and `s[i] = v` are checked against the slice's own length, not the
     array's.
- **`pankti_len(s)` is the slice's length,** for a slice variable or a slice expression.
- **`vibhag` is the slice-parameter keyword:** `विभाग` in Devanagari, and a word in each of the eleven
  `lang/*.lang` packs (one line each), so `फलन योग(विभाग s)` works with `--lang hindi`. I tested it.
- **A variable is a slice when it is declared from one** (`vitti s = a[1:3]`, `vitti t = s`) or is a
  `vibhag` parameter.

**Proof:** `examples/248_r23_slices.sm`. It reads and writes through slices, takes slices of slices,
passes a `kosh` slice, and has a recursive sum that splits its slice in halves, so each call takes part of
the array.

## Errors: two new messages, in all eleven packs

| Case | Message (default) |
|---|---|
| slicing a raw pointer (an untyped parameter, a `nirmmita` result) or a `kosh dasham` | `vibhag: mala, kosh va vibhag apekshita` |
| anything but a slice, `mala` or `kosh` passed to a `vibhag` parameter | the same |
| `prati s` of a slice | `vibhag prakriyayah na pratyarpaniyah` ("a slice must not be returned from a prakriya") |

**The new pack lines are mine (`r23_msg_slice_base`, `r23_msg_slice_return`).** For Sanskrit, Hindi and
Gujarati they need the owner's eye like any new line. For the other eight they are DRAFT, like the rest of
those packs. `sandesh --check` passes, and my R21 structural checker reports 1,430 rows with 0 hard
violations.

## What I did not do, and why

- **A slice cannot outlive the function that made it.** Its descriptor lives in that frame. That is why
  returning one is an error. A heap descriptor would cost one `mmap` page per slice, which is the
  allocator `mala` uses, and that is too dear for a value made in a loop.
- **A slice made at one place in a loop is the same slice each time round.** The next iteration remakes it,
  so keeping slices from different iterations in a `mala` keeps copies of the last one. Passing and using
  them, which is the normal case and what the example does, is unaffected. Recursion is also fine: each
  activation has its own frame.
- **No slices of a `kosh dasham`.** Its elements are binary64; this version is integers only.
- **A `kosh` that grows after it was sliced leaves the slice pointing at the old storage.**
- **Raw pointers cannot be sliced,** because their length is unknown. An untyped parameter must be
  declared `vibhag` to be sliced. The library's `(a, n)` functions keep working as they are. Moving them
  to `vibhag` parameters is the composability you asked about, but it is a library change I did not make
  this round.
