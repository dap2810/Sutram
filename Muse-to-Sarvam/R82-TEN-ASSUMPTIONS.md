# Ten things a programmer from another language will get wrong in Sutram

*For the top of `docs/LANGUAGE-REFERENCE.md`. Every item below was
verified on compiler v277. Where the reference already states the
behaviour, it says so — those are not on this list.*

## 1. `tak` is INCLUSIVE

You write `chakra i = 0 tak 3` expecting three runs (0, 1, 2), as in
most languages' `range`. You get four.

```
chakra i = 0 tak 3 { likha(i) }    # prints: 0  1  2  3
```

`tak` includes its endpoint, ascending and descending alike. The
consequence that bites: `chakra i = 0 tak n` over an `n`-element
array runs `n + 1` times and overruns by one. For `n` elements,
write `chakra i = 0 tak n - 1`, or loop while `i < n`.

## 2. Integer division truncates toward ZERO

You come from Python and expect `-7 / 2` to be `-4` (floor). It is
`-3`. The remainder follows the dividend, not the divisor.

```
likha(0 - 7 / 2)     # prints: -3    (Python: -4)
likha(7 / (0 - 2))   # prints: -3
likha((0 - 7) % 2)   # prints: -1    (Python: +1)
```

This is C/Java behaviour. The reference's arithmetic section covers
division by zero and by −1, but never states the truncation rule.

## 3. `==` on strings compares ADDRESSES, not contents

You write `yadi (s == "hello")` expecting a content comparison. It
is false — even when `s` holds exactly "hello", and even when two
variables hold the same text.

```
vitti s = "hello"
vitti t = "hello"
yadi (s == t) { likha(1) } anya { likha(0) }       # prints: 0
yadi (s == "hello") { likha(1) } anya { likha(0) } # prints: 0
```

A string value is an address. To compare contents, use
`vartani_tul`. (Related, and now stated in the reference: `likha`
of a string *variable* prints its address, not its text — use
`shabda(s)` for the text.)

## 4. Indexing a string reads QWORDS, not bytes

You write `s[0]` expecting `'h'` (104). You get a large number —
the 8 bytes at that address as one cell, and strings are not laid
out as plain cell arrays, so it is not even the first eight bytes
in any useful sense.

```
vitti s = "hello"
likha(s[0])          # prints: -8554587013629844120   (not 104)
```

To read byte `i` of a string, use `akshar(s, i)` — `akshar(s, 0)`
is 104, `akshar(s, 1)` is 101. The same warning applies to
functions taking `(buf, n)`: they read qword cells, so a string
literal is not a buffer for them — build a cell array, or use the
string builtins.

## 5. Dasham division by zero does NOT stop the program

You read "dividing by zero stops the program" and assume it covers
`1.0 / 0.0`. It does not — that sentence is about integers.
Dasham division follows IEEE: it yields infinity, silently.

```
dasham inf = 1.0 / 0.0
yadi (inf > 0) { likha(1) }   # prints: 1 — it is +inf
likha(inf)                     # prints: -9223372036854.775808
```

The misprint is the known printer limit (admitted in the
reference: `likha` of a large `dasham` prints the smallest
`vitti` rendering, whatever the value). And `0.0 / 0.0` is 0, not
NaN. Integer `/` and `%` by zero do stop the program, with
`E_SHUNYA_BHAJAN` and the line.

## 6. Assignment is NOT an expression

You write `x = (y = 5)`, or `yadi ((a = b) == 0)`, as in C. It
fails to parse. Assignment is a statement only: it cannot nest,
cannot appear inside an expression, and cannot be chained.

```
x = (y = 5)     # parse error
```

Write the assignments as separate statements, then use the
variables.

## 7. `vitti` is NOT a parameter type

You write `prakriya f(vitti x)`, following the local-declaration
form. It fails to parse. Integer parameters are untyped; only
`dasham` (and container types) appear in a parameter list.

```
prakriya f(vitti x) { nivartanam x + 1 }   # parse error
prakriya f(x) { nivartanam x + 1 }         # this is the form
prakriya g(dasham x) { nivartanam x }      # dasham IS a type here
```

## 8. A `kosh` passed as a parameter cannot be GROWN

You pass a `kosh` to a function and call `kosh_push` on it,
expecting the caller's `kosh` to grow. It is refused at compile
time: `kosh-tarke kosh_push asamarthitam`.

```
prakriya grow(kosh k) {
    kosh_push(k, 7)          # refused: push on a parameter
    nivartanam kosh_len(k)
}
```

Reading and writing elements within capacity works (`k[i]`,
`kosh_len(k)`); only growing is refused. Grow the `kosh` in the
caller, or pre-allocate capacity and write by index.

## 9. An uninitialized `vitti` reads 0

You come from C and expect garbage in an uninitialized local. You
get 0 — and still 0 on a second call, after another call wrote 99
into the same stack space. Locals are zeroed.

```
prakriya f() {
    vitti x
    likha(x)      # prints: 0, on the first call and on the second
    x = 99
    nivartanam 0
}
```

Do not rely on it for logic the reader cannot see — initialize
anyway — but do not expect garbage either.

## 10. Trailing statements after an indented `mukhya` EXECUTE

You write code after `mukhya`, expecting it to be dead code or an
error. After an *indented* `mukhya`, it runs. After a *braced*
`mukhya`, the same code is a compile error.

```
mukhya()
    likha("inside")
likha("trailing")     # prints too: inside, trailing

mukhya() {
    likha("inside")
}
likha("trailing")     # compile error
```

If your program has a brace-less `mukhya`, everything after it
in the file is part of the program. Put a braced `mukhya` last,
or keep all code inside it.

---

*Already stated in the reference, so not listed above:
`nirmmita(n)` counts bytes while `p[i]` counts 8-byte cells (§6c,
titled exactly that); `likha` of a string variable prints its
address (its own section); the `mukhya`-versus-`prakriya` brace
inconsistency (documented with the "always use braces" advice);
and the integer arithmetic policy — runtime wrap, written-number
refusal, division-by-zero stop (§3a). `&&` and `||` short-circuit,
as expected.*
