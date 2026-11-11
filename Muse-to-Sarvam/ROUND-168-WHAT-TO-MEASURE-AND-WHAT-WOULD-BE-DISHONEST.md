# ROUND-168 — what should be measured, and what would be dishonest

**Base:** main at v315, tip commit `064b05ad` · **Deliver into:** `Muse-to-Sarvam/`

**Read only. Nothing compiled or run.** Every line number below was re-grepped
on this tree; every count re-derived from it. Paths are relative to the repo
root. The benchmark numbers quoted are Claude's R185 measurements, read from
`Claude-to-Sarvam/R185-00-*.md` and `evidence-r185/benchmarks/` — this round
did not re-measure anything, and says where R185 is the only source.

Sources read: `src/sutram_compiler.asm` (33,704 lines),
`src/r68_compiler_entry.asm`, `lib/` (24 modules), `examples/` (331 `.sm`
files, re-counted), `benchmarks/` (8 programs), `README.md`,
`PROJECT-MASTER.md`, `ROADMAP.md`, `docs/LANGUAGE-REFERENCE.md`,
`docs/sutram-book-english.html`, `docs/sutram-book-sanskrit.html`,
`docs/sutram-benchmark-report.html`, `docs/BUILDING.md`,
`docs/sutram-project-status.html`, `docs/sutram-stdlib-reference.html`,
`docs/rounds/WHATS-LEFT.md`, `docs/decisions/MEMORY-MY-IDEA.md`.

## Facts the scenarios rest on (all read from the compiler)

- **No optimiser.** Codegen is a single walk over a syntax tree. The peephole
  optimiser exists but is opt-in (`-DSUTRAM_R65_PEEPHOLES=1`) and default-OFF
  (`src/sutram_compiler.asm:137`, `:1539-1540`); it never deletes emitted
  bytes. There is no inlining of functions: the only "inlining" in the
  source is top-level constant substitution (`:17359`). There is no loop work
  of any kind (no LICM, no unrolling, no vectorisation), and no constant
  propagation beyond `fold_const` on literal expressions (`:16519`,
  `:16569`, `:16619`).
- **Registers go to the first five variables, in declaration order**
  (`:29580-29587`); the sixth variable onward lives in memory. The compiler
  does not choose which variables deserve a register. R185 observed the
  consequence on its hot loop: the two loop variables, declared fifth and
  sixth, did not get registers, and declaring them first made the same loop
  28% faster.
- **Every operator with two computed sides pushes one side to the stack and
  pops it** (R185, from the disassembly; the emission pattern is visible
  throughout `gen_expr`, e.g. the push/pop around `.ge_call` at `:22051`).
- **A `kosh` is a descriptor**: `[d-16]` length, `[d-8]` capacity, `[d]`
  elements (`:572-573`). Every `kosh` access loads length and elements from
  the descriptor (`r127_ix`, `:577`; `r128_ixr`, `:586`), so there is a
  descriptor indirection plus a bounds check on every `kosh` read
  (`emit_array_bounds_check`, `:21942`) and every `kosh` write (`:19845`).
  A `mala`'s indexes are bounds-checked (`:11425`). Raw `nirmmita` pointers
  have no descriptor, so there is nothing to check against.
- **A `kosh` grows by doubling its capacity** (`:9098`) inside its own
  64 MiB reservation (`R101A_REGION`, `:9104`); it never moves until it
  passes 8,388,603 elements, and only then takes the relocating path.
- **String `+` allocates a new string**: strlen both sides, allocate
  `la + lb + 1` (`:23848`). `vartani_cat(dst, src)` is `strcat` into a
  caller-provided buffer (`:24051`). There is no string-builder module in
  `lib/` (24 modules; `varna.smlib` mentions a `strb` header that is not
  a file in the tree).
- **Calls are native calls, args in registers, arg0 first** (`:19067`).
  There is no inlining to remove them.
- **Input is numbers only.** `grahan` (BN 33) reads one line from stdin and
  parses digits (`:1074`). There is no time builtin in the source (no
  `samay`/`kaal`/`ghadi` name anywhere in `src/`), so timing must be done
  from outside the program. There are no threads in the language: the only
  `thread` in `src/` is the compiler's own process-spawn code (`:2694`);
  `README.md:33` uses "thread" only as the meaning of the name Sutram.
- **File reading exists and is thin.** `lib/patra.smlib:29-56`:
  `patra_path_sarv(path, out, cap)` opens with `dvaram`, loops `paadh`
  until the count is met or EOF, closes. Number parsing exists in the
  library (`lib/vakyank.smlib:81`, `varna_tak_ank`, and `:264`,
  `varna_tak_dashm`) — but it parses a **mala of integer character codes,
  not raw bytes**, and "Sutram has no byte-write primitive, so we use cell
  arrays of char codes" (`lib/vakyank.smlib:6-8`). A program that reads a
  file must therefore copy bytes cell-by-cell into a `mala` before it can
  parse them: an extra pass and 8x the memory of the file.
