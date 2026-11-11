# ROUND-231 — Reference coverage ledger

Companion to `ROUND-231-REFERENCE-BOOK-AUDIT.md`. Main `064b05ad3ca597e94e246e9d78d972361235e0ad`, compiler v315; 11 November 2026. Repository-relative paths and one-based lines. **NOT RUN — read-side role, no toolchain used.** This is an inventory of static review coverage, not a blanket proof of correctness.

## Builtins: every ASCII spelling in the dispatch table

`C` means `src/sutram_compiler.asm`. All 69 ASCII spellings below are present in its table, grouped into 46 dispatch identities. Legacy spellings resolve to the same identities; the withdrawn dot product is recognized but refused. Each parenthesized number is the exact table line. The verdict concerns the reference description, not all possible arguments.

| Dispatch identity | Spellings (C line) | Review |
|---|---|---|
| `BN_LIKH` | `likh` (902) | Clarify width: likh(addr,value) stores eight bytes; raw pointer preconditions apply. |
| `BN_STHAGITA` | `sthagita` (903) | Program-stop statement agrees; not a thread primitive. |
| `BN_PAD` | `pad` (904) | Clarify width: pad(addr) reads one unsigned byte (C:22651–22672); raw pointer preconditions apply. |
| `BN_DVARAM` | `dvaram` (905) | R03: open, not merely a descriptor helper. |
| `BN_PAADH` | `paadh` (906) | R03: fd read, not open. |
| `BN_LIKHA` | `likha` (907) | Overloaded value printing agrees; string/no-LF versus numeric/LF matters. |
| `BN_BAND` | `band` (908) | Close descriptor description agrees. |
| `BN_NETSOCK` | `jala` (909), `netsock` (953) | R10: Linux socket operation; unsupported in the Windows shim. |
| `BN_NETBIND` | `jala_bandh` (910), `netbind` (954) | R10: Linux bind operation; unsupported in the Windows shim. |
| `BN_NETLIST` | `jala_shru` (911), `netlisten` (955) | R10: Linux listen operation; unsupported in the Windows shim. |
| `BN_NETACC` | `jala_grah` (912), `netaccept` (956) | R10: Linux accept operation; unsupported in the Windows shim. |
| `BN_NIRMRITA` | `nirmmita` (913) | R11–R12: zeroing and Windows negative-size qualifications. |
| `BN_LIKH8` | `likh8` (914) | R01: 64-bit memory store. |
| `BN_PAD8` | `pad8` (915) | R01: 64-bit memory load. |
| `BN_VARTLEN` | `vartani_aayam` (916) | R07: bytes to NUL, not Unicode character count. |
| `BN_VARTCMP` | `vartani_tul` (917) | R08: 0 equal / 1 different, not lexical ordering. |
| `BN_VARTCAT` | `vartani_sandhi` (918), `vartani_cat` (957) | In-place append and literal-destination refusal agree; caller must provide writable capacity. |
| `BN_VECADD` | `sankhya_yog` (919) | Four raw float32 lanes, addps: described accurately; no native float32 scalar type. |
| `BN_VECMUL` | `sankhya_gunan` (920) | Four raw float32 lanes, mulps: described accurately; no native float32 scalar type. |
| `BN_VECDOT` | `sankhya_bindu` (921), `sankhya_dot` (958) | Withdrawn, E_PRATYAHRITA; recognized name is not an available operation. |
| `BN_LKFMT` | `likha_rup` (922), `likha_fmt` (959) | Literal prefix plus integer and LF agrees; not placeholder substitution. |
| `BN_CHARAT` | `akshar` (923) | R07: unsigned byte at an index. |
| `BN_CHARCD` | `aksharank` (924) | R05/R07: optional byte index is honored. |
| `BN_CHARFR` | `anka_akshar` (925), `char_from` (960) | R07: low byte followed by NUL; zero code yields empty string. |
| `BN_CHARUP` | `akshar_guru` (926), `char_upper` (961) | R07: ASCII case conversion on the low byte. |
| `BN_CHARLO` | `akshar_laghu` (927), `char_lower` (962) | R07: ASCII case conversion on the low byte. |
| `BN_LIKH8C` | `likh8c` (928) | R02: conditionally store a qword to memory, not print a character. |
| `BN_PAD8C` | `pad8c` (929) | R02: conditionally read a qword from memory, not read a character. |
| `BN_MEMSET` | `smaran` (930) | Fill bytes description agrees; caller supplies valid memory. |
| `BN_MEMCPY` | `smaran_pratilip` (931), `smaran_cp` (963) | Copy bytes description agrees; not a promised overlap-safe move. |
| `BN_VARTCP` | `vartani_pratilip` (932) | R07: copy through terminating NUL into caller-provided writable capacity. |
| `BN_GRAHAN` | `grahan` (933) | R04: stdin digit accumulator; sign, final EOF, invalid-byte and overflow limitations. |
| `BN_LKHB` | `likha_santat` (934), `lkhb` (964) | Numeric output without LF agrees, including dasham. |
| `BN_SHABDA` | `shabda` (935) | Print a NUL-terminated byte string, no automatic LF. |
| `BN_PANKTILEN` | `pankti_gan` (936), `pankti_len` (965) | R06: stored array/slice length, not only a literal array length. |
| `BN_KOSHPUSH` | `kosh_kship` (937), `kosh_yuj` (944), `kosh_push` (966), `kosh_enqueue` (973) | Push/enqueue aliases agree; descriptor and growth semantics match the newer kosh section. |
| `BN_KOSHPOP` | `kosh_hri` (938), `kosh_pop` (967) | Remove last element; documented empty-container error is retained. |
| `BN_KOSHLEN` | `kosh_gan` (939), `kosh_len` (968) | Current element count. |
| `BN_KOSHCAP` | `kosh_ksham` (940), `kosh_cap` (969) | Current capacity. |
| `BN_KOSHCLEAR` | `kosh_shodh` (941), `kosh_clear` (970) | Clear logical length, not a promise to release all allocation. |
| `BN_KOSHEMPTY` | `kosh_rikt` (942), `kosh_empty` (971) | Empty predicate. |
| `BN_KOSHPEEK` | `kosh_iksh` (943), `kosh_peek` (972) | Read last element; empty-container error. |
| `BN_KOSHDEQUEUE` | `kosh_apanay` (945), `kosh_dequeue` (974) | Remove first element; empty-container error. |
| `BN_SETCHAR` | `akshar_rakh` (946) | R09: present but missing from primary table; unchecked one-byte store. |
| `BN_DVARLIKHA` | `dvaram_likha` (947) | Raw fd write with returned count; no value formatting. |
| `BN_PARIMANA` | `parimana` (948) | R13: logical allocation accounting, not RSS or reservation size. |

