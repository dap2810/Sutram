> **Status at v405 — the return keyword is decided.** **`nivartanam` (निवर्तनम्, `ni` + `vṛt`) is the keyword; `prati` is kept as a legacy alias so no existing program stops compiling.** Applied across 162 files in R53/R54 with **zero goldens changed**.
>
> **Two corrections to the table below, both from measuring rather than reading:** **`chay` IS real Sanskrit (चय, heap)** — the `chiti_*` rename I proposed is churn and should not happen. **`kosh_enqueue` must not become `kosh_purva_yuj`** — enqueue appends at the REAR, and `purva` means front.
>
> **And the Devanagari column was ahead of the Latin column:** the pack already held proper Sanskrit compounds for ten builtins (`kosh_push` -> कोशपुष्, `kosh_cap` -> कोशक्षमता, `kosh_empty` -> कोशरिक्त). **The answer to "what should these be called" was already in the tree.** See `docs/reports/LANG-PACK-AUDIT.md`.

# The complete word table — with the English meaning, and what I would change

## The principle I got wrong last time

**I shortened words into fragments.** **`paripurna` -> `purn` loses `pari` (around, complete).** **`viparyay` -> `vip`
is not a word.** **`apanay` -> `nay` means "to lead", not "to remove".** **`mukhya` -> `mukh` means "face".**

**So the rule is: a name must be a COMPLETE Sanskrit word, or a compound of complete words.** **Never a fragment.** **A
word that is short because it lost half its meaning is worse than a long word that means what it says.**

**Which means: most of the 305 names are already right, and the problems are specific.**

---

## 1. The 38 keywords — with English, and a verdict

