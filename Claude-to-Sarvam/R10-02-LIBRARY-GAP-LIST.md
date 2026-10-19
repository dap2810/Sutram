# R10-02 — WS2 (Step 5): the open functions, continued

**Measured with the same tools and verdict rules,** against this branch's compiler. Linux. The per-mutant
list is in `evidence-r10/gap-list/lib-gap-list.md`.

**255 of 303 functions are closed (R9: 235; R8: 212). 48 are open.** Boundary mutants killed: **889 of
1,119** (R9: 881).

*(Your brief says "the 91 open functions": that was R8's count. R9 brought it to 68, and this round to 48.)*

## Closed this round (20), and how

**By proof** (`tests/stdlib/r10_roop_suchi_edges.sm`, expectations computed in Python first):

| Function | The proof |
|---|---|
| `roop_ank_aadhar` | −2^63 in base 29, whose last digit is 12: `c` lower case, `C` upper case |
| `roop_ank_dhvaj` | 0 with flags: `0`, no minus sign |
| `suchi_antah`, `suchi_kramank` | the value just past the length is a stale one; it must not be found |
| `avali_tak_mala` | a guard cell after the output survives |
| `suchi_viparyay`, `suchi_shreni` | their documented return of 1, and the result |

**By argument** (`tools/lib_gap_reviewed.json`, 31 new entries, each with its reason):

| Function | Why the remaining mutants are equivalent |
|---|---|
| `roop_pad_vam`, `roop_pad_dakshin`, `roop_pad_madhya`, `roop_chinhit`, `roop_sign_akshar` | each loop's extra pass writes a byte that the next write or the terminator overwrites |
| `roop_ank`, `roop_ank_aadhar` (`val < 0`) | 0 returns before the test |
| `roop_ank_aadhar` (`lo < 10`) | on the −2^63 path, `lo` is 2^63 mod base, which is never exactly 10 for any base 2..36 (checked over all 35) |
| `budbud_shreni`, `shankh_shreni`, `nivesh_shreni`, `mil_shreni_punar` (`>` → `>=`, `<` → `<=`) | swapping or moving equal integers changes nothing; integers have no stability to lose |
| `viparyay_mala`, `suchi_viparyay` | `i = j` swaps the middle with itself |
| `dwi_anwesh` | the equal case has already returned |
| `suchi_vardh` | its only caller tests `== 0`, so returning 2 for success is the same |

## Still open (48)

- **aadhar** (2): `brihat_ank_tak`, `brihat_ank_se`
- **anukram** (2): `anukram_khip_ashtak`, `anukram_grah_ashtak`
- **brihat** (3): `brihat_gun`, `brihat_bhajshesh`, `brihat_shesh`
- **kalana** (5): `pravan`, `kalana_trapiz`, `simpson`, `pravan2`, `bahu_mula`
  - These take `kosh dasham`. A generator for those is needed.
- **khand** (7): `khand_bhed`, `khand_pratisthap`, `khand_yuj`, `khand_viparyay`, `khand_unnat`,
  `khand_ant`, `khand_avanat`
- **nighantu** (9): `nighantu_anwesh`, `nighantu_vardh`, `nighantu_apanay` (the one GAP),
  `nighantu_rikta`, `nighantu_grah_mool`, `nighantu_kunji_gudh`, `nighantu_koshtha_likh`,
  `nighantu_mulya`, `nighantu_kunjika`
- **roop** (2): `roop_varg_mool`, `roop_sthir_mool`
- **samanvaya** (2): `rekha_manak`, `sadish_yoga`
- **sangrah** (3): `rakh_tak_mala`, `rakh_sampat`, `rakh_rikta`
- **sankhyiki** (1): `purna_vyapti`
- **suchi** (2): `suchi_rikta`, `avali_rikta`
  - Their clearing loops would write one cell past the block. That cell is outside the allocation, so no
    guard can sit there, and these stay OVERRUN honestly.
- **vakyank** (2): `varna_tak_dashm`, `pad_vam`
- **varna** (8): `varna_bhed`, `varna_antah`, `varna_unnat`, `varna_pratisthap`, `varna_chhid`,
  `varna_viparyay`, `varna_gan`, `varna_avanat`

**What remains:**

- **34 OVERRUN:** a loop running once more would go unnoticed.
- **38 REVIEW:** list, string or float arguments, not decided yet.
- **1 GAP.**

**Why not more:** F1 came first, as the brief says. This round's Step 5 work was what fitted after it.