Canonical and legacy naming behavior is implemented around C:900–1065 and C:33307 onward. `vartlen`, `charat` and `memcpy` are correctly identified in the reference as former documentation mistakes, not accepted spellings. The same table also has the Devanagari parimana spelling at C:949, for 70 total rows; it shares BN_PARIMANA. Other language-pack keyword translations are separate from this ASCII inventory.

## Library names: definitions and reference descriptions

Exact identifier matching finds 86 library definitions whose names occur in the reference. This includes names also reused in examples (`fib`, `madhya`, `yog`, `yoga`); name coincidence does not import a module. The source location is the definition, not a claim that the whole implementation has been exhaustively proved. “No mismatch found” means the limited description in the reference did not contradict the inspected implementation.

| Name | Definition | Reference lines | Verdict |
|---|---|---|---|
| `brihat_ank_se` | `lib/aadhar.smlib:80` | 136 | R15: invalid descriptors leave destination untouched; later failures clear it. |
| `asti_yugm` | `lib/ank.smlib:4` | 375 | No mismatch found in the stated description. |
| `asti_visham` | `lib/ank.smlib:8` | 375 | No mismatch found in the stated description. |
| `ank_gan` | `lib/ank.smlib:12` | 375 | No mismatch found in the stated description. |
| `ank_yog` | `lib/ank.smlib:27` | 375 | No mismatch found in the stated description. |
| `viparyay_ank` | `lib/ank.smlib:44` | 134, 375 | No mismatch found in the stated description. |
| `asti_viparyay_sam` | `lib/ank.smlib:70` | 375 | No mismatch found in the stated description. |
| `seemit` | `lib/ank.smlib:78` | 375 | No mismatch found in the stated description. |
| `fib` | `lib/ank.smlib:89` | 116, 375, 533, 535 | Library function exists; the syntax example separately defines its own fib. |
| `asti_sampurna` | `lib/ank.smlib:106` | 375 | No mismatch found in the stated description. |
| `collatz_charan` | `lib/ank.smlib:125` | 375 | No mismatch found in the stated description. |
| `brihat_ank_se_laghu` | `lib/brihat.smlib:29` | 407 | No mismatch found in the stated description. |
| `brihat_ank_tak_laghu` | `lib/brihat.smlib:71` | 137, 408 | R14: missing lower-bound digit guard; negative digits are not refused. |
| `dwi_ghat` | `lib/chandas.smlib:13` | 117 | No mismatch found in the stated description. |
| `meru` | `lib/chandas.smlib:29` | 117 | No mismatch found in the stated description. |
| `matra_meru` | `lib/chandas.smlib:63` | 116 | No mismatch found in the stated description. |
| `varg` | `lib/ganit.smlib:7` | 117, 374 | No mismatch found in the stated description. |
| `vargit` | `lib/ganit.smlib:15` | 117, 374 | No mismatch found in the stated description. |
| `ghan` | `lib/ganit.smlib:23` | 118, 374 | No mismatch found in the stated description. |
| `nirapeksh_mulya` | `lib/ganit.smlib:34` | 132, 374 | No mismatch found in the stated description. |
| `laghu2` | `lib/ganit.smlib:45` | 374 | No mismatch found in the stated description. |
| `adhik2` | `lib/ganit.smlib:53` | 374 | No mismatch found in the stated description. |
| `mahattam_samapavartak` | `lib/ganit.smlib:63` | 133, 374, 393 | No mismatch found in the stated description. |
| `laghuttam_samapavartya` | `lib/ganit.smlib:86` | 117, 374 | R16: delegated gcd can stop before sentinel/zero handling. |
| `ghat` | `lib/ganit.smlib:108` | 118, 374 | No mismatch found in the stated description. |
| `kramgun` | `lib/ganit.smlib:139` | 116, 374, 395 | No mismatch found in the stated description. |
| `asti_abhajya` | `lib/ganit.smlib:155` | 374 | No mismatch found in the stated description. |
| `yog_tak` | `lib/ganit.smlib:171` | 117, 374 | No mismatch found in the stated description. |
| `dvigun` | `lib/ganit.smlib:186` | 131, 374, 717 | No mismatch found in the stated description. |
| `trigun` | `lib/ganit.smlib:194` | 131, 374 | No mismatch found in the stated description. |
| `vardh` | `lib/ganit.smlib:202` | 131, 374 | No mismatch found in the stated description. |
| `ekanka_gan` | `lib/ganit.smlib:209` | 6, 258 | R27: negative input returns 0; domain qualification missing. |
| `kuttaka` | `lib/ganita.smlib:21` | 377 | No mismatch found in the stated description. |
| `ganita_vargmool` | `lib/ganita.smlib:66` | 377 | No mismatch found in the stated description. |
| `ganita_nirapeksh` | `lib/ganita.smlib:92` | 132, 377 | No mismatch found in the stated description. |
| `chakravala` | `lib/ganita.smlib:102` | 377 | No mismatch found in the stated description. |
| `samasa` | `lib/ganita.smlib:186` | 377 | No mismatch found in the stated description. |
| `brahmagupta_kshetr` | `lib/ganita.smlib:205` | 135, 377 | No mismatch found in the stated description. |
| `ganita_janchit_yuj` | `lib/ganita.smlib:363` | 114 | No mismatch found in the stated description. |
| `madhava_vargmool` | `lib/madhava.smlib:13` | 378 | No mismatch found in the stated description. |
| `madhava_pi` | `lib/madhava.smlib:26` | 378 | No mismatch found in the stated description. |
| `madhava_sin` | `lib/madhava.smlib:50` | 378, 880 | No mismatch found in the stated description. |
| `madhava_cos` | `lib/madhava.smlib:80` | 378 | No mismatch found in the stated description. |
| `madhava_atan` | `lib/madhava.smlib:115` | 378 | No mismatch found in the stated description. |
| `patra_asti` | `lib/patra.smlib:81` | 10, 138 | Reference explicitly records its OS-query limitation; no claim of repair. |
| `roop_ank_upasarga` | `lib/roop.smlib:239` | 264 | R28: bases 2..36; prefixes only 2/8/16. |
| `roop_purti_vam` | `lib/roop.smlib:252` | 6, 260 | No mismatch found in the stated description. |
| `roop_purti_dakshin` | `lib/roop.smlib:285` | 261 | No mismatch found in the stated description. |
| `roop_purti_madhya` | `lib/roop.smlib:319` | 262 | No mismatch found in the stated description. |
| `roop_sthir` | `lib/roop.smlib:597` | 881 | No mismatch found in the stated description. |
| `roop_chihna_akshar` | `lib/roop.smlib:646` | 265 | No mismatch found in the stated description. |
| `yog_seema` | `lib/sadhan.smlib:16` | 118, 139 | No mismatch found in the stated description. |
| `adish_gunan` | `lib/samanvaya.smlib:136` | 140 | No mismatch found in the stated description. |
| `rakh_ubhaya_bhed` | `lib/sangrah.smlib:63` | 259 | No mismatch found in the stated description. |
| `yoga` | `lib/sankhyiki.smlib:16` | 1347 | Library definition exists; local demonstration names do not automatically refer to this function. |
| `madhya` | `lib/sankhyiki.smlib:27` | 1273 | Library definition exists; R24 concerns a different, locally defined scratch example. |
| `bindu_gunan` | `lib/sankhyiki.smlib:100` | 140, 197 | No mismatch found in the stated description. |
| `purna_prasaran` | `lib/sankhyiki.smlib:182` | 117 | R17: truncated mean and per-deviation square limit. |
| `vinimay` | `lib/shreni.smlib:6` | 376 | No mismatch found in the stated description. |
| `budbud_shreni` | `lib/shreni.smlib:13` | 376, 381 | No mismatch found in the stated description. |
| `viparyay_mala` | `lib/shreni.smlib:28` | 376 | No mismatch found in the stated description. |
| `laghu` | `lib/shreni.smlib:39` | 376 | No mismatch found in the stated description. |
| `adhik` | `lib/shreni.smlib:53` | 376 | No mismatch found in the stated description. |
| `yog` | `lib/shreni.smlib:66` | 376, 699, 1170, 1171, 1173 | Library function exists; slice example separately uses this as an illustrative function name. |
| `anwesh_sarak` | `lib/shreni.smlib:77` | 376 | No mismatch found in the stated description. |
| `gan` | `lib/shreni.smlib:87` | 376 | No mismatch found in the stated description. |
| `asti_kramabaddha` | `lib/shreni.smlib:98` | 6, 253, 266, 376 | No mismatch found in the stated description. |
| `dwi_anwesh` | `lib/shreni.smlib:108` | 376 | No mismatch found in the stated description. |
| `shankh_shreni` | `lib/shreni.smlib:120` | 376, 381 | No mismatch found in the stated description. |
| `suchi_shreni` | `lib/suchi.smlib:214` | 141 | No mismatch found in the stated description. |
| `suchi_asti_kramabaddha` | `lib/suchi.smlib:270` | 267 | No mismatch found in the stated description. |
| `purti_vam` | `lib/vakyank.smlib:241` | 263 | No mismatch found in the stated description. |
| `varna_tak_dashm` | `lib/vakyank.smlib:277` | 142 | No mismatch found in the stated description. |
| `varna_maap` | `lib/varna.smlib:19` | 379 | No mismatch found in the stated description. |
| `akshar_sanket` | `lib/varna.smlib:23` | 379 | No mismatch found in the stated description. |
| `asti_ank_akshar` | `lib/varna.smlib:27` | 379 | No mismatch found in the stated description. |
| `asti_unnat_akshar` | `lib/varna.smlib:34` | 379 | No mismatch found in the stated description. |
| `asti_avanat_akshar` | `lib/varna.smlib:41` | 379 | No mismatch found in the stated description. |
| `asti_akshar_akshar` | `lib/varna.smlib:48` | 379 | No mismatch found in the stated description. |
| `asti_avakash_akshar` | `lib/varna.smlib:56` | 379 | No mismatch found in the stated description. |
| `gan_swar` | `lib/varna.smlib:63` | 379 | No mismatch found in the stated description. |
| `gan_akshar` | `lib/varna.smlib:78` | 379 | No mismatch found in the stated description. |
| `anwesh_akshar` | `lib/varna.smlib:90` | 379 | No mismatch found in the stated description. |
| `asti_sarv_ank` | `lib/varna.smlib:101` | 379 | No mismatch found in the stated description. |
| `unnat_sanket` | `lib/varna.smlib:113` | 379 | No mismatch found in the stated description. |
| `avanat_sanket` | `lib/varna.smlib:120` | 379 | No mismatch found in the stated description. |

