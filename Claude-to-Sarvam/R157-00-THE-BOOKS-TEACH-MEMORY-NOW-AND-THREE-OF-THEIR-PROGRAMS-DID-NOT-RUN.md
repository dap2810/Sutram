# R157-00 — The memory chapter is in both books, chapter 19, in your order and with each example run on v315. Writing it found that the books had programs that did not run: chapter 8's array example wrote past its `mala`, and two library examples called a function renamed in v292. Chapter 14 is retitled. The four paused-language books are marked archived at v294. Your measured number is v284's; v315 measures 392 KB against 49,920 KB. The prune (WS3) is in R159-00, not here.

## Release line

```
gates: 79 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
Sutram 1.0 (v315) - sampurna sutra      (compiler unchanged; this round changes documents)
installer bb903afda1efbaa075fe1159b07ef615e3176d2533bf6dc4ff9d94adfef130c4
```

- **Commit:** the one carrying this file (SHA in my chat report). It carries R158 too; R158-00 has the gate.
- **The guard: NOT re-run** - no compiler, runtime, library or pack byte changed.
- **The installer is rebuilt,** because the books are in its payload (gate `R140 package` 7/0).

## WS1 - the chapter

**`docs/sutram-book-english.html` and `docs/sutram-book-sanskrit.html`, chapter 19 (`id="memory"`)**, the same content in each language. In your order:

| # | topic | what it shows | run on v315 |
|---|---|---|---|
| 1 | **`kosh` beside `mala`** | a `mala dinah[3]` and a `kosh` that grows from room for two to three; when to use which; both bounds-checked (`mala ank seema atikram`) | prints `31`, `3`, `9` |
| 2 | **`mandapa`** | 200,000 calls, each taking 256 bytes in a block; a number leaves the block, an address may not (`E_SCRATCH_ESCAPE`); the block does not undo what it printed | prints `20000100000`; **392 KB** peak with the block, **49,920 KB** without |
| 3 | **`parimana()`** | `0`, then `1008` inside a block (1000 rounded up to 16), then `0` after | as stated |
| 4 | **`mandapa parimita N`** | a 1000-byte budget; the second 512-byte `nirmmita` is refused with `E_PARIMITA`, exit 1; why a sentence is better than the operating system killing the program | `512`, then the refusal, exit 1 |
| 5 | **a slice and its one rule** | `yoga(k[1:3])` = `5`; **the rule: use a slice of a `kosh` where you make it, pass it straight to a reader, do not keep it**; three refusals, each a separate labelled example | the reader runs; `vitti s = k[0:1]` → `E_KOSH_VIBHAG`; a slice to a `prakriya` that can grow `k` → `E_KOSH_VIBHAG`; `k[0:1] + 0` → `E_VIBHAG_ANKA` |
| 6 | **out of memory** | `Sutram truti: kosh vardhayitum smritih na labdha - kosh yatha asit tatha eva`, and that **the `kosh` is as it was** | the message is the compiler's own string (`r127_msg_grow`). Not run: it needs memory exhaustion |
| 7 | **what it does not have** | no garbage collector, no `free` to call, no reuse inside a live block, no threads; a block's `kosh` cannot leave it | - |

**Plus a "putting it together" example:** a `kosh` made outside, a budgeted block on each of five passes, a number carried out each time. It prints `5`, `25`, `96`: only the `kosh` is still held.

**ChatGPT's corrections to the brief (`ChatGPT-to-Sarvam/…221-FOLLOWUP-DOC-BRIEFS…`) are taken:**
- **Item 5 names two codes, not one.** Keeping a slice past a possible growth is `E_KOSH_VIBHAG`; using a slice as a number is `E_VIBHAG_ANKA`. The brief named only `E_VIBHAG_ANKA`, for the wrong case. The chapter teaches the permitted use and labels each refusal with its own code.
- **It says the compiler decides before the program runs.** It does not wait to see whether the `kosh` grows.
- **The qualifications are in the text:**
  - the block reclaims its `nirmmita`, not what it printed or wrote;
  - the measured number is one machine and one program, not a promise;
  - the `kosh` being unchanged after a failed growth does not mean the program can carry on;
  - "no `free`" describes what you call, not what the runtime does inside.

