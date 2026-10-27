# R44-00 — Hand-back to Sarvam: the first lines

- **The rename is ONE commit on `main`: `cca5b35b2e52e5b02a5350a17d2485e46902eec4`.**
  - **A veto reverts it whole:** `git revert cca5b35b`.
  - This hand-back is a separate commit, so reverting the rename does not delete the record.
  - Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v250) - sampurna sutra`.**
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=224`, FAIL=0.** That is 223 plus the new test 256.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud, with a display (Xvfb): 41 PASS / 0 FAIL / 1 NOT-RUN.** The
  NOT-RUN is Windows execution.
- **The guard:** I compared each program in its old form, compiled by v249, with its new form, compiled by v250.
  **574 programs: 480 byte-identical, 93 refused identically, 0 DIFFER, 1 new.**
  - The 1 new program is test 256.
  - It held on all three paths: the Linux compiler to ELF, the Linux compiler to PE, and the Windows compiler under
    Wine.

## WS1 — the rename

| Was | Now |
|---|---|
| `vartani_len` | **`vartani_aayam`** |
| `vartani_cmp` | **`vartani_tul`** |
| `vartani_cp` | **`vartani_pratilip`** |

**Changed:**

- **The compiler:** the builtin table's three strings, and four comments.
- **`lib/varna`, `lib/khand`, `lib/gudh`:** 13 calls and comments.
- **Callers:** 3 examples, 4 `tests/r5x_check` programs, and 3 tools that name the builtins.
- **The Linux IDE's highlight list,** with `sutram-gui` rebuilt.
- **Checked against Muse's independent caller list** (`Muse-to-Sarvam/2026-10-27-round44-rename-pankti.md`):
  its 9 program sites and 9 `lib/` code sites are exactly the ones renamed here. None was missed and none is extra.
- **Pins:** compiler `7b0d8217`, sandesh `58306e21`. **No R70 fixture or expectation changed.**

**The old names are now refused**, with *agyat prakriya: vartani_len*. **I kept no compatibility alias**, as with
the earlier renames.

## WS2 — the loop is closed

`examples/256_r44_vartani_sanskrit_names.sm` calls all three. Among them is **`vartani_pratilip`, the name that
begins with the keyword `prati`.**

- **v249 refuses it:** *agyat prakriya: vartani_pratilip*.
- **v250 prints `6 0 1 2 0`:** length, equal, not equal, the length after a second copy, equal again.

**One consequence, caught by the gates:**

- My R43 boundary test had defined a user `prakriya` named `vartani_pratilip`. **That name is now a builtin, so a
  program can no longer define it.** The test failed, correctly.
- **Its first case now calls the builtin.** The "user prakriya with a keyword prefix" case uses
  **`pratilekha_kuru`** instead.
- 682 checks, 0 failed.

## WS3 — the guard, and a correction to the brief

**The brief expected the callers to compile to different bytes "because the name changed". They do not.**

- **The 7 programs whose source was renamed are all byte-identical.**
- **So are the 53 programs that `yoj` a renamed library module** (`varna`, `khand`, `gudh`).
- **The reason: a builtin's name never reaches the executable, only the code it emits.** No symbol table is
  written.
- **So "the emitted instructions are identical apart from the symbol" holds more strongly: there is no symbol, and
  every byte is identical.**

## What I did NOT do, and why

- **No Devanagari forms in `lang/`. I stopped there on purpose.**
  - **No `vartani_*` builtin has a Devanagari spelling today,** so there is no pattern to follow.
  - **The compound's spelling is a vocabulary decision.** `वर्तनी` + `आयाम` is `वर्तन्यायाम` with sandhi, or
    `वर्तनीआयाम` without. **That decision is the owner's.**
  - **The brief says `lang/*.lang`, but the ten other packs are frozen** (`LANGUAGE-PRIORITY.md` wins). So at most
    `lang/sanskrit.lang` would change.
  - **Candidates, for the owner:**

    | Builtin | With sandhi | Without sandhi |
    |---|---|---|
    | `vartani_aayam` | `वर्तन्यायाम` | `वर्तनीआयाम` |
    | `vartani_tul` | `वर्तनीतुल` | — |
    | `vartani_pratilip` | `वर्तनीप्रतिलिपि` | — |

    Each addition moves `src/r22_lang_builtin.inc` and its pin, and is then tested by `tests/r43` automatically.
- **No prose documents were renamed.** That is ChatGPT's R119 list.
  - Still naming the old builtins: `docs/LANGUAGE-REFERENCE.md` (3), `docs/R54-BUILTIN-BOUNDS.md` (8),
    `docs/R50-BYTE-PACKED-TEXT.md`, `docs/STRING-BYTE-PARITY.md`, and the historical round records.
  - `docs/sutram-stdlib.html` is generated, so `gates.sh` regenerated it.
- **The Windows IDE (`windows/gui/sutram_gui.asm`, `sutram-ide-gui.exe`) still highlights the old names.** It
  belongs to the Windows channel, and its binary does not rebuild reproducibly here.
- **`compiler/verified_snapshots/` is a historical snapshot.** Left as it is.
- **Windows: NOT RUN natively this round.** The Wine guard ran: 480 / 93 / 0 DIFFER. The R42 workflow can be
  started again if you want it on real Windows.
- **I did not touch `backups/`.** No `.lang` file changed.

## A finding: these were not the last English builtin names

The builtin table still has, by my reading:

- **`netsock`, `netbind`, `netlisten`, `netaccept`**
- **`kosh_push`, `kosh_pop`, `kosh_len`, `kosh_cap`, `kosh_clear`, `kosh_empty`, `kosh_peek`, `kosh_enqueue`,
  `kosh_dequeue`**
- **`pankti_len`**, **`vartani_cat`**, **`smaran_cp`**, **`likha_fmt`**, **`sankhya_dot`**
- **`char_from`, `char_upper`, `char_lower`**

**That is 21 names with an English part.** Several of them have Sanskrit Devanagari aliases in
`lang/sanskrit.lang`, for example `कोशपुष् kosh_push`, but the Latin core name is English. **Reported, not acted on:
which to rename, and to what, is the owner's.**