### Shorthand families and aliases

The table above counts exact name matches, so these shortened references also need expansion:

| Reference form | Actual definitions | Verdict |
|---|---|---|
| `ganita_janchit_yuj` / `_nyun` / `_gun` | `ganita_janchit_yuj` (`lib/ganita.smlib:363`); `ganita_janchit_nyun` (`lib/ganita.smlib:389`); `ganita_janchit_gun` (`lib/ganita.smlib:416`) | Status-cell form exists for the three named operations. |
| `ganita_paripurna_*` | `ganita_paripurna_yuj` (`lib/ganita.smlib:495`); `ganita_paripurna_nyun` (`lib/ganita.smlib:514`); `ganita_paripurna_gun` (`lib/ganita.smlib:534`); `ganita_paripurna_ghat` (`lib/ganita.smlib:615`); `ganita_paripurna_bhaj` (`lib/ganita.smlib:647`); `ganita_paripurna_shesh` (`lib/ganita.smlib:665`); `ganita_paripurna_nirapeksh` (`lib/ganita.smlib:695`); `ganita_paripurna_kramgun` (`lib/ganita.smlib:710`) | R29: arithmetic overflow saturation is not a universal invalid-input policy; zero divisor returns 0. |

All ten old library names at R:258–267 have the compiler rename mappings (C:983–1065,33307 onward):

