# AUDIT-01 — Correctness, at the owner's request: 150 small programs run against the compiler, each with the answer the language should give. **The code generator held: every program with a known arithmetic answer printed it.** **Six defects are not in the reference or the release notes. The worst gives a wrong number with no message: a `prakriya` that ends without `nivartanam` returns whatever was last computed.** Report only - nothing is fixed, nothing is built.

## What this is, and what it is not

- **Asked by the owner in chat (10 November 2026): "audit the compiler and improve" - correctness first, report before fixing.** It is not a Sarvam round.
- **Compiler: v321 (the staged tip, `r182-unknown-character`).** Every finding below is in code that v316-v321 did not touch, so it is in v315 on main as well: **findings 1 to 5 were also run on v315 and behave the same** (`v315.out`); finding 6 and the messages were run on v321 only.
- **Method:** `evidence-audit-01/probe.py` compiles and runs each program in `b1.txt` ... `b7.txt` and prints what it got beside what was expected; the outputs are `b1.out` ... `b7.out`. 150 programs: numbers and operators, collections, loops, names, strings, `dasham`, `prakriya`, program structure, kind confusion, and 25 with a known computed answer.
- **"Not in the documents" means:** I searched `docs/LANGUAGE-REFERENCE.md` and `docs/RELEASE-NOTES.md` for each and found nothing. **I did not trace the partners' folders round by round**; where a search there found the topic, I say so. So "new" below means "not documented", not "never seen".
- **What it cannot show:** 150 programs are a sample. Passing 25 arithmetic programs does not prove the code generator; it shows no fault was found in ordinary shapes.

## The findings, worst first

### 1. A `prakriya` that ends without `nivartanam` returns a leftover value - silently

```
prakriya f(a) {            prakriya f(a) {              prakriya f(n) {
    vitti b = a * 3            likha("in f\n")              vitti s = 0
}                          }                                chakra i = 1 tak n { s = s + i }
likha(f(5))   -> 15        vitti r = f(5) ; likha(r) -> 5   }
                                                        likha(f(4))   -> 5
```

**What it returns is whatever the last instruction left behind** - the last value computed, an argument, a loop bound. **And a `prakriya` that returns on some paths only returns a leftover on the others** (`fn_ret_some_paths`). The student who forgets `nivartanam s` in the third program gets 5 where 10 was meant, and nothing says so.
**Not in the reference** (it shows `nivartanam` in every example and says nothing of a body without one). The partners' folders mention the topic in four files I did not read through.
**The two sound fixes:** return 0 always, or refuse when a `prakriya` whose result is *used* can reach its end without `nivartanam`. The first changes the bytes of every such `prakriya`; the second refuses programs that compile today.

### 2. `krama` and `agrim` outside any loop compile, and do nothing

`krama` as the first line of `mukhya`, inside a `yadi` with no loop around it, or in a `prakriya` body: **accepted, and the program carries on** (`krama_outside`, `agrim_outside`, `krama_in_fn_no_loop`, `krama_in_yadi_no_loop`). A student who writes `krama` meaning "stop here" gets a program that does not stop.
**Not in the reference.** My own R11-R14 "what is open" files mention loop words outside a loop; I did not trace whether it was accepted or forgotten.

### 3. `mala m[n]` with a negative or very large `n` is a crash, not a message

| | result |
|---|---|
| `mala m[-3]` - written as a number | **compiles; SIGSEGV when run** |
| `vitti n = 0 - 1 ; mala m[n]` | **SIGSEGV** |
| `vitti n = 2000000000 ; mala m[n]` (16 GB) | **SIGSEGV** |
| `vitti n = 100000000 ; mala m[n]` (800 MB) | works |
| `mala m[0]` | compiles, runs |

**A `kosh`'s capacity is checked (R128, a named stop); a `mala`'s length is not.** `nirmmita(-1)` written as a number is refused when compiled; `mala m[-3]` is not. **Not in the documents.**

### 4. `likha(m)` on a `mala` prints an address

`mala m[2] ; likha(m)` prints `140373678620680`. **The same on a `kosh` was closed long ago** (`E_KOSH_DVARA`); on a `mala` it is still open. A `mala` cannot be compared or added to (`E_MALA_GANIT`), but it can be printed, and what is printed is not its numbers. **Not in the documents.**

### 5. A `kosh` is accepted as a condition

`kosh k[1] ; yadi (k) { ... }` compiles and the branch runs - a `kosh` is always "true". **A string in the same place is refused** (`E_VARTANI_SATYA`, with a hint to write `s != ""`), for exactly the reason that applies here: every `kosh`, even an empty one, is true, so the test means nothing. The student meant `kosh_gan(k) > 0` or `kosh_rikt(k)`. **Not in the documents.**

### 6. A `chakra` whose end is the largest number never ends

`chakra i = 9223372036854775806 tak 9223372036854775807 { ... }` runs for ever: after the last pass `i + 1` wraps to the smallest number, which is still "not past the end". **Exotic - no student writes this bound - but it is a loop that cannot terminate.** The release notes' section on what wraps does not mention it.

