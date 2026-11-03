# Sutram — ROUND-112: the contract audit. Which of the 306 promise what they cannot deliver?

**Base:** main at v292 · **Deliver into:** `Muse-to-Sarvam/`

## Your R111 is the most useful finding of the week
**`sankhya_bindu` is total garbage: 0 for every collection shape, segfault on scalars.** **And your line - "unstable garbage, not a computation" - is exactly the right way to put it.**

## WS1 - and the class it belongs to
**ChatGPT found `patra_asti(path)` in its capability probe: the name says "file exists", the body tests "opens read-only successfully".** **Those differ.**

**So there are at least two functions in the 306 whose name promises something the body cannot deliver.** **How many more are there?**

**Read every `prakriya` in the 24 modules and flag any where:**
- **the name promises a computation the body cannot perform**
- **the body returns a value of a different type than the name implies**
- **the function can return garbage rather than refusing**

**You have 306 to read.** **That is a large round and it is the right one - this class of defect returns a plausible number and the student believes it.**

**Give me: the count, and the list with one line each.**

## WS2 - and rank them
**Not all are equal.** **`sankhya_bindu` returns 0 for everything - a student notices.** **`patra_asti` is wrong only for paths that exist but will not open - a student may never hit it.**

**Rank by: does it produce a WRONG ANSWER, or merely a DIFFERENT answer than the name implies?**

**The first is a defect. The second is a documentation problem.** **Say which each one is.**

## WS3 - and one I want checked specifically
**`sankhya_dot` and `sankhya_bindu` are the same function.** **Are there other builtin aliases where the OLD name and the NEW name promise different things?** **A rename that changes the meaning is worse than either name alone.**
