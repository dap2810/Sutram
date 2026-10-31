# What you will assume wrongly, coming from another language

A section for the top of the reference, in the reference's voice.
Each entry gives the assumption, what Sutram actually does, and
one line of code with what it actually prints. Every line was run
on v279 (see the Round 86 report: 26/26 verified, and the Round
87 report for the rewritten `nirmmita` entry, also verified on
v279). Entries marked
STATED are already in the reference; they are collected here so a
student finds them in one place, before they are confused. Entries
marked NOT STATED name the section that should carry the sentence.
This is the single final version, replacing the Round 84, Round
85, and Round 86 drafts (the only change from Round 86 is the
`nirmmita` entry).
85 drafts.

## The five that bite first

**You assume a loop `0 tak 3` runs 0, 1, 2.** It runs 0, 1, 2, 3:
`tak` is inclusive at both ends. — STATED (§6a)

`chakra i = 0 tak 3` → prints 0, 1, 2, 3.

**You assume `nirmmita(64)` gives you 64 slots.** It gives you
64 bytes, and `p[i]` counts 8-byte cells: `p[7]` is the eighth
cell, not the eighth byte. And the assumption still bites — but
it bites with an error, not a corrupted heap. A constant index
whose 8-byte cell would extend past the allocation is refused at
compile time, with the line, the index, and the allocation size;
a variable index past the end faults at runtime. — STATED (§6c
states the byte/cell rule; the refusal is v274 and is NOT STATED
as such)

`vitti p = nirmmita(64); p[7] = 42` → `likha(p[7])` prints 42
(the cell fits: 7×8+8 = 64). `vitti p = nirmmita(10); p[1] = 5` →
refused: `E_NIRMMITA_SEEMA: pankti 3:8 - p[1] nirmmita(10) bahih`
("for p[1], nirmmita(16) is needed"). A variable index past the
end (`p[i]` with `i = 8` on `nirmmita(64)`) → stops at runtime
with `mala ank seema atikram`, exit 1.

**You assume `-7 / 2` is `-4` (floor).** Sutram truncates toward
zero, like C: `-7 / 2` is `-3`, and `-7 % 2` is `-1`. — NOT STATED
(§3a covers division by zero and by −1, not this)

`vitti a = 0 - 7` → `a / 2` prints −3, `a % 2` prints −1.

**You assume a decimal number stays decimal wherever you put it.**
`vitti` is integer storage and `dasham` is float storage, and
since v279 a *written* fraction in a `vitti` is refused outright
— it does not truncate silently any more. A `dasham` variable
keeps the fraction. But the refusal is narrow: it covers a bare
written fraction only. A computed float stored into a `vitti`
still truncates toward zero, and an integral `dasham` literal is
allowed. — NOT STATED (new in v279; replaces the Round 85 entry,
which described v278 truncation)

`vitti f = 3.5` → refused (`E_DASHAM_VITTI`: use `dasham`).
`dasham g = 3.5` → 3.500000. `vitti h = x / 2` with `x = 7.0` →
3 (computed, still truncates). `vitti f = 3.0` → 3 (allowed).

**You assume `vitti a = k` copies a `kosh`.** It makes a second
name for the same buffer, and the two diverge if growth
relocates: after an intervening allocation forces `k` to move,
`a` still reads the old buffer. — STATED (§16, v278)

`vitti a = k` (after one push, with an allocation between) →
after `k[0] = 99`, `a[0]` prints 41 and `k[0]` prints 99.

## The rest

**You assume string ordering is lexicographic.** It compares
addresses: the order is declaration order, not alphabetical. —
NOT STATED

`s = "b", t = "a"` → `s < t` is true; swapped contents, still
true.

**You assume `==` on strings compares contents.** It compares
addresses: two separately written `"hello"` literals are unequal.
Use `vartani_tul` for contents. — NOT STATED

`s = "hello", t = "hello"` → `s == t` is false, `s != t` is
true.

**You assume indexing a string reads a byte.** It reads a qword,
like every other index: use `akshar(s, i)` for the byte. —
NOT STATED

`s = "hello"` → `akshar(s, 0)` is 104, `akshar(s, 1)` is 101.

**You assume dividing a `dasham` by zero stops the program, like
integer division.** It does not: `1.0 / 0.0` is +inf, silently,
and the program continues; `0.0 / 0.0` is 0, not NaN. The printer
now prints these correctly: `inf`, and large values in scientific
notation. — NOT STATED (before v279 the printer printed the
minimum value for these; that is fixed)

