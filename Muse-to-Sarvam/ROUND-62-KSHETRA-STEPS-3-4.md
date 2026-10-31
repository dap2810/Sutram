# ROUND-62 — steps 3 and 4 finished: exit lowering, the check, and the measured surface

Base: origin/main `6800b310`, CHANGELOG v414, compiler v261.
Read first: `docs/decisions/MEMORY-UNIQUE-HYBRID.md`, my ROUND-61 critique,
`ChatGPT-to-Sarvam/ROUND-134-KSHETRA-REVIEW.md`,
`Claude-to-Sarvam/R62-00-KSHETRA-STEPS-3-4.md`.

Design only. No tree changes. This round's job is to finish steps
3 (the block) and 4 (the check) to the point where development can
start — which means: verify the other parties' designs against the
source and the tree, answer the four step-3 questions and the step-4
question independently where my answer differs, and measure the
four lens numbers. Where I agree with Claude or ChatGPT I say so
and say what I checked; agreement without a check is worthless
here, and there are two places where I correct my own ROUND-61
position in light of the settled design.

## 0. What is settled, and what this round adds

Settled (brief + all parties): the block is the lifetime carrier;
the region is **lexical, not dynamic** — a `nirmmita` written
inside a block uses the scratch cursor, every other `nirmmita`
(outside blocks, inside library bodies, `kosh` growth of an outer
`kosh`) uses the persistent cursor; steps 0–2 (kosh fix, bump,
`dvi-mukha` two cursors) will be built; the one-sentence scope
rule is dead and step 4 is real work.

Two consequences of the lexical settlement that close my ROUND-61
critique, stated plainly so the record is clear:

- **My §1.3 (callee allocates dynamically) is fixed by
  lexicality, not by the check.** Under the lexical rule, a
  callee's allocations are persistent by construction — they are
  not textually inside the block, so they never use the scratch
  cursor and no rewind touches them. `l = suchi_srij(10)` inside
  a block is safe: `l` is a persistent allocation, and assigning
  it to an outer variable is fine. The dynamic-vs-textual gap
  that killed the first rule disappears because the rule is now
  *defined* textually. (The price, noted in §4.3: wrapping a
  request in a block does not reclaim helper allocations — the
  block reclaims only direct `nirmmita` inside it. That must be
  documented, not implied away.)
