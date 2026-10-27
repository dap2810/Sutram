# Every word in the language — Sanskrit, English, and what I would change

**Four tables: the keywords, the builtins, the module names, and the recurring stems inside function names.**
**Every entry has what it does and my suggestion.** **Nothing here is applied; this is the page to go through.**

---

## 1. The 38 keywords

| # | Sanskrit | Devanagari | English | What it does | My suggestion |
|---|---|---|---|---|---|
| 1 | `mukhya` | मुख्य | main | the entry point | **keep** - 6 letters, and `main` is a C habit anyway |
| 2 | `vitti` | वित्ति | var | declares a variable | **keep** - 5 letters, used everywhere |
| 3 | `anka` | अङ्क | int | the integer type | **keep** - 4 letters |
| 4 | `dasham` | दशम | float | the 64-bit float type | **keep** - "tenth" for a decimal |
| 5 | `sankhya` | सङ्ख्या | number | generic numeric | **keep** - but it is 7 letters and rarely typed |
| 6 | `yadi` | यदि | if | condition | **keep** - 4 letters |
| 7 | `anya` | अन्यत्र | else | the alternative | **consider `any`** - `anya` is 4, `any` is 3 and reads as else. **But `anya` is correct Sanskrit for "other"** |
| 8 | `yavat` | यावत् | while | loop while true | **keep** - 5 letters, and "as long as" is the right sense |
| 9 | `chakra` | पुनरावर्तन | for | counted loop | **keep** - the Devanagari says `punaravartana` (repetition) but the Latin is `chakra` (wheel). **That mismatch should be fixed: one word, both scripts** |
| 10 | `kuru` | कुरु | do | do-while | **keep** |
| 11 | `prati` | प्रतियाति | return | returns a value | **keep** - 5 letters, and it is the one that made `pratilip` possible |
| 12 | `prakriya` | प्रक्रिया | function | declares a function | **keep** - 7 letters, but it is the most important word in the language |
| 13 | `likha` | लिख | print | prints a value | **keep** - 5 letters |
| 14 | `likh` | लेख | write | raw write | **consider merging with `likha`** - two words one letter apart for print vs write is a trap |
| 15 | `pad` | पाठ | read | raw read | **keep** - 3 letters |
| 16 | `grahan` | ग्रहण | input | read from the user | **keep** - but `pad` and `grahan` both read. **Document the difference in one line** |
| 17 | `purna` | पूर्ण | true | boolean true | **keep** - "full, complete" |
| 18 | `shunya` | शून्य | false | boolean false | **keep** - "zero, void" |
| 19 | `sutra` | सूत्र | const | constant | **keep** - and it is the language's own name |
| 20 | `krama` | क्रम | break | leaves a loop | **keep** |
| 21 | `agrim` | उद्देश्य | continue | next iteration | **keep** - but the Devanagari says `uddeshya` (purpose) and the Latin says `agrim` (next). **Fix the mismatch** |
| 22 | `guna` | गुण | switch | selects on a value | **keep** - "quality, attribute" |
| 23 | `bhavana` | भावना | case | a switch arm | **keep** |
| 24 | `mala` | पङ्क्ति | array | fixed array | **keep** - `mala` means "row, garland", and it was chosen over `pankti` |
| 25 | `kosh` | कोश | vector | growable array | **keep** - "treasury, sheath" |
| 26 | `vibhag` | विभाग | slice | a view into an array | **keep** |
| 27 | `ganana` | सृजन | enum | enumerated type | **consider `ganana` → `sankhya`?** No - `sankhya` is taken. **`ganana` means "counting", which is right for an enum** |
| 28 | `abhava` | निषेध | not | logical negation | **keep** - "absence" |
| 29 | `rachana` | रचना | struct | a record type | **keep** - "construction, arrangement" |
| 30 | `yoj` | आयोजन | include | pulls in a module | **keep** - 3 letters, used constantly |
| 31 | `satya` | परिग्रह | bool | the boolean type | **consider `satya` → keep**; the Devanagari says `parigraha` (grasping). **Fix the mismatch** |
| 32 | `tak` | पर्यन्त | to | a range's end | **keep** - 3 letters |
| 33 | `shabda` | शब्द | print string | prints a string variable | **consider merging with `likha`** - three print words is too many |
| 34 | `yantra` | निष्क्रिय | asm | inline assembly | **keep** - "instrument, machine" |
| 35 | `siddhi` | सिद्धि | success | the ok result | **keep** |
| 36 | `dosh` | दोष | error | the error result | **keep** - "fault, defect" |
| 37 | `prasar` | प्रसार | propagate | passes the error up | **keep** |
| 38 | `nirmmita` | निर्मित | alloc | allocates memory | **keep** |
| 39 | `sthagita` | स्थगित | pause | sleeps | **keep** |
| 40 | `dvaram` | द्वारम् | open | opens a file | **keep** |
| 41 | `band` | बन्ध | close | closes a file | **keep** - 4 letters |
| 42 | `paadh` | पाठ | ? | **appears twice with `pad`** - check | **investigate: `pad` and `paadh` both exist** |

