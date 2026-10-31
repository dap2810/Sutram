# R81-00 — `parikshita` is built: transitive, refused at the first bad edge; the library can use 63 of 306 functions, and the rest need a language feature, not conversion

- **Commits on `main`, in order:** `39ed6b2` (1/3 **v277**: the checker, examples 282–285, the formatter) · `625bac0` (2/3 the gate) · then the reference §20, the changelog and this hand-back with `evidence-r81/`. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v277) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=253`, FAIL=0** (four new examples, 282–285). Library proofs **229/229**. Property
  proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 56 PASS / 0 FAIL / 1 NOT-RUN (Windows execution)** — one new, **`R81 parikshita`** (24 cases).
- **The guard, v276 (origin/main) → v277, `tools/guard_pair.py`, all three paths (Linux ELF, Linux PE, the Windows
  compiler under Wine): 663 programs — 535 byte-identical, 124 refused identically, 0 DIFFER, 4 new.** The Windows compiler's 535 outputs are byte-identical to the Linux compiler's PE outputs.
  **Unmarked code is untouched, in bytes**: the checker runs only on marked bodies and emits nothing.

## WS1 — `parikshita prakriya`, built

**The form.** `parikshita` directly before `prakriya` or `mukhya`. It is contextual, as ChatGPT R149 proposed: not
a new keyword, no pack changed, and elsewhere still an ordinary name (`vitti parikshita = 4` compiles, a case in
the gate). Before anything else it is `E_PARIKSHITA_STHAN`.

**What is verified.** After the whole program is parsed — so every definition is known, and recursion and forward
calls work — the compiler walks every marked body, before, inside and after each `mandapa`. **What it does not
know is refused, not warned, and no output file is written.**

| in a checked function | verdict |
|---|---|
| a call to another `parikshita` function | allowed — and that function is itself checked, so the rule is **transitive** |
| **a call to any other `prakriya`, a library one included** | **`E_APARIKSHITA_AHVAN`, at the call's line and column, naming the callee** |
| `likha` (not its raw `likha(fd, buffer, count)` form), `likha_fmt`, `grahan`, `nirmmita` | allowed: the trust base, four builtins |
| any other builtin (`likh8`, `pad8`, `akshar`, `akshar_rakh`, `smaran`, `shabda`, `kosh_*`, files…), `kosh`, `rachana` fields, slices, function values, `prasar`, `yadi dosh`, inline assembly | `E_APARIKSHITA_KARYA`, naming it |
| `a[i]` on a `mala` declared in the function; `p[i]` where `vitti p = nirmmita(NUMBER)` and `p` is never assigned again | allowed — both are bounds-checked (R78, at run time or when compiled) |
| **`x[i]` on anything else** — a parameter, `p + 8`, a size computed at run time | **`E_APARIKSHITA_SMRITI`, at the `]`** |

**The test that matters, as you wrote it** — `examples/283`:

```
yoj mala
parikshita mukhya() {
    ...
    likha(mala_yog(p, 3))
}
```
```
283_r81_parikshita_refuses_library.sm:10:11: Sutram Error [E_APARIKSHITA_AHVAN]: parikshita prakriya 'mukhya' aparikshitam prakriyam 'mala_yog' ahvayati
      likha(mala_yog(p, 3))
            ^
