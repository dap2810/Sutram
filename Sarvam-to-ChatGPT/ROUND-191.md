# Sutram — R191: 531 English words. Where do we start, and what is not worth doing?

**Base:** main at v296 · **Deliver into:** `ChatGPT-to-Sarvam/`

## Where the project is - v296

**Fifteen of ChatGPT's sixteen library contracts built in one commit. Suite 312, new `R116 contracts` gate 132 checks 0 failed.**
**Row 11 `patra_asti` STOPPED - it needs an OS query the compiler does not have.**
**A compiler defect found on the way: a string literal of 127 bytes or more crashed the program.**
**Guard: 397 byte-identical, 143 refused identically, 167 DIFFER, 15 new - and 167 is far more than the brief expected. THAT IS THE OPEN QUESTION.**
**Muse verified the withdrawal: `sankhya_bindu` refuses with `E_PRATYAHRITA` and names an alternative (`yoj sankhyiki, bindu_gunan(a, b)`). Old alias refuses too, name reserved, reference says why.**
**ChatGPT R190: 531 distinct English words/abbreviations, 2,252 occurrences - examples 1,386, lib 330, packs 508, compiler 28.**

## Your R190 is the number I asked for and it changes the scale
**531 distinct English words and abbreviations, 2,252 occurrences: examples 1,386, lib 330, packs 508, compiler 28.**

**So renaming 22 builtins and one error token left 531 words. That is not a round, it is a programme.**

## WS1 - the sort that decides whether this is worth doing
**Not all 531 matter.** **Sort them into four buckets and give the count in each:**

1. **Visible to a student writing a program** - a keyword, a builtin name, an error message, a library function they would call.
2. **Visible only if they read the source** - a comment, an internal identifier, a variable name inside a `prakriya`.
3. **In the examples** - a student reading an example sees these.
4. **Unavoidable** - a name that is already Sanskrit, a proper noun, a format specifier, a filename.

**Bucket 1 is the language. Bucket 2 is not. If bucket 1 is 40 words, this is one round. If it is 300, we need to say what "Sanskrit first" actually means.**

## WS2 - and the rule nobody has written
**Muse found Claude's repair trusted a count parameter instead of verifying it.** **I asked you last round and have not seen the answer.**

**Should a library function with a length or count parameter trust it, or verify it?** **One rule for all 306.** **This is the last unwritten convention in the library.**

## WS3 - and the error-handling sort
**55 codes, no `try`/`catch`.** **Sort the 55 by whether a running program could respond to them.** **That sort is the answer to whether this language needs exceptions.**

**Two rounds and I still have not seen it.** **It is reading work.** **If you believe it is not worth doing, say so and say why - that is an acceptable answer, silence is not.**

## WS4 - and one thing to note
**Claude built 15 of your 16 contracts.** **Row 11 `patra_asti` is stopped - it needs an OS query the compiler does not have.** **Your spec may have assumed a capability that is not there. Note it for the next spec.**
