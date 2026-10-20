# R15-03 evidence: mutant score of every library function

303 functions · 5944 mutants besides S · 4993 killed (84.0%) · S killed in 303 of 303

| mutant kind | killed / mutants |
|---|---|
| S whole body | 303 / 303 (100%) |
| R result + 1 | 288 / 295 (98%) |
| C comparison flipped | 677 / 872 (78%) |
| N yadi negated | 462 / 479 (96%) |
| A arithmetic operator | 1044 / 1157 (90%) |
| L && / || | 17 / 18 (94%) |
| K literal + 1 | 1793 / 2299 (78%) |
| D statement deleted | 712 / 824 (86%) |

Survivors: 951 · WITNESS 23 · NO-WITNESS (likely equivalent) 110 · NOT-TRIED (lists, strings, records, or an effect in memory or a file) 818

| verdict (by the score, NO-WITNESS survivors left out) | functions |
|---|---|
| DECORATION | 0 |
| WEAK | 1 |
| PARTIAL | 60 |
| STRONG | 105 |
| COMPLETE | 137 |
| S only (no other mutant compiles) | 0 |
| NO PROOF | 0 |

Verdicts: DECORATION = the proofs kill S (the whole body broken) and no other mutant; WEAK = under 50% of the other mutants killed; PARTIAL = 50-79%; STRONG = 80-99%; COMPLETE = 100%: every mutant killed, or the survivors have no witness. A surviving mutant may be equivalent (no input can tell it apart); see R15-03 for what that means for the ranking.

## Ranked, weakest first

