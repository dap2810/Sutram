# The complete vocabulary — every name, and what is not Sanskrit

**Extracted from `lib/*.smlib` on main at compiler v253.** **24 modules, 305 functions.** **This is the list to check for
nomenclature: is every name Sanskrit, is it easy to type, and is it easy to remember.**

---

## The 24 modules and their functions

### `ganita` — 22 functions (the checked-arithmetic family)
`kuttaka` · `ganita_vargmool` · `ganita_nirapeksh` · `chakravala` · `samasa` · `brahmagupta_kshetr` ·
`ganita_janchit_yuj` · `ganita_janchit_nyun` · `ganita_janchit_gun` · `ganita_janchit_bhaj` · `ganita_janchit_shesh` ·
`ganita_paripurna_yuj` · `ganita_paripurna_nyun` · `ganita_paripurna_gun` · `ganita_janchit_ghat` ·
`ganita_janchit_kramgun` · `ganita_paripurna_ghat` · `ganita_paripurna_bhaj` · `ganita_paripurna_shesh` ·
`ganita_janchit_nirapeksh` · `ganita_paripurna_nirapeksh` · `ganita_paripurna_kramgun`

### `ganit` — 18 functions
**A SECOND MODULE WITH THE SAME NAME, ONE LETTER SHORT.** **See the findings below.**
`varg` · `vargit` · `ghan` · `nirapeksh_mulya` · `laghu2` · `adhik2` · `mahattam` · `laghuttam` · `ghat` · `kramgun` ·
`asti_abhajya` · `yog_tak` · `dvigun` · `trigun` · `vardh` · **`bit_gan`** · `ganit_yadricch` · `ganit_seemit`

### `suchi` — 34 functions (the largest)
`suchi_srij` · `suchi_vardh` · `suchi_khip` · `suchi_grah` · `suchi_sangrah` · `suchi_maap` · `suchi_nivesh` ·
`suchi_apanay` · `suchi_vinimay` · `suchi_viparyay` · `suchi_shreni` · `suchi_laghu` · `suchi_adhik` · `suchi_yog` ·
`suchi_gan` · `suchi_anwesh` · **`suchi_asti_sorted`** · `suchi_dwi_anwesh` · `suchi_rikta` · `suchi_antah` ·
`suchi_kramank` · **`chay_khip`** · **`chay_apanay`** · **`chay_avalok`** · **`chay_rikta`** · `avali_srij` ·
`avali_pravesh` · **`avali_nishkas`** · `avali_avalok` · `avali_tak_mala` · `avali_antah` · `avali_rikta` ·
`avali_shunya` · `avali_maap`

### `varna` — 27 functions (characters and bytes)
`varna_maap` · `akshar_sanket` · `asti_ank_akshar` · `asti_unnat_akshar` · `asti_avanat_akshar` · `asti_akshar_akshar` ·
`asti_avakash_akshar` · `gan_swar` · `gan_akshar` · `anwesh_akshar` · `asti_sarv_ank` · `unnat_sanket` ·
`avanat_sanket` · `varna_sam` · `varna_anwesh` · `varna_antah` · `varna_pratisthap` · `varna_bhed` · `varna_yuj` ·
`varna_chhid` · `varna_unnat` · `varna_avanat` · `varna_aadi` · `varna_ant` · `varna_tul` · `varna_viparyay` ·
`varna_gan`

### `roop` — 23 functions (formatting)
`roop_ank` · `roop_ank_aadhar` · **`roop_ank_aadhar2`** · `roop_ank_dhvaj` · `roop_dash` · `roop_shodash` ·
`roop_shodash_unnat` · `roop_asht` · `roop_dwi` · `roop_ank_pre` · `roop_pad_vam` · `roop_pad_dakshin` ·
`roop_pad_madhya` · `roop_varg_mool` · `roop_varg_bharatiya` · `roop_varg_vishwa` · `roop_varg` · `roop_varg_ank` ·
`roop_sthir_mool` · `roop_sthir` · `roop_sthir_chinhit` · `roop_chinhit` · **`roop_sign_akshar`**

