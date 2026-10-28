# R51-00 — The writing style, from the compiler side: what each costs in NASM

**Measured on `main` `aaaa6655`, compiler v255, Linux x86-64 (cloud).** Every "today" block below was compiled and run; the
transcript is `evidence-r51/today.txt`. Line numbers are `src/sutram_compiler.asm` (24,517 lines). **Nothing is
implemented this round.**

**Three of the brief's premises are not what the compiler does today. I measured each before answering:**

| Brief says | The compiler today |
|---|---|
| P1: one labelled value takes three statements | **`likha("x = ", x)` is one statement and prints `x = 42\n`** (the two-argument form, `.ge_lk_two`, line 16142) |
| P2: the loop is C-shaped with three clauses | **The C-shape is a syntax error.** The loop is already **`chakra i = 0 tak 10 { … }`** (`.ps_for`, line 9315) |
| P4: every `mukhya` ends with `prati 0` | **0 of the 141 examples with a `mukhya` (136 top-level, 5 in subfolders) have `prati` in it.** It is optional, and the program exits 0 at its end |

**Every size below is my estimate**, from the neighbouring code each change would copy.

---

## P1 — printing a labelled value

```sutram
# today: one statement, if there is ONE value
likha("x = ", x)                      # x = 42
# today: two values on one line cost five statements
likha("x = ")
lkhb(x)
likha(", y = ")
lkhb(y)
likha("\n")
```
```sutram
# as I would have it: a string literal first, then up to 5 more values, one line
likha("x = ", x, ", y = ", y)          # x = 42, y = 7
```

- **Why:** one line of output should be one statement, for any number of values.
- **Size: small to medium.**
  - In the **emitter**: a new `.ge_lk_seq` beside `.ge_lk_two` (line 16142), about 40 lines. Like `.ge_lk_two`, it builds the
    one-argument calls itself: `likha` for a string, `lkhb` for a number, one `"\n"` at the end.
  - In the **parser**: `likha` goes from `db 1,3` to `db 1,6` in `r54_builtin_arity_table` (line 264). The parser already
    caps a call at 6 arguments (`.pp_ic_parse`, line 11486).
  - **The argument count is known at compile time.** It is the AST node's `[rbx+16]`, so nothing is decided at run time.
  - **A `dasham` value needs about 15 more lines**, for a float printer without the newline. Today `lkhb(2.5)` prints the
    raw bits, `4612811918334230528` (see the seventh idea).
- **Breaks: no.** The three-argument form already means `likha(fd, buf, len)`, the raw write. **All 55 three-argument calls in
  the tree pass `1` or `fd` first, never a string literal.** So "a string literal first" selects the new form without
  touching any existing call.
- **Is it variadic `likha` in the parser or the emitter? The emitter.** The parser only lets the count through.
- **Invisible to the guard: yes.** No existing program has a string literal first in a call with three or more arguments.

## P2 — a counted loop

```sutram
# today, and it already reads as a sentence
chakra i = 0 tak 10 {
    likha(i)
}
```
```sutram
# as I would have it: the same - leave it as it is
chakra i = 0 tak 10 {
    likha(i)
}
```

- **Why leave it:** this is what the brief asks for. Both ends are included, and `chakra j = 5 tak 1` counts down, which is
  documented in `docs/LANGUAGE-REFERENCE.md:193`. **The C-shape `chakra (vitti i = 0; i < 3; i = i + 1)` is refused today, and
  it should stay refused.**
- **Size: none.** (`.ps_for`, line 9315, 87 lines, builds `AST_FOR`; `tak` is a keyword, and `lang_to_word` handles a pack's
  own word for it.)
- **Breaks: no.**
- **One possible addition, if a step is ever wanted:** `chakra i = 0 tak 10 krame 2`. That is a new keyword, so it is a
  vocabulary question, not mine. I do not propose it.

## P3 — declaring a variable

```sutram
# today
vitti x = 5
x = x + 1
```
```sutram
# as I would have it: the same - leave it as it is
vitti x = 5
x = x + 1
```

- **Why leave it:** `x = 5` without `vitti` is an error today (`E_UNDEFINED_NAME`), **on purpose** (R4).
  - Before R4, a misspelled name was silently a new variable that read as 0: a wrong answer, with no message.
  - `vitti` is the only thing that tells the compiler a typo from a new name.
- **Size: small** to make it optional: drop the `E_UNDEFINED_NAME` check on assignment.
- **Breaks: yes.** `examples/227_assign_undeclared` and the scope tests (`228`, `229`) are negative tests built on exactly
  this error, and every typo becomes silent again.

## P4 — returning from a function

```sutram
# today: mukhya needs no prati
mukhya() {
    likha("namaste")
}
```
```sutram
# as I would have it: the same - leave it as it is
mukhya() {
    likha("namaste")
}
```

- **Why leave it:** it is already the end the brief wants.
- **One real defect behind the premise:** **`prati 3` in `mukhya` compiles and exits 0.** `.gs_ret_epilogue` (line 14491)
  always emits `exit(0)`. Only `prati dosh(c)` sets the status (R25).