---

## 2. The builtins (compiler-level, not library)

| Sanskrit | English equivalent | Note | My suggestion |
|---|---|---|---|
| `akshar` | char_at | character at an index | **keep** |
| `aksharank` | char_code | the code of a character | **keep** |
| `akshar_rakh` | set_char | writes a character | **keep** |
| `vartani_aayam` | strlen | length of a string | **keep** - was `vartani_len` |
| `vartani_tul` | strcmp | compares strings | **keep** - was `vartani_cmp` |
| `vartani_pratilip` | strcpy | copies a string | **keep** - was `vartani_cp` |
| `vartani_cat` | strcat | joins strings | **consider `vartani_yuj`** - `cat` is English |
| **`pankti_len`** | array length | the digit-array length | **rename `pankti_aayam`** - the last English word in a keyword |
| `sankhya_yog` | vector add | | **keep** |
| `sankhya_gunan` | vector multiply | | **keep** |
| `sankhya_dot` | **dot product** | **`dot` is English** | **rename `sankhya_bindu`** - `bindu` is the Sanskrit for point |
| `likha_fmt` | **format** | **`fmt` is English** | **rename `likha_roop`** - `roop` is the project's formatting word |
| `kosh_push` | push | | **rename `kosh_khip`** - `khip` already exists in `suchi_khip` |
| `kosh_pop` | pop | | **rename `kosh_apanay`** - `apanay` already exists in `chay_apanay` |
| `kosh_len` | length | | **rename `kosh_aayam`** |
| `kosh_cap` | capacity | | **rename `kosh_dharita`?** - ChatGPT rejected `dharita`. **Better: `kosh_kshamata`** |
| `kosh_clear` | clear | | **rename `kosh_shodh`** |
| `kosh_empty` | is empty | | **rename `kosh_rikt`** - matches `rakh_rikta`, `suchi_rikta` |
| `kosh_peek` | peek | | **rename `kosh_iksh`** |
| `kosh_dequeue` | dequeue | | **rename `kosh_agran_apanay`?** or **`kosh_purva_apanay`** |
| `kosh_enqueue` | enqueue | | **rename `kosh_agran_yuj`?** or **`kosh_purva_yuj`** |
| `netsock`, `netbind`, `netlisten`, `netaccept` | networking | **all four are English** | **rename `jal_sutra`, `jal_bandh`, `jal_shravan`, `jal_grahan`?** - needs a decision |

---

## 3. The 24 module names

| Module | Sanskrit sense | My suggestion |
|---|---|---|
| `ganita` | mathematics (checked) | **see the problem below** |
| `ganit` | mathematics (plain) | **see the problem below** |
| `suchi` | list | keep |
| `varna` | character, letter | keep |
| `roop` | form | keep |
| `khand` | piece, bit | keep - "fragment" for bit operations |
| `nighantu` | glossary | keep - it is the word for a dictionary |
| `sankhyiki` | statistics | keep |
| `phal` | fruit, result | keep |
| `shreni` | row, rank | keep |
| `sangrah` | collection | keep |
| `brihat` | great | keep |
| `samanvaya` | coordination | keep |
| `ank` | digit, number | keep |
| `mala` | row, garland | keep |
| `sadhan` | instrument | keep |
| `kalana` | calculation | keep |
| `chandas` | metre | keep |
| `vakyank` | sentence-number | keep - base conversion |
| `anukram` | sequence | keep |
| `madhava` | (the Kerala mathematician) | keep - a historical name |
| `patra` | leaf, page | keep - files |
| `aadhar` | base, support | keep |
| `gudh` | hidden | keep - hashing |

