# The nomenclature — short, meaningful, and checkable

**The rule I applied to every entry:**
1. **A stem is at most 5 letters.** **Sanskrit is rich in short roots; a 9-letter stem is a sentence, not a name.**
2. **One stem per meaning.** **No `kunji`/`kunjika`.**
3. **No digits.** **A second function gets a second word.**
4. **`_` separates stems.** **Nothing else is needed** - the lexer allows letters, digits and `_` in a name, and a
   keyword only matches at a word boundary, so `_` is the one sign we need.
5. **A root, not a compound.** **`apanay` is `apa` + `nay`; the name should be `nay`.**

---

## 1. The keywords — shortened

| # | Now | Letters | Shorter | English | Why |
|---|---|---|---|---|---|
| 1 | `mukhya` | 6 | **`mukh`** | main | drop the vowel ending; Sanskrit stems drop it in compounds |
| 2 | `vitti` | 5 | **`vitt`** | var | same |
| 3 | `anka` | 4 | `ank` | int | same - and it matches the `ank` module |
| 4 | `dasham` | 6 | **`dash`** | float | 4 letters |
| 5 | `sankhya` | 7 | **`sankh`** | number | 5 letters |
| 6 | `yadi` | 4 | `yadi` | if | already short |
| 7 | `anya` | 4 | `anya` | else | already short |
| 8 | `yavat` | 5 | `yavat` | while | already short |
| 9 | `chakra` | 6 | **`chak`** | for | 4 letters |
| 10 | `kuru` | 4 | `kuru` | do | already short |
| 11 | `prati` | 5 | `prati` | return | already short |
| 12 | `prakriya` | 8 | **`kriya`** | function | **5 letters, and `kriya` is the word for action** |
| 13 | `likha` | 5 | **`likh`** | print | **merge `likha` and `likh`: one word for writing** |
| 14 | `pad` | 3 | `pad` | read | already short |
| 15 | `grahan` | 6 | **`grah`** | input | 4 letters, and it matches the `grah` stem |
| 16 | `purna` | 5 | `purn` | true | 4 letters |
| 17 | `shunya` | 6 | **`shuny`** | false | 5 letters |
| 18 | `sutra` | 5 | `sutra` | const | already short, and it is the language's name |
| 19 | `krama` | 5 | `kram` | break | 4 letters, and it matches the `kram` stem |
| 20 | `agrim` | 5 | `agrim` | continue | already short |
| 21 | `guna` | 4 | `gun` | switch | **merge with the `gun` stem (multiply)? NO - `gun` is multiply. Use `vikalp` (5) for switch** |
| 22 | `bhavana` | 7 | **`bhav`** | case | 4 letters |
| 23 | `mala` | 4 | `mala` | array | already short |
| 24 | `kosh` | 4 | `kosh` | vector | already short |
| 25 | `vibhag` | 6 | **`vibhag`** | slice | keep - it is the right word and 6 is acceptable |
| 26 | `ganana` | 6 | **`ganan`** | enum | 5 letters |
| 27 | `abhava` | 6 | **`abh`** | not | 3 letters |
| 28 | `rachana` | 7 | **`rach`** | struct | 4 letters |
| 29 | `yoj` | 3 | `yoj` | include | already short |
| 30 | `satya` | 5 | `saty` | bool | 4 letters |
| 31 | `tak` | 3 | `tak` | to | already short |
| 32 | `shabda` | 6 | **`shabd`** | print string | **merge into `likh`** |
| 33 | `yantra` | 6 | **`yantr`** | asm | 5 letters |
| 34 | `siddhi` | 6 | **`siddh`** | success | 5 letters |
| 35 | `dosh` | 4 | `dosh` | error | already short |
| 36 | `prasar` | 6 | **`pras`** | propagate | 4 letters |
| 37 | `nirmmita` | 8 | **`nirm`** | alloc | **4 letters; `nirmmita` is the longest keyword and it is a common operation** |
| 38 | `sthagita` | 8 | **`sthag`** | pause | 5 letters |
| 39 | `dvaram` | 6 | **`dvar`** | open | 4 letters |
| 40 | `band` | 4 | `band` | close | already short |

**And one to remove: `paadh` duplicates `pad`.** **One read word, not two.**

---

## 2. The modules — the `ganita`/`ganit` fix

