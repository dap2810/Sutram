# The library gap list

303 functions in 24 modules. Whole-body mutant (S) detected for 303. Off-by-one and boundary mutants killed: **935/1119**. Surviving: EQUIVALENT 117, LIKELY-EQ 58, NO-CONTRACT 6, OUT-OF-CONTRACT 3.

**Closed** (every boundary mutant killed, or only equivalent / likely-equivalent / out-of-contract survivors): **303** functions. **Open: 0.**

## By module

| module | functions | S detected | boundary mutants killed | functions with a GAP | OVERRUN | REVIEW | equivalent / likely |
|---|---|---|---|---|---|---|---|
| aadhar | 2 | 2 | 16/16 | 0 | 0 | 0 | 0 / 0 |
| ank | 10 | 10 | 29/36 | 0 | 0 | 0 | 2 / 4 |
| anukram | 5 | 5 | 20/22 | 0 | 0 | 0 | 2 / 0 |
| brihat | 12 | 12 | 46/52 | 0 | 0 | 0 | 2 / 0 |
| chandas | 6 | 6 | 17/18 | 0 | 0 | 0 | 1 / 0 |
| ganit | 18 | 18 | 28/36 | 0 | 0 | 0 | 2 / 5 |
| ganita | 22 | 22 | 80/114 | 0 | 0 | 0 | 12 / 21 |
| gudh | 2 | 2 | 3/3 | 0 | 0 | 0 | 0 / 0 |
| kalana | 6 | 6 | 29/37 | 0 | 0 | 0 | 8 / 0 |
| khand | 22 | 22 | 95/110 | 0 | 0 | 0 | 15 / 0 |
| madhava | 5 | 5 | 8/22 | 0 | 0 | 0 | 1 / 13 |
| mala | 8 | 8 | 15/16 | 0 | 0 | 0 | 1 / 0 |
| nighantu | 17 | 17 | 58/71 | 0 | 0 | 0 | 10 / 2 |
| patra | 3 | 3 | 8/13 | 0 | 0 | 0 | 0 / 5 |
| phal | 14 | 14 | 24/24 | 0 | 0 | 0 | 0 / 0 |
| roop | 23 | 23 | 75/99 | 0 | 0 | 0 | 24 / 0 |
| sadhan | 7 | 7 | 13/16 | 0 | 0 | 0 | 0 / 3 |
| samanvaya | 10 | 10 | 24/27 | 0 | 0 | 0 | 3 / 0 |
| sangrah | 14 | 14 | 31/34 | 0 | 0 | 0 | 3 / 0 |
| sankhyiki | 16 | 16 | 34/41 | 0 | 0 | 0 | 6 / 1 |
| shreni | 14 | 14 | 36/46 | 0 | 0 | 0 | 9 / 0 |
| suchi | 34 | 34 | 74/83 | 0 | 0 | 0 | 5 / 4 |
| vakyank | 6 | 6 | 57/57 | 0 | 0 | 0 | 0 / 0 |
| varna | 27 | 27 | 115/126 | 0 | 0 | 0 | 11 / 0 |

## Open functions, module by module (most-used first)


## Functions without a direct proof (S mutant not detected directly)