### `khand` — 22 functions (bit operations)
`khand_bandh` · `khand_mukt` · `khand_pratilip` · `khand_maap` · `khand_anwesh` · `khand_antah` · `khand_pratisthap` ·
`khand_bhed` · `khand_yuj` · `khand_chhid` · `khand_unnat` · `khand_avanat` · `khand_aadi` · `khand_ant` ·
`khand_tul` · `khand_viparyay` · `khand_gan` · `khand_gan_swar` · `khand_gan_akshar` · `khand_anwesh_akshar` ·
`khand_asti_sarv_ank` · `khand_sam`

### `nighantu` — 17 functions (maps)
`nighantu_kunji_gudh` · `nighantu_kunji_sam` · `nighantu_koshtha_likh` · `nighantu_anwesh` · `nighantu_srij` ·
`nighantu_khip` · `nighantu_grah` · `nighantu_antah` · `nighantu_apanay` · `nighantu_rikta` · `nighantu_vardh` ·
`nighantu_grah_mool` · `nighantu_maap` · `nighantu_mil` · `nighantu_mulya` · `nighantu_kunjika` ·
`nighantu_kunjika_ashtak`

### `sankhyiki` — 16 functions (statistics)
`yoga` · `madhya` · `laghutama` · `adhikatama` · `vyapti` · `prasaran` · `sankhyiki_vargmool` · `vichalan` · `bindu` ·
`manak` · `purna_yoga` · `purna_madhya` · `purna_laghutama` · `purna_adhikatama` · `purna_vyapti` · `purna_prasaran`

### `phal` — 14 functions (the result type)
`phal_siddhi` · `phal_dosh` · `phal_asti_siddhi` · `phal_mulya` · `phal_mulya_va` · `phal_se_siddhi` ·
`phal_janchit_yuj` · `phal_janchit_nyun` · `phal_janchit_gun` · `phal_janchit_bhaj` · `phal_janchit_shesh` ·
`phal_janchit_ghat` · `phal_janchit_kramgun` · `phal_janchit_nirapeksh`

### `shreni` — 14 functions (sorting)
`vinimay` · `budbud_shreni` · `viparyay_mala` · `laghu` · `adhik` · `yog` · `anwesh_sarak` · `gan` ·
**`asti_sorted`** · `dwi_anwesh` · `shankh_shreni` · `nivesh_shreni` · `mil_shreni_punar` · `mil_shreni`

### `sangrah` — 14 functions (sets)
`rakh_srij` · `rakh_yuj` · `rakh_antah` · `rakh_apanay` · `rakh_maap` · `rakh_samroop_diff` · `rakh_sangam` ·
`rakh_sampat` · `rakh_bhed` · `rakh_vardh` · `rakh_rikta` · `rakh_sam` · `rakh_asti_upasamuh` · `rakh_tak_mala`

### `brihat` — 13 functions (big numbers)
`brihat_shunyank` · `brihat_ank_se_laghu` · `brihat_ank_tak_laghu` · `brihat_pratilip` · `brihat_tul` · `brihat_yuj` ·
`brihat_nyun` · `brihat_gun` · `brihat_asti_shunyank` · `brihat_bhaj` · `shesh` · `brihat_shesh` · `brihat_shesh_tr` ·
`brihat_ghatmod`

### `samanvaya` — 11 functions (linear algebra)
`samanvaya_akar_na` · **`pehchan`** · `vivartana` · `matrika_yoga` · **`skalar`** · `matrika_gunana` · **`nishan`** ·
**`nirnaya2`** · **`nirnaya3`** · `sadish_yoga` · `rekha_manak`

### `ank` — 10 functions (numbers)
`asti_yugm` · `asti_visham` · `ank_gan` · `ank_yog` · `viparyay_ank` · `asti_vilom` · `seemit` · **`fib`** ·
`asti_sampurna` · `collatz_charan`

### `mala` — 8 functions (fixed arrays)
`mala_nava` · `mala_sangrah` · `mala_grah` · `mala_purn` · `mala_pratilip` · `mala_yog` · `mala_sangrah_surakshit` ·
`mala_grah_surakshit`

### `sadhan` — 7 functions (instruments)
`antargam` · `yog_seema` · `shesh` · `bhaj_urdhva` · **`util_chinha`** · `satya_tak_ank` · `ank_adhik`

### `kalana` — 6 functions (calculus)
`kalana_trapiz` · **`simpson`** · `pravan` · **`pravan2`** · `bahu_ganana` · `bahu_mula`

### `chandas` — 6 functions (metre and combinatorics)
`dviguna` · `meru` · `matra_meru` · `asti_guru` · `guru_gan` · `meru_mala`

