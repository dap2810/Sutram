# Sutram against other languages - the programs, the method, and what each scenario can and cannot show

**One command:**

```
sh run-all.sh /path/to/sutram_compiler
```

It builds every program this machine can build, runs each five times, checks that each printed the right
answer, and writes `results.md` (the tables) and `results.json`. **A compiler that is not installed leaves a row
that says so; nothing is estimated.** It needs `python3`; everything else is optional.

## What is measured

- **Run time is the wall time of the whole process, best of five** - from starting the program to its exit. So
  it includes starting the language's runtime. **The `empty` column is that cost alone:** subtract it to see
  the work.
- **Compile time is the wall time of the compiler command, best of five.**
- **Every number is a 64-bit integer in every language,** because that is what a Sutram `vitti` is. C would
  ordinarily use a 32-bit `int`, which is half the memory and twice as many numbers per vector instruction -
  **this choice favours Sutram, and it is the only way to make the programs do the same work.**
- **A program that prints the wrong answer is marked and not timed.**

## The scenarios

| | what it does | what it shows | what is not fair |
|---|---|---|---|
| **empty** | nothing | the cost of starting | - |
| **A** | 10,000,000 passes of `s = s + i * 2` | the cost of the simplest loop - **and whether a compiler notices the loop is not needed** | An optimising compiler replaces the whole loop by its answer. Its time is then the time of `empty`: **that is not "a faster loop", it is no loop.** |
| **A2** | 10,000,000 passes of `s = (s + i * 2) ^ (s >> 3)` | the same loop when it cannot be replaced: each pass needs the result of the one before | Added by Claude; not in the round's brief. Sutram's `>>` moves zeros in from the left and C's keeps the sign; the values here stay positive, so the answers agree. JavaScript needs `BigInt` to hold 64 bits, which is slow - that row measures `BigInt`. |
| **B** | grow a collection to 1,000,000 numbers, then sum it | what a growing collection costs | **Not the same work in any two languages.** C has no collection: the program writes one (`malloc`, `realloc` to double). Sutram's `kosh`, Rust's `Vec`, Go's slice and C++'s `vector` are built in and check or do not check each access by their own rules. Java's `ArrayList<Long>` makes an object for every number. |
| **C** | fill 10,000,000 numbers (80 MB), then sum all of them 20 times | a hot loop over a large array | **80 MB does not fit in the processor's cache,** so a fast loop waits for memory and a slow loop does not: the gap between compilers is smaller here than the code deserves. `C0` is the fill alone. |
| **D** | the same 200,000,000 additions on 100,000 numbers (800 KB), summed 2,000 times | **the same hot loop when memory is not the limit - this is where an optimiser shows what it does** | Added by Claude; not in the brief. `D0` is the fill alone. |

**Sutram in C and D uses raw memory (`nirmmita`, `p[i]`), which is not checked - as a C array is not.** The
table also gives the same loop over a `kosh`, where every index is checked against the length.

## What the flags mean

- **C, no flag** is `-O0`: every variable lives in memory. **`-O2`** is what people ship. **`-O3 -march=native`**
  lets the compiler use every instruction this processor has; it is the ceiling, not the usual build.
- **Rust "debug"** is plain `rustc`; **`-C opt-level=3`** is the optimisation level `cargo build --release`
  sets (the programs are single files, built with `rustc` directly).
- **Go** has one build; `go build` optimises.
- **Java** is `javac` then `java`: the time includes starting the JVM and its compiling the loop while it runs.
- **Node and Python** are run from source.

## What to expect, and why

**Sutram has no optimiser.** It turns each statement into machine code as it reads it. It keeps the first few
variables of a `prakriya` in registers; the rest live in memory. Every operator with two computed sides pushes
one to the stack and pops it. It does not remove a loop it could compute, does not use vector instructions,
does not unroll, does not move a calculation out of a loop.

- **Against C with no flag: about the same,** sometimes faster (C at `-O0` keeps everything in memory).
- **Against `-O2`: Sutram should lose, by more as the loop gets tighter.** A is lost completely (the loop is
  removed); D is the honest measure of the gap.
- **Compile time: Sutram should win by a wide margin** - one pass, no assembler, no linker, one process.

**A table that shows only the rows Sutram wins is a sales sheet. Read A2, C and D.**

## What this does not measure

- Programs with function calls, strings, structures, recursion or input and output. **Four loops are not a
  language.**
- Memory use.
- Windows.
- Zig, Perl and Ruby have no programs here. C++ has B, C and D only (A is the C program).

## The compile-time program

`gen_big.py N DIR` writes the same program in Sutram, C, Rust, Go and Java: `N` functions of six lines and a
main that calls each once. **`N` is 128 because that is the most `prakriya` one Sutram program may have** -
the 129th is refused. So the comparison cannot be made on a large source: the other compilers were not asked
for more than Sutram accepts.

## Files

```
a_arith.*  a2_arith_dependent.*  b_collect.*  c_sum_buffer.*  empty.*      .sm .c .rs .js .py  (.cpp for B, C)
c_sum_kosh.sm                    scenario C / D with a kosh
c_sum_buffer_hot_first.sm        scenario C / D with the hot loop's two variables declared first (not run by bench.py)
go/<scenario>/main.go            java/<Scenario>.java
gen_big.py                       the compile-time program
bench.py                         builds, runs, checks, writes results.md and results.json
results.md, results.json         the last run on the cloud machine (run 3); results-run2.*: the run before it
run-all.sh                       the one command
```