| # | Sanskrit | Devanagari | English | Letters | Verdict |
|---|---|---|---|---|---|
| 1 | `mukhya` | मुख्य | main | 6 | **KEEP** - `mukh` means "face", not "main". **The word is right.** |
| 2 | `vitti` | वित्ति | var | 5 | **KEEP** - `vitt` means "wealth" |
| 3 | `anka` | अङ्क | int | 4 | **KEEP** - already short, and it is a real word for "digit" |
| 4 | `dasham` | दशम | float | 6 | **KEEP** - `dash` means "ten"; `dasham` means "tenth", which is a decimal |
| 5 | `sankhya` | सङ्ख्या | number | 7 | **KEEP** - `sankh` means "conch" |
| 6 | `yadi` | यदि | if | 4 | **KEEP** |
| 7 | `anya` | अन्यत्र | else | 4 | **KEEP** - but **the Devanagari `anyatra` means "elsewhere"; the Latin `anya` means "other".** **Fix: use `anya` in both scripts** |
| 8 | `yavat` | यावत् | while | 5 | **KEEP** - "as long as", exactly right |
| 9 | `chakra` | **पुनरावर्तन** | for | 6 | **KEEP the Latin; FIX the Devanagari.** **`punaravartana` is 13 letters and means "repetition"; `chakra` (wheel) is the loop.** **One word, both scripts** |
| 10 | `kuru` | कुरु | do | 4 | **KEEP** - imperative of "do", exact |
| 11 | `prati` | प्रतियाति | return | 5 | **KEEP** - but **Devanagari `pratiyati` is "goes towards"; `prati` alone is "towards/back".** **Fix: `prati` in both** |
| 12 | `prakriya` | प्रक्रिया | function | 8 | **KEEP** - **8 letters, but it is a complete word and it is the most important one.** **`kriya` alone means "action" and loses `pra-` (forth).** **I was wrong to shorten it** |
| 13 | `likha` | लिख | print | 5 | **KEEP** |
| 14 | `likh` | लेख | write | 4 | **CHANGE: merge into `likha`.** **Two words one letter apart, for print vs raw write, is a trap.** **One word for "write"; raw write can be a separate builtin if needed** |
| 15 | `pad` | पाठ | read | 3 | **KEEP** |
| 16 | `grahan` | ग्रहण | input | 6 | **KEEP** - `grahan` is "receiving", `pad` is "reading". **Two different things, two words** |
| 17 | `purna` | पूर्ण | true | 5 | **KEEP** - "full, complete" |
| 18 | `shunya` | शून्य | false | 6 | **KEEP** - "zero, void" |
| 19 | `sutra` | सूत्र | const | 5 | **KEEP** - and it is the language's name |
| 20 | `krama` | क्रम | break | 5 | **KEEP** - "step, order"; breaking is leaving the order |
| 21 | `agrim` | **उद्देश्य** | continue | 5 | **KEEP the Latin; FIX the Devanagari.** **`uddeshya` means "purpose"; `agrim` means "next".** **`agrim` is the right sense** |
| 22 | `guna` | गुण | switch | 4 | **KEEP** - "quality, attribute"; a switch selects on one |
| 23 | `bhavana` | भावना | case | 7 | **KEEP** - "bringing into being" |
| 24 | `mala` | पङ्क्ति | array | 4 | **KEEP the Latin; FIX the Devanagari.** **`pankti` was the retired word; `mala` (row, garland) replaced it. The Devanagari still says `pankti`** |
| 25 | `kosh` | कोश | vector | 4 | **KEEP** - "treasury, sheath" |
| 26 | `vibhag` | विभाग | slice | 6 | **KEEP** - "division", exact for a slice |
| 27 | `ganana` | सृजन | enum | 6 | **KEEP the Latin; FIX the Devanagari.** **`srijan` means "creation"; `ganana` means "counting".** **An enum is a counted set - `ganana` is right** |
| 28 | `abhava` | निषेध | not | 6 | **KEEP the Latin; FIX the Devanagari.** **`nishedh` is "prohibition"; `abhava` is "absence", which is what negation is** |
| 29 | `rachana` | रचना | struct | 7 | **KEEP** - "construction, arrangement" |
| 30 | `yoj` | आयोजन | include | 3 | **KEEP** - and 3 letters |
| 31 | `satya` | **परिग्रह** | bool | 5 | **KEEP the Latin; FIX the Devanagari.** **`parigraha` means "grasping"; `satya` is "truth"** |
| 32 | `tak` | पर्यन्त | to | 3 | **KEEP the Latin; FIX the Devanagari.** **`paryanta` is 8 letters; `tak` is 3 and means "until"** |
| 33 | `shabda` | शब्द | print string | 6 | **CHANGE: merge into `likha`.** **Three print words is two too many** |
| 34 | `yantra` | **निष्क्रिय** | asm | 6 | **KEEP the Latin; FIX the Devanagari.** **`nishkriya` means "inactive"; `yantra` means "machine".** **Inline assembly is a machine, not inactivity** |
| 35 | `siddhi` | सिद्धि | success | 6 | **KEEP** - "accomplishment" |
| 36 | `dosh` | दोष | error | 4 | **KEEP** - "fault, defect" |
| 37 | `prasar` | प्रसार | propagate | 6 | **KEEP** - "spreading", exact for propagating an error |
| 38 | `nirmmita` | निर्मित | alloc | 8 | **KEEP** - **8 letters, but `nirm` is not a word and `nirmiti` (creation) is the same length.** **The word is right** |
| 39 | `sthagita` | स्थगित | pause | 8 | **KEEP** - "postponed, stopped", exact |
| 40 | `dvaram` | द्वारम् | open | 6 | **KEEP** - "door"; opening a file is opening a door |
| 41 | `band` | बन्ध | close | 4 | **KEEP** - "bond, close" |
| 42 | **`paadh`** | पाठ | ? | 5 | **REMOVE** - it duplicates `pad` |

**So: 3 keywords change (`likh`, `shabda`, `paadh`), 8 Devanagari rows need fixing, and 31 are already right.**

---

## 2. The Devanagari mismatches — 8 rows

**These are the real defect: the Latin name and the Devanagari name are different words.**

| Latin (used) | Devanagari (in `lang/sanskrit.lang`) | Fix |
|---|---|---|
| `anya` | अन्यत्र `anyatra` | **अन्य `anya`** |
| `chakra` | पुनरावर्तन `punaravartana` | **चक्र `chakra`** |
| `prati` | प्रतियाति `pratiyati` | **प्रति `prati`** |
| `agrim` | उद्देश्य `uddeshya` | **अग्रिम `agrim`** |
| `mala` | पङ्क्ति `pankti` | **माला `mala`** |
| `ganana` | सृजन `srijan` | **गणना `ganana`** |
| `abhava` | निषेध `nishedh` | **अभाव `abhava`** |
| `satya` | परिग्रह `parigraha` | **सत्य `satya`** |
| `tak` | पर्यन्त `paryanta` | **तक् `tak`** |
| `yantra` | निष्क्रिय `nishkriya` | **यन्त्र `yantra`** |

**10 rows.** **A programmer who writes Devanagari gets a different word from the one the Latin uses.** **That is not a
naming preference; it is two vocabularies in one language.**