- **My §1.2 (container returned) is fixed by the check, not by
  lexicality.** A container built inside a block has scratch
  data; returning it is caught by check rule C (the returned
  value's kind is block — §4.2 verifies this). Lexicality alone
  does not fix it; the check does. Both fixes are needed, and
  they fix different cases.

What this round adds beyond Claude's R62-00 and ChatGPT's R134:
(1) the exit-lowering load measured (§5.1 — it is the common
case, not an edge case); (2) a third hole in the check Claude's
rules miss (container reads, §4.2); (3) a cheap closure of rule
D for library callees (a retain table, no second pass, §4.3);
(4) a correction to my own exhaustion position (§3.4); (5) a
verdict on the `kshetra` naming collision (§6).

## 1. Verification of Claude's design against the source

I checked the hook locations Claude cites. All exist as stated:
`.gs_break` / `.gs_continue` / `.gs_return` (`:14440`),
`.gs_assign` (`:13074`), `.gs_assign_index` (`:13267`),
`.gs_assign_field`, `r23_slice_vars` (`src/r23_capabilities.inc:
416`), `r25_gen_prasar` (`src/r25_phal.inc:178`) with the
short-branch 127 check (`:203`), and the loop break-patch stack
(`:14015`, `:14054`). The `prasar` trap is real: adding 14
bytes inside that branch can cross the 127 bound, and Claude's
fix (restore before the `jz` only on the block path, or widen
to `rel32` on the block path only, keeping the no-block
encoding byte-identical) is the right shape. I also checked the
claim that loop generators already save per-loop state on the
compiler stack — the break-patch save/restore pattern is there,
so recording kshetra depth beside it (~10 lines) is plausible.

Line-count plausibility: Claude prices step 3 at ~310 and step 4
at ~270 lines. Against analogues in this compiler — the slice
check's list machinery (~55 lines for the list alone), the debug
counter registration, the `prasar` generator (~150 lines for a
simpler feature) — those totals are in the right order of
magnitude, possibly 20% light for the check's error plumbing
(line numbers through all 8 hook sites). I would budget **~650
lines for steps 3 + 4** rather than ~580, plus the 40-line debug
fail-stop. That is an estimate, not a measurement, and it does
not change the decision.

## 2. Step 3, question 1: exit lowering, priced

### 2.1 Where the restore goes, and what it costs

Endorsed from Claude, with one correction noted in §2.2:

| Exit | Where the restore goes | Added cost when crossing ≥ 1 block | When crossing none |
|---|---|---|---|
| `krama` | `.gs_break`, before the existing `jmp` | 2 instr, 10–14 bytes | 0 bytes |
| `agrim` | `.gs_continue`, before the existing `jmp` | 2 instr, 10–14 bytes | 0 bytes |
| `nivartanam` | `.gs_return`, after the value is in `rax` (and `rdx` for `phal`) | 2 instr, 14 bytes via a scratch register the value does not use (`mov r11,[mark]; mov [rip+cursor],r11`) | 0 bytes |
| `prasar` | `r25_gen_prasar`, before its inline epilogue | same 14 bytes | 0 bytes |
| `sthagita` (process end) | — | nothing | — |

The rule: **an exit restores the cursor to the mark of the
outermost block it leaves.** A break/continue/return that stays
inside all open blocks restores nothing; a jump that leaves
several blocks restores once, to the outermost left. The
compiler knows the depth at the jump site and the depth at the
target (loops record depth at entry, beside the existing
break-patch state), so the mark to restore is a compile-time
lookup, not a runtime decision.

### 2.2 Collapse to the outermost mark is correct, not just an optimization

ChatGPT's lowering algorithm emits cleanup inner-to-outer and
treats collapse to the outermost mark as "a proven
optimization". For v1 that inverts the reasoning: with pure
cursor restore, the intermediate restores are **no-ops by
construction** — restoring to an inner mark and then immediately
to an outer mark leaves exactly the outer mark's value, so
emitting only the outer restore is not an optimization, it is
the same semantics with fewer instructions. Collapse is
correct. ChatGPT's caution becomes load-bearing only if cleanup
ever gains side effects beyond the cursor restore (zeroing on
exit, `mprotect`, decommit) — in that case per-region cleanup
inner-to-outer is required, and the design must say so at that
point. For v1, one restore per exit path, whatever the nesting
depth. This is the answer to "nested blocks where only the
inner is left": leaving only the inner restores the inner mark
(normal block exit); leaving both restores the outer mark (one
store, and the inner restore is subsumed, not skipped).

### 2.3 Why the lowering load is the common case, not an edge case

See §5.1: 58.4% of all exit statements in the tree sit inside
an inner block, and 100% of `krama` / `agrim` do. Exit lowering
is not a rare path to bolt on — it is the path most jumps take.
That does not change the per-exit cost (still 2 instructions),
but it means the lowering must be right for guarded jumps
(`yadi (...) { krama }` inside a loop inside a block — the
dominant shape), not just for bare jumps. The depth bookkeeping
must count kshetra depth, not brace depth: a `krama` inside a
`yadi` inside a block crosses the block; a `krama` inside a
`yadi` inside a loop with no block crosses nothing. The
compiler's per-loop depth record handles both, since the target
depth is what matters, not the number of braces in between.

## 3. Step 3, questions 2–4

### 3.1 Question 2: nested blocks — marks as hidden locals (endorsed, with a note on identities)

Claude's answer is the right one: **each block's mark is a
hidden local of the enclosing function** (`0kshetra1`,
`0kshetra2`, … by nesting depth, via `alloc_var`), living in a
callee-saved register or an `rbp` slot like any local. That is
what makes it recursion-safe (each activation has its own
frame, hence its own marks) and nesting-safe with no shadow
stack. Entry: `0kshetra<d> = 0kshetra_cursor` (2 instr, 10–14
bytes). Normal exit: the reverse. A `nirmmita` inside the block:
load cursor, subtract size, align down, compare with the
persistent cursor, store, return, then zeroing — 6 instructions
plus `rep stosb` (~40 + 12 bytes), per Claude's count, which I
have not independently re-derived but which matches the shape
of the existing `r38_nirm_seq` emission plus the
persistent-cursor comparison.

On ChatGPT's suggestion that marks need unique identities
rather than depth: for **lexical** nesting, depth suffices.
At most one block per depth is live at a time per activation
(siblings are sequential, not concurrent; a loop re-entry
overwrites the same slot, which is correct since the previous
iteration's block already exited). Identities would be needed
only if regions could interleave dynamically — coroutines,
first-class continuations — which Sutram does not have. Depth
is not a shortcut here; it is exact for this language's block
structure. (If regions ever become dynamic, revisit.)

One guard-visible consequence, noted by Claude and confirmed:
the hidden mark local takes a register or slot, which can move
a user variable from a register to the stack **in functions
that contain a block only**. Programs without a block are
unaffected. The guard plan (§7) must confirm this.

### 3.2 Question 3: can a block contain a `nivartanam`? Yes — allow it

I choose **allow**, agreeing with Claude and ChatGPT, for
three reasons:

- **Cost is small and contained:** 14 bytes / 2 instructions,
  emitted only when a return actually sits inside a block.
  Functions without a block pay nothing.
- **Forbidding it would cripple the block for this library's
  own style.** Early returns are everywhere: 909 `nivartanam`
  statements in `lib/` + `examples/` + `tests/` `.sm` files
  (my count, §5.1), 48.8% of them guard returns inside `yadi`
  blocks. A block that cannot contain an early return cannot
  contain most real function bodies — it would be usable only
  for straight-line code, which is not where the loop pattern
  lives.
- **Safety comes from step 4, not from the lowering.** The
  return value is checked before the restore is emitted:
  `nivartanam p` with a block-kind `p` is refused; `nivartanam
  n` with a plain value restores and returns. The lowering is
  mechanical; the check is what makes it safe. Forbidding
  returns would be using a syntactic ban to do the check's job,
  and it would ban the safe cases along with the unsafe ones.

The one case that needs care is `prasar` (failure propagation):
it has its own epilogue and the short-branch bound (§1), and
`yadi dosh` handling may *continue* inside the region rather
than exiting — handled failure inside a region must NOT rewind
it (ChatGPT's K18). The lowering must distinguish "failure
propagates out" (rewind, preserve `rax`/`rdx` status) from
"failure handled here" (no rewind). That distinction is in the
existing `prasar` / `dosh` machinery; the block work must hook
both arms, not just the exit arm.

### 3.3 Question 4: exhaustion — the split policy (and a correction to my ROUND-61 position)

Claude's split policy is the coherent version under the settled
`dvi-mukha` design, and I **correct my ROUND-61 position**
accordingly. My ROUND-61 advice ("clean abort, never silent
`mmap` fallback") was written for a single-arena design, where
a fallback forks the lifetime semantics (fallback blocks survive
rewinds). Under `dvi-mukha` that objection does not apply to
the persistent side, because persistent allocations never rewind
anyway — arena or `mmap`, their lifetime is program duration.
The only difference is speed and accounting. So:

| Who runs out | Behaviour | Why |
|---|---|---|
| Persistent cursor (all existing programs) | **Fall back to today's `mmap`, silently** | Constraint: existing programs allocate beyond any arena (the 1,000,000 × 64 B program takes 4 GB today and works). The fallback changes speed, never behaviour. One addition I propose: in `--debug` builds, count fallbacks (the R46 debug-counter pattern) so the silent path is visible where it matters. |
| Scratch cursor (a `nirmmita` inside a block) | **`nirmmita` returns 0** — its failure contract today | A fallback `mmap` here would not be rewound, so the block's one promise would silently stop holding. 0 is the contract every caller already knows how to test, and it lets the programmer decide (e.g., fall back to a persistent allocation explicitly — their choice, visible in source). |
| `kosh` / `mala` declared inside a block | **Runtime error, exit 1** | These write their header through the returned pointer without testing it, so 0 would be a crash (ChatGPT's R131 hazard). The runtime-error construction exists (`mala` bounds failure, `:14620-14640`). |

**The message.** For the `kosh`/`mala` runtime error, Claude
proposes (UNCHECKED Sanskrit — ChatGPT must check it before
use, per the owner's rule): `Sutram Error: kshetra purnam -
smritih nasti` / क्षेत्रं पूर्णम् — स्मृतिः नास्ति ("the
region is full — there is no memory"), followed by the
requested size. I endorse the shape (Latin + Devanagari, size
included) but not the words until checked. **Where the string
lives matters:** a message in the per-pack table needs an entry
in all eleven packs or `tools/sandesh.py --check` fails — and
the ten non-Sanskrit packs are frozen. Follow the R52 precedent:
keep the message as a Sanskrit-only string outside the table
(`src/r52_yoj_hint.inc` pattern) and report it as such. That is
not a dodge; it is the established way to add a Sanskrit-only
diagnostic without developing frozen packs.

**Arena size.** With rewind, the scratch side holds the peak
live set, so a few hundred MiB is plenty; the persistent side
is bounded by the fallback, not by the arena. A `.bss` arena
must stay well under the smallest machine's RAM (ROUND-60's
finding: 8 GiB of `.bss` fails to load on 7 GB). The default
must be modest and the flag must be validated against the
target (32-bit targets cannot take a large default at all).
No 16 TiB default — ChatGPT's and my ROUND-61 positions agree
here, and the Linux `MAP_NORESERVE` caveat stands: a huge
reservation with a bounds check does not give clean exhaustion
(fault-time SIGSEGV at RAM + swap before the check fires), so
the checked limit, not the reservation size, is the real budget.

## 4. Step 4: the check

### 4.1 The design, endorsed with two additions

Claude's design (kind list per function like `r23_slice_vars`;
`kind(expr)` over the expression AST; rules A–E; pre-scan for
loop-carried flow) is the smallest honest check I can see, and
I endorse its structure. The details that matter:

- **Kind propagation through arithmetic is mandatory, not
  optional.** `kind(e1 + e2)` = block if either operand is
  block (deepest depth). Without it, `outer = note + 64`
  launders the pointer — the brief's own hard case. The lib
  measurement (§5.3) shows why this rule is cheap in practice
  (18 occurrences, all buffer addresses), but the rule must
  exist regardless of frequency, because a single laundered
  store defeats the check.
- **The pre-scan for loop-carried flow is required, not an
  optimization.** A single forward walk accepts `outer = x`
  before `x = nirmmita(8)` in a loop body, and the next
  iteration escapes. The pre-scan (collect every variable ever
  assigned a block-kind value anywhere in the block, treat it
  as block-kind from the first line) is ~60 lines and monotone
  kinds make it sound without a fixed point. One documented
  false positive: a variable used as a plain integer before it
  becomes a pointer in the same block is treated as block-kind
  throughout, so `outer = x` before the `nirmmita` assignment
  is refused even though `x` is still 0 there. Conservative
  rejection of a rare pattern; acceptable, but document it —
  a programmer hitting it will otherwise file it as a compiler
  bug.
- **Calls have kind none (rule D) — honestly unknown, and that
  honesty is the design's strength.** A call result cannot be
  proven block or non-block without the callee's body. The
  check says so instead of pretending.

### 4.2 The container case is caught — and a third hole Claude misses

First, the verification: my ROUND-61 container case (build a
list inside the block, return it) is caught by Claude's rules
in composition. The store `l[2] = d` is allowed (rule B: the
container `l` is itself block-kind at the same depth), but the
return `nivartanam l` is refused (rule C: `kind(l)` is block).
The store into an outer container is refused by rule B
(container not block-kind), and the assignment to an outer
variable is refused by rule A. So the container case is closed
— by rules A + B + C together, not by any one of them. That is
worth stating because it shows the check is a system, not a
list of independent rules.

**The hole Claude misses: laundering through block-kind
container reads.** Rule B allows storing a block pointer into
a block-kind container. But the corresponding **read** —
`m[i]`, a field read — has kind **none** in Claude's table
("honestly unknown"). So:

```
kshetra
    vitti arr = nirmmita(80)
    arr[0] = p          # allowed: arr is block-kind (rule B)
    outer = arr[0]      # allowed: kind(arr[0]) is none — LAUNDERED
```

The taint is stored legally and read back clean. This is the
same class as Claude's "integer laundering through memory"
(`likh8` / `pad8`), but through the language's own containers
rather than raw memory operations — which makes it more likely
to occur in real code (arrays of pointers are an ordinary
pattern). The fix options are: (a) reads from block-kind
containers are block-kind (conservative; false positives when
the element is a plain integer read and assigned outside —
e.g., reading a count from a block array and returning it
would be refused incorrectly); or (b) document it as hole #3
(alongside rule D and memory laundering) and rely on the debug
fail-stop (§4.4). For v1 I recommend (b) with the hole named
explicitly — option (a)'s false positives would reject common
integer-element code, and the debug build catches the escape
at first use. But it must be **named** in the check's
documentation, not discovered later: "values read out of a
block-kind container lose their kind".

### 4.3 Closing rule D for library callees, cheaply (no second pass)

Claude leaves rule D (passing a block pointer to a function
that keeps it) open, on the grounds that a per-function
"retains argument i" summary needs the callee's body analysed
first — a second pass over the program. That is true for
**user** functions. For the **library** it is unnecessary: the
retaining functions are known, few, and stable. The value
positions are exactly four functions' value arguments:
`suchi_khip` (arg 1), `avali_pravesh` (arg 1), `nighantu_khip`
(arg 4), `kosh_push` / `kosh_enqueue` (arg 1). A static table
of those five entries, checked at call sites in the same walk
as rules A–C (~20 lines, no new pass), closes rule D for every
library callee — which is where the tree's own code would hit
it. User callees remain unknown (allowed, documented hole,
debug fail-stop). The lens measurement (§5.4) shows why this
matters for the future rather than the present: **zero** call
sites in the current tree pass an allocation as a value to a
retaining function, so the table changes nothing for existing
code — but it turns rule D from "open hole" into "open hole
only for user functions", which is a materially smaller claim
and, importantly, it gives the acceptance test K02
(`suchi_khip(outer_list, region_pointer)` must be rejected) a
passing implementation on day one.

Also worth adding to the check, from ChatGPT's matrix: **raw
memory writes and indirect/FFI calls with block-kind arguments
must be refused in the checked subset** (K06, K08), not given
kind none. `likh8(outer_address, p)` writes a block pointer
into memory the compiler cannot place — that is a store, and
rule B already covers `likh8` as a hook; the point is that the
hook must refuse when the *value* is block-kind regardless of
whether the destination is placeable. Similarly, an indirect
call (`yantra`) with a block-kind argument cannot be checked
against a retain table, so it must be refused in the checked
subset rather than allowed. These are small additions to the
same hooks, and they prevent the check from being bypassed by
choosing an uncheckable operation.

### 4.4 The debug fail-stop: good mitigation, not a substitute

Claude's mitigation for the remaining holes (rule D for user
functions, memory laundering, container-read laundering): in a
`--debug` build, the scratch cursor never rewinds and each
block's pages are `mprotect`ed on exit (~40 lines), so a
pointer that slips through faults at first use. I endorse
building this — it turns silent corruption into a loud fault
during development, which is the difference between a bug found
in testing and a bug shipped. But it must be described
accurately: **it mitigates, it does not close.** A release
build still dangles silently through any of the three holes.
The check's documentation must list the three holes and say
"release builds do not trap these; debug builds fault on first
use". A lint plus a fail-stop debug build is the honest shape,
as Claude says — provided the word "honest" is doing the work
of naming the holes, not of implying they are closed.

### 4.5 Pricing, endorsed with a contingency

Step 4 (~270 lines: kind list ~50, `kind(expr)` ~60, pre-scan
~60, hooks ~80, line-numbered errors ~20) and step 3 (~310
lines) are plausible against the analogues in §1; I budget
**~650 total** to cover error plumbing. Runtime cost of the
check is zero (all decisions at compile time; no byte emitted
for a passing check). Compile-time cost per operation:
per assignment/store, one `kind(expr)` walk (a few nodes) +
one kind-list scan + one watermark compare; per call, nothing
(rule D) except the retain-table lookup for known lib callees
(§4.3); per arithmetic operation, one recursion step inside
`kind(expr)`; per block entry, the pre-scan (one extra walk of
the block's statements). None of these is on the hot path of
the emitted program — they are compiler-time costs, and they
scale with the size of the function, not with the program's
runtime.

## 5. The lens: four numbers

### 5.1 Lens 1: exits inside a construct that would be a block — 58.4%, and 100% for jumps

Method: for every function in `lib/`, `examples/`, `tests/`
`.sm` / `.smlib` (excluding `tests/negative/`), count
`krama`, `agrim`, `nivartanam` statements and how many sit
inside at least one inner brace block (counting same-line
blocks like `yadi (b < 2) { nivartanam 0 }`, which are the
dominant guard style in `lib/` — an earlier pass that missed
same-line blocks undercounted nivartanam badly, and I corrected
it; the numbers below include same-line blocks).

| Exit | Total | Inside an inner block | Rate |
|---|---|---|---|
| `krama` | 105 | 105 | 100.0% |
| `agrim` | 103 | 103 | 100.0% |
| `nivartanam` | 909 | 444 | 48.8% |
| **All** | **1,117** | **652** | **58.4%** |

Functions with at least one exit inside an inner block: 222
of 1,032 (21.5%).

Reading: **every** `krama` / `agrim` in the tree sits inside a
guard block — because jumps are almost always guarded by
`yadi`. So any kshetra block containing a loop will
essentially always have guarded jumps needing lowering; the
lowering must handle jumps from inside `yadi` blocks (depth
bookkeeping by kshetra depth, §2.3), not just bare jumps.
Nearly half of all returns are guard returns inside `yadi`
blocks. The honest framing: 58.4% is an **upper bound** on the
lowering load — it counts exits inside *any* inner block,
whereas only exits inside an actual kshetra block need
lowering. But it establishes that exit lowering is the common
case: if blocks become common, most jumps in them will need
it. The per-exit cost stays 2 instructions (§2.1); the load is
in getting the depth bookkeeping right, not in the instruction
count.

### 5.2 Lens 2: `nirmmita` calls inside loops today — 1 of 322 (re-confirmed)

Two independent methods (per-function loop-stack walk and
whole-file loop-body ranges) agree on current main: **0 of the
284 `.sm` (a) sites are inside a loop body**, across 48 files
that contain loops. The single in-loop site in the whole tree
remains the `tests/r38/test_fail_alloc.py` temporary
(`likha(nirmmita(8) == 0)` inside a `yavat` loop — an
alloc-failure probe, not a server loop). Total: **1 of 322
executable sites (0.3%)**. The tree's loops use allocations
made before the loop; they do not allocate inside it. As in
ROUND-61: the loop pattern helps future long-running programs
first and converts almost no existing code. Step 3's value is
for programs not yet written, and that should be stated when
prioritizing it against steps 0–2 (which help existing code
immediately).

### 5.3 Lens 3: pointer arithmetic on lib allocations — 10 sites, 18 occurrences, all buffer addresses

Method: for each of the 36 lib executable sites, search the
enclosing function for `var + ...` / `var - ...` applied to
the allocation variable (direct uses only; derived variables
not followed — see the note below).

**10 of 36 lib sites (27.8%) use pointer arithmetic, 18
occurrences total**, all in `nighantu` / `sangrah` scratch
buffers (`tmp`, `tmpa`, `tmpb`, `scratch`). Every occurrence
is of one form: `base + pos + 1` computing the address of a
segment inside a scratch buffer, passed as a **key buffer** to
`nighantu_khip` / `nighantu_antah` (bytes copied, pointer not
retained) or as a **compare buffer** to `khand_tul` /
`khand_mukt`. None is stored, none is returned, none is a
derived pointer that escapes.

What this means for step 4: the arithmetic rule (`kind`
propagates through BINOP) is exercised by a small, uniform
surface in lib — 18 occurrences, all buffer uses. The check's
per-arithmetic cost (one recursion step) is negligible here,
and the rule's *existence* matters more than its frequency:
without BINOP propagation, `tmpa + pos + 1` would launder the
kind, and a future store of such a derived pointer would be
missed. Note the measurement scope: derived variables (e.g.,
`q = p + 8`, then arithmetic on `q`) are not counted, because
the check follows taint through assignments — a derived
variable's arithmetic is also followed, so the true
arithmetic-following load is somewhat larger than 18. The
direct count bounds lib's own surface; it does not bound user
code's.

### 5.4 Lens 4: call sites passing an allocation to a storing helper — 0 strict, 30 broad

Two counts, and the distinction between them is the point:

- **Strict (pointer passed as a *value* to a retaining
  function): 0 call sites.** No (a) site in the tree passes an
  allocation as the value argument of `suchi_khip`,
  `avali_pravesh`, `nighantu_khip` (arg 4), or `kosh_push` /
  `kosh_enqueue` (arg 1). Rule D's hole is currently
  unexercised in the tree's own code.
- **Broad (allocation passed as buffer/key/out to one of
  Claude's 13 "caller-reachable" helpers): 30 distinct sites
  (29 `.sm` + 1 `.py`), 49 occurrences.** By callee:
  `brihat_ank_tak` 12, `nighantu_khip` 11 (all arg 2, key
  buffer — bytes copied, pointer not retained),
  `ank_tak_varna` 10, `rakh_tak_mala` 9, `ank_tak_aadhar_varna`
  7. Every one is a buffer/key/out use (write-through or
  bytes-copied), not pointer retention.

Attribution correction, stated plainly: the brief says "you
found 13 of 25 allocating helpers" — that count is **Claude's**
(`evidence-r60/library-escapes.txt`), not mine. My ROUND-59
pointer-escape count was 8 lib sites (6 returned + 2 stored).
Claude's 13 includes 6 "store into caller-reachable memory"
cases (`brihat_ank_tak`, `rakh_tak_mala`, `vakyank_ank_tak_*`,
and the two growth helpers) where the helper writes *data*
into caller memory without retaining the *pointer*. Both
counts are correct; they count different things (pointer
escape vs caller-reachable writes), and lens 4's two numbers
above keep them apart. For step 4, the strict count (0) is the
one that sizes rule D's hole in the current tree; the broad
count (30) sizes the surface that a careless rule D (refusing
all passes to those helpers) would falsely reject — which is
why rule D must allow buffer passes and refuse only value
retention, i.e., why the retain table (§4.3) must be keyed by
argument position, not by function name alone.

## 6. The `kshetra` naming collision: keep the word for the block, move the field messages

Claude's finding (§0 of R62-00) is confirmed and matters:
`kshetra` already means a struct **field** in three existing
diagnostics (`E_UNKNOWN_FIELD`: "agyat kshetra 'w'";
`E_AMBIGUOUS_FIELD`: "kshetra 'x'"; "rachana kshetra seema
atikram"), pinned by three goldens and
`tests/r23/test_capabilities.py`. ChatGPT's R134 §8 approved
the word without seeing this.

My recommendation: **keep `kshetra` for the block, and move
the field diagnostics to another word in a small follow-up
round** (with ChatGPT's word check, as for any new Sanskrit
term). Reasons: (a) the block is the reviewed, approved term
(Benfey p. 240: field, place, extent — the region metaphor),
and renaming the block now would reopen a settled decision;
(b) the field use is the minority use (three diagnostics vs a
language construct); (c) the confusion is human, not
grammatical — the parser cannot confuse them (block keyword at
statement position vs field name after `.`), but a programmer
reading "agyat kshetra" after writing a `kshetra` block will
wonder whether the block is unknown, and that confusion lands
exactly on the Sanskrit-speaking programmers the messages
serve. The follow-up is small (three diagnostic strings +
goldens + the r23 test) and must not be bundled into the
block implementation — it is a separate, reviewable change.
Until it lands, the block documentation must note the double
meaning explicitly.

## 7. What remains before development starts

Steps 3 and 4 are finishable on this design. The remaining
gates, in order:

1. **The acceptance matrix.** Adopt ChatGPT's K01–K28 as the
   gate, plus three cases from this round and ROUND-61: the
   container negative test (return a record wrapping a block
   pointer — must fail), the callee negative test (now a
   *positive* test under lexicality: assigning a constructor's
   result inside a block must be allowed, since it is
   persistent), and the `agrim`-in-block loop test (bounded
   memory with `agrim` on the hot path, §2.3/§3.2 of ROUND-61).
   K02 must pass via the retain table (§4.3), not just via
   rule D's documentation.
2. **The guard gate (Claude's, endorsed).** Every hook is
   gated on `r62_depth > 0` and the keyword appears in no
   existing program, so steps 3 + 4 must emit **0 DIFFER** on
   all 577 guard programs before the block itself works. If
   not, the gate is leaking and development stops. Note the
   guard-visible consequences that are *not* steps 3–4's:
   step 1 changes how the 248 allocating guard programs
   allocate (bytes change, output must not), step 0 changes
   every `kosh` program, Windows changes every `.exe`.
3. **The two tests, restated with the fixes.** The 1,000,000 ×
   64 B block-in-loop test must include the `agrim` variant
   (bounded memory on the continue path, not just the
   fall-through path). The assign-to-outer-variable negative
   test must fail **with a line number** (the slice refusal's
   missing line number, via `capacity_fail`, must not be
   repeated — the `pankti N` path exists and must be used).
4. **The Sanskrit checks.** Claude's exhaustion message and
   any field-diagnostic replacement word go to ChatGPT before
   use; both stay outside the per-pack table (R52 precedent)
   until/unless the owner decides otherwise.
5. **The documented holes, named in the check's documentation:**
   rule D for user functions, memory laundering, container-read
   laundering (§4.2) — with the debug fail-stop as mitigation,
   not closure.

With those gates, steps 3 and 4 are ready and development of
steps 1–4 together can start. Without the gates — in
particular without the acceptance matrix and the guard gate —
development should not start, because the failure mode is
silent unsoundness (a check that claims more than it proves),
which is worse than no check at all.

## NOT RUN

- Windows / WSL: the PE `.bss` behavior, `MEM_RESERVE` +
  chunked-commit behavior, and the Windows exhaustion paths are
  analyzed from documentation and the Linux measurements, not
  run on Windows (Windows is the owner's own work, per the
  brief).
- Browser automation: no browser component in this round.
- Implementation: no compiler code was changed and no
  `kshetra` program was run (the syntax does not exist yet);
  the guard was not re-run (no tree changes). Claude's and
  ChatGPT's figures cited here are their measurements, checked
  for consistency with the source (hook locations verified,
  §1) and with my own ROUND-59/61 counts, not re-run as
  implementations.
- The Sanskrit in §3.3 is proposed, not checked.
