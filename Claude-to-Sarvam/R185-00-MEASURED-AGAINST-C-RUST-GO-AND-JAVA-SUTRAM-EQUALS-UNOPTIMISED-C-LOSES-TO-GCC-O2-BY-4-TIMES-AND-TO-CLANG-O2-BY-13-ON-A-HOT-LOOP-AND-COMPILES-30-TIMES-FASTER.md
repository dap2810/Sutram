# R185-00 — This machine has the compilers, so it is measured: gcc, clang, Rust, Go, Java, Node, Python. **Sutram runs about as fast as C compiled with no flag. Against `gcc -O2` it loses a hot loop by 4.4 times, against `clang -O2` and Rust by 13, against `gcc -O3 -march=native` by 17 - when the array fits in the cache. On the 80 MB array you asked for the gap is 3 to 5 times, because memory hides part of it.** In the simplest loop the optimisers win by not running it at all. **Sutram compiles 30 times faster than gcc and its executable is 372 bytes.** No compiler was changed; nothing is staged.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
measured: Sutram v315 (main) and v323 (staged tip, r184-read-a-line f05ddd7e)
     - the two compile all five benchmark programs to IDENTICAL bytes, so they are one row measured twice
crash corpus, suite, gates: NOT RUN this round - no source file changed. They stand as in R184-00
     (v323: corpus 227 / 0 failed · suite PASS=329 · gates 89 PASS / 0 FAIL / 1 NOT-RUN, Linux, Xvfb)
