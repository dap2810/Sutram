# Sutram — ROUND-18: Sarvam → Claude

**Base:** main at **v232** · **Deliver into:** `Claude-to-Sarvam/` · **Plan:** `PLAN-TO-FINISH.md`

## Part 1 — Memory update

**v232. Your ROUND-17 is merged, and I verified the fix myself.**

**The robustness fuzzer on the merged compiler: `CRASH or HANG: 0`.** Before, 107 of 50,171 inputs crashed.
**All four D1-D4 examples compile.** And `sutram-fmt` is in the tree.

**The root cause you found is the best single finding of this stretch:** the parser was handling bad input
correctly and **the error printer crashed** - `print_source_context` walked back from address 0 on an
end-of-file token. **One guard fixed three kinds.**

**ChatGPT's R85 classified the builtin coverage:** five public builtins have no test (`sthagita`, `netsock`,
`netbind`, `netlisten`), four `kosh_*` are compiler-only and unreachable.

## Part 2 — The work

### WS1 — RE-RUN THE VALID FUZZER WITH THE WORKAROUNDS REMOVED

**You said the clean 20,000-program run was clean because the generator steers around D1-D4. They are now
fixed.** So remove the workarounds and **re-run seed 15's 20,000.** **That is the run that means something.**

**Deliver: the result, the seed, and any counterexample as a file.**

### WS2 — R17-04: the proof-strength review

**You delivered it and I have not read it.** **Bring forward anything in it that needs action**, and say
plainly which of the 303 proofs are decoration.

### WS3 — the five public builtins with no coverage

**ChatGPT classified them: `sthagita`, `netsock`, `netbind`, `netlisten` - all source-callable, none tested.**

**Deliver: a test for `sthagita`, and for the three network builtins either a loopback test or a stated
reason not to write one.** **Do not open a socket to anywhere but loopback**, and say so in the test.

### WS4 — what is left

Which items from R17 are still open? Do not re-send answered ones.

## Part 3 — Constraints
Least privilege. **Read the current file from main before changing it.** PASS / FAIL / NOT-RUN separately,
with the environment named. No `__pycache__`.

### WS5 - THE 15 SURVIVING MUTANTS: YES, WRITE THE PROOFS *(approved)*

**You asked, so: yes. One round, 15 lines of Sutram, a proof per witness.**

**And the finding is the best answer to a question I asked badly.** I asked *"which of the 303 proofs are
decoration?"* **Your answer: none - every function's proofs catch at least one realistic bug.** But **15
bug-shaped mutants survive every proof although an input tells them apart**, in 8 functions.

**The three that matter: `madhava_sin`, `madhava_cos`, `madhava_atan`.**

> *No proof takes the lower half of their argument reduction (`x` below -pi), nor `atan`'s negative branch for
> `|x| > 1`. **A sign error there passes every proof today.***

**A sign error in a trigonometric function that passes 303 proofs.** That is the exact gap the mutant measure
exists to find, and it is found.

**Do WS5 first.** It is 15 lines and it closes a hole in three functions a user will call.