**The problem: `ganita` and `ganit` are the same word, one letter apart, for two different families.**
**My suggestion: rename `ganit` to `ganan` (counting) or `sankhya`-something, OR merge them and keep `ganita` only.**
**This is the single most important naming fix in the project.**

---

## 4. The recurring stems inside function names

**These are the words a learner must know to read any name.** **Sorted by how often they appear.**

| Stem | Meaning | Appears in | My suggestion |
|---|---|---|---|
| `asti` | is / exists (predicate) | `asti_yugm`, `asti_visham`, `asti_sampurna`, `asti_sorted`, `asti_abhajya` | **keep** - it marks every boolean-returning function, which is a real convention |
| `srij` | create | `suchi_srij`, `avali_srij`, `rakh_srij`, `nighantu_srij` | **keep** |
| `khip` | insert, throw in | `suchi_khip`, `chay_khip`, `nighantu_khip`, `anukram_khip_*` | **keep** - and it is why `kosh_khip` beats `kosh_push` |
| `apanay` | remove, take away | `suchi_apanay`, `chay_apanay`, `rakh_apanay`, `nighantu_apanay` | **keep** - and it is why `kosh_apanay` beats `kosh_pop` |
| `grah` | take, receive | `suchi_grah`, `mala_grah`, `nighantu_grah`, `anukram_grah_*` | **keep** |
| `maap` | measure | `suchi_maap`, `rakh_maap`, `nighantu_maap`, `khand_maap`, `varna_maap`, `avali_maap`, `anukram_maap_ashtak` | **keep** - it is the length convention |
| `rikta` | empty | `suchi_rikta`, `chay_rikta`, `rakh_rikta`, `avali_rikta`, `nighantu_rikta` | **keep** |
| `antah` | contains | `suchi_antah`, `varna_antah`, `rakh_antah`, `nighantu_antah`, `khand_antah`, `avali_antah` | **keep** |
| `vardh` | grow | `suchi_vardh`, `rakh_vardh`, `nighantu_vardh`, `vardh` | **keep** |
| `anwesh` | search | `suchi_anwesh`, `varna_anwesh`, `khand_anwesh`, `nighantu_anwesh`, `anwesh_sarak` | **keep** |
| `yuj` | join, add | `varna_yuj`, `rakh_yuj`, `khand_yuj`, `brihat_yuj` | **keep** |
| `tul` | weigh, compare | `varna_tul`, `khand_tul`, `brihat_tul` | **keep** - and it is why `vartani_tul` beats `vartani_cmp` |
| `pratilip` | copy | `mala_pratilip`, `khand_pratilip`, `brihat_pratilip` | **keep** |
| `bhed` | split, differ | `varna_bhed`, `rakh_bhed`, `khand_bhed` | **keep** |
| `viparyay` | reverse | `varna_viparyay`, `suchi_viparyay`, `khand_viparyay`, `viparyay_ank`, `viparyay_mala` | **keep** |
| `gan` | count, group | `varna_gan`, `suchi_gan`, `khand_gan`, `ank_gan`, `gan_swar`, `gan_akshar` | **keep** |
| `unnat` | raise, upper | `varna_unnat`, `khand_unnat`, `asti_unnat_akshar`, `roop_shodash_unnat` | **keep** |
| `avanat` | lower | `varna_avanat`, `khand_avanat`, `asti_avanat_akshar` | **keep** |
| `sanket` | symbol, signal | `akshar_sanket`, `unnat_sanket`, `avanat_sanket` | **keep** |
| `mulya` | value | `phal_mulya`, `nighantu_mulya`, `nirapeksh_mulya` | **keep** |
| `janchit` | checked | `ganita_janchit_*`, `phal_janchit_*` | **keep** - the checked-arithmetic marker |
| `paripurna` | complete, saturating | `ganita_paripurna_*` | **keep** - the saturating marker |
| `nirapeksh` | independent, absolute | `ganita_janchit_nirapeksh`, `nirapeksh_mulya` | **keep** |
| `shreni` | row, sort | `suchi_shreni`, `budbud_shreni`, `mil_shreni` | **keep** |
| `kunjika` | key | `nighantu_kunjika`, `nighantu_kunjika_ashtak` | **keep** |
| `kunji` | key (variant) | `nighantu_kunji_gudh`, `nighantu_kunji_sam` | **`kunji` and `kunjika` are two forms of one word. Pick one** |
| `koshtha` | cell, compartment | `nighantu_koshtha_likh` | **keep** |
| `surakshit` | safe, guarded | `mala_sangrah_surakshit`, `mala_grah_surakshit` | **keep** |
| `seemit` / `seema` | bounded, limit | `seemit`, `yog_seema` | **`seemit` and `seema` are two forms. Pick one** |
| `laghu` | light, small | `laghu`, `laghuttam`, `suchi_laghu`, `shreni_laghu`, `brihat_*_laghu` | **keep** - and it is the word I proposed for the int type |
| `adhik` | more, greater | `adhik`, `adhikatama`, `suchi_adhik`, `ank_adhik` | **keep** |

