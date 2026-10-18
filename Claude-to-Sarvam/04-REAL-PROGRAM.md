# WS4 — A real Sutram program: `04-ankatalika.sm`

**Date:** 2026-10-18 · **Base:** main at v162, commit `feef075` · **Files:** `04-ankatalika.sm` (214 lines),
`04-ankatalika.expected.txt` (its exact stdout)

---

## 1. What it is

A class marks ledger (अङ्क-तालिका). It holds one class's marks, prints a ranked ledger with grade bands
and a bar per ten marks, sorts a copy to get the ranking and the median, prints mean / standard
deviation / min / max to two decimals, draws a grade histogram, computes the pass rate, and prints the
term's fee totals in **Indian digit grouping** (`Rs 1,23,52,500`). It is the kind of thing a school
clerk would actually want, and it exercises the parts of the library a beginner would reach for.

**Five library modules:** `sankhyiki` (statistics over `kosh dasham`), `suchi` (dynamic list, merge
sort, sum), `roop` (fixed decimals, Indian grouping, column padding), `ganit` (`adhik2`/`laghu2`,
`ghat`), `ank` (`asti_yugm`). Plus the builtins `kosh_*`, `nirmmita`, `likh8c`, the three-argument
`likha(1, buf, n)` byte write, and `lkhb`.

## 2. What I actually ran

```sh
nasm -f elf64 -I. src/r68_compiler_entry.asm -o /tmp/s.o && ld -o sutram_compiler /tmp/s.o
./sutram_compiler Claude-to-Sarvam/04-ankatalika.sm /tmp/ankatalika.bin
/tmp/ankatalika.bin > Claude-to-Sarvam/04-ankatalika.expected.txt ; echo "exit=$?"
./sutram_compiler --check Claude-to-Sarvam/04-ankatalika.sm
cd /tmp && /home/claude/sutram/sutram_compiler /home/claude/sutram/Claude-to-Sarvam/04-ankatalika.sm a2.bin \
  && ./a2.bin | diff - /home/claude/sutram/Claude-to-Sarvam/04-ankatalika.expected.txt && echo IDENTICAL
sha256sum /tmp/ankatalika.bin /tmp/a2.bin
python3 -c "import statistics as s; m=[91,67,78,34,88,59,95,72,45]; print(sum(m)/9, s.pstdev(m))"
```

## 3. What I observed

```
OK: compiled 32785 bytes
exit=0
Sutram janch: OK (nirgat binary nahi)
IDENTICAL                                  (compiled from /tmp — module path resolves via /proc/self/exe)
4449c5a4b982a07b591e…  /tmp/ankatalika.bin
4449c5a4b982a07b591e…  /tmp/a2.bin         (byte-identical binary from two cwds)
69.88888888888889 19.745291671937302       (python; program prints 69.89 and 19.75)
```

Full stdout is in `04-ankatalika.expected.txt`; the first lines:

```
=== Anka-talika: kaksha 10, varshik pariksha ===
Vidyarthi: 9

Kramank  Anka  Shreni  Dand
      1    91  A       #########
      2    67  C       ######
      …
Kram (uttam se nimn): 95, 91, 88, 78, 72, 67, 59, 45, 34
Madhyama (median): 72
Yog (total):       629
Madhya (mean):     69.89
Vichalan (std):    19.75
Nyuntam / Uchchtam: 34.00 / 95.00
Prasar (range):    61
…
Kaksha shulk yog:      Rs 12,35,250
Das varsh ka anuman:   Rs 1,23,52,500
```

Checked by hand: sum 629, mean 69.89, population σ 19.75, median 72 (sorted middle), range 95−34 = 61,
137,250 × 9 = 1,235,250 → `12,35,250`, × 10 → `1,23,52,500`. Grade bands A/B/C/D/F = 2/2/2/2/1, pass 8/9
= 88 %.

## 4. What the language is like to use — observations from writing it

These are observations, not defects, unless marked.

1. **Builtin names are reserved everywhere and the error does not say so.** My first draft used a local
   `vitti band = 65`; `band` is the close-handle builtin, so the compiler said `parse error … near token
   'band'` — the same message as for any typo. A beginner cannot tell "reserved word" from "syntax
   error". Related: `yog`, `gan`, `adhik`, `laghu`, `varg` are library function names a learner will
   also want as variable names once the module is imported.
2. **Defect (WS1 F12):** with modules imported, the normal-mode parse error gave **line 2020** for an error
   on line 175. `--check` gave 175. Writing this program without `--check` would have been painful.
3. **`likha` has three personalities** — `likha("text")` prints no newline, `likha(number)` prints a
   newline, `likha("text", number)` prints both and a newline, `likha(1, buf, n)` is a raw byte write.
   `lkhb` prints a number without newline but prints the *address* of a string literal. Once learned
   it is fine; it is not in `LANGUAGE-REFERENCE.md` in that form.
4. **Byte strings from `roop` need the `likha(1, buf, n)` idiom**, which no document outside
   `tests/stdlib/fmt_*.sm` shows. A one-paragraph "how to print what `roop` returns" would save every
   new user an hour. (`04-ankatalika.sm` wraps it in `likh_dasham_2` / `likh_rupaye` for that reason.)
5. **`mahattam`/`laghuttam` are GCD/LCM, not max/min** (`adhik2`/`laghu2` are max/min). I used the wrong
   pair first and got `-1529` for a range. `LANGUAGE-REFERENCE.md:127` lists them without meanings; the
   sample at line 143 shows `mahattam(48, 36) # 12`, which is the only hint.
6. **`sankhyiki` is typed on `kosh dasham`**, so integer marks must be pushed twice (an integer `kosh`
   for indexing and sorting, a `dasham` kosh for statistics). Not wrong, but a learner will ask why.
7. **No string variables in the ledger.** Printing student names from a table of literals is awkward
   (an array of string pointers plus `shabda` works, but I kept the program to marks). A `varna` list
   example in the docs would help.
8. **What was pleasant:** the module system "just worked" with five imports from any cwd; `kosh` and
   `suchi` were predictable; `roop_varg_ank(v, 1, out)` giving lakh/crore grouping in one call is a
   genuinely Indian touch no other language offers out of the box; `--check` is fast and its messages
   with source context are good.

## 5. What I did not do, and why

- Did not add the program to `examples/` or `tests/expect/` — those are gated corpora; the owner decides
  whether it becomes example 220 with a golden. The `.sm` and the expected output are here so it can be
  dropped in unchanged.
- Did not read input (`grahan`) — the brief asked for something that compiles and runs with an exact
  command; fixed data keeps the expected output exact.
- Did not test on Windows.
