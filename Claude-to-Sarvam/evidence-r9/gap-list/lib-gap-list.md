# The library gap list

303 functions in 24 modules. Whole-body mutant (S) detected for 303. Off-by-one and boundary mutants killed: **881/1119**. Surviving: EQUIVALENT 62, GAP 1, LIKELY-EQ 57, NO-CONTRACT 4, OUT-OF-CONTRACT 3, OVERRUN 55, REVIEW 56.

**Closed** (every boundary mutant killed, or only equivalent / likely-equivalent / out-of-contract survivors): **235** functions. **Open: 68.**

## By module

| module | functions | S detected | boundary mutants killed | functions with a GAP | OVERRUN | REVIEW | equivalent / likely |
|---|---|---|---|---|---|---|---|
| aadhar | 2 | 2 | 13/16 | 0 | 2 | 1 | 0 / 0 |
| ank | 10 | 10 | 29/36 | 0 | 0 | 0 | 2 / 4 |
| anukram | 5 | 5 | 16/22 | 0 | 2 | 2 | 2 / 0 |
| brihat | 12 | 12 | 38/52 | 0 | 7 | 1 | 2 / 0 |
| chandas | 6 | 6 | 17/18 | 0 | 0 | 0 | 1 / 0 |
| ganit | 18 | 18 | 28/36 | 0 | 0 | 0 | 2 / 5 |
| ganita | 22 | 22 | 80/114 | 0 | 0 | 0 | 12 / 21 |
| gudh | 2 | 2 | 3/3 | 0 | 0 | 0 | 0 / 0 |
| kalana | 6 | 6 | 26/37 | 0 | 1 | 10 | 0 / 0 |
| khand | 22 | 22 | 91/110 | 0 | 5 | 2 | 12 / 0 |
| madhava | 5 | 5 | 8/22 | 0 | 0 | 0 | 1 / 13 |
| mala | 8 | 8 | 15/16 | 0 | 0 | 0 | 1 / 0 |
| nighantu | 17 | 17 | 49/71 | 1 | 5 | 5 | 9 / 2 |
| patra | 3 | 3 | 8/13 | 0 | 0 | 0 | 0 / 5 |
| phal | 14 | 14 | 24/24 | 0 | 0 | 0 | 0 / 0 |
| roop | 23 | 23 | 72/99 | 0 | 15 | 10 | 2 / 0 |
| sadhan | 7 | 7 | 13/16 | 0 | 0 | 0 | 0 / 3 |
| samanvaya | 10 | 10 | 24/27 | 0 | 0 | 2 | 1 / 0 |
| sangrah | 14 | 14 | 27/34 | 0 | 5 | 2 | 0 / 0 |
| sankhyiki | 16 | 16 | 34/41 | 0 | 0 | 1 | 5 / 1 |
| shreni | 14 | 14 | 36/46 | 0 | 2 | 6 | 2 / 0 |
| suchi | 34 | 34 | 66/83 | 0 | 7 | 4 | 3 / 3 |
| vakyank | 6 | 6 | 53/57 | 0 | 0 | 4 | 0 / 0 |
| varna | 27 | 27 | 111/126 | 0 | 4 | 6 | 5 / 0 |

## Open functions, module by module (most-used first)

- **aadhar** (2/2): `brihat_ank_tak` (OVERRUN), `brihat_ank_se` (OVERRUN/REVIEW)
- **anukram** (2/5): `anukram_khip_ashtak` (OVERRUN/REVIEW), `anukram_grah_ashtak` (OVERRUN/REVIEW)
- **brihat** (3/12): `brihat_gun` (OVERRUN), `brihat_bhajshesh` (OVERRUN), `brihat_shesh` (OVERRUN/REVIEW)
- **kalana** (5/6): `pravan` (REVIEW), `kalana_trapiz` (REVIEW), `simpson` (REVIEW), `pravan2` (REVIEW), `bahu_mula` (OVERRUN/REVIEW)
- **khand** (7/22): `khand_bhed` (REVIEW), `khand_pratisthap` (REVIEW), `khand_yuj` (OVERRUN), `khand_viparyay` (OVERRUN), `khand_unnat` (OVERRUN), `khand_ant` (OVERRUN), `khand_avanat` (OVERRUN)
- **nighantu** (9/17): `nighantu_anwesh` (REVIEW), `nighantu_vardh` (REVIEW), `nighantu_apanay` (GAP), `nighantu_rikta` (OVERRUN), `nighantu_grah_mool` (REVIEW), `nighantu_kunji_gudh` (REVIEW), `nighantu_koshtha_likh` (OVERRUN/REVIEW), `nighantu_mulya` (OVERRUN), `nighantu_kunjika` (OVERRUN)
- **roop** (10/23): `roop_ank_aadhar` (REVIEW), `roop_ank_dhvaj` (REVIEW), `roop_pad_vam` (OVERRUN/REVIEW), `roop_chinhit` (OVERRUN), `roop_sign_akshar` (OVERRUN), `roop_ank` (REVIEW), `roop_pad_dakshin` (OVERRUN/REVIEW), `roop_pad_madhya` (OVERRUN/REVIEW), `roop_varg_mool` (OVERRUN/REVIEW), `roop_sthir_mool` (REVIEW)
- **samanvaya** (2/10): `rekha_manak` (REVIEW), `sadish_yoga` (REVIEW)
- **sangrah** (3/14): `rakh_tak_mala` (OVERRUN/REVIEW), `rakh_sampat` (OVERRUN), `rakh_rikta` (REVIEW)
- **sankhyiki** (1/16): `purna_vyapti` (REVIEW)
- **shreni** (6/14): `dwi_anwesh` (REVIEW), `budbud_shreni` (OVERRUN/REVIEW), `viparyay_mala` (OVERRUN), `shankh_shreni` (REVIEW), `mil_shreni_punar` (REVIEW), `nivesh_shreni` (REVIEW)
- **suchi** (8/34): `suchi_vardh` (OVERRUN/REVIEW), `suchi_shreni` (REVIEW), `suchi_rikta` (OVERRUN), `suchi_antah` (OVERRUN), `suchi_kramank` (OVERRUN), `suchi_viparyay` (OVERRUN/REVIEW), `avali_tak_mala` (OVERRUN), `avali_rikta` (OVERRUN/REVIEW)
- **vakyank** (2/6): `varna_tak_dashm` (REVIEW), `pad_vam` (REVIEW)
- **varna** (8/27): `varna_bhed` (OVERRUN), `varna_antah` (REVIEW), `varna_unnat` (OVERRUN), `varna_pratisthap` (REVIEW), `varna_chhid` (REVIEW), `varna_viparyay` (OVERRUN/REVIEW), `varna_gan` (REVIEW), `varna_avanat` (OVERRUN)

