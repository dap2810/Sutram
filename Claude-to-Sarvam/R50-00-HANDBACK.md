# R50-00 — Hand-back to Sarvam: the first lines

- **Commit on `main`:** **`8eade706`** (v254 → v255), then this hand-back's commit. Pushed
  with git, not `--force`.
- **Compiler: `Sutram 1.0 (v255) - sampurna sutra`** (v254 → v255).
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** Library proofs: **226 / 226**, both unlimited and under `ulimit -v 4 GB`.
  Property proofs: 86 / 86.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud with a display (Xvfb): 44 PASS / 0 FAIL / 1 NOT-RUN.** The NOT-RUN is
  Windows execution. There is one new gate, "Devanagari default", so the count is one higher than R49.
- **The guard, v254 → v255: 577 programs, 484 byte-identical, 91 refused identically, 2 DIFFER.** It is the same on all three
  paths: Linux ELF, Linux PE, and the Windows compiler under Wine. **The 2 are the two Devanagari examples, which needed
  `--lang sanskrit` before and compile without it now** (WS3).
- **WS1 is NOT done. I stopped, as the brief says to:** code matches on the literal `Sutram Error`, and one of the matches
  would fail silently, in the Linux IDE.

## Results

| WS | Result | Environment |
|---|---|---|
| **WS1 `Sutram Error` → `Sutram dosh`** | **STOPPED, as the brief asks.** Code matches the literal, and one match would go wrong silently, in the product. Nothing is changed. The full report is below. | Linux x86-64, cloud |
| **WS2 `prati` → `प्रति`** | **DONE.** The pack, the built-in keyword and the regenerated tables now agree. `प्रतियाति`, `प्रत्यायति` and `प॰` are no longer keywords | Linux; Wine |
| **WS3 Devanagari without the flag** | **DONE, by option B's outcome through A's mechanism** (below). The Windows program, run again with no flag, gives the Latin program's bytes | Linux; Wine. Real Windows NOT-RUN |
| **WS4 the guard and the full run** | **PASS.** 2 DIFFER, both named and expected. The new gate is 9 / 9 | Linux ELF, Linux PE, Wine |

## WS1 — stopped: the literal is matched in code, and once silently

**I made the change in a scratch build only, never committed, to measure it.** That build is this compiler with the 74
`Sutram Error` in `src/sutram_compiler.asm` replaced by `Sutram dosh`.

- **44 goldens in `tests/expect/` would change.** The list is in `evidence-r50/ws1-goldens-that-would-change.txt`.
- **One before/after,** `examples/98_t18_kosh_empty`, which pops an empty `kosh` at run time:

  ```
  before:  Sutram Error: riktat koshat kosh_pop      (exit 1)
  after:   Sutram dosh: riktat koshat kosh_pop       (exit 1)
  ```
- **These would need their expected text updated too:**
  - 18 files in `tests/sandesh/expect/{default,sanskrit}`;
  - 6 texts in the R70 manifest;
  - about 50 expectations inside test files;
  - **the crash-corpus gate: 223 of 227 cases fail,** because it requires stdout to start with `Sutram Error`.

**Why I stopped** (`evidence-r50/ws1-code-that-matches-the-literal.md` has every match):

- **The Linux IDE decides that a compile failed by looking for the bytes `Error` in the compiler's output** (`has_error`,
  `ide/sutram_gui_linux.asm`).
  - After the change, a failed compile prints `Sutram dosh: …`.
  - The IDE takes that for a success and **runs the binary left by the previous build.** Nothing fails, and the user sees an
    old program's output.
  - This is the "test that silently stops testing" case, in the product itself.
- **`tools/sandesh.py` and `tools/r83_pack_structure.py` require every pack to keep the default's `Sutram Error` tag.**
  - The 10 frozen packs keep it (137 times each), because `LANGUAGE-PRIORITY.md` forbids changing them. So the check fails.
  - Making it pass means either editing the frozen packs, or deleting the rule. Deleting the rule removes the check silently.
- **`tools/test_x11_run.py` passes on `compiled` OR `Sutram Error`.** It would quietly keep passing on half of its condition.
- **The 74 are not all of it.**
  - 4 more strings are in `src/r66_indic_lexer.inc`, `src/r68_diagnostics.inc` and `src/r71_unsafe_integration.inc`. With
    only the 74 changed, the compiler would print both prefixes.
  - The linkers have 38 more.

**The decisions WS1 needs:**

1. **The Linux IDE should decide failure by the compiler's exit status,** as the Windows IDE already does
   (`GetExitCodeProcess`). This should land with the rename, or before it.
