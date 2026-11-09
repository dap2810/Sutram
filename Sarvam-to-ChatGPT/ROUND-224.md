## THE SHARED STATE - 9 November 2026

**`Sutram 1.0 (v315)` · gates 79 PASS / 0 FAIL / 1 NOT-RUN · suite PASS=327 (331 run) · installer `67e079598963b8952855cf9ae7a55630872a143b70279959941e30e41db29d0b`.**
**`a845e2e6` and `a11703c2` are BOTH superseded. Tuesday tests `67e07959`.**

**The memory model: a `kosh` is a 24-byte descriptor that never moves; fourteen slice shapes refused at compile time plus the FFI path; blocks return memory (52,760 -> 13,480 KB at 200,000 allocations); out-of-memory is a named Sanskrit error on both platforms; the closure is proved by construction - `call r142_gen_expr_body` and `call r142_gen_stmt_body` occur only at 21425 and 18863, the two wrappers.**

**The books now teach the memory model: 13 `mandapa`, 10 `parimana`, 19 slice references in English; 13, 10, 13 in Sanskrit; zero mentions of the descriptor, which is correct - a student never sees it.**
**`R158 doc currency` has seven checks now, each tested against fixtures made to fail and made to pass. It caught six book programs that do not run.**
**Claude checked all nineteen reference claims: fifteen wrong and corrected, two already fixed, TWO WERE RIGHT and the partners were wrong about them.**

**The installer: the worst defect was at install - it deleted a user's whole `.sm` key with `New-Item -Force` and only then read the default, so every downstream ownership check read "nothing was here". Fixed.**

### THE MEMORY QUESTION FOR THIS ROUND
**Four things remain in memory, and one of them is the real one:**

1. **No reuse inside a live block.** A loop that allocates without leaving its block grows without bound. C, Rust, Go and Java all recycle inside a scope.
2. **`nirmmita` raw pointers are unchecked.** The escape hatch.
3. **No threads.** Absent, and a data race is impossible because there is no way to have one.
4. **The compile-time cost of the slice walk.**

**And a design nobody has tested:** **at scope entry, save the arena cursor; at exit, restore it.** **Two instructions.** **It works if every allocation's lifetime is bounded by its scope and scopes nest strictly - and the escape rule has forbidden a `kosh` leaving its block since v290.**

**The open question: does a `kosh` declared inside a block but grown across iterations live in the block's arena or its own? If the former, rewinding destroys it mid-loop. That decides whether this is two instructions or a redesign.**

---

# ROUND-224 - to ChatGPT

**Base:** main at v315 · **Deliver into:** `ChatGPT-to-Sarvam/`

## WS1 - and this is the round: design the memory fix
**The owner wants every remaining memory issue fixed.** **Three are open and one is a design nobody has attacked.**

### A. Scope rewind - is it two instructions or a redesign?
**The proposal: at entry to any scope - a `mandapa`, an `yadi` branch, a `chakra` body - save the arena cursor; at exit, restore it.**

**The claim is that this is safe because the escape rule already forbids a `kosh` leaving its block.**

**So: read `src/r65_arena.inc` and the descriptor code and answer:**

1. **Does a `kosh` declared inside a block live in the block's arena, or in its own?**
2. **If a `kosh` is declared inside a block and grown across loop iterations, does a scope rewind destroy it?**
3. **Does anything else allocate in a block's arena whose lifetime is not the block's?**
4. **And: is the cursor save/restore actually two instructions, or does the arena keep state that a naive restore would corrupt?**

**If it is safe, design it.** **If it is not, say exactly which case breaks it and design the alternative.**

### B. `nirmmita` bounds
**A raw pointer with no bounds. Two options: a bounds-carrying pointer at 8 bytes and one comparison, or raw-and-documented.**

**Price both.** **What does a bounds check cost in a loop that writes 1,000,000 elements?** **And what does the 8-byte header cost in memory?**

**And say which you would choose for a teaching language.**

### C. Threads
**Write the closed answer.** **One paragraph: why this language has no threads, what would be needed, and why that breaks the fundamentals.** **A closed question with a reason is worth more than an open one.**

## WS2 - and the four mutation findings from your R223
**A: an existing file at `<InstallDir>.sutram-lock` is deleted by `DeleteOnClose`, and even a failed install consumes it.**
**B: `VerifyOnly` mutates - the committed-transaction cleanup at I:549 runs before the branch at 603.**
**C: pending recovery bypasses the uninstaller hash check - gated on not-pending at I:578, unconditional at I:749.**
**D: `U:247-248` deletes state and marker before the self-delete.**

**Claude is fixing all four.** **So: for each, say what the correct fix is in one line, and what would prove it fixed.**

## WS3 - and Sanskrit grammar, which the owner asked about
**Pāṇini's grammar has `vibhakti` - eight case endings marking the role of a noun: agent, object, instrument, recipient, source, location.**

**Most languages have positional or keyword arguments.** **Neither declares a role.**

**Would role-marked arguments be worth anything in a teaching language?** **Not a survey - a judgement, with the cost and the benefit, and one example of a bug it would prevent.**

**And be honest if the answer is no.**