- `bit_gan` → `ekanka_gan`.
- `rakh_samroop_diff` → `rakh_ubhaya_bhed`.
- `roop_pad_vam` → `roop_purti_vam`.
- `roop_pad_dakshin` → `roop_purti_dakshin`.
- `roop_pad_madhya` → `roop_purti_madhya`.
- `pad_vam` → `purti_vam`.
- `roop_ank_pre` → `roop_ank_upasarga`.
- `roop_sign_akshar` → `roop_chihna_akshar`.
- `asti_sorted` → `asti_kramabaddha`.
- `suchi_asti_sorted` → `suchi_asti_kramabaddha`.

`mukhya`, `abhava`, `siddhi`, `dosh` and `prasar` are language forms, not missing stdlib functions. Locally defined or contextual names include `f`, `g`, `joda`, `bhaj`, `ek_adhik`, `padh_ya`, `aarohi`, `shreni`, `agla`, `Bindu.chal`, `tulana`, `dek`, `rakh`, `naam`, `ghata`, `jod`, `padh`, `madhya`, `fib`, `yog` and `yoga`. Their availability depends on the shown or surrounding declaration. `trunc` is mathematical explanation, not a supplied function. `sankhya_padh` is the specific unsupported helper in R:1236; it needs a definition returning a phal.

