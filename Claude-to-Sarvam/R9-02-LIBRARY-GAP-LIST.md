# R9-02 — WS2 (Step 5): the open functions, continued

**Measured with R8's tools and verdict rules.** Linux, against this branch's compiler.

## Result

**235 of 303 functions are closed (R8: 212). 68 are open (R8: 91).** Boundary mutants killed:
**862 → 881 of 1,119**.

| module | functions | open in R8 | **open now** | boundary mutants killed, R8 → now |
|---|---|---|---|---|
| aadhar | 2 | 2 | **2** | 13 → 13 / 16 |
| anukram | 5 | 4 | **2** | 13 → 16 / 22 |
| brihat | 12 | 9 | **3** | 31 → 38 / 52 |
| kalana | 6 | 5 | **5** | 26 → 26 / 37 |
| khand | 22 | 13 | **7** | 87 → 91 / 110 |
| mala | 8 | 4 | **0** | 12 → 15 / 16 |
| nighantu | 17 | 9 | **9** | 48 → 49 / 71 |
| roop | 23 | 10 | **10** | 72 → 72 / 99 |
| samanvaya | 10 | 2 | **2** | 24 → 24 / 27 |
| sangrah | 14 | 3 | **3** | 27 → 27 / 34 |
| sankhyiki | 16 | 1 | **1** | 34 → 34 / 41 |
| shreni | 14 | 6 | **6** | 36 → 36 / 46 |
| suchi | 34 | 11 | **8** | 65 → 66 / 83 |
| vakyank | 6 | 2 | **2** | 53 → 53 / 57 |
| varna | 27 | 10 | **8** | 111 → 111 / 126 |
| the other 9 modules | 87 | 0 | **0** | unchanged |

**The per-mutant list, with source line, verdict and reason, is in `evidence-r9/gap-list/lib-gap-list.md`.**

## Closed this round (23), and how

**By proof** (`tests/stdlib/r9_guard_cells.sm`, `r9_guard_cells2.sm`):

- Each function gets n cells and **a guard after them**. The guard holds a value that would change the
  answer if read, or that must survive.
- Every expectation was written from the contract before the run (`evidence-r9/expectations/`), and the
  compiled runs agree.

| Function | The proof |
|---|---|
| `brihat_asti_shunyank` | guard digit 5 after three 0s; must still say "zero" |
| `brihat_shunyank`, `brihat_pratilip` | guard 77 must survive |
| `brihat_nyun` | 321 − 123 = 198; a guard digit 9 would borrow; returns 0 |
| `khand_anwesh_akshar`, `khand_gan_akshar` | the byte searched for is just past n |
| `khand_asti_sarv_ank` | `0`, `9`, `/`, `:` at the ends of the digit range |
| `anukram_khip_i64` | 8 bytes exactly filling the buffer; guard byte; −2^63's sign byte |
| `mala_purn`, `mala_pratilip`, `mala_grah_surakshit` | guard 77 or 66; index = n returns 0 |
| `avali_antah` | the slot after the tail holds a value already dequeued |
| (also asserted) `brihat_gun`, `nighantu_rikta` | their documented returns (0, 1); their loop mutants remain open |

**By argument** (`tools/lib_gap_reviewed.json`, each with its reason). **These are not padding;** each says
why no input can tell the mutant apart:

| Mutant | Why it is equivalent |
|---|---|
| `khand_pratilip`, `khand_bandh`, `khand_mukt` loop `<=` | the extra write is `out[n]`, which the terminator overwrites |
| `gan_swar`, `varna_sam` loop `<=` | the extra read is the terminator, 0 |
| `brihat_ank_se_int` carry loop | carry is 0 long before j = n |
| `anukram_grah_i64` `top >= 128` → `> 128` | 128 · 2^56 wraps to −2^63, the same value. Checked with MIN. |
| `anukram_khip_i64` `val < 0` → `<= 0` | 0 % 256 is 0 |
| `avali_pravesh` growth copy | the extra cell is the tail, overwritten at once |
| `mala_nava` | since F2 (R9-03), `nirmmita(0)` is 0, which is what the mutant returns |
| `suchi_apanay` shift | LIKELY-EQ: it writes only the dead cell past the new length |

**New verdict, NO-CONTRACT (4).** The only difference is a return value that no comment promises: four
`brihat` helpers. **I did not write a proof for them,** because it would pin an implementation detail. If
you want their returns to be part of the contract, document them, and the proofs are one line each.

## Still open (68), most-used first in each module

- **aadhar** (2): `brihat_ank_tak`, `brihat_ank_se`
- **anukram** (2): `anukram_khip_ashtak`, `anukram_grah_ashtak`
- **brihat** (3): `brihat_gun`, `brihat_bhajshesh`, `brihat_shesh`
- **kalana** (5): `pravan`, `kalana_trapiz`, `simpson`, `pravan2`, `bahu_mula`
  - These take `kosh dasham`. The witness tool cannot feed them yet.
- **khand** (7): `khand_bhed`, `khand_pratisthap`, `khand_yuj`, `khand_viparyay`, `khand_unnat`,
  `khand_ant`, `khand_avanat`
- **nighantu** (9): `nighantu_anwesh`, `nighantu_vardh`, `nighantu_apanay`, `nighantu_rikta`,
  `nighantu_grah_mool`, `nighantu_kunji_gudh`, `nighantu_koshtha_likh`, `nighantu_mulya`,
  `nighantu_kunjika`
  - `nighantu_apanay` holds the one remaining GAP: a deletion whose probe chain wraps past the last slot.
- **roop** (10): all the formatting helpers. They were not reached this round.
- **samanvaya** (2): `rekha_manak`, `sadish_yoga`
- **sangrah** (3): `rakh_tak_mala`, `rakh_sampat`, `rakh_rikta`
- **sankhyiki** (1): `purna_vyapti`
- **shreni** (6): `dwi_anwesh`, `budbud_shreni`, `viparyay_mala`, `shankh_shreni`, `mil_shreni_punar`,
  `nivesh_shreni`
- **suchi** (8): `suchi_vardh`, `suchi_shreni`, `suchi_rikta`, `suchi_antah`, `suchi_kramank`,
  `suchi_viparyay`, `avali_tak_mala`, `avali_rikta`
- **vakyank** (2): `varna_tak_dashm`, `pad_vam`
- **varna** (8): `varna_bhed`, `varna_antah`, `varna_unnat`, `varna_pratisthap`, `varna_chhid`,
  `varna_viparyay`, `varna_gan`, `varna_avanat`

**What remains open:**

- **55 OVERRUN:** a loop running once more would go unnoticed.
- **56 REVIEW:** list or string arguments, not decided yet.
- **1 GAP.**

**Why fewer this round than last:**

- Most of this round went to F1's reproduction, the compiler fixes and the IDE (WS5/WS6).
- `roop` (10 functions) is the largest block left.

**One limit found while writing these:** one test file cannot import six library modules ("vistarit srot
seema atikram", the expanded-source limit), so the guard proofs are split in two. This is a capacity, not a
bug, but a program that needs `brihat`, `khand`, `anukram`, `mala`, `nighantu` and `suchi` together
cannot be written.

## Gates (branch, Linux)

| Check | Result |
|---|---|
| `proof_lib` | **209 / 209** (205 + 4 new) |
| `proof_props` | 86 / 86 |
| the gap pipeline | `evidence-r9/gap-list/`; log in `logs/lib_proof_gaps.log` |