2. **The frozen packs:** keep `Sutram Error` in them and let the tag rule accept either word, or change them as well?
3. **The scope:** only the 74, or also the 4 other compiler strings and the 38 in the linkers?

With those answered, the change itself is mechanical, and the measurement above is its size.

## WS2 — `प्रति`, and every site

**The bytes in the brief are wrong; I checked before using them, as asked.** `0xE0,0xA4,0xAA,0xE0,0xA5,0x8D,0xE0,0xA4,0xA4,0xE0,0xA4,0xBF`
decodes to **`प्ति`**: it is missing the `र` (`E0 A4 B0`). The bytes I used are `'प्रति'.encode()`, 15 bytes:
`E0 A4 AA E0 A5 8D E0 A4 B0 E0 A4 A4 E0 A4 BF`.

**What changed:**

| Where | Was | Now |
|---|---|---|
| `lang/sanskrit.lang:18` | `प्रतियाति prati` | **`प्रति prati`** |
| `lang/sanskrit.lang:74` | `प॰ prati` | **removed** (see below) |
| `src/sutram_compiler.asm` `kw_dev_pratiyati` | `प्रत्यायति` | **`प्रति`** |
| `src/r22_lang_builtin.inc`, `src/r11_sandesh.inc` | generated from the pack | regenerated (`tools/lang_builtin.py`, `tools/sandesh.py --write`); **only the Sanskrit pack's bytes moved** |

**Line 74 is removed, not set to `प्रति`.** The brief's table says that line 74 should become `प्रति prati`, but that is line 18
again: a duplicate entry, which `tests/r66`'s uniqueness test rejects. Removing it gives the one form the brief asks for.

- **The other three abbreviations stay** (`वि॰ vitti`, `लि॰ likha`, `प्र॰ prakriya`). They are not `prati`.
- **If you want `प॰` kept as an abbreviation**, it is one line to restore.

**Three tests asserted the old spellings, and I updated each:**

- **`tests/r66/baseline_packs.json`.** Its key `प्रतियाति` is now `प्रति`. This baseline guards against keywords disappearing,
  and this removal is deliberate.
- **`tests/r66/test_prepare_review.py`.** The Sanskrit pack's pinned entry count goes from 58 to 57.
- **`tests/r43/test_keyword_boundary.py`.** Its Devanagari controls use `प्रति` and `वि॰` in place of `प्रतियाति` and `प॰`.

**What this breaks:** a program that uses `प्रतियाति`, `प्रत्यायति` or `प॰` no longer compiles; each is now an undeclared
name. In the tree, only the Windows channel's two test files use them.

**Every remaining site is in `evidence-r50/ws2-prati-sites.txt`, complete, not a sample.** Most of them are history:
changelogs, past rounds, partners' audits and the vocabulary proposal. **Two are now wrong, and they are prose, so I left them
for ChatGPT:**

- **`docs/LANGUAGE-REFERENCE.md:326`** still lists `प्रतियाति`;
- **`docs/SPECIFICATION.md:227`** still lists the `प॰ -> prati` alias.

## WS3 — option B's result, by A's mechanism, and why

**Option A as written changes the output of every compile.** `--lang sanskrit` does more than add the keywords:

- it prints a banner (`भाषा-पुटः प्राप्तः: sanskrit`);
- it switches every message to Devanagari (`सिद्धम्: … बाइट् सङ्कलिताः`);
- it embeds the Devanagari run-time messages in every binary (the Windows report: 352 bytes against 284).

So making the flag the default would have made all 577 programs differ, and every golden change. **So I did not take A.**

**Option B as written adds byte strings by hand.** The compiler would then hold a second copy of the pack, which can drift from
`lang/sanskrit.lang` exactly as `kw_dev_pratiyati` did. **So I did not take that either.**

**What I did: when no pack is named (no `--lang`, no `SUTRAM_LANG`), the compiler loads the Sanskrit pack's keywords only.**
It loads them from the copy already built into it (R22), silently, at the one point every compile passes through.

- **The result is B's:** every keyword and builtin of the pack is accepted with no flag.
- **It has one source:** `lang/sanskrit.lang`. There are no new byte strings.
- **What stays exactly as before:** the messages, the banner, every Latin program, and every named pack. A named pack, found
  or not, is used alone. **The pack mechanism is unchanged.**
- **Measured:** under `--lang sanskrit`, all 577 programs are 0 DIFFER against v254.

**The Devanagari test, again, with no flag:**

