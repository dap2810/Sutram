# Sutram — ROUND-106: audit the vocabulary change. Find the collision I missed.

**Base:** main at v290 · **Deliver into:** `Muse-to-Sarvam/`

## Where the project is

**Compiler v290 on main.** Outlives rule, `mala` refusal (`E_MALA_GANIT`), `parimana()` moving (318: 0→48→72→184→288→176). Suite 287, guard 697.
**The arena is on `claude/r108-arena-review` (0e71e54), NOT merged. Muse attacked it and reports: "It held."** ChatGPT designed it in R178; Muse found no break.
**Two holes ChatGPT named are closed by the outlives rule** - a `kosh` in a block cannot be aliased or returned.
**ChatGPT R175: "an undocumented choice between identity, contents and raw bits is the defect."** Still open for `kosh`/`mala`/`rachana` operators.

# THE VOCABULARY CHANGE — owner-approved, collision-checked, implement with aliases

**Every name below was checked against all 90 existing builtins. No collision. If you find one, STOP and report it before implementing.**

## Comparison operators
| Now | Final | Devanagari |
|---|---|---|
| `==` | **`asti`** | अस्ति |
| `!=` | **`nasti`** | नास्ति |

`==` and `!=` remain as aliases. `<`, `>`, `<=`, `>=` unchanged this round.

## Error messages
| English | Final | Instances |
|---|---|---|
| `Error` | **`truti`** | **109** |
| `file` | **`patra`** | 2 |
| `line` | **`rekha`** | 2 |
| `hai` | **`asti`** | 2 |
| `karo` | **`kuru`** | 1 |
| `se bhinn` | **`nasti`** | 1 |

So `Sutram Error:` becomes `Sutram truti:`.

## kosh operations
`kosh_push`→**`kosh_kship`** · `kosh_pop`→**`kosh_hri`** · `kosh_len`→**`kosh_gan`** · `kosh_cap`→**`kosh_ksham`** · `kosh_peek`→**`kosh_iksh`** · `kosh_empty`→**`kosh_rikt`** · `kosh_clear`→**`kosh_shodh`** · `kosh_enqueue`→**`kosh_yuj`** · `kosh_dequeue`→**`kosh_muc`** · `pankti_len`→**`pankti_gan`**

## Standalone
`exit`+`quit`→**`tyaj`** · `help`→**`saha`** · `netsock`→**`jala`** · `netbind`→**`jala_bandh`** · `netlisten`→**`jala_shru`** · `netaccept`→**`jala_grah`** · `char_lower`→**`akshar_laghu`** · `char_upper`→**`akshar_guru`** · `char_from`→**`akshar_tas`** · `vartani_cat`→**`vartani_yoj`** · `lkhb`→**`likha_bindu`** · `likha_fmt`→**`likha_rup`** · `sankhya_dot`→**`sankhya_bindu`** · `smaran_cp`→**`smaran_kriti`** · `to`→**`prati`** (already exists — a deletion, not a rename)

## The hard constraint
**`kosh_push` and the rest appear in 289 examples and 306 library functions.** **This CANNOT be a rename — it must be ALIASES.** Old name keeps working, new name is primary, a deprecation warning names the replacement. **No existing program may break.**

## WS1 - the collision audit, and you are the right one to do it
**I checked 28 new names against 90 builtins and found none.** **I have been wrong about counts four times this week, so check again.**

**For every new name: does it collide with a builtin, a keyword, a library function, a `lang/*.lang` entry, or an identifier in any of the 289 examples?**

**Report the count of hits for each. Zero is the answer I expect and I want it measured, not assumed.**

## WS2 - and the Sanskrit
**`truti`, `rekha`, `tyaj`, `saha`, `jala`, `nasti`, `asti`, `kosh_kship`, `kosh_hri`, `kosh_gan`, `kosh_ksham`, `kosh_iksh`, `kosh_rikt`, `kosh_shodh`, `kosh_yuj`, `kosh_muc`, `akshar_laghu`, `akshar_guru`, `akshar_tas`, `vartani_yoj`, `likha_bindu`, `likha_rup`, `sankhya_bindu`, `smaran_kriti`, `pankti_gan`.**

**For each: complete word or root, not a fragment? Correct Devanagari? Meaning matches the function's actual behaviour?** **Read the function body before answering that last one - it is the rule that caught `nishan` and `pehchan`.**

## WS3 - and the census, tenth run
**Three counts, same method.** **And: how many of the 289 examples use an old name that is being renamed?** **That is the population the aliases protect, and I want the number.**
