# What you will assume wrongly, coming from another language

A page for the top of the reference. Every line below was run on v278
(the current compiler) and checked against `docs/LANGUAGE-REFERENCE.md`
as it stands on main. Items marked STATED are already in the reference
(they belong on this page anyway, so the page stands alone); items
marked NOT STATED are the gaps, each with the sentence that closes it.
This page supersedes the ten-item page delivered in Round 82: the
`tak` verdict there is corrected (see item 1), and three new items
(13–15) were found this round.

## 1. `tak` is INCLUSIVE — STATED (§6a)

`chakra i = 0 tak 3` runs four times: 0, 1, 2, 3. The endpoint is
inclusive, exactly like `arabhya … paryantam`.

Correction to Round 82, owned: Round 82 called this a gap ("only
implied"). That was overstated. §6a already prints the exact stdout
for the `tak` form — 0, 1, 2, 3, 4 for `chakra i = 0 tak 4` — and calls
the endpoints inclusive. The gap is closed; the sentence above is
the page's canonical form, not a new claim.

## 2. `nirmmita(n)` counts BYTES, `p[i]` counts 8-byte qwords — STATED (§6c)

`nirmmita(64)` gives 64 bytes, which is 8 cells, not 64. `p[i]` moves
8 bytes per step: `p[1]` is the second cell, 8 bytes past `p[0]`.

## 3. Integer division truncates toward ZERO — NOT STATED (§3a)

`-7 / 2` is `-3`, where Python gives `-4`. `-7 % 2` is `-1`: the
remainder takes the dividend's sign. §3a covers division by zero and
by −1, but never says which way division rounds. Sentence for §3a:
"Integer `/` truncates toward zero and `%` takes the dividend's
sign: `-7 / 2` is `-3`, `-7 % 2` is `-1`."

## 4. `vitti a = k` makes two names for one buffer — and they diverge — STATED (§16, v278)

`vitti a = k` (or `a = k`) compiles and makes `a` a bounds-checked
view of `k`'s buffer *as it is now*, with `k`'s length *as it is now*.
If `k` grows and the cells move, only the name pushed through follows
them; the other name stays on the old buffer with the old length.
Whether the cells move depends on what else was allocated: on Linux
a `kosh` that is the newest block grows in place (the two names stay
one); on Windows it always moves — so the same program can print
different results on the two systems. Nothing is ever freed, so the
old buffer is valid memory: a stale read is a wrong value, not a
crash. Rule: keep one name per `kosh`; copy values out, not the
`kosh`.

One sharpening §16 could still take: it says "with the old length",
but not the sharpest form of it — `a[1]` faults even when nothing
relocates, if `k` had length 1 when the alias was made. The length
freezes at alias time; only a push *through that name* updates it.

## 5. String `==` compares ADDRESSES, not contents — NOT STATED

`s == t` is false for two variables holding `"hello"`, and
`s == "hello"` is false too. Use `vartani_tul` for contents.

## 6. Indexing a string reads QWORDS, not bytes — NOT STATED

`s[0]` on `"hello"` is not 104. It reads a whole 8-byte cell (and a
string is not a `(buf, n)` buffer at all). Use `akshar(s, i)` for
the byte: `akshar(s, 0)` is 104, `akshar(s, 1)` is 101.

## 7. `dasham` division by zero does NOT stop the program — NOT STATED

`1.0 / 0.0` is +inf, silently — the program goes on, and the printer
renders it as the minimum value. `0.0 / 0.0` is 0, not NaN. Only
integer division by zero stops the program (§3a).

## 8. Assignment is NOT an expression — NOT STATED

`x = (y = 5)` is refused at parse time. An assignment is a statement;
it has no value to nest.

## 9. `vitti` is NOT a parameter type — NOT STATED

Integer parameters are untyped (`prakriya f(n)`); `dasham` is a
parameter type, `vitti` is not. Writing `prakriya f(vitti n)` is a
parse refusal.

## 10. `kosh_push` on a `kosh` PARAMETER is refused — NOT STATED

A `kosh` parameter can be read and indexed within its capacity, but
it cannot be grown: `kosh_push` on it is refused
(`kosh-tarke kosh_push asamarthitam`). Grow in the caller.

## 11. An uninitialized `vitti` reads 0 — NOT STATED

Even on a second call, after another call wrote 99 into the same
name. Locals are genuinely zeroed, unlike C. Do not rely on it for
meaning — but do not fear garbage either.

## 12. Trailing statements after an INDENTED `mukhya` EXECUTE — NOT STATED

After a braced `mukhya`, anything further is a compile error. After
an indented `mukhya`, trailing top-level statements run. The two
forms do not behave the same at the end of the file.

## 13. A negative `kosh` index FAULTS — it does not wrap — NOT STATED (new this round)

`k[-1]` is not the last element. It stops the program with
`mala ank seema atikram`, exit 1. There is no Python-style negative
indexing; out of range in either direction is a fault.

## 14. `likha(k)` prints the `kosh`'s ADDRESS, not its elements — NOT STATED (new this round)

`likha(k)` prints a large number — the buffer's address. The
reference's "Printing a string variable" section covers string
variables only; a `kosh` behaves the same way and is not mentioned.
To print elements, print them one by one (`k[i]` in a loop).

## 15. `kosh == kosh` compares ADDRESSES, not contents — NOT STATED (new this round)

Two `kosh` holding identical elements compare unequal: `a == b` is
false, `a != b` is true. There is no builtin that compares contents;
compare lengths with `kosh_len`, then elements.

## Already stated elsewhere, so not repeated above

- A `kosh` made inside a `mandapa` lives as long as the block (§19,
  v278): after the block it is gone, and a `prakriya` that receives
  it stops with `E_KOSH_MANDAPA` (examples 286–287).
- Empty `kosh_pop` / `kosh_peek` / `kosh_dequeue` abort with their
  own diagnostics and exit 1 (§16).
- String `+` concatenates: `"a" + "b"` is `"ab"`.
- Redeclaring a `vitti` is refused, in the same block and in a
  nested one (`'x' purvam eva ghoshitam`).