| module | function | status | contract (source comment) |
|---|---|---|---|
| nighantu | `nighantu_koshtha_likh(m, slot, cap, key, keyn, val)` | PROVEN-INDIRECT | nighantu_koshtha_likh(m, slot, cap, key, keyn, val) — store key+val at slot and mark it live (internal helper; keyn alre |
| nighantu | `nighantu_kunji_gudh(key, keyn, cap)` | PROVEN-INDIRECT | nighantu_kunji_gudh(key, keyn, cap) — home bucket of key (internal helper). |
| nighantu | `nighantu_kunji_sam(m, slot, cap, key, keyn)` | PROVEN-INDIRECT | nighantu_kunji_sam(m, slot, cap, key, keyn) — 1 if slot's key equals (key,keyn) (internal helper; keyn already truncated |
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
| madhava | `madhava_pi` | 10 | `C1:<-><=` | `yavat (k < 30) {` | LIKELY-EQ | 1 inputs |
| madhava | `madhava_pi` | 10 | `C2:>->>=` | `yadi (util_chinha > 0) {` | LIKELY-EQ | 1 inputs |
| nighantu | `nighantu_anwesh` | 10 | `C3:>->>=` | `yadi (kn > 32) { kn = 32 }` | EQUIVALENT | clamp |
| sadhan | `bhaj_urdhva` | 10 | `C3:>->>=` | `yadi (r > 0) {` | LIKELY-EQ | 361 inputs |
| sadhan | `bhaj_urdhva` | 10 | `C4:>->>=` | `yadi (b > 0) { q = q + 1 }` | LIKELY-EQ | 361 inputs |
| sadhan | `bhaj_urdhva` | 10 | `C5:<-><=` | `yadi (b < 0) { q = q + 1 }` | LIKELY-EQ | 361 inputs |
| sangrah | `rakh_tak_mala` | 10 | `C2:<-><=` | `yavat (k < seglen) {` | EQUIVALENT | reviewed: R11: the extra byte copied per segment lands on the first byte of the next segment's copy, which the next pass overwrites; after the last segment it lands inside scratch (cap*32+1 bytes) past every segment, where nothing reads (khand_tul and khand_mukt read lens[i] bytes from ptrs[i]) |
| sangrah | `rakh_tak_mala` | 10 | `C3:<-><=` | `yavat (i < nk - 1) {` | EQUIVALENT | reviewed: R11: the extra outer bubble pass i = nk - 1 has an empty inner loop (j < 0) |
| sangrah | `rakh_tak_mala` | 10 | `C5:>->>=` | `yadi (khand_tul(scratch + ptrs[j], lens[j], scratch + ptrs[j + 1], len` | EQUIVALENT | reviewed: R11: a set's elements are distinct stored byte strings, so khand_tul of two different elements is never 0 and no equal pair is swapped |
| ank | `ank_yog` | 9 | `C2:<-><=` | `yadi (x < 0) { x = 0 - x }` | EQUIVALENT | abs-zero |
| brihat | `brihat_ghatmod` | 9 | `R` | `` | NO-CONTRACT | reviewed: the return value is not documented; res is the result |
| madhava | `madhava_sin` | 9 | `C1:>->>=` | `yadi (y > pi) { y = y - pi2 }` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_sin` | 9 | `C2:<-><=` | `yadi (y < 0.0 - pi) { y = y + pi2 }` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_sin` | 9 | `C3:<-><=` | `yavat (n < 16) {` | LIKELY-EQ | 332 inputs |
| roop | `roop_ank_aadhar` | 9 | `C4:<-><=` | `yadi (val < 0) {` | EQUIVALENT | reviewed: v = 0 returns '0' before this test is reached |
| roop | `roop_ank_aadhar` | 9 | `C6:<-><=` | `yadi (lo < 10) {` | EQUIVALENT | reviewed: lo is (2^63 mod base) on this -2^63-only path; for every base 2..36 it is never exactly 10, so < 10 and <= 10 agree (checked over all 35 bases) |
| ganita | `ganita_nirapeksh` | 8 | `C1:<-><=` | `yadi (x < 0) { prati 0 - x }` | EQUIVALENT | abs-zero |
| madhava | `madhava_cos` | 8 | `C1:>->>=` | `yadi (y > pi) { y = y - pi2 }` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_cos` | 8 | `C2:<-><=` | `yadi (y < 0.0 - pi) { y = y + pi2 }` | LIKELY-EQ | 332 inputs |
| madhava | `madhava_cos` | 8 | `C3:<-><=` | `yavat (n < 16) {` | LIKELY-EQ | 332 inputs |
| nighantu | `nighantu_apanay` | 8 | `C1:>->>=` | `yadi (kn > 32) { kn = 32 }` | EQUIVALENT | clamp |
| nighantu | `nighantu_apanay` | 8 | `C7:<=-><` | `yadi (i <= j) { can_move = 1 }` | EQUIVALENT | reviewed: i == j cannot happen: j starts at i + 1 and stops at the empty slot |
| nighantu | `nighantu_apanay` | 8 | `C9:<=-><` | `yadi (i <= j) { can_move = 1 }` | EQUIVALENT | reviewed: as C7 |
| patra | `patra_likh_sarv` | 8 | `C2:<-><=` | `yadi (fd < 0) { prati 0 - 1 }` | LIKELY-EQ | 600 inputs |
| patra | `patra_likh_sarv` | 8 | `C4:<=-><` | `yadi (w <= 0) {` | LIKELY-EQ | 600 inputs |
| roop | `roop_pad_vam` | 8 | `C1:<=-><` | `yadi (w <= cnt) {` | EQUIVALENT | reviewed: width = length: the pad path pads 0 bytes and copies the same text, returning the same count |
| roop | `roop_pad_vam` | 8 | `C2:<-><=` | `yavat (i < cnt) {` | EQUIVALENT | reviewed: the extra pass writes out[n], which the terminator then overwrites |
| roop | `roop_pad_vam` | 8 | `C3:<-><=` | `yavat (i < npad) {` | EQUIVALENT | reviewed: the extra pad byte lands where the copy (or, for empty text, the terminator) writes next |
| roop | `roop_pad_vam` | 8 | `C4:<-><=` | `yavat (i < cnt) {` | EQUIVALENT | reviewed: the extra pass writes out[width], which the terminator then overwrites |
| sankhyiki | `bindu` | 8 | `C1:<-><=` | `yadi (nb < n) { n = nb }` | EQUIVALENT | min/max tie |
| sankhyiki | `purna_adhikatama` | 8 | `C3:>->>=` | `yadi (xs[i] > m) { m = xs[i] }` | EQUIVALENT | min/max tie |
| sankhyiki | `purna_laghutama` | 8 | `C3:<-><=` | `yadi (xs[i] < m) { m = xs[i] }` | EQUIVALENT | min/max tie |
| sankhyiki | `sankhyiki_vargmool` | 8 | `C2:<-><=` | `yavat (k < 1000) {` | LIKELY-EQ | 332 inputs |
| shreni | `dwi_anwesh` | 8 | `C3:<-><=` | `yadi (a[mid] < target) { lo = mid + 1 } anya { hi = mid - 1 }` | EQUIVALENT | reviewed: a[mid] == target has already returned, so < and <= see the same values |
| suchi | `avali_srij` | 8 | `C1:<-><=` | `yadi (c < 1) { c = 1 }` | EQUIVALENT | clamp |
| suchi | `avali_srij` | 8 | `C2:<-><=` | `yadi (sz < 0) { prati 0 }` | LIKELY-EQ | 6 inputs |
| varna | `varna_tul` | 8 | `C1:<-><=` | `yadi (yn < n) { n = yn }` | EQUIVALENT | reviewed: yn == n sets n to the same value |
| brihat | `brihat_pratilip` | 7 | `R` | `` | NO-CONTRACT | reviewed: as brihat_shunyank R |
| brihat | `brihat_shesh` | 7 | `R` | `` | NO-CONTRACT | reviewed: the return value is not documented; res is the result |
| ganit | `adhik2` | 7 | `C1:>->>=` | `yadi (x > y) { prati x }` | LIKELY-EQ | 361 inputs |
| ganit | `laghu2` | 7 | `C1:<-><=` | `yadi (x < y) { prati x }` | LIKELY-EQ | 361 inputs |
| ganit | `nirapeksh_mulya` | 7 | `C1:<-><=` | `yadi (x < 0) {` | LIKELY-EQ | 332 inputs |
| kalana | `pravan` | 7 | `C1:<-><=` | `yadi (kosh_len(ys) < n) { n = kosh_len(ys) }` | EQUIVALENT | reviewed: R11 clamp: at kosh_len(ys) == n the assignment stores the value n already has (kosh_len has no side effect); the clamp rule's pattern does not match a call on the left |
| khand | `khand_chhid` | 7 | `C2:>=->>` | `yadi (lo >= slen) {` | EQUIVALENT | reviewed: lo == sn: the mutant reads one more byte; a space moves lo past sn, which still leaves hi <= lo and an empty result |
| khand | `khand_chhid` | 7 | `C5:<=-><` | `yadi (hi <= lo) {` | EQUIVALENT | reviewed: hi == lo: byte hi - 1 is a space skipped by the first loop, so hi drops below lo and the result is still empty |
| khand | `khand_viparyay` | 7 | `C1:<=-><` | `yadi (n <= 0) {` | EQUIVALENT | reviewed: sn = 0: the swap loop does nothing, the terminator lands at out[0], and 0 is returned either way |
| khand | `khand_viparyay` | 7 | `C2:<-><=` | `yavat (i < j) {` | EQUIVALENT | reviewed: R11: the extra pass happens only at i == j (odd n, the middle byte) and stores s[mid] at dst[mid], which the odd-length store after the loop does too; for even n the loop ends at i = j + 1. In place (src == out) the same |
| nighantu | `nighantu_grah_mool` | 7 | `C1:>->>=` | `yadi (kn > 32) { kn = 32 }` | EQUIVALENT | clamp |
| patra | `patra_asti` | 7 | `C1:<-><=` | `yadi (fd < 0) { prati 0 }` | LIKELY-EQ | 332 inputs |
| roop | `roop_chinhit` | 7 | `C2:<-><=` | `yavat (i < n) {` | EQUIVALENT | reviewed: the extra pass copies tmp's terminator to out[n], which the terminator write repeats |
| roop | `roop_chinhit` | 7 | `C3:<-><=` | `yavat (i < n) {` | EQUIVALENT | reviewed: as C2, one place to the right |
| roop | `roop_sign_akshar` | 7 | `C2:<-><=` | `yavat (i < n) {` | EQUIVALENT | reviewed: as roop_chinhit C2 |
| roop | `roop_sign_akshar` | 7 | `C3:<-><=` | `yavat (i < n) {` | EQUIVALENT | reviewed: as roop_chinhit C3 |
| sankhyiki | `purna_vyapti` | 7 | `C1:<=-><` | `yadi (n <= 0) { prati 0 }` | EQUIVALENT | reviewed: R11: n == 0: purna_adhikatama and purna_laghutama both return 0 for n <= 0, so the mutant returns 0 - 0 = 0, the real result |
| shreni | `adhik` | 7 | `C3:>->>=` | `yadi (a[i] > best) { best = a[i] }` | EQUIVALENT | min/max tie |
| suchi | `suchi_apanay` | 7 | `C3:<-><=` | `yavat (k < lst[0] - 1) {` | LIKELY-EQ | reviewed: the extra pass copies d[len] into d[len - 1], which is past the new length; d[len] is read one cell past the length (past the block only when the list is full). Nothing reads either cell |
| varna | `varna_sam` | 7 | `C2:<-><=` | `yavat (i < na) {` | EQUIVALENT | reviewed: the extra pass compares the two terminators, both 0 |
| varna | `varna_unnat` | 7 | `C1:<-><=` | `yadi (slen < 0) {` | EQUIVALENT | reviewed: slen = 0: the loop does nothing and dst[0] = 0 either way |
| varna | `varna_unnat` | 7 | `C2:<-><=` | `yavat (i < slen) {` | EQUIVALENT | reviewed: R11: as khand_unnat C2, for cells: dst[slen] is overwritten by the terminator store |
| ank | `seemit` | 6 | `C1:<-><=` | `yadi (x < a) { prati a }` | OUT-OF-CONTRACT | reviewed: only lo > hi tells them apart (v = lo > hi); for lo <= hi, v = lo returns lo either way |
| ank | `seemit` | 6 | `C2:>->>=` | `yadi (x > b) { prati b }` | LIKELY-EQ | 600 inputs |
| kalana | `kalana_trapiz` | 6 | `C1:<-><=` | `yadi (kosh_len(ys) < n) { n = kosh_len(ys) }` | EQUIVALENT | reviewed: R11 clamp: at kosh_len(ys) == n the assignment stores the value n already has (kosh_len has no side effect); the clamp rule's pattern does not match a call on the left |
| khand | `khand_unnat` | 6 | `C1:<-><=` | `yadi (slen < 0) {` | EQUIVALENT | reviewed: sn = 0: the loop does nothing and the terminator lands at out[0] either way |
| khand | `khand_unnat` | 6 | `C2:<-><=` | `yavat (i < slen) {` | EQUIVALENT | reviewed: R11: the extra pass i = slen writes out[slen], which the terminator store right after the loop overwrites with 0; the only other effect is a read of src[slen], one byte past the input |
| nighantu | `nighantu_kunji_gudh` | 6 | `C1:<-><=` | `yadi (cap < 1) { prati 0 }` | EQUIVALENT | reviewed: R11: cap == 1: the real function returns fnv1a(...) % 1, which is 0 for every hash, and fnv1a has no side effect |
| roop | `roop_ank` | 6 | `C2:<-><=` | `yadi (val < 0) {` | EQUIVALENT | reviewed: v = 0 returns '0' before this test is reached |
| roop | `roop_pad_dakshin` | 6 | `C1:<=-><` | `yadi (w <= cnt) {` | EQUIVALENT | reviewed: as roop_pad_vam C1 |
| roop | `roop_pad_dakshin` | 6 | `C2:<-><=` | `yavat (i < cnt) {` | EQUIVALENT | reviewed: as roop_pad_vam C2 |
| roop | `roop_pad_dakshin` | 6 | `C3:<-><=` | `yavat (i < cnt) {` | EQUIVALENT | reviewed: the extra copied byte lands where the padding (or the terminator) writes next |
| roop | `roop_pad_dakshin` | 6 | `C4:<-><=` | `yavat (i < npad) {` | EQUIVALENT | reviewed: the extra pad byte is out[width], which the terminator overwrites |
| roop | `roop_pad_madhya` | 6 | `C1:<=-><` | `yadi (w <= cnt) {` | EQUIVALENT | reviewed: as roop_pad_vam C1 |
| roop | `roop_pad_madhya` | 6 | `C2:<-><=` | `yavat (i < cnt) {` | EQUIVALENT | reviewed: as roop_pad_vam C2 |
| roop | `roop_pad_madhya` | 6 | `C3:<-><=` | `yavat (i < left) {` | EQUIVALENT | reviewed: the extra left pad byte is overwritten next by the copy, the right padding or the terminator |
| roop | `roop_pad_madhya` | 6 | `C4:<-><=` | `yavat (i < cnt) {` | EQUIVALENT | reviewed: the extra copied byte is overwritten next by the right padding or the terminator |
| roop | `roop_pad_madhya` | 6 | `C5:<-><=` | `yavat (i < npad - left) {` | EQUIVALENT | reviewed: the extra right pad byte is out[width], which the terminator overwrites |
| roop | `roop_sthir_mool` | 6 | `C1:<-><=` | `yadi (pl < 0) { pl = 0 }` | EQUIVALENT | clamp |
| roop | `roop_sthir_mool` | 6 | `C2:>->>=` | `yadi (pl > 9) { pl = 9 }` | EQUIVALENT | clamp |
| roop | `roop_varg_mool` | 6 | `C4:<-><=` | `yavat (i < cnt) {` | EQUIVALENT | reviewed: R11: the extra pass i = cnt can only set dot = cnt, which is dot's starting value; it reads one byte past the input |
| roop | `roop_varg_mool` | 6 | `C12:>->>=` | `yadi (rem > 3) {` | EQUIVALENT | reviewed: R11: this test is in the anya of yadi (rem == 3), so rem != 3 and rem > 3 equals rem >= 3 |
| sankhyiki | `adhikatama` | 6 | `C3:>->>=` | `yadi (xs[i] > m) { m = xs[i] }` | EQUIVALENT | min/max tie |
| sankhyiki | `laghutama` | 6 | `C3:<-><=` | `yadi (xs[i] < m) { m = xs[i] }` | EQUIVALENT | min/max tie |
| suchi | `suchi_vardh` | 6 | `R` | `` | EQUIVALENT | reviewed: its only caller, suchi_khip, tests == 0; 2 and 1 both mean success there |
| suchi | `suchi_vardh` | 6 | `C2:<-><=` | `yavat (i < lst[0]) {` | LIKELY-EQ | reviewed: copies one cell past the length into the new block's next free slot, which the push then writes |
| varna | `varna_chhid` | 6 | `C2:>=->>` | `yadi (lo >= slen) {` | EQUIVALENT | reviewed: R11: at lo == slen the mutant reads s[slen] (and on while those are spaces) and may move lo further; then hi = slen <= lo and the copy loop copies nothing: empty output, return 0, as the real code. It only reads past the end |
| varna | `varna_chhid` | 6 | `C5:<=-><` | `yadi (hi <= lo) {` | EQUIVALENT | reviewed: R11: at hi == lo the mutant reads s[hi - 1] once more (a leading space when lo > 0, s[-1] when slen == 0) and may lower hi below lo; the copy loop copies nothing either way |
| varna | `varna_viparyay` | 6 | `C1:<=-><` | `yadi (n <= 0) {` | EQUIVALENT | reviewed: R11: n == 0 then runs the main path: no swaps (j = -1), no middle store (0 % 2 == 0), dst[0] = 0, return 0: the same as the guarded branch |
| varna | `varna_viparyay` | 6 | `C2:<-><=` | `yavat (i < j) {` | EQUIVALENT | reviewed: R11: as khand_viparyay C2 |
| kalana | `bahu_mula` | 5 | `C3:<-><=` | `yadi ((flo < 0.0) == (fhi < 0.0)) { ok[0] = 0.0; prati 0.0 }` | EQUIVALENT | reviewed: R11: flo == 0.0 and fhi == 0.0 return two lines earlier (NaN too: with ucomisd an unordered compare sets ZF, so NaN == 0.0 is true), so here flo is nonzero and flo < 0.0 equals flo <= 0.0 |
| kalana | `bahu_mula` | 5 | `C5:<-><=` | `yadi ((flo < 0.0) == (fhi < 0.0)) { ok[0] = 0.0; prati 0.0 }` | EQUIVALENT | reviewed: R11: as C3, for fhi |
| kalana | `bahu_mula` | 5 | `C8:<-><=` | `yadi ((fm < 0.0) == (flo < 0.0)) {` | EQUIVALENT | reviewed: R11: fm == 0.0 (and NaN) returns on the line before, so fm is nonzero here |
| kalana | `bahu_mula` | 5 | `C10:<-><=` | `yadi ((fm < 0.0) == (flo < 0.0)) {` | EQUIVALENT | reviewed: R11: flo is the starting value (nonzero, see C3) or an earlier fm (nonzero, see C8) |
| kalana | `pravan2` | 5 | `C1:<-><=` | `yadi (kosh_len(ys) < n) { n = kosh_len(ys) }` | EQUIVALENT | reviewed: R11 clamp: at kosh_len(ys) == n the assignment stores the value n already has (kosh_len has no side effect); the clamp rule's pattern does not match a call on the left |
| kalana | `simpson` | 5 | `C1:<-><=` | `yadi (kosh_len(ys) < n) { n = kosh_len(ys) }` | EQUIVALENT | reviewed: R11 clamp: at kosh_len(ys) == n the assignment stores the value n already has (kosh_len has no side effect); the clamp rule's pattern does not match a call on the left |
| nighantu | `nighantu_koshtha_likh` | 5 | `R` | `` | NO-CONTRACT | reviewed: R11: an internal helper; its return value is not documented and its one caller (nighantu_khip) calls it as a statement |
| shreni | `budbud_shreni` | 5 | `C1:<-><=` | `yavat (i < n) {` | EQUIVALENT | reviewed: the extra outer pass has an inner bound n - 1 - n < 0, so it does nothing |
| shreni | `budbud_shreni` | 5 | `C3:>->>=` | `yadi (a[j] > a[j + 1]) {` | EQUIVALENT | reviewed: swapping two equal integers changes nothing (integers have no identity to keep stable) |
| shreni | `mil_shreni_punar` | 5 | `R` | `` | NO-CONTRACT | reviewed: the return value of this private recursion is not documented or used |
| shreni | `mil_shreni_punar` | 5 | `C8:<-><=` | `yadi (a[j] < a[i]) {` | EQUIVALENT | reviewed: taking the right element on a tie of equal integers changes nothing |
| shreni | `shankh_shreni` | 5 | `C5:>->>=` | `yadi (a[j - gap] > temp) {` | EQUIVALENT | reviewed: moving an equal integer past another changes nothing |
| shreni | `viparyay_mala` | 5 | `C1:<-><=` | `yavat (i < j) {` | EQUIVALENT | reviewed: i = j swaps the middle element with itself |
| suchi | `suchi_viparyay` | 5 | `C1:<-><=` | `yavat (i < j) {` | EQUIVALENT | reviewed: i = j swaps the middle element with itself |
| khand | `khand_avanat` | 4 | `C1:<-><=` | `yadi (slen < 0) {` | EQUIVALENT | reviewed: as khand_unnat C1 |
| khand | `khand_avanat` | 4 | `C2:<-><=` | `yavat (i < slen) {` | EQUIVALENT | reviewed: R11: as khand_unnat C2 |
| samanvaya | `rekha_manak` | 4 | `C3:<-><=` | `yadi (e < 0.0) { e = 0.0 - e }` | EQUIVALENT | reviewed: R11 abs-zero with a dasham literal: at e == 0.0 the mutant makes e = +0.0 where the real code may keep -0.0; row starts at +0.0 and only grows, and row + -0.0 == row + 0.0 for every such row |
| samanvaya | `rekha_manak` | 4 | `C4:>->>=` | `yadi (row > best) { best = row }` | EQUIVALENT | min/max tie |
| shreni | `nivesh_shreni` | 4 | `C4:>->>=` | `yadi (arr[j] > key) {` | EQUIVALENT | reviewed: as shankh_shreni C5 |
| varna | `varna_avanat` | 4 | `C1:<-><=` | `yadi (slen < 0) {` | EQUIVALENT | reviewed: as varna_unnat C1 |
| varna | `varna_avanat` | 4 | `C2:<-><=` | `yavat (i < slen) {` | EQUIVALENT | reviewed: R11: as varna_unnat C2 |
| samanvaya | `sadish_yoga` | 3 | `C1:<-><=` | `yadi (kosh_len(v) < n) { n = kosh_len(v) }` | EQUIVALENT | reviewed: R11 clamp: at kosh_len(v) == n the assignment stores the value n already has (kosh_len has no side effect); the clamp rule's pattern does not match a call on the left |
