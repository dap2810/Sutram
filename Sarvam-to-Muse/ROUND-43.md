# Sutram — ROUND-43: Sarvam → Muse

**Base:** main at **v359**, compiler **v249** · **Deliver into:** `Muse-to-Sarvam/`

## READ FIRST
`/LANGUAGE-PRIORITY.md` and `docs/PATH-TO-COMPLETION.md`. If this brief conflicts, they win.

## THE TASK: the lexer, so a Sanskrit word is never blocked by a keyword prefix
**`prati` is the `return` keyword. A library function called `vartani_pratilip` (string-copy) must be legal.**
**Today we do not know whether it is** - and the project has been choosing worse words to avoid the question
(`anuk` instead of `pratilip`). **The owner wants this solved permanently.**

## Part 1 — Your job: the INDEPENDENT test, not the fix

**Claude is implementing the fix. You are the second reading - which is what caught r18 and `meru_pankti`.**

### WS1 — TEST THE LEXER AS IT STANDS, INDEPENDENTLY
**On main v249, before Claude's change lands, answer these five questions with a compile and the exact output:**
1. **Does `prakriya vartani_pratilip(...)` compile?**
2. **Does a CALL to `vartani_pratilip(x)` compile, or is it tokenised as `prati` + `lip`?**
3. **Does `vitti pratiX = 1` compile?** (a variable whose name starts with a keyword)
4. **Does a Devanagari identifier beginning with a Devanagari keyword compile** - e.g. `प्रतिलिपि` where `प्रति` is a
   keyword?
5. **Does `mukhyata` (keyword `mukhya` + `ta`) compile as one identifier?**

**Report each as PASS / FAIL with the compiler's exact message.** **This is the baseline the fix will be measured
against.**

### WS2 — the guard: state the number.
### WS3 — nothing else this round. **Do not implement the fix; Claude is.**

## Part 3 — Constraints
Least privilege. **PASS / FAIL / NOT-RUN separately.** **Do not touch `backups/` or a frozen pack.**
