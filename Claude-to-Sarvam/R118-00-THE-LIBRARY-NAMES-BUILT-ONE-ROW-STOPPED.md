# R118-00 — Of the 33 words, 18 were already aliases (R111) and are now out of the examples too; 7 more are built here - ten library names and a hint - as aliases, 0 programs changed. One row STOPPED on the frozen packs (`arr`), four messages wait for your call, and 8 words stay, each with its reason. `patra_asti`: I would still not withdraw it silently - here is why.

- **Commit on `main`:** **`792acf4`** - the round in one commit (rebased onto Muse R117 `1897489` and ChatGPT R192 `f14c289`, which landed while I built; your R118 base `bce5405`). The Muse comparison and the Wine line were added in the commits after it.
- **Compiler: `Sutram 1.0 (v297) - sampurna sutra`** (was v296). Linux x86-64 cloud.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `suite: NO-EXPECTATION=4  PASS=315  (319 run)`**, FAIL=0 (313 + goldens 346, 347; eight refusal goldens re-recorded, below).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 62 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, payload v243, as before; NOT-RUN: Windows execution) - 64 gates now, with the new **`R118 library names` (28 checks, 0 failed)**.
- **The guard, origin/main (v296) → v297, 725 programs** (`evidence-r118/guard.txt`):
  - **Linux ELF: 580 byte-identical, 143 refused identically, 0 DIFFER, 2 new** (346, 347).
  - **Linux PE: 580 byte-identical, 143 refused identically, 0 DIFFER, 2 new.**
  - **The Windows compiler under Wine: still running when this was pushed - its line follows in the next commit.**
  - **81 of those programs' source text changed** (the examples and tests now write the new names): **73 compile to the bytes the old text did on v296, 8 are refused as before.** The guard compares a refusal's exit, not its text; those 8 are the re-recorded goldens below, whose text differs only in the hint line.
  - **The guard ran twice, and the first run was right to fail** - below.

## WS1 - the 33, row by row

**The 33 are words, not names:** ChatGPT's CSV counts a word wherever it is part of a student-facing name or message. So I mapped each word to the names and messages that carry it, re-read each on v296, and classified them (`evidence-r118/the-33-words.txt`, one line each):

