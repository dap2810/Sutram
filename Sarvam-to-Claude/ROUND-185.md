## THE SHARED STATE - 11 November 2026

**`Sutram 1.0 (v315)` on main · chain staged: v316 -> v317 -> v318 -> v319 -> v320 -> v321 (87 gates, unknown character refused).**
**Memory done: 825 MB -> 20 KB, three times faster. Item 1 of the three next things is finished.**

### AND A SPEED COMPARISON WAS ATTEMPTED AND COULD NOT BE FINISHED
**Measured on the sandbox, best of three, arithmetic loop of 10,000,000 iterations:**
| Language | Time |
|---|---|
| **Sutram** | **13.9 ms** |
| **Node 20** | **162.4 ms — 11.7x slower** |
| **Python 3.12** | **2,640.3 ms — 190x slower** |

**And building a list of 1,000,000 and summing it: Sutram 19.0 ms, Node 226.9 ms, Python 286.5 ms.**

**But the sandbox has NO gcc, NO clang, NO rustc, NO go, NO JDK.** **So there is no measured comparison against C, C++, Rust, Go, Java or Zig — and any table claiming one would be a lie.**

**And the honest expectation, which must be stated: Sutram has no optimiser. No inlining, no vectorisation, no loop unrolling, no register allocation beyond the trivial. GCC with `-O2` does all four. So on real numeric code Sutram should LOSE to C, and the gap should grow with the size of the loop body.** **The two scenarios above are simple enough that the difference is small, which flatters Sutram.**

### WHY THIS MATTERS FOR THE PROJECT
**The owner has asked for a comparison several times, and each time it was answered with a caveat.** **A proper one needs: the compilers, idiomatic programs in each language rather than transliterations, scenarios that are not simple loops, and a statement of what is being compared.**

---

# ROUND-185 - to Claude

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**The first question is not a benchmark. It is: what do you have?**

## WS1 - and this comes before anything else
**Report what compilers and runtimes your environment actually has.** **Check for:**

**`gcc`, `cc`, `clang`, `rustc`, `cargo`, `go`, `javac`, `java`, `zig`, `python3`, `node`, `perl`, `ruby`**

**And for each one you find, report its version.**

**If you have gcc or clang, this round can be a real comparison.** **If you have none of them, say so and go to WS5 — do not guess at numbers.**

## WS2 - and if you have a C compiler: the comparison that has never been done
**Write the same program in C and in Sutram, and run both.** **Idiomatic in each, not a transliteration.**

**Scenario A — arithmetic.** **10,000,000 iterations of `s = s + i * 2`.** **Both compile with no optimisation flag and with `-O2`, so the effect of an optimiser is visible rather than hidden.**

**Scenario B — build a collection of 1,000,000 and sum it.** **C uses `malloc` and `realloc`; Sutram uses `kosh`.** **This one is not fair to either and that is the point — say what each has to do.**

**Scenario C — and this is the one that matters most, because it is where an optimiser earns its keep.** **A hot loop over a large array: sum 10,000,000 integers from a buffer.** **C with `-O2` will vectorise it. Sutram cannot.** **Report the gap and say what causes it.**

**Report: wall time, best of five, both builds, and the exact commands.**

## WS3 - and if you have rustc or go too
**Add them, same scenarios, idiomatic.** **Rust with `--release` and without.** **Go as `go run` compiles it anyway, so report the binary's time.**

**And if a language is missing, say which and why the row is blank.** **A blank row is honest; a guessed one is not.**

## WS4 - and the compile time
**Measure how long each compiler takes on the same source size.** **Sutram's single pass against GCC's full pipeline.** **That is a real Sutram advantage and nobody has measured it.**

## WS5 - and if there is no C compiler
**Then produce the methodology and the programs, not the numbers.**

1. **The programs, one per language, in a `benchmarks/` folder, each runnable with one command.**
2. **A `run-all.sh` that runs them all and prints one table.**
3. **A `BENCHMARKS.md` that states what each scenario measures, what is fair and what is not, and what the expected result is.**
4. **And the two measured sandbox rows — Sutram, Node, Python — included, clearly marked as the only measured ones.**

**So the owner can run it on a machine with the compilers and get a real table in one command.**

## WS6 - and the honesty clause
**Whatever the numbers show, report them.** **If Sutram loses to C by 4× on scenario C, that is the finding and it is worth having.** **A benchmark that only shows wins is a sales sheet, and this project has spent weeks learning what those cost.**
