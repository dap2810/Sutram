# ROUND-83: the alias census, the guard-page check, and the assumptions page

Base: origin/main at v278 (compiler `Sutram 1.0 (v278)`), tree reset to
`a41b5ba8` before work. No tree changes. Deliverables in
`Muse-to-Sarvam/`: this report, `R83-THE-ASSUMPTIONS-PAGE.md`, and
`r83_alias_census.json` (the auditable census data).

## WS1 — the census: 3 · 1 · 0

Question: how many programs in `examples/`, `tests/` and `lib/`
assign one `kosh` to another (`vitti a = k` or `a = k`)? For each,
does the `kosh` grow after the alias, and is there an allocation
between the alias and the growth?

**Aliases total: 3. Aliases that grow: 1. Aliases that grow with an
intervening allocation: 0.**

So the brief's conditional holds: **the defect is real, but nothing
in the tree hits it.** The one program that grows after aliasing
grows with no allocation in between, which is the safe shape.

### Method (and the false-positive trap)

Per-function scope, comments and string literals stripped. A `kosh`
name is a `kosh … name[…]` declaration or a `kosh … name` parameter
in that function. An alias site is `vitti a = k` (decl-init) or
`a = k` (assignment, `a` not itself a `kosh`) where `k` is such a
name and the right-hand side is *bare* — followed by a statement
end, not by `[`, `(`, or an operator. Growth is `kosh_push` /
`kosh_enqueue` on `k` or on any alias of `k`, later in the same
function. An intervening allocation is a `nirmmita(` call, a `kosh`
declaration, a push/enqueue on a *different* `kosh`, or a call to a
library function that itself calls `nirmmita` (the 26 from the R82
analysis), between the alias and the first growth.

The bare-right-hand-side rule matters: the first pass counted 39
sites, and 36 of them were element reads, not aliases —
`phal = ank_suchi[0] + weight`, `dasham h = xs[i + 1] - xs[i]`,
`vitti total = ys[i]` — where the name after `=` is followed by
`[`. Every library "alias" and every test "alias" in the first pass
was of that form. After the fix, the library has **zero** aliases
and the tests have **zero** aliases. Two further manual checks:
the tree's only bracketless `kosh` declaration (`kosh row`,
examples/203) has no alias, and none of the five Devanagari `kosh`
files (97, 100, 110, 122, 219) assigns its `kosh` to another
variable — 219's "aliases" are Devanagari *builtin* names, not
`kosh` aliasing. No `kosh`-to-`kosh` assignment exists anywhere.

### The three sites

| file | alias | grows? | intervening allocation? | what it is |
|---|---|---|---|---|
| examples/252_r38_alias_kosh_oob | `w = v` | no | — | R38 probe: an alias must be bounds-checked like the original. `w[5] = 9.9` on a cap-4 `kosh` stops with `mala ank seema atikram`, exit 1. No growth, so no divergence. |
| examples/255_r42_alias_kosh_push | `w = v` | yes, via `w` | none | R42 probe: push through the alias grows the original. `kosh_len(v)` is 2, `w[1]` is 4, exit 0. No allocation between alias and growth, so no relocation, so no divergence. |
| examples/287_r82_kosh_after_mandapa | `bahar = k` | no | — | The v278 block rule, not divergence: `k` is made inside a `mandapa`, aliased out, and read after the block. The program stops with `E_KOSH_MANDAPA` (generation check), exit 1 — it prints 22 from inside the block first, then faults on the post-block read. |

### A refinement the census condition does not capture: the length freezes too

The brief's condition is about the *buffer* diverging on
relocation. There is a second, independent divergence, measured
this round: the alias's *length* freezes at alias time, and only a
push *through that name* updates it.

- Alias after 1 push, read `a[1]` with no growth at all: faults
  (`mala ank seema atikram`, exit 1). The length is 1, not 2.
- Alias after 2 pushes, read `a[1]`: 42, and `k[1]`: 42.
- 255 is safe on this axis too, because its growth goes through
  the alias (`kosh_push(w, 4)` updates `w`'s length to 2, so
  `w[1]` works). Had 255 grown through `v` and then read `w[1]`,
  it would have faulted on length, not diverged silently.

So "grows" needs one more qualifier for a complete census: grows
*through which name*. In this tree the answer does not change
anything — the only grow site grows through the alias — but a
future program that aliases, grows through the original, and reads
past the alias-time length through the alias will fault, and that
fault is the length divergence, not the buffer divergence.

### The brief's verified behaviour, re-run on v278

- With the obstacle (`vitti obstacle = nirmmita(64)` between alias
  and growth): `a[0] = 41, k[0] = 99`. Diverges, as stated.
- Without it: `a[0] = 999, k[0] = 999`. Agrees, as stated.
  Divergence is conditional on relocation, exactly as the brief
  says. The earlier "they agree" test proved nothing about the
  class because it was the no-obstacle case.

## WS2 — the guard-page check, done independently

