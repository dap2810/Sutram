# R190-00 — The loop that runs no times: **I chose none of your three as written, and measured why.** Counting down when the loop runs would make every loop over an empty collection run twice. Refusing when it runs would stop it. Refusing `chakra i = 5 tak 3` when compiled would refuse the documented countdown, which works. **What v326 does: it warns, when the program is compiled, for the one shape that is nearly always a countdown - `chakra i = n tak 1` - and both books, which said the loop "counts down automatically", now say what is true.** `chakra i = 5 tak e` stays silent, and I say below why it must until the language has a word for counting down. **And the shared state is wrong about the converter: `varna_tak_ank` does not take a string. `"42"` gives 0.** A function that does is added.

## Release line

```
main  (the commit carrying this file; SHA in my chat report)   Sutram 1.0 (v315) - sampurna sutra, unchanged
staged r190-chakra-and-converter c3b7b9ef   Sutram 1.0 (v326) - sampurna sutra     (on r189-audit-fixes 22466bda = v325)
     crash corpus: 227 cases + manifest, 0 failed
     suite: NO-EXPECTATION=4 PASS=332 (336 run; example 364, with a golden) · contracts (R116): 139 checks, 0 failed
     gates: 93 PASS / 0 FAIL / 1 NOT-RUN  (Linux, Xvfb; NOT-RUN = Windows execution; evidence-r190/gates-v326.txt)
     installer (payload v326): 160a1ab6f38b5263aabfd625aad3e624f705d9fd2d524c05644c197b7405f4fc
     the guard, v326 against v325: 788 programs - 581 byte-identical, 196 refused identically, 10 DIFFER, 1 new
            (Linux and Windows executables, the same line)
            the 10 all bring in `vakyank`, which has one more function; all 10 print the same and exit the same
            the compiler's change is a message: it changed the bytes of no program
```

Sanskrit only; no pack touched; `backups/` untouched. `R159 no personal paths`: 0. Not merged.

## WS1 - the four questions

**1. Why - the code.** `src/sutram_compiler.asm`, in the `chakra` generator, under the comment *"Direction
detection: descending when both bounds are constants and start > end"*. It sets `for_descend` to 1 **only when
the start node and the end node are both `AST_NUM`** and the start is larger. That one flag then chooses two
things: the step (`+1` or `-1`) and the test before every pass (`i <= end`, or `i >= end`). **The end is not
required to be a number - any expression is accepted - and when it is not a number the loop is compiled as
counting up.** So `chakra i = 5 tak e` stores 5, tests `5 <= e`, finds it false, and leaves. It does not compare
"the wrong way"; it never chose a way.

**2. What a descending loop does, and whether it is documented.** `chakra i = 5 tak 3` counts **5 4 3**. It is
documented: the reference shows `chakra j = 5 tak 1  # for (descending)`, `examples/36_descending.sm` is named
for it, and **both books had a section "Descending Loops" that said: "If the start value is greater than the end
value, the loop counts down automatically."** **That sentence is the defect a student meets.** It is true of
written numbers and false of everything else. **So: the code does what it was built to do, the design is
inconsistent, and the books taught the inconsistent half as the rule.**

**3. The sibling, `chakra i = 1 tak 0`.** **It runs twice: 1, then 0.** Written numbers count down. And
`chakra i = 0 tak -1` runs 0, then -1. **So a student who writes an empty range in numbers gets two passes, and
one who writes a countdown in variables gets none.**

**4. Both ends expressions, `chakra i = a tak b`.** With `a = 5`, `b = 3`: **no passes.** With `a = 1`, `b = 0`:
no passes. With `a = 3`, `b = 5`: 3 4 5. **The problem is not "one end a literal". It is "not both ends
literals".** The whole table, measured (`evidence-r190/before-after.txt`; pinned in the gate):

| written | runs |
|---|---|
| `5 tak 3` · `1 tak 0` · `0 tak -1` | 5 4 3 · **1 0** · **0 -1** |
| `a tak b` (5, 3) · `a tak b` (1, 0) · `5 tak e` (3) · `n tak 1` (5) | **nothing** |
| `a tak b` (3, 5) · `3 tak 5` | 3 4 5 |

## The decision

### Why not "make it count down"

**Because when the loop runs, a countdown and an empty range are the same thing.** `chakra i = 5 tak e` with
`e = 3`, and `chakra i = 0 tak n - 1` with `n = 0`, both arrive with the start past the end. The second is how
every loop over a collection is written: **24 of the 157 `chakra` loops in the examples, tests and library end
in `... - 1`.** Counting down would run each of them twice on an empty collection - `i = 0`, then `i = -1` - and
the body would read element -1. **That replaces a loop that silently does nothing with a loop that silently
reads outside its data.** `chakra i = 0 tak -1` in written numbers already does exactly that today.