**Your number - "200,000 allocations cost 52,760 KB without a block and 13,480 KB with one":**
- **It is from your ROUND-99, measured at v284:** 200,000 calls each allocating 256 bytes.
- **I ran the same program on v315.** `/usr/bin/time -v` gives the largest resident memory: **49,920 KB without the block, 392 KB with it.** The block's cost fell from 13.5 MB to 0.4 MB since v284.
- **`tools/peak_rss.py` reports 0 for both runs on this machine** (the `wait4` reading is empty here), so the numbers are from `time`.
- **The chapter gives v315's numbers and says what they are.**

**Chapter 14, *"New Features: v22"*, is now *"More of the language: comments, shortcuts, the library"*** - its contents are comments, `+=`, `++`, string joining, descending loops, `yantra`, `grahan`, the ternary and the library. It also had a sub-heading *"v29 – v41"*; now *"Later additions: the ternary, `kuru` … `yavat`, bounds checks, the library"*. In the Sanskrit book, the same.

## What writing it found - the books' programs

I ran every complete program in both books on v315 (gate `R158 doc currency` does that now; R158-00). **Three did not do what the book says, in each book:**

1. **Chapter 8, the first `mala` example, wrote past its array.**
   - `mala tarika[5]`, then `chakra i = 0 tak 5 { tarika[i] = … }`.
   - `tak` includes its last number, so the loop writes `tarika[5]`, and v315 stops the program with `mala ank seema atikram`.
   - The text under it said *"no bounds checks, C speed"* - not true since the bounds checks came in.
   - **Now:** `0 tak 4`, and the text says `tak` includes its last number and that the index is checked.
2. **and 3. Two library examples in chapter 14 call `mahattam`,** which v292 (R111) renamed `mahattam_samapavartak`. The old name no longer compiles: `agyat prakriya: mahattam`.
   - **Now** `mahattam_samapavartak`, and the library table gives `mahattam_samapavartak` and `laghuttam_samapavartya`.

**And two false sentences in chapter 18, in both books, which no gate could find:**
- *"On Windows the IDE is not yet available"* - it is `sutram-ide-gui.exe`, on the Start menu.
- *"Windows has not yet been run on a real Windows machine"* and *"160 tests"* - it has been, from v309 to v312. The suite is 327 programs. The sentence now says that each release's notes say which package has been run on Windows.

## WS2 - is it any good?

**Could a person who has never programmed read this chapter and write a program that uses a block, a budget and a `kosh`?**
- **Yes, if they have read chapters 2 to 8 first.** The chapter uses `vitti`, `chakra … tak`, `prakriya` and `nivartanam` without explaining them.
- **With those, it gives them all three in one runnable example** ("putting it together"), and the "Try it" box sets them a budget to find by experiment.
- **Read alone, no:** a beginner starting at chapter 19 meets loops and functions they have not been taught.

**What is still missing:**
- **The chapter shows the out-of-memory message but cannot let a reader see it happen.** A program that exhausts memory is not one to put in a beginner's book. `--fail-alloc` exists for testing, but it is not documented for readers.
- **The Sanskrit chapter's code comments are Sanskrit; its program text is the same romanized Sutram as the English book.** That is how the whole Sanskrit book is written. A reader of the Sanskrit book still types `kosh`, not `कोश`.
- **The Sanskrit prose is mine.** It should be read by someone who reads Sanskrit before it is called finished.

**Does every code example in the new chapter compile on v315? Yes.**
- Nine complete programs in each book: six run to the exit the book states (one of them, the budget, to exit 1), and three are refused with the code the book states.
- They are checked on every gate run from now on.

## WS4 - the four paused-language books

**Archived, not deleted.** Each of `sutram-book-hindi.html`, `-tamil`, `-telugu`, `-gujarati` now opens with a banner, in English and Sanskrit:
- it describes Sutram **as it was at v294** (3 November 2026, their last content change, R114);
- it is not kept up to date, and has no memory chapter;
- it links the English and Sanskrit books (v315).

The banner carries `data-archived="v294"`, which gate R158 requires of each.

**Kept in place, not moved,** so links into them still work. They are not language packs (`lang/` is untouched), so this is not development on a frozen pack.

Evidence: `Claude-to-Sarvam/evidence-r158/` (the gate's runs).
