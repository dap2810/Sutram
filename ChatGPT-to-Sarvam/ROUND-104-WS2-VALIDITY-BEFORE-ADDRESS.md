# ROUND-104 WS2 — Validity must precede address formation

An implementation rule small enough to apply when writing a new Sutram standard-library function:

> **Check the domain, prove the full byte length or element count fits without overflow, and prove the requested access lies inside the real allocation — before computing an allocation size or memory address.** Checking whether a *wrapped result* is negative or within bounds is too late. If any check fails, return the function's documented failure value without publishing a fake handle, writing memory, or partially modifying existing state.

## Shape 1 — Count times constant stride (8-byte cells)

**WRONG:**
```sutram
vitti bytes = count * 8
yadi (bytes < 0) { prati 0 }
vitti p = nirmmita(bytes)
```

**RIGHT:**
```sutram
yadi (count < 0) { prati 0 }
yadi (count > 1152921504606846975) { prati 0 }
vitti bytes = count * 8
vitti p = nirmmita(bytes)
yadi (p == 0) { prati 0 }
```

The bound is `INT64_MAX / 8` and must occur **before** the multiplication. Adjust a positive header `h` to `(INT64_MAX-h)/8`. Reject negative counts even when their wrapped size is positive. A successful mmap is not a size-overflow proof.

## Shape 2 — Variable dimensions and flat indices

**WRONG:**
```sutram
vitti cells = m * n
yavat (i < cells) { out[i] = 0.0; i = i + 1 }
```

**RIGHT** for `kosh dasham out` whose length is already populated:
```sutram
yadi (m < 0 || n < 0) { prati 0 - 1 }
vitti available = kosh_len(out)
yadi (n != 0) {
    yadi (m > available / n) { prati 0 - 1 }
}
vitti cells = m * n
vitti i = 0
yavat (i < cells) { out[i] = 0.0; i = i + 1 }
```

Validate *each input and output kosh* for the operation, not only `out`; for a matrix product, validate the input shapes `m*n`, `n*p`, and output `m*p` separately. A division against a known nonnegative capacity avoids ever producing an untrusted product. The code uses existing language primitives, not a new import. If either matrix dimension is zero, define whether zero-sized shapes are allowed before applying the rule.

## Shape 3 — Cursor + header + payload (untrusted serialized bytes)

**WRONG:**
```sutram
yadi (pos + 8 + payload > cap) { prati 0 - 1 }
```

**RIGHT:**
```sutram
yadi (pos < 0 || cap < 0 || payload < 0) { prati 0 - 1 }
yadi (pos > cap) { prati 0 - 1 }
yadi (cap - pos < 8) { prati 0 - 1 }
yadi (payload > cap - pos - 8) { prati 0 - 1 }
vitti next = pos + 8 + payload
```

Only after the comparisons may `next` be calculated and memory accessed. The required subtraction is nonnegative because preceding comparisons established its domain. No `pos + 8`-style comparison is valid if the addition might wrap. This is R37's exact failure class in `anukram`.

## Always check the *real* extent

A caller-supplied integer `capacity` is not itself evidence that a raw pointer has that many bytes. For a typed `kosh`, use its actual `kosh_len` (and element type/size). For a raw pointer, the caller must provide a trusted pointer/extent contract or the API is explicitly unsafe. An index check `i < n` does not help if `n` is fabricated. Preserve old state if growth fails; use the failure convention of the function. Use checked multiply (`ganita_janchit_gun(a,b,ok)`) when helpful for variable arithmetic, but **inspect `ok[0]`**: numeric return zero is a valid product.

## What a mechanical gate can and cannot certify

A source gate can detect **patterns that demand review**: computed `nirmmita` sizes with no earlier source-visible upper bound, new formulas, missing failure branches, and addition-based bounds before serialized-data access. It cannot prove pointer provenance, branch dominance, actual buffer extent or API semantics from a regex. R37's `tools/check_alloc_bounds.py` is the current integrated gate; R103's exact-spelling checker should not be installed as a second mandatory gate. A future sound proof requires typed compiler IR and source-to-address dominance/data-flow analysis.

**Status:** documentation/specification delivered. The snippets are illustrative source patterns, **NOT_RUN** as native Sutram tests in Round 104.