Sanket: parikshita prakriya keval parikshita prakriyah ahvayitum shaknoti - 'mala_yog' api 'parikshita prakriya' bhavet, athava ahvanam tyajyatam
```

*(checked function 'mukhya' calls the unchecked 'mala_yog'; a checked function may call only checked functions —
mark 'mala_yog' too, or drop the call.)* **Transitive, at the first bad edge** (`examples/284`): `mukhya` →
`dugna` (checked) → `ek_adhik` (not) is refused at `dugna`'s call, not at `mukhya`.

**Unmarked → checked:** an unmarked caller may call a checked function with numbers (a case in the gate). A
checked function cannot receive a buffer: indexing a parameter is refused (`examples/285`). **Under `--separate`
the verdict is the same** — accepted and refused alike (`evidence-r81/separate-compilation.txt`).

**The gate can fail.** `tests/r81_parikshita/test_parikshita.py`: a checked chain and a recursive pair accepted;
an unmarked leaf, an unmarked library function, a marked *prototype* over an unmarked definition, a function value, seven raw constructs, four
unbounded indexes refused; an out-of-range `mala` index still stopping at run time. **Against a checker switched
off it fails 15 of 24; with transitivity switched off, exactly the 3 call cases** (`evidence-r81/gate-calibration.txt`).

## WS2 — the honest part: **63 of 306 functions, and the rest is not a conversion job**

I marked every `prakriya` in a copy of the library and compiled each module. On each refusal I unmarked the
function named, and repeated until all 24 compiled — so a function that calls a refused one is refused in its
turn, and what is left is exactly what passes. Then I confirmed every module compiles with those 63 marked
(`evidence-r81/ws2-library-size.txt`, the script beside it).

| | |
|---|---|
| **modules that could be marked whole** | **3 of 24: `ank` (10), `madhava` (5), `sadhan` (7)** |
| functions that pass unchanged | **63 of 306** — the three above, `ganit` 17/18, `ganita` 13/23, `chandas` 5/6, and one each in `anukram`, `mala` (`mala_nava`), `samanvaya`, `varna` (2), `sankhyiki` |
| modules with none | **13**: `aadhar`, `brihat`, `gudh`, `kalana`, `khand`, `nighantu`, `patra`, `phal`, `roop`, `sangrah`, **`shreni` (sorting)**, **`suchi` (lists)**, `vakyank` |

**Why the other 243 — followed to the function that fails on its own:**
- **131 read or write a buffer they are given** (`mala_yog(p, n)`, every sort, every list). A checked function
  cannot be given storage: nothing says how long the block behind an address is. **That is a language feature —
  a bounded buffer parameter (R149's "view") — not a rewrite.**
- **112 use a builtin outside the trust base:** `akshar` / `akshar_rakh` (bytes of a string) 63, `kosh_len` 18,
  `likh8` / `pad8` 21, `vartani_aayam` 7, `dvaram` 3. Each needs a checked form first (checked strings, a
  checked `kosh`).

**Muse's R81 count is different, and both are right for their rule.** Muse counted from the sources:
**281** with no `kosh`, **128** with also no memory access through a parameter — treating every other builtin as
neutral. The checker as built also refuses the raw byte and qword builtins (`akshar`, `akshar_rakh`, `likh8`,
`pad8`, …) and every function that reaches one, which gives **63**. Admitting those builtins would raise the
count, but they read and write through addresses with no known extent — what the boundary exists to stop.

**So: none of the 243 without work on the language.** The 63 are the pure-number functions; marking them is one
word each, and I have not done it, as you asked. **What it means for a student today:** a checked program can
compute and print, allocate in a block, and use its own `mala`; it can call no library function (none is
marked); and **a checked sort must be one function**, because it cannot pass its array to a helper
(`examples/282` is exactly that, and it is accepted).

## WS3 — the one thing you wanted to see work

**`examples/282`: a `parikshita mukhya` that makes twelve numbers with a checked helper, sorts them in a
`mandapa` (insertion sort), and prints them** — accepted, and matches Python (`8 25 30 36 38 47 55 57 67 76 86 89`).
**The same program calling an unmarked library function is refused with the call named** (`examples/283`, above).

## What is partial, said plainly

- **A refused builtin or construct is reported at the function's `parikshita`, not at its own line** — builtin
  nodes keep no source position; the message names it (`'likh8' parikshitum na shakyate`). Calls and indexes
  have their exact position.
- **`mala_nava` passes**: it allocates and returns the address as a number. No checked code can index that
  address (it is not a `nirmmita(NUMBER)` name), so it is harmless here — but it is R149's "raw-pointer
  factory", and a stricter rule would refuse returning an address at all. Not done.
- **`mala` indexes are recognised by name within the function** (a shadowing `mala` and scalar of the same name in
  two blocks would be confused). Not seen in the tree.
- **Not done (R149's list):** bounded views, checked handles, interface hashes for separately compiled objects
  (the importer rechecks the module's source instead, which R149 allows), effect tracking for globals.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs (no pack text; the messages are Sanskrit
  in every pack), `MEMORY-DECISION.md`. **Not run:** real Windows (Wine only).
