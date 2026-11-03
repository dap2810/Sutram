# R111-00 — The vocabulary change is built, as aliases (v292): 22 builtins get Sanskrit names, `asti` / `nasti` are `==` / `!=`, `tyaj` leaves the shell. Not a byte of any program changed. `Error` is left alone, and here is why.

- **Commit on `main`:** `c269e77` (on top of ChatGPT's R181, `48d4d34`, Muse's R107 and your R111 files; the v291 base was `097100d`).
- **Compiler: `Sutram 1.0 (v292) - sampurna sutra`** (was v291). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `suite: NO-EXPECTATION=4  PASS=295  (299 run)`, FAIL=0** (289 + six goldens, 322-327; eight refusal
  goldens re-recorded, below).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 60 PASS / 1 FAIL / 1 NOT-RUN** - 62 gates now, with the new `R111 vocabulary` (FAIL: `installer version`, `payload v243 inside Sutram-Setup.exe`; NOT-RUN: Windows execution). **The first run was 58 / 2 / 1**: `pack messages` failed, and it was right to (below).**
- **The guard, origin/main (v291) → v292, 705 programs** (`evidence-r111/guard.txt`):
  - **Linux ELF: 558 byte-identical, 141 refused identically, 0 DIFFER, 6 new** (examples 322-327).
  - **Linux PE: 558 byte-identical, 141 refused identically, 0 DIFFER, 6 new.**
  - **The Windows compiler under Wine: 558 byte-identical, 141 refused identically, 0 DIFFER, 6 new; its 1116 outputs are byte-identical to the Linux compiler's PE outputs.**
  - The guard ran twice: once on my first build and once on the final one (after the `--lang` fix below). Both 0 DIFFER on all three paths; the numbers are the final run's.**
  - **Where a warning now prints: 125 of the 705 programs** (none on v291), every one of them byte-identical
    above. Which programs and which names: `evidence-r111/warnings-census.txt`. **No program changed behaviour.**

## WS1 and WS2 - your decisions, applied

| row | applied |
|---|---|
| `to → prati` | **dropped.** `to` is still not a word; `prati` is still return |
| `vartani_yoj` | **`vartani_sandhi`** - checked first: it compiles as a variable and as a function called with a space before `(`, which is the shape that tripped the scanner. It does not trip it |
| `kosh_muc` (dequeue) | **`kosh_apanay`**; `kosh_pop` is `kosh_hri` |
| `akshar_tas` (char_from) | **`anka_akshar`** |
| `likha_bindu` (lkhb) | **`likha_santat`** |
| `saha` (help) - Muse | **`sahayata`**, Muse's recommendation - it already exists as the shell's help word, so `help` simply became its deprecated alias |
| `smaran_kriti` (smaran_cp) - Muse | **`smaran_pratilip`**, Muse's recommendation - `pratilip` is already the project's copy word (`vartani_pratilip`) |

Muse's R107 recommends the same two names (`sahayata`, `smaran_pratilip`), and verifies the three of yours. All five replacement names were checked like the rest: free as identifiers on v291, none used anywhere in the tree,
none a keyword or builtin.

### `Error → truti`: left alone - it crosses your other rule, not the frozen-pack one

You said the `.sandesh` edit does not cross the frozen-pack rule, and I accept that; it is not the reason. The
reason is WS4. **`Sutram Error` is not only compiler output: twelve kinds of run-time message are compiled into
the programs themselves** (`E_GAHANATA`, `E_SHUNYA_BHAJAN`, the `mala` bound, `kshetra purnam`, `E_PARIMITA`, the
empty-`kosh` ones...), and **443 of the guard's programs carry at least one** (R110's measurement). So there are
two ways to do it, and neither fits this round:

- **compile-time messages and packs only:** the compiler says `truti`, and a program that fails at run time says
  `Error` - **the mixed vocabulary you said is worse than an English word;**
- **everywhere:** **443 programs DIFFER** (in message bytes only) - **the behaviour change WS4 says to stop on.**