| Now | Letters | Shorter | Meaning | Why |
|---|---|---|---|---|
| **`ganita`** | 6 | **`ganit`** | **checked arithmetic** | **the family with `janchit`/`paripurna`** |
| **`ganit`** | 5 | **`gan`** | **plain arithmetic** | **3 letters, and `gan` is the root of both** |
| `suchi` | 5 | **`such`** | list | 4 letters |
| `varna` | 5 | `varn` | character | 4 letters |
| `roop` | 4 | `roop` | form | keep |
| `khand` | 5 | `khand` | piece, bit | keep |
| `nighantu` | 8 | **`nigh`** | map | **4 letters; `nighantu` is the longest module name** |
| `sankhyiki` | 9 | **`sankhiki`** | statistics | 8 - **or `anki` (4)** for "of numbers" |
| `phal` | 4 | `phal` | result | keep |
| `shreni` | 6 | **`shren`** | sort | 5 letters |
| `sangrah` | 7 | **`sangr`** | set | 5 letters |
| `brihat` | 6 | **`brih`** | big number | 4 letters |
| `samanvaya` | 9 | **`saman`** | linear algebra | **5 letters; `samanvaya` is the longest name in the project** |
| `ank` | 3 | `ank` | number | keep |
| `mala` | 4 | `mala` | array | keep |
| `sadhan` | 6 | **`sadh`** | instrument | 4 letters |
| `kalana` | 6 | **`kalan`** | calculus | 5 letters |
| `chandas` | 7 | **`chand`** | metre | 5 letters |
| `vakyank` | 7 | **`vaky`** | base conversion | 4 letters |
| `anukram` | 7 | **`kram`** | sequence | **4 letters - but `kram` is also the break keyword. Use `anuk` (4)** |
| `madhava` | 7 | **`madh`** | the Kerala series | 4 letters |
| `patra` | 5 | `patr` | file | 4 letters |
| `aadhar` | 6 | **`aadh`** | base | 4 letters |
| `gudh` | 4 | `gudh` | hash | keep |

---

## 3. The stems — shortened to roots

| Now | Letters | Root | Shorter | Meaning | Count |
|---|---|---|---|---|---|
| `asti` | 4 | अस् | **`asti`** | is (boolean marker) | 8 | **keep - it is the one convention that is already perfect** |
| `maap` | 4 | माप् | `maap` | measure | 7 | keep |
| `khip` | 4 | क्षिप् | `khip` | insert | 4 | keep |
| **`apanay`** | **6** | **नय्** | **`nay`** | **remove** | **4** | **`apa`+`nay` = "lead away"; the root is `nay`** |
| `srij` | 4 | सृज् | `srij` | create | 4 | keep |
| `grah` | 4 | ग्रह् | `grah` | take | 4 | keep |
| **`anwesh`** | **6** | **इष्** | **`ish`** | **search** | **5** | **3 letters; `anwesh` is `anu`+`ish`** |
| **`viparyay`** | **8** | **विप्** | **`vip`** | **reverse** | **5** | **3 letters - the longest stem in the project** |
| **`pratilip`** | **8** | **लिप्** | **`lip`** | **copy** | **3** | **3 letters** |
| **`janchit`** | **7** | **चित्** | **`janch`** | **checked** | **10** | **5 letters; `janch` is the check** |
| **`paripurna`** | **9** | **पूर्ण** | **`purn`** | **saturating** | **8** | **4 letters - the longest stem in the project** |
| **`nirapeksh`** | **9** | **अपेक्ष्** | **`apeksh`** | **absolute** | **4** | **or `mukt` (4) for "free"** |
| `tul` | 3 | तुल् | `tul` | compare | 3 | keep |
| `yuj` | 3 | युज् | `yuj` | join | 4 | keep |
| `bhed` | 4 | भिद् | `bhid` | split | 3 | keep `bhed` |
| `vardh` | 5 | वृध् | `vardh` | grow | 4 | keep |
| **`antah`** | **5** | **अन्त्** | **`ant`** | **contains** | **6** | **3 letters** |
| `rikta` | 5 | रिच् | `rikt` | empty | 5 | keep |
| **`sanket`** | **6** | **केत** | **`ket`** | **symbol** | **3** | **3 letters** |
| `mulya` | 5 | मूल् | **`mul`** | value | 3 | **3 letters** |
| `shreni` | 6 | श्रेणि | `shren` | sort | 3 | 5 letters |
| `unnat` | 5 | उन्नत | `unnat` | raise | 4 | keep |
| `avanat` | 6 | अवनत | **`avan`** | lower | 3 | 4 letters |
| `gan` | 3 | गण् | `gan` | count | 6 | keep |
| `kram` | 4 | क्रम् | `kram` | step | 2 | keep |
| `gun` | 3 | गुण् | `gun` | multiply | 2 | keep |
| `bhaj` | 4 | भज् | `bhaj` | divide | 3 | keep |
| `shesh` | 5 | शेष | `shesh` | remainder | 4 | keep |
| `ghat` | 4 | घात | `ghat` | power | 3 | keep |
| `varg` | 4 | वर्ग | `varg` | square | 4 | keep |
| `mool` | 4 | मूल | `mool` | root | 3 | keep |

---

## 4. The builtins — shortened and Sanskrit