## Functions without a direct proof (S mutant not detected directly)

| module | function | status | contract (source comment) |
|---|---|---|---|
| brihat | `brihat_shesh(ank, shesh, res, n)` | PROVEN-INDIRECT | brihat_shesh(num, shesh, res, n) — res = num % shesh, where num has 2n digits Helper for powmod. Uses long division. she |
| nighantu | `nighantu_koshtha_likh(m, slot, cap, key, keyn, val)` | PROVEN-INDIRECT | nighantu_koshtha_likh(m, slot, cap, key, keyn, val) — store key+val at slot and mark it live (internal helper; keyn alre |
| nighantu | `nighantu_kunji_gudh(key, keyn, cap)` | PROVEN-INDIRECT | nighantu_kunji_gudh(key, keyn, cap) — home bucket of key (internal helper). |
| nighantu | `nighantu_kunji_sam(m, slot, cap, key, keyn)` | PROVEN-INDIRECT | nighantu_kunji_sam(m, slot, cap, key, keyn) — 1 if slot's key equals (key,keyn) (internal helper; keyn already truncated |
| roop | `roop_sthir_mool(dasham x, places, always_sign, out)` | PROVEN-INDIRECT | --- fixed decimals (private helper) --- roop_sthir_mool(dasham x, places, always_sign, out) — |x| rounded HALF AWAY FROM |
| roop | `roop_varg_mool(src, sn, step, out)` | PROVEN-INDIRECT | --- thousands grouping (private helper) --- roop_varg_mool(src, sn, step, out) — group the integer part of a digit strin |
| shreni | `mil_shreni_punar(a, tmp, lo, hi)` | PROVEN-INDIRECT | mil_shreni(a, n) — top-down merge sort using a temp buffer. |
| suchi | `suchi_vardh(l)` | PROVEN-INDIRECT | suchi_vardh(l) — private helper: dvigun l's capacity, copying the data. Returns 1 ok / 0 allocation failure (list unchan |

## Every surviving mutant, most-used function first

| module | function | uses | mutant | source line | verdict | why |
|---|---|---|---|---|---|---|
| brihat | `brihat_ank_se_int` | 60 | `C2:<-><=` | `yadi (v < 0) { v = 0 - v }` | EQUIVALENT | abs-zero |
| brihat | `brihat_ank_se_int` | 60 | `C6:<-><=` | `yavat (j < c) {` | EQUIVALENT | reviewed: the carry loop only writes while carry is 1; adding 1 to MAX's digits stops at the lowest digit (7 -> 8), so the extra pass at j = n writes nothing |
| nighantu | `nighantu_khip` | 41 | `C3:>->>=` | `yadi (kn > 32) { kn = 32 }` | EQUIVALENT | clamp |
| ganit | `mahattam` | 34 | `C2:<-><=` | `yadi (x < 0) { x = 0 - x }` | EQUIVALENT | abs-zero |
| ganita | `chakravala` | 23 | `C5:<-><=` | `yadi (d < 0 && r != 0) { t = t - 1 }` | LIKELY-EQ | reviewed: floor adjustment when r = 0 picks the other bracketing candidate; tests/stdlib/r8_chakravala_sweep.sm (n = 2..99) agrees |
| ganita | `chakravala` | 23 | `C6:!=->==` | `yadi (d < 0 && r != 0) { t = t - 1 }` | LIKELY-EQ | reviewed: as C5; the sweep agrees |
| ganita | `chakravala` | 23 | `C7:<-><=` | `yavat (cnt < 2) {` | LIKELY-EQ | reviewed: a third candidate m (t + 2) is further from sqrt(n) than the two bracketing ones, so it is never chosen; the sweep agrees |
| ganita | `chakravala` | 23 | `C8:>=->>` | `yadi (m >= 0 && m <= 3037000499) {` | LIKELY-EQ | reviewed: m = 0 is never the better candidate for n >= 2; the sweep agrees |
| ganita | `chakravala` | 23 | `C9:<=-><` | `yadi (m >= 0 && m <= 3037000499) {` | LIKELY-EQ | reviewed: m = 3037000499 needs n near 2^63; the sweep cannot reach it. Not proven |
| ganita | `chakravala` | 23 | `C10:<-><=` | `yadi (f < 0) { f = 0 - f }` | EQUIVALENT | abs-zero |
| ganita | `chakravala` | 23 | `C11:<-><=` | `yadi (bf < 0 ¦¦ f < bf) {` | LIKELY-EQ | reviewed: a tie between the two candidates: either gives a valid step; the sweep agrees |
| ganita | `chakravala` | 23 | `C12:<-><=` | `yadi (bf < 0 ¦¦ f < bf) {` | LIKELY-EQ | reviewed: as C11 |
| khand | `khand_tul` | 20 | `C1:<-><=` | `yadi (yn < n) { n = yn }` | EQUIVALENT | min/max tie |
| nighantu | `nighantu_grah` | 20 | `C1:>->>=` | `yadi (kn > 32) { kn = 32 }` | EQUIVALENT | clamp |
| ganit | `laghuttam` | 19 | `C2:<-><=` | `yadi (r < 0) { r = 0 - r }` | EQUIVALENT | abs-zero |
| nighantu | `nighantu_srij` | 19 | `C1:<-><=` | `yadi (c < 1) { c = 1 }` | EQUIVALENT | clamp |
| nighantu | `nighantu_srij` | 19 | `C2:<-><=` | `yadi (sz < 0) { prati 0 }` | LIKELY-EQ | 6 inputs |
| nighantu | `nighantu_srij` | 19 | `C4:<-><=` | `yavat (i < c) {` | LIKELY-EQ | 6 inputs |
| ganita | `ganita_paripurna_ghat` | 18 | `C4:>->>=` | `yadi (base > 0) { prati maxv }` | LIKELY-EQ | 352 inputs |
| ganita | `ganita_paripurna_ghat` | 18 | `C7:>->>=` | `yadi (base > 0) { prati minv }` | LIKELY-EQ | 352 inputs |
| suchi | `avali_pravesh` | 17 | `C3:<-><=` | `yavat (k < qu[0]) {` | EQUIVALENT | reviewed: the extra cell copied into the new block is at the tail, which the new value overwrites at once |
| ganita | `ganita_paripurna_gun` | 16 | `C6:==->!=` | `yadi (x == 0 - 1) { prati maxv }` | LIKELY-EQ | 361 inputs |
| ganita | `ganita_paripurna_gun` | 16 | `C8:<-><=` | `yadi (x < 0) { neg = 1 - neg }` | LIKELY-EQ | 361 inputs |
| ganita | `ganita_paripurna_gun` | 16 | `C9:<-><=` | `yadi (y < 0) { neg = 1 - neg }` | LIKELY-EQ | 361 inputs |
| nighantu | `nighantu_antah` | 15 | `C1:>->>=` | `yadi (kn > 32) { kn = 32 }` | EQUIVALENT | clamp |
| ganita | `ganita_vargmool` | 14 | `C1:<-><=` | `yadi (x < 0) { prati 0 }` | LIKELY-EQ | 332 inputs |
| khand | `khand_bandh` | 14 | `C1:<=-><` | `yadi (cnt <= 0) {` | EQUIVALENT | reviewed: n = 0 skips the loop and writes the same single terminator |
| khand | `khand_bandh` | 14 | `C2:<-><=` | `yavat (i < cnt) {` | EQUIVALENT | reviewed: as khand_pratilip C2: out[n] is overwritten by the terminator |
| anukram | `anukram_khip_i64` | 13 | `C4:<-><=` | `yadi (val < 0) {` | EQUIVALENT | reviewed: val = 0: 0 % 256 is 0, so the floor correction does nothing either way |
| ganita | `ganita_janchit_yuj` | 13 | `C1:>=->>` | `yadi (x >= 0) {` | EQUIVALENT | reviewed: x = 0 takes the other branch, where y < 0 gives s = y < 0: no overflow on either branch |
| ganita | `ganita_janchit_yuj` | 13 | `C2:>=->>` | `yadi (y >= 0) {` | EQUIVALENT | reviewed: y = 0: s = x, which cannot overflow |
| ganita | `ganita_janchit_yuj` | 13 | `C4:<-><=` | `yadi (y < 0) {` | EQUIVALENT | reviewed: y = 0 with x < 0: s = x < 0, which is not flagged either way |
| ganita | `kuttaka` | 13 | `C3:<-><=` | `yadi (bb < 0) { bb = 0 - bb }` | EQUIVALENT | abs-zero |
| ganita | `kuttaka` | 13 | `C4:>->>=` | `yadi (bb > 0) {` | OUT-OF-CONTRACT | reviewed: b = 0 (congruence modulo 0); the witness also breaks the stated precondition gcd(a, b) | c |
| mala | `mala_nava` | 13 | `C1:<-><=` | `yadi (sz < 0) { prati 0 }` | EQUIVALENT | reviewed: since R9 (F2) nirmmita(0) returns 0, which is what the mutant returns; before R9 mala_nava(0) was -22 (finding F2) |
| suchi | `suchi_srij` | 13 | `C1:<-><=` | `yadi (c < 1) { c = 1 }` | EQUIVALENT | clamp |
| suchi | `suchi_srij` | 13 | `C2:<-><=` | `yadi (sz < 0) { prati 0 }` | LIKELY-EQ | 6 inputs |
| vakyank | `varna_tak_dashm` | 13 | `C10:>->>=` | `yadi (c1 > 57) {` | REVIEW | a parameter is a list, string or record |
| vakyank | `varna_tak_dashm` | 13 | `C11:<-><=` | `yadi (ndig < 18) {` | REVIEW | a parameter is a list, string or record |
| vakyank | `varna_tak_dashm` | 13 | `C12:<-><=` | `yadi (p < cnt) {` | REVIEW | a parameter is a list, string or record |
| ank | `asti_sampurna` | 12 | `C1:<-><=` | `yadi (x < 2) { prati 0 }` | LIKELY-EQ | 330 inputs |
| ank | `asti_sampurna` | 12 | `C2:<=-><` | `yavat (d <= x / d) {` | LIKELY-EQ | 330 inputs |
| ank | `collatz_charan` | 12 | `C4:>->>=` | `yadi (x > 3074457345618258602) { prati 0 - 1 }` | LIKELY-EQ | 332 inputs |
| anukram | `anukram_grah_i64` | 12 | `C4:>=->>` | `yadi (top >= 128) {` | EQUIVALENT | reviewed: top byte 128 is the only input that differs: 128 * 2^56 wraps to -2^63, which is what -128 * 2^56 gives (checked by r9_guard_cells.sm with MIN) |
| ganita | `brahmagupta_kshetr` | 12 | `C1:<-><=` | `yadi (p < 0) { prati 0 }` | LIKELY-EQ | 600 inputs |
| khand | `khand_mukt` | 12 | `C1:<=-><` | `yadi (cnt <= 0) {` | EQUIVALENT | reviewed: n = 0 skips the loop and writes the same single terminator |
| khand | `khand_mukt` | 12 | `C2:<-><=` | `yavat (i < cnt) {` | EQUIVALENT | reviewed: as khand_pratilip C2: out[n] is overwritten by the terminator cell |
| madhava | `madhava_vargmool` | 12 | `C1:<=-><` | `yadi (v <= 0.0) { prati 0.0 }` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_vargmool` | 12 | `C2:<-><=` | `yadi (g < 1.0) { g = 1.0 }` | EQUIVALENT | clamp |
| madhava | `madhava_vargmool` | 12 | `C3:<-><=` | `yavat (i < 1000) {` | LIKELY-EQ | 332 inputs |
| varna | `gan_swar` | 12 | `C1:<-><=` | `yavat (i < n) {` | EQUIVALENT | reviewed: the extra pass reads the terminator (0), which is not a vowel |
| ank | `ank_gan` | 11 | `C2:<-><=` | `yadi (x < 0) { x = 0 - x }` | EQUIVALENT | abs-zero |
| ganita | `ganita_janchit_nirapeksh` | 11 | `C2:<-><=` | `yadi (x < 0) { prati 0 - x }` | EQUIVALENT | abs-zero |
| khand | `khand_pratilip` | 11 | `C1:<=-><` | `yadi (cnt <= 0) {` | EQUIVALENT | reviewed: n = 0 skips the loop and writes the same terminator at out[0] |
| khand | `khand_pratilip` | 11 | `C2:<-><=` | `yavat (i < cnt) {` | EQUIVALENT | reviewed: the extra pass writes out[n], which the terminator then overwrites; it reads one source byte past n but nothing depends on it |
| madhava | `madhava_atan` | 11 | `C1:<-><=` | `yadi (ax < 0.0) {` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_atan` | 11 | `C4:<-><=` | `yavat (k < 60) {` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_atan` | 11 | `C5:>->>=` | `yadi (util_chinha > 0) {` | LIKELY-EQ | 332 inputs |
| patra | `patra_path_sarv` | 11 | `C2:<-><=` | `yadi (fd < 0) { prati 0 - 1 }` | LIKELY-EQ | 600 inputs |
| patra | `patra_path_sarv` | 11 | `C3:<-><=` | `yavat (total < c) {` | LIKELY-EQ | 600 inputs |
| shreni | `laghu` | 11 | `C3:<-><=` | `yadi (a[i] < best) { best = a[i] }` | EQUIVALENT | min/max tie |
| brihat | `brihat_bhajshesh` | 10 | `R` | `` | NO-CONTRACT | reviewed: the return value is not documented; q and r are the results and are checked |
| brihat | `brihat_bhajshesh` | 10 | `C1:<-><=` | `yavat (i < c) {` | OVERRUN | one pass past the end |
| brihat | `brihat_bhajshesh` | 10 | `C3:<-><=` | `yavat (m < c) {` | OVERRUN | one pass past the end |
| brihat | `brihat_bhajshesh` | 10 | `C7:<-><=` | `yavat (k < c) {` | OVERRUN | one pass past the end |
| brihat | `brihat_gun` | 10 | `C2:<-><=` | `yavat (i < c) {` | OVERRUN | one pass past the end |
| brihat | `brihat_gun` | 10 | `C3:<-><=` | `yavat (j < c) {` | OVERRUN | one pass past the end |
| chandas | `meru` | 10 | `C3:>->>=` | `yadi (r > top - r) { r = top - r }` | EQUIVALENT | clamp |
| ganit | `ganit_seemit` | 10 | `C1:<-><=` | `yadi (x < a) { prati a }` | OUT-OF-CONTRACT | reviewed: as ank.seemit. The comment says lo > hi returns lo; the code returns hi when v >= lo (R8-01 finding F4) |
| ganit | `ganit_seemit` | 10 | `C2:>->>=` | `yadi (x > b) { prati b }` | LIKELY-EQ | 600 inputs |
| ganit | `yog_tak` | 10 | `C1:<=-><` | `yadi (x <= 0) { prati 0 }` | LIKELY-EQ | 332 inputs |
| ganita | `ganita_janchit_nyun` | 10 | `C2:<-><=` | `yadi (y < 0) {` | EQUIVALENT | reviewed: y = 0: d = x, no overflow |
| ganita | `ganita_janchit_nyun` | 10 | `C3:<-><=` | `yadi (d < 0) {` | EQUIVALENT | reviewed: x >= 0, y < 0: the true x - y is in [1, 2^64 - 1], so the wrapped d is never 0 |
| ganita | `ganita_janchit_nyun` | 10 | `C4:>=->>` | `yadi (y >= 0) {` | EQUIVALENT | reviewed: y = 0: d = x, no overflow |
| ganita | `ganita_janchit_nyun` | 10 | `C5:>=->>` | `yadi (d >= 0) {` | EQUIVALENT | reviewed: x < 0, y >= 0: the true x - y is in [-2^64 + 1, -1], so the wrapped d is never 0 |
| ganita | `ganita_paripurna_nirapeksh` | 10 | `C2:<-><=` | `yadi (x < 0) { prati 0 - x }` | EQUIVALENT | abs-zero |
| ganita | `ganita_paripurna_nyun` | 10 | `C2:<-><=` | `yadi (y < 0) {` | LIKELY-EQ | 361 inputs |
| ganita | `ganita_paripurna_nyun` | 10 | `C3:<-><=` | `yadi (d < 0) { prati maxv }` | LIKELY-EQ | 361 inputs |
| ganita | `ganita_paripurna_nyun` | 10 | `C4:>=->>` | `yadi (y >= 0) {` | LIKELY-EQ | 361 inputs |
| ganita | `ganita_paripurna_nyun` | 10 | `C5:>=->>` | `yadi (d >= 0) { prati minv }` | LIKELY-EQ | 361 inputs |
| ganita | `ganita_paripurna_yuj` | 10 | `C1:>=->>` | `yadi (x >= 0) {` | LIKELY-EQ | 361 inputs |
| ganita | `ganita_paripurna_yuj` | 10 | `C2:>=->>` | `yadi (y >= 0) {` | LIKELY-EQ | 361 inputs |
| ganita | `ganita_paripurna_yuj` | 10 | `C4:<-><=` | `yadi (y < 0) {` | LIKELY-EQ | 361 inputs |
| khand | `khand_bhed` | 10 | `C11:>=->>` | `yadi (rpos >= slen) {` | REVIEW | a parameter is a list, string or record |
| madhava | `madhava_pi` | 10 | `C1:<-><=` | `yavat (k < 30) {` | LIKELY-EQ | 1 inputs |
| madhava | `madhava_pi` | 10 | `C2:>->>=` | `yadi (util_chinha > 0) {` | LIKELY-EQ | 1 inputs |
| nighantu | `nighantu_anwesh` | 10 | `C1:<-><=` | `yadi (cap < 1) { prati 0 - 1 }` | REVIEW | a parameter is a list, string or record |
| nighantu | `nighantu_anwesh` | 10 | `C3:>->>=` | `yadi (kn > 32) { kn = 32 }` | EQUIVALENT | clamp |
| sadhan | `bhaj_urdhva` | 10 | `C3:>->>=` | `yadi (r > 0) {` | LIKELY-EQ | 361 inputs |
| sadhan | `bhaj_urdhva` | 10 | `C4:>->>=` | `yadi (b > 0) { q = q + 1 }` | LIKELY-EQ | 361 inputs |
| sadhan | `bhaj_urdhva` | 10 | `C5:<-><=` | `yadi (b < 0) { q = q + 1 }` | LIKELY-EQ | 361 inputs |
| sangrah | `rakh_tak_mala` | 10 | `C1:<-><=` | `yavat (i < nk) {` | OVERRUN | one pass past the end |
| sangrah | `rakh_tak_mala` | 10 | `C2:<-><=` | `yavat (k < seglen) {` | OVERRUN | one pass past the end |
| sangrah | `rakh_tak_mala` | 10 | `C3:<-><=` | `yavat (i < nk - 1) {` | OVERRUN | one pass past the end |
| sangrah | `rakh_tak_mala` | 10 | `C5:>->>=` | `yadi (khand_tul(scratch + ptrs[j], lens[j], scratch + ptrs[j + 1], len` | REVIEW | a parameter is a list, string or record |
| sangrah | `rakh_tak_mala` | 10 | `C6:<-><=` | `yavat (i < nk) {` | OVERRUN | one pass past the end |
| aadhar | `brihat_ank_tak` | 9 | `C3:<-><=` | `yavat (i < c) {` | OVERRUN | one pass past the end |
| ank | `ank_yog` | 9 | `C2:<-><=` | `yadi (x < 0) { x = 0 - x }` | EQUIVALENT | abs-zero |
| brihat | `brihat_ghatmod` | 9 | `R` | `` | NO-CONTRACT | reviewed: the return value is not documented; res is the result |
| madhava | `madhava_sin` | 9 | `C1:>->>=` | `yadi (y > pi) { y = y - pi2 }` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_sin` | 9 | `C2:<-><=` | `yadi (y < 0.0 - pi) { y = y + pi2 }` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_sin` | 9 | `C3:<-><=` | `yavat (n < 16) {` | LIKELY-EQ | 332 inputs |
| nighantu | `nighantu_vardh` | 9 | `C1:<-><=` | `yadi (newcap < n) { prati 0 }` | REVIEW | a parameter is a list, string or record |
| roop | `roop_ank_aadhar` | 9 | `C4:<-><=` | `yadi (val < 0) {` | REVIEW | a parameter is a list, string or record |
| roop | `roop_ank_aadhar` | 9 | `C6:<-><=` | `yadi (lo < 10) {` | REVIEW | a parameter is a list, string or record |
| roop | `roop_ank_aadhar` | 9 | `C7:==->!=` | `yadi (up == 1) {` | REVIEW | a parameter is a list, string or record |
| varna | `varna_bhed` | 9 | `C3:<-><=` | `yavat (ci < slen) {` | OVERRUN | one pass past the end |
| ganita | `ganita_nirapeksh` | 8 | `C1:<-><=` | `yadi (x < 0) { prati 0 - x }` | EQUIVALENT | abs-zero |
| madhava | `madhava_cos` | 8 | `C1:>->>=` | `yadi (y > pi) { y = y - pi2 }` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_cos` | 8 | `C2:<-><=` | `yadi (y < 0.0 - pi) { y = y + pi2 }` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_cos` | 8 | `C3:<-><=` | `yavat (n < 16) {` | LIKELY-EQ | 332 inputs |
| nighantu | `nighantu_apanay` | 8 | `C1:>->>=` | `yadi (kn > 32) { kn = 32 }` | EQUIVALENT | clamp |
| nighantu | `nighantu_apanay` | 8 | `C7:<=-><` | `yadi (i <= j) { can_move = 1 }` | EQUIVALENT | reviewed: i == j cannot happen: j starts at i + 1 and stops at the empty slot |
| nighantu | `nighantu_apanay` | 8 | `C9:<=-><` | `yadi (i <= j) { can_move = 1 }` | EQUIVALENT | reviewed: as C7 |
| nighantu | `nighantu_apanay` | 8 | `C12:>=->>` | `yadi (j >= cap) { j = 0 }` | GAP | reviewed: j == cap reads the key-length cell of slot 0 instead of wrapping; needs a deletion whose probe chain wraps past the end with a 1-byte key in slot 0 |
| nighantu | `nighantu_rikta` | 8 | `C1:<-><=` | `yavat (i < cap) {` | OVERRUN | one pass past the end |
| nighantu | `nighantu_rikta` | 8 | `C2:<-><=` | `yavat (k < 32) {` | OVERRUN | one pass past the end |
| patra | `patra_likh_sarv` | 8 | `C2:<-><=` | `yadi (fd < 0) { prati 0 - 1 }` | LIKELY-EQ | 600 inputs |
| patra | `patra_likh_sarv` | 8 | `C4:<=-><` | `yadi (w <= 0) {` | LIKELY-EQ | 600 inputs |
| roop | `roop_ank_dhvaj` | 8 | `C1:<-><=` | `yadi (val < 0) {` | REVIEW | a parameter is a list, string or record |
| roop | `roop_pad_vam` | 8 | `C1:<=-><` | `yadi (w <= cnt) {` | REVIEW | a parameter is a list, string or record |
| roop | `roop_pad_vam` | 8 | `C2:<-><=` | `yavat (i < cnt) {` | OVERRUN | one pass past the end |
| roop | `roop_pad_vam` | 8 | `C3:<-><=` | `yavat (i < npad) {` | OVERRUN | one pass past the end |
| roop | `roop_pad_vam` | 8 | `C4:<-><=` | `yavat (i < cnt) {` | OVERRUN | one pass past the end |
| sankhyiki | `bindu` | 8 | `C1:<-><=` | `yadi (nb < n) { n = nb }` | EQUIVALENT | min/max tie |
| sankhyiki | `purna_adhikatama` | 8 | `C3:>->>=` | `yadi (xs[i] > m) { m = xs[i] }` | EQUIVALENT | min/max tie |
| sankhyiki | `purna_laghutama` | 8 | `C3:<-><=` | `yadi (xs[i] < m) { m = xs[i] }` | EQUIVALENT | min/max tie |
| sankhyiki | `sankhyiki_vargmool` | 8 | `C2:<-><=` | `yavat (k < 1000) {` | LIKELY-EQ | 332 inputs |
| shreni | `dwi_anwesh` | 8 | `C3:<-><=` | `yadi (a[mid] < target) { lo = mid + 1 } anya { hi = mid - 1 }` | REVIEW | a parameter is a list, string or record |
| suchi | `avali_srij` | 8 | `C1:<-><=` | `yadi (c < 1) { c = 1 }` | EQUIVALENT | clamp |
| suchi | `avali_srij` | 8 | `C2:<-><=` | `yadi (sz < 0) { prati 0 }` | LIKELY-EQ | 6 inputs |
| varna | `varna_tul` | 8 | `C1:<-><=` | `yadi (yn < n) { n = yn }` | EQUIVALENT | reviewed: yn == n sets n to the same value |
| anukram | `anukram_grah_ashtak` | 7 | `C3:>->>=` | `yadi (p2 + cnt > c) { prati 0 - 1 }` | REVIEW | a parameter is a list, string or record |
| anukram | `anukram_grah_ashtak` | 7 | `C4:<-><=` | `yavat (i < cnt) {` | OVERRUN | one pass past the end |
| anukram | `anukram_khip_ashtak` | 7 | `C3:>->>=` | `yadi (p + 8 + cnt > c) { prati 0 - 1 }` | REVIEW | a parameter is a list, string or record |
| anukram | `anukram_khip_ashtak` | 7 | `C4:<-><=` | `yavat (i < cnt) {` | OVERRUN | one pass past the end |
| brihat | `brihat_pratilip` | 7 | `R` | `` | NO-CONTRACT | reviewed: as brihat_shunyank R |
| brihat | `brihat_shesh` | 7 | `R` | `` | NO-CONTRACT | reviewed: the return value is not documented; res is the result |
| brihat | `brihat_shesh` | 7 | `C2:<-><=` | `yavat (m2 < c) {` | OVERRUN | one pass past the end |
| brihat | `brihat_shesh` | 7 | `C5:>=->>` | `yavat (brihat_tul(tr, m, c) >= 0) {` | REVIEW | a parameter is a list, string or record |
| brihat | `brihat_shesh` | 7 | `C6:<-><=` | `yavat (k < c) {` | OVERRUN | one pass past the end |
| ganit | `adhik2` | 7 | `C1:>->>=` | `yadi (x > y) { prati x }` | LIKELY-EQ | 361 inputs |
| ganit | `laghu2` | 7 | `C1:<-><=` | `yadi (x < y) { prati x }` | LIKELY-EQ | 361 inputs |
| ganit | `nirapeksh_mulya` | 7 | `C1:<-><=` | `yadi (x < 0) {` | LIKELY-EQ | 332 inputs |
| kalana | `pravan` | 7 | `C1:<-><=` | `yadi (kosh_len(ys) < n) { n = kosh_len(ys) }` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| kalana | `pravan` | 7 | `C2:<-><=` | `yadi (n < 2) { prati 0.0 }` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| khand | `khand_chhid` | 7 | `C2:>=->>` | `yadi (lo >= slen) {` | EQUIVALENT | reviewed: lo == sn: the mutant reads one more byte; a space moves lo past sn, which still leaves hi <= lo and an empty result |
| khand | `khand_chhid` | 7 | `C5:<=-><` | `yadi (hi <= lo) {` | EQUIVALENT | reviewed: hi == lo: byte hi - 1 is a space skipped by the first loop, so hi drops below lo and the result is still empty |
| khand | `khand_pratisthap` | 7 | `C2:<=-><` | `yadi (flen <= 0) {` | REVIEW | a parameter is a list, string or record |
| khand | `khand_viparyay` | 7 | `C1:<=-><` | `yadi (n <= 0) {` | EQUIVALENT | reviewed: sn = 0: the swap loop does nothing, the terminator lands at out[0], and 0 is returned either way |
| khand | `khand_viparyay` | 7 | `C2:<-><=` | `yavat (i < j) {` | OVERRUN | one pass past the end |
| khand | `khand_yuj` | 7 | `C1:<-><=` | `yavat (si < cnt) {` | OVERRUN | one pass past the end |
| nighantu | `nighantu_grah_mool` | 7 | `C1:>->>=` | `yadi (kn > 32) { kn = 32 }` | EQUIVALENT | clamp |
| nighantu | `nighantu_grah_mool` | 7 | `C2:<-><=` | `yadi (slot < 0) { prati def }` | REVIEW | a parameter is a list, string or record |
| patra | `patra_asti` | 7 | `C1:<-><=` | `yadi (fd < 0) { prati 0 }` | LIKELY-EQ | 332 inputs |
| roop | `roop_chinhit` | 7 | `C2:<-><=` | `yavat (i < n) {` | OVERRUN | one pass past the end |
| roop | `roop_chinhit` | 7 | `C3:<-><=` | `yavat (i < n) {` | OVERRUN | one pass past the end |
| roop | `roop_sign_akshar` | 7 | `C2:<-><=` | `yavat (i < n) {` | OVERRUN | one pass past the end |
| roop | `roop_sign_akshar` | 7 | `C3:<-><=` | `yavat (i < n) {` | OVERRUN | one pass past the end |
| sangrah | `rakh_sampat` | 7 | `C1:<-><=` | `yavat (i < nka) {` | OVERRUN | one pass past the end |
| sankhyiki | `purna_vyapti` | 7 | `C1:<=-><` | `yadi (n <= 0) { prati 0 }` | REVIEW | a parameter is a list, string or record |
| shreni | `adhik` | 7 | `C3:>->>=` | `yadi (a[i] > best) { best = a[i] }` | EQUIVALENT | min/max tie |
| suchi | `suchi_apanay` | 7 | `C3:<-><=` | `yavat (k < lst[0] - 1) {` | LIKELY-EQ | reviewed: the extra pass copies d[len] into d[len - 1], which is past the new length; d[len] is read one cell past the length (past the block only when the list is full). Nothing reads either cell |
| vakyank | `pad_vam` | 7 | `C1:<=-><` | `yadi (w <= cnt) { prati cnt }` | REVIEW | a parameter is a list, string or record |
| varna | `varna_antah` | 7 | `C1:>=->>` | `yadi (varna_anwesh(hay, hn, needle, nn) >= 0) { prati 1 }` | REVIEW | a parameter is a list, string or record |
| varna | `varna_sam` | 7 | `C2:<-><=` | `yavat (i < na) {` | EQUIVALENT | reviewed: the extra pass compares the two terminators, both 0 |
| varna | `varna_unnat` | 7 | `C1:<-><=` | `yadi (slen < 0) {` | EQUIVALENT | reviewed: slen = 0: the loop does nothing and dst[0] = 0 either way |
| varna | `varna_unnat` | 7 | `C2:<-><=` | `yavat (i < slen) {` | OVERRUN | one pass past the end |
| ank | `seemit` | 6 | `C1:<-><=` | `yadi (x < a) { prati a }` | OUT-OF-CONTRACT | reviewed: only lo > hi tells them apart (v = lo > hi); for lo <= hi, v = lo returns lo either way |
| ank | `seemit` | 6 | `C2:>->>=` | `yadi (x > b) { prati b }` | LIKELY-EQ | 600 inputs |
| kalana | `kalana_trapiz` | 6 | `C1:<-><=` | `yadi (kosh_len(ys) < n) { n = kosh_len(ys) }` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| khand | `khand_unnat` | 6 | `C1:<-><=` | `yadi (slen < 0) {` | EQUIVALENT | reviewed: sn = 0: the loop does nothing and the terminator lands at out[0] either way |
| khand | `khand_unnat` | 6 | `C2:<-><=` | `yavat (i < slen) {` | OVERRUN | one pass past the end |
| nighantu | `nighantu_kunji_gudh` | 6 | `C1:<-><=` | `yadi (cap < 1) { prati 0 }` | REVIEW | a parameter is a list, string or record |
| roop | `roop_ank` | 6 | `C2:<-><=` | `yadi (val < 0) {` | REVIEW | a parameter is a list, string or record |
| roop | `roop_pad_dakshin` | 6 | `C1:<=-><` | `yadi (w <= cnt) {` | REVIEW | a parameter is a list, string or record |
| roop | `roop_pad_dakshin` | 6 | `C2:<-><=` | `yavat (i < cnt) {` | OVERRUN | one pass past the end |
| roop | `roop_pad_dakshin` | 6 | `C3:<-><=` | `yavat (i < cnt) {` | OVERRUN | one pass past the end |
| roop | `roop_pad_dakshin` | 6 | `C4:<-><=` | `yavat (i < npad) {` | OVERRUN | one pass past the end |
| roop | `roop_pad_madhya` | 6 | `C1:<=-><` | `yadi (w <= cnt) {` | REVIEW | a parameter is a list, string or record |
| roop | `roop_pad_madhya` | 6 | `C2:<-><=` | `yavat (i < cnt) {` | OVERRUN | one pass past the end |
| roop | `roop_pad_madhya` | 6 | `C3:<-><=` | `yavat (i < left) {` | OVERRUN | one pass past the end |
| roop | `roop_pad_madhya` | 6 | `C4:<-><=` | `yavat (i < cnt) {` | OVERRUN | one pass past the end |
| roop | `roop_pad_madhya` | 6 | `C5:<-><=` | `yavat (i < npad - left) {` | OVERRUN | one pass past the end |
| roop | `roop_sthir_mool` | 6 | `C1:<-><=` | `yadi (pl < 0) { pl = 0 }` | EQUIVALENT | clamp |
| roop | `roop_sthir_mool` | 6 | `C2:>->>=` | `yadi (pl > 9) { pl = 9 }` | EQUIVALENT | clamp |
| roop | `roop_sthir_mool` | 6 | `C7:>=->>` | `yadi (scaled >= 9223372036854775807.0) {` | REVIEW | a parameter is a list, string or record |
| roop | `roop_varg_mool` | 6 | `C4:<-><=` | `yavat (i < cnt) {` | OVERRUN | one pass past the end |
| roop | `roop_varg_mool` | 6 | `C12:>->>=` | `yadi (rem > 3) {` | REVIEW | a parameter is a list, string or record |
| sankhyiki | `adhikatama` | 6 | `C3:>->>=` | `yadi (xs[i] > m) { m = xs[i] }` | EQUIVALENT | min/max tie |
| sankhyiki | `laghutama` | 6 | `C3:<-><=` | `yadi (xs[i] < m) { m = xs[i] }` | EQUIVALENT | min/max tie |
| suchi | `suchi_antah` | 6 | `C1:<-><=` | `yavat (i < lst[0]) {` | OVERRUN | one pass past the end |
| suchi | `suchi_kramank` | 6 | `C1:<-><=` | `yavat (i < lst[0]) {` | OVERRUN | one pass past the end |
| suchi | `suchi_rikta` | 6 | `C1:<-><=` | `yavat (i < l[1]) {` | OVERRUN | one pass past the end |
| suchi | `suchi_shreni` | 6 | `R` | `` | REVIEW | a parameter is a list, string or record |
| suchi | `suchi_vardh` | 6 | `R` | `` | REVIEW | a parameter is a list, string or record |
| suchi | `suchi_vardh` | 6 | `C2:<-><=` | `yavat (i < lst[0]) {` | OVERRUN | one pass past the end |
| varna | `varna_chhid` | 6 | `C2:>=->>` | `yadi (lo >= slen) {` | REVIEW | a parameter is a list, string or record |
| varna | `varna_chhid` | 6 | `C5:<=-><` | `yadi (hi <= lo) {` | REVIEW | a parameter is a list, string or record |
| varna | `varna_gan` | 6 | `C1:<=-><` | `yadi (nlen <= 0) { prati 0 }` | REVIEW | a parameter is a list, string or record |
| varna | `varna_pratisthap` | 6 | `C2:<=-><` | `yadi (flen <= 0) {` | REVIEW | a parameter is a list, string or record |
| varna | `varna_viparyay` | 6 | `C1:<=-><` | `yadi (n <= 0) {` | REVIEW | a parameter is a list, string or record |
| varna | `varna_viparyay` | 6 | `C2:<-><=` | `yavat (i < j) {` | OVERRUN | one pass past the end |
| aadhar | `brihat_ank_se` | 5 | `C5:>=->>` | `yadi (dv >= b) { prati 0 }` | REVIEW | a parameter is a list, string or record |
| aadhar | `brihat_ank_se` | 5 | `C6:<-><=` | `yavat (k < c) {` | OVERRUN | one pass past the end |
| kalana | `bahu_mula` | 5 | `C3:<-><=` | `yadi ((flo < 0.0) == (fhi < 0.0)) { ok[0] = 0.0; prati 0.0 }` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| kalana | `bahu_mula` | 5 | `C5:<-><=` | `yadi ((flo < 0.0) == (fhi < 0.0)) { ok[0] = 0.0; prati 0.0 }` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| kalana | `bahu_mula` | 5 | `C6:<-><=` | `yavat (k < 80) {` | OVERRUN | one pass past the end |
| kalana | `bahu_mula` | 5 | `C8:<-><=` | `yadi ((fm < 0.0) == (flo < 0.0)) {` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| kalana | `bahu_mula` | 5 | `C10:<-><=` | `yadi ((fm < 0.0) == (flo < 0.0)) {` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| kalana | `pravan2` | 5 | `C1:<-><=` | `yadi (kosh_len(ys) < n) { n = kosh_len(ys) }` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| kalana | `pravan2` | 5 | `C3:>=->>` | `yadi (i >= n - 1) { prati 0.0 }` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| kalana | `simpson` | 5 | `C1:<-><=` | `yadi (kosh_len(ys) < n) { n = kosh_len(ys) }` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| khand | `khand_ant` | 5 | `C3:<-><=` | `yavat (i < sflen) {` | OVERRUN | one pass past the end |
| nighantu | `nighantu_koshtha_likh` | 5 | `R` | `` | REVIEW | a parameter is a list, string or record |
| nighantu | `nighantu_koshtha_likh` | 5 | `C1:<-><=` | `yavat (i < keyn) {` | OVERRUN | one pass past the end |
| nighantu | `nighantu_kunjika` | 5 | `C1:<-><=` | `yavat (i < cap) {` | OVERRUN | one pass past the end |
| nighantu | `nighantu_mulya` | 5 | `C1:<-><=` | `yavat (i < cap) {` | OVERRUN | one pass past the end |
| sangrah | `rakh_rikta` | 5 | `R` | `` | REVIEW | a parameter is a list, string or record |
| shreni | `budbud_shreni` | 5 | `C1:<-><=` | `yavat (i < n) {` | OVERRUN | one pass past the end |
| shreni | `budbud_shreni` | 5 | `C3:>->>=` | `yadi (a[j] > a[j + 1]) {` | REVIEW | a parameter is a list, string or record |
| shreni | `mil_shreni_punar` | 5 | `R` | `` | REVIEW | a parameter is a list, string or record |
| shreni | `mil_shreni_punar` | 5 | `C8:<-><=` | `yadi (a[j] < a[i]) {` | REVIEW | a parameter is a list, string or record |
| shreni | `shankh_shreni` | 5 | `C5:>->>=` | `yadi (a[j - gap] > temp) {` | REVIEW | a parameter is a list, string or record |
| shreni | `viparyay_mala` | 5 | `C1:<-><=` | `yavat (i < j) {` | OVERRUN | one pass past the end |
| suchi | `avali_rikta` | 5 | `R` | `` | REVIEW | a parameter is a list, string or record |
| suchi | `avali_rikta` | 5 | `C1:<-><=` | `yavat (i < q[1]) {` | OVERRUN | one pass past the end |
| suchi | `avali_tak_mala` | 5 | `C1:<-><=` | `yavat (k < qu[0]) {` | OVERRUN | one pass past the end |
| suchi | `suchi_viparyay` | 5 | `R` | `` | REVIEW | a parameter is a list, string or record |
| suchi | `suchi_viparyay` | 5 | `C1:<-><=` | `yavat (i < j) {` | OVERRUN | one pass past the end |
| khand | `khand_avanat` | 4 | `C1:<-><=` | `yadi (slen < 0) {` | EQUIVALENT | reviewed: as khand_unnat C1 |
| khand | `khand_avanat` | 4 | `C2:<-><=` | `yavat (i < slen) {` | OVERRUN | one pass past the end |
| samanvaya | `rekha_manak` | 4 | `C3:<-><=` | `yadi (e < 0.0) { e = 0.0 - e }` | REVIEW | no number input runs cleanly (the parameters are addresses) |
| samanvaya | `rekha_manak` | 4 | `C4:>->>=` | `yadi (row > best) { best = row }` | EQUIVALENT | min/max tie |
| shreni | `nivesh_shreni` | 4 | `C4:>->>=` | `yadi (arr[j] > key) {` | REVIEW | a parameter is a list, string or record |
| varna | `varna_avanat` | 4 | `C1:<-><=` | `yadi (slen < 0) {` | EQUIVALENT | reviewed: as varna_unnat C1 |
| varna | `varna_avanat` | 4 | `C2:<-><=` | `yavat (i < slen) {` | OVERRUN | one pass past the end |
| samanvaya | `sadish_yoga` | 3 | `C1:<-><=` | `yadi (kosh_len(v) < n) { n = kosh_len(v) }` | REVIEW | no number input runs cleanly (the parameters are addresses) |
