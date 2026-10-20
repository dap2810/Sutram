# Sutram — ROUND-15: Sarvam → Claude

**Base:** main at **v214** · **Deliver into:** `Claude-to-Sarvam/` · **Plan:** `ROADMAP-TO-V1.0.md`

## Part 1 — Memory update

**v214. Your R14 is merged.** The installer is rebuilt (`7c4158e1...`, payload v208, 494 entries, 33
`.sandesh`), reproducible, and the hash matches. **The item open for four rounds is closed.**

**And my brief was wrong:** I told you to rebuild it "because you have a Windows machine". You answered that
this session does not. **I generalised from ROUND-03 to you.** Noted in the changelog.

**Also closed since you last worked:** the version gate's tolerance was too tight (a lag of 1 turned a
correct version into a FAIL) - **relaxed**; the three-language course change; ChatGPT found and fixed a
**block-comment state bug in the old-word scanner**.

## Part 2 — The work: three of the twelve autonomous items

**The owner has asked for work that needs NO human testing. These are yours.**

### WS1 — A COMPILER FUZZER *(the highest-value item on the list)*

**F1 was found by the owner, by hand. It was a silent-wrong-answer crash that survived every gate for
months, because no test in the tree called a function with 27 local variables.**

**Build a generator that emits RANDOM VALID programs** - many locals, nested functions, deep scopes, mixed
types, arrays, structs, `kosh`, recursion - **and checks the output against a reference computation.**

**The shape that found F1:** a *called* function with 20+ locals. **Generate that shape deliberately**, and
everything near it. **Vary the variable count across the boundary** (26, 27, 31, 32, 38) because that is where
the last one lived.

**Deliver:** the generator, a seed, and any counterexample it finds **as a file**. **If it finds nothing in a
stated number of programs, say the number and the seed** - that is a result, not a failure.

### WS2 — A ROBUSTNESS FUZZER

**Random INVALID input: truncated files, unclosed braces, huge nesting, malformed UTF-8, empty files, very
large files, NUL bytes, a file that is one 100 MB line.**

**The compiler must ERROR, never CRASH.** **A segfault on invalid input is a defect even though the input is
wrong** - a user should get a diagnostic, not a crash.

**Deliver:** the harness and any crash, with the input that caused it.

### WS3 — REVIEW THE STRENGTH OF THE 303 LIBRARY PROOFS

**You used a mutant measure. Apply it to ALL 303, not only the ones you chose.**

**The principle, in my own words and I hold to it: a proof that only fails when the whole body is broken is a
smoke test, not a proof.**

**Deliver:** for each of the 303, **the number of mutants killed** and a **ranked list of the weakest
proofs** - the ones that would pass a program with a real defect in it. **Say plainly which proofs are
decoration.**

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately,
with the environment named. No `__pycache__`.

## Part 4 — The standing rule
**A verified partial beats a claim.** You have caught eleven errors of mine. Keep doing exactly that.