---

## 3. The builtins — with English

| Sanskrit | English | Letters | Verdict |
|---|---|---|---|
| `akshar` | char_at | 6 | **KEEP** |
| `aksharank` | char_code | 9 | **KEEP** - `akshar` + `ank` = character-number, a real compound |
| `akshar_rakh` | set_char | 11 | **KEEP** - `rakh` is "place", and `rakh_*` is the set-module prefix |
| `vartani_aayam` | strlen | 14 | **KEEP** - `vartani` (string) + `aayam` (extent) |
| `vartani_tul` | strcmp | 11 | **KEEP** |
| `vartani_pratilip` | strcpy | 16 | **KEEP** - `pratilip` is "a copy", and it was the word the lexer question was about |
| `vartani_cat` | strcat | 11 | **CHANGE: `vartani_yuj`** - `cat` is English, `yuj` is "join" and already a stem |
| `pankti_len` | array length | 10 | **CHANGE: `mala_aayam`** - **`pankti` is the retired word and `len` is English** |
| `sankhya_yog` | vector add | 11 | **KEEP** - `yog` is "union" |
| `sankhya_gunan` | vector multiply | 13 | **KEEP** - `gunan` is "multiplication" |
| `sankhya_dot` | dot product | 11 | **CHANGE: `sankhya_bindu`** - `bindu` is "point" |
| `likha_fmt` | format | 9 | **CHANGE: `likha_roop`** - `roop` is the project's formatting word |
| `kosh_push` | push | 9 | **CHANGE: `kosh_khip`** - **`khip` already exists in `suchi_khip`, `nighantu_khip`, `anukram_khip`** |
| `kosh_pop` | pop | 8 | **CHANGE: `kosh_apanay`** - **`apanay` already exists in `chay_apanay`, `suchi_apanay`, `rakh_apanay`** |
| `kosh_len` | length | 8 | **CHANGE: `kosh_aayam`** |
| `kosh_cap` | capacity | 8 | **CHANGE: `kosh_kshamata`** - ChatGPT rejected `dharita`; `kshamata` is "capacity" |
| `kosh_clear` | clear | 10 | **CHANGE: `kosh_shodh`** - "cleansing" |
| `kosh_empty` | is empty | 10 | **CHANGE: `kosh_rikt`** - matches `rakh_rikta`, `suchi_rikta` |
| `kosh_peek` | peek | 9 | **CHANGE: `kosh_iksh`** - "to look" |
| `kosh_dequeue` | dequeue | 13 | **CHANGE: `kosh_purva_apanay`** - "remove from the front" |
| `kosh_enqueue` | enqueue | 13 | **CHANGE: `kosh_purva_yuj`** - "join at the front" |
| `netsock` | socket | 7 | **CHANGE: `jala_sutra`** - `jala` is "net"; `sutra` is "thread" |
| `netbind` | bind | 7 | **CHANGE: `jala_bandh`** - "tie the net" |
| `netlisten` | listen | 9 | **CHANGE: `jala_shravan`** - "hearing" |
| `netaccept` | accept | 9 | **CHANGE: `jala_grahan`** - "receiving" |

---

## 4. The 24 modules — with English

| Module | English | Letters | Functions | Verdict |
|---|---|---|---|---|
| **`ganita`** | mathematics, checked | 6 | 22 | **KEEP** - it is the fuller word and the larger family |
| **`ganit`** | mathematics, plain | 5 | 18 | **CHANGE - this is the real problem.** **See below** |
| `suchi` | list | 5 | 34 | **KEEP** - "list, index" |
| `varna` | character, letter | 5 | 27 | **KEEP** |
| `roop` | form | 4 | 23 | **KEEP** |
| `khand` | piece, bit | 5 | 22 | **KEEP** - "fragment", exact for bit operations |
| `nighantu` | glossary, map | 8 | 17 | **KEEP** - **8 letters, but it is the actual word for a dictionary.** **`nigh` is a fragment** |
| `sankhyiki` | statistics | 9 | 16 | **KEEP** - "the science of numbers", a real derivation |
| `phal` | fruit, result | 4 | 14 | **KEEP** |
| `shreni` | row, rank | 6 | 14 | **KEEP** - "row, series" |
| `sangrah` | collection | 7 | 14 | **KEEP** |
| `brihat` | great | 6 | 13 | **KEEP** - and it is the "big number" family |
| `samanvaya` | coordination | 9 | 11 | **KEEP** - **9 letters, but `saman` alone means "equal", which is a different word** |
| `ank` | digit, number | 3 | 10 | **KEEP** |
| `mala` | row, garland | 4 | 8 | **KEEP** |
| `sadhan` | instrument | 6 | 7 | **KEEP** |
| `kalana` | calculation | 6 | 6 | **KEEP** |
| `chandas` | metre | 7 | 6 | **KEEP** |
| `vakyank` | sentence-number | 7 | 6 | **KEEP** - base conversion of a written number |
| `anukram` | sequence | 7 | 5 | **KEEP** - **`kram` alone is the break keyword; `anukram` is "sequence"** |
| `madhava` | (the Kerala mathematician) | 7 | 5 | **KEEP** - a historical name, and it identifies the series |
| `patra` | leaf, page | 5 | 3 | **KEEP** - a file is a page |
| `aadhar` | base, support | 6 | 2 | **KEEP** |
| `gudh` | hidden | 4 | 2 | **KEEP** - hashing is hiding |

