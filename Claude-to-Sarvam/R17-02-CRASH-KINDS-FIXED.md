# R17-02 — WS2: the six crash kinds are diagnostics now

**The compiler no longer crashes on any of the 107 inputs of R15-02, nor on 150,000 new ones.** Environment:
**Linux**, main's compiler for "before", this branch's for "after".

## Each kind, its fix, its diagnostic

| # | Input | What was wrong | The fix | The diagnostic now |
|---|---|---|---|---|
| **R1** | `yoj` as the last bytes of the file | The parser did stop with an error, **but the error printer crashed**: the end-of-file token has no source pointer, and `print_source_context` walked back from address 0. | The printer clamps the pointer into the source; an end-of-file token is shown at the end. **This one guard fixed R1, R2 and R3.** | `vyakaran dosh, pankti 1:4, shabd 'patra-ant'` with the line and a caret |
| **R2** | `prakriya f(`, `prakriya f(a,`, `prakriya f(0)q` at the end of the file | The same for the first two. For `f(0)`: an untyped parameter accepted **any** token as its name ("the historical permissive grammar"), so a number, the end of the file, or a string was stored as a name and the duplicate check crashed on it. | A parameter must be a name (an identifier, a keyword, or a builtin's name). | `vyakaran dosh … shabd 'patra-ant'`; `… shabd '0'` |
| **R3** | `rachana P = {` and `rachana P = { x,` at the end of the file | As R2: a field name could be any token. | A field must be a name. | `vyakaran dosh … shabd 'patra-ant'` |
| **R4** | `yadi … anya { } anya yadi …` | After an `anya` body, the parser looked for `anya` **again** and parsed a second one over the first. | One `anya` per `yadi`. The second is left to the statement parser, which rejects it. | `vyakaran dosh, pankti 2:59, shabd '{'` (it points into the second `anya yadi`, not at the `anya`; a sharper location is possible but needs its own message) |
| **R5** | `x + 1 = 7`, `a[1] + 1 = 2`, `likha("") = x` | Any expression was accepted left of `=` (and `+=` …, `++`); the code generator then read its first field as a name. | The target of an assignment must be a name, an element `a[i]` or a field `p.f`. **`5 = 7` and `likha(1) = 7`, which used to compile silently, are errors now.** `(x) = 7` still compiles (it is a name). | `vyakaran dosh, pankti 3:11, shabd '='` |
| **R6** | about 19,000 levels of `(`, unary `-`, or nested calls | Unbounded recursion ran out of stack. | A counter in `parse_primary`, through which every nested expression passes: **1,024 levels**, then a diagnostic. A call or a unary minus with its parentheses takes two levels, so about 500 nested calls. The block limit (128) already existed. | `Sutram Error: khand gahrai seema atikram` |

**R6's message is the block-nesting one ("khand gahrai", block depth), reused.** A message of its own
("expression nesting") would need an entry in all eleven packs, which are under review; I did not want to
write eleven translations this round. **If you want a dedicated message, say so, and it is one default plus
eleven lines.**

## The negative corpus

**`tests/negative/r17/`: nine inputs, one per crash shape**, and **`tools/crash_corpus.py`** runs them plus
twelve generated nesting inputs (parentheses, `yadi` blocks, unary minus, nested calls at 20,000 and 100,000
levels, and each at a depth that must compile). The rule it enforces, per input: **exit status 1, a diagnostic
on stdout that starts with `Sutram Error`, and no output file.** A signal or exit 0 is a failure.

- It is a gate: **"crash corpus (21 cases, 0 failed)"**.
- On v226's compiler: **14 of 21 fail.**

**Why not R70's manifest:** its loader requires exactly the six R70 categories (`CATEGORIES` is compared for
equality, and `tests/r70` tests that), so new cases there would mean changing ChatGPT's runner and its
tests. A second, small corpus with its own runner seemed the smaller change. **Say if you would rather have
them folded into R70.**

## The fuzzer afterwards

| Run | Compiler | CRASH | HANG |
|---|---|---|---|
| seed 15, 171 fixed cases + 50,000 mutations (the R15 run) | main | **107** | 0 |
| the same | this branch, after R1–R6 | 11 (all `rachana P = { x,` — R3's comma variant, then fixed) | 0 |
| seed 16, 50,000 mutations | this branch, after R1–R6 | 17 (16 `rachana … ,`; 1 empty `guna`, then fixed) | 0 |
| **seed 15, 171 + 50,000** | **this branch, final** | **0** | **0** |
| **seed 16, 50,000** | **this branch, final** | **0** | **0** |
| **seed 17, 50,000** | **this branch, final** | **0** | **0** |

The three final runs used the ROUND-17 compiler before its version string changed; the only source change
after them is `msg_version`.

## Still accepted silently (unchanged this round)

From R15-02, not crashes, not asked for, and still so: an integer literal past 64 bits wraps without a word;
`mala a[-5]` compiles and crashes at run time; a second `mukhya` is ignored; text after the program is
ignored; a source file over 64 KiB is cut without a word. **Each is a decision, not a fix I would make
unasked.**

## Checks

As R17-01's table; in addition `tools/crash_corpus.py`: 21/21 (Linux); `win/sutram.exe` on R1: the diagnostic
(Wine 9.0); Windows NOT-RUN.
