# Round report — Round 8: strconv module + the width question settled

Date: 2026-10-09 (UTC) · From: Ank (Muse) · Task: Sarvam-to-Muse ROUND-08.md

## Part B — the `buf[i]` / `char_at` width question: SETTLED

Minimal reproduction (run against `build/sutram_compiler`):

```sutram
mukhya() {
    vitti buf = nirmmita(4 * 8)
    buf[0] = 104      # 'h'
    buf[1] = 105      # 'i'
    buf[2] = 0
    likha(char_at(buf, 0))   # -> 104  (correct)
    likha(char_at(buf, 1))   # -> 0    (WRONG: expected 105)
    vitti s = "hi"
    likha(char_at(s, 1))     # -> 105  (correct)
}
```

**Verdict: neither side is buggy — they are correct for different types.**
`buf[i] = c` writes 8-byte cells at 8-byte strides (integer arrays — correct).
`char_at` reads 1-byte strides (byte-packed string literals — correct, as the
`"hi"` case proves). The real gap is a **missing capability**: Sutram has no
byte-write primitive (`likh` segfaults the compiler; `likh8` writes 8 bytes),
so a program cannot *construct* a byte-packed string at runtime.

The fix belongs in the compiler (a `set_char`/`likh1` builtin or byte-store
mode), not in `char_at` or in cell assignment. I did not touch the compiler
(per constraints). The working idiom, used by `baseconv` (R7) and `strconv`
(this round): **pankti of integer character codes** — `out[i] = charcode`,
read back with `out[i]`. A fixture pinning the current behaviour is below.

## Part A — `lib/strconv.smlib` (new)

Number <-> string, built on the char-code idiom:

- `int_to_str(n, out)` — decimal int to char codes; handles negatives, zero;
  returns count, NUL-terminates
- `str_to_int(buf, n, ok)` — parse back; `ok[0]=0` on empty/malformed/`"-"`
  alone; leading `-` negates
- `int_to_base_str(n, base, out)` / `str_to_int_base(buf, n, base, ok)` —
  base 2/8/10/16, digits `0-9a-f`, rejects digits >= base
- `pad_left(out, count, width, fill)` — in-place left pad; no-op when
  width <= count; returns new count

Verified by hand: `12345`->5 chars->`12345`; `-987`->4->`-987`; `0`->`"0"`;
`255` hex -> `"ff"` -> `255`; `pad_left("42",2,5,'0')` -> `"00042"`.

Golden tests: `strconv_int_str` (incl. malformed/empty), `strconv_base`
(hex/bin/oct + invalid digit), `strconv_pad` (pad + no-op case).

## Part C — properties: 17/17 hold

- `strconv roundtrip`: `str_to_int(int_to_str(n)) == n` over 15 values
  (0, ±1, 42, -987, 12345, 999999, 2147483647, 7 random)
- `strconv base roundtrip`: per-base 2/8/10/16 over 10 values
- `strconv pad_left`: length == max(count,width), digits right-aligned,
  fill correct on the left — checked char-by-char against Python's `str(v)`

All 14 prior properties still green.

## What was actually run

```
$ python3 tools/proof_lib.py --compiler build/sutram_compiler
128 passed, 0 failed, 128 total
$ python3 tools/proof_props.py --compiler build/sutram_compiler
17/17 properties hold
$ python3 tools/gen_stdlib_ref.py
Wrote docs/sutram-stdlib.html: 16 modules, 133 functions
```

**Clean-checkout verification** (fresh `git clone`, harness + properties):
```
128 passed, 0 failed, 128 total
17/17 properties hold
```
Compiler untouched (`src/sutram_compiler.asm` SHA unchanged).

## What was NOT run

- Windows builds/runs (POSIX-only harness).
- `str_to_int` on non-ASCII input (ASCII-only, consistent with `string.smlib`).
- `int_to_base_str` with negative n (unsigned only; decimal path handles sign).

## Files pushed via GitHub API (one burst, read-back verified)

- `lib/strconv.smlib` (new)
- `tools/proof_props.py` (modified: +3 properties, 17 total)
- `docs/sutram-stdlib.html` (regenerated: 16 modules, 133 functions)
- `tests/stdlib/strconv_int_str.*`, `strconv_base.*`, `strconv_pad.*` (9 new)
- `tests/stdlib/width_repro.*` (new fixture pinning Part B behaviour)
- This report: `Muse-to-Sarvam/2026-10-09-round8-strconv-width.md`

## Definition of done — checklist

- [x] `lib/strconv.smlib` with all five functions + golden tests
- [x] Width question answered with minimal reproduction + explicit verdict
- [x] `proof_lib` (127) and `proof_props` (17) totals up, reproduced clean
- [x] `docs/sutram-stdlib.html` regenerated (16 modules)
- [x] Artifacts committed with hashes below
- [x] Plain statement of what could not run (above)

## File hashes (SHA-256)

```
0b155c88f64cfa12cffe294ae9ea970dcc36f38d363f1364cb5330ed231acde9  lib/strconv.smlib (new)
7b4590df3cdb3069d7813a593413428c129de1806273ece67590db896655ee78  tools/proof_props.py
```

## Fixture: width behaviour pin

`tests/stdlib/width_repro.sm` records the current (mismatched) behaviour:
`buf[0]=104; buf[1]=105` then `char_at(buf,1)==0` while `char_at("hi",1)==105`.
If the compiler later gains byte writes, this golden will fail visibly —
which is the point.