---

## 5. The English that is left, and my suggestion

| Name | Where | My suggestion |
|---|---|---|
| **`fib`** | `ank` | **rename `anukram_sankhya`** (sequence number) or **`meru_sankhya`** - Fibonacci is the Meru sequence in Indian mathematics |
| **`fnv1a`, `fnv1a_varna`** | `gudh` | **KEEP** - FNV-1a is a named algorithm; renaming it would hide which hash it is |
| **`simpson`** | `kalana` | **KEEP** - a named method. `simpson` in the docs, and the Sanskrit name would not identify it |
| **`skalar`** | `samanvaya` | **rename `ekank`** (single number) - and `sadish` (vector) already exists beside it, so `ekank`/`sadish` is a real pair |
| **`util_chinha`** | `sadhan` | **rename `upayog_chinha`** - `upayog` is "use", which is what util means |
| **`bit_gan`** | `ganit` | **rename `ansh_gan`** - `ansh` is "part", which is what a bit is |
| **`asti_sorted`**, **`suchi_asti_sorted`** | `shreni`, `suchi` | **rename `asti_shrenit`** - `shrenit` is "arranged, sorted", from `shreni` |
| **`roop_sign_akshar`** | `roop` | **rename `roop_chinha_akshar`** - `chinha` is the project's own word for sign |
| **`pehchan`** | `samanvaya` | **rename `abhigyan`** - "recognition" in Sanskrit; `pehchan` is Hindi |
| **`nishan`** | `samanvaya` | **rename `chinha`** - the project already uses `chinha` for sign |
| **`chay_khip`, `chay_apanay`, `chay_avalok`, `chay_rikta`** | `suchi` | **`chay` is not a standard stem. If it means "stack", rename to `chiti_*`** (heap) - `chiti` is a real word and reads as a stack |
| **`avali_nishkas`** | `suchi` | **rename `avali_apanay`** - the project's own word for remove |
| **`samanvaya_akar_na`** | `samanvaya` | **the space looks like a truncation. Check what it was meant to be** |
| **`nirnaya2`, `nirnaya3`, `laghu2`, `adhik2`, `pravan2`, `roop_ank_aadhar2`** | 4 modules | **each needs a real second name.** **A digit means the name ran out** |
| **`kosh_push` etc. (9)** | builtins | **see table 2** - use the project's own `khip`/`apanay` |
| **`netsock`, `netbind`, `netlisten`, `netaccept`** | builtins | **all four English. `jala` (net) is the Sanskrit stem: `jala_sutra`, `jala_bandh`, `jala_shravan`, `jala_grahan`** |

---

## What I would do, in order

1. **`ganita` vs `ganit`** - the one that will actually confuse a learner
2. **`kosh_push` → `kosh_khip`, `kosh_pop` → `kosh_apanay`** - free wins, the words already exist
3. **`pankti_len` → `pankti_aayam`** - the last English word in a keyword
4. **`pehchan` → `abhigyan`, `nishan` → `chinha`, `skalar` → `ekank`** - three words that are not even Sanskrit
5. **The five numbered suffixes** - each needs a name
6. **`chay_*` → `chiti_*`** - if it is a stack
7. **The networking four** - needs a decision on the `jala` stem
8. **`fib`** - the last abbreviation a user types

---

*Built by Sarvam, 27 October 2026, from `lib/*.smlib`, `src/sutram_compiler.asm` and `lang/sanskrit.lang` on main at
compiler v253. Every name was read from a declaration. Nothing is renamed.*
