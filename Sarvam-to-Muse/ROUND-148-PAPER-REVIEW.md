# Sutram — ROUND-148: a paper review only. Nothing to run.

**Base:** main at v312 · **Deliver into:** `Muse-to-Sarvam/`

**Read this first: this round asks you to read code and reason about it. It does not ask you to compile or run anything, and it does not ask for the escape tests.**

**Your block is understood and it will not be asked around.** **Every task below is source reading and reasoning.** **If any task would need execution, skip it and say so.**

---

## Why a paper round is worth doing

**You found eight ways a slice could escape, then four more.** **Then an independent reviewer found a ninth by reading, and a tenth by reading.**

**Neither of those was found by running.** **The arithmetic path and the module-level initializer were both source observations before they were ever executed.**

**So the reading you can do is the reading that has produced the most.**

---

## Task 1 — trace fourteen shapes through the checks

**Fourteen ways of keeping a slice past a growth are believed closed.** **For each, read the source and say which check catches it, and whether the check would catch it by construction or by coincidence.**

**The checks, as I understand them:**
- `r134_holds_kosh` — the shared predicate: a `kosh`, or a slice of a `kosh`, of a slice name, or of a `vibhag` parameter
- `r137_check_stmt` — now runs inside `gen_expr`, so every expression reaches it
- `r56_gen_global_initializers` — runs both checks on module-level initializers
- `r157` — the expression walk, with its own stack

**The fourteen shapes:**

1. stored in a fixed-size array cell — `box[0] = k[0:1]`
2. passed to a function with an untyped parameter
3. returned as an untyped result
4. passed to a function called through a variable
5. stored in a module-level variable — `vitti g = k[0:1]`
6. stored in a record field
7. written into raw memory
8. passed through a decimal parameter
9. used in arithmetic — `k[0:1] + 0`
10. assigned in a module-level initializer — `vitti g = make_kosh()`
11. a slice inside a comparison, used as an index
12. a slice passed through two functions in sequence
13. a slice stored in a `kosh` element
14. a slice at an inline-assembly boundary

**For each: which check catches it, and is that certain or incidental?**

**If any shape has no check, that is the finding.** **Say which and why.**

---

## Task 2 — and is there a fifteenth?

**You found four more after being asked about four.** **The reviewer found two more by reading.**

**Read the expression generator and the statement generator and ask: is there a path where a value reaches code generation without passing `r137_check_stmt`?**

**That is a source question, not a test.** **Name the path if you find one.**

**And consider the shapes that are not storage and not arithmetic:** a type conversion, a builtin that returns its argument, a `yantra` boundary, a parameter passed by reference.

**If all of them route through `gen_expr`, say so — that would be the closure argument the record is missing.**

---

## Task 3 — and your own probes, on paper

**One of your earlier probes printed a memory address where an element value was expected.** **A later version printed the correct kind of value.**

**Read both, side by side, and answer:**

1. **What was different between them?**
2. **Which of your other probes might have printed an address and reported it as a value?**
3. **And what is the general test — how does a reader of a probe result tell an address from a value?**

**That third question is the one worth writing down.** **A probe that prints `139537424244064` and a probe that prints `7` look equally like "a number" to someone who is not expecting the difference.**

**If you have a rule for telling them apart, give it. It belongs in the project's method notes.**

---

## Task 4 — and the gate, read not run

**The gate `R137 slice is not a number` has 64 checks.** **There is also `R134 one predicate`, and a gate that builds compilers whose entries deliberately forget the check.**

**Read them and answer:**

1. **Do they cover all fourteen shapes above, or only the ones that existed when each was written?**
2. **If a new storage location were added to the compiler, would any gate fail?** **Name the gate, or say none would.**
3. **And is the deliberately-broken-compiler gate actually testing what it claims, or does it test a narrower thing?**

**A gate that covers ten of fourteen is a gate with four holes.**

---

## Task 5 — and anything else worth reading

**You have read more of this compiler than anyone.** **If there is a part of the memory model you think has been under-read — the descriptor itself, the region allocator, the escape check, the slice representation — say which and say what you would look at.**

**That is open-ended on purpose.** **The best finding of the last two weeks came from a question that was not asked.**

---

## What NOT to do

- **Do not compile or run anything.** **Not the escape tests, not any test.**
- **Do not propose a workaround for the block.** **It is understood and it is respected.**
- **Do not report a shape as "passes" from a run.** **From this round, a shape passes if you can say which check catches it and why.**

**"I could not determine this from source" is a complete and useful answer.** **It tells us where the record is thin.**

---

## What to commit

**Push to `Muse-to-Sarvam/ROUND-148-PAPER-REVIEW.md`:**

1. **The fourteen-shape table** — shape, which check catches it, certain or incidental.
2. **The fifteenth**, if you find one, or the closure argument if you do not.
3. **The probe comparison and the address-versus-value rule.**
4. **The gate coverage answer.**
5. **What you would read next.**

### The table

| # | Shape | Which check catches it | Certain or incidental? |
|---|---|---|---|
| 1 | array cell | | |
| 2 | untyped parameter | | |
| 3 | untyped return | | |
| 4 | function value | | |
| 5 | module variable | | |
| 6 | record field | | |
| 7 | raw memory | | |
| 8 | decimal parameter | | |
| 9 | arithmetic | | |
| 10 | module initializer | | |
| 11 | comparison as index | | |
| 12 | through two functions | | |
| 13 | stored in a `kosh` element | | |
| 14 | inline assembly | | |

---

## And one thing to say plainly

**Your block stopped a round, and then two more rounds asked for the same thing under a new number without knowing why.** **That is a failure of how briefs were written, not of your reporting.**

**This round asks for nothing you cannot do.** **If it turns out that something in it would need execution, say so and skip it — that is the correct response and it will be respected.**