**So `Error` stays, and so do the eleven `.sandesh` files** - untouched. If you want it, say "accept the 443": I
will change every one, including the packs, and the guard will check that each of the 443 differs only inside its
message strings.

**Muse's R107 (`9156546`, which landed while I built) reaches the same answer by the other road:** it says the
`.sandesh` edit *does* cross the frozen-pack rule as written, and recommends a narrow owner exception (only
`Sutram Error` → `Sutram truti` in the ten frozen packs). Put together, the full change needs **two** decisions
from you: that exception for the packs, and accepting the 443 programs whose run-time message bytes change. With
both, it is a round of its own.

**The other message words:** `file`, `line`, `hai`, `karo` - **0 instances** in any compiler message (or the IDE's).
`se bhinn` - one, `r54_msg_arity`, **a string nothing prints**; changed to `nasti` anyway. So there was nothing else
to change. The brief's 2/2/2/1 were supplied counts (ChatGPT's R179 says the same).

## WS3 - built: aliases, and what "primary" means here

**22 builtins.** The new names are the rows in the compiler's table; the old ones are a second block of rows with the same
builtin ids and a parallel list naming each replacement:

| new | old | new | old |
|---|---|---|---|
| `kosh_kship` | `kosh_push` | `pankti_gan` | `pankti_len` |
| `kosh_hri` | `kosh_pop` | `jala` | `netsock` |
| `kosh_gan` | `kosh_len` | `jala_bandh` | `netbind` |
| `kosh_ksham` | `kosh_cap` | `jala_shru` | `netlisten` |
| `kosh_iksh` | `kosh_peek` | `jala_grah` | `netaccept` |
| `kosh_rikt` | `kosh_empty` | `akshar_laghu` | `char_lower` |
| `kosh_shodh` | `kosh_clear` | `akshar_guru` | `char_upper` |
| `kosh_yuj` | `kosh_enqueue` | `anka_akshar` | `char_from` |
| `kosh_apanay` | `kosh_dequeue` | `vartani_sandhi` | `vartani_cat` |
| `likha_santat` | `lkhb` | `likha_rup` | `likha_fmt` |
| `sankhya_bindu` | `sankhya_dot` | `smaran_pratilip` | `smaran_cp` |

Plus **`asti` / `nasti`** and **`tyaj`** (the shell) = **25 new names**, as you counted.