### Why not "refuse it" when the loop runs

**Because it stops every program that loops over nothing.** Measured with a compiler built for the measurement
(`evidence-r190/probe.patch`; never shipped): `examples/362_r186_patra_sankhya_yoga.sm` on an empty file prints
`yogah: 0` today. With the refusal it stops. **An empty file, an empty `kosh`, a count of zero are ordinary; a
language that stops on them teaches a student to fear loops.**

### Why not "refuse it" when compiled

**`chakra i = 5 tak 3` cannot be refused, because it works and is documented:** 18 loops in 12 files count
down in written numbers. **And the case that is wrong - a variable - cannot be refused when compiled, because
the compiler does not know its value.**

### What is true, and what I did

**The silence cannot be removed for every shape without a way to say "count down" in the language.** An
inclusive range that guesses its direction cannot express "empty". That is the design defect, and its fix is a
word - a language addition, and the owner's.

**What can be done now, and is done in v326:**

1. **A warning when the program is compiled, for the shape that is nearly always a countdown:** a start that is
   not a number and an end that is - `chakra i = n tak 1`, `chakra i = n - 1 tak 0`.

   ```
   Sutram suchana: chakra 'i' urdhvam eva ganayati - arambhah antat adhikah chet ekavaram api na chalati; avarohaya 'yavat' likhatu
   ```

   ("the `chakra` counts up only; if the start is past the end it runs not even once; to count down write
   `yavat`".) On stderr, the program compiled and unchanged. **Why that shape: nobody counts *up* from a variable
   to a fixed 1 or 0. In the 157 loops of this tree, none has it - so the warning costs nothing that exists.**
   It fires on the shape, not the values: `chakra i = n tak 5` with `n = 3`, which is correct, is warned about
   too. **That is its cost, and I think it is the right one.**
2. **Both books corrected.** "Descending Loops" now says: only with written numbers; with a variable the loop
   counts up and may run no times; the `yavat` form to count down, as a program.
3. **The reference, §6a:** the table above, the reason, and the warning.

**What stays silent, and I will not pretend otherwise: `chakra i = 5 tak e`, and `chakra i = a tak b`.** They are
also the shapes of `chakra i = 1 tak n` and `chakra i = lo tak hi` - every ordinary loop. **Your example is the
one I cannot warn about.**

**You said refusing teaches better than documenting. I agree, and a warning is the nearest thing to a refusal
that does not refuse a correct program.** If the owner would rather have a refusal for `n tak 1`, it is one
branch instruction away from the warning - and it would refuse `chakra i = n tak 5` as well.

### The number that surprised me

**Of the 591 programs in the guard's set that run, exactly one enters a `chakra` with its start past its end**
(`evidence-r190/probe-run.txt`). **It is `examples/115_perf_loop_bottom.sm`, and it does so on purpose:**

```
vitti lo = 5
vitti hi = 3
vitti empty = 0
chakra k = lo tak hi { empty = empty + 1 }      # golden: 0
```

two lines below `chakra d = 3 tak 1`, whose golden is the countdown. **So both halves of this behaviour were
written down as intended, in one test.** That is why I call it a design and not a slip - and why "count down"
would have changed a golden that was put there to stop exactly that.

## WS2 - the proof

1. **Wrong today** (v325): `chakra_5_tak_e.sm` prints `end` and nothing before it. No message.
2. **After** (v326): the same program prints the same - **unchanged, as explained.** `chakra_n_tak_1.sm`
   compiles with the warning above and runs the same.
3. **The guard against v325: 10 DIFFER, none from the loop.** The compiler's change is a message on stderr;
   **581 programs are byte-identical and none of the 787 is warned about.** The 10 that differ all bring in
   `vakyank`, to which WS4 adds a function, and all 10 print and exit the same (`differ-run.txt`). **No program
   in the set "relies on the zero-pass behaviour" by mistake; one relies on it by design.**
4. **Suite 332, corpus 227 / 0, contracts 139 / 0, gates: above.**

**Gate `R190 chakra and converter`: 19 checks.** Sixteen pin the loop: every row of the table, both spellings,
`yavat`, which shapes are warned about and which are not, and that the warned loop is the same program.

## WS3 - the other loop forms

| form | the same defect? |
|---|---|
| `chakra ... arabhya ... paryantam` | **yes - it is the same loop.** `5 arabhya e paryantam` with `e = 3`: no passes; `5 arabhya 3 paryantam`: 5 4 3 |
| `yavat (cond) { }` | **no.** The student writes the condition; there is no direction to guess. Counts 5 4 3 from a variable |
| `kuru { } yavat (cond)` | **no**, the same; its body runs once before the test, as it should |
| `krama`, `agrim` | not loops: leave the loop, and go to the next pass. **No form has a step.** |

**The family does share a comparison, and it is the one in `chakra`.** `yavat` and `kuru` take theirs from the
program.

## WS4 - the converter: the premise is wrong, and here is what is true

**`varna_tak_ank(buf, n, ok)` does not convert what `vartani_grahan()` returns.** Run (`conv1.sm`):

| the line typed | `varna_tak_ank(s, vartani_aayam(s), ok)` |
|---|---|
| `42` | **0, `ok` 0** |
| `-17` | 0, `ok` 0 |
| `12345678` | 0, `ok` 0 |
| `7` | 7, `ok` 1 - by accident |

**It reads one character code per eight-byte cell of a `mala`; a string is one byte per character.** Its own
header says so ("Buffers are mala of integer character codes (not byte-packed strings)"). `7` works because a
one-character string followed by zero bytes happens to read as the number 55. **So the Python model was not
already there: there was `input()`, and an `int()` for a different kind of text.** The three lines did not exist.

**They do now.** `vartani_tak_ank(s, ok)`, in the same module, with its sibling's rules - I did not invent any:

```
yoj vakyank

mukhya() {
    mala ok[1]
    vitti s = vartani_grahan()            # read a line
    vitti n = vartani_tak_ank(s, ok)      # convert it
    likha(n * 2)                          # use it
}
```

- **The name** follows `varna_tak_ank`, `ank_tak_varna`: `vartani` is the language's word for a string.
- **"Not a number" is `ok[0] = 0`** - the module's own convention.
- **Strict, as `varna_tak_ank` is:** digits and one leading `-`. **It reports everything `grahan()` gets wrong:**
  `abc`, `5abc`, `12 34`, ` 42`, `+5`, `-`, an empty line, a number past the largest `vitti` - each is `ok` 0.
  Text longer than 31 characters is `ok` 0 too (a number that fits has at most 20), which keeps its scratch a
  fixed size; the scratch is given back.
- **In the reference (§4d), in both books** (a section after `vartani_grahan`), the README, and
  `examples/364_r190_vartani_tak_ank.sm` with a golden.

**This is R189's option B, built.** In R189 I said three choices were the owner's - the name, the failure
signal, what counts as a number. **The module already had an answer to all three, so I took them.** If the
owner wants any of them otherwise, it is one function to change.

## WS5 - the audit rows: one is wrong, one is right and understated

I wrote "two of the audit's own rows are wrong". **That was loose. Precisely:**

- **R19 is wrong.** It says the sentence "an empty string is still true in `yadi (s)`" contradicts the refusal
  `E_VARTANI_SATYA` and should be removed. **The sentence is true where it stands:** it is about values the
  compiler does not know are strings. `vitti g = ""` at module level, then `yadi (g)`, compiles and runs the
  branch; so does a `mala` element holding `""`. The refusal covers known strings only. **Kept, and made
  precise.**
- **R18 is right, and says too little.** It calls the braces section "obsolete". **The section said a
  `prakriya` of three lines without braces "does NOT compile", and called that verified. It compiles and prints
  12.** The quoted failure came from a file with no `mukhya`. **Rewritten.** That is a Tier 1 sentence - guidance
  that makes a student add braces for a reason that is false - filed as Tier 3.

**And one of mine that the audit had right:** in R186 I wrote that `dvaram` and `paadh` return -1 on failure.
They return the system's negative error code (-2, -9). ChatGPT's row said so; mine is corrected in v325.

## Not done, and why

- **`chakra i = 5 tak e` and `chakra i = a tak b` still run no times in silence** - stated above, in the books,
  the reference and `docs/WHATS-LEFT.md`. **The sound fix is a word for counting down. I did not design one:
  it is a language addition.**
- **`chakra i = 1 tak 0` in written numbers still runs twice** - stated in the reference's table. A warning
  for it is possible (both ends known when compiled); **not done, because the written countdown is the
  documented feature and I could not tell `1 tak 0` from `5 tak 3` by anything but taste.**
- **Windows: not run.** Under Wine (`evidence-r190/wine.txt`) the Windows compiler prints the warning for
  `chakra i = n tak 1` and none for `5 tak e` or `5 tak 3`, the three loops run as on Linux, and `vartani_tak_ank`
  accepts and reports the same lines. **Wine is not Windows.**
- **The warning is not shown in a `--lang` run** - the packs are frozen, and it would be untranslated there.
- **The Windows checklist is reissued for v326** (`Claude-to-Sarvam/SUTRAM-WINDOWS-ACCEPTANCE.md`): commit
  `c3b7b9ef...`, installer `160a1ab6...`, compiler `F22FEA3F...`. Every pinned file was downloaded from GitHub
  again and its hash matches; every expected output was taken again under Wine and is v325's except the version
  line (`evidence-r190/checklist-v326/`). **It does not test the new warning or the converter** - both are in the
  gates. **Its PowerShell blocks are still NOT RUN.**
