# R112-00 — `kosh_iksh` is a stack's peek and is now documented as one. The `.sandesh` files are language packs, so `Sutram Error` stays and the reference says why. The tree is inconsistent on root versus noun, and I left it. The reference and the vocabulary page list all 22.

- **Commit on `main`:** `9653ef0` (documentation and evidence only; on top of ChatGPT's R182, `ac6af3a`, and your R112 files).
- **Compiler: `Sutram 1.0 (v292) - sampurna sutra`, unchanged** - nothing in this round needed the compiler.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `suite: NO-EXPECTATION=4  PASS=295  (299 run)`, FAIL=0** (re-run on this tree).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux cloud): 60 PASS / 1 FAIL / 1 NOT-RUN** (re-run; FAIL `installer
  version`, `payload v243 inside Sutram-Setup.exe`; NOT-RUN Windows execution).
- **The guard: not run** - no compiler, library or example changed, so there is nothing to compare. R111's final run
  (v291 → v292, 705 programs, 0 DIFFER on ELF, PE and Wine) is the current one.

**One correction to the brief's summary first.** R111's `pack messages` failure was not about `Error`: it was the
*deprecation warning* appearing in `--lang` runs, which I fixed by printing it only without `--lang`. `Error` was
left alone for the reason in WS2 below, which still holds whatever the answer about the packs is.

## WS1 - `kosh_iksh` takes one argument, and that is right

**Measured on v292** (`evidence-r112/kosh-iksh-v292.txt`, programs beside it):

```
kosh_kship 3, 7, 11      iksh 11  gan 3          k[0] 3  k[1] 7  k[2] 11
kosh_hri -> 11           iksh 7   gan 2          (the new last element)
kosh_apanay -> 3         iksh 7   gan 1          (dequeue takes the front; iksh still shows the last)
empty kosh               Sutram Error: riktat koshat kosh_peek   (exit 1)
kosh_iksh(k, 0)          Sutram Error: vyakaran dosh ... shabd ')'
```

1. **"Peek the last element" is the intended behaviour, and the right one.** `kosh_iksh` returns what `kosh_hri`
   would take next, without taking it - a stack's *peek* is its top, and the top of a `kosh` used as a stack is its
   last element. The old reference said "last element, not removed"; it now says it plainly, with the arity.
2. **The indexed form needs no new capability - it exists: `k[i]`.** It reads any position, is bounds-checked
   (past the length: `mala ank seema atikram`, exit 1), and costs nothing new. So the front of a queue - what
   `kosh_apanay` would take - is `k[0]`. A two-argument `kosh_iksh(k, i)` would be a second spelling of `k[i]`; I
   would not build it.

**Documented** in `docs/LANGUAGE-REFERENCE.md` §16. The table now gives each row's old name, `kosh_iksh` as "one
argument: the last element - the one `kosh_hri` would take next - not removed", and a paragraph covering `k[i]`,
`k[0]` for a queue's front, and the empty-`kosh` stop. While there I fixed `kosh_shodh`'s row, which read
"sangrah logical length to 0" - an old global replace of "set" (see the end).

**Two smaller things a student will meet, not changed (each changes the compiler):** `kosh_iksh(k, 0)` is
refused with a generic grammar error at the `)`, not "takes one argument"; and the empty-`kosh` message still
names `kosh_peek` - it is compiled into the program, so renaming it changes binaries.

## WS2 - the `.sandesh` files are language packs. `Error` stays.

**Plainly: they are packs.** Each `lang/<pack>.sandesh` is one language's messages: the text is in that language
and its script, and the checker refuses any letter outside the pack's script. With `--lang <pack>` the compiler
speaks from that file and no other (`tools/sandesh.py`: *"one set per language pack"*). A pack is its
`.lang` (the words of the code) plus its `.sandesh` (the words of the messages). Ten of the eleven are frozen.

**And `Sutram Error` inside them is not loose English prose - it is a token the owner's R11 rule deliberately keeps
identical in every pack**, like the `[E_CODE]` tags (*"identifiers, not prose: the owner's rule"*, `sandesh.py`).
That is why the pack gate caught a change to it: the rule exists so an error looks the same, and can be searched
for, in every language.

So by your own test, **`Error` stays, and the reference now says why** (§4b, "Why one English word remains"):

- it is that fixed token, the same in all eleven packs, ten of them frozen;
- **and programs carry it** - a program that stops at run time prints the message from its own bytes, and 443 of the
  guard's 705 programs contain one. That second reason holds even if you decide the packs are only strings - so if you
  ever want `truti`, it takes both decisions (a scoped exception for the ten packs, and accepting 443 binaries
  whose message bytes change), and it is a round of its own.

## WS3 - root or noun: the tree is inconsistent, and I left it

**The rule you asked for does not exist in the tree, so no rule I applied would be consistent with it.** Three ways
it disagrees with itself (`evidence-r112/naming-consistency.txt`):

