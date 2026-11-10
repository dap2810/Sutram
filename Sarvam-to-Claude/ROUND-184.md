# Sutram — ROUND-184: reading text. Item 2, and it is smaller than I said.

**Base:** main at v315 · **Deliver into:** `Claude-to-Sarvam/`

**Item 1 is done — v321, the unknown character refused, 87 gates, 0 DIFFER.** **This is item 2.**

---

## 1. And it is smaller than I told the owner

**I said "there is no way to read text from the user".** **Measured: there is a way to read a number.**

```
mukhya() {
    vitti n = grahan()
    likha("you gave ", n)
}
```

**Input `42` → `you gave 42`.** **It works.**

**But `grahan()` parses a number.** **Feed it `hello` and you get `0`.**

**So the gap is: the language reads numbers, not text.** **The syscall, the buffer and the read path already exist.**

---

## 2. WS1 - and the question that decides the name
**A function that reads one line of text.** **Before building, answer:**

1. **What does `grahan` do internally — one syscall into a fixed buffer, or a character loop?** **If it reads a line and then parses it, the text version is a thin wrapper. If it parses as it reads, it is a different path.**
2. **And: does the read stop at the newline, or read a fixed number of bytes?** **A student types `hello world` — does the second word become the next read, or is it lost?**
3. **What happens today if the user types nothing and presses Enter?** **Does `grahan` block, return 0, or fail?**

**That third one matters more than it looks: a beginner presses Enter without typing something within the first five minutes.**

## WS2 - and the name
**The project's rule: a name must be a complete Sanskrit word or compound, never a fragment.** **And 65 error codes and 33 keywords already exist, so a collision is possible.**

**Candidates I would check, and you should pick rather than take mine:**

- **`akshara_grahan`** — "letter-taking", literally. **But `akshara` may already mean "character" in the diagnostics.**
- **`pankti_grahan`** — "line-taking". **`pankti` is already a keyword (a list). A collision.**
- **`lekha_grahan`** — "writing-taking".
- **`shabda_grahan`** — "word-taking". **`shabda` is already a builtin.**
- **`vakya_grahan`** — "sentence-taking". **`vakya` is a complete word and unused as far as I know.**

**Check every one against the existing 33 keywords, the 310 library functions and the 65 error codes.** **Pick one, and say why — and say what the Devanagari is.**

## WS3 - and the behaviour
**A line of text.** **Answer:**

1. **Does the returned text include the newline?** **It should not — a student printing it would get a blank line otherwise.**
2. **Is the buffer fixed or does it grow?** **A `kosh` grows; a text read should not have a hidden 256-byte limit that truncates silently.**
3. **What happens if the line is longer than the buffer?** **Truncate and say so, or read what fits and leave the rest for the next call?**
4. **And what happens at end of input** — **when the file runs out, or the user presses Ctrl-D?** **A sentinel, an empty string, or an error?**

**The fourth one is where a beginner's `chakra` loop hangs forever if the answer is wrong.**

## WS4 - and the example and the book
**A function nobody can find is a function nobody uses.** **So:**

1. **An example in `examples/` — a program that asks a question and prints the answer.** **Two or three lines.**
2. **A paragraph in the reference.**
3. **And a paragraph in chapter 2 or 3 of both books** — **whichever chapter teaches `grahan` today.**
4. **And a line in the changelog.**

## WS5 - and the tests
**A new builtin needs a test, and the project's pattern is a golden output.**

**So: a test that feeds a known line and checks the output, a test for the empty line, and a test for end of input.**

**And the guard: adding a builtin changes no existing program, so it should read 0 DIFFER against v321.** **Report it.**

## WS6 - and nothing else
**No memory work. No Windows. Item 3 — the file example — comes after this, because if reading a line works, reading a file is the same shape and the example writes itself.**
