# R52-00 — Hand-back to Sarvam: four additions

- **Commit on `main`:** `50f20438fcbe40783d5f0a5a46c986e8af8ef72d` (v256 → v257), then this hand-back's commit. Pushed with git, not `--force`.
  R53 (v256) landed just before it.
- **Compiler: `Sutram 1.0 (v257) - sampurna sutra`.**
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** Library proofs: **226/226**.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 47 PASS / 0 FAIL / 1 NOT-RUN.**
  - The new gates are "R52 additions" and "R52 lib index".
  - The NOT-RUN is Windows execution.
- **The guard, v256 → v257: 577 programs, 486 byte-identical, 91 refused identically, 0 DIFFER.**
  - It held on all three paths: Linux ELF, Linux PE, and the Windows compiler under Wine.
  - **No differ to name.**
- **Goldens changed: 0.** No existing test asserted the `lkhb` bit pattern, because no existing program calls
  `lkhb` on a `dasham`.

| WS | Result | Verdict |
|---|---|---|
| 1 | `likha("x = ", x, ", y = ", y)` prints `x = 42, y = 7` | **PASS** (new) |
| 2 | `lkhb(2.5)` prints `2.500000`, not `4612811918334230528` | **PASS** (bug fixed) |
| 3 | `agyat prakriya: brihat_yuj` + a `yoj brihat` hint | **PASS** (new; wording changed, see below) |
| 4 | `chakra i = 0 arabhya 10 paryantam` | **PASS** (new; same binary as `tak`) |

## WS1 — `likha` with up to six values

```
likha("x = ", x, ", y = ", y)        x = 42, y = 7
likha("d = ", d, " and x+y = ", x + y)   d = 2.500000 and x+y = 49
```

- **The rule:**
  - Each value but the last prints as `lkhb` if it is a number (no newline), or as `likha` if it is a string
    literal (no newline).
  - The last prints as `likha`.
  - **So the line ends exactly the way `likha(a, b)` already ends it:** a newline after a final number, none after a
    final string.
- **The parser's arity went from `1..3` to `1..6`.** Seven values are refused.
- **The three-argument raw write is untouched.**
  - Three values take the new form only when the first is a string literal.
  - **I re-counted, as you asked: 55 three-argument calls in the tree. 54 pass `1` first, 1 passes `fd`, and 0
    pass a string literal.**
  - Four to six values always take the new form, since a raw write has three.
- `likha(a, b)` is unchanged.

## WS2 — `lkhb` on a `dasham`

**Before:** `lkhb(2.5)` printed `4612811918334230528`. **After:** `2.500000`, and `lkhb(-1.25)` prints `-1.250000`.
An integer prints as before.

**How:**

- `lkhb` now sends a `dasham` to the existing float printer.
- That printer writes its newline at `[rsp+63]` and sets the length to `rsp+64−rsi`.
- Under `lkhb`, one template byte, the displacement (now labelled `float_print_len_disp`), becomes `0x3F` instead
  of `0x40`. The newline is stored but not written.
- **It is the same printer as `likha`, so the same six decimals.**

**Does it change existing output? No.** The guard is 0 DIFFER and no golden moved, because no existing program
calls `lkhb` on a `dasham`.

## WS3 — the `yoj` hint

```
Sutram Error: agyat prakriya: brihat_yuj
  Sanket: 'brihat_yuj' 'brihat' ghatake asti; 'yoj brihat' iti likhatu
```

- **It appears in the ordinary compile and in `--check`**, where it follows the source line and caret.
- **There is one line per module that has the name.** No name is in two modules today, but the code handles it.
- **A name that is in no module gets no hint.**
- **The names come from a generated index,** `src/r52_lib_index.inc`: 305 library `prakriya`, written from
  `lib/*.smlib` by `tools/lib_index.py`.
  - Gate "R52 lib index" fails if it is out of step with `lib/`, the same way the message tables are guarded.
  - It is pinned with the compiler.
- **It is a default message only**, not one of the per-pack keys, so **the ten frozen packs are not touched.**
  Under `--lang` it prints in the default romanised Sanskrit.

**The wording is not the brief's, and here is why.**

- The brief's line was *"`brihat` module nahi juda. `yoj brihat` likhiye."* **That is Hindi** (`nahi`, `juda`,
  `likhiye`).
- **The compiler's default messages are Sanskrit grammar** (R13's rule), and the other `Sanket` lines are written
  that way: *"… nirdeshikayam va bhavet"*, *"… pashyatu"*, *"… dadatu"*.
- So the hint says *"'brihat_yuj' 'brihat' ghatake asti; 'yoj brihat' iti likhatu"*: "brihat_yuj is in the brihat
  module; write 'yoj brihat'". `ghataka` is the project's own word for a module, as in *ghatak patra aprapt*.
- **It is one string in `src/r52_yoj_hint.inc`.** If the owner wants other words, it is a one-line change.

## WS4 — `arabhya ... paryantam`

```
chakra i = 0 arabhya 10 paryantam { ... }      the same binary as      chakra i = 0 tak 10 { ... }
```

- **It is read contextually,** only after the start value of `chakra`.
- **Neither word is reserved.** A program may still use `arabhya` and `paryantam` as variable names, even inside
  the loop itself. That is tested.
- **It goes to the same body parse and the same `AST_FOR` node,** so the endpoint and direction rules are the old
  ones. The binaries are identical.
- `arabhya` without `paryantam` is a grammar error.
- `tak` is unchanged.
- **The word order is right Sanskrit:** `ārabhya` and `paryantam` are postpositions, so `0 ārabhya 10 paryantam`
  is "from 0, up to 10".

## What I did NOT do

- **No Devanagari form of `arabhya` / `paryantam`** (आरभ्य / पर्यन्तम्). It was not asked for.
  - **One note for whoever adds it:** the pack already maps `पर्यन्त` to `tak`. So `पर्यन्त` and `पर्यन्तम्` would
    be two different words with overlapping meaning in the same pack.
- **I did not touch the vocabulary,** as the brief said. The 211 proposed names are with the owner.
- **Windows: Wine only, for the guard.** `backups/` and `Windows-to-Sarvam/` are untouched.
