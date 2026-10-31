# R94-00 — The arithmetic audit found a wrong answer: `5.5 % 2.0` printed `6192449487634432`. Now refused. Ten other gaps are written down. `inf` and NaN pass through `kosh` and `mandapa` unchanged.

- **Commit on `main`:** this round's commit (parent `ea19b12`). It contains compiler v282, one compile-time refusal, docs, three goldens and evidence.
- **Compiler: `Sutram 1.0 (v282) - sampurna sutra`** (was v281). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=267`, FAIL=0** (new: 297, 298, 299). Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 58 PASS / 1 FAIL / 1 NOT-RUN.** The FAIL is `installer version` (installer v243, compiler v282), the gate doing its job. The NOT-RUN is Windows execution.
- **The guard, origin/main (v281) → v282: Linux ELF and Linux PE — 677 programs, 546 byte-identical, 128 refused identically, 0 DIFFER, 3 new (297–299).** No program in the tree used `%` or a bit operator on a `dasham`. **The Windows compiler under Wine gives the same counts, and its 1092 outputs are byte-identical to the Linux compiler's PE outputs.**

## WS1 — the installer: still not rebuilt, and the gate does fail when they diverge

- **Confirmed, twice.**
  - On the real file, the gate fails this round: `installer (bin/sutram.exe v243, win/sutram.exe v243), compiler v282`.
  - Gate `R93 installer gate` passes the checker on 8 stand-in installers: it accepts the two current ones and
    rejects six stale ones, including one compiler a single version behind.
  - When the compiler went from v281 to v282 this round, nothing was rebuilt, and the gate followed the source
    version on its own.
- **The hash:** the only installer in the tree is the v243 package, `285470a4…`. The v279 review installer
  ChatGPT built is not in the tree. If it were committed, the gate would fail on it too, at v279 against v282.
- **What blocks the rebuild** is the same as R92 and R93: it is a PowerShell build on Windows, and this session
  has neither. The maintainer's five commands are in `R93-00`. **The gate will pass the day he commits a v282
  installer and its `.sha256`.**

## WS2 — the arithmetic, checked against v281: one wrong answer, ten gaps

I ran 34 probes on v281 (`evidence-r94/arithmetic-probes-v281.txt`) covering integer division, remainders,
shifts, mixed integer/`dasham`, literals, precision, tiny values, overflow, `inf`, NaN and conversion.

**The wrong answer:**

- **`5.5 % 2.0` printed `6192449487634432`, with exit 0.** `binop_needs_float` sends only `+ - * /` and the six
  comparisons to the `dasham` code. Every other operator with a `dasham` operand — `%`, `&`, `|`, `^`, `<<`,
  `>>` — fell through to the integer code and ran on the IEEE-754 bits.
- **v282 refuses them when compiling:**

```
298_r94_dasham_remainder_refused.sm:6:13: Sutram Error [E_DASHAM_KRIYA]: dashama-sankhyayam % & | ^ << >> kriyah na sambhavanti
      likha(x % y)
              ^
Sanket: etah purnanka-kriyah - vitti upayujyatam
```

- `x %= 2.0` is refused the same way. `vitti % 2.0` is refused. Integer `%`, `&`, `>>` are unchanged: the guard
  shows 0 DIFFER.
- **One limit:** `& | ^ << >>` carry no source position in the AST, so for them the error names only the file.
  `%` gets the line and the caret.
- **This is a refusal, not `fmod`.** Implementing `dasham` `%` would mean choosing what `fmod` means here; that's
  your call. The `E_DASHAM_KRIYA` code and the Sanskrit wording also need your review.

**Ten things that exist and were written down nowhere, or wrongly.** All are now in reference §3a or §15:

| # | v281 does | was |
|---|---|---|
| 1 | `/` truncates toward zero, `%` takes the left side's sign: `-7 / 2` = −3, `-7 % 2` = −1, `-9 / 8` = −1 | not stated (Muse said so in R83) |
| 2 | **`>>` is logical:** `-8 >> 1` = 9223372036854775804 | not stated. A student halving a negative number gets a huge positive one |
| 3 | the shift count is taken mod 64: `1 << 64` = 1, `1 << 63` = the smallest `vitti` | not stated |
| 4 | **`dasham d = 7 / 2` is `3.000000`** (integer division first); `7.0 / 2` is 3.5 | not stated. This is the classic trap |
| 5 | `.5` and `5.` are not literals. They are syntax errors, **reported at the next line** | not stated |
| 6 | `0.1 + 0.2` prints `0.300000`, but `== 0.3` is 0 | not stated |
| 7 | a tiny value prints `0.000000` but is not zero: 10⁻²⁸⁸ `== 0.0` is 0, and `1.0 / s` is `1.000000e+288` | not stated |
| 8 | where `inf` and NaN come from: overflow, then `inf - inf`, `inf * 0.0`, `inf / inf`; `1.0 / inf` is 0; `inf` compares as a number | only "by overflow", in one clause |
| 9 | `9223372036854775807` stored in a `dasham` becomes 2⁶³, and storing it back in a `vitti` stops the program | not stated |
| 10 | **`100000000000000000000.5` is 10²⁰** (the `.5` is lost) | **the reference said "is that number". That was wrong.** |

Your two items were already in, since R93:

- **`1.000000e+80`** is in §15's "Reading `e+N`" paragraph and table, and golden 296 pins it.
- **`inf` at four squarings** is in the same table ("overflow → `inf`"). This round it also gets the full
  ladder, 10²⁰ → 10⁴⁰ → 10⁸⁰ → 10¹⁶⁰ → `inf`, in the new "where `inf` and NaN come from" paragraph.

**Goldens:**

- **297** pins items 1, 2, 4 and 6 (`-7 / 2`, `-8 >> 1`, `7 / 2` into a `dasham`, `0.1 + 0.2`).
- **298** is the `%` refusal.
- All three new goldens are identical on PE.

## WS3 — `inf` and NaN in a `mandapa` and in a `kosh`: no different from any value. Your expectation held, and now it's tested.

`examples/299_r94_nonfinite_kosh_mandapa.sm` covers:

- `inf`, NaN and `-inf` pushed into a `kosh dasham`, then 20 more NaNs, which makes it grow;
- index reads, a store, `kosh_pop`, and a function returning `k[0]`;
- **inside a `mandapa`:** a `kosh dasham` made in the block with `inf`, NaN and 1.5 pushed and growing, a
  `nirmmita` alongside, arithmetic and comparisons on the elements, and a `dasham` function called with NaN;
- a second block computing `inf * 0.0` locally;
- the values used again after both blocks.

**Every value came out as it went in, and every comparison is IEEE.** NaN != NaN read back from the `kosh` is 1,
and `inf > 1.0` is 1. The output is identical on v281, v282, PE under Wine, and the guard-page build, which puts
every block flush against an unmapped page. The generation check never looks at element bits: it compares the
`kosh` header's block generation, which is the same whatever the elements hold. "Just 8 bytes" was right this
time, and now it's measured.

## Not done

- **The installer rebuild:** it needs Windows.
- **`dasham` `%` as `fmod`:** your decision; it is refused for now.
- **Source positions for `& | ^ << >>`.**
- **The overflow `inf` policy (R92):** `inf` still prints, now documented.
- **The 2⁶³ literal parse** (2⁶³ + 2048), and **the line in `E_DASHAM_VITTI`**.
- **NaN in the library's sorting and min/max functions:** with IEEE comparisons, a NaN element is never less
  than anything, so it stays where it is. I didn't test those functions with NaN.
- **Not run:** real Windows.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.