The six-module table lists 60 real names, but the corresponding current definition counts are ganit 18, ank 10, shreni 14, ganita 27, madhava 5, varna 27: **101**. Whole-library enumeration gives **310 definitions in 24 modules**, including private-style helpers. This is not a count of exported, stable public contracts.

## Every concrete error code named in the reference

All 40 codes have message definitions. `E_CODE` and `E_KOSH_*` are notation, excluded from that count. Locations below point to actual message text, not just comments; additional translated variants exist. The verdict compares the reference description with the source, not just a string search.

| Code | Message location | Contract review |
|---|---|---|
| `E_AKARA_ASAMYA` | lib/samanvaya.smlib:138; lib/sankhyiki.smlib:102 | Unequal dot-product lengths: message and guard agree. |
| `E_AMBIGUOUS_FIELD` | C:342 | Ambiguous field/method resolution: agrees. |
| `E_ANTARAL_MISHRA` | C:745 | Mixed leading indentation at one line: agrees. |
| `E_APARIKSHITA_AHVAN` | C:411 | Call to a non-parikshita function from checked code: agrees. |
| `E_APARIKSHITA_KARYA` | C:412 | Forbidden builtin in checked code: agrees. |
| `E_APARIKSHITA_SMRITI` | C:413 | Memory access outside the checked subset: agrees. |
| `E_ARITY` | C:345 | Wrong function/method argument count: agrees. |
| `E_ATIPRAVAH` | C:401; lib/ganit.smlib:188 | Constant overflow / guarded library overflow: agrees; plain runtime arithmetic still wraps. |
| `E_CHAKRA_DASHAM` | C:484 | Float counted-loop bounds: agrees. |
| `E_DASHAM_KRIYA` | C:487 | Unsupported float remainder/bit operations: agrees. |
| `E_DASHAM_VITTI` | C:445,448 | Fractional/out-of-range narrowing: compile-time and runtime forms agree. |
| `E_GAHANATA` | C:683 | Call-depth limit: agrees. |
| `E_KOSH_DVARA` | C:613,620,622 | Kosh entering an untyped/raw-number path: agrees. |
| `E_KOSH_GANIT` | C:550,633 | Kosh used in numeric arithmetic/comparison: agrees; R20 corrects the old rationale. |
| `E_KOSH_MANDAPA` | C:438,557,559 | Static block escape and runtime expired generation forms: agree. |
| `E_KOSH_VIBHAG` | C:628,649,652 | Unsafe kosh-slice storage/call paths: agrees with the newer slice section. |
| `E_LIKHA_TRAYA` | C:503 | Historical code, correctly marked as v286 behavior at R:336; old checker disabled (C:8748). |
| `E_MALA_GANIT` | C:655 | Array numeric operands: agrees. |
| `E_MULYA_AYOGYA` | lib/brihat.smlib:73,79 | Message exists, but digit guard misses d < 0: R14. Do not call that contract enforced. |
| `E_MULYA_VINA` | C:491 | Uninitialized local scalar: agrees; module initializers and container declarations differ. |
| `E_NIRMMITA_RNA` | C:731 | Negative literal allocation size: agrees. Computed negative scratch uses a separate runtime path; R12. |
| `E_NIRMMITA_SEEMA` | C:735 | Provable fixed raw-allocation index excess: agrees; not a general raw-pointer safety guarantee. |
| `E_PARIKSHA_PADANI` | C:646 | Invalid or duplicate --analysis-steps option: agrees. |
| `E_PARIMITA` | C:8916,8919 | Block-budget exhaustion and invalid written budget: agrees. |
| `E_PARSE` | C:268 | Exists on check-mode syntax route; ordinary parse diagnostics need not carry the code: R31. |
| `E_PHALA_SEEMA` | lib/brihat.smlib:80; lib/ganit.smlib:36,80 | Representability failures exist as described; LCM also inherits the gcd fatal case: R16. |
| `E_PRATYAHRITA` | C:661 | Withdrawn sankhya_bindu/sankhya_dot: agrees. |
| `E_RACHANA_GANIT` | C:656 | Recognized structure reference in numeric operands: agrees; inference limitations remain. |
| `E_SCRATCH_ESCAPE` | C:722,724,726 | Statically visible scratch return/store escape: agrees; not a proof against indirect escape. |
| `E_SHUNYA_BHAJAN` | C:390,397 | Integer and float divide-by-zero / integer remainder by zero: agrees. |
| `E_UNKNOWN_FIELD` | C:338 | Unknown field: agrees. |
| `E_VAKYA_SEEMA` | C:636 | Per-statement analysis-step budget exhausted: agrees; distinct from tree capacity. |
| `E_VARTANI_CAT` | C:515 | Unsupported mixed string concatenation: agrees. |
| `E_VARTANI_GANIT` | C:538 | Forbidden string arithmetic/bit operations: agrees. |
| `E_VARTANI_SATYA` | C:547 | String used as a whole condition: correct at R:469, contradicted at R:490; R19. |
| `E_VARTANI_STHIRA` | C:673,676 | Literal destination for in-place append: compile-time and runtime messages agree. |
| `E_VARTANI_TUL` | C:509 | Mixed string/non-string comparison: agrees. |
| `E_VIBHAG_ANKA` | C:631 | Slice used as a number: agrees. |
| `E_VITTI_PRAKAR` | C:602 | A name changing inferred kind: agrees. |
| `E_VRIKSHA_SEEMA` | C:644 | AST capacity limit distinct from analysis budget: agrees. |