| rank | function | killed / mutants | score | verdict | survivors W / NW / NT | surviving mutants (first 6) | proofs that name it |
|---|---|---|---|---|---|---|---|
| 1 | `ganita.chakravala` | 31 / 63 | 49% | WEAK | 0 / 0 / 32 | C5:<-><=@L108 C6:!=->==@L108 C7:<-><=@L113 C8:>=->>@L115 C9:<=-><@L115 C10:<-><=@L121 … | 6 |
| 2 | `suchi.avali_srij` | 18 / 36 | 50% | PARTIAL | 2 / 0 / 16 | C1:<-><=@L382 C2:<-><=@L384 K:0@L379 K:0@L380 K:0@L381 K:1@L382 … | 15 |
| 3 | `nighantu.nighantu_kunji_gudh` | 3 / 6 | 50% | PARTIAL | 0 / 0 / 3 | C1:<-><=@L39 K:1@L39 K:0@L39 | 0 |
| 4 | `sangrah.rakh_yuj` | 1 / 2 | 50% | PARTIAL | 0 / 0 / 1 | K:1@L43 | 22 |
| 5 | `roop.roop_pad_dakshin` | 17 / 33 | 52% | PARTIAL | 0 / 0 / 16 | C1:<=-><@L276 C2:<-><=@L278 C3:<-><=@L287 C4:<-><=@L292 K:0@L274 K:0@L275 … | 2 |
| 6 | `nighantu.nighantu_srij` | 21 / 40 | 52% | PARTIAL | 0 / 0 / 19 | C1:<-><=@L112 C2:<-><=@L114 C4:<-><=@L119 K:0@L109 K:0@L110 K:0@L111 … | 26 |
| 7 | `suchi.suchi_srij` | 18 / 33 | 55% | PARTIAL | 1 / 0 / 14 | C1:<-><=@L51 C2:<-><=@L53 K:0@L48 K:0@L49 K:0@L50 K:1@L51 … | 23 |
| 8 | `khand.khand_bandh` | 9 / 16 | 56% | PARTIAL | 0 / 0 / 7 | C1:<=-><@L44 C2:<-><=@L48 K:0@L45 K:0@L45 D@L45 K:0@L52 … | 6 |
| 9 | `patra.patra_likh_sarv` | 17 / 30 | 57% | PARTIAL | 0 / 0 / 13 | C2:<-><=@L65 C4:<=-><@L68 K:0@L61 K:577@L64 K:0@L65 A:+@L67 … | 1 |
| 10 | `mala.mala_nava` | 4 / 7 | 57% | PARTIAL | 0 / 0 / 3 | C1:<-><=@L13 K:8@L11 K:0@L13 | 10 |
| 11 | `suchi.suchi_vardh` | 13 / 22 | 59% | PARTIAL | 0 / 0 / 9 | R C2:<-><=@L73 A:*@L68 K:2@L68 A:*@L69 K:0@L72 … | 0 |
| 12 | `roop.roop_pad_madhya` | 28 / 46 | 61% | PARTIAL | 0 / 0 / 18 | C1:<=-><@L311 C2:<-><=@L313 C3:<-><=@L323 C4:<-><=@L328 C5:<-><=@L333 K:0@L308 … | 2 |
| 13 | `anukram.anukram_grah_ashtak` | 20 / 32 | 62% | PARTIAL | 0 / 0 / 12 | A:-@L117 A:-@L117 K:0@L117 K:1@L117 K:0@L117 K:1@L117 … | 3 |
| 14 | `roop.roop_pad_vam` | 21 / 33 | 64% | PARTIAL | 0 / 0 / 12 | C1:<=-><@L243 C2:<-><=@L245 C3:<-><=@L254 C4:<-><=@L259 K:0@L241 K:0@L242 … | 2 |
| 15 | `phal.phal_janchit_shesh` | 7 / 11 | 64% | PARTIAL | 0 / 0 / 4 | K:1@L150 K:0@L150 D@L150 K:0@L152 | 3 |
| 16 | `suchi.suchi_adhik` | 9 / 14 | 64% | PARTIAL | 0 / 0 / 5 | K:0@L232 D@L232 K:0@L235 D@L235 K:0@L236 | 3 |
| 17 | `patra.patra_path_sarv` | 22 / 34 | 65% | PARTIAL | 0 / 0 / 12 | C2:<-><=@L37 C3:<-><=@L38 K:0@L33 K:0@L37 A:+@L39 A:-@L39 … | 2 |
| 18 | `roop.roop_sign_akshar` | 22 / 34 | 65% | PARTIAL | 0 / 0 / 12 | C2:<-><=@L610 C3:<-><=@L619 K:0@L605 K:0@L606 D@L609 K:1@L612 … | 2 |
| 19 | `roop.roop_chinhit` | 23 / 35 | 66% | PARTIAL | 0 / 0 / 12 | C2:<-><=@L580 C3:<-><=@L589 K:0@L575 K:0@L576 D@L579 K:1@L582 … | 2 |
| 20 | `sankhyiki.purna_vyapti` | 4 / 6 | 67% | PARTIAL | 0 / 0 / 2 | C1:<=-><@L175 K:0@L175 | 2 |
| 21 | `shreni.mil_shreni` | 2 / 3 | 67% | PARTIAL | 0 / 0 / 1 | A:*@L213 | 4 |
| 22 | `suchi.suchi_anwesh` | 2 / 3 | 67% | PARTIAL | 0 / 0 / 1 | K:0@L257 | 3 |
| 23 | `suchi.suchi_gan` | 2 / 3 | 67% | PARTIAL | 0 / 0 / 1 | K:0@L250 | 2 |
| 24 | `suchi.suchi_yog` | 2 / 3 | 67% | PARTIAL | 0 / 0 / 1 | K:0@L243 | 2 |
| 25 | `brihat.brihat_ank_se_int` | 34 / 50 | 68% | PARTIAL | 0 / 0 / 16 | C2:<-><=@L39 C6:<-><=@L50 A:-@L39 K:0@L39 A:+@L52 K:8@L52 … | 20 |
| 26 | `khand.khand_viparyay` | 26 / 38 | 68% | PARTIAL | 0 / 0 / 12 | C1:<=-><@L469 C2:<-><=@L475 K:0@L466 K:0@L467 K:0@L468 K:0@L469 … | 2 |
| 27 | `varna.varna_viparyay` | 26 / 38 | 68% | PARTIAL | 0 / 0 / 12 | C1:<=-><@L496 C2:<-><=@L502 K:0@L493 K:0@L494 K:0@L495 K:0@L496 … | 2 |
| 28 | `khand.khand_mukt` | 11 / 16 | 69% | PARTIAL | 0 / 0 / 5 | C1:<=-><@L66 C2:<-><=@L70 K:0@L67 K:0@L67 D@L67 | 2 |
| 29 | `khand.khand_pratilip` | 11 / 16 | 69% | PARTIAL | 0 / 0 / 5 | C1:<=-><@L86 C2:<-><=@L90 K:0@L87 D@L87 D@L94 | 6 |
| 30 | `khand.khand_avanat` | 18 / 26 | 69% | PARTIAL | 0 / 0 / 8 | C1:<-><=@L384 C2:<-><=@L388 K:0@L383 K:0@L384 K:0@L385 D@L385 … | 4 |
| 31 | `khand.khand_unnat` | 18 / 26 | 69% | PARTIAL | 0 / 0 / 8 | C1:<-><=@L362 C2:<-><=@L366 K:0@L361 K:0@L362 K:0@L363 D@L363 … | 4 |
| 32 | `nighantu.nighantu_antah` | 7 / 10 | 70% | PARTIAL | 0 / 0 / 3 | C1:>->>=@L170 K:32@L170 K:32@L170 | 6 |
| 33 | `varna.varna_avanat` | 17 / 24 | 71% | PARTIAL | 0 / 0 / 7 | C1:<-><=@L416 C2:<-><=@L420 K:0@L416 K:0@L417 D@L417 K:0@L428 … | 4 |
| 34 | `varna.varna_unnat` | 17 / 24 | 71% | PARTIAL | 0 / 0 / 7 | C1:<-><=@L395 C2:<-><=@L399 K:0@L395 K:0@L396 D@L396 K:0@L407 … | 4 |
| 35 | `roop.roop_ank_aadhar` | 37 / 52 | 71% | PARTIAL | 0 / 0 / 15 | C4:<-><=@L91 C6:<-><=@L99 A:*@L73 K:0@L75 K:0@L77 K:0@L79 … | 4 |
| 36 | `ganita.ganita_janchit_nyun` | 20 / 28 | 71% | PARTIAL | 0 / 0 / 8 | C2:<-><=@L248 C3:<-><=@L249 C4:>=->>@L255 C5:>=->>@L256 K:0@L248 K:0@L249 … | 6 |
| 37 | `sangrah.rakh_tak_mala` | 34 / 47 | 72% | PARTIAL | 0 / 0 / 13 | C2:<-><=@L244 C3:<-><=@L254 C5:>->>=@L257 A:*@L222 A:+@L222 A:*@L224 … | 9 |
| 38 | `vakyank.ank_tak_aadhar_varna` | 34 / 47 | 72% | PARTIAL | 0 / 0 / 13 | A:*@L141 D@L144 K:0@L144 K:0@L144 D@L148 K:0@L148 … | 5 |
| 39 | `suchi.avali_pravesh` | 32 / 44 | 73% | PARTIAL | 0 / 0 / 12 | C3:<-><=@L414 K:0@L401 K:0@L402 K:0@L403 K:0@L404 K:0@L405 … | 13 |
| 40 | `phal.phal_janchit_bhaj` | 8 / 11 | 73% | PARTIAL | 0 / 0 / 3 | K:1@L136 K:0@L136 D@L136 | 3 |
| 41 | `phal.phal_janchit_ghat` | 8 / 11 | 73% | PARTIAL | 0 / 0 / 3 | K:1@L163 K:0@L163 D@L163 | 2 |
| 42 | `phal.phal_janchit_gun` | 8 / 11 | 73% | PARTIAL | 0 / 0 / 3 | K:1@L122 K:0@L122 D@L122 | 5 |
| 43 | `phal.phal_janchit_kramgun` | 8 / 11 | 73% | PARTIAL | 0 / 0 / 3 | K:1@L176 K:0@L176 D@L176 | 2 |
| 44 | `phal.phal_janchit_nirapeksh` | 8 / 11 | 73% | PARTIAL | 0 / 0 / 3 | K:1@L189 K:0@L189 D@L189 | 2 |
| 45 | `phal.phal_janchit_nyun` | 8 / 11 | 73% | PARTIAL | 0 / 0 / 3 | K:1@L108 K:0@L108 D@L108 | 3 |
| 46 | `nighantu.nighantu_grah_mool` | 11 / 15 | 73% | PARTIAL | 0 / 0 / 4 | C1:>->>=@L312 K:0@L311 K:32@L312 K:32@L312 | 3 |
| 47 | `kalana.simpson` | 34 / 46 | 74% | PARTIAL | 0 / 0 / 12 | C1:<-><=@L35 N@L35 A:*@L38 A:-@L38 A:-@L38 A:/@L38 … | 2 |
| 48 | `roop.roop_ank` | 34 / 46 | 74% | PARTIAL | 0 / 0 / 12 | C2:<-><=@L42 A:*@L34 K:0@L36 D@L39 K:1@L39 K:0@L42 … | 1 |
| 49 | `vakyank.varna_tak_dashm` | 63 / 84 | 75% | PARTIAL | 0 / 0 / 21 | C20:<-><=@L325 C24:==->!=@L344 C25:<-><=@L352 C27:>=->>@L358 C31:<-><=@L374 C36:>->>=@L397 … | 4 |
| 50 | `sankhyiki.adhikatama` | 9 / 12 | 75% | PARTIAL | 0 / 0 / 3 | C3:>->>=@L53 K:0@L49 K:1@L54 | 2 |
| 51 | `sankhyiki.laghutama` | 9 / 12 | 75% | PARTIAL | 0 / 0 / 3 | C3:<-><=@L40 K:0@L36 K:1@L41 | 2 |
| 52 | `ank.seemit` | 3 / 5 | 75% | PARTIAL | 1 / 1 / 0 | C1:<-><=@L65 C2:>->>=@L66 | 2 |
| 53 | `ganit.ganit_seemit` | 3 / 5 | 75% | PARTIAL | 1 / 1 / 0 | C1:<-><=@L161 C2:>->>=@L162 | 2 |
| 54 | `varna.varna_tul` | 19 / 25 | 76% | PARTIAL | 0 / 0 / 6 | C1:<-><=@L473 K:0@L471 N@L473 K:1@L476 K:1@L477 K:1@L480 | 2 |
| 55 | `kalana.bahu_mula` | 26 / 34 | 76% | PARTIAL | 0 / 0 / 8 | C3:<-><=@L124 C5:<-><=@L124 C8:<-><=@L132 C10:<-><=@L132 K:0@L122 K:0@L123 … | 3 |
| 56 | `brihat.brihat_ghatmod` | 17 / 22 | 77% | PARTIAL | 0 / 0 / 5 | R A:*@L316 A:*@L316 A:*@L317 K:0@L329 | 3 |
| 57 | `nighantu.nighantu_grah` | 14 / 18 | 78% | PARTIAL | 0 / 0 / 4 | C1:>->>=@L161 K:0@L160 K:32@L161 K:32@L161 | 17 |
| 58 | `ganita.ganita_janchit_yuj` | 22 / 28 | 79% | PARTIAL | 0 / 0 / 6 | C1:>=->>@L221 C2:>=->>@L222 C4:<-><=@L229 K:0@L221 K:0@L222 K:0@L229 | 6 |
| 59 | `roop.roop_ank_aadhar2` | 22 / 28 | 79% | PARTIAL | 0 / 0 / 6 | K:0@L145 A:-@L148 D@L148 K:0@L152 K:0@L152 D@L152 | 4 |
| 60 | `shreni.dwi_anwesh` | 15 / 19 | 79% | PARTIAL | 0 / 0 / 4 | C3:<-><=@L106 K:0@L101 A:-@L102 K:1@L106 | 3 |
| 61 | `varna.varna_gan` | 19 / 24 | 79% | PARTIAL | 0 / 0 / 5 | K:0@L527 K:0@L528 A:-@L529 A:-@L530 A:+@L533 | 4 |
| 62 | `samanvaya.matrika_yoga` | 8 / 10 | 80% | STRONG | 0 / 0 / 2 | A:*@L55 A:*@L59 | 1 |
| 63 | `samanvaya.skalar` | 8 / 10 | 80% | STRONG | 0 / 0 / 2 | A:*@L65 A:*@L69 | 1 |
| 64 | `sangrah.rakh_sangam` | 33 / 41 | 80% | STRONG | 0 / 0 / 8 | A:*@L105 A:+@L105 A:*@L106 A:+@L106 K:0@L111 K:1@L114 … | 2 |
| 65 | `varna.varna_chhid` | 33 / 41 | 80% | STRONG | 0 / 0 / 8 | C2:>=->>@L361 C5:<=-><@L370 K:0@L362 D@L362 K:0@L371 D@L371 … | 2 |
| 66 | `anukram.anukram_grah_i64` | 34 / 42 | 81% | STRONG | 0 / 0 / 8 | C4:>=->>@L77 A:-@L66 K:0@L66 K:1@L66 N@L77 K:128@L77 … | 3 |
| 67 | `vakyank.varna_tak_ank` | 43 / 53 | 81% | STRONG | 0 / 0 / 10 | D@L94 K:0@L94 K:0@L95 D@L102 K:0@L102 K:0@L102 … | 5 |
| 68 | `suchi.avali_avalok` | 13 / 16 | 81% | STRONG | 0 / 0 / 3 | K:0@L452 K:0@L454 D@L454 | 4 |
| 69 | `nighantu.nighantu_vardh` | 35 / 43 | 81% | STRONG | 0 / 0 / 8 | K:0@L281 K:0@L282 K:0@L283 K:0@L284 K:0@L287 K:0@L288 … | 3 |
| 70 | `khand.khand_gan_swar` | 22 / 27 | 81% | STRONG | 0 / 0 / 5 | K:0@L519 K:0@L521 K:97@L524 K:105@L524 K:117@L524 | 4 |
| 71 | `aadhar.brihat_ank_tak` | 40 / 49 | 82% | STRONG | 0 / 0 / 9 | K:0@L25 K:16@L25 K:1@L32 D@L33 K:0@L33 K:0@L33 … | 5 |
| 72 | `khand.khand_anwesh_akshar` | 9 / 11 | 82% | STRONG | 0 / 0 / 2 | K:0@L554 K:1@L557 | 5 |
| 73 | `samanvaya.sadish_yoga` | 9 / 11 | 82% | STRONG | 0 / 0 / 2 | C1:<-><=@L119 N@L119 | 1 |
| 74 | `suchi.avali_rikta` | 14 / 17 | 82% | STRONG | 0 / 0 / 3 | K:3@L509 K:0@L509 D@L509 | 4 |
| 75 | `varna.varna_aadi` | 14 / 17 | 82% | STRONG | 0 / 0 / 3 | K:0@L442 K:0@L444 K:1@L445 | 3 |
| 76 | `khand.khand_bhed` | 44 / 53 | 83% | STRONG | 0 / 0 / 9 | K:0@L211 K:0@L212 K:0@L213 K:0@L217 K:0@L218 K:0@L219 … | 5 |
| 77 | `nighantu.nighantu_anwesh` | 35 / 42 | 83% | STRONG | 0 / 0 / 7 | C3:>->>=@L91 K:0@L87 K:0@L88 K:32@L91 K:32@L91 K:1@L98 … | 1 |
| 78 | `suchi.suchi_apanay` | 25 / 30 | 83% | STRONG | 0 / 0 / 5 | C3:<-><=@L157 K:0@L151 K:0@L152 A:-@L157 K:0@L157 | 6 |
| 79 | `suchi.chay_avalok` | 15 / 18 | 83% | STRONG | 0 / 0 / 3 | K:0@L347 K:0@L349 D@L349 | 3 |
| 80 | `sadhan.util_chinha` | 5 / 6 | 83% | STRONG | 1 / 0 / 0 | K:0@L44 | 1 |
| 81 | `khand.khand_tul` | 26 / 31 | 84% | STRONG | 0 / 0 / 5 | C1:<-><=@L444 K:0@L440 K:0@L441 K:0@L442 N@L444 | 5 |
| 82 | `sangrah.rakh_samroop_diff` | 38 / 45 | 84% | STRONG | 0 / 0 / 7 | A:*@L69 A:+@L69 A:*@L70 A:+@L70 K:0@L75 K:1@L79 … | 3 |
| 83 | `shreni.adhik` | 11 / 13 | 85% | STRONG | 0 / 0 / 2 | C3:>->>=@L56 K:1@L53 | 4 |
| 84 | `shreni.laghu` | 11 / 13 | 85% | STRONG | 0 / 0 / 2 | C3:<-><=@L44 K:1@L45 | 4 |
| 85 | `varna.varna_sam` | 11 / 13 | 85% | STRONG | 0 / 0 / 2 | C2:<-><=@L117 K:0@L116 | 1 |
| 86 | `nighantu.nighantu_apanay` | 45 / 53 | 85% | STRONG | 0 / 0 / 8 | C1:>->>=@L192 C7:<=-><@L210 C9:<=-><@L216 K:0@L186 K:0@L187 K:0@L188 … | 4 |
| 87 | `samanvaya.rekha_manak` | 17 / 20 | 85% | STRONG | 0 / 0 / 3 | C3:<-><=@L138 C4:>->>=@L142 K:0@L132 | 2 |
| 88 | `sankhyiki.purna_prasaran` | 17 / 20 | 85% | STRONG | 0 / 0 / 3 | K:0@L182 K:0@L185 K:0@L186 | 2 |
| 89 | `sangrah.rakh_bhed` | 23 / 27 | 85% | STRONG | 0 / 0 / 4 | A:*@L155 A:+@L155 K:0@L159 K:1@L163 | 2 |
| 90 | `sangrah.rakh_sampat` | 23 / 27 | 85% | STRONG | 0 / 0 / 4 | A:*@L134 A:+@L134 K:0@L138 K:1@L142 | 3 |
| 91 | `roop.roop_varg_mool` | 47 / 55 | 85% | STRONG | 0 / 0 / 8 | C4:<-><=@L365 C12:>->>=@L398 K:0@L352 K:0@L358 K:0@L358 K:0@L362 … | 0 |
| 92 | `vakyank.pad_vam` | 18 / 21 | 86% | STRONG | 0 / 0 / 3 | A:-@L237 K:0@L248 D@L248 | 3 |
| 93 | `brihat.brihat_pratilip` | 12 / 14 | 86% | STRONG | 0 / 0 / 2 | R K:0@L91 | 2 |
| 94 | `shreni.asti_sorted` | 12 / 14 | 86% | STRONG | 0 / 0 / 2 | K:1@L93 K:1@L95 | 4 |
| 95 | `suchi.avali_shunya` | 6 / 7 | 86% | STRONG | 0 / 0 / 1 | K:0@L516 | 3 |
| 96 | `suchi.chay_rikta` | 6 / 7 | 86% | STRONG | 0 / 0 / 1 | K:0@L360 | 2 |
| 97 | `khand.khand_pratisthap` | 43 / 50 | 86% | STRONG | 0 / 0 / 7 | K:0@L152 K:0@L153 D@L163 K:0@L163 A:+@L168 D@L191 … | 6 |
| 98 | `nighantu.nighantu_rikta` | 37 / 43 | 86% | STRONG | 0 / 0 / 6 | K:0@L251 K:0@L252 K:0@L253 K:2@L256 K:2@L258 A:+@L262 | 4 |
| 99 | `chandas.meru` | 19 / 23 | 86% | STRONG | 3 / 1 / 0 | C3:>->>=@L29 K:0@L27 N@L29 A:-@L29 | 3 |
| 100 | `khand.khand_gan` | 19 / 22 | 86% | STRONG | 0 / 0 / 3 | K:0@L500 A:-@L502 A:-@L503 | 3 |
| 101 | `suchi.suchi_nivesh` | 32 / 37 | 86% | STRONG | 0 / 0 / 5 | K:0@L128 K:0@L129 K:1@L132 K:0@L133 K:0@L136 | 4 |
| 102 | `khand.khand_chhid` | 39 / 45 | 87% | STRONG | 0 / 0 / 6 | C2:>=->>@L329 C5:<=-><@L337 K:0@L324 K:0@L327 K:0@L349 D@L349 | 2 |
| 103 | `nighantu.nighantu_mil` | 26 / 30 | 87% | STRONG | 0 / 0 / 4 | A:*@L331 A:+@L331 K:0@L335 K:0@L337 | 3 |
| 104 | `sankhyiki.purna_adhikatama` | 13 / 15 | 87% | STRONG | 0 / 0 / 2 | C3:>->>=@L167 K:0@L162 | 2 |
| 105 | `sankhyiki.purna_laghutama` | 13 / 15 | 87% | STRONG | 0 / 0 / 2 | C3:<-><=@L154 K:0@L149 | 2 |
| 106 | `varna.asti_sarv_ank` | 13 / 15 | 87% | STRONG | 0 / 0 / 2 | K:0@L92 K:1@L95 | 3 |
| 107 | `madhava.madhava_cos` | 20 / 28 | 87% | STRONG | 3 / 5 / 0 | C1:>->>=@L75 C2:<-><=@L76 C3:<-><=@L80 N@L75 N@L76 A:-@L76 … | 3 |
| 108 | `madhava.madhava_sin` | 20 / 28 | 87% | STRONG | 3 / 5 / 0 | C1:>->>=@L55 C2:<-><=@L56 C3:<-><=@L60 N@L55 N@L56 A:-@L56 … | 3 |
| 109 | `sangrah.rakh_asti_upasamuh` | 20 / 23 | 87% | STRONG | 0 / 0 / 3 | A:*@L200 A:+@L200 K:0@L204 | 2 |
| 110 | `ganita.ganita_janchit_gun` | 42 / 48 | 88% | STRONG | 0 / 0 / 6 | K:0@L276 D@L280 K:0@L280 K:1@L280 K:0@L284 K:1@L284 | 6 |
| 111 | `khand.khand_yuj` | 35 / 40 | 88% | STRONG | 0 / 0 / 5 | K:0@L290 K:0@L291 K:0@L292 K:1@L307 D@L312 | 3 |
| 112 | `nighantu.nighantu_koshtha_likh` | 35 / 40 | 88% | STRONG | 0 / 0 / 5 | R K:0@L73 D@L73 K:1@L74 K:1@L76 | 0 |
| 113 | `shreni.mil_shreni_punar` | 44 / 50 | 88% | STRONG | 0 / 0 / 6 | R C8:<-><=@L193 K:0@L165 K:1@L181 K:1@L184 K:0@L209 | 0 |
| 114 | `suchi.suchi_vinimay` | 22 / 25 | 88% | STRONG | 0 / 0 / 3 | K:0@L173 K:0@L174 K:0@L177 | 4 |
| 115 | `khand.khand_aadi` | 15 / 17 | 88% | STRONG | 0 / 0 / 2 | K:0@L408 K:1@L413 | 3 |
| 116 | `khand.khand_anwesh` | 39 / 44 | 89% | STRONG | 0 / 0 / 5 | K:0@L109 K:0@L110 K:0@L111 D@L115 A:-@L116 | 3 |
| 117 | `roop.roop_ank_dhvaj` | 47 / 53 | 89% | STRONG | 0 / 0 / 6 | K:0@L173 K:0@L174 A:-@L177 D@L187 K:0@L187 K:0@L188 | 5 |
| 118 | `vakyank.varna_tak_ank_aadhar` | 48 / 54 | 89% | STRONG | 0 / 0 / 6 | D@L184 K:0@L184 K:0@L185 K:1@L191 K:57@L193 K:102@L196 | 5 |
| 119 | `suchi.suchi_viparyay` | 16 / 18 | 89% | STRONG | 0 / 0 / 2 | C1:<-><=@L195 K:0@L194 | 3 |
| 120 | `roop.roop_sthir_mool` | 49 / 55 | 89% | STRONG | 0 / 0 / 6 | C1:<-><=@L471 C2:>->>=@L472 K:0@L465 K:0@L506 D@L529 D@L553 | 1 |
| 121 | `shreni.nivesh_shreni` | 25 / 28 | 89% | STRONG | 0 / 0 / 3 | C4:>->>=@L150 K:1@L148 K:1@L154 | 5 |
| 122 | `shreni.shankh_shreni` | 25 / 28 | 89% | STRONG | 0 / 0 / 3 | C5:>->>=@L121 A:/@L112 K:2@L112 | 2 |
| 123 | `khand.khand_ant` | 17 / 19 | 89% | STRONG | 0 / 0 / 2 | K:0@L423 K:1@L428 | 4 |
| 124 | `varna.varna_ant` | 17 / 19 | 89% | STRONG | 0 / 0 / 2 | K:0@L457 K:1@L460 | 3 |
| 125 | `anukram.anukram_khip_ashtak` | 26 / 29 | 90% | STRONG | 0 / 0 / 3 | A:-@L95 K:0@L95 K:1@L95 | 3 |
| 126 | `varna.varna_pratisthap` | 45 / 50 | 90% | STRONG | 0 / 0 / 5 | K:0@L186 D@L194 A:+@L200 D@L223 K:0@L223 | 4 |
| 127 | `suchi.avali_nishkas` | 27 / 30 | 90% | STRONG | 0 / 0 / 3 | K:0@L434 K:0@L435 K:1@L442 | 11 |
| 128 | `ganita.ganita_janchit_nirapeksh` | 18 / 20 | 90% | STRONG | 0 / 0 / 2 | C2:<-><=@L542 K:0@L542 | 5 |
| 129 | `khand.khand_asti_sarv_ank` | 18 / 20 | 90% | STRONG | 0 / 0 / 2 | K:0@L569 K:0@L570 | 6 |
| 130 | `samanvaya.pehchan` | 18 / 20 | 90% | STRONG | 0 / 0 / 2 | A:*@L29 D@L29 | 2 |
| 131 | `shreni.budbud_shreni` | 18 / 20 | 90% | STRONG | 0 / 0 / 2 | C1:<-><=@L15 C3:>->>=@L18 | 3 |
| 132 | `nighantu.nighantu_kunjika` | 39 / 43 | 91% | STRONG | 0 / 0 / 4 | K:0@L385 K:0@L386 A:+@L390 K:32@L390 | 4 |
| 133 | `khand.khand_gan_akshar` | 10 / 11 | 91% | STRONG | 0 / 0 / 1 | K:0@L539 | 4 |
| 134 | `sankhyiki.bindu` | 10 / 11 | 91% | STRONG | 0 / 0 / 1 | C1:<-><=@L103 | 3 |
| 135 | `shreni.anwesh_sarak` | 10 / 11 | 91% | STRONG | 0 / 0 / 1 | K:0@L73 | 3 |
| 136 | `shreni.viparyay_mala` | 10 / 11 | 91% | STRONG | 0 / 0 / 1 | C1:<-><=@L30 | 2 |
| 137 | `varna.gan_akshar` | 10 / 11 | 91% | STRONG | 0 / 0 / 1 | K:0@L70 | 4 |
| 138 | `kalana.kalana_trapiz` | 21 / 23 | 91% | STRONG | 0 / 0 / 2 | C1:<-><=@L19 N@L19 | 2 |
| 139 | `suchi.chay_apanay` | 21 / 23 | 91% | STRONG | 0 / 0 / 2 | K:0@L330 K:0@L331 | 3 |
| 140 | `brihat.brihat_shesh` | 44 / 48 | 92% | STRONG | 0 / 0 / 4 | R A:*@L271 K:1@L273 K:1@L276 | 2 |
| 141 | `suchi.suchi_sangrah` | 11 / 12 | 92% | STRONG | 0 / 0 / 1 | K:0@L110 | 2 |
| 142 | `varna.varna_yuj` | 35 / 38 | 92% | STRONG | 0 / 0 / 3 | K:1@L343 K:0@L348 D@L348 | 2 |
| 143 | `anukram.anukram_khip_i64` | 37 / 40 | 92% | STRONG | 0 / 0 / 3 | C4:<-><=@L49 K:0@L49 A:-@L52 | 3 |
| 144 | `madhava.madhava_atan` | 38 / 47 | 93% | STRONG | 3 / 6 / 0 | C1:<-><=@L98 C4:<-><=@L112 C5:>->>=@L114 N@L98 A:-@L104 K:1@L104 … | 3 |
| 145 | `varna.varna_bhed` | 51 / 55 | 93% | STRONG | 0 / 0 / 4 | C13:>=->>@L305 K:0@L265 K:0@L267 K:1@L310 | 5 |
| 146 | `ganita.ganita_janchit_shesh` | 26 / 28 | 93% | STRONG | 0 / 0 / 2 | K:0@L338 D@L338 | 5 |
| 147 | `kalana.pravan` | 26 / 28 | 93% | STRONG | 0 / 0 / 2 | C1:<-><=@L60 N@L60 | 4 |
| 148 | `sankhyiki.prasaran` | 13 / 14 | 93% | STRONG | 0 / 0 / 1 | K:0@L67 | 3 |
| 149 | `nighantu.nighantu_kunjika_ashtak` | 41 / 44 | 93% | STRONG | 0 / 0 / 3 | K:0@L418 K:0@L419 K:0@L420 | 5 |
| 150 | `ganita.brahmagupta_kshetr` | 14 / 17 | 93% | STRONG | 1 / 2 / 0 | C1:<-><=@L176 K:0@L176 K:0@L176 | 4 |
| 151 | `ganita.ganita_paripurna_kramgun` | 14 / 15 | 93% | STRONG | 1 / 0 / 0 | K:9223372036854775807@L565 | 5 |
| 152 | `ganita.kuttaka` | 30 / 35 | 94% | STRONG | 2 / 3 / 0 | C3:<-><=@L35 C4:>->>=@L36 K:0@L31 K:0@L35 K:0@L36 | 5 |
| 153 | `nighantu.nighantu_khip` | 45 / 48 | 94% | STRONG | 0 / 0 / 3 | C3:>->>=@L138 K:0@L133 K:0@L134 | 25 |
| 154 | `kalana.bahu_ganana` | 15 / 16 | 94% | STRONG | 0 / 0 / 1 | K:0@L103 | 2 |
| 155 | `brihat.brihat_bhajshesh` | 46 / 49 | 94% | STRONG | 0 / 0 / 3 | R A:+@L204 K:0@L217 | 5 |
| 156 | `kalana.pravan2` | 32 / 34 | 94% | STRONG | 0 / 0 / 2 | C1:<-><=@L80 N@L80 | 4 |
| 157 | `suchi.suchi_khip` | 16 / 17 | 94% | STRONG | 0 / 0 / 1 | K:0@L87 | 18 |
| 158 | `ank.ank_gan` | 20 / 23 | 95% | STRONG | 1 / 2 / 0 | C2:<-><=@L16 K:0@L16 K:0@L16 | 4 |
| 159 | `brihat.brihat_tul` | 20 / 21 | 95% | STRONG | 0 / 0 / 1 | K:1@L99 | 7 |
| 160 | `brihat.brihat_gun` | 42 / 44 | 95% | STRONG | 0 / 0 / 2 | A:*@L159 A:+@L174 | 5 |
| 161 | `vakyank.ank_tak_varna` | 45 / 47 | 96% | STRONG | 0 / 0 / 2 | A:*@L50 K:0@L72 | 7 |
| 162 | `nighantu.nighantu_kunji_sam` | 23 / 24 | 96% | STRONG | 0 / 0 / 1 | K:0@L48 | 0 |
| 163 | `varna.gan_swar` | 24 / 25 | 96% | STRONG | 0 / 0 / 1 | C1:<-><=@L58 | 4 |
| 164 | `samanvaya.matrika_gunana` | 26 / 27 | 96% | STRONG | 0 / 0 / 1 | A:*@L89 | 2 |
| 165 | `aadhar.brihat_ank_se` | 35 / 36 | 97% | STRONG | 0 / 0 / 1 | K:0@L82 | 4 |
| 166 | `varna.varna_anwesh` | 37 / 38 | 97% | STRONG | 0 / 0 / 1 | A:-@L149 | 3 |
| 167 | `ganita.ganita_paripurna_gun` | 35 / 49 | 100% | COMPLETE | 0 / 14 / 0 | C6:==->!=@L400 C8:<-><=@L404 C9:<-><=@L405 K:0@L392 K:0@L397 K:1@L397 … | 5 |
| 168 | `ganita.ganita_paripurna_nyun` | 15 / 23 | 100% | COMPLETE | 0 / 8 / 0 | C2:<-><=@L374 C3:<-><=@L375 C4:>=->>@L378 C5:>=->>@L379 K:0@L374 K:0@L375 … | 5 |
| 169 | `ganita.ganita_vargmool` | 22 / 29 | 100% | COMPLETE | 0 / 7 / 0 | C1:<-><=@L46 K:0@L46 K:1@L53 K:2@L54 K:1@L54 K:1@L55 … | 5 |
| 170 | `ganita.ganita_paripurna_ghat` | 34 / 40 | 100% | COMPLETE | 0 / 6 / 0 | C4:>->>=@L480 C7:>->>=@L485 K:0@L480 A:-@L481 K:0@L485 A:-@L486 | 5 |
| 171 | `ganita.ganita_paripurna_yuj` | 17 / 23 | 100% | COMPLETE | 0 / 6 / 0 | C1:>=->>@L354 C2:>=->>@L355 C4:<-><=@L359 K:0@L354 K:0@L355 K:0@L359 | 5 |
| 172 | `madhava.madhava_vargmool` | 9 / 15 | 100% | COMPLETE | 0 / 6 / 0 | C1:<=-><@L14 C2:<-><=@L16 C3:<-><=@L18 N@L16 K:0@L17 K:1000@L18 | 3 |
| 173 | `ank.asti_sampurna` | 19 / 24 | 100% | COMPLETE | 0 / 5 / 0 | C1:<-><=@L87 C2:<=-><@L93 K:2@L87 A:/@L96 K:1@L98 | 4 |
| 174 | `madhava.madhava_pi` | 20 / 25 | 100% | COMPLETE | 0 / 5 / 0 | C1:<-><=@L32 C2:>->>=@L34 K:1@L31 K:30@L32 K:0@L40 | 3 |
| 175 | `sadhan.bhaj_urdhva` | 18 / 23 | 100% | COMPLETE | 0 / 5 / 0 | C3:>->>=@L34 C4:>->>=@L35 C5:<-><=@L37 K:0@L35 K:0@L37 | 2 |
| 176 | `sankhyiki.sankhyiki_vargmool` | 9 / 13 | 100% | COMPLETE | 0 / 4 / 0 | C2:<-><=@L86 K:0@L85 K:1000@L86 K:1@L88 | 2 |
| 177 | `ank.ank_yog` | 22 / 24 | 100% | COMPLETE | 0 / 2 / 0 | C2:<-><=@L30 K:0@L30 | 3 |
| 178 | `ank.collatz_charan` | 29 / 31 | 100% | COMPLETE | 0 / 2 / 0 | C4:>->>=@L114 K:3074457345618258602@L114 | 4 |
| 179 | `ganit.laghuttam` | 10 / 12 | 100% | COMPLETE | 0 / 2 / 0 | C2:<-><=@L64 K:0@L64 | 5 |
| 180 | `ganit.mahattam` | 9 / 11 | 100% | COMPLETE | 0 / 2 / 0 | C2:<-><=@L51 K:0@L51 | 6 |
| 181 | `ganit.nirapeksh_mulya` | 5 / 7 | 100% | COMPLETE | 0 / 2 / 0 | C1:<-><=@L19 K:0@L19 | 3 |
| 182 | `ganita.ganita_nirapeksh` | 4 / 6 | 100% | COMPLETE | 0 / 2 / 0 | C1:<-><=@L70 K:0@L70 | 2 |
| 183 | `ganita.ganita_paripurna_nirapeksh` | 12 / 14 | 100% | COMPLETE | 0 / 2 / 0 | C2:<-><=@L553 K:0@L553 | 5 |
| 184 | `chandas.matra_meru` | 18 / 19 | 100% | COMPLETE | 0 / 1 / 0 | K:1@L42 | 3 |
| 185 | `ganit.adhik2` | 2 / 3 | 100% | COMPLETE | 0 / 1 / 0 | C1:>->>=@L35 | 2 |
| 186 | `ganit.laghu2` | 2 / 3 | 100% | COMPLETE | 0 / 1 / 0 | C1:<-><=@L28 | 2 |
| 187 | `ganit.yog_tak` | 19 / 20 | 100% | COMPLETE | 0 / 1 / 0 | C1:<=-><@L115 | 4 |
| 188 | `ank.asti_vilom` | 6 / 6 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 189 | `ank.asti_visham` | 5 / 5 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 190 | `ank.asti_yugm` | 5 / 5 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 191 | `ank.fib` | 14 / 14 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 192 | `ank.viparyay_ank` | 30 / 30 | 100% | COMPLETE | 0 / 0 / 0 |  | 6 |
| 193 | `anukram.anukram_maap_ashtak` | 3 / 3 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 194 | `brihat.brihat_ank_tak_int` | 16 / 16 | 100% | COMPLETE | 0 / 0 / 0 |  | 14 |
| 195 | `brihat.brihat_asti_shunyank` | 14 / 14 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 196 | `brihat.brihat_nyun` | 32 / 32 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 197 | `brihat.brihat_shunyank` | 12 / 12 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 198 | `brihat.brihat_yuj` | 24 / 24 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 199 | `chandas.asti_guru` | 21 / 21 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 200 | `chandas.dviguna` | 10 / 10 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 201 | `chandas.guru_gan` | 11 / 11 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 202 | `chandas.meru_pankti` | 6 / 6 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 203 | `ganit.asti_abhajya` | 17 / 17 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 204 | `ganit.bit_gan` | 11 / 11 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 205 | `ganit.dvigun` | 3 / 3 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 206 | `ganit.ganit_yadricch` | 9 / 9 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 207 | `ganit.ghan` | 3 / 3 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 208 | `ganit.ghat` | 9 / 9 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 209 | `ganit.kramgun` | 13 / 13 | 100% | COMPLETE | 0 / 0 / 0 |  | 7 |
| 210 | `ganit.trigun` | 3 / 3 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 211 | `ganit.vardh` | 3 / 3 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 212 | `ganit.varg` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 7 |
| 213 | `ganit.vargit` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 214 | `ganita.ganita_janchit_bhaj` | 28 / 28 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 215 | `ganita.ganita_janchit_ghat` | 23 / 23 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 216 | `ganita.ganita_janchit_kramgun` | 23 / 23 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 217 | `ganita.ganita_paripurna_bhaj` | 19 / 19 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 218 | `ganita.ganita_paripurna_shesh` | 19 / 19 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 219 | `ganita.samasa` | 11 / 11 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 220 | `gudh.fnv1a` | 13 / 13 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 221 | `gudh.fnv1a_varna` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 222 | `khand.khand_antah` | 6 / 6 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 223 | `khand.khand_maap` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 224 | `khand.khand_sam` | 6 / 6 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 225 | `mala.mala_grah` | 4 / 4 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 226 | `mala.mala_grah_surakshit` | 11 / 11 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 227 | `mala.mala_pratilip` | 14 / 14 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 228 | `mala.mala_purn` | 11 / 11 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 229 | `mala.mala_sangrah` | 6 / 6 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 230 | `mala.mala_sangrah_surakshit` | 13 / 13 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 231 | `mala.mala_yog` | 12 / 12 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 232 | `nighantu.nighantu_maap` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 18 |
| 233 | `nighantu.nighantu_mulya` | 22 / 22 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 234 | `patra.patra_asti` | 8 / 8 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 235 | `phal.phal_asti_siddhi` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 236 | `phal.phal_dosh` | 8 / 8 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 237 | `phal.phal_janchit_yuj` | 11 / 11 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 238 | `phal.phal_mulya` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 239 | `phal.phal_mulya_va` | 6 / 6 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 240 | `phal.phal_se_siddhi` | 17 / 17 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 241 | `phal.phal_siddhi` | 7 / 7 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 242 | `roop.roop_ank_pre` | 6 / 6 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 243 | `roop.roop_asht` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 244 | `roop.roop_dash` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 245 | `roop.roop_dwi` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 246 | `roop.roop_shodash` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 247 | `roop.roop_shodash_unnat` | 3 / 3 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 248 | `roop.roop_sthir` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 249 | `roop.roop_sthir_chinhit` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 250 | `roop.roop_varg` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 251 | `roop.roop_varg_ank` | 5 / 5 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 252 | `roop.roop_varg_bharatiya` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 253 | `roop.roop_varg_vishwa` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 254 | `sadhan.ank_adhik` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 255 | `sadhan.antargam` | 6 / 6 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 256 | `sadhan.satya_tak_ank` | 3 / 3 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 257 | `sadhan.shesh` | 8 / 8 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 258 | `sadhan.yog_seema` | 11 / 11 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 259 | `samanvaya.nirnaya2` | 8 / 8 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 260 | `samanvaya.nirnaya3` | 30 / 30 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 261 | `samanvaya.nishan` | 10 / 10 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 262 | `samanvaya.vivartana` | 17 / 17 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 263 | `sangrah.rakh_antah` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 10 |
| 264 | `sangrah.rakh_apanay` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 265 | `sangrah.rakh_maap` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 9 |
| 266 | `sangrah.rakh_rikta` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 267 | `sangrah.rakh_sam` | 10 / 10 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 268 | `sangrah.rakh_srij` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 22 |
| 269 | `sangrah.rakh_vardh` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 270 | `sankhyiki.madhya` | 5 / 5 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 271 | `sankhyiki.manak` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 272 | `sankhyiki.purna_madhya` | 6 / 6 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 273 | `sankhyiki.purna_yoga` | 9 / 9 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 274 | `sankhyiki.vichalan` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 275 | `sankhyiki.vyapti` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 276 | `sankhyiki.yoga` | 8 / 8 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 277 | `shreni.gan` | 11 / 11 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 278 | `shreni.vinimay` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 279 | `shreni.yog` | 9 / 9 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 280 | `suchi.avali_antah` | 16 / 16 | 100% | COMPLETE | 0 / 0 / 0 |  | 4 |
| 281 | `suchi.avali_maap` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 9 |
| 282 | `suchi.avali_tak_mala` | 14 / 14 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 283 | `suchi.chay_khip` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 284 | `suchi.suchi_antah` | 12 / 12 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 285 | `suchi.suchi_asti_sorted` | 3 / 3 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 286 | `suchi.suchi_dwi_anwesh` | 3 / 3 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 287 | `suchi.suchi_grah` | 10 / 10 | 100% | COMPLETE | 0 / 0 / 0 |  | 13 |
| 288 | `suchi.suchi_kramank` | 13 / 13 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 289 | `suchi.suchi_laghu` | 14 / 14 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 290 | `suchi.suchi_maap` | 2 / 2 | 100% | COMPLETE | 0 / 0 / 0 |  | 11 |
| 291 | `suchi.suchi_rikta` | 14 / 14 | 100% | COMPLETE | 0 / 0 / 0 |  | 6 |
| 292 | `suchi.suchi_shreni` | 5 / 5 | 100% | COMPLETE | 0 / 0 / 0 |  | 6 |
| 293 | `varna.akshar_sanket` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 294 | `varna.anwesh_akshar` | 11 / 11 | 100% | COMPLETE | 0 / 0 / 0 |  | 5 |
| 295 | `varna.asti_akshar_akshar` | 16 / 16 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 296 | `varna.asti_ank_akshar` | 9 / 9 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 297 | `varna.asti_avakash_akshar` | 3 / 3 | 100% | COMPLETE | 0 / 0 / 0 |  | 1 |
| 298 | `varna.asti_avanat_akshar` | 9 / 9 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 299 | `varna.asti_unnat_akshar` | 9 / 9 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 300 | `varna.avanat_sanket` | 9 / 9 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 301 | `varna.unnat_sanket` | 9 / 9 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |
| 302 | `varna.varna_antah` | 6 / 6 | 100% | COMPLETE | 0 / 0 / 0 |  | 2 |
| 303 | `varna.varna_maap` | 1 / 1 | 100% | COMPLETE | 0 / 0 / 0 |  | 3 |