- **To make `prati N` the exit status: small,** about 10 lines in `.gs_ret_epilogue`.
- **Breaks: yes, 2 programs.** `tests/stdlib/strconv_overflow.sm` (`prati 1`, 9 times, expected exit 0) and
  `tests/r29/proj/main.sm` (`prati vam(1) + dakshin(1)`). **So leave it.** At most, the docs could say the value is ignored.

## P5 — an error a beginner can act on

```
# today (ordinary compile): no file, no line, no hint
Sutram Error: agyat prakriya: brihat_yuj
```
```
# as I would print it
prog.sm:2:11: Sutram Error [E_UNDEFINED_FUNCTION]: agyat prakriya 'brihat_yuj'
Sanket: 'brihat_yuj' brihat-ghatake asti; srotasah arambhe likhatu: yoj brihat
```

- **Why:** the message should name the fix, and the fix is one line.
- **A correction: the compiler does NOT know today that the function is in the library.** It reads only the modules a
  program names with `yoj`, so it would need an index of `lib/`.
- **Size: medium-small:**
  - **An index:** `tools/lib_index.py` writes `src/r51_lib_index.inc`, mapping each of the 305 function names to its module
    (about 6 KB), generated and pinned like `src/r22_lang_builtin.inc`.
  - **The lookup and the hint:** about 40 lines at the two error sites, `.bc_old_error` (line 12447) and `.r48_found`
    (line 8365).
  - **The location:** about 10 lines. The ordinary compile prints no line today; the `--check` path already finds it
    (`r51_print_origin`, `.r48_found`).
  - **One new message key.** Under `LANGUAGE-PRIORITY.md` the frozen packs would show the default text.
- **Breaks: no.** It changes only the message of a program that does not compile.
- **Invisible to the guard: for every program that compiles, yes.** The refused programs that call a library function
  without `yoj` print the new message.

## P6 — the speakable test

```sutram
# today (since R50 this needs no flag)
मुख्य() {
    वित्ति फलम् = 2 + 3।
    लिख(फलम्)।
}
```
```sutram
# as I would have it: the same - leave the grammar as it is
मुख्य() {
    वित्ति फलम् = 2 + 3।
    लिख(फलम्)।
}
```

- **Read aloud:** *"mukhya. vitti phalam = 2 + 3. likha phalam."* Every word is Sanskrit, but **it is not a sentence.** It
  has no verb at the end and no case endings, and the `=`, `(` and `{` are not words.
- **Why leave it:** a program that reads as Sanskrit prose needs a different grammar, with verb-final order and endings that
  carry the roles. **That is a second language, not a feature.**
- **Size: large.** Every statement parser below `parse_body` (line 7221) would change.
- **Breaks: yes, if it replaced the current grammar.** If it were added beside the current grammar, it would be two
  grammars to keep correct.
- **What already helps, and costs nothing:** Devanagari keywords, the danda `।` as a terminator, and Devanagari names.

---

## Which are invisible to the guard

| | Change | Invisible? |
|---|---|---|
| **P1** | `likha` with a string literal first and 3 to 6 arguments | **Yes.** No existing call has this shape |
| P2 | none | yes (nothing changes) |
| P3 | `vitti` optional | **No.** It breaks the negative tests and hides typos |
| P4 | none (or `prati N` as the exit status: **no, 2 programs**) | yes, if left |
| **P5** | the hint and the location | **Yes for every compiled program.** Only refused programs' messages change |
| P6 | none | yes (nothing changes) |

## Which first: P5

**It is the only one of the six that fixes something a beginner hits today with no way out.**

- It touches only the error path, so no executable changes.
- The location half is already written, in the `--check` path.

**P1 second:** it is also invisible to the guard, but today's two-argument form already covers the commonest case.

## The seventh idea: say what the parser already knows

**The parser knows the builtin's name and how many arguments it takes. When a call has the wrong count, it reports a
syntax error at the `)` instead.**

```
# today: likha() , or kosh_push(5)
Sutram Error: vyakaran dosh, pankti 2:11, shabd ')'
      likha()
          ^
Sanket: asmin sthane shabdam vyakaranam cha pashyatu.
```
```
# as I would print it
prog.sm:2:5: Sutram Error [E_ARITY]: 'likha' ityasmai 0 tarkah dattah; 1 - 6 apekshitah
```

- **The message already exists and is never used:** `r54_msg_arity` (line 254) is defined and referenced nowhere.
- **The check exists too:** `r54_builtin_arity_ok` (line 11670) knows the expected counts, but the parser answers its
  failure with `jz parse_error` (line 11598).
- **Size: small,** about 20 lines at line 11598, using the E_ARITY wording that user functions already have.
- **Breaks: no. Invisible to the guard:** only programs that do not compile change their message.

**Two more of the same kind, found while measuring.** Each is silent today, and each is small to make loud:

- **`likha("x = ", x, 9)` compiles and prints nothing.** It is taken as the raw write `likha(fd, buf, len)`, with a string as
  the file descriptor. P1 would turn this exact shape into the useful form.
- **`lkhb(2.5)` prints `4612811918334230528`,** the double's bits as an integer. The emitter knows the argument is a
  `dasham` and prints it as an integer anyway.

## The rules

- Nothing here needs a runtime, a collector or a tool beyond one generator script.
- No English keyword is introduced; the only new words are message text, in the existing romanised Sanskrit.
- Nothing proposed changes a program that compiles today, except P3 and the P4 alternative, which I recommend against.
