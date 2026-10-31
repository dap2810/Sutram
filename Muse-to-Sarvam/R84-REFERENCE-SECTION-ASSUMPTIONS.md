# What you will assume wrongly, coming from another language

A section for the top of the reference, in the reference's voice. Each
entry gives the assumption, what Sutram actually does, and one line
of code showing the difference. Every line was run on v278 (see the
Round 84 report: 19/19 verified). Entries marked STATED are already
in the reference; they are collected here so a student finds them
in one place, before they are confused. Entries marked NOT STATED
name the section that should carry the sentence.

## The five that bite first

**You assume `tak` means "up to but not including", like Python's
`range`.** Sutram's endpoint is inclusive. — STATED (§6a)

`chakra i = 0 tak 3` → runs four times: 0, 1, 2, 3.

**You assume `nirmmita(64)` gives 64 cells.** It gives 64 bytes,
which is 8 cells; `p[i]` moves 8 bytes per step. — STATED (§6c)

`vitti p = nirmmita(64)` → `p[7]` is the last cell in the block.

**You assume `-7 / 2` is `-4`, like Python.** Integer division
truncates toward zero, and the remainder takes the dividend's
sign. — NOT STATED (§3a covers division by zero and by −1, never
the rounding direction)

`-7 / 2` → `-3`, and `-7 % 2` → `-1`.

**You assume `vitti a = k` copies the `kosh`.** It makes `a` a
second name for the same buffer, as it is now, with the length as
it is now. If `k` grows and the cells move, only the name pushed
through follows them; the other name stays on the old buffer with
the old length. On Linux a `kosh` that is the newest block grows
in place (the two names stay one); on Windows it always moves.
Nothing is ever freed, so a stale read is a wrong value, not a
crash. — STATED (§16, v278)

`vitti a = k` (then an allocation, a push, and `k[0] = 99`) →
`a[0]` is still 41.

**You assume `"b" < "a"` is false, because strings compare
lexicographically.** String comparison compares addresses, not
contents — the order is declaration order, not alphabetical order.
— NOT STATED (new this round; the reference says nothing about
string ordering)

`vitti s = "b"; vitti t = "a"` → `s < t` is true.

## The rest

**You assume `s == t` compares contents.** It compares addresses:
two variables holding `"hello"` compare unequal. Use `vartani_tul`
for contents. — NOT STATED

`s == t` (both `"hello"`) → false.

**You assume `s[0]` is the first byte.** Indexing a string reads a
whole 8-byte cell, and a string is not a `(buf, n)` buffer at all.
Use `akshar(s, i)` for the byte. — NOT STATED

`akshar(s, 0)` on `"hello"` → 104; `s[0]` is not 104.

**You assume dividing a `dasham` by zero stops the program.**
Only integer division by zero stops it. `1.0 / 0.0` is +inf,
silently, and the program goes on; `0.0 / 0.0` is 0, not NaN. —
NOT STATED

`1.0 / 0.0` → +inf, and the next line still runs.

**You assume an assignment has a value.** It is a statement, not
an expression, and cannot be nested. — NOT STATED

`x = (y = 5)` → refused at parse time.

**You assume `vitti` is a parameter type.** Integer parameters are
untyped; `dasham` is a parameter type, `vitti` is not. — NOT STATED

`prakriya f(vitti n)` → refused at parse time.

**You assume a `kosh` parameter can be grown.** It can be read
and indexed within its capacity, but not grown: `kosh_push` on it
is refused. Grow in the caller. — NOT STATED

`kosh_push(k, 1)` inside `prakriya f(kosh k)` → refused
(`kosh-tarke kosh_push asamarthitam`).

**You assume an uninitialized `vitti` holds garbage, like C.**
Locals are genuinely zeroed — even on a second call, after another
call wrote 99 into the same name. — NOT STATED

`vitti x` (no initializer) → `likha(x)` prints 0, every call.

**You assume trailing statements after `mukhya` are dead or an
error, whichever form `mukhya` takes.** After a braced `mukhya`
they are a compile error; after an indented `mukhya` they execute.
— NOT STATED

`likha(8)` written after an indented `mukhya` → prints 8.

**You assume `k[-1]` is the last element, like Python.** There is
no negative indexing; out of range in either direction is a fault.
— NOT STATED

`k[-1]` → stops with `mala ank seema atikram`, exit 1.

**You assume `likha(k)` prints the `kosh`'s elements.** It prints
the buffer's address. The reference's "Printing a string variable"
section covers string variables only; a `kosh` behaves the same
way. — NOT STATED

`likha(k)` → a large number (the address), not 10, 20.

**You assume `a == b` compares two `kosh` element by element.**
It compares addresses: identical contents compare unequal. There
is no builtin that compares contents; compare lengths with
`kosh_len`, then elements. — NOT STATED

`a == b` (both holding 7) → false.

**You assume `chakra j = 5 tak 1` is empty, like Python's
`range(5, 1)`.** A `tak` loop counts down when the start is above
the end. — STATED (reference line 317, with the ascending example
beside it)

`chakra j = 5 tak 1` → 5, 4, 3, 2, 1.

**You assume the loop variable survives the loop, like Python.**
It does not: `i` is scoped to the loop, and using it afterwards is
a compile error. — NOT STATED (new this round)

`likha(i)` after the loop → refused (`'i' … not visible outside`).
