# R9-01 — WS1: F1 as files

**F1 reproduces on v188, on Linux and with the Windows compiler under Wine. It is not fixed on the branch.**
The defect is real. **My R8 description of when it happens was imprecise,** and that is why your four
attempts were correct. The precise rule, and why each of your attempts missed it, are below.

## The files and the command

`Claude-to-Sarvam/evidence-r9/F1/`:

| File | Expected | v188 |
|---|---|---|
| `f1_a_callee_overwrites_caller.sm` | `10 20 30 29` | **`10 28 29 29`** |
| `f1_b_forty_variables.sm` | `55 6 7 39 40` | **`151 38 39 39 40`** |
| `f1_c_return_address.sm` | `7` | **segmentation fault** |
| `f1_d_chakravala_in_a_loop.sm` (uses `lib/ganita`) | `3 2 2 1 9 4` | **`3 2 3 2 3 2 …` forever** |
| `f1_e_varna_bhed_temporary.sm` (uses `lib/varna`) | `2 1002 1002` | **`2 5 1002`** |

**Notes:**

- The expected values are in each file's first line, so the runner prints them beside the actual output.
- None of the files needs Wine. Two need `lib/`, so run from the repository root.

```
sh Claude-to-Sarvam/evidence-r9/F1/run-f1.sh ./sutram_compiler
```

**Pasted output, main's committed `sutram_compiler`** (it is not executable, F6, so `chmod +x` first). The
same output comes from a fresh build of main's `src/`, and from this branch (`logs/f1-linux.txt`):

```
f1_a_callee_overwrites_caller
    expected: 10 20 30 29
    got:      10 28 29 29
f1_b_forty_variables
    expected: 55 6 7 39 40
    got:      151 38 39 39 40
Segmentation fault
f1_c_return_address
    expected: 7
    got:      (no output)
f1_d_chakravala_in_a_loop
    expected: 3 2 2 1 9 4
    got:      3 2 3 2 3 2 3 2 3 2 3 2 3 2 3 2 3 2 3 2
f1_e_varna_bhed_temporary
    expected: 2 1002 1002
    got:      2 5 1002
```

**Wine:** `win/sutram.exe` from main, under **Wine 9.0**, gives the same `10 28 29 29` and
`151 38 39 39 40`, and no output for f1_c (`logs/f1-wine.txt`). **Not run on Windows.**

## What actually happens

**The setup:**

- The first 5 variables of a function, counting parameters, live in registers.
- The rest get stack slots:
  - in a called function, `rbp-24`, `rbp-32`, …
  - in `mukhya`, `rbp-8`, `rbp-16`, …

**The defect:**

- Every load and store of a slot is emitted with a **one-byte displacement**.
- So any slot below `rbp-128` wraps to a positive offset: `rbp-136` becomes `rbp+0x78`.
- Pasted from `objdump` of f1_b (`logs/f1-objdump.txt`):

```
 136:   48 89 45 80     mov    %rax,-0x80(%rbp)
 13f:   48 89 45 78     mov    %rax,0x78(%rbp)      <- the 17th slot, meant to be rbp-136
```

**What that does depends on the variable count:**

| Variables in the function (counting parameters) | Where the wrapped slots land | What you see |
|---|---|---|
| up to 19 (a called function) or 21 (`mukhya`) | nowhere: no slot wraps | correct |
| **20+ in a called function** | above its frame: the caller's stack (its saved registers, pushed temporaries) | **the caller's variables or temporaries change**, but only if the caller keeps something live there (f1_a, f1_d, f1_e) |
| 22–37 in `mukhya` | above `mukhya`'s frame, which nothing else reads while it runs | correct values, by luck |
| **34+ in a called function** | the return address | **crash** (f1_c) |
| **38+ in any function** | slot 33 (`rbp-264`) wraps onto slot 1 (`rbp-8`) | **the function's own variables overwrite each other** (f1_b: `v37` shares `v5`'s cell) |

**R8 said "more than 21 variables", which was wrong for called functions (the threshold is 20) and
incomplete.** A called function shows nothing unless its caller has something at those addresses, and
`mukhya` itself shows nothing until 38 variables.

## Why your four attempts were correct

| Your attempt | Why it did not trigger |
|---|---|
| 26 variables in `mukhya`, summed: 325 | `mukhya`'s wrapped slots land above its own frame, and nothing reads them back: the 22–37 row |
| A caller with 23 variables calling a function: 1007 | The *caller's* wrapped slots are above its frame. The callee's frame is below it, so they never meet. **The trigger is a big callee, not a big caller.** |
| A 40-variable caller: 152 | This one should show aliasing if it reads `v5`–`v7` after `v37`–`v39` are written. **Could you send the file?** Your `152` does not match any sum I can construct from 40 variables, so I may be misreading the program. |
| A plain call: 1007 | No function with 20+ variables |

## In the library

**The functions above the threshold:**

- `chakravala` (29 variables)
- `varna_bhed` and `khand_bhed` (25)
- `varna_tak_dashm` and `roop_sthir_mool` (22)

**Verified wrong results** for `chakravala` (f1_d) and `varna_bhed` (f1_e).

The R8 proofs `r8_chakravala_sweep` and `r8_split_model` call these through a one-line wrapper, and say so.

## The fix (not applied; it is yours to schedule)

**What:** one helper, used at the 15 sites (decl, assign, var load, index, field, the `chakra` slots, named
load/store). It emits disp8 for −128..127 and disp32 (ModRM `0x85`) otherwise.

**Effort:**

- one round
- every committed binary rebuilt and re-pinned
- the five files above, which become goldens

**Measure first:** rebuild the tree and compare every program's output, as for block scope.