R30 applies across the table: a file/line/column may precede `Sutram truti`. A code appearing in source, a guard being complete, and a particular example reaching that guard are separate questions. No error was induced by this review.

## Every fenced reference block

Opening/closing fence lines identify the exact block in `docs/LANGUAGE-REFERENCE.md`. “Yes” means syntax and visible bindings look valid by source reading; it does not mean executed, or safe for arbitrary inputs. “Fragment” requires surrounding declarations/entry point. “Schematic” contains literal ellipses or an undefined illustrative helper. “Negative” intentionally demonstrates semantic refusal.

| Fence lines | Class / static verdict | Reason or qualification |
|---|---|---|
| 30–33 | Program — yes | Simple main/string print; no automatic newline. |
| 35–38 | Shell — not Sutram | Compile/run commands; platform-dependent, not executed. |
| 210–212 | Output | Legacy builtin notice. |
| 252–254 | Output | Legacy library notice. |
| 283–288 | Program — yes | Scalar 42 print with LF. |
| 290–292 | Output | Matches scalar-print rule statically. |
| 295–300 | Program — yes | Literal prefix plus scalar. |
| 302–304 | Output | Matches prefix/scalar rule statically. |
| 310–316 | Program — yes | Four value arguments, numeric last argument adds LF. |
| 318–320 | Output | Matches value-print rule statically. |
| 323–327 | Program — yes | Raw four-byte fd write. |
| 329–331 | Output | Raw write includes LF in literal. |
| 341–347 | Program — yes | Legacy lkhb resolves, emits a compilation notice; dasham output has no automatic LF. |
| 349–351 | Output | Numeric text followed by explicit separator/LF. |
| 355–359 | Program — yes | Literal prefix plus integer via likha_rup. |
| 361–363 | Output | Matches likha_rup rule. |
| 389–397 | Program — yes | ganit import resolves both functions; explicit LF after numeric prints adds blank lines. |
| 494–537 | Program — yes | Brace-free main can collect later function definitions; joda indentation accepted. The brace comment is stale (R18/R21). |
| 539–544 | Fragment — valid grammar | Ternary and do-while; requires x, i and enclosing body. |
| 551–556 | Program — yes | Brace-free main with three statements. |
| 558–562 | Fragment — valid declaration | Contrary to its caption, multi-statement indented function is accepted; add main for a complete program. |
| 581–587 | Program — yes | Inclusive counted loop, ordinary 0..4 bounds. |
| 589–595 | Program — yes | arabhya/paryantam form of the same loop. |
| 597–603 | Output | Expected 0 through 4, each with LF. |
| 612–620 | Program — yes | dasham while loop; not a float chakra. |
| 632–638 | Fragment — valid grammar | Indented while and following statement; requires initialized i and enclosing main. |
| 694–696 | Diagnostic | Call-depth message exists; not executed here. |
| 720–724 | Program — yes | Danda terminators and UTF-8 literal. |
| 735–744 | Program — yes | Devanagari keyword spellings under Sanskrit language pack; integer sum loop. |
| 857–862 | Negative — semantic refusal | Grammar is formed, but vitti f = 3.5 is refused with E_DASHAM_VITTI. |
| 873–875 | Diagnostic | Runtime narrowing message exists. |
| 972–984 | Program — yes | Kosh descriptor aliases survive growth. |
| 988–991 | Output | Consistent with descriptor alias semantics, not a new run. |
| 1015–1027 | Program — yes | Typed kosh parameter can grow and return its length. |
| 1093–1096 | Fragment — intentional refusal | With k a kosh in context, changing a to raw memory is E_VITTI_PRAKAR. |
| 1127–1133 | Fragment — schematic | Literal ... and contextual x/j/v; not compilable as printed. |
| 1148–1152 | Fragment — contextual | Structure and method declaration valid; call requires a declared instance p and entry point. |
| 1169–1174 | Fragment — schematic | Literal ...; slicing requires array context. Not a complete program. |
| 1203–1218 | Program — yes | Explicit result propagation; predicts 6 then exit status 1. |
| 1234–1241 | Fragment — incomplete helper | sankhya_padh is not supplied; needs a phal-returning definition and entry point. |
| 1254–1264 | Fragment — schematic | Two block forms plus literal ... and contextual x. |
| 1272–1282 | Fragment — valid declaration | Scratch return of scalar allowed; omitted sorting means return b, not median. |
| 1364–1367 | Diagnostic | Static kosh block escape message and hint exist. |
| 1378–1380 | Diagnostic | Callee-escape message exists. |
| 1390–1393 | Diagnostic | Expired kosh generation message and hint exist. |
| 1428–1434 | Output | Allocation-accounting illustration; 16-byte rounding explains 1072; 8288 agrees with the described simple growth case, not a measured RSS. |
| 1459–1469 | Program — yes | Budget loop is syntactically valid and intended to stop at runtime after 16384 allocations of 64 bytes. |
| 1471–1473 | Diagnostic | Block-budget failure message exists. |
| 1507–1517 | Program-shaped — schematic | Checked function plus main contains literal ...; not compilable as printed. |
| 1543–1550 | Program — yes | Literal/variable/concatenated string print plus numeric prints. |