## Every WITNESS: an input on which the mutant differs and no proof uses it

| function | mutant | input | real | mutant gives |
|---|---|---|---|---|
| `ank.ank_gan` | K:0@L16 | [-9] | 1 | 2 |
| `ank.seemit` | C1:<-><=@L65 | [3037000499, 3037000499, -1] | -1 | 3037000499 |
| `chandas.meru` | K:0@L27 | [-7, -7] | 0 | 1 |
| `chandas.meru` | N@L29 | [100, 16] | 192939124439967674 | -89841263756067081 |
| `chandas.meru` | A:-@L29 | [3037000499, 3037000499] | 1 | CRASH |
| `ganit.ganit_seemit` | C1:<-><=@L161 | [3037000499, 3037000499, -1] | -1 | 3037000499 |
| `ganita.brahmagupta_kshetr` | K:0@L176 | [16, 5, 4, 1000] | 0 | 1 |
| `ganita.ganita_paripurna_kramgun` | K:9223372036854775807@L565 | [1000000000] | 9223372036854775807 | CRASH |
| `ganita.kuttaka` | C4:>->>=@L36 | [-9223372036854775807, 0, 12] | 0 | CRASH |
| `ganita.kuttaka` | K:0@L31 | [0, 0, 4611686018427387904] | 0 | 1 |
| `madhava.madhava_atan` | N@L98 | [-20] | -1.520838 | -1.520817 |
| `madhava.madhava_atan` | A:-@L104 | [-20] | -1.520838 | 1.520838 |
| `madhava.madhava_atan` | K:1@L104 | [-20] | -1.520838 | 1.520838 |
| `madhava.madhava_cos` | N@L76 | [2] | -0.416147 | -0.416148 |
| `madhava.madhava_cos` | A:-@L76 | [2] | -0.416147 | -0.416148 |
| `madhava.madhava_cos` | A:+@L76 | [-18] | 0.660317 | 0.606488 |
| `madhava.madhava_sin` | N@L56 | [3] | 0.141120 | 0.141111 |
| `madhava.madhava_sin` | A:-@L56 | [3] | 0.141120 | 0.141111 |
| `madhava.madhava_sin` | A:+@L56 | [-18] | 0.750987 | 0.770223 |
| `sadhan.util_chinha` | K:0@L44 | [1] | 1 | 0 |
| `suchi.avali_srij` | A:*@L383 | [3037000499] | 0 | 140028479705088 |
| `suchi.avali_srij` | K:0@L384 | [9223372036854775807] | 0 | 1 |
| `suchi.suchi_srij` | A:*@L52 | [3037000499] | 0 | 139713393201152 |