`dasham q = 1.0 / 0.0` → `q > 0` is true, and `likha(q)` prints
`inf`. `likha(1e20)` prints `1.000000e+20`.

**You assume assignment is an expression.** It is not: you cannot
assign inside an assignment, a condition, or a call argument. —
NOT STATED

`vitti x = (y = 5)` → refused.

**You assume you can write the type of an integer parameter.**
You cannot: integer parameters are untyped; `vitti` is not a
parameter type, but `dasham` is. — NOT STATED

`prakriya f(vitti n)` → refused.

**You assume you can push to a `kosh` you received as a
parameter.** You cannot: `kosh_push` on a `kosh` parameter is
refused, though indexing within capacity works. — NOT STATED

`prakriya f(kosh k) { kosh_push(k, 1) }` → refused.

**You assume an uninitialized variable holds garbage.** It holds
0 — even on a second call, after another call wrote 99. Locals
are genuinely zeroed. — NOT STATED

`vitti x` (uninitialized) → prints 0, then 99 after another call
writes 99, then 0 again on the next call.

**You assume nothing runs after `mukhya`.** After an indented
`mukhya`, trailing top-level statements execute; after a braced
`mukhya`, they are a compile error. — NOT STATED

Indented `mukhya` printing 7, followed by a top-level `likha(8)`
→ prints 7, then 8. Braced `mukhya` with the same trailing line
→ refused.

**You assume a negative index wraps, like Python.** It faults:
there is no wrap, and no silent read. — NOT STATED

`k[-1]` → stops with `mala ank seema atikram`, exit 1.

**You assume `likha(k)` prints a `kosh`'s contents.** It prints
the buffer's address. — NOT STATED (the "Printing a string
variable" section covers string variables only)

`likha(k)` → prints an address (136702555324432 on this run),
not the contents.

**You assume `==` on two `kosh` compares contents.** It compares
addresses: two `kosh` with identical contents are unequal. —
NOT STATED

Two `kosh` each holding 7 → `a == b` is false, `a != b` is
true.

**You assume a descending `tak` loop runs empty, like Python's
`range`.** It counts down. — STATED (reference line 317)

`chakra j = 5 tak 1` → prints 5, 4, 3, 2, 1.

**You assume a loop variable survives the loop.** It does not:
using it after the loop is a compile error. — NOT STATED

`likha(i)` after `chakra i = 0 tak 3` → refused (`'i' … not
visible outside`).

**You assume `s + t` concatenates, because `"a" + "b"` is
`"ab"`.** Literal + literal concatenates (at compile time);
variable + variable adds the addresses. — NOT STATED

`vitti s = "a"; vitti t = "b"` → `s + t` prints an address sum
(8388922 on this run), not `"ab"`.

**You assume NaN is unequal to everything, including itself.**
In Sutram, NaN compares equal to every `dasham`: `nan == 5` is
true, and `nan !=` anything is false. (You get a NaN from
`inf - inf`, where `inf` is `1.0 / 0.0`; `0.0 / 0.0` is 0, not
NaN, so this does not arise from the division entry above.) —
NOT STATED

`dasham nan = inf - inf` → `nan == 5` is true, `nan != 5` is
false.

**You assume a `tak` bound written as a `dasham` behaves like
the integer bound, or is refused like a written fraction in a
`vitti`.** Neither: it compiles cleanly and never stops. The
integer loop variable counts past the bound forever. — NOT STATED
(new this round; this is a compiler defect to fix — a `dasham`
bound should be refused, like `vitti f = 3.5` — not a behaviour
to document permanently)

`chakra i = 0 tak 3.5` → prints 0, 1, 2, … and never stops
(246,013 lines in one second, killed by timeout; the same for
`tak 3.0`).

## What changed in v279 (for the reference maintainer)

- A written fraction in a `vitti` is refused (`E_DASHAM_VITTI`),
  replacing v278's silent truncation for that case. Computed
  floats into a `vitti` still truncate (the `madhava` period
  count and the `roop` rounding step still work as before).
- The `dasham` printer is fixed: large values print in
  scientific notation and infinities print as `inf`, not the
  minimum value. The §3a "Not yet right" printer note is now
  outdated.
- The `dasham` `tak` bound runaway is new in this round's
  findings and is not in v279's changelog; it needs a compiler
  refusal, not just a section entry.