### The `ganita` / `ganit` problem — the one real fix

**Both mean "mathematics". One letter apart. `ganita` has 22 functions, `ganit` has 18.** **A learner cannot tell them
apart and a typo silently picks the wrong family.**

**My suggestion: rename the SMALLER one to a word that says what it is.** **`ganit` is the plain-arithmetic family -
`varg`, `ghan`, `ghat`, `dwigun`, `trigun`, `mahattam`, `laghuttam`.** **That is elementary arithmetic.**

**Two options:**
1. **`ganit` -> `ganan`** (counting) - a real word, 5 letters, and it distinguishes without a fragment
2. **`ganit` -> `vyavahar`** (ordinary practice) - 8 letters, but says "everyday arithmetic"

**I would take `ganan`.** **It is a real word, it is the same length, and `ganita`/`ganan` cannot be confused.**

---

## 5. The stems — with English, and a verdict

| Stem | English | Letters | Count | Verdict |
|---|---|---|---|---|
| `asti` | is (boolean marker) | 4 | 8 | **KEEP - the one convention that is already perfect** |
| `maap` | measure | 4 | 7 | **KEEP** |
| `khip` | insert | 4 | 4 | **KEEP** |
| `apanay` | remove | 6 | 4 | **KEEP - `nay` alone is "lead", not "remove"** |
| `srij` | create | 4 | 4 | **KEEP** |
| `grah` | take | 4 | 4 | **KEEP** |
| `anwesh` | search | 6 | 5 | **KEEP - `ish` alone is "seek"; `anwesh` is "search after"** |
| `viparyay` | reverse | 8 | 5 | **KEEP - `vip` is not a word** |
| `pratilip` | copy | 8 | 3 | **KEEP - `lip` alone is "smear"** |
| `janchit` | checked | 7 | 10 | **KEEP - it is a complete participle** |
| `paripurna` | saturating | 9 | 8 | **KEEP - `purn` alone is "full", but `pari-purna` is "completely full", which is the saturating sense** |
| `nirapeksh` | absolute | 9 | 4 | **KEEP - `nirapeksh` is "independent"; an absolute value is independent of sign** |
| `tul` | compare | 3 | 3 | **KEEP** |
| `yuj` | join | 3 | 4 | **KEEP** |
| `bhed` | split | 4 | 3 | **KEEP** |
| `vardh` | grow | 5 | 4 | **KEEP** |
| `antah` | contains | 5 | 6 | **KEEP - "within", exact** |
| `rikta` | empty | 5 | 5 | **KEEP** |
| `sanket` | symbol | 6 | 3 | **KEEP - `ket` alone is "banner"** |
| `mulya` | value | 5 | 3 | **KEEP** |
| `shreni` | sort | 6 | 3 | **KEEP** |
| `unnat` | raise | 5 | 4 | **KEEP** |
| `avanat` | lower | 6 | 3 | **KEEP** |
| `gan` | count | 3 | 6 | **KEEP** |
| `kram` | step | 4 | 2 | **KEEP** |
| `gun` | multiply | 3 | 2 | **KEEP** |
| `bhaj` | divide | 4 | 3 | **KEEP** |
| `shesh` | remainder | 5 | 4 | **KEEP** |
| `ghat` | power | 4 | 3 | **KEEP** |
| `varg` | square | 4 | 4 | **KEEP** |
| `mool` | root | 4 | 3 | **KEEP** |