## By module

| module | functions | killed / mutants | DECORATION | WEAK | PARTIAL | STRONG | ALL KILLED |
|---|---|---|---|---|---|---|---|
| aadhar | 2 | 75 / 85 | 0 | 0 | 0 | 2 | 0 |
| ank | 10 | 153 / 167 | 0 | 0 | 1 | 1 | 8 |
| anukram | 5 | 120 / 146 | 0 | 0 | 1 | 3 | 1 |
| brihat | 12 | 313 / 346 | 0 | 0 | 2 | 5 | 5 |
| chandas | 6 | 85 / 90 | 0 | 0 | 0 | 1 | 5 |
| ganit | 18 | 125 / 136 | 0 | 0 | 1 | 0 | 17 |
| ganita | 22 | 479 / 589 | 0 | 1 | 2 | 6 | 13 |
| gudh | 2 | 14 / 14 | 0 | 0 | 0 | 0 | 2 |
| kalana | 6 | 154 / 181 | 0 | 0 | 2 | 4 | 0 |
| khand | 22 | 442 / 541 | 0 | 0 | 6 | 13 | 3 |
| madhava | 5 | 107 / 143 | 0 | 0 | 0 | 3 | 2 |
| mala | 8 | 75 / 78 | 0 | 0 | 1 | 0 | 7 |
| nighantu | 17 | 441 / 523 | 0 | 0 | 5 | 10 | 2 |
| patra | 3 | 47 / 72 | 0 | 0 | 2 | 0 | 1 |
| phal | 14 | 108 / 130 | 0 | 0 | 7 | 0 | 7 |
| roop | 23 | 378 / 501 | 0 | 0 | 8 | 3 | 12 |
| sadhan | 7 | 53 / 59 | 0 | 0 | 0 | 1 | 6 |
| samanvaya | 10 | 151 / 163 | 0 | 0 | 0 | 6 | 4 |
| sangrah | 14 | 188 / 228 | 0 | 0 | 2 | 5 | 7 |
| sankhyiki | 16 | 129 / 150 | 0 | 0 | 3 | 5 | 8 |
| shreni | 14 | 205 / 232 | 0 | 0 | 2 | 9 | 3 |
| suchi | 34 | 429 / 524 | 0 | 0 | 8 | 13 | 13 |
| vakyank | 6 | 251 / 306 | 0 | 0 | 2 | 4 | 0 |
| varna | 27 | 471 / 540 | 0 | 0 | 5 | 11 | 11 |