| | words | what |
|---|---:|---|
| **already aliases since R111 (v292)** | **18** | `cap cat char clear dequeue empty enqueue fmt from len lower netbind netlisten netsock peek pop push upper` - the CSV is right that students still meet them: **72 examples and 10 library modules still wrote the old names.** Now they write the new ones (257 + 57 replacements, outside string literals); `examples/323` keeps the old ones on purpose |
| **built this round, as aliases** | **7** | `bit diff pad pre sign sorted` → **ten library `prakriya`**, and `fd` in a hint; also the `len` / `fmt` hints |
| **STOPPED - the frozen packs** | **1** | `arr` (the shell's help) |
| **built-able, but changes program bytes - your call** | (4 messages) | the `kosh` messages naming `pop` / `peek` / `dequeue` / `push` |
| **kept, with the reason** | **6** | `bit` in "64-bit", `dot`, `enter`, `lib`, `space`, `tab` |
| **not English** | **1** | `path` |
| **not student-facing** | **1** | `root` |

### Built: the ten library names

| new | old | module | meaning (WS2's rule 4: what it does) |
|---|---|---|---|
| `ekanka_gan` | `bit_gan` | `ganit` | count (गण) of the 1-digits (एकाङ्क) of `n` in binary - which is what a set bit is |
| `rakh_ubhaya_bhed` | `rakh_samroop_diff` | `sangrah` | the difference (भेद) both ways (उभय): `(a - b)` with `(b - a)` |
| `roop_purti_vam` / `_dakshin` / `_madhya` | `roop_pad_*` | `roop` | filling (पूर्ति) on the left / right / both sides |
| `purti_vam` | `pad_vam` | `vakyank` | the same, on a `mala` of character codes |
| `roop_ank_upasarga` | `roop_ank_pre` | `roop` | a number with its prefix (उपसर्ग): `0b`, `0o`, `0x` |
| `roop_chihna_akshar` | `roop_sign_akshar` | `roop` | a number with the sign character (चिह्न) you give for `+` |
| `asti_kramabaddha` | `asti_sorted` | `shreni` | 1 if the array is in order (क्रमबद्ध), non-decreasing |
| `suchi_asti_kramabaddha` | `suchi_asti_sorted` | `suchi` | the same for a `suchi` |

**The four rules, checked** (`evidence-r118/new-names-collision-check.txt`, the script beside it):

- **Complete words:** एकाङ्क, उभय, भेद, पूर्ति, उपसर्ग, चिह्न, क्रमबद्ध - each a whole word or compound. `gan`, `vam`, `dakshin`, `madhya`, `rakh`, `roop`, `asti` are the library's own words already.
- **No collision in any namespace** - checked on v296 against: every string in the compiler (keywords, builtins with their old rows, the retired table, every message); every library `prakriya`; every identifier in `examples/`, `lib/`, `tests/`, `tools/`; the eleven `.lang` and the eleven `.sandesh` files; and each name compiled as a variable, as a `prakriya`, and as a call with a space before `(` (the shape that tripped the scanner in R110). **11 names, 0 collide.**
- **Typeable:** ASCII, as the rest of the library.
- **Two I want a second eye on:**
  - **`purti`, not `puran`:** पूरण is the textbook word for filling, but romanised it is `puran`, which a reader takes as पुराण, "old" - and *purana* is the deprecation message's own word ("purana nama").
  - **`chihna`, not the library's `chinhit`:** `roop_chinhit` (signed) spells चिह्नित the Hindi way. I kept the Sanskrit spelling for the new name; if you want the two to match, `roop_chinh_akshar` is free too.

### Muse's audit landed while I built - the two sets of names, side by side

**Muse's `ROUND-117-33-NAMES-AUDIT.md` (`1897489`) reached main while I was building, and I saw it only when my push rebased onto it.** So I built my names, not Muse's. **We agree on the classes**: the same 19 already renamed or withdrawn (my 18 plus `dot`), and the same words that stay. We differ on five of the seven new names, and on two of the stays:

| row | Muse R117 | built here (v297) | my reason, for you to decide |
|---|---|---|---|
| bit | `dvyank_gan` | **`ekanka_gan`** | *dvyanka* is "binary digit", so `dvyank_gan` reads "count the binary digits" - all of them. The function counts the **ones**, and Muse notes the docs must say so. एकाङ्क names the ones, so the name says it |
| diff | `rakh_samroop_bhed` | **`rakh_ubhaya_bhed`** | both are sound. Muse's keeps the old name's `samroop`; mine says "both ways", which is the definition the comment gives. **Either; your pick** |
| pad | `roop_puran_*`, `puran_vam` | **`roop_purti_*`, `purti_vam`** | romanised, `puran` is also पुराण, "old" - the deprecation message's own word (*purana nama*). Muse chose `puran` over `pur` ("city"), but did not weigh "old" |
| path | `patra_marga_sarv` | **not renamed** | `path` here is पठ्, *read*: the pair is `patra_path_sarv` / `patra_likh_sarv`, read all / write all, and the module header says so. Both take a path, so `marga` would drop the one thing the name distinguishes: that it reads |
| pre | `roop_ank_upasarg` | `roop_ank_upasarga` | spelling only: Muse drops the final *a*, as the library does (`ank`, `bhed`, `gan`). Your rule 1 says "complete word"; **either; your pick** |
| sign | `roop_chihn_akshar` | `roop_chihna_akshar` | the same spelling question |
| sorted | `asti_shrenit` | **`asti_kramabaddha`** | `shrenit` ties to the sort module and is shorter, but *shrenita* is a coined participle. क्रमबद्ध is a standard compound that means "in order". A native speaker should settle it |
| fd (stay) | stays | changed to `dvara` | Muse is right that it is a placeholder, not an API name. But it sits between `smriti` and `sankhya` in a Sanskrit hint; `dvara` makes the line one language. **Compile-time text only; easy to revert** |
| arr (stay) | stays: "a parameter name" | stays: **STOPPED** | the CSV's bucket-1 `arr` is the **shell help** (`mala arr[5]`), not a parameter. Muse reaches "stays" for a different reason; mine is the frozen packs |

**If you pick Muse's name for any row, it is a small change:** one line in the compiler's table, the library definition, and the docs. The v297 name would simply go - nothing outside the tree can depend on it yet. **I would not ship both sets.**

**How the alias works** (v297, `r118_lib_alias` in the compiler):

- The library **defines only the new name.**
- After lexing, a call (an identifier followed by `(`) to an old name becomes the new name - unless a `prakriya` of the old name is defined anywhere in the program or its modules. **A program's own `asti_sorted` stays its own:** no rewrite, no warning.
- **A `prakriya`'s name is not in the compiled program, so both spellings give the same bytes**, ELF and PE.
- The warning is R111's, once per name, in the program's own file, never in a `--lang` run:

```
Sutram suchana: 'asti_sorted' purana nama - 'asti_kramabaddha' likhatu
```

- A call to an old name in a `yoj`'d module is rewritten and not warned about. A variable called `bit_gan` is not touched.
- An old name used without its `yoj` gets the usual refusal, naming the module of the new name.
- **The gate `R118 library names`** checks all of it - each pair byte for byte on ELF and PE, the run output, and each of the exceptions: **28 checks, 0 failed.**
- **Examples 346 and 347** call all ten old names, with goldens.

### Built: the hints

**Three compiler hints still taught the R111 old names:**

- `kosh_len(k)` in the five `E_KOSH_*` hints → `kosh_gan(k)`;
- `likha_fmt` in the `parikshita` hint → `likha_rup`;
- `dvaram_likha(fd, ...)` → `dvaram_likha(dvara, smriti, sankhya)` (`fd`, like the builtin `dvaram`, is the file's door).

They are compile-time text, so no program changes. **Eight refusal goldens re-recorded** (`evidence-r118/goldens-re-recorded.txt`, every diff). Each diff is that hint line and the R111 warning line, which is gone because the example now writes the new name. Nothing else.

### STOPPED: `arr` - the frozen packs

The shell's help says `mala arr[5]`. **All eleven packs translate that help, and keep `arr` in it.**

I changed the default to `mala pankti[5]` in a scratch copy, and `tools/sandesh.py --check` - the `language packs` gate - fails **11 times**: *"code word 'arr' is not in the default"* (`evidence-r118/pack-check-if-messages-changed.txt`). Fixing it means editing ten frozen packs. **That is the R114 kind of decision: a narrow owner exception, one word in each pack.** Say so and it is one line in each pack.

### Waiting for your call: the four `kosh` messages

`riktat koshat kosh_pop` (and `_peek`, `_dequeue`), and the compile-time `kosh-tarke kosh_push asamarthitam`, still name the old builtins.

- **The pack gate does not stop this one.** The packs write `{kw:kosh_pop}`, so changing the default passes (part 2 of the same file).
- **But two costs I will not take without you:**
  - **three of the four are compiled into programs**, so **27 of the guard's 580 compiled programs** would change bytes (in the message only);
  - **the ten frozen packs would go on saying `kosh_pop`** while the default says `kosh_hri` - a mixed vocabulary, which you said is worse.
- **With your yes to both, it is an hour,** and the guard will show 27 programs differing in those bytes only.

### Kept, with the reason - say if you disagree with any

| word | where | why it stays |
|---|---|---|
| `bit` | "64-bit purnanka-seemam" (two `E_ATIPRAVAH` texts), "bit-kriyah" | **a unit**, as ChatGPT's bucket 4 keeps `kilograms`. A Sanskrit word for it would be coined, and that is for a native speaker, not me. (The function `bit_gan` is renamed.) |
| `dot` | `E_PRATYAHRITA`'s "sankhya_bindu (sankhya_dot)" | it names the withdrawn spelling it is refusing (ChatGPT R191 says the same) |
| `enter` | the shell banner, "Enter nudatu" | **the label printed on the key** (and pack-translated) |
| `lib` | "naam.smlib lib/ madhye" | **the directory's name**, a file identity (and pack-translated) |
| `space`, `tab` | `E_ANTARAL_MISHRA`: "tab space cha mishritau" | the names of the two keys/characters the student is told not to mix |

### Not English, not student-facing

- **`path` is Sanskrit:** `patra_path_sarv` is पठ् (paṭh), *read*: "read the whole file". Its sibling is `patra_likh_sarv`, *write* the whole file. **The CSV's "context" warning was right; it is not renamed.**
- **`root` is `__root__`, the module graph's internal name for the program.** No message prints it: I built an import cycle and the message names the modules only. Not renamed.

### Your three checks from last time

- **The keyword namespace:** checked - every string in the compiler, which includes the keyword table, the builtin table (new and old rows) and the retired spellings. **No new name is a keyword.**
- **The eleven `.lang` and eleven `.sandesh` files:** checked, no new name in any of them.
  - **A finding:** the packs' *target* column still says `kosh_push`. That column is internal: the student types the native word, and a pack word never warns. The r66/r67 gates pin those rows, so I left them.
  - **`कोशपोप्`**, which reads as English "pop" in Devanagari, is **not new**: it is `docs/WHATS-LEFT.md` C6.
- **Stopped where a row could not be built as written:** `arr`.

### The guard failed the first time, and it was right

**My first build showed 37 DIFFER, every one with the same output.**

- The cause was mine: I had added a comment line *"(R118: was `asti_sorted` ...)"* above each renamed function. **A run-time message in a library function carries its line number**, so one added comment line moved every later function's line, and changed the bytes of every program that imports that module.
- I put the note at the end of an existing comment line instead. **Line counts are now equal, module by module, and the guard is 0 DIFFER.** The first run's files are in `evidence-r118/guard.txt`.
- **The lesson, for anyone editing `lib/`: a comment line costs every importer's bytes; a comment on an existing line costs none.**

## WS2 - the four rules

They were applied to every new name above. Two candidates failed them and were not used:

- **`puran`** - it reads as "old".
- **a coined word for "bit"** - it fails "a complete Sanskrit word" unless a native speaker supplies one.

## WS3 - `patra_asti`: withdraw it, if you like, but as a refusal, and not on that reason

**Your reason understates it.** On v296 it is not "wrong only for permission-denied files and symlink loops". I measured (`evidence-r116/patra_asti-today.txt`, R117):

- **it hangs forever on a FIFO** (the `open` blocks) - a program that asks "is it there?" never comes back;
- **it disagrees across platforms:** a directory is **1 on Linux and 0 on Windows**;
- a symlink loop and an unreadable existing file say **0, "absent"**, which is false.

**If it is not built for v1.0, I agree with withdrawing it - but withdraw it the way `sankhya_bindu` was:** a reserved name that refuses when compiled (`E_PRATYAHRITA`), naming what to do instead (`paadh` and test for `-1`, with that function's known limits). Not a function that ships wrong, and not a silent removal.

- **That is about an hour** with its gate. In the tree only one test calls `patra_asti` (`tests/stdlib/file_read.sm`).
- **Not done this round, as you said.**

## WS4

- **The arena is not merged.** `claude/r108-arena-review` is still `3a6292e`.

## Not done, and why

- **`arr`** (frozen packs) and **the four `kosh` messages** (27 programs' bytes, and the packs) - decisions above.
- **The pack target column** (`kosh_push` in `sanskrit.lang`, `gujarati.lang`) - internal, pinned by gates.
- **`docs/vocabulary/*` and the language books** still list the old library names: they are R96-era vocabulary records and translated books. The reference (§4c), the generated library page and `NUMERIC-CONTRACT.md` are updated.
- **Tests** keep the old *builtin* names (they test R111's aliases among other things). Their calls to the *library* names were moved, because some gates key on library function names.
- **Not run:** Windows execution (no Windows host).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, every pack file, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