### `vakyank` — 6 functions (base conversion)
`ank_tak_varna` · `varna_tak_ank` · `ank_tak_aadhar_varna` · `varna_tak_ank_aadhar` · `pad_vam` · `varna_tak_dashm`

### `anukram` — 5 functions (buffers)
`anukram_maap_ashtak` · `anukram_khip_i64` · `anukram_grah_i64` · `anukram_khip_ashtak` · `anukram_grah_ashtak`

### `madhava` — 5 functions (the Kerala series)
`madhava_vargmool` · `madhava_pi` · `madhava_sin` · `madhava_cos` · `madhava_atan`

### `patra` — 3 functions (files)
`patra_path_sarv` · `patra_likh_sarv` · `patra_asti`

### `aadhar` — 2 functions
**`brihat_ank_tak`** · **`brihat_ank_se`**

### `gudh` — 2 functions (hashing)
**`fnv1a`** · **`fnv1a_varna`**

---

## What is NOT Sanskrit — the findings

### English words (7)
| Name | Module | Note |
|---|---|---|
| **`fib`** | `ank` | **abbreviation of Fibonacci.** 3 letters, no Sanskrit |
| **`fnv1a`, `fnv1a_varna`** | `gudh` | **the FNV-1a algorithm's name** - a proper noun, like MD5 |
| **`simpson`** | `kalana` | **Thomas Simpson's rule** - a proper name |
| **`skalar`** | `samanvaya` | **English "scalar" transliterated** |
| **`util_chinha`** | `sadhan` | **`util` is English**; `chinha` is Sanskrit |
| **`bit_gan`** | `ganit` | **`bit` is English** |
| **`asti_sorted`** | `shreni` | **`sorted` is English** |
| **`suchi_asti_sorted`** | `suchi` | same |
| **`roop_sign_akshar`** | `roop` | **`sign` is English** |

### Not Sanskrit at all — Hindi/Urdu (2)
| Name | Module | Sanskrit would be |
|---|---|---|
| **`pehchan`** | `samanvaya` | **`abhigyan`** (recognition) or `chinha` |
| **`nishan`** | `samanvaya` | **`chinha`** or `lakshan` (mark) |

### Numbered suffixes — a short form (5)
`laghu2` · `adhik2` · `pravan2` · `nirnaya2` · `nirnaya3` · `roop_ank_aadhar2`

**A digit in a name means the second one has no better name.** **`nirnaya2` and `nirnaya3` are three functions with one
name and two digits.**

### Dubious coinages (5)
| Name | Why |
|---|---|
| **`chay_khip`, `chay_apanay`, `chay_avalok`, `chay_rikta`** | **`chay` is not a standard Sanskrit stem.** If it means "stack", `chiti` (heap) or `rachana` would be a real word |
| **`avali_nishkas`** | `nishkas` is not a standard word for "remove"; `apanay` is, and the project already uses it |
| **`samanvaya_akar_na`** | the space before `na` looks like a truncation |

### And the biggest one — two modules with the same name
**`ganita` (22 functions) and `ganit` (18 functions).** **One letter apart, same word, different modules.** **`ganita` is
the checked-arithmetic family; `ganit` is the plain-arithmetic family.**

**A learner cannot tell them apart, and a typo silently picks the wrong module.** **That is worse than any English word on
this list.**

### And two functions named twice
**`aadhar` has `brihat_ank_se` and `brihat_ank_tak`; `brihat` has `brihat_ank_se_laghu` and `brihat_ank_tak_laghu`.**
**The same concept, two names, in two modules.**

---

## What I would ask of the owner

**Three questions, in order of impact:**

1. **Should `ganita` and `ganit` be merged or renamed?** **This is the one that will bite a learner.**
2. **The nine English words and two Hindi words — replace them, or accept them?** **`fib`, `simpson` and `fnv1a` are
   proper names and arguably should stay; `skalar`, `bit_gan`, `asti_sorted`, `roop_sign_akshar` and `util_chinha` are
   not.**
3. **The five numbered suffixes — what are `nirnaya2` and `nirnaya3` actually for?**

---

*Extracted by Sarvam, 27 October 2026, from `lib/*.smlib` on main at compiler v253. Every name above was read from a
`prakriya` declaration, not from memory.*
