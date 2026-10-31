# The Sanskrit pack — audit, 28 October 2026

**`lang/sanskrit.lang`, 58 keyword/builtin rows, measured on `main` at v400.**

**This is the file that decides what a Devanagari program may write.** **Every row below was read from the file, not remembered.**

---

## 1. Eleven rows where the Devanagari is the WRONG WORD

**Not a spelling variant — a different word.** **A programmer who writes `चक्र` for the loop gets an error, because the pack
only accepts `पुनरावर्तन`.**

| Latin keyword | Devanagari in the pack | What that word means | Should be |
|---|---|---|---|
| **`chakra`** | **पुनरावर्तन** | *punah-avartana* — **repetition** | **चक्र** (wheel, loop) |
| **`anya`** | **अन्यत्र** | *anyatra* — **elsewhere** | **अन्य** (other) |
| **`agrim`** | **उद्देश्य** | *uddeshya* — **purpose, aim** | **अग्रिम** (next) |
| **`mala`** | **पङ्क्ति** | *pankti* — **row** — **and `pankti` is the RETIRED array word** | **माला** (garland, row) |
| **`ganana`** | **सृजन** | *srijan* — **creation** | **गणना** (counting) |
| **`yantra`** | **निष्क्रिय** | *nishkriya* — **inactive** | **यन्त्र** (machine, instrument) |
| **`satya`** | **परिग्रह** | *parigraha* — **possession, grasping** | **सत्य** (truth) |
| **`tak`** | **पर्यन्त** | *paryanta* — **limit, end** | **तक्** (until) |

**`mala` is the worst of the eight.** **The pack maps it to `पङ्क्ति`, which is the word the project deliberately retired.** **So a Devanagari programmer writing the current array keyword has to type the old one.**

## 2. Three rows that are ABBREVIATIONS, not words

**These use U+0970, the Devanagari abbreviation sign.** **An abbreviation is not a keyword a learner can read.**

| Latin | Devanagari | Note |
|---|---|---|
| **`vitti`** | **वि॰** | **an abbreviation of वित्ति** |
| **`likha`** | **लि॰** | **an abbreviation of लिख** |
| **`prakriya`** | **प्र॰** | **an abbreviation of प्रक्रिया** |

**And `vitti`, `likha` and `prakriya` each ALSO have a full Devanagari row.** **So both spellings work, which is why nobody
noticed.** **But the abbreviation rows are clutter that will confuse anyone reading the pack.**

## 3. Four Latin names appear more than once

| Latin | Times in the pack |
|---|---|
| **`likha`** | **3** |
| **`vitti`** | **2** |
| **`prakriya`** | **2** |
| **`shabda`** | **2** |

**`likha` three times is the one that matters:** **three different Devanagari spellings all map to `likha`.** **That is not
wrong — it means the pack accepts all three — but nothing in the file says which one is canonical.**

## 4. And the good news: the Devanagari side is AHEAD of the Latin side

**Ten builtins already have proper Sanskrit compounds in the pack, while their Latin names are still English-ish:**

| Latin name | Devanagari in the pack |
|---|---|
| `pankti_len` | **पङ्क्तिदैर्घ्य** |
| `kosh_push` | **कोशपुष्** |
| `kosh_pop` | **कोशपोप्** |
| `kosh_len` | **कोशदैर्घ्य** |
| `kosh_cap` | **कोशक्षमता** |
| `kosh_clear` | **कोशशुद्धि** |
| `kosh_empty` | **कोशरिक्त** |
| `kosh_peek` | **कोशशिखर** |
| `kosh_dequeue` | **कोशनिर्गम** |
| `kosh_enqueue` | **कोशप्रवेश** |

**So the Sanskrit for these already exists and was chosen deliberately.** **That is the answer to the naming debate for these
ten: the Devanagari column already says what the Latin column should say.** **`kosh_push` is `कोशपुष्`, so the Latin should be
`kosh_push` -> the word the pack already uses.**

**Note `kosh_pop` -> कोशपोप्.** **That looks like a transliteration of the English "pop" into Devanagari rather than a Sanskrit
word.** **Worth a check before it is treated as precedent.**

## What I would do, in order

1. **Fix the eight wrong words.** **`चक्र`, `अन्य`, `अग्रिम`, `माला`, `गणना`, `यन्त्र`, `सत्य`, `तक्`.** **No compiler change - the pack is data.**
2. **Delete the three abbreviation rows.** **The full spellings already exist.**
3. **Mark the canonical Devanagari for `likha` and say in a comment why the other two exist.**
4. **Fix `पङ्क्ति` in `pankti_len` too** - **it carries the retired word in its Devanagari name.**
5. **And check `कोशपोप्`** - **if it is a transliteration of the English, it is not a Sanskrit name.**

**All five are edits to one data file.** **None of them touches the compiler, and none changes what a Latin program does.**