- **The tree already has benchmark programs** (`benchmarks/`):
  `bench_loop.sm` (sum 1..10,000,000), `bench_arith.sm` (mixed `*`, `/`,
  `%`, shifts over 2,000,000), `bench_fib.sm` (recursive `fib(27)`),
  `bench_nested.sm` (nested loops with a conditional), and the four
  `r46_hotcall_*.sm` (nested `prakriya` calls, 3,000,000–6,000,000
  iterations; the array one is headed "bounds-checked indexing and nested
  user functions").

---

## Task 1 — what should be measured, and what would be dishonest

### Scenario table

| # | Scenario | What it measures | Optimiser changes the answer? | Fair? |
|---|---|---|---|---|
| 1 | Arithmetic in a loop | loop + integer ops | **Yes — decisively** (loop deletion) | Only in the dependent-chain form (A2); the naive form is a bad scenario |
| 2 | Hot loop over a large array | memory + loop body | **Yes** (vectorisation, register use) | Yes, in two sizes: cache-fitting (honest) and 80 MB (memory-bound) |
| 3 | Building a collection | allocation + growth + indexed write | Barely (growth is runtime work) | Yes, if start capacity and the sum phase are stated |
| 4 | String concatenation in a loop | allocation + copying | No (allocation-dominated) | Yes, run twice: naive `+` and competent buffer |
| 5 | A function call in a loop | call overhead | **Yes** (inlining) | Only if inlining is prevented on all sides, or allowed on all sides and said so |
| 6 | Reading a file and summing numbers | I/O + parsing | No | Only with the read phase timed apart from the parse phase |
| 7 | Sorting 100,000 numbers | algorithm + indexed access | Partly (inlining of the comparator; vectorisation no) | Only with the algorithm fixed to O(n log n) on all sides |
| 8 | Recursion (fib) — added | call + stack traffic | Yes (inlining, tail calls) | Yes, small; the program already exists in-tree |
| 9 | Float arithmetic — added | scalar float loop | Yes (SIMD doubles) | Yes; the program already exists in-tree |
| 10 | Many small allocations — added | allocator | No | Yes; the measurement is already named in the tree |
| 11 | Startup / empty program — added | runtime startup | No | Yes, as its own scenario, not as a speed claim |
| 12 | One real program, ported — added | everything at once | Yes, everywhere | Yes — the only scenario that answers "is Sutram fast for real work" |

### 1. Arithmetic in a loop — measured already, and it flatters Sutram

**The brief is right, and the flattery is worse than it says.** The two
measured rows (10M arithmetic loop; 1M list build) are simple loops, and
the arithmetic one is the shape an optimiser most easily defeats — not by
running it faster, but by not running it at all. R185's scenario A
(`s = s + i * 2`, 10,000,000 passes) shows it: `gcc -O2`, `clang -O2` and
Rust take the time of an empty program, because the loop is replaced by
its answer (`99999990000000` loaded as a constant). **So A does not measure
a faster loop. It measures whether a compiler can see that a loop is not
needed. Sutram cannot.** Where the loop does run — Sutram, clang with no
flag, Go — the three take 8 ms.

**The Sutram program** is already in the tree: `benchmarks/bench_loop.sm`
(`yavat (i <= 10000000) { s = s + i; i = i + 1 }`, `likha(s)`) and
`benchmarks/bench_arith.sm` (mixed `*`, `/`, `%`, shifts; `acc = (acc * 3
+ i) % 1000003`). The `%` and `/` in `bench_arith.sm` matter: division is
not vectorisable and not strength-reducible in the same way, so the mixed
loop is a fairer shape than the pure add.

**The fair equivalents.** C: `int64_t s = 0; for (int64_t i = 1; i <=
10000000; i++) s += i;` — with `int64_t`, because that is what a Sutram
`vitti` is (R185: "C would normally use a 32-bit `int`: half the memory,
twice the numbers per vector instruction. That choice favours Sutram").
Rust: `let mut s: i64 = 0; for i in 1..=10_000_000 { s += i; }`, with the
result passed through `std::hint::black_box`. Go: the same loop with
`int64`, result kept alive. **The result must be used** (printed, or
`black_box` / `runtime.KeepAlive`); a loop whose result is discarded is
deletable in every optimising compiler and the measurement is then a
measurement of deletion.

**The honest form is the dependent chain.** R185 added A2 for exactly
this: `s = (s + i * 2) ^ (s >> 3)` — each pass needs the result of the
one before, so nothing can replace it. On A2 Sutram takes 20 ms; gcc
takes 8–9 ms with or without `-O2`; Go 11 ms. Sutram is the slowest
compiled language on A2 except Rust in debug mode — about twice as slow as
unoptimised gcc. The cause is in the generated code: for an operator with
two computed sides Sutram pushes one side to the stack and pops it, and
here that is on the path every pass waits for.

**Sutram's structural disadvantage:** no LICM, no strength reduction, no
loop deletion, push/pop per operator, registers in declaration order.
**Verdict: keep the scenario, but only in the A2 form. The naive form is a
bad scenario and should not be published.**

### 2. A hot loop over a large array — vectorisation decides everything

**The brief is right.** This is the scenario that matters most, and it must
be run at two sizes, because the size changes what is measured. R185 ran
both: **C** — fill 10,000,000 numbers (80 MB), sum them 20 times; **D** —
the same 200,000,000 additions on 100,000 numbers (800 KB), summed 2,000
times. On C the gap is 3–5x (Sutram 39.8 ms per 10M additions; gcc `-O2`
12.6; clang `-O2` 8.7; Rust 8.4; gcc `-O3 -march=native` 7.4). On D it is
4.4x to gcc `-O2`, 13x to clang `-O2` and Rust, 17x to gcc `-O3
-march=native` (Sutram 14.5 ms per 10M; gcc `-O2` 3.3; clang `-O2` 1.1;
Rust 1.1; `-O3` native 0.84). **80 MB does not fit in the processor's
cache, so on C a fast loop spends its time waiting for memory. C understates
the gap — 3 to 5 times where the code is 4 to 17 times slower. D is where
an optimiser shows what it does.**

**The Sutram program** should be written twice, and the two rows labelled
as different comparisons: once over raw memory (`nirmmita`, `p[j]` —
unchecked, as a C array is not) and once over a `kosh` (every index
checked against the length). R185 did both, and found one thing it could
not explain: on C, the same loop over a `kosh` is *faster* than over raw
`nirmmita` memory in each of the three runs (32.2/35.5 ms against
38.7/39.8); on D it is slower, as expected (19.2 against 14.5). That
inversion is unresolved and should be investigated before either row is
quoted.

**The fair equivalents.** C: fill an `int64_t` array, then
`for (j = 0; j < n; j++) s += a[j];` in a loop, at `-O0`, `-O2`, and
`-O3 -march=native` — three rows, not one, because `-O3 -march=native`
is the ceiling, not the usual build. Rust: `a.iter().sum::<i64>()` (which
auto-vectorises) and, separately, an explicit indexed loop. Go: an explicit
indexed loop (Go's compiler does not auto-vectorise; that is a real
difference between the languages and should be said, not hidden). The fill
must be timed apart from the sum (`C0`/`D0` in R185): filling is allocation
+ write bandwidth, summing is the loop.

**What the optimiser changes:** everything. Sutram's loop is 22
instructions for one addition; gcc `-O2`'s is four. The loop's two
variables sit in memory, not registers. Each `p[j]` and each loop test
pushes a value to the stack and pops it. There are no vector instructions;
clang `-O2`, Rust and `gcc -O3 -march=native` add several numbers per
instruction. **And a correction to the brief's expectation:** "C with
`-O2` will vectorise it" is true of clang and not of gcc 13.3 — gcc `-O2`'s
executable has no vector addition in it; clang's has. gcc `-O2`'s 4.4x is
register use and a short loop alone. Vectors are what take clang, Rust and
`-O3` from 4x to 13x and 17x (all R185).

**Sutram's structural disadvantage:** no vectorisation, no register
choice, descriptor indirection + bounds check per access on the `kosh`
row, push/pop per operator. **Verdict: keep, as the headline scenario,
at both sizes, with the fill timed apart and both the `nirmmita` and the
`kosh` rows.**

### 3. Building a collection — C has `realloc`, Go has a slice

**The Sutram program:** a `kosh` grown with `kosh_kship` (or indexed
assignment past the end) to 1,000,000 elements, then summed. Growth is
doubling inside a 64 MiB region with no move until 8,388,603 elements,
so the growth itself is cheap — a pointer bump plus a length store per
push, with a bounds check per index. The cost is in the indexed writes
and the sum, not in the growth.

**The fair equivalents.** C: `malloc` + `realloc` doubling, written by
hand — C has no collection, so the program writes one. Rust: `Vec::new()`
with `push` (and, as a second row, `Vec::with_capacity(1_000_000)` —
capacity-known vs capacity-unknown is a different question and the two
rows answer different things). Go: `append` to a nil slice. C++:
`std::vector::push_back`. **Not the same work in any two rows:** R185's B
says so plainly — C grows its own array with `realloc`; Sutram's `kosh`,
Rust's `Vec`, Go's slice and C++'s `vector` are built in and check or do
not check each access by their own rules; Java's `ArrayList<Long>` makes
an object for every number (130 ms against Sutram's 8–11 ms — that row
measures boxing, not the language).

**What the optimiser changes:** little. Growth is runtime work; no
optimiser removes a `realloc`. Inlining of the push path matters at the
margin. **What must be controlled:** start capacity (unknown vs
pre-sized), whether the sum phase is inside the timed region (R185's B
includes it; say so), and peak memory — and memory must be reported as
RSS, not virtual size, because a Sutram `kosh` reserves 64 MiB of
address space (`MAP_NORESERVE`, pages committed only when touched) while
a C `realloc` commits what it grows. **Verdict: keep. It is the fairest
of the seven, because it is the one where the optimiser matters least.**

### 4. String concatenation in a loop — quadratic in some languages

**The Sutram program, naive:** `vitti s = ""` then `s = s + t` in a loop.
Each `+` allocates a new string (`strlen` both sides, allocate `la + lb
+ 1`) and copies both. The total copied bytes grow quadratically with the
number of appends, and every intermediate string is garbage the language
has no way to free (there is no `free`; a `kosh`'s region is reclaimed at
block exit, a string's allocation is not).

**The Sutram program, competent:** pre-allocate a `nirmmita` buffer of
the final size and `vartani_cat(dst, src)` into it, tracking the length
by hand. That is linear — but it is manual capacity management, and
there is no builder in `lib/`. The two rows must both be run and labelled:
the naive row measures the default idiom, the competent row measures the
ceiling.

**The fair equivalents.** C: `strcat` into a `malloc`'d buffer grown by
doubling (or a single pre-sized buffer — say which). Rust:
`String::push_str` (amortised linear, capacity doubling). Go:
`strings.Builder` (amortised linear). Java: `StringBuilder`. Python:
`"".join(list)` (the competent form) and `s += t` (the naive, quadratic
form) — both, labelled. **The optimiser changes almost nothing here;**
this scenario measures the allocation model, not the code generator.
Inlining of the append path matters at the margin only.

**Verdict: keep, run twice (naive and competent). A table that shows only
one of the two rows is dishonest in either direction — the naive row alone
makes Sutram look hopeless, the competent row alone hides what the default
idiom costs.**

### 5. A function call in a loop — inlining decides it

**The Sutram program already exists in the tree:**
`benchmarks/r46_hotcall_stack.sm` (two-deep call, 6,000,000 iterations),
`r46_hotcall_nested.sm` (three-deep, 4,500,000),
`r46_hotcall_array.sm` (call + bounds-checked indexing, 3,000,000),
`r46_hotcall_float.sm` (repeated `dasham` calls, 4,500,000). The shape
is `sum = sum + bridge(i)` in a `yavat` loop, where `bridge` calls `leaf`.

**The fair equivalents — and the trap.** A competent C programmer writes
`static int leaf(int x) { return x + 1; }` and `gcc -O2` inlines both
`leaf` and `bridge` away entirely, leaving no call at all. So the naive
comparison measures inlining, not call cost. To measure call cost, the
callee must not be inlinable: put it in a separate translation unit, or
mark it `__attribute__((noinline))` in C, `#[inline(never)]` in Rust,
`//go:noinline` in Go. **Run both forms and label them:** with inlining
allowed (measures the whole toolchain) and with inlining prevented
(measures the call itself). Sutram has no inlining at all, so its row is
the same in both forms — which is itself the finding.

**Sutram's structural disadvantage:** none beyond the absence of inlining
— a Sutram call *is* a native call with args in registers, and the cost is
the call + the callee prologue + the register shuffling. The disadvantage
is that Sutram cannot ever remove the call. **What must be controlled:**
same call depth, same argument count and types (64-bit), same iteration
count, and the callee must do the same work (a leaf that returns `x + 1`
in every language, not a leaf that does nothing in one and something in
another). **Verdict: keep, but only in the noinline form as a call
measurement. The inlining-allowed form is a different scenario — call it
"small-function elimination", not "call overhead".**

### 6. Reading a file and summing numbers — I/O dominates

**The brief is right: the language matters least here, and the scenario is
worth running precisely to show that.** Split it into two timed phases or
it says nothing: (a) read the file, (b) parse the numbers. Phase (a) is
the OS — page cache, read size, syscall count. Phase (b) is the language.

**The Sutram program:** `patra_path_sarv(path, out, cap)` reads the whole
file into a `nirmmita` buffer (`dvaram` + a `paadh` loop until the count is
met or EOF). Then parse with `varna_tak_ank` — but that parses a `mala` of
character codes, not raw bytes, and there is no byte-write primitive, so
the program must first copy the bytes cell-by-cell into a `mala`: an extra
pass and 8x the memory of the file. That bridge is part of the honest cost
of the scenario in Sutram and must be inside the timed region, not hidden
outside it. `grahan` is not the tool here: it reads one line from stdin and
parses digits, and it is a number reader, not a file reader.

**The fair equivalents.** C: `fread` the file, then `strtoll` in a loop
(or a hand parser over the buffer — say which; the hand parser is faster
and is what a competent C programmer writes for a sum). Rust:
`std::fs::read` + `split` + `parse::<i64>()`, or `BufRead::lines`. Go:
`os.ReadFile` + `bufio.Scanner` + `strconv.ParseInt`. **What must be
controlled:** the same file (same bytes, same size — 10 MB of decimal
numbers, say), page cache warm (run once to warm, then time — or cold,
but say which), the buffer size, and whether the parse is included.
**Verdict: keep, as a two-phase measurement. As a single number it is a
bad scenario — it would attribute the OS's speed to the language.**

### 7. Sorting 100,000 numbers — the algorithm matters more than the language

**The brief is right, and the sentence should be in the report itself.**
If the algorithm is not fixed, the comparison is meaningless: Sutram's
`budbud_shreni` (bubble sort, `lib/shreni.smlib:12`) against Rust's
`sort_unstable` (pdqsort) would be a ~1000x algorithm gap, not a language
gap. **Fix the algorithm to O(n log n) on all sides and say so.**

**The Sutram program:** `mil_shreni(a, n)` (`lib/shreni.smlib:222`) — the
only O(n log n) sort in the library. It allocates `tmp = nirmmita(n * 8)`
as scratch and returns -1 if that fails. `shankh_shreni` (shell sort,
`:119`) is the second choice; it sorts in place but its complexity
depends on the gap sequence and it is not O(n log n) in the same sense.
`budbud_shreni` must not be the Sutram row.

**The fair equivalents.** C: `qsort` (glibc: a mergesort/quicksort hybrid
with a function-pointer comparator — that row measures comparator call
overhead) **and** a hand-rolled quicksort or introsort (that row measures
the loop). Rust: `slice::sort_unstable` (pdqsort). Go: `slices.Sort`
(pdqsort). **What the optimiser changes:** the comparator's inlining
(qsort's function pointer cannot be inlined; pdqsort's is monomorphised
and inlined). Vectorisation does not apply to a comparison sort.
**Sutram's structural disadvantage:** bounds-checked indexing on every
access, recursive `prakriya` calls that cannot be inlined, and the merge's
extra memory traffic (a full scratch copy). **What must be controlled:**
the same input distribution — random, already sorted, reverse sorted, and
few-unique values, as four rows, because pdqsort adapts to patterns and
merge sort does not; the same `n`; and the output must be verified sorted
(a program that prints the wrong answer is not timed — R185's rule).
**Verdict: keep, with the algorithm fixed and four input distributions.
Without those two constraints it is a bad scenario.**

### Scenarios the brief missed

**8. Recursion — `bench_fib.sm` already exists.** `fib(27)` measures call
+ stack traffic with no loop at all. C/Rust/Go equivalents are the same
naive double recursion. The optimiser matters (inlining, tail calls —
none of which apply to naive fib, which is the point: it is one of the
few shapes where the optimiser has little to say). Keep, small.

**9. Float arithmetic — `r46_hotcall_float.sm` already exists.**
Repeated `dasham` calls and float accumulation over 4,500,000
iterations. The optimiser matters decisively here: SIMD doubles are what
take clang/Rust/`-O3` from 4x to 13x on the integer loop, and the same
applies to floats. Fair equivalents: C `double` loop at `-O0`/`-O2`/`-O3
-march=native`; Rust `f64` iterator sum; Go `float64` loop. Note the
precision contract: Sutram `dasham` is IEEE-754 double; the sum order must
be the same on all sides or the answers differ in the last bits (and a
program that prints the wrong answer is not timed).

**10. Many small allocations.** The tree already names this measurement:
`docs/rounds/WHATS-LEFT.md:87-91` — "N allocations of a fixed size,
malloc against an arena, same loop, cycles counted with `rdtsc`", noted as
not yet done because the sandbox has no C compiler. The Sutram side is a
loop of `nirmmita` (or `kosh` creation) — a pointer bump against the
arena. The C side is `malloc`/`free` in a loop. **The honest version of
this scenario is the one place Sutram should win outright** — but it can
only be run where both allocators exist, and the `free` half has no Sutram
equivalent (there is no `free`; reclamation is at block exit or program
end), so the two programs do different work and that must be stated.

**11. Startup / empty program.** R185 measured it: Sutram 0.4 ms, C
1.3–1.5 ms, Go 1.6 ms, Python 12.9 ms, Node 25.4 ms, Java 40.2 ms. This
is a legitimate scenario on its own — for short-lived CLI tools, startup
*is* the program — but it measures runtime startup, not the language, and
must be reported as such. It is also the reason wall-time-of-whole-process
must always be reported beside the `empty` column: subtract it to see the
work (R185's method).

**12. One real program, ported.** The scenario the brief's "scenarios that
are not simple loops" points at and never names. Pick one of the 331
examples — a file-processing program, or a numerical one like `chakravala`
— and port it faithfully to C, Rust and Go. This is the only scenario that
answers "is Sutram fast for real work", and it is the hardest to make fair,
because a port is a judgement call on every line. Do it last, after the
micro-scenarios have established the shape of the gap.

### What must be controlled, for every measurement

- **Warmup.** Java and Node need it (JIT); Go, Rust, C and Sutram do not —
  but say so per row rather than assuming it. R185's method (wall time of
  the whole process, best of five) includes JVM startup in Java's row
  (40 ms) and JIT compilation while it runs; that is honest if stated.
- **Allocation.** Inside the timed region or outside it — state it.
  Pre-sizing a collection (Rust `with_capacity`) is a different scenario
  from growing it.
- **I/O buffering.** `patra_path_sarv` issues raw `read` syscalls in a
  loop; C's `fread` buffers. Either buffer on both sides or use raw reads
  on both sides — and say which.
- **Input size, relative to the cache.** 800 KB and 80 MB are different
  measurements (R185 C vs D). State the size and the machine's cache, or
  the ratio is uninterpretable.
- **The machine, and its sharing.** R185's machine is shared, and "the
  same Sutram executable, measured twice in one run, gave 7.9 ms and 12.0
  ms on scenario A. Read every figure as ±10%, and the small ones as
  worse." No ratio should be quoted without its machine.
- **Correctness first.** A program that prints the wrong answer is marked
  and not timed (R185's rule). Every language must compute the same answer
  in 64-bit integers — C would normally use a 32-bit `int`, which is half
  the memory and twice the numbers per vector instruction, and that choice
  favours Sutram, so the 64-bit choice must be stated.
- **Best-of vs mean, and what is subtracted.** Best of five, wall time of
  the whole process, with the `empty` column beside it so the reader can
  subtract startup. A mean with a standard deviation is better than a
  best-of; a best-of with no variance stated is a lower bound, not a
  measurement.

---

## Task 2 — the one number nobody should publish

### Sentences that say "fast" without a measurement behind them

**1. The book, English — the headline overstatement.**

> "1. **Simplicity of Python, speed of C.** You write readable code with
> clean Sanskrit keywords; the compiler produces a tiny native binary that
> runs as fast as hand-written assembly."
> — `docs/sutram-book-english.html:86-87`

The same sentence in Sanskrit:

> "१. पायथन-सदृशी सरलता, C-सदृशी वेगः। … संकलकः लघुं नेटिव्-बाइनरी
> निर्माति यत् हस्त-लिखित-असेंबली-समानं वेगेन चलति।"
> — `docs/sutram-book-sanskrit.html:85-86`

No measurement is cited in either book, and the sentence is now
contradicted by a measurement that exists: R185's disassembly shows
Sutram's hot loop is 22 instructions for one addition where gcc `-O2`'s
is four, and Sutram loses the hot loop 4.4x to gcc `-O2`, 13x to clang
`-O2` and Rust, 17x to `gcc -O3 -march=native` — and 2.2x to Node on the
same loop. "As fast as hand-written assembly" is false as written; "speed
of C" is false against optimised C and was already false against the
project's own 2026-10-21 table (Sutram 13.30 ms vs C 7.88 ms on sum
1..10M — 1.7x slower). **This is the sentence the round is about. It
should not survive in either book.**

Two more stale sentences in the same chapter, not speed claims but
wrong numbers a student will trust:

> "Because the compiler is one readable assembly patra (~9000 lines)…"
> — `docs/sutram-book-english.html:88`, and again at `:357` ("The compiler
> itself is ~9000 lines of NASM").

The main compiler file is 33,704 lines on this tree. The "~9000 lines"
figure is stale by ~3.7x.

> "The compiler is checked by **327 example programs**…"
> — `docs/sutram-book-english.html:755` (in "What the project is careful
> about").

There are 331 `.sm` files in `examples/` on this tree, re-counted.

**2. The benchmark report page — the number nobody should publish.**

`docs/sutram-benchmark-report.html` is a whole page built around one
ratio, and the ratio does not survive R185:

> "Sutram compiles to run at 86% of C -O2 on simple loops — within ~15%
> of the fastest mainstream compiled language"
> — `docs/sutram-benchmark-report.html:886`; the same figure as "1.16×
> the speed of C -O2 (86% of C's speed)" at `:726`, and "Native-speed
> loops — 86% of C -O2" at `:766`.

> "Sutram sits right next to the compiled native languages, far ahead of
> every interpreter and VM-based runtime."
> — `:588`

> "On `sum += i*2`, Sutram takes **190 ms** vs C -O2's **103 ms**."
> — `:906`; the callout title: "C -O2 is ~1.8× faster than Sutram" (`:905`)

> "Even on the simple loop, C -O2 is ~16% faster." (87 ms vs 101 ms)
> — `:918-919`

> "Java (warm JIT, ~120 ms) and Go (~110 ms) are within ~20% of Sutram
> on the loop."
> — `:934-936`

> "1.9× faster than **Node.js**" and "160× faster than **Python**
> (16 s vs 0.1 s)"
> — `:734-738`

The page's own table (`:641-642`) gives the measured rows: Sutram 101 ms
loop / 190 ms arithmetic (100M iterations); C `-O2` 87 / 103; C `-O0` 384.
The rest of the table — C++ `-O2`, Rust release, Java, Go — is
**estimated**: "use well-known benchmark figures (the language wasn't
available in the sandbox)" (`:624`), with no citation of which figures
(`:960-976`: "measured = run in sandbox · estimated = published benchmark
figure"). The methodology (`:960`) says the measured rows were "actually
executed in a sandbox: a 100 million iteration loop, timed as wall-clock,
averaged over 3 runs" — but the page carries **no date, no version, no
machine, no programs and no commands**. The numbers cannot be reproduced
from the page, and the "101 ms" figure appears nowhere else in the tree
(grepped: no other file cites it).

Against R185, the page's headline ratio is wrong in the direction that
matters: on the loops that actually run, Sutram is 4.4x–17x slower than
the optimising compilers, not 1.16x; and on the hot loop Node is 2.2x
*faster* than Sutram, not 1.9x slower. The page's "C -O2 is ~1.8× faster"
on `sum += i*2` cannot even be adjudicated, because R185 shows gcc `-O2`
deletes that exact loop (scenario A: 1.2 ms, the time of an empty
program) — so either the page's C program differs from its description in
a way the page does not record, or it was measured on a compiler that did
not delete the loop, which the page does not name. **The page is an orphan:
nothing in the tree links to it** (no link from `README.md` or any doc
found by grep), which is the only reason it has not done damage. It should
be withdrawn or rewritten from R185, not patched: its measured rows are
unverifiable and its headline ratio is contradicted.

**3. The reference — an unmeasured comparative.**

> "60 functions across six modules. `shankh_shreni` is markedly faster
> than `budbud_shreni` on real arrays."
> — `docs/LANGUAGE-REFERENCE.md:381`

Shell sort is asymptotically faster than bubble sort, so the sentence is
true as complexity — but "on real arrays" is an empirical claim, and no
measurement is cited anywhere in the tree. Either cite one or drop "on
real arrays".

**4. A design doc — a speed claim with the measurement openly pending.**

> "**Region allocation — allocate is a pointer bump, free is a pointer
> reset.** **Faster than malloc, and nothing can leak.**"
> — `docs/rounds/WHATS-LEFT.md:87`

The same paragraph says, immediately below: "**The measurement to settle
it is not done yet.** It should be: N allocations of a fixed size, malloc
against an arena, same loop, cycles counted with `rdtsc`." So this one is
framed honestly as a hypothesis with its test named — but the bare
sentence "Faster than malloc" is still there, in a doc a reader will
quote without the next paragraph. It should carry its own qualifier.

**5. A conditional target, not a claim — noted, not charged.**

> "**Write a Sutram program that allocates 1,000,000 blocks of 64 bytes in
> a loop.** **Time it today.** **Then time it with the `.bss` arena.**
> **If it is not at least 100x faster and the binary has not grown by 64
> MB, the idea is wrong.**"
> — `docs/decisions/MEMORY-MY-IDEA.md:115`

This is a falsifiable target for an idea, not a claim about the language.
It is the right shape and needs no change.

**Not a language speed claim — noted for completeness:**

> "`madhava_pi()` — Madhava's fast series for pi…"
> — `docs/sutram-stdlib-reference.html:234`

"Fast" here describes the series' convergence rate, a mathematical
property of the Madhava series, not the language. Not a violation.

### The honest standard the project already holds — and two docs that meet it

> "**No performance claim.** The compiler emits native code; that is not
> by itself a speed claim."
> — `PROJECT-MASTER.md:333`; the same rule at `:83` ("Do not claim what
> you have not measured") and `:440`.

> "the compiler emits native code, but no benchmark has shown it faster
> than anything. Native output is not, by itself, a speed claim."
> — `docs/sutram-project-status.html:230`

The status-page sentence is now itself stale in the other direction: R185
*has* now shown Sutram faster than some things on some shapes (1.6x
faster than gcc with no flag on the cache-fitting loop; faster than Python
and Node on the simple loop and the collection build). It needs updating
to the R185 record, not deleting.

### Speed claims that DO have a measurement behind them

- **PROJECT-MASTER.md:275-307, "The performance fundamental".**
  Measured 2026-10-21 (Debian 12, x86-64, best of five; C via `zig cc
  -O2`, Zig 0.13.0 ReleaseFast): sum 1..10M — Sutram 13.30 ms, C 7.88 ms,
  Zig 1.77 ms (1.7x and 7.5x slower); startup, empty program — Sutram
  3.36 ms WINS; binary size, hello — 205 B WINS; peak RSS — Zig wins by
  120 KB. The section states its own limit: "one integer loop cannot
  support a claim about 'all aspects'. String, allocation and call-heavy
  shapes are needed before that claim can be made." The aim stated at
  `:277` ("be faster than C and Zig, in all aspects") is an aim, not a
  claim, and the section is explicit that the aim is not met. This is the
  model for how the other docs should write. Note the date: 2026-10-21,
  three weeks before this round, on a different machine from both the
  sandbox rows and R185 — its ratios are not interchangeable with either.
- **The book's register section, both books.** "On a representative
  numerical program this produced a measured speed-up of about **1.2×**
  … and on a tight integer loop the generated code went from 13
  instructions to 5 — a measured **4.9×**. Every claim in this section was
  measured on the same machine before and after, not estimated."
  (`docs/sutram-book-english.html:747-751`;
  `docs/sutram-book-sanskrit.html:647-648`.) Measured, but unverifiable
  from the book: no machine, no date, no evidence pointer, no program
  named. The numbers presumably describe the register work; the section
  does not say which. Keep the numbers, add the pointer — or they are a
  claim without evidence in a project whose rule is that evidence stays.
- **The overflow-check cost, in the reference.** "`+` `-` `*` past the
  range, at run time | wraps around, silently (checking every operation
  measured +5% to +282% on the benchmarks, so it is not done)"
  (`docs/LANGUAGE-REFERENCE.md:107`). A measured range, but "on the
  benchmarks" names no benchmark. Same treatment: name it.
- **R185, the current record.** All of the R169 header's numbers come
  from it (see "Brief corrections"). It is the only comparison in the
  tree that names its machine, its compiler versions, its method (wall
  time of the whole process, best of five) and its programs
  (`evidence-r185/benchmarks/`).

### The R169 header's table, checked against R185

The header says: "C, no optimisation flag — identical; `gcc -O2` — 4.4x
slower; `clang -O2`, Rust `-O3` — 13x slower; `gcc -O3 -march=native` —
17x slower; on an 80 MB array — the gap narrows to 3-5x; compile time —
30x faster than gcc; executable — 372 bytes." Every figure traces to
R185, but every figure has had its qualification cut off:

- **"C identical"** is the 80 MB array row only (C: Sutram 39.8 ms per
  10M additions, gcc no flag 39.8). On the cache-fitting loop D, Sutram is
  1.6x *faster* than gcc with no flag (14.5 vs 23.6). The header's bare
  "identical" is true of one row and false of the other.
- **4.4x / 13x / 17x** are the D row (cache-fitting): 14.5 vs 3.3 / 1.1 /
  0.84. On the 80 MB array the same compilers are 3.2x / 4.6x / 5.4x.
  The header does say "on an 80 MB array the gap narrows to 3-5x", which
  is the C row — so the two halves are consistent, but a reader who quotes
  only the first line quotes the worst case as the case.
- **"Compile time 30x faster than gcc"** is the *small*-program figure
  (scenario A: Sutram 1.1 ms vs gcc 34.5 ms). On the big program (1,156
  lines) it is 9–17x vs gcc (4.7–5.7 vs 51.2–82.4). The header states the
  small figure as the figure.
- **"372 bytes"** is the scenario-A executable; the hello binary in the
  2026-10-21 table is 205 B. Different programs, both measured — say
  which.

**Do these contradict the R168 brief's "no compilers on the sandbox"? No.**
R185 was measured on Claude's machine, which has the compilers (gcc
13.3.0, clang 18.1.3, rustc 1.97.0, go 1.24.7, OpenJDK 21.0.12, python
3.13.17, node v22.23.4; shared cloud machine, two cores, x86-64 Linux).
The brief's statement is about the sandbox, and it is true of the
sandbox. What R185 contradicts is the *benchmark-report page*, not the
brief — and R185 says so itself: "Neither table is wrong; neither ratio
should be quoted without its machine." The R169 header quotes the ratios
without the machine. That is the thing nobody should publish as-is.

**Should any of them be a claim the docs carry?** The D-row gaps (4.4x /
13x / 17x) and the compile-time figures may be carried — with the machine,
the program, and the row named, as R185 names them. The 86% figure from
the benchmark page may not. The "30x" compile figure may be carried only
as "30x on a small program, ~10x on a 1,156-line program".

---

## Task 3 — the compile-time advantage

### Is "much faster to compile than GCC, Rust or Go" real and defensible?

**Yes — and it is the strongest speed claim in the project, because it is
the one that does not depend on the optimiser gap.** R185 measured it,
best of five, wall time of the compiler command (WS4):

| | small (scenario A) | big (1,156 lines) |
|---|---|---|
| **Sutram** — source to executable, one process | **1.1 ms** | **4.7–5.7 ms** |
| gcc, no flag | 34.5 ms | 82.4 ms |
| gcc -O2 | 37.2 ms | 51.2 ms |
| clang, no flag | 64.6 ms | 76.6 ms |
| clang -O2 | 65.9 ms | 99.3 ms |
| rustc, debug | 110.0 ms | 140.4 ms |
| rustc, opt-level 3 | 117.0 ms | 136.5 ms |
| go build (stdlib already built) | 164.7 ms | 195.4 ms |
| javac (to `.class` only) | 504.6 ms | 745.2 ms |

So: about **30x faster than gcc on a small program, 9–17x on the big
one**; 20–30x faster than rustc; 30–40x faster than `go build`; 100x+
faster than `javac` (which only produces `.class` files). And the
executables, scenario A: Sutram **372 bytes**; gcc 15,968; Go 2,209,063;
Rust (opt-level 3) 4,359,144. The shape of the claim is therefore: **"an
order of magnitude faster to compile, and the gap is largest on small
programs"** — not a single number. The bare "30x" is the small-program
figure.

### What the compiler does per line — read from the source

The entry point is 20 lines (`src/r68_compiler_entry.asm`): a macro that
wraps two call sites, then `%include "src/sutram_compiler.asm"`. The
pipeline in `_start` (`src/sutram_compiler.asm:2745`, calls at `:3163`,
`:3182`, `:3195`, `:3226`) is:

1. **Lex** (`call lex`, `:3163`) — a hand-written scanner over the
   expanded source: classify each byte, skip comments and strings, emit
   tokens. Work per token is O(1) classification; there is no allocation
   per token beyond the token stream.
2. **Import expansion** — transitive imports expanded in bounded,
   deterministic breadth-first rounds (R40, `:3592`), into the 128 KiB
   expanded-source buffer (`IMPORT_BUF_CAP`). This is the only repeated
   pass over the source, and it is bounded.
3. **Parse** (`call parse_program`, `:3182`) — builds a syntax tree in a
   3 MiB heap (43,690 nodes max; `E_VRIKSHA_SEEMA`, `:644`). Work per
   statement is building its tree nodes. Literal expressions are folded
   at parse time (`fold_const`, `:16519` and following) — the only
   "optimisation" in the pipeline, and it is constant folding, not
   optimisation.
4. **Codegen** (`call gen_code`, `:3195`) — **one walk** over the tree
   (`gen_stmt` / `gen_expr`), emitting machine-code bytes directly from
   fixed templates. There is no intermediate representation, no second
   pass, no analysis pass, no register-allocation pass: the first five
   variables of a `prakriya` get registers at declaration (`:29580`), the
   rest get stack slots. The peephole pass is opt-in and off.
5. **ELF write** (`call write_elf`, `:3226`) — headers + the emitted bytes,
   one process, no assembler, no linker.

So "compiles in one pass" is imprecise as stated: there are four phases
(lex, parse-to-tree, one codegen walk, ELF write), plus the bounded import
expansion. What is true is that **codegen is a single walk with no
optimisation passes and no separate assembly or link step**. The honest
phrasing is "single codegen walk, no optimiser, no assembler, no linker,
one process" — not "one pass".

### What a single-pass compiler costs, and what an optimising one costs, per line

Per line, Sutram pays: lexing (O(chars)), tree-node construction
(O(statements)), one emission walk (O(tree nodes), each node emitting a
fixed template of bytes), and the ELF write (O(bytes)). All of it is
linear in the size of the program, with small constants, in one process,
with no file I/O beyond reading the source and writing the output.

Per line, an optimising compiler pays: lexing and parsing to an AST,
lowering to IR, **several optimisation passes over the IR** — each O(IR
size) with analysis (alias analysis, loop analysis, value numbering) —
**register allocation** (graph colouring, the expensive part, and the
reason the gap grows with program size), instruction scheduling, then
assembly and linking as separate processes with their own startup and
file I/O. The optimisation passes are also where the *variance* comes
from: gcc `-O2` was *quicker* than gcc with no flag on R185's "big"
program (51.2 ms vs 82.4 ms), because it deleted the functions it had
inlined — optimiser time is not monotone in program size.

That is why the gap is 10–30x and why it is structural: Sutram does not
do the work the others do. The gap is also why the claim is safe to make
in direction and needs a measurement only in magnitude. It would become
false if Sutram gained optimisation passes, a register allocator, or a
link step — i.e. exactly the work the roadmap wants (PROJECT-MASTER.md
:301-305: peephole on, register allocation, loop optimisation, constant
folding, instruction selection). The project should expect the compile-time
advantage to narrow as the optimiser grows, and say so when it does.

### The limits of the claim, read from R185

- **It is capped by a limit the reference does not state.** A Sutram
  program may have at most 128 `prakriya` (`FUNC_TABLE_CAP` /
  `FUNC_DEFS_CAP` equ 128, `src/sutram_compiler.asm:52-54`); the 129th is
  refused. R185 could not compare on a 10,000-line program; the other
  compilers were given only what Sutram accepts. The "big" program is
  1,156 lines. Whether the 10–30x gap holds at 10,000 lines is
  **unmeasured**, and the reference's "Size limits" section names two
  limits (128 KiB expanded source, 3 MiB tree — `:383-384`) and does not
  name this one.
- **It is a wall-time-of-one-command claim.** It includes process startup
  for every compiler. That favours Sutram (one small process) and is
  honest for the "edit, compile, run" loop, but it is not a claim about
  incremental builds, where `go build` and `cargo` cache aggressively.
  An incremental-build comparison is a different scenario and has not
  been run.

### Confirm or refute: "the only speed claim this language can make without a benchmark"

**Confirmed in substance, refuted as written.** The brief's point stands:
compile speed is the only speed claim that is true by construction — it
follows from what the compiler does not do — and R185 has now measured it
at 9–30x, so it can be stated with a number and a program size. But it is
not literally the only claim statable without a benchmark: binary size
(205 B hello, 372 B scenario A) and zero runtime dependencies are also
measurable without a benchmark, though they are size claims, not speed
claims; and the book's register section (1.2x / 4.9x) already states speed
numbers with measurements behind them, however unverifiable from the book.
The precise form is: **compile speed is the only *runtime-performance*
claim this language can make that does not depend on the optimiser gap —
and the only one whose direction is guaranteed by the compiler's
structure rather than by a measurement on one machine.**

---

## Brief corrections (with numbers)

1. **"Bounds checks on every `kosh` read" is right; "on every access" would
   not be.** `kosh` reads (`:21942`) and writes (`:19845`) are checked
   against the descriptor length at runtime. Raw `nirmmita` pointers have
   no descriptor to check against. A `mala`'s indexes are checked only
   when the compiler knows the size (`r81_index_ok`, `:11561`: "a mala of
   this function, or a name R78 knows the size of").
2. **"C with `-O2` will vectorise it" is true of clang, not of gcc 13.3.**
   R185: gcc `-O2`'s executable for the hot loop has no vector addition;
   clang's has. gcc `-O2`'s 4.4x is register use and a short loop alone.
   The brief states it conditionally ("If GCC's `-O2` would vectorise…"),
   so it is not wrong — but the expectation should carry R185's
   correction.
3. **"No register allocation beyond the trivial" is right, and the trivial
   rule is now citable:** the first five variables of a `prakriya`, in
   declaration order, get registers (`:29580-29587`); the rest live in
   memory.
4. **"Descriptor indirection on every access" is right** (`r127_ix`,
   `:577`; `r128_ixr`, `:586` — length and elements reloaded from the
   descriptor on every access).
5. **"No threads" is right.** No thread builtin or keyword exists; the
   only `thread` in `src/` is the compiler's own process-spawn code
   (`:2694`).
6. **"Two measured rows" understates the in-tree benchmark set.**
   `benchmarks/` holds eight programs, not two: `bench_loop.sm`,
   `bench_arith.sm`, `bench_fib.sm`, `bench_nested.sm`, and the four
   `r46_hotcall_*.sm`. The brief's two rows are a subset; the other six
   are the call-overhead and recursion shapes this round's Task 1 reuses.
7. **The R169 header's numbers are R185's numbers with the qualifications
   cut off** (see Task 2): "C identical" is the 80 MB row only (on D
   Sutram is 1.6x faster than gcc with no flag); "30x faster than gcc" is
   the small-program compile figure (big program: 9–17x); "372 bytes" is
   the scenario-A executable (hello is 205 B). The header does not name
   the machine; R185 does, and warns that no ratio should be quoted
   without it.
8. **"Sixty-four false claims by Sarvam this stretch" (R169 header) was not
   re-derived here.** The R166 brief said 63. The increment is consistent
   with one more found since, but no count in this round was re-derived
   from the tree, and this round does not confirm or correct it.
9. **The book's "327 example programs" is stale** — 331 `.sm` files in
   `examples/`, re-counted on this tree. The book's "~9000 lines" for the
   compiler is stale by ~3.7x (33,704 lines for `src/sutram_compiler.asm`
   alone).
10. **R185's "Sutram turns each statement into machine code as it reads
    it" (BENCHMARKS.md) is imprecise.** The compiler lexes, expands
    imports, parses into a syntax tree, and *then* walks the tree emitting
    code (`:3163`, `:3182`, `:3195`). The codegen walk is single; the
    pipeline is not.
11. **The R168 header's chain ("v316 -> v321, 87 gates") and the R169
    header's ("v316 -> v322/v323") differ because the chain grew between
    the two briefs**, not because either is wrong. Noted so the difference
    is not read as a contradiction.

Two citations in the working notes were corrected during verification
before this report was written: the "raw `nirmmita` pointers stay
unchecked" line was cited to `:19799`, which is an unrelated `mov`
instruction — the quoted comment text does not exist in `src/`, so the
claim is stated here only in the form the code supports (no descriptor,
nothing to check against); and the 128-`prakriya` refusal message quoted
in the notes was not found verbatim, so the limit is cited here to the
capacity constants (`FUNC_TABLE_CAP` / `FUNC_DEFS_CAP`, `:52-54`) instead.

---

## Could not determine

- Whether the benchmark-report page's C programs (100M loop, 190 ms vs
  103 ms) differ from R185's scenario A in a way that explains why gcc
  `-O2` did not delete the page's loop. The page contains no program text,
  no commands, no machine and no date, so the discrepancy cannot be
  adjudicated from the tree.
- Whether `likha` issues one `write` syscall per value. The emission has
  many `mov eax, 1` (write) sites, but which belong to `likha`'s per-value
  path was not established by reading in this round. It matters for any
  scenario that prints inside the timed region.
- Whether Sutram's `dasham` (float) codegen is scalar SSE throughout, and
  what the float loop's instruction count is. The scenario is recommended
  (Task 1 §9) on the strength of `r46_hotcall_float.sm` existing, not on
  a verified reading of the float emitter.
- Why a `kosh` beats raw `nirmmita` memory on R185's scenario C (32.2/35.5
  ms vs 38.7/39.8). R185 reports it and does not investigate it; neither
  does this round (read-only, no execution).
- Whether the book's register-section numbers (1.2x, 13→5 instructions,
  4.9x) describe the R57 register work or another change, and on which
  machine and date they were measured. No evidence pointer exists in the
  book or the tree.
- Whether the compile-time gap (9–30x) holds at 10,000 lines. R185 could
  not run it: the 128-`prakriya` limit caps the Sutram side at 1,156
  lines in its "big" program.
- Whether the loop-body-size claim ("the gap should grow with the size of
  the loop body", R168 brief) holds as an isolated variable. R185 varies
  the loop shape (A vs A2 vs D) but never varies body size alone.
- "Sixty-four false claims" (R169 header) — not re-derived (see correction
  8).

---

## Summary

**Task 1:** Of the brief's seven scenarios, five are keepers with
conditions (hot array loop at two sizes; collection build; string
concatenation run twice, naive and competent; call in a loop only with
inlining prevented; file reading only as two timed phases), one is a bad
scenario in its naive form (the arithmetic loop, which optimising
compilers delete — keep only the dependent-chain form), and one is a
keeper only with its premise stated in the report (sorting, algorithm
fixed to O(n log n), four input distributions). Four more are added:
recursion and float arithmetic (both already exist in-tree as benchmark
programs), many small allocations (the measurement the tree already
names but has not run), and startup time — plus one real ported program,
which is the only scenario that answers whether Sutram is fast for real
work. **Task 2:** The book's "Simplicity of Python, speed of C … runs as
fast as hand-written assembly" (both books) is unmeasured and now
contradicted by R185, and must go; the benchmark-report page's "86% of C
-O2" is unverifiable (no date, machine, programs or commands in the page)
and contradicted on the loops that actually run, and the page should be
withdrawn or rewritten from R185, not patched; the reference's "markedly
faster … on real arrays" and the design doc's "Faster than malloc" need
their measurements cited or their qualifiers restored. What *is* measured
and honest is the PROJECT-MASTER table (2026-10-21), the book's register
numbers (measured but without an evidence pointer), and R185 — which does
not contradict the brief's "no compilers on the sandbox", because R185
was measured on Claude's machine, not the sandbox. **Task 3:** "Much
faster to compile than GCC, Rust or Go" is real and measured — ~30x on a
small program, 9–17x on a 1,156-line program, 20–40x against rustc and
`go build` — but "one pass" is imprecise (lex, import expansion, parse to
a tree, one codegen walk, ELF write; no optimiser, no assembler, no
linker, one process), and the claim is capped by the unstated
128-`prakriya` limit and unmeasured at 10,000 lines. The brief's "only
speed claim without a benchmark" is confirmed in substance with one
qualification: it is the only *runtime-performance* claim whose direction
is guaranteed by the compiler's structure rather than by a measurement on
one machine.

---

*Read-only round. Nothing compiled or run. All benchmark figures are
Claude's R185 measurements, read from the tree, not re-measured here.*
