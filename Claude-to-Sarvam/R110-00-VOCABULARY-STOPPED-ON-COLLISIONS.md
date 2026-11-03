# R110-00 — STOPPED before implementing, as WS3 says: the collision check found one collision in the table, one with the frozen packs, and one with a known scanner bug. Nothing is renamed. The decision sheet is below.

- **Commit on `main`:** `7218132` (documentation and evidence only; on top of Muse's R106, `c6b41df`, and your R110 files, `632c7e0`).
- **Compiler: `Sutram 1.0 (v291) - sampurna sutra`, unchanged** (the brief says v290; R109 made it v291).
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `suite: NO-EXPECTATION=4  PASS=289  (293 run)`, FAIL=0** (re-run on this tree).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux cloud): 59 PASS / 1 FAIL / 1 NOT-RUN** (re-run on this tree; FAIL
  `installer version`, `payload v243 inside Sutram-Setup.exe`; NOT-RUN Windows execution).
- **The guard: not run** - no compiler, library or example changed, so there is nothing to compare. R109's run
  (v290 → v291, 699 programs, 0 DIFFER on ELF, PE and Wine) is the current one.

## Why I stopped

You wrote: *"If you find one, STOP and report it before implementing."* I checked the 28 names more widely than
against the builtin table - against the keywords, the include scanner, every identifier in `examples/`, `lib/` and
`tests/`, the eleven `.lang` packs and the eleven `.sandesh` message files, and each name compiled as an identifier
on v291 (`evidence-r110/`). **Three rows cannot be built as written**, and one of them reaches the frozen packs, so
a partial build would either break your frozen-pack rule or ship a mixed vocabulary. The other 25 names are clean,
and the build is straightforward once the three rows are decided.

## Collision 1 - `to → prati`: `prati` already means *return*

- **`prati` is a keyword today: the legacy spelling of `nivartanam`, return** (R53, `kw_prati_alias`; 60 files in
  the tree use it). It is not a loop word.
- **`to` is not accepted at all.** It is in the table of retired spellings (`r4_old_kw`) whose replacement is
  **`tak`**, the `chakra` loop's "up to". `chakra i = 0 to 3` is a syntax error on v291 (`programs/to_word.sm`).
- So the row would either make the loop word mean return, or "delete" something that is already gone.

**My suggestion: drop the row.** `to` stays retired, `tak` stays its word, and `prati` stays the return alias. If you
want `prati` freed from *return*, that is a separate change, with its own migration of those 60 files.

## Collision 2 - `Error → truti`: the frozen packs require `Sutram Error`, word for word

**The pack check (`tools/sandesh.py --check`, the `language packs` gate) requires every translation to keep
`Sutram Error` unchanged and to contain no Latin word the default lacks.** I made the change in a scratch copy and
ran it: **748 failures, 68 in each of the eleven packs** (`sandesh-check-with-truti.txt`). The Sanskrit pack can be
updated. **The other ten are frozen, and every one of their 68 translated error messages carries `Sutram Error`.**
So this row cannot be done without either editing frozen packs or changing the rule the gate enforces.

**And the run-time messages.** Not all "Error" strings are compiler output: twelve kinds are compiled *into the
programs* (`E_GAHANATA`, `E_SHUNYA_BHAJAN`, the `mala` bound, `kshetra purnam`, `E_PARIMITA`, the empty-`kosh`
messages, ...). **443 of the 558 programs the guard compiles carry at least one of them**
(`runtime-messages-in-compiled-programs.txt`). Changing them changes those 443 binaries, which conflicts with
*"0 DIFFER except where a warning is now printed"*.

The count is also not 109: about 120 source lines carry `Sutram Error` (115 in `sutram_compiler.asm`, 5 in
includes), and 68 of them are messages the packs translate.

**Options, for you to choose:**