Totals: **50 fences = 32 source specimens + 18 shell/output/diagnostic blocks**. The 32 source specimens comprise **20 complete programs judged valid**, **1 deliberate semantic rejection**, **1 schematic program-shaped block**, and **10 fragments** (some valid with context, some schematic or intentionally rejected). This classification is not a claim that every fence should compile.

## Inline specimens and behavioral coverage

Inline syntax is distributed through prose and tables. The groups below cover the reference sections; short forms with omitted declarations are patterns, not independent executable files. Findings are linked where a rule is contradicted.

| Reference lines / topic | Static reading |
|---|---|
| 41–100, keywords/types/operators | Declarations, comparisons, aliases and expressions are grammar forms; guna multiplication label needs R32. No invented samapt terminator is needed. |
| 103–145, integer limits and numeric contracts | Constant-overflow and zero-divisor examples are intentional refusals; runtime wrapping, truncating division/remainder and logical shifts agree. Library boundary exceptions: R14–R17/R29. |
| 156–228, builtin signatures/legacy names | Names resolve as listed in the builtin ledger; wrong memory/file descriptions and byte semantics: R01–R10. Recognized withdrawn names remain refused. |
| 232–275, diagnostics and renamed library calls | Legacy calls map to current definitions; generic E_CODE and E_KOSH_* are notation. Diagnostic prefix/mode qualifications: R30–R31. |
| 278–365, printing forms | One-to-six values, numeric final LF, raw fd write and literal-prefix formatting agree. A raw byte buffer is not automatically a string value. |
| 369–411, imports and bigint cells | yoj imports definitions; LSB-first digits and eight-byte cell offsets agree. Counts/parameter warning stale: R25–R26. |
| 414–490, strings/arrays/kosh/structures | String comparisons/concatenation and deliberate mixed-type refusals follow source rules; empty-string condition and old identity rationale conflict: R19–R20. |
| 494–650, control flow and indentation | Ternary, do-while, braces and indented bodies are grammar forms; guna retains its documented special block form. Function-brace claim stale (R18), integer-loop endpoint caveat R33. |
| 654–706, bounds/narrowing/depth | p[9] after nirmmita(10) is an eight-byte-cell bound violation, intentionally refused; raw pointer arithmetic/stores do not gain general bounds safety. Float narrowing/depth examples are negative cases. |
| 709–782, native scripts/flags | Danda and demonstrated keyword spellings are token forms; invocations are shell specimens. Not a native-speaker review or a CLI execution pass. |
| 833–952, dasham | Arithmetic, narrowing, divide-by-zero and special-value examples must be distinguished from intentional refusals; raw SIMD float32 lanes are different from dasham binary64. |
| 955–1114, kosh/slice/analysis limits/kinds | Current descriptor alias, typed-parameter growth and slice restrictions agree; snippets using f/dek/etc require the stipulated signatures. Assigning a kosh to raw-number paths and slice-number uses are deliberate negative cases. |
| 1117–1179, function values/methods/slices | Valid forms need declarations; ellipses remain schematic; p.chal requires an instance; universal declaration-order claim needs R21. |
| 1182–1241, explicit results | siddhi/dosh return, prasar propagation and yadi dosh syntax are supported; missing sankhya_padh definition needs R22. Fatal library diagnostics are not recoverable phal results. |
| 1244–1419, block lifetimes | Lexically marked scratch/escape rules differ from persistent kosh/mala allocation and hidden-callee allocations; negative Windows allocation and zeroing claims need R11–R12. Median illustration omits its algorithm (R24). |
| 1422–1498, accounting/budgets | parimana is logical byte accounting with alignment; block budgets and intended refusal are supported. Distinguish current allocation, freed old kosh region, and physical OS usage (R13). |
| 1501–1557, checked subset/output recap | Checked-call/builtin/memory restrictions match the named errors; literal ellipses are not accepted source (R23). Historical 306-function count needs a date or update (R26). |

## Limits of this ledger

This is static contract and example review of the requested reference, plus chapters 1–3 of the English and Sanskrit books in the companion report. It is not a fresh benchmark, full-library proof run, full-book execution report, native Windows acceptance, staged-branch acceptance, or linguistic certification. No source, tests or golden outputs were changed. **NOT RUN — read-side role, no toolchain used.**