## Messages that are true and do not help (no defect in what is compiled)

Each of these is refused, correctly. **Each says only `vyakaran dosh` and a place - often the wrong place:**

| the program | the message | what it does not say |
|---|---|---|
| `likha("abc)` - a string never closed | `vyakaran dosh, pankti 4:1, shabd 'patra-ant'` | that a string opened on line 2 is not closed; it points at the end of the file |
| no `mukhya` at all | `vyakaran dosh ... 'patra-ant'` | that `mukhya` is missing |
| a `prakriya` written after `mukhya` | `vyakaran dosh, pankti 4:1, shabd 'prakriya'` | that `mukhya` must come last |
| a `prakriya` with seven parameters | `vyakaran dosh, pankti 1:30, shabd 'h'` | that six is the limit |
| `likha` with seven values | `vyakaran dosh, pankti 2:29, shabd '7'` | that six is the limit |
| `yadi a == 1 {` | `vyakaran dosh, pankti 3:10, shabd 'a'` | that the condition needs `( )` |
| `yadi (a = 1)` | `vyakaran dosh, pankti 3:13, shabd '='` | that `==` was meant |
| `likha(1e5)` | `agyat naam 'e5'` | that this form of number is not known |

**For a beginner these are the same kind of failure R182 closed: the message names what the compiler was left holding, not what was typed.** They are eight separate small changes, each a refusal that already exists and needs a sentence.

## Checked, and as documented (not findings)

- **Integer overflow wraps silently** (`a + 1` past the largest number; `4611686018427387904 * 4` is 0) - the release notes say so, with a table.
- **`chakra i = 5 tak 1` counts down** - the reference shows it.
- **`1 << 64` is 1** - the reference says the count is taken modulo 64.
- **`-7 / 2` is -3 and `-7 % 2` is -1; dividing by zero stops with `E_SHUNYA_BHAJAN`** - as the reference says, for `dasham` too.
- **A number is also an address:** `vitti a = 5 ; a[0]` is a SIGSEGV, and `a[0]` on a string reads eight raw bytes as a number. That is the raw-memory design (`vitti p = nirmmita(64) ; p[1]` is the legitimate form), and the release notes say a raw address is unchecked. **I list it because a beginner reaches it by accident, not because it is undocumented.**
- **A `dasham` given to a `prakriya` whose parameter has no kind is converted to a whole number:** `half(5.0)` with `prakriya half(x) { nivartanam x / 2 }` prints **2**, and `half(3.7)` stops with `E_DASHAM_VITTI`. Write `prakriya half(dasham x)` and it prints 2.500000. The reference says a `dasham` converts when it is whole and stops when it is not. **Documented - and still a trap: 2 where 2.5 was meant, with no message.**
- **A `chakra`'s end is read again on every pass** (`n = 5` inside the loop makes `chakra i = 1 tak n` run five times) and its variable can be changed inside the loop (`i = i + 1` gives 1, 3, 5). I did not find either stated; I did not look long. Neither is wrong, but one of them should be written down.
- **Refused as they should be:** using a name before it is declared, declaring it twice (in an inner block too), a `vitti` with no value, a wrong number of arguments (`E_ARITY`, with both counts), an undefined `prakriya`, two definitions of one, recursion without end (`E_GAHANATA`, a named stop), a number too big for 64 bits (`E_ATIPRAVAH`), arithmetic on a string or a `mala`, a string as a condition.

## The 25 programs with a known answer - all correct

Nested calls as arguments, calls inside an expression (evaluated left to right), six parameters with seven locals, `fib(20)` = 6765, recursion carrying locals (5050), compound assignment on an element, an index computed by a call, nested ternary, nested loops, `krama` and `agrim` together, `krama` out of the inner of two `yavat`, signed comparison, `dasham` comparison and mixed arithmetic, `&&` / `||` values and short-circuit, a negative index (stops), string equality and joining in a loop, a `kosh` of 100 summed. **No wrong answer found.**

## What I would fix first, if asked

1. **Finding 1** - a wrong number with no message, in the most ordinary beginner mistake there is.
2. **Finding 3** - a crash where a sentence should be; the check exists for `kosh` already.
3. **Finding 2** and **finding 5** - two refusals; each stops a program that today runs and does something other than what was written.
4. **Finding 4**, then the eight messages.

**Each is a change to what existing programs do or to which programs compile, so each needs the guard and a decision - which is why this is a report.**

## Not done

- **Nothing fixed.** As asked.
- **On v315:** findings 1-5 run; finding 6 and the eight messages not run there.
- **Windows not run.**
- **Not audited at all:** the library (`lib/`), separate compilation and linking, the foreign-function interface, the IDEs, file input and output, the language packs (frozen). The crash corpus already covers "invalid input must not crash the compiler", so I did not repeat it.
- **The partners' records were searched by phrase, not read.**