**All 31 stems are right.** **My previous version shortened eight of them into fragments, and every one of those was a
mistake.**

**Two inconsistencies to fix, not shorten:** **`kunji` vs `kunjika`** (both "key") and **`seemit` vs `seema`** (both
"bound"). **Pick one of each.**

---

## 6. The English left — with English meaning, and a verdict

| Name | Module | English | Verdict |
|---|---|---|---|
| `fib` | `ank` | Fibonacci | **CHANGE: `meru_sankhya`** - **Fibonacci IS the Meru sequence in Indian mathematics; the name is both shorter in meaning and more accurate** |
| `fnv1a` | `gudh` | the FNV-1a hash | **KEEP** - **a published algorithm; renaming hides which hash** |
| `fnv1a_varna` | `gudh` | FNV-1a over bytes | **KEEP** - same reason |
| `simpson` | `kalana` | Simpson's rule | **KEEP** - **a published method; renaming hides which rule** |
| `skalar` | `samanvaya` | scalar | **CHANGE: `ekank`** - "single number", and `sadish` (vector) already sits beside it |
| `util_chinha` | `sadhan` | utility sign | **CHANGE: `upayog_chinha`** - `upayog` is "use" |
| `bit_gan` | `ganit` | bit count | **CHANGE: `ansh_gan`** - `ansh` is "part" |
| `asti_sorted` | `shreni` | is sorted | **CHANGE: `asti_shrenit`** - from `shreni` |
| `suchi_asti_sorted` | `suchi` | is sorted | **CHANGE: `suchi_asti_shrenit`** |
| `roop_sign_akshar` | `roop` | sign character | **CHANGE: `roop_chinha_akshar`** - `chinha` is the project's word for sign |
| `pehchan` | `samanvaya` | identity (Hindi) | **CHANGE: `abhigyan`** - "recognition" in Sanskrit; **`pehchan` is Hindi** |
| `nishan` | `samanvaya` | mark (Hindi) | **CHANGE: `chinha`** - **`nishan` is Hindi** |
| `chay_khip` | `suchi` | stack insert | **CHANGE: `chiti_khip`** - **`chay` is not a Sanskrit stem; `chiti` is "heap", which is a stack** |
| `chay_apanay` | `suchi` | stack remove | **CHANGE: `chiti_apanay`** |
| `chay_avalok` | `suchi` | stack look | **CHANGE: `chiti_avalok`** |
| `chay_rikta` | `suchi` | stack empty | **CHANGE: `chiti_rikta`** |
| `avali_nishkas` | `suchi` | row remove | **CHANGE: `avali_apanay`** - the project's own remove word |
| `samanvaya_akar_na` | `samanvaya` | matrix shape | **CHANGE: `samanvaya_akar`** - the space is a truncation |
| `nirnaya2`, `nirnaya3` | `samanvaya` | decision, 2 and 3 | **CHANGE - need real names.** **Ask what they compute** |
| `laghu2`, `adhik2` | `ganit` | less-than, greater-than | **CHANGE: `laghutar`, `adhikatar`** - the comparative forms, both real words |
| `pravan2` | `kalana` | slope, second | **CHANGE: `pravan_dwi`** - "second slope" |
| `roop_ank_aadhar2` | `roop` | second base | **CHANGE: `roop_ank_aadhar_dwi`** |

---

## 7. What actually changes, counted honestly

| Measure | Now | After |
|---|---|---|
| **Keywords changed** | - | **3** (`likh`, `shabda`, `paadh`) |
| **Devanagari rows fixed** | - | **10** |
| **Builtins renamed** | - | **15** |
| **Modules renamed** | - | **1** (`ganit` -> `ganan`) |
| **Stems changed** | - | **0** - **all 31 are right** |
| **Library names changed** | - | **22** |
| **English removed** | 9 | **2** (`fnv1a`, `simpson` - both published algorithm names) |
| **Hindi removed** | 2 | **0** |
| **Numbered suffixes removed** | 6 | **0** |
| **Duplicate modules** | 1 pair | **0** |
| **Keyword length unchanged** | - | **every keyword keeps its length except the 3 above** |

**So the honest summary: my previous version would have rewritten 200 names to save characters. This one changes 51 names,
and every change is either a defect (English, Hindi, a digit, a duplicate) or a Devanagari mismatch.**

---

*Rewritten by Sarvam, 27 October 2026. The rule: a name is a complete Sanskrit word or a compound of complete words -
never a fragment. Nothing is applied.*