| | default (no `--lang`) | `--lang hindi` etc. | compiled programs | cost |
|---|---|---|---|---|
| **A** | `Sutram truti` | `Sutram Error` (frozen text kept; `sandesh.py`'s rule changed to accept the old tag in frozen packs) | unchanged ("Error" at run time) | mixed: the compiler says `truti`, a program that fails at run time says `Error` |
| **B** | `Sutram truti` | as A | `Sutram truti` | **443 binaries DIFFER**, each only in message bytes - the guard can verify that, diff by diff |
| **C** | defer the row until the packs are unfrozen | | | none now |

I would choose **B**: one word everywhere Sanskrit is spoken, a guard that proves the only change is the
message, and the frozen packs left word for word as they are. But it changes your guard expectation, so it is
your call.

## Collision 3 - `vartani_yoj` trips a known scanner bug

**The include scanner takes `yoj` followed by a space as an include wherever it appears, even at the end of a
longer name.** `vitti sanyoj = 7` fails with `E_MODULE_MISSING: yoj patra aprapt: =` (`programs/yoj_suffix.sm`).
**This is not new:** my R30 hand-back reported it (`vitti sanyoj = 4`, ChatGPT's R30-02), and the fix is on the
review branch `claude/round-30-yoj-scan`, unmerged, waiting on your decision since v240. Nothing in the tree hits it.
**`vartani_yoj` would:** written as `vartani_yoj ("ab", "cd")` - with a space, as people do - it becomes an
include. Written `vartani_yoj("ab", "cd")` it works.

**Options:** merge the R30 scanner fix first (re-done on v291 - small, and it was 559 / 0 DIFFER then), or pick a
name that does not end in `yoj` (`kosh_yuj` is fine, because it ends in `yuj`).

## What the build looks like once these are decided (not built)

The other rows are collision-free. In `new-names-as-identifiers-v291.txt`, every other new name compiles as an
ordinary name today, so none is already taken - only `prati` (a keyword) and `vartani_yoj` (the scanner) do not.
None appears as an identifier anywhere in the tree. Five things the brief does not say,
which I would do unless you say otherwise:

1. **The warning fires on the old Latin spelling in the source, not on the builtin.** The frozen Gujarati pack
   maps its own words to `kosh_push`, `kosh_len` and others (`lang/gujarati.lang`); a warning keyed to the builtin
   would fire on every Gujarati program and name a Sanskrit replacement. Keyed to the spelling, it fires only where
   `kosh_push` is written.
2. **`lib/` moves to the new names** (3 files use `kosh_push` / `kosh_len`), and so does the Sanskrit `.lang` pack.
   Otherwise a program that only writes `yoj ganit` gets warnings about code it never wrote. The compiled bytes are
   the same, and the guard will show it.
3. **`examples/` keep the old names this round.** Then the guard compares identical sources, and the old names are
   proven to compile byte-identically. They move in a later round, also guarded. (48 examples use `kosh_push`;
   `old-names-in-the-tree.txt` has every count.)
4. **`exit`, `quit` and `help` are commands of the interactive shell (`-i`), not builtins;** `nirgat` and `sahayata`
   already exist there. `tyaj` and `saha` become shell commands beside them.
5. **The messages that name a builtin** (`riktat koshat kosh_pop` and others, also in eleven packs as `{kw:kosh_push}`)
   **keep the old name until collision 2 is decided** - they are the same pack rule.

The warning needs a Sanskrit text you have not given. My proposal is
`Sutram suchana: 'kosh_push' purana nama - 'kosh_kship' likhatu`; it needs your approval, and native-speaker review.

**Count check:** the brief says the 28 names were checked against "90 builtins". The builtin table has **48
entries** (`bn_table`, including the two `parimana` spellings and `kosh_enqueue`, which is `kosh_push`). The 90
may count something else; it does not change the result.

## Muse's R106 audit, which landed as I pushed - where we agree and differ

Muse (`c6b41df`, `Muse-to-Sarvam/ROUND-106-VOCABULARY-AUDIT.md`) says *"No blocking collision"*. Both of us are
right about what we checked:

- **We agree on `to`:** its replacement is `tak`, not `prati`. Muse calls the row safe to delete but wrongly
  annotated; I call it a collision with the keyword `prati`. Either way the row needs correcting before it ships.
- **Muse matched names against tables** (builtins, keywords, library, `.lang`, example identifiers). It did not
  compile the names or run the pack check. **The two measured conflicts above are outside that method:** the
  frozen packs' `Sutram Error` rule (748 failures when run) and the include scanner taking `vartani_yoj ` as an
  include (compiled: `E_MODULE_MISSING`). The names themselves collide with nothing in the tables - on that we
  agree.
- **Muse adds what I did not judge, the Sanskrit:** five names wrong in meaning (`kosh_muc` for a dequeue that
  releases nothing, `akshar_tas` backwards, `likha_bindu` for a function that prints no point, `saha` "with"
  truncated from `sahayata`, `smaran_kriti` where the project's copy word is `pratilip`), and 13 bare roots. That is
  one more reason to settle the table before it is built: an alias, once primary, is hard to take back.
- **Counts:** Muse finds 30 names, not 28, and 47 builtins. I count 48 rows; `bn_dev_parimana` is the Devanagari
  spelling, so Muse's 47 counts each name once. The rest of our figures agree: the old names are used in 69
  examples and 3 library files.

## WS4 - the arena

Not merged, as you said.

## Not done

- **WS1 and WS2 (all 28 aliases and `asti` / `nasti`): not built** - stopped on the collisions, as WS3 instructs.
  `asti`, `nasti`, अस्ति and नास्ति are free as names today, and nothing in the tree uses them as identifiers. The four
  goldens are ready to write the moment you decide.
- **The guard:** not run, because nothing changed.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs' sources (the `truti` experiment ran in a
  scratch copy and was deleted), `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
