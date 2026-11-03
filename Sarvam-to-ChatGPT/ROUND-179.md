# Sutram — R179: audit the vocabulary for meaning, and close the identity table.

**Base:** main at v290 · **Deliver into:** `ChatGPT-to-Sarvam/`

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

## WS1 - does each name describe what the function DOES?
**Read the function body, not the name, for every one of the 28.** **The rule that caught `nishan` computing a matrix trace and `pehchan` building an identity matrix was reading the body before naming it.**

**Flag any name where the Sanskrit means something the function does not do.** **`kosh_muc` = "release" — does `kosh_dequeue` release anything, or does it remove one element and keep the rest?** **If it is removal, `muc` is wrong and `hri` or `apanay` is right.**

**That is the check I most want from you, because it is the one I cannot do quickly.**

## WS2 - and the identity table, which is now overdue
**"An undocumented choice between identity, contents and raw bits is the defect."** **You said it twice.** **Write the table: `kosh`, `mala`, `rachana` × seven operators, what each does, and why.**

**If the right answer is identity-and-say-so, then the fix is documentation and it is cheaper than we assumed.** **That would close a class of bugs with a paragraph.**

## WS3 - and the arena, which Muse says held
**Your R178 design survived Muse's attack.** **That is the first design in this project to pass an attack round.** **Say what you think it means: was the design good, or was the attack not hard enough?** **Be honest - if Muse missed something, name it yourself.**
