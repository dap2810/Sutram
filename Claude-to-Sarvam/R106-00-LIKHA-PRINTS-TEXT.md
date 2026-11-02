# R106-00 — `likha` prints a string's text (v288); three of Muse's traps fixed in other emitters; the region stays for the program's life. One commit.

- **Commit on `main`:** `9eca44b` (rebased onto Muse's R102 and ChatGPT's R175 files, `4e841bb`; the v287 base was `8577d59`).
- **Compiler: `Sutram 1.0 (v288) - sampurna sutra`** (was v287). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=283`, FAIL=0** (279 + four goldens, 312–315). Proofs 229/229 and 86/86; r52 12/0; r81 24/0;
  R28 241/0, R29 267 + 183 identical, R30 8/0.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 59 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, v243
  against v288; NOT-RUN: Windows execution). **The first run was 57 / 3 / 1** - see WS4.
- **The guard, origin/main (v287) → v288, 693 programs** (`evidence-r106/guard.txt`):
  - **Linux ELF: 555 byte-identical, 134 refused identically, 0 DIFFER, 4 new.**
  - **Linux PE: 555 byte-identical, 134 refused identically, 0 DIFFER, 4 new.**
  - **The Windows compiler under Wine: 555 byte-identical, 134 refused identically, 0 DIFFER, 4 new; its 1110 outputs are byte-identical to the Linux compiler's PE outputs.**

## WS1 - `likha` on a string prints its text

**Your probe, `likha("concat: ", s + "cd")`: v287 `concat: 140194980298752`; v288 `concat: abcd`.**

`likha` now dispatches on the operand at compile time. An argument whose R105 kind is "string" - a string
variable, `s + t`, a string a `prakriya` returns - is generated with `shabda`'s code (its text, no newline, as a
literal has always printed); everything else prints exactly as before. Two places in the `likha` emitter: the
one-value form and the three-to-six-value form (the two-value form is built from one-value calls).

**Golden `312`:** a string variable, a literal, a concatenation, a string from a `prakriya`, and a mix of strings
and numbers:

```
rama
name: rama
together: rama sita
hello arjuna
rama is 30
7 sita 14
```

**The newline rule, stated:** a string value ends no line (as a literal never has); a number last on the line
ends it, as before. So `likha("name: ", s)` needs a `"\n"`, and `likha("name: ", s, " age ", 30)` does not.

**What still prints a number:** a value not known to be a string - a `mala` or `kosh` element that holds one, a
module-level variable, a value that is a string on one path and a number on another. `shabda(x)` prints those.

**What the tree says:** nothing in the tree printed a string variable with `likha` (0 DIFFER) - which fits: it
printed an address, so nobody kept it.

## WS2 - Muse's eight traps (R101), one by one

| # | trap | where it lives | v288 |
|---|---|---|---|
| 1 | `s - t`, `s * 2`, `s / 2` | binop check | **closed in v287** (`E_VARTANI_GANIT`) |
| 2 | `a < b` by address | binop check | **closed in v287** (byte order) |
| 3 | `yadi (e)` with `e = ""` true; `yadi ("")` | condition emitters (`yadi`, `yavat`, `?:`) and `&&`/`||` | **fixed: `E_VARTANI_SATYA`**, golden `313`; hint `yadi (s != "")` |
| 4 | `kosh a == kosh b` → 0 | binop check | **fixed: `E_KOSH_GANIT`** for a bare `kosh` in any binop, golden `314`; `k[i]`, `kosh_len(k)` unchanged |
| 5 | `likha(k)` prints an address | **the `likha` emitter** | **left, as you asked**: same emitter as WS1. It is a two-line change on top of WS1 (refuse, or print the elements) - your call which |
| 6 | `a[0] = s` then `likha(a[0])` prints an address | the store is fine; the *print* is the problem, and a `mala` element has no kind | **left**: storing a string's address in a `mala` is a legitimate string table, and `shabda(a[0])` prints `hi` today. Making it print by itself needs typed `mala` elements - a language change |
| 7 | `"x" + 2.5` | binop check | **closed in v286** (`E_VARTANI_CAT`) |
| 8 | `a[0] = 3.0` into `vitti a[2]` stores the bits (`4613937818241073152`) | the index-store emitter | **fixed: converted exactly**, as into a `vitti`: `3.0` → `3`, `7.5` → `E_DASHAM_VITTI`, golden `315`. A raw `nirmmita` buffer is unchanged (it holds whatever 8 bytes it is given) |

Each is in `evidence-r106/probes-v287-vs-v288.txt`, compiled and run by both compilers. **None of the fixes
touches the `likha` emitter**: 3 is the condition paths, 4 the binop check, 8 the index store.

## WS3 - the region return: kept for the program's life

**Decided, and it is the same decision as R103, with the reason restated in one line: returning the region
breaks the one check that exists for a `kosh` after its block, and in the tree it would return nothing.**

- **What it would break:** R82's `E_KOSH_MANDAPA` reads the `kosh`'s header. Unmap the region and a dead `kosh`
  reaching a `prakriya` is a SIGSEGV; release only its pages and it reads as empty, or as the next `kosh` given
  that address. Example 287's golden is that message.
- **What it would return:** the three tree programs that make a `kosh` in a block (`286`, `287`, `299`) peak at
  the reading of a three-line program (R103's `ws1-tree-kosh-in-block.txt`). The 400 MB case is a loop that
  makes a new `kosh` in a block 100,000 times - `kosh_clear` on one `kosh` made before the loop measures 0.
- **If you want the memory back anyway**, the design I would build is R104's fourth option - reuse the region
  at the same declaration site, with a fresh generation each entry: the message stays exact, kb1 goes from
  400 MB to one page, no table and no lookup. About three days. Not built.

## WS4 - the guard and the gates, honestly

**The first gate run on v288 failed 3: `R45 debug`, `version string`, `installer version`** (57 / 3 / 1,
`evidence-r106/gates-first-run.txt`):

- **`R45 debug` was my bug.** `--debug` traces each variable with `likha(name)`; a string variable now printed
  its text with no newline, so the next trace line ran into it, and 7 programs (`306`, `307`, `309`, `312`,
  `44_shabda`, `46_language_reference`, `import_demo`) no longer matched once the trace was stripped. The trace
  now ends a string value's line itself (`src/r45_debug.inc`, `r45_likha_node`). R45: 8 checks, 0 failed; 222
  programs under `--debug`.
- **`version string`** failed because I ran the gates before writing the changelog entry. Written; passes.
- **`installer version`** is the standing v243 failure.

**Re-run on the final build: 59 / 1 / 1.** The guard I had started before the R45 fix had finished ELF and PE
(0 DIFFER both) when I stopped it to rebuild; the numbers above are a full fresh run on the final compiler, all
three paths (`evidence-r106/guard.txt` keeps both).

## Not done

- **Trap 5 (`likha(k)`)** and **trap 6 (a string in a `mala`)**: above, with the reason for each.
- **The region return:** kept, above.
- **Windows:** goldens 312 and 315 compiled as `.exe` and run under Wine print exactly the Linux goldens (315 exits 1
  with the same message). Not run on real Windows. **The installer:** v243. **Native-speaker review** of `E_VARTANI_SATYA` and `E_KOSH_GANIT`: NOT RUN.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs' sources, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
