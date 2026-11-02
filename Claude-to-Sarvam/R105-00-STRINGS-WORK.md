# R105-00 — Strings work (v287): `==` `!=` `<` `>` `<=` `>=` compare text, `+` makes a new string, and `likha(a, " ", b)` prints three values. The tree's 683 programs: 0 DIFFER.

- **Commit on `main`:** `d305f4a` (rebased onto Muse's R101 census commits, `abd17f2`; the v286 base was `b929973`).
- **Compiler: `Sutram 1.0 (v287) - sampurna sutra`** (was v286). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=279`, FAIL=0** (273 + six new goldens). Proofs 229/229 and 86/86; r52 12/0; r81 24/0.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 59 PASS / 1 FAIL / 1 NOT-RUN.** The FAIL is `installer
  version` (v243 against v287); the NOT-RUN is Windows execution. (A first run failed R28 and R29 on golden 307;
  fixed below, re-run: `evidence-r105/gates-first-run.txt`, `gates.txt`.)
- **The guard, origin/main (v286) → v287, 689 programs** (`evidence-r105/guard.txt`):
  - **Linux ELF: 551 byte-identical, 132 refused identically, 0 DIFFER, 6 new** (the six goldens).
  - **Linux PE: 551 byte-identical, 132 refused identically, 0 DIFFER, 6 new.**
  - **The Windows compiler under Wine: 551 byte-identical, 132 refused identically, 0 DIFFER, 6 new; its 1102 outputs are byte-identical to the Linux compiler's PE outputs.**

## WS4 first, because its answer is short: no program in the tree changes

You expected every program that compares or concatenates a string to move. **None does: 0 DIFFER on ELF, PE and
Wine, and none of the 132 refusals flipped.** The reason is v286: Muse's patch refused every shape that compared
or joined two strings with an operator, so the tree that passes the v286 suite contains none - the programs
that compare strings call `vartani_tul`, which is unchanged. A program that refused under v286 is what moves,
and the 37 probes in `evidence-r105/probes-v286-vs-v287.txt` show each kind: refused → correct answer for the
shapes that now work; refused → still refused for the shapes the compiler cannot decide; and the silent ones
v286 missed (below) → correct or refused. **No legitimate program in the tree is broken; there is no tree
program whose old behaviour was the bug.**

## WS1 - `==` and `!=` on two strings compare contents

**How:** when both operands are strings, the compiler rewrites the node to `vartani_tul(a, b) ==/!= 0` and
generates that. `vartani_tul` is the existing builtin (0 when equal), so its convention is untouched, and the
compare that follows is the ordinary integer one. **No length cap:** the loop runs to the first difference or
the NUL.

**The emitted loop** (`evidence-r105/emitted-code.txt`, from `programs/dis.sm`):

```
pop rdi ; mov rsi, rax
L: movzx ecx, byte [rdi] ; movzx edx, byte [rsi] ; cmp ecx, edx ; jne NE
   test ecx, ecx ; jz EQ ; inc rdi ; inc rsi ; jmp L
EQ: xor eax, eax ; jmp done          NE: mov eax, 1
cmp rax, 0 ; sete / jne ...           (the ordinary == 0)
```

**Cost: 9 instructions a byte, no allocation.** 1,000,000 comparisons of two equal 64-byte strings: 0.04 s.
**The integer `==` path is not touched:** the decision is made at compile time from the operands' kinds; a
program with no string comparison compiles to the same bytes (the guard: 551 identical), and the 1,000,000
integer-comparison loop `programs/intcmp1m.sm` compiles to a byte-identical binary on v286 and v287 (0.00 s).

**Golden `306`:** equal 1, unequal 0, prefix `"ab" == "abc"` 0 both ways, empty `"" == ""` 1, empty against
non-empty 0, a literal, `!=`, and in `yadi` and `yavat` conditions.

**I also did the ordering, because it is the same loop:** `<` `<=` `>` `>=` on two strings rewrite to (first
differing byte of a − that of b) compared with 0 - a new internal builtin, 35 bytes of emitted code. `"apple" < "banana"`
is 1, a prefix sorts first (golden `309`). That closes Muse's R100 trap 2 (ordering by address).

## WS2 - `+` on two strings makes a new string

**How:** the node becomes an internal call: `strlen(a)`, `strlen(b)`, allocate `la + lb + 1`, `rep movsb` both,
store the NUL; the value is the new string. `a` and `b` are unchanged. (`evidence-r105/emitted-code.txt`.)

**Where the result lives: on the persistent side, as a `nirmmita` outside a `mandapa` - for the rest of the
program.** I chose that over scratch because a joined string is usually kept (returned, stored, joined again),
and a scratch result that escaped its block would be the exact silent-read class this project spent ten rounds
closing. **The cost, measured:** each `+` keeps `la + lb + 1` bytes (rounded to 16) for the program's life:
1,000,000 joins of two 8-byte strings in a loop peaked at **31,104 KB** in 0.04 s (re-run on the final build: 31,232 KB, 0.08 s) (`programs/cat1m.sm`); `s = s + x`
repeated copies the growing prefix each time (quadratic). It is not counted by `mandapa parimita`. On Linux an
allocation failure is `E_VARTANI_SMRITI`, exit 1, before any byte is written. Scratch strings, released at block
end with the escape refused, are the natural next step if you want them - say so.

**Golden `307`:** `"rama" + " " + "sita"`, the inputs unchanged, a `prakriya` that returns `"namaste, " + naam`,
a join in a loop, and `s + 1` (still pointer arithmetic).

## WS3 - `likha` with three values prints three values

**Done, not refused:** `likha(a, " ", b)` prints `7 9`; `likha(a, b, a)` prints `797` (golden `308`). Since v286
every raw write in the tree is `dvaram_likha`, so the three-value form no longer has to guess; v286's
`E_LIKHA_TRAYA` is gone. `tests/r52` now checks the print instead of the refusal.

**Not changed, and your call:** `likha(s)` on a string *variable* still prints its address; `shabda(s)` prints the
text (Reference "Printing a string variable"). With the analysis below the compiler now knows when `s` is a
string, so making `likha` print it is a small change - but it changes what `likha` means, so I did not do it
unasked.

## What decides "is this a string" - and the three holes ChatGPT found in v286

Replacing a refusal with a byte loop is only safe if "string" is right: a number taken for a string is now a
read through a wild pointer, not a wrong `0`. v286 tracked strings by **the last assignment generated**, and
ChatGPT's R173 showed three ways that lies. I replaced it:

**The rule (v287):** before a function is generated, the compiler walks its whole body once and records every
declaration and assignment of each name. **A variable is a string when every value it is given in the function
is a string** (a literal, a string variable, `s + t`, a string-returning `prakriya`). **A parameter is a string
when every call in the program passes one; a `prakriya` returns a string when every `nivartanam` returns one** -
computed to a fixpoint over the whole program before `mukhya` is generated. A variable given a string somewhere
and something else elsewhere is "sometimes a string": beside a string it is refused; beside numbers it keeps its
integer meaning. Everything else is a number, as before. Compile time: the 283 examples compile in 0.28 s (0.31 s
on v286).

| ChatGPT R173 | v286 | v287 |
|---|---|---|
| P173-01 `s = "ab"; s = s + s; shabda(s)` (`programs/p173_01.sm`) | **exit 139**, as ChatGPT predicted from the source (the flag is cleared before the right side is checked, so the address sum goes through) | `abab`; in a loop (`self_join_loop.sm`) `xxxxxxxx`, compares equal |
| P173-02 `vitti p = s + off` vs `shabda(s + off)` (`fastpaths.sm`, `p173_02b.sm`) | the first refused, the second printed `bcd` | both `bcd`: every register fast path (`try_emit_int_decl_reg`, `_reg_assignment`, `_self_update`) now leaves a string operand to the one generic rule |
| P173-03 `s + banao()`, `banao()` returning `"cd"` | **exit 139** (the call result was taken for an integer offset) | `abcd`: `banao` is known to return a string |

**Also fixed by the same rule:** a string passed to a parameter - `prakriya same(a, b) { nivartanam a == b }`
called with `"ab", "ab"` printed **0** on v286 (two parameters, untracked, addresses compared); v287 prints **1**.
A string-returning `prakriya`, a ternary of two strings, and Devanagari text (`"राम" + " " + "सीता"`, `==`) work.

**Refused, not guessed** (each in `probes-v286-vs-v287.txt`): a string beside a number (`s == 5`, `s < n`);
a variable assigned a number on one path and a string on another (`examples/310`); a parameter passed a string
by one caller and a number by another; a module-level variable or a `kosh` beside a string; a `prakriya` used
as a value (`vitti g = f`), whose callers cannot be seen; `-` `*` `/` `%` and bit operators on a string -
**`E_VARTANI_GANIT`**, new (`examples/311`; Muse's trap 1: `s - t` printed `-14`). String ± integer stays pointer
arithmetic.

**One fix this round needed:** the first full gate run failed R28 and R29 on golden 307. I had marked every
parameter "unknown" in `--object` and `--separate` builds, so a linked program's `abhivadan(naam)` did not know
`naam` was a string while the direct compile did. Now only a module object (no `mukhya`), whose callers really
are elsewhere, treats its parameters as unknown; R28 241/0, R29 267 + 183 identical, R30 8/0.

## Windows

The four new running goldens compiled as `.exe` and run under Wine print exactly the Linux goldens (the join's
allocation goes through the same `nirmmita` path). Not run on real Windows. The `E_VARTANI_SMRITI` check is
Linux-only.

## Not done, and why

- **`likha(s)` printing text:** above - a meaning change, yours to order.
- **Not known to be strings:** module-level variables, `kosh` / `mala` elements (Muse's trap 6), a `prakriya`
  used as a value, a module object's parameters. Beside a string they are refused; with each other they still
  compare as numbers. **An empty string is still true in `yadi (s)`** (Muse's trap 3); a string is a pointer.
- **Scratch strings** (a `+` inside a `mandapa` released at its end): not built; the persistent choice is stated.
- **The installer** (v243); **native-speaker review** of the new and changed Sanskrit (`E_VARTANI_TUL`,
  `E_VARTANI_CAT`, `E_VARTANI_GANIT`, `E_VARTANI_SMRITI`): NOT RUN.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs' sources, `MEMORY-DECISION.md`,
  `Muse-to-Sarvam/`.