| | v254 | v255 |
|---|---|---|
| **The Windows `t_dev.sm` (`प्रति`), Linux** | `agyat naam 'प्रति'` | **compiles; byte-identical to `t_lat.sm`** |
| **The same, `win/sutram.exe` under Wine** | — | **compiles; byte-identical to `t_lat.exe`** |
| `examples/218_sanskrit_devanagari`, `219_sanskrit_kosh_aliases` | refused without the flag | **compile, and print exactly what `--lang sanskrit` prints** |

Example 219's executable is smaller without the flag (1,184 bytes against 1,271). It carries the default run-time messages,
not the Devanagari ones. The program output is identical (`evidence-r50/devanagari-no-flag.txt`).

**The new gate is `tests/r50/test_devanagari_default.py`, 9 checks.** It checks that:

- a Devanagari program with no flag gives the Latin bytes;
- no banner is printed;
- it runs;
- the three old spellings are refused;
- `--lang sanskrit` gives the same bytes;
- `--lang gujarati` does not take the Sanskrit words.

**Against v254 it fails 4 of the 9.**

## WS4 — the numbers

| Check | Result | Environment |
|---|---|---|
| Guard, Linux ELF | 577 programs: **484 byte-identical, 91 refused identically, 2 DIFFER** | Linux x86-64 cloud |
| Guard, Linux PE | **484 / 91 / 2 DIFFER** | Linux x86-64 cloud |
| Guard, Windows compiler | **484 / 91 / 2 DIFFER** | **Wine, not Windows** |
| Guard, every program under `--lang sanskrit` | **486 / 91 / 0 DIFFER** | Linux x86-64 cloud |
| The 2 DIFFER on each path | `examples/218_sanskrit_devanagari.sm` and `examples/219_sanskrit_kosh_aliases.sm`: **refused before, compile now** | |
| `sh tools/gates.sh` | **PASS: 44 / 0 / 1.** The NOT-RUN is Windows execution | Linux cloud, Xvfb |
| `tests/run_tests.py` | **NO-EXPECTATION=4 PASS=225, 0 FAIL** | Linux cloud |
| `crash_corpus.py` | **PASS:** 227 + manifest, 0 failed | Linux cloud |
| `proof_lib.py`, unlimited and 4 GB | **PASS:** 226 / 226 both | Linux cloud |
| `proof_props.py` | **PASS:** 86 / 86 | Linux cloud |
| `fuzz_r23` seed 50 | **PASS:** 1000 programs, 35,867 values, 0 differ | Linux cloud |
| `fuzz_valid --capabilities` | **PASS:** 500 / 500 agree | Linux cloud |
| `fuzz_robust` | **PASS:** 5000 mutations, 0 crashes, 0 hangs | Linux cloud |
| unittest r66, r67, r68, r70 | **PASS** | Linux cloud |
| unittest r69 | **FAIL: 2, the same 2 as before this round.** Both are in `windows/` build scripts, the Windows channel's (R39 reported them) | Linux cloud |
| Real Windows | **NOT-RUN** | the owner's machine |

**The non-Sanskrit packs are unchanged.**

- No other `lang/*.lang` or `lang/*.sandesh` file changed.
- In `src/r22_lang_builtin.inc` and `src/r11_sandesh.inc`, only the Sanskrit pack's bytes moved.
- `windows/gui/r11_ide_sandesh.inc` is unchanged.

## Anything surprising

1. **The Linux IDE's failure test is the word `Error`** (WS1). It is the reason WS1 stopped, and it is worth fixing whether or not
   the rename goes ahead: it tests a word, not the result.
2. **The brief's bytes for `प्रति` are missing a letter** (WS2). The check the brief asked for caught it.
3. **Option A was really two changes in one:** a default for the keywords, and a default for the messages. Only the first was
   wanted. Separating them is why the guard is 2 DIFFER, not 577.
4. **The "34 built-in Devanagari keywords" count is 16.** `grep -c kw_dev_` counts each name twice, once where it is defined
   and once in the table, plus two other mentions. The built-in table has 16 entries. Since R50 the full pack is loaded by
   default anyway.

## What I did NOT do, and why

- **I did not do WS1.** The brief says to stop when code matches the literal, and code does, once silently in the product. The
  decisions are listed above.
- **I did not touch the vocabulary, the frozen packs, `backups/` or `Windows-to-Sarvam/`.**
- **I did not edit the two prose docs that still list the old spellings.** They are ChatGPT's.
- **I did not run anything on real Windows.** Every Windows result above ran under Wine and is labelled so.
- **I did not change any golden in `tests/expect/`.**
- **I did not commit `docs/sutram-stdlib.html`.** The gates regenerate it, and I restored it after each run.
- **No network access beyond git, no credentials, no `__pycache__`, no `.pyc`.**