the guard: no compiler changed - identity
```

Sanskrit only; no pack touched; `backups/` untouched. `R159 no personal paths`: 0.

## WS1 - what this environment has

| | |
|---|---|
| `gcc`, `cc`, `g++` | 13.3.0 |
| `clang` | 18.1.3 |
| `rustc`, `cargo` | 1.97.0 |
| `go` | 1.24.7 |
| `javac`, `java` | OpenJDK 21.0.12 (patch 1) |
| `python3` | 3.13.17 |
| `node` | v22.23.4 |
| `perl` | v5.38.2 - **found, no programs written** |
| `ruby` | 3.3.6 - **found, no programs written** |
| `zig` | **not found - the row is blank** |

**The machine:** a shared cloud machine, two cores, x86-64 Linux. **I do not write its processor model into the
repository** (the privacy instruction names hardware detail). **It is shared, and it shows:** the same Sutram
executable, measured twice in one run, gave 7.9 ms and 12.0 ms on scenario A. **Read every figure as ±10%, and
the small ones as worse.**

## The table (run 3 of 3; `evidence-r185/benchmarks/results.md`; run 2 beside it)

**Wall time of the whole process, best of five, milliseconds.** `empty` is a program that does nothing - the
cost of starting. The last two columns are the hot loop alone: 10,000,000 additions, the fill subtracted.

| | empty | A | A2 | B | C, per 10 M additions | D, per 10 M additions |
|---|---:|---:|---:|---:|---:|---:|
| **Sutram** (v315 = v323) | 0.4 | 8.1 | 20.2 | 10.8 | **39.8** | **14.5** |
| C, gcc, no flag | 1.5 | 23.1 | 8.9 | 9.1 | 39.8 | 23.6 |
| C, clang, no flag | 1.3 | 8.0 | 9.9 | 10.0 | 22.1 | 7.8 |
| **C, gcc -O2** | 1.3 | 1.2 | 7.8 | 5.3 | **12.6** | **3.3** |
| **C, clang -O2** | 1.4 | 1.4 | 8.7 | 5.8 | **8.7** | **1.1** |
| C, gcc -O3 -march=native | 1.3 | 1.1 | 7.7 | 4.5 | 7.4 | 0.84 |
| C++, g++ -O2 | | | | 11.6 | 13.3 | 3.2 |
| Rust, debug | 1.5 | 39.2 | 38.4 | 15.9 | 48.2 | 24.4 |
| **Rust, opt-level 3** | 1.5 | 1.6 | 8.7 | 6.0 | **8.4** | **1.1** |
| Go | 1.6 | 8.1 | 11.4 | 47.4 | 13.3 | 3.3 |
| Java | 40.2 | 49.8 | 57.0 | 130.3 | 13.3 | 3.9 |
| Node | 25.4 | 42.4 | 471.8 | 95.7 | 19.5 | 6.7 |
| Python | 12.9 | 661.6 | 1574.0 | 89.4 | 86.1 | 47.6 |
| Zig | | | | | | *not installed* |

- **A** - 10,000,000 passes of `s = s + i * 2`. **B** - grow a collection to 1,000,000 and sum it.
  **C** - fill 10,000,000 numbers (80 MB), sum them 20 times. These are yours.
- **A2 and D are mine, and I say why below.** A2: `s = (s + i * 2) ^ (s >> 3)`. D: scenario C's 200,000,000
  additions on 100,000 numbers (800 KB) summed 2,000 times.
- **Every number is 64 bits in every language** - what a `vitti` is. C would normally use a 32-bit `int`:
  half the memory, twice the numbers per vector instruction. **That choice favours Sutram.**

**The commands** (`bench.py` runs exactly these): `sutram_compiler x.sm out` · `gcc -o out x.c` · `gcc -O2 -o
out x.c` · `gcc -O3 -march=native -o out x.c` · `clang` the same · `g++ [-O2]` · `rustc -o out x.rs` · `rustc -C
opt-level=3 -o out x.rs` · `go build -o out .` · `javac -d build X.java` then `java -cp build X` · `node x.js` ·
`python3 x.py`. **One command for all of it: `sh run-all.sh /path/to/sutram_compiler`.**

## WS2 - what each scenario shows

### A: the optimisers win by not running the loop

`gcc -O2`, `clang -O2` and Rust take the time of an empty program. **The loop is not there:** gcc's `main`
loads the answer, `99999990000000`, as a constant and prints it (`evidence-r185/what-the-compilers-made.txt`).
**So A does not measure a faster loop. It measures whether a compiler can see that a loop is not needed.
Sutram cannot.** Where the loop does run - Sutram, clang with no flag, Go - the three take 8 ms. gcc with no
flag takes 23: it keeps `s` and `i` in memory; Sutram keeps them in registers.

**That is why I added A2:** the same loop made so that each pass needs the one before, which nothing can
replace. **Sutram takes 20 ms; gcc takes 8 to 9 with or without `-O2`; Go 11. Sutram is the slowest compiled
language on A2 except Rust in debug mode - about twice as slow as unoptimised gcc (1.9 and 2.3 times in the two runs).** The cause is in the
generated code (`sutram-a2-disassembly.txt`): for an operator with two computed sides Sutram pushes one side
to the stack and pops it, and here that is on the path every pass waits for.

### B: about equal to unoptimised C; half the speed of optimised C; several times faster than Go

**Not the same work in any two rows.** C grows its own array with `realloc`; Sutram's `kosh` grows and checks
every index; Go's `append` and Java's `ArrayList<Long>` pay their collectors (Java makes an object for each
number). **Sutram 8 to 11 ms; `gcc -O2` 5.3; Rust 6.0; Go 47 (89 and 54 in the earlier runs); Java 130.**

### C and D: the hot loop - the one that matters

| 10,000,000 additions | Sutram | gcc no flag | gcc -O2 | clang -O2 | Rust | gcc -O3 native | Go | Java | Node |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **C** - 80 MB | 39.8 ms | 39.8 | 12.6 | 8.7 | 8.4 | 7.4 | 13.3 | 13.3 | 19.5 |
| Sutram is slower by | | **equal** | **3.2×** | **4.6×** | **4.7×** | **5.4×** | 3.0× | 3.0× | 2.0× |
| **D** - 800 KB | 14.5 ms | 23.6 | 3.3 | 1.1 | 1.1 | 0.84 | 3.3 | 3.9 | 6.7 |
| Sutram is slower by | | *1.6× faster* | **4.4×** | **13×** | **13×** | **17×** | 4.4× | 3.8× | **2.2×** |

**On D, Node is twice as fast as Sutram.**

**What causes it, read in the generated code** (`sutram-c_sum_buffer-disassembly.txt`):

1. **Sutram's loop is 22 instructions for one addition.** gcc `-O2`'s is four.
2. **The loop's two variables, `s` and `j`, are in memory, not registers.** In this program four variables
   got registers and these two, declared fifth and sixth, did not. **Declaring them first makes the same loop
   28% faster - 14.1 to 10.1 ms on D** (`c_sum_buffer_hot_first.sm`, `hot-first.txt`). Sutram does not choose
   which variables deserve a register; it takes them in the order they are written.
3. **Each `p[j]` and each loop test pushes a value to the stack and pops it.**
4. **No vector instructions.** clang `-O2`, Rust and `gcc -O3 -march=native` add several numbers per
   instruction.

**And a correction to the brief: "C with `-O2` will vectorise it" is true of clang and not of gcc 13.3.**
gcc `-O2`'s executable has no vector addition in it; clang's has. **gcc -O2's 4.4 times is register use and a
short loop alone. Vectors are what take clang, Rust and `-O3` from 4 times to 13 and 17.**

**Why D exists:** 80 MB does not fit in the processor's cache, so on C a fast loop spends its time waiting
for memory. **C understates the gap - 3 to 5 times where the code is 4 to 17 times slower.**

**One thing I cannot explain:** on C, the same loop over a `kosh` - every index checked - is *faster* than
over raw `nirmmita` memory in each of the three runs (run 3: 32.2 and 35.5 ms against 38.7 and 39.8; the
ranges over all runs touch at 36). On D it is slower, as expected (19.2 against 14.5). **I did not investigate; I report it.**

## WS3 - Rust, Go, Java

In the table. **Rust is built with `rustc` directly, not `cargo`:** `-C opt-level=3` is the level `cargo build
--release` sets; the debug row is plain `rustc`. **Go has one build.** **Java's time includes starting the JVM
(40 ms) and its compiling the loop while it runs.** C++ has B, C and D (A is the C program). **Blank: Zig, not
installed. Perl and Ruby are installed and I wrote no programs for them.**

## WS4 - compile time: the real advantage, measured

Best of five, milliseconds. "big" is the same generated program in each language: 128 functions of six lines
and a main that calls each (1,156 lines of Sutram).

| | small (scenario A) | big |
|---|---:|---:|
| **Sutram** - source to executable, one process | **1.1** | **4.7 to 5.7** |
| gcc, no flag | 34.5 | 82.4 |
| gcc -O2 | 37.2 | 51.2 |
| clang, no flag | 64.6 | 76.6 |
| clang -O2 | 65.9 | 99.3 |
| rustc, debug | 110.0 | 140.4 |
| rustc, opt-level 3 | 117.0 | 136.5 |
| go build (the standard library already built) | 164.7 | 195.4 |
| javac (to `.class` only) | 504.6 | 745.2 |

**Sutram is about 30 times faster than gcc on a small program and 9 to 17 times faster on the big one.**
(gcc `-O2` is quicker than no flag on "big" because it deletes the functions it has inlined.)

**And the executables, scenario A:** Sutram **372 bytes**; gcc 15,968; Go 2,209,063; Rust (opt-level 3) 4,359,144.

**What limits this comparison - found while making it:** **a Sutram program may have at most 128
`prakriya`.** The 129th is refused: `Sutram truti: prakriya paribhasha-suchi seema atikram` - no code, no line
(`prakriya-limit.txt`). **So I could not compare on a 10,000-line program; the other compilers were given
only what Sutram accepts.** The reference's "Size limits" names two limits and says there are others; **I did
not find this one stated there** (searched, not read end to end).

## WS5 - the folder, though it was asked only if there were no compilers

`Claude-to-Sarvam/evidence-r185/benchmarks/`: the programs in eight languages, `run-all.sh`, `bench.py`,
`gen_big.py`, **`BENCHMARKS.md`** (what each scenario measures, what is not fair in it, what to expect), and
the results of runs 2 and 3. **It is in my folder and not in the repository's root because this round changes
no branch. If you want `benchmarks/` in the tree, it moves as it is.** On a machine without a compiler the
row is left blank and says which tool is missing.

## WS6 - the findings, without the wins first

1. **Sutram loses the hot loop to every optimising compiler: 4 times to gcc `-O2` and Go, 13 to clang and
   Rust, 17 to `gcc -O3`, and 2 to Node.**
2. **Sutram is the slowest compiled row on A2** but one.
3. **Sutram equals C with no flag** - faster than gcc's, slower than clang's.
4. **Sutram compiles 9 to 30 times faster than gcc and makes a 372-byte executable.**
5. **Against Python, Sutram is 2 to 80 times faster; against Node, faster on A and B, slower on the hot loop.**

## Where this contradicts the record

| | the shared state (your sandbox) | here |
|---|---:|---:|
| Sutram, A | 13.9 ms | 7.7 to 8.1 ms |
| Node, A | 162.4 ms (Node 20) | 40 to 42 ms (Node 22) |
| Python, A | 2,640 ms (3.12) | 646 to 662 ms (3.13) |
| Sutram / Node / Python, B | 19.0 / 226.9 / 286.5 ms | 8 to 11 / 85 to 96 / 86 to 89 ms |

**A different machine and newer runtimes. "Node is 11.7 times slower" is 5 times here** - and on the hot loop
Node is faster than Sutram. **Neither table is wrong; neither ratio should be quoted without its machine.**
**"No register allocation beyond the trivial" is right:** registers go to the first variables written.
**"C with `-O2` will vectorise it" is wrong for gcc 13.3**, as above.

## Not done, and why

- **Windows: not run.** Linux only.
- **Zig: not installed. Perl, Ruby: no programs.**
- **Four loops and one generated file are not a language comparison:** no strings, no function calls in the
  hot path, no structures, no recursion, no input or output, no memory figures.
- **Not investigated:** why a `kosh` beats raw memory on C.
- **Not repeated on a quiet machine** - there is none here. Three runs; runs 2 and 3 are in the folder.
- **No compiler change.** Finding 2 of "what causes it" (hot variables first) and the push-and-pop of every
  operator are the two places a small change would buy the most. **That is a proposal, not work done.**
- **ROUND-183 (the baseline) is still queued and not started.**
