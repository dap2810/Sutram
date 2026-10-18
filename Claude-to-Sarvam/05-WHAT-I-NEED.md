# WS5 — What was missing, plainly

**Date:** 2026-10-18 · in order of how much time each would have saved.

---

## 1. A gate list that is the gate list

`PROJECT-MASTER.md` §11 gives six commands; §6 reports twelve numbers; the CI workflows run a
thirteenth (`tests/module_graph`). The numbers in §11 and §6 disagree with each other, and three of the
§6 rows cannot be reproduced by any command in the tree (`Module graph OK`, `GUI 18/18`, `R70 6/6`).
I spent the first hour working out which numbers were measurable and how.

**Ask:** one script, `tools/gates.sh` (or a Make target), that builds the canonical compiler, the
terminal IDE and the GUI into the repo root, runs *every* gate that §6 reports, and prints PASS / FAIL /
NOT-RUN per gate — nothing else. Then §6 becomes "the output of `tools/gates.sh` on `<commit>`" and
cannot drift. If a gate needs an environment the script cannot provide (X11, Windows), it prints
NOT-RUN with the reason rather than being omitted.

## 2. The compiler at the repo root, or a documented `SUTRAM_COMPILER`/`SUTRAM_IDE`/`SUTRAM_GUI`

The module path resolves relative to the binary (`/proc/self/exe`), so a compiler built anywhere but
the root gives `undefined function: varg` for `yoj ganit` from another cwd — the suite's `79_ayojan_cwd`
case fails (186, not 187) until the binary is copied to `./sutram_compiler`. Four tools default to
`/scratch/work/...`. None of this is written anywhere a new collaborator reads first.

**Ask:** a line in §11: "build into the repository root; the suite, `ide_test.py` and the X11 tools
look there, or set `SUTRAM_COMPILER` / `SUTRAM_IDE` / `SUTRAM_GUI`." And `sutram_compiler`, `sutram-ide`,
`sutram-gui` in `.gitignore` (they are not — only `*.bin`/`*.o` are — so a careless `git add -A` commits
a 190 KB binary).

## 3. A decision on the *register* of diagnostics before the text is written

WS1 needed a rule for what "Sanskrit" means in a sentence. The existing non-English strings are Hindi
with Sanskrit nouns (`dekho`, `dabao`, `nahi mila`). The directive says Sanskrit. Translating 67
messages twice because the register changes afterwards would waste a round.

**Ask:** Sarvam decides one of: (a) noun-only templates (my proposals), (b) Hindi-register sentences
as now, (c) classical Sanskrit sentences; and whether the 10 packs' message strings follow the same
rule. Also whether `lang/sanskrit.lang` keeps the classical words (`अन्यत्र`, `पुनरावर्तन`…) or
follows the vocabulary's Devanagari column (`अन्य`, `चक्र`…) — WS2 §3.2 shows the three sources
disagree today.

## 4. A way to see the un-doubled text of the localized strings

The 50 localized strings in the compiler are double-encoded (WS1 F1). Whoever fixes them needs a
one-shot script that decodes each `db` line, shows the recovered text next to the pack's own words,
and re-emits the line; and a **golden test** that compiles a bad program with `--lang hindi` and
compares bytes, so this cannot regress silently again. I can write both if asked; the compiler file is
not mine to touch.

## 5. A user-level diagnostics spec (one page)

Before any text is translated: which stream (stdout today — WS1 F7), what exit code (missing input
file exits 0 today — F6), one location format (`file:line:col:` from `--check` vs `at line L:C` from
normal mode — F4), and correct line numbers in normal mode when modules are imported (F12). These are
format decisions that the translation then inherits. Translating first and fixing format later means
re-translating.

## 6. Reserved-word diagnostics

`vitti band = 1` fails with the generic parse error because `band` is a builtin. A `Sanket:` line
saying "`band` is a builtin name" would have been a one-minute fix for me and looks cheap in
the parser (the lexer has already classified the token as a builtin by the time `parse_error` fires —
I did not verify the exact path). Same for a module function name
used as a variable after `yoj`.

## 7. Less, not more, documentation — one place for library signatures

`LANGUAGE-REFERENCE.md` §4b lists 60 of 303 functions and has a limitation that no longer exists;
`docs/sutram-stdlib-reference.html` is generated (`tools/gen_stdlib_ref.py`) and complete. The `.md`
should point at the generated page and stop carrying its own copy. The prose-damage list in WS3 §4.8 is
long because the same facts are written in many files; each extra copy is another place to be wrong.

## 8. The environment was fine

NASM 2.16.01, GNU ld, Python 3 — nothing missing. Build takes 1.7 s; the whole gate set under two
minutes. No network was needed and none was used. No root. The one thing I could not do is anything
Windows.

## 9. Things I would volunteer for next round, if useful

- The re-encoding script + golden for F1 (item 4).
- A `tests/module_graph` fixture update (`ayojan`→`yoj`, `pratiyati`→`prati`) with the 18/18 re-run.
- The `to`→`tak` and `.vardh`→`.inc` and `empty mala`→`empty array` document fixes as one
  documentation-only commit, each line listed.
- A Devanagari-spelling decision table for item 3, if Sarvam wants options laid out rather than a
  recommendation.