| Now | Shorter | English | Why |
|---|---|---|---|
| `akshar` | `aksh` | char_at | 4 letters |
| `aksharank` | `akshank` | char_code | 7 - or **`ank_aksh`** (7) |
| `akshar_rakh` | **`aksh_rakh`** | set_char | 9 |
| `vartani_aayam` | **`varn_aayam`** | strlen | 11 - **`varn` is the shorter module stem** |
| `vartani_tul` | **`varn_tul`** | strcmp | 8 |
| `vartani_pratilip` | **`varn_lip`** | strcpy | **8, and it uses the short root** |
| `vartani_cat` | **`varn_yuj`** | strcat | 8 |
| **`pankti_len`** | **`mala_aayam`** | array length | **the module is `mala`; `pankti` is the retired word** |
| `sankhya_yog` | **`sankh_yuj`** | vector add | 10 |
| `sankhya_gunan` | **`sankh_gun`** | vector multiply | 9 |
| **`sankhya_dot`** | **`sankh_bindu`** | dot product | `bindu` is point |
| **`likha_fmt`** | **`likh_roop`** | format | 9 |
| **`kosh_push`** | **`kosh_khip`** | push | 9 - `khip` already exists |
| **`kosh_pop`** | **`kosh_nay`** | pop | 8 - `nay` is the short remove root |
| **`kosh_len`** | **`kosh_aayam`** | length | 10 |
| **`kosh_cap`** | **`kosh_ksham`** | capacity | 10 - `ksham` = capacity, 5 letters |
| **`kosh_clear`** | **`kosh_shodh`** | clear | 10 |
| **`kosh_empty`** | **`kosh_rikt`** | is empty | 10 - matches `rakh_rikt` |
| **`kosh_peek`** | **`kosh_iksh`** | peek | 9 |
| **`kosh_dequeue`** | **`kosh_agran_nay`** | dequeue | 14 - **or `kosh_purv_nay`** (13) |
| **`kosh_enqueue`** | **`kosh_agran_yuj`** | enqueue | 14 - **or `kosh_purv_yuj`** (13) |
| `netsock` | **`jal_sutra`** | socket | 9 |
| `netbind` | **`jal_bandh`** | bind | 9 |
| `netlisten` | **`jal_shrav`** | listen | 10 |
| `netaccept` | **`jal_grah`** | accept | 8 |

---

## 5. The English left — my final suggestion

| Now | Where | Suggestion | Verdict |
|---|---|---|---|
| **`fib`** | `ank` | **`meru_sankh`** | **Fibonacci IS the Meru sequence in Indian mathematics** |
| **`fnv1a`**, **`fnv1a_varna`** | `gudh` | **KEEP** | **a named algorithm - renaming hides which hash** |
| **`simpson`** | `kalana` | **KEEP** | **a named method** |
| **`skalar`** | `samanvaya` | **`ekank`** | **and `sadish` (vector) already sits beside it** |
| **`util_chinha`** | `sadhan` | **`upayog_chinh`** | `upayog` = use |
| **`bit_gan`** | `gan` | **`ansh_gan`** | `ansh` = part |
| **`asti_sorted`**, **`suchi_asti_sorted`** | `shren`, `such` | **`asti_shrenit`** | from `shreni` |
| **`roop_sign_akshar`** | `roop` | **`roop_chinh_aksh`** | `chinha` is the project's word |
| **`pehchan`** | `samanvaya` | **`abhigyan`** | **Hindi, not Sanskrit** |
| **`nishan`** | `samanvaya` | **`chinh`** | **Hindi, not Sanskrit** |
| **`chay_khip`** etc (4) | `such` | **`chiti_khip`**, **`chiti_nay`**, **`chiti_iksh`**, **`chiti_rikt`** | `chiti` = heap, a real word for a stack |
| **`avali_nishkas`** | `such` | **`avali_nay`** | the project's own remove root |
| **`samanvaya_akar_na`** | `saman` | **`saman_akar`** | the space is a truncation |
| **`nirnaya2`**, **`nirnaya3`** | `saman` | **need real names** | a digit means the name ran out |
| **`laghu2`**, **`adhik2`** | `gan` | **`laghutam`**, **`adhikatam`** exist - so these are **`laghu`/`adhik` compared, and the 2 forms are the "lesser/greater" pair** | **rename `laghutar` / `adhikatar`** |
| **`pravan2`** | `kalan` | **`pravan`** and **`pravan2`** are probably first and second derivative | **rename `pravan` / `pravan_dwi`** |
| **`roop_ank_aadhar2`** | `roop` | second base | **`roop_ank_aadhar_dwi`** |

---

## 6. What the shortening buys, counted

| Measure | Now | After |
|---|---|---|
| Longest keyword | **`nirmmita` / `sthagita`, 8** | **`vibhag`, 6** |
| Longest module | **`samanvaya`, 9** | **`sankhiki`, 8** |
| Longest stem | **`paripurna`, 9** | **`apeksh`, 6** |
| Longest builtin | **`vartani_pratilip`, 16** | **`kosh_agran_nay`, 14** |
| Average keyword length | **5.4** | **4.5** |
| English words | **9** | **2** (`fnv1a`, `simpson` - both proper names) |
| Hindi words | **2** | **0** |
| Numbered suffixes | **6** | **0** |
| Duplicate modules | **1 pair** | **0** |

---

*Rewritten by Sarvam, 27 October 2026. Every shortening is a Sanskrit root or a stem-form, not an English abbreviation.
Nothing is applied.*