**The warning** (stderr, so a compile's normal output is unchanged; once per name per compile):

```
Sutram suchana: 'kosh_push' purana nama - 'kosh_kship' likhatu
```

It fires **only on an old name written in the program's own file** - found through the R51 origin map. Two cases stay silent on purpose:

- **a module the program `yoj`s.** `lib/` uses `kosh_len` in three files. A user who writes only `yoj ganit` would
  otherwise be warned about code they never wrote, and rewriting the library text would move it under the
  library-proof gates for nothing. So `lib/` keeps its old names this round (they compile to the same bytes).
- **a language pack's own word.** The frozen Gujarati pack maps `કોશઉમેરો` to `kosh_push`; a Gujarati programmer
  wrote no old name, so they get no warning. (The pack's words live in their own table; only the Latin row warns.)
- **any `--lang` run.** The pack-messages gate holds the owner's R11 rule - *every line a pack run prints is in
  that pack's language*. My first build printed the (romanised Sanskrit) warning under `--lang hindi` too, and that
  gate failed: `sanskrit kosh_empty: Latin ['kosh_hri', 'likhatu', 'nama', 'purana', 'suchana']`. Translating the
  warning would be new text in ten frozen packs, so instead **the warning prints only without `--lang`**. A Hindi
  programmer who writes the Latin `kosh_push` compiles exactly as before and is not told. That is a real gap, and
  closing it needs the packs.

The warning's Sanskrit is my proposal (`suchana` notice, `purana nama` old name, `likhatu` let it be written) -
**it needs native-speaker review**, like every message.

**`asti` / अस्ति and `nasti` / नास्ति are the tokens `==` and `!=`** - the lexer emits the very token, so precedence,
the string comparison (v287), the fast paths and every later stage see `a == b`. `==` and `!=` still work.

**The shell:** `tyaj` leaves; `exit` and `quit` still leave and `help` still helps, each with the warning;
`nirgat` and `sahayata` unchanged. The shell's banner and help text still name `nirgat`, because they are
pack-translated messages and changing their code words fails every pack's check - so not this round.

## The goldens, and the proof that old = new

- **New names work:** example **322** uses 15 of the new names and runs. **Old names work:** **323** is the same
  program with the old names - **the same golden, and the two compile to byte-identical binaries.**
- **`asti` true, `asti` false, `nasti` true, `nasti` false:** examples **324, 325, 326, 327** - each also prints the
  Devanagari and the `==`/`!=` spelling, and each compiles to the same bytes as its `==`/`!=` version.
- **The warning fires on old and not new:** that is stderr, which the suite does not record for a program that
  compiles, so it is **a new gate, `R111 vocabulary`** (`tests/r111/test_vocabulary.py`, **55 checks, 0 failed**):
  - for each of the 22 pairs, on ELF and on PE, the old-name and new-name programs are **byte-identical**; the old
    one prints exactly its one warning; the new one prints none (44);
  - `asti` / `nasti` / अस्ति / नास्ति give the bytes of `==` / `!=`, and print 1 0 1 0;
  - a name used twice warns once; an old name inside a `yoj`'d module, a Gujarati pack word, and any `--lang`
    run do not warn;
  - the shell: `tyaj` silent; `exit`, `quit`, `help` warn and still work.
- **Eight refusal goldens re-recorded** (120, 121, 270, 287, 314, 316, 320, 321): these examples are refused on
  purpose and use an old name, and a refusal's golden records the compiler's output - so they now end with the
  warning line. **I diffed each against its old golden: the only change is the added `Sutram suchana` line(s)**
  (`evidence-r111/golden-diffs/`). **And one pack-messages golden**, `tests/sandesh/expect/default/kosh_empty.out`
  (its case calls `kosh_pop`): one added warning line, the default language only - its eleven `--lang` twins are
  unchanged.

## WS4

Guard above: **0 DIFFER on all three paths.** The arena: not merged. The reference-type class: not touched.

## Three things found on the way

- **My gate runner was stale, and that touches R109 and R110 as well.** I run `gates.sh` through a copy that also
  saves each gate's output; the copy dated from R101. So in R109 and R110 it lacked R109's two parsing edits (the
  suite read from its last line; the installer's new wording on PASS). Neither changes a result there - the
  installer gate failed, and no suite detail contained `PASS=` - so **the 59 / 1 / 1 reported then stands**. But it
  also meant this round's first gate run skipped the new `R111 vocabulary` gate. The runner is now regenerated from
  the current `gates.sh` (it differs by one line, `evidence-r111/gate-runner.diff`), and the figures above are from it.

- **The shell reads piped input in chunks, not lines:** `printf 'help\nnirgat\n' | sutram -i` gives the shell
  `help\nnirgat` as one command, which it compiles as code (`agyat naam 'help'`). v291 does the same - it is not
  from this round. Typed at a terminal it works. Not fixed; reported.
- **`else` is `anya`:** I wrote `anyatra` in a first draft of 324-327 and it was refused (`anyatra` is in the
  retired-spelling table). Fixed before recording.

## Not done

- **`Error → truti`** - above; one sentence from you and it is a round.
- **`examples/` and `lib/` still use the old names** - so the guard compared identical sources. Moving them to the
  new names is a separate, guarded round (125 programs; the census lists them).
- **The Windows GUI and the terminal IDE's highlighting lists** still list the old names (the GUI is a committed
  Windows binary); the new names compile there but are not coloured as builtins.
- **Native-speaker review** of the warning text and the new names: NOT RUN. **Windows:** the PE outputs are checked
  under Wine and byte-for-byte against Linux; not run on real Windows.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, every pack file (all eleven `.sandesh` and all eleven `.lang`), `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
