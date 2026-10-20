# R13-02 — WS2: the default is Sanskrit grammar

## When: now, not after the Sanskrit review. Why.

**You left the timing to me. I did it now, for three reasons:**

1. **The owner uses the default, every day.** He has only ever run `hello.sm` and the IDE, in the
   default. Waiting for the Sanskrit review, which is last in the order, would leave the text he actually
   reads in Hindi grammar for the longest time.
2. **"Fix once" does not need the wait.**
   - The 42 default messages say the same things as the Devanagari Sanskrit set, sentence for sentence. I
     wrote them from it, in the project's plain romanisation.
   - When the Sanskrit review corrects a message, the same correction applies to both, and it touches the
     same 42 lines.
3. **The cost of doing it twice is small.** The goldens are re-recorded by a command, and each one moves
   only by the message text. That is checked below.

**What stays unreviewed:** the new default wording is as unverified as the Devanagari Sanskrit it follows.
It belongs in the Sanskrit review when that comes.

## What changed

**All 42 messages**, plus 2 that the sentences need:

- **31 in the compiler**
- **11 in the IDE**
- the IDE's start-up error box
- `mg_e_noexp2`: "'x' from module 'm' not exported" needs the ablative, `ghatakat`

**A rescan of every default for Hindi function words** (`se`, `me`, `hai`, `nahi`, `ke liye`, `ko`, `dein`,
`dekho`, `chahiye`, `janch`, `taiyar` …) **finds none.**

| Before (Hindi grammar) | Now (Sanskrit grammar) |
|---|---|
| `Sanket: 'x' pahle se ghoshit hai; naya man dene ke liye: x = ...` | `Sanket: 'x' purvam eva ghoshitam; navinam manam datum: x = ...` |
| `'f' ko 1 tark diye; hastakshar me 2` | `'f' ityasmai 1 tarkah dattah; hastakshare 2` |
| `Sanket: utne hi tark dein jitne prakriya ki paribhasha me hain` | `Sanket: prakriyayah paribhashayam yavantah tarkah santi, tavantah eva dadatu` |
| `Sanket: is sthan par shabd aur vyakaran dekho.` | `Sanket: asmin sthane shabdam vyakaranam cha pashyatu.` |
| `Sutram Error: rikta kosh se kosh_pop` | `Sutram Error: riktat koshat kosh_pop` |
| `Sutram janch: shuddh (nirgat patra nahi)` | `Sutram pariksha: shuddham (nirgata-patram na rachitam)` |
| `Taiyar. F5: sampadak ka karyakram sankalan aur chalan.` | `Sajjam. F5: sampadakasya karyakramasya sankalanam chalanam cha.` |

**The full set** is the diff of `src/sutram_compiler.asm`, `src/r68_diagnostics.inc` and
`windows/gui/sutram_gui.asm` on the branch.

**Not changed:**

- **`Sutram Error` and the `[E_CODE]` tags.** They are unchanged, so scripts that match on the tags keep
  working.
- **The default messages that already used no Hindi grammar.** "Sanskrit throughout" was the decision for
  these 42. The rest still use the old loose romanisation (`mala ank seema atikram`, not
  `…simatikramah`), which is a spelling question, not a grammar one.
- **The 11 packs.** No translation changed, except that `msg_version` now takes the version from the
  default (R13-01).

## What moved, and the check that it was only the text

**Each moved golden was compared with its old version, with every old message replaced by its new one.
All are equal:** nothing else in any output changed.

| What | Count |
|---|---|
| goldens in `tests/expect` | **17** |
| default goldens in `tests/sandesh/expect/default` | 9 (no pack golden moved) |
| R70 corpus expectations | 3 (`bad_arity`, `malformed_literal`, `unterminated_string`) |
| tests and tools that quote the text | `tests/r68/test_r68.py`, `tools/r48_stage2_acceptance.py`, `tools/r64_source_gate.py`, `tools/r68_native_acceptance.py` |
| docs | the six books, `KOSH-BUILTINS.md`, `KOSH-REUSE.md`, `NEGATIVE-CORPUS.md`, `windows/gui/MANUAL-WINDOWS-GUI-TEST.md` |
| pins | the compiler, **`src/r68_diagnostics.inc`** (ChatGPT's file: only its two default messages changed) and `src/r11_sandesh.inc`, in `r69_build.py` and its lock, the R70 manifest and both docs. The reason is in each `repinned` text. |

- **Measured against R12-02's prediction:** 17 / 9 / 3 / 4 / 10, as predicted.
- **`docs/CHANGELOG.md` keeps its old quotes:** it is history.
- **The word-level diff of every golden** is in `evidence-r13/goldens-moved.txt`.

## Checks

| Check | Environment | Result |
|---|---|---|
| suite · pack messages · proof_lib · proof_props | Linux | 205/4 · OK · 217 · 86/86 |
| R70 corpus · `tests/r70` · `r69_build.py --check-only` | Linux | 6/6 · OK · SOURCE_PINS_CHECKED |
| `tests/r66 r67 r68 r72 module_graph ci windows_accept r65_finish gui` · translit · `r64_source_gate` · namespace oracle | Linux | all OK · 24,761/0 · PASS · PASS |
| `win/sutram.exe`: a duplicate-name error, and `--version` | Wine 9.0 | `Sanket: 'x' purvam eva ghoshitam; …` · `Sutram 1.0 (v208)` |
| the IDE's output pane at start | Wine 9.0 | `Sajjam. F5: sampadakasya karyakramasya sankalanam chalanam cha.` (`evidence-r13/ide-default-ready.png`) |
| Windows | — | **NOT-RUN** |
