# R87-00 — The fraction is lost at the assignment, by design of `vitti`; a written fraction there is now refused, and every `dasham` prints right

- **Commit on `main`:** this round's commit (parent `e2f88f2`) — compiler v279, two goldens, one fixture, one proof generator, docs, evidence.
- **Compiler: `Sutram 1.0 (v279) - sampurna sutra`** (was v278). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=258`, FAIL=0** (two new goldens, 289 and 290). Library proofs **229/229**. Property proofs **86/86** (after the `breadth26` fix below — it was 85/86 first).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 57 PASS / 0 FAIL / 1 NOT-RUN (Windows execution); guard pages 5/5, suite 258/0.** The first run was 55/2/1 — both FAILs explained below (`evidence-r87/gates-first-run.txt`).
- **The guard, origin/main (v278) → this tree (v279), 666 programs, on three paths:** Linux ELF, Linux PE, and the Windows compiler under Wine — each **459 byte-identical, 127 refused identically, 80 DIFFER, 0 new**. **Every one of the 80 DIFFER programs was run, old binary and new: 79 print the same bytes with the same exit code (ELF natively, PE under Wine); 1 changed — `examples/r71/conversion.sm`, now refused, which is intended.** The 79 differ only because the float printer's code changed; none of them prints a value the old printer got wrong. The Windows compiler's 1077 outputs are byte-identical to the Linux compiler's PE outputs, except one (below).

## WS1 — where the fraction goes: at the assignment, because `vitti` is the integer type

`evidence-r87/ws1-disassembly.txt`, v278, the code emitted for the declaration:

```
vitti f = 3.5                         dasham f = 3.5
movabs rax,0x400c000000000000         movabs rax,0x400c000000000000
movq   xmm0,rax                       mov    rbx,rax
cvttsd2si rax,xmm0                    ...
mov    rbx,rax
```

**3.5 is parsed correctly (0x400c000000000000 is 3.5) in both.** With `vitti` the compiler converts it with
`cvttsd2si` — truncate — before the store; with `dasham` the bits are stored as they are. **So it is your
candidate 1, but not a parsing bug: `vitti` is the integer type, and a float stored into it is converted.**
The store and the print are right: `dasham f = 3.5; likha("f=", f)` prints `f=3.500000` on v278.

**A variable is a float today — when it is declared `dasham`.** The reference never said so plainly: the keyword
table called `vitti` "variable", and §5 Types listed no float. That is the real defect for a student: the
word that means "variable" in every example silently means "whole number".

## WS2 — the scope, on Linux and PE (`evidence-r87/ws1-ws2-runs.txt`)

| program | v278 ELF | v278 PE | v279 (both) |
|---|---|---|---|
| `vitti f = 3.5; likha("f=", f)` | `f=3` | `f=3` | **refused: `E_DASHAM_VITTI`** |
| `vitti f = 3.5; vitti g = f * 2.0; likha(g)` | **`6`** | `6` | refused (at the 3.5) |
| `dasham f = 3.5; dasham g = f * 2.0; likha(g)` | `7.000000` | `7.000000` | `7.000000` |
| `dasham a = 3.5; dasham b = 2.0; likha(a / b)` (via `c`) | `1.750000` | `1.750000` | `1.750000` |
| `dasham x = 2.75; vitti a = x; vitti b = 0.0 - x` | `a=2 b=-2` | same | same — still converts |
| `likha(10000000000000.0)` (ChatGPT R156) | **`-9223372036854.775808`** | same | `10000000000000.000000` |
| `dasham f = 10000000000000.0; likha(f)` | **`-9223372036854.775808`** | same | `10000000000000.000000` |

Note `vitti g = f * 2.0` printed **6**, not 7: `f` was already 3. **PE and ELF agree on every line.** ChatGPT's
negative was not a Windows symptom of the same bug — it was a second defect, the printer, hit by a large
value; it is the same on Linux. ChatGPT's own R157 reached the same conclusion on native Windows.

## WS3 — two fixes

### 1. A written fraction stored in a `vitti` is refused — `E_DASHAM_VITTI`

```
a.sm:2:15: Sutram Error [E_DASHAM_VITTI]: dashamah sankhya purnanka-vittau na sthapyate - bhinnam lupyeta
      vitti f = 3.5
                ^