Built the guard-page compiler from `tools/guard_page.py`
(`nasm -dGUARD_PAGES`, kept in the round's workspace): **controls
5/5** (all four controls SIGSEGV as they must, the clean control
runs clean). Then ran both cases under it.

**The brief's expectation is confirmed: the stale read does NOT
fault.** Under the guard build, the obstacle case prints `a[0] =
41, k[0] = 99`, exit 0 — identical to the normal build. A stale
handle reading a *live* block does not fault, guard pages or not:
the guard sits at the block's *end*, and a stale read of the old
buffer is in-bounds of that old buffer. It is a wrong value, not
an out-of-bounds access, so no guard page is crossed.

**But the guard build changes the semantics in a way that matters
for Claude's checking: under it, the no-obstacle case diverges
too** — `a[0] = 41, k[0] = 999`. The guard build has no arena and
no `kosh` extension, so every growth relocates, obstacle or not.
That means the guard build cannot be used to check whether a
program's aliases agree: it diverges always. It can only check
whether a stale read *faults*, and the answer is no.

The isolated stale read confirms the mechanism: after divergence,
`a[0]` reads 41 (live, stale) under both builds, and `a[1]`
faults under both builds — not with SIGSEGV but with the `kosh`
bounds check (`mala ank seema atikram`), because the alias's
length froze at 1. The guard build adds nothing here; the
compiler's own bounds check is what fires.

### What would change if anything ever freed the old buffer

Today the old buffer is never freed (no `munmap`, no free
primitive), which is why the stale read is silent. If relocation
freed the old buffer, the stale read would fault — under the
normal build (SIGSEGV on unmapped memory) and under the guard
build alike. That would turn silent divergence into a loud fault,
which is the fail-stop the guard-page gate is for. But it would
also break the invariant the region design recorded: old buffers
must never be unmapped or reused while nameable. And freeing
*with reuse* (recycling the address to a new allocation) would be
worse than today: the stale read would return a *new* value
silently, instead of the old one — wrong data that looks fresh.
Freeing without reuse is the only form that helps, and it costs
the "never freed" guarantee the current design leans on. So the
guard build, as it stands, does not catch this defect class, and
no guard-page result should be read as "the alias is safe".

## WS3 — the page

`R83-THE-ASSUMPTIONS-PAGE.md` is the page: fifteen items, each
run on v278 and checked against the reference as it stands.

The brief's four, verdicts:

- `tak` inclusive — **STATED (§6a)**. Correction to Round 82,
  owned: Round 82 called this a gap ("only implied"). The §6a
  example already prints the exact stdout for the `tak` form
  (0, 1, 2, 3, 4) and calls the endpoints inclusive. The gap was
  overstated; the page carries the sentence anyway, marked stated.
- `nirmmita` bytes vs `p[i]` qwords — **STATED (§6c)**.
- Integer division truncates toward zero — **NOT STATED (§3a)**.
  §3a covers division by zero and by −1, never the rounding
  direction. Sentence supplied: "Integer `/` truncates toward zero
  and `%` takes the dividend's sign: `-7 / 2` is `-3`,
  `-7 % 2` is `-1`."
- `vitti a = k` aliasing — **STATED (§16, v278)**, with the
  relocation condition, the Linux/Windows difference, the
  old-buffer-valid point, and the "keep one name per `kosh`" rule.
  One sharpening offered: §16 says "with the old length" but not
  the sharpest form — `a[1]` faults even when nothing relocates.

Round 82's eight further items, all re-checked against the
current reference: **all eight still unstated** (string `==`,
string indexing, `dasham` division by zero, assignment not an
expression, `vitti` as a parameter type, `kosh_push` on a
parameter, uninitialized `vitti` reading 0, trailing statements
after an indented `mukhya`). Their sentences are carried over,
credited to Round 82.

Three new items found this round by reading the reference against
the compiler:

- A negative `kosh` index faults (`k[-1]` → `mala ank seema
  atikram`, exit 1); there is no Python-style wrap.
- `likha(k)` prints the `kosh`'s buffer address, not its elements
  (the reference's "Printing a string variable" section covers
  string variables only).
- `kosh == kosh` compares addresses: two `kosh` with identical
  elements compare unequal. No builtin compares contents.

Checked and *not* page items (so Sarvam does not re-derive them):
a `kosh` made in a `mandapa` lives as long as the block (§19);
empty pop/peek/dequeue abort (§16); string `+` concatenates
(`"a" + "b"` is `"ab"`); redeclaring a `vitti` is refused, in the
same block and in a nested one — both shapes were probed on v278,
so the Round 81 "silent redeclaration" note does not apply to
either of them.

## NOT RUN

Windows, browser, implementation. The guard-page result is Linux
only (the diagnostic build and the PE allocator differ, and §19
says a `mandapa` is an ordinary block in a Windows program).
The census is a static analysis of the tree as it stands; it does
not execute every alias site (the three sites were each run, and
the two verified cases were re-run, but the 0 for the third count
is a property of the source text, not of a runtime sweep).
