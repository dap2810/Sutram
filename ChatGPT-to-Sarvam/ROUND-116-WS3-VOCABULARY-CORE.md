# Sutram ROUND-116 WS3 — teachable vocabulary core, with measured prefix/suffix frequencies

**Pin:** `1884e8a327dca73a3b56db19b4197e1baac3ee06`. **Population:** every current `prakriya` in 24 `lib/*.smlib`, 305 unique names. Frequency evidence from the exact source-name inventory [Part A](ROUND-114-RAW-NAMES-A.tsv), [Part B](ROUND-114-RAW-NAMES-B.tsv), [full histogram](ROUND-114-WS1-MEASURED-PREFIXES.json). **260 of 305** names contain an underscore and thus have a genuine last component; **45 are one-token names** and excluded from the suffix-frequency counts here.

**Verdict:** teach **a small set of productive naming families + real examples + the full 305-name lookup**, never the unqualified claim that the compiler implements a generic `domain_qualifier_action` naming grammar. A source identifier's recognizability is a pedagogical aid, not Sanskrit grammatical certification or license to invent API names.

## Beginner order: first understand the data/API distinction, then these families

| Suggested lesson | First-token family | Exactly how many current names | Example actually defined (owning module) | Teaching boundary |
|---|---|---:|---|---|
| 1. Fixed raw buffers vs dynamic collections | `mala_*` | **8** | `mala_grah` (`mala`) | Raw `mala` helper pointer is fixed-size and caller-managed; not the resizable language `kosh` |
| 2. Lists | `suchi_*` | **21** | `suchi_khip` (`suchi`) | Handle-based list; stack/queue names are different families in same module |
| 3. Byte strings | `khand_*` | **22** | `khand_anwesh` (`khand`) | Packed bytes with explicit lengths; do not mix with qword-cell string arrays |
| 4. Character/cell strings | `varna_*` | **18** | `varna_anwesh` (`varna`) | Distinguish cell array operations from packed byte strings and NUL-terminated calls |
| 5. Arithmetic with failure conventions | `ganita_*` | **18** | `ganita_janchit_yuj` (`ganita`) | Some functions in ganita are unprefixed (e.g., `kuttaka`), and saturation uses `paripurna`, not imaginary `sat` |
| 6. Formatting | `roop_*` | **23** | `roop_ank` (`roop`) | Output byte buffers, width and rounding constraints |
| 7. Maps | `nighantu_*` | **17** | `nighantu_grah` (`nighantu`) | Map keys are byte strings; sentinel/failure rules require attention |
| 8. Explicit success/failure | `phal_*` | **14** | `phal_siddhi` (`phal`) | Mutable 2-cell Result representation, check success explicitly |

**These eight families cover 141 distinct current names (46.2% of the 305).** Lesson order is based on conceptual dependencies, not strictly frequency rank. A `kosh` type or `akshar_rakh` builtin is not a `lib/kosh.smlib` or `lib/akshar.smlib` function family.

## Second lesson: family exceptions that appear in actual source

| Family | Count | Meaning & where to find it |
|---|---:|---|
| `brihat_*` | **15** | 13 functions in `brihat` and two conversion functions in `aadhar`; prefix does not prove defining module |
| `rakh_*` | **14** | Set operations actually in `sangrah`, not a `rakh.smlib` module |
| `asti_*` | **13** | Predicate-style names across different modules, not an importable domain |
| `avali_*` | **9** | Queue operations inside `suchi` |
| `chay_*` | **4** | Stack operations inside `suchi` |

## Beginner order: useful endings, counted ONLY when there is an underscore

| Order | Final component | Frequency among 260 compounds | Real example (defining module) | Practical mnemonic |
|---|---|---:|---|---|
| 1 | `srij` | **4** | `suchi_srij` (`suchi`) | Create/initialize |
| 2 | `khip` | **3** | `suchi_khip` (`suchi`) | Insert/push |
| 3 | `grah` | **3** | `mala_grah` (`mala`) | Retrieve |
| 4 | `maap` | **6** | `suchi_maap` (`suchi`) | Size/measure |
| 5 | `gan` | **6** | `suchi_gan` (`suchi`) | Count (but `ank_gan` counts digits) |
| 6 | `anwesh` | **6** | `suchi_anwesh` (`suchi`) | Search |
| 7 | `antah` | **6** | `nighantu_antah` (`nighantu`) | Membership/contains |
| 8 | `rikta` | **5** | `suchi_rikta` (`suchi`) | Empty/clear |
| 9 | `apanay` | **4** | `suchi_apanay` (`suchi`) | Remove |
| 10 | `yuj` | **7** | `ganita_janchit_yuj` (`ganita`) | Join/add; meaning depends on data type |
| 11 | `gun` | **4** | `ganita_janchit_gun` (`ganita`) | Multiply |
| 12 | `nyun` | **4** | `ganita_janchit_nyun` (`ganita`) | Subtract |

**Non-verbal suffixes are not actionable procedures.** `akshar` (**10**), `ank` (**7**) and `shreni` (**5**) are common last components, but often describe an object, representation or operation family. Do not teach "last token is always a verb." Source input has **126 different terminal components** among 260 compounded names; a short memorized table is a starting point, never exhaustive.

## Necessary beginner checks

- For every displayed callable, copy the **actual** signature and import from `lib/`/`docs/sutram-stdlib.html`, never synthesize calls from likely-sounding pieces; `ganita_paripurna_yuj` exists, `ganita_sat_yuj` does not.
- Teach success/failure channels and pointer allocation sizes where relevant; a familiar name does not imply memory safety.
- Build a searchable, reviewed **305-name current lookup** organized by the actual defining module. Human-authored explanations and examples must receive separate executable acceptance.
- A Sanskrit scholar must certify linguistic morphology/etymology; an observed underscore convention is a software convention.

**PASS — frequency counts from all pinned source declarations, 0 inferred callable names. NOT RUN - no toolchain** for beginner example compilation and Windows testing.