1. **Roots and full nouns side by side** - as you say: `yoj`, `kship`, `hri`, `gan`, `iksh` are roots; `ganana`,
   `parimita`, `sandhi`, `pratilip` are words.
2. **The final short *a* is dropped in some words and kept in others**, in the oldest keywords: `kosh` (कोश),
   `dasham`, `akshar`, `smaran` drop it; `anka`, `guna`, `mandapa`, `rachana`, `sutra` keep it. **`apanay` is `apanaya`
   with the final *a* dropped - the same thing `kosh` does**, so it is no more irregular than the language's own name
   for the thing it works on.
3. **One root, two spellings, one of them new in v292:** the library writes क्षिप् as **`khip`**
   (`suchi_khip`, `nighantu_khip`, `chay_khip`, `anukram_khip_i`, `anukram_khip_aayam_purva`), and v292's builtin
   writes it **`kship`** (`kosh_kship`) - which matches how the tree writes क्ष everywhere else (`akshar`, `kosh_ksham`,
   `kosh_iksh`, `kshetra`), but not the five library functions. The 29 October proposal in `docs/vocabulary/`
   had chosen `kosh_khip` for exactly that reason. And "length" is **`aayam`** in `vartani_aayam` and three library
   names, but **`gan`** in `kosh_gan` and `pankti_gan`.

Regularising any of these renames names that already work (`kosh` itself, or five library functions, or a builtin
published one round ago). **So I left `kosh_apanay` as it is**, and I am handing the rule to the place you have also
asked for it - Muse's R108 has the same question. If the rule that comes back is "roots, final *a* dropped, `ksh`",
the tree needs two changes to fit it: the five `khip` functions, and `vartani_aayam` or the two `_gan` names.

**"The two other flags Muse raised in R106":** if you mean `saha` and `smaran_kriti`, they are **already applied, in
v292** - `help` → **`sahayata`** (the shell's existing help word) and `smaran_cp` → **`smaran_pratilip`**, both as Muse
recommended. Muse's R107 recommends the same two. The `R111 vocabulary` gate checks both pairs: `smaran_cp`
compiles to the same bytes as `smaran_pratilip`, and `help` warns and names `sahayata`. Muse's remaining R106 notes - `kosh_ksham` an adjective where
`kshamata` is the noun, `jala` ambiguous with water, `sankhya_bindu` not saying "product" - were marked *"noted,
not rejected"*, with no replacement recommended, so there was nothing to apply.

## WS4 - the docs

- **`docs/LANGUAGE-REFERENCE.md`:** §4 (the builtin table: new name, old in brackets), §4b (the full 22, `asti` /
  `nasti`, the shell, the warning, and now *why `Error` remains*), and §16 (every `kosh` row with its old name, and
  the `kosh_iksh` paragraph). Done in R111 and completed now.
- **`docs/sutram-vocabulary.html`** (the "Frozen Vocabulary" page): a new section, **"Builtins renamed in v292 (R111)
  - the old names still work"** - all 22 with concept, old name, new name, Devanagari and meaning, plus `asti`,
  `nasti`, `tyaj`, `sahayata`, and the two words not renamed. Rendered and checked
  (`evidence-r112/vocabulary-page-new-section.png`).
- **And a mismatch the page already had, now marked on it:** its "Error codes and CLI flags" tables show
  `E_PARSE → E_VYAKARAN`, `E_UTF8 → E_LIPI`, `--check → --janch`, `--lang → --bhasha` and others. **None of those is in
  the compiler**: it prints `E_PARSE` and `E_MODULE_CYCLE` and accepts `--check`, `--lang` and `--version`;
  `E_VYAKARAN`, `E_LIPI`, `E_AGYAT`, `E_SEEMA` and `E_ANK_DOSH` appear nowhere in its source; `--janch` is not a flag.
  I did not rename anything; the page now says, under those tables, that they are the decided vocabulary and not
  what the compiler does (`evidence-r112/vocabulary-page-not-in-compiler-note.png`).

## Found on the way, not fixed

- **"sangrah" for "set" in English prose:** the same old replace that broke `kosh_shodh`'s row is in `README.md`
  (*"or sangrah `SUTRAM_LANG=tamil`"*), `AGENTS.md` (*"Do not sangrah up background watching"*) and a few other docs.
  Some files use `sangrah` correctly, as the module name ("collection"), so it needs a reading, not a replace. I fixed
  only the one in the reference table I was rewriting.
- **`docs/reports/KOSH-BUILTINS.md`** and the six book editions still use the old `kosh_*` names. They are still valid
  programs (aliases), but no longer the primary spelling.

## Not done

- **`Error → truti`:** stays, by WS2.
- **Any rename for consistency (WS3):** left, as above.
- **Native-speaker review** of the 22 words and the Devanagari column on the vocabulary page: NOT RUN.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, every pack file, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
