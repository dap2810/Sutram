# Sutram ROUND-117 WS2 — the actual beginner teaching order, one clear reason and one verified current callable each

**Read main pinned at** `fd02405aad986001c451ee5c5decb91346c7bb53` (compiler v248; 27 October 2026). **Language priority:** Sanskrit only until v1.0; ten other packs frozen. This order is a **curriculum recommendation**, not a compiler feature or a universal name-generation grammar.

**Before the first function:** show `mukhya`, `vitti`, `prakriya`, `likha`, and `yoj`; explain that builtin symbols, keywords, native types (`kosh`) and callable functions in `lib/*.smlib` are different categories. Do not invent `lib/kosh.smlib` or `lib/akshar.smlib`.

## Eight introductory lessons, with REAL current source signatures

| Order | Topic / first-token family | Measured global names | Verified callable in current source and exact source location | One-line reason |
|---:|---|---:|---|---|
| **1** | Fixed raw qword buffers — `mala_*` | **8** | `mala_grah(arr, i)`, `lib/mala.smlib:28` | Learn memory address, cell index and the fact that caller-managed allocation and length are distinct. |
| **2** | Lists — `suchi_*` | **21** | `suchi_khip(l, v)`, `lib/suchi.smlib:87` | Contrast automatic list growth and logical length with manually managed raw buffers. |
| **3** | Explicit-length byte strings — `khand_*` | **22** | `khand_anwesh(hay, hn, needle, nn)`, `lib/khand.smlib:104` | Teach why byte lengths and packed representations matter for safe string searches. |
| **4** | Character/cell helpers — `varna_*` | **18** | `varna_anwesh(hay, hn, needle, nn)`, `lib/varna.smlib:140` | Compare qword-cell character sequences with packed bytes, so callers don't mix representations. |
| **5** | Checked arithmetic — `ganita_*` | **18** | `ganita_janchit_yuj(a, b, ok)`, `lib/ganita.smlib:216` | Introduce explicit success flags and distinguish checked from `paripurna` saturating operations. |
| **6** | Formatting — `roop_*` | **23** | `roop_dash(v, out)`, `lib/roop.smlib:212` | Show conversions into caller-provided byte output buffers with an explicit format contract. |
| **7** | Maps — `nighantu_*` | **17** | `nighantu_grah(m, cap, key, keyn)`, `lib/nighantu.smlib:159` | Practice keyed lookup, byte-string keys, capacity and absent-value sentinel ambiguity. |
| **8** | Explicit Result values — `phal_*` | **14** | `phal_siddhi(out, v)`, `lib/phal.smlib:33` | Gather result status and value in one caller-owned 2-cell object instead of relying only on an error sentinel. |

**Eight measured prefixes collectively cover 141/305 real functions**, with a learner-oriented order rather than frequency order. The counts come from the full all-305 source inventory of R114, corroborated by current direct source reads. `varna_*` is a *cross-module first-token count* of 18, of which 15 declarations are in `lib/varna.smlib`; the teaching example is verified in that module. Do not misinterpret every same-prefix function as a member of the same import.

## Next: teach the five notable families that do NOT mirror module filenames

| Second-stage token | Measured first-token frequency | What a learner should remember |
|---|---:|---|
| `brihat_*` | 15 | Big integer functionality; 13 in `lib/brihat.smlib`, two in `lib/aadhar.smlib` |
| `rakh_*` | 14 | Set family defined inside `lib/sangrah.smlib` |
| `asti_*` | 13 | Predicate-like naming convention found in multiple modules |
| `avali_*` | 9 | Queue family inside `lib/suchi.smlib` |
| `chay_*` | 4 | Stack family inside `lib/suchi.smlib` |

## Suffixes to teach by learning utility, with actual measured frequency

**Frequency denominator:** 260 names containing an underscore (the other 45 have no "suffix" in this sense). These are the final underscore-delimited components, not all tokens anywhere in a name.

| Beginner sequence | Ending | Count | Real example |
|---:|---|---:|---|
| 1 | `srij` | **4** | `suchi_srij` — create |
| 2 | `khip` | **3** | `suchi_khip` — insert/push |
| 3 | `grah` | **3** | `mala_grah` — retrieve |
| 4 | `maap` | **6** | `suchi_maap` — measure/length |
| 5 | `gan` | **6** | `suchi_gan` — count occurrences |
| 6 | `anwesh` | **6** | `khand_anwesh` — search |
| 7 | `antah` | **6** | `nighantu_antah` — contains |
| 8 | `rikta` | **5** | `suchi_rikta` — empty/clear |
| 9 | `apanay` | **4** | `suchi_apanay` — remove |
| 10 | `yuj` | **7** | `ganita_janchit_yuj` — join/add |
| 11 | `gun` | **4** | `ganita_janchit_gun` — multiply |
| 12 | `nyun` | **4** | `ganita_janchit_nyun` — subtract |

**Not every last component is a verb**: `akshar` (10), `ank` (7), `shreni` (5) often name objects, representations, or action families. Even familiar prefixes/suffixes **do not authorize constructing a name that source doesn't declare**; use the complete `docs/sutram-stdlib.html` index to look up only real callables, and regenerate it from current source to synchronize descriptions.

## Evidence and limits

- Counts: `ChatGPT-to-Sarvam/ROUND-114-WS1-MEASURED-PREFIXES.json`, source names Parts A/B; current module+example signature lookups were made on pin `fd02405...`.
- Eight lesson examples were independently located in live `lib/` by actual `prakriya` declaration and line, **not synthesized from word-parts**.
- These examples were **NOT compiled or executed** by ChatGPT: **NOT RUN - no toolchain**. "Verified example" here means **verified actual callable name and declaration**, not tested stdout or runtime properties.
- Claims of formal Sanskrit derivation require a Sanskritist; underscore-word patterns are pedagogical conveniences, not Pāṇinian samāsa.