Sanket: vitti purnankanam eva; dashamaya 'dasham' likhyatam: dasham f = 3.5
```

- **Refused:** a written float literal that has a fraction, or is too large for a `vitti` (|v| ≥ 2⁶³), stored
  into a `vitti` — in a declaration (`vitti f = 3.5`, `vitti b = -2.75`) or an assignment (`f = 2.25`). `vitti n = 7.0` is accepted (no fraction lost).
- **Not refused: a computed value.** `vitti a = x` with `x` a `dasham` still converts, truncating toward zero.
  **I did not refuse that,** because the tree relies on it: 30 programs convert a computed float into a `vitti`
  (`evidence-r87/ws2-float-to-int-sites.txt`), mostly the `madhava` library's `vitti k = x / pi2` and fixed-point
  checks (`vitti s = madhava_sin(x) * 1000000.0`). Refusing those, or inferring `dasham` from the initializer, is
  a language decision — yours. Inference would also change the meaning of every one of those 30 programs.
- **Not covered, still silent:** a written fraction stored into an *integer `kosh`* — `kosh_push(a, 2.9)` stores
  2, and example 112 pins that as the intended rule. Same class of loss; I left it, as it is pinned behaviour.

**What it broke in the tree:** exactly one program — `examples/r71/conversion.sm` (`vitti a = 2.75`). It is the R71
specification fixture for "conversion truncates toward zero", so I kept its meaning: it now converts through a
`dasham` (`dasham x = 2.75; vitti a = x; vitti b = 0.0 - x`), and its `.out` (`2 / -2 / 2.500000`) is
**unchanged** and passes. (Its harness, `tools/r71_native_acceptance.py`, pins compiler sources from R71 and could
not run on v278 either.)

**And one proof it exposed — the more important find:** property `breadth26` failed to compile. Its generator
wrote `vitti want = 3.14159`, and `f`, `diff`, `lim` as `vitti` too: **both sides truncated and the tolerance
became 0, so the float-parser check compared whole parts only.** On v278, a parser returning 3.9 for "3.14159"
passed it (`evidence-r87/breadth26-property-was-vacuous.txt`). I changed the four declarations to `dasham`;
it holds 86/86 on v279 **and on v278** — the parser was right, the check was weak. **That is the bug class this
refusal exists for, found in our own proofs.**

### 2. The printer — every `dasham` prints

The printer computed round(x·10⁶) into a 64-bit integer. That is exact only while x·10⁶ < 2⁵³ — from **9.0×10⁹**
the last digits drift (9223372036854.0 printed `9223372036853.999616`) — and it overflows from **9.2×10¹²**, where
the conversion returns 0x8000000000000000: hence `-9223372036854.775808` for 10¹³, for inf and for NaN.

Now: below 9.0×10⁹ **the old path, unchanged** (same digits); from there to 2⁶³ the whole part and the fraction
are printed apart; from 2⁶³ `d.dddddde+N`; and `inf`, `-inf`, `nan` by name.

**Checked against Python** (`f"{x:.6f}"`, `f"{x:.6e}"` from 2⁶³), 64 values across both signs, the 2⁵³/10⁶ and
2⁶³/10⁶ boundaries, rounding cases (0.0000005, 1.005, 2.675), 2⁶³ itself, 10³⁰, inf, −inf, NaN: **v279 matches
on 64 of 64, ELF and PE byte-identical** (`evidence-r87/ws3-printer-vs-python.txt`). v278 got 29 of them wrong.

### The golden you asked for — `examples/289_r87_float_print.sm`

```
literal 3.500000
variable 3.500000
computed 7.000000
average 4.500000
negative -0.875000
large 10000000000000.000000
near 2^53/10^6 9223372036854.000000
above 2^63 1.234568e+22
inf inf -inf
nan nan
```

A literal, a `dasham` variable, a value computed through variables, an average — all six decimals — plus the
printer's edges. v278 printed the last five lines as `-9223372036854.775808` (four times) and `…853.999616`.
Same on PE. **`examples/290_r87_fraction_into_vitti.sm`** is the refusal golden (`vitti f = 3.5`, refused at 4:15).

**Goldens that locked in truncation: none in the suite.** I searched every `.out` for the overflow string (none)
and every program for a written fraction stored in a `vitti` (only `r71/conversion.sm`, not a suite golden).
The suite goldens that print a truncated value (madhava, `fmt_*`, 112) truncate *on purpose*.

## Docs

- `docs/LANGUAGE-REFERENCE.md`: keyword table — `vitti` is "whole-number (integer) variable; for a fraction
  use `dasham`"; §5 Types gains the `dasham` row; §15 rewritten — the refusal with an example, the conversion rule
  (computed → truncates toward zero), the printer's formats, a warning that NaN comparisons are wrong; and its
  stale "floats do not cross function boundaries / no float arrays" removed (both work: examples 93, 109).
  §3a's "Not yet right" note now says fixed in v279. `1e5` is still refused (checked) — said so.
- `docs/CHANGELOG.md`: v279 entry.

## Gates — the two FAILs of the first run

1. **property proofs 85/86** — `breadth26`, above; fixed.
2. **guard pages: suite FAIL=1, property 85/86** — the property is the same one. The suite failure in the
   guard-page build did **not** reproduce: `tools/guard_page.py` rerun alone gives `controls 5/5, suite PASS=258
   FAIL=0, library proofs 229/229, property proofs 86/86, 0 failed`. The first run shared the two cores with the
   Wine guard, and I did not keep its output, so **I cannot name the test** — I am reporting it, not explaining
   it away. The full gate rerun (`evidence-r87/gates.txt`) is 57/0/1.

## The one Wine-path difference

The Windows-compiler guard ran while I rewrote `r71/conversion.sm`, so it compiled the new text (its log says
"source changed"); the Linux runs compiled the old text and refused it. That is the single output where the
Windows compiler's PE differs from the Linux compiler's PE — different sources, not different compilers.

## What I did not do

- **No refusal of computed float→`vitti` conversions, no type inference** — your decision; 30 programs depend on the current rule.
- **Integer-`kosh` stores of a written fraction** are still silent (example 112 pins it).
- **The NaN comparison defect (R86) is not fixed** — `nan` now *prints* as `nan`, but `n == 5.0` is still true. The reference warns.
- **Not run:** real Windows (Wine only). **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.
