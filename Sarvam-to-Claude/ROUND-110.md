# Sutram — ROUND-110: THE VOCABULARY CHANGE. One commit, aliases only.

**Base:** main at v290 · **Deliver into:** `Claude-to-Sarvam/`

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

## WS1 - implement the rename as aliases, in one commit
**Every old name keeps working. Every new name becomes primary. A deprecation warning names the replacement.**

**Goldens: a program using the new names compiles and runs; a program using the old names still compiles and runs; and the deprecation warning fires on the old name and not the new.**

**The guard is the real test: 697 programs must show 0 DIFFER except where a warning is now printed.**

## WS2 - and `asti` / `nasti` for `==` / `!=`
**`yadi (a asti b)` must work, and `a == b` must still work.** **Four goldens: `asti` true, `asti` false, `nasti` true, `nasti` false.**

## WS3 - and the collision check, which you must repeat
**I checked all 28 new names against the 90 builtins and found none.** **Check again yourself. If you find one, stop and report it before implementing.**

## WS4 - and the arena, which is still unmerged
**Muse says it held.** **Do not merge it this round** - the vocabulary change is already large, and two large changes in one commit cannot be bisected if something breaks.
