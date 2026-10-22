# Round 102 WS1 — Checked sizes and indices across the whole standard library

**Scope:** all **24** `lib/*.smlib` files in Git tree `f68ce9e357493005d63afa0797abe04e8361c78c`, at main `d6a4635c1dc9dc127589f96f29cce1864da80ab6` (changelog v302). The API tree was not truncated. Each file was read, including complete function bodies. This is a **source audit**, not a claim that a scanner or the native suite ran. Exact source blobs, every allocation call and grouped explicit index sites are in `ROUND-102-SOURCE-INVENTORY.json`.

**Concurrent update:** Claude R36 landed while this audit was underway. At `004a28a2d696caa552269ccf9765d1e609282b85`, only `mala`, `suchi` and `nighantu` differ in the library tree. R36 fixes list/queue growth bounds and `nighantu_vardh` failure handling. Those are **closed in the newer tree**, not new work to duplicate. This review adds negative-domain and index/shape analysis rather than repeating R35/R36 constructor repairs. Production code, existing tests and goldens were not changed by ChatGPT.

## The rule: validity must precede address formation

For a nonnegative count `n`, positive constant stride `s`, and nonnegative header `h`, validate **`n <= (INT64_MAX-h)/s` before evaluating `n*s+h`**. Reject negative counts first. For two variable dimensions, check the product with an explicit success flag, then compare with the actual buffer length. For a byte offset `off`, require a known extent and `width <= extent-off` after proving `0 <= off <= extent`. Check base-address addition in the address domain too; signed count arithmetic does not prove pointer provenance or nonwrapping unsigned pointer addition.

A negative-result check after multiplication, a small wrapped result, or a successful OS allocation is **not** an overflow proof. A bounds check on an already-wrapped index is also insufficient. Once a boundary check proves a whole loop's valid shape, do not insert a general checked-multiply call at every element.

### The real helper and its status channel

The brief's `ganita_checked_mul` is descriptive English. The actual function is **`ganita_janchit_gun(a,b,ok)` in `lib/ganita.smlib`**, not `lib/ganit.smlib`. It returns the product and sets `ok[0]=1`, or returns zero with `ok[0]=0` on signed overflow. **A zero return alone is ambiguous:** `0*8` legitimately succeeds. Check `ok[0]` after **each** stage. Likewise `ganita_janchit_yuj` checks additions. `checked_mul(n+1,8)` is too late if `n+1` already overflowed.

The helper accepts signed arithmetic, not a size domain: `-1*8` succeeds arithmetically with -8. Reject negative counts separately. Never replace allocation arithmetic with saturation; a clamped size is not enough storage for the promised count. Use a caller-owned status cell, not a new heap allocation just to check arithmetic.

**Use the helper** at variable-by-variable dimension/stride boundaries where an existing `ganita` dependency and a reviewable failure convention exist. **Prefer exact inline division bounds** for constant-size collection allocation/growth: no extra import, no status-cell machinery, no repeated call per element. R36 measured only **1,114 bytes of source-expansion headroom** in the combined container test (64,422/65,536); adding a whole arithmetic module or long comments could break accepted builds. That is a concrete reason to use compact bounds, not to omit checks. R36's reference to the helper's English name/module is corrected above.

## Allocation inventory — 35 calls, not 35 demonstrated bugs

The source review enumerated **25 variable-size `nirmmita` calls** and **10 constant-size calls**. Variable formulas appear in seven modules. The list below includes already-safe sites and conditional caller-contract risks, not just failures.

| File / function | Every variable allocation expression | Recommendation and current status |
|---|---|---|
| `aadhar` / `brihat_ank_tak` | `c*8`; `c*4*8` | Validate nonnegative n and 4n-cell output/scratch extent; constant bound `n<=MAX/32` before both products. Both allocation results need checks before copying. A valid actual input array is an existing caller precondition; do not claim huge fabricated n is supported input. |
| `brihat` / `brihat_shesh` | `c*8` | Validate n/2n extents before its first input read, then scratch allocation. |
| `brihat` / `brihat_ghatmod` | `c*2*8`; `c*8` | Require n<=MAX/16 for the 2n scratch and sufficient actual input/output extents; check both allocation results. |
| `mala` / `mala_nava` | `c*8` | R35 upper bound handles positive counts. **Negative domain still unguarded**, including after R36: see witness below. Add explicit negative-count policy before multiplication. |
| `nighantu` / `nighantu_srij` | `(2+3*c)*8+c*32` | **Already bounded in R35**, `c<=164703072086692424`, after clamping to >=1. Retain this exact `16+56c` proof; do not redo. |
| `nighantu` / `nighantu_vardh` | `oldcap*33+1` | Fits for an intact constructor-created map. **R36 now checks both `newm` and scratch allocation failure**; previous `newm[0]` null dereference was fixed. |
| `nighantu` / `nighantu_mil` | `scap*33+1` | Fits if scap really equals the bounded source-map capacity. Validate the explicit capacity against the handle; allocation failure remains unchecked. |
| `sangrah` / `rakh_samroop_diff`, `rakh_sangam` | each has `cap*33+1` and `bcap*33+1` (4 calls) | Validate both source capacities/handles. Arithmetic fits for legitimate maps, but allocation failure is independent. |
| `sangrah` / `rakh_sampat`, `rakh_bhed`, `rakh_asti_upasamuh` | each `cap*33+1` (3 calls) | Same invariant and failure checks. |
| `sangrah` / `rakh_tak_mala` | `cap*33+1`; `cap*32+1`; `cap*8` for ptrs; `cap*8` for lens (4 calls) | All fit under an intact map's bound; all allocation results need checks. Qword-cell output has a **different, larger** required extent. |
| `shreni` / `mil_shreni` | `n*8` | Validate actual input n and signed byte count; check scratch allocation before merge recursion. |
| `suchi` / `suchi_srij`, `avali_srij` | each `sz=c*8` (2 calls) | **Fixed in R35:** clamp >=1, prebound <=MAX/8, check allocation. Do not repeat. |
| `suchi` / `suchi_vardh`, `avali_pravesh` | each `ncap*8` after `ncap=cap*2` (2 calls) | **Fixed in R36** with old cap<=MAX/16 before growth; preserve old state when refusing. |

**Ten constants:** `suchi_srij` header 24 and `avali_srij` header 32; `roop_ank` 176, `roop_ank_aadhar` 560, `roop_varg_ank` 32, `roop_sthir_mool` 176, `roop_chinhit` 32, `roop_sign_akshar` 32; `ank_tak_varna` 176 and `ank_tak_aadhar_varna` 560 in `vakyank`. **No arithmetic-overflow fix is needed for those constants.** Some callers still lack allocation-failure checks; classify that separately.

### Why valid-map scratch buffers are not positive-wrap defects

For `C <= floor((MAX-16)/56)=164703072086692424`, `33*C+1 <= 5435201378860849993 < MAX`. The map constructor's bound therefore proves scratch formulas fit **when the explicit cap matches intact metadata**. Claiming otherwise would be a false positive. Malformed raw handles or mismatched cap arguments are a separate validation boundary. Do not add checked multiplication in every hash-probe loop where a validated map invariant already proves the offset.

Similarly, a positive-wrap growth witness using old cap `2^60+1` is **outside** R35's constructor invariant. Within that invariant, excessively large growth may instead produce a negative byte count and rely on allocation refusal. R36's prebound makes refusal deterministic. Do not describe the forged-header counterexample as a naturally reachable capacity of a real constructed collection.

## Every explicit scaled-index family found

Repeated copies of the same stride within a function are grouped. The inventory JSON gives exact function lists and expression patterns; implicit qword `a[i]` is addressed by the common extent rule, not counted as a written multiplication.

| Module | Functions with multiplication feeding an explicit address/index or loop shape | Required boundary proof |
|---|---|---|
| `brihat` | `brihat_shunyank`, `brihat_ank_se_int`, `brihat_ank_tak_int`, `brihat_pratilip`, `brihat_tul`, `brihat_yuj`, `brihat_nyun`, `brihat_gun`, `brihat_asti_shunyank`, `brihat_bhajshesh`, `brihat_shesh` | All `base+i/j/k/m*8` variants; multiplication uses `(i+j)*8`, `(i+c)*8`, and `c*2` loop sizes. Check n/2n real extents once; prove index sums within them before entering loops. Digit products such as digit*digit are bounded numeric values, not address offsets. |
| `mala` | `mala_sangrah`, `mala_grah`, `mala_purn`, `mala_pratilip`, `mala_yog`, `mala_sangrah_surakshit`, `mala_grah_surakshit` | `base+j*8`; the two `surakshit` routines only test `0<=j<n`. A caller-supplied huge n is not proof of byte extent. Either require trusted construction metadata or validate a bounded span. Raw APIs remain explicitly caller-responsible. |
| `khand` | `khand_bhed`, `khand_yuj` | `dst+(wpos+1)*8`, `p+rpos*8`. Validate nonnegative segment lengths, accumulation addition, cell scaling and destination capacity including terminator. Do not multiply bytes by 8 by mistake. |
| `varna` | `varna_gan` | `h+pos*8`. Source cell extent and loop progress must bound pos before scaling. |
| `nighantu` | `nighantu_kunji_sam`, `nighantu_koshtha_likh`, `nighantu_khip`, `nighantu_grah`, `nighantu_apanay`, `nighantu_rikta`, `nighantu_vardh`, `nighantu_grah_mool`, `nighantu_mulya`, `nighantu_kunjika`, `nighantu_kunjika_ashtak` | Map indices `2+2*cap+slot`, bytes `(2+3*cap)*8+slot*32`, plus variants for i/j/oldcap. They fit for validated cap/slot. **`nighantu_kunjika` additionally emits `out+(wpos+1)*8`**, not protected by map storage size. |
| `sangrah` | `rakh_tak_mala` | `out+(wpos+1)*8`. Packed keys become qword cells: worst-case output including a trailing cell is `(33*cap+1)*8 = 264*cap+8`. Validate output extent independently of the map's `56*cap+16` allocation. |
| `samanvaya` | `pehchan`, `vivartana`, `matrika_yoga`, `skalar`, `matrika_gunana`, `nishan`, `rekha_manak` | Shapes `n*n,m*n,n*p,m*p` and indices `i*n+j,j*m+i,i*n+k,k*p+j,i*p+j,i*n+i`. **Best general checked-multiply candidates:** validate nonnegative dimensions, checked products and actual `kosh_len` before any output. Then inner row indices follow from proved shapes. A wrapped small index may pass the existing kosh index guard. |

### New discriminating witnesses, deliberately not executed as memory accesses

- **Negative constructor count:** `mala_nava(-2305843009213693951)` has count `-2^61+1`. The R35/R36 upper-bound check passes because the count is negative; low 64 bits of `count*8` are **8**, so `sz<0` also misses it. This remains in R36 source. Recommend rejecting negative counts explicitly; do not claim a native allocation/result was observed here.
- **Matrix product:** `m=4611686018427387905` (`2^62+1`), `n=4`: mathematical cells are `2^64+4`; machine product is **4**. The `matrika_yoga` loop can see a four-cell shape after wrapping. This is a demonstrated arithmetic counterexample and missing dimension-validation issue, not a valid gigantic matrix that was allocated or a native run.
- **Raw stride:** `(2^61+1)*8` aliases byte offset 8. Existing `index<n` checks against an untrusted n do not establish safety. Invalid extent metadata remains a caller-contract violation until a checked span boundary exists.

## What should NOT call the checked helper

`ganit` includes intentional wrapping factorial/sum behavior and an LCG modulo 2^64. Changing it would change accepted numerical semantics. `gudh`'s FNV uint32 intermediate times 16777619 fits int64 and is reduced modulo 2^32. `anukram` byte packing/unpacking products have small, provable bounds; these are not address products. `roop`'s integer power-of-ten loop is clamped to nine digits; `vakyank` bounds mantissa length and decimal parser intermediates (including an intentional route to INT64_MIN). Floating products in `kalana`, `madhava`, `sankhyiki`, and matrix value arithmetic are not signed integer size checks. `ank`, `chandas`, `sadhan`, and other `ganita` math need numerical-contract decisions, not blanket allocator hardening. `patra` has no multiplication; `phal` delegates to checked functions and uses caller-owned fixed result cells.

**All 24 modules accounted for:** seven allocation-bearing variable-size modules, plus scaled-index modules, constant-buffer modules and the numerical/no-targeted-product exclusions in the inventory. This does not certify every implicit raw pointer access, every arithmetic operation, or every caller contract as safe.

## Adjacent defects and implementation order

1. **Add domain/shape checks**, including negative `mala_nava`, matrix dimension products, and strict byte/cell unit distinctions. Preflight before reads or writes; don't partly update output and then discover overflow.
2. **Define failure conventions for unchecked allocations** in `aadhar`, `brihat`, `shreni`, `nighantu_mil`, `sangrah`, and fixed scratch formatters. A count-returning function cannot silently repurpose zero without reviewing ambiguity. R36 has already fixed `nighantu_vardh`.
3. **Addition-only bounds deserve a separate ticket:** `anukram` tests `p+8>cap`, `p+8+cnt>cap`, `p2+cnt>cap`; these can wrap. Require `0<=p<=cap`, then compare widths with `cap-p`. Checked multiplication alone cannot fix them. This is outside the literal multiplication request but the same validate-before-address rule.
4. Use isolated, small arithmetic/shape regression programs. Check both bounded and unlimited-address-space environments without actually allocating huge buffers. Record old-vs-new deliberate failures. Production native tests, library failure contract and golden changes remain Claude/Muse/owner work.

## Executed evidence

`ROUND-102-CONTROLS.py` was actually run with Python. **69 assertion groups PASS / 0 FAIL**, including a source-equivalent model of `ganita_janchit_gun` tested against exact big integers on **20,256 input pairs**, positive-wrap/negative-domain/shape witnesses, safe-map and constant-size proofs, and the separate WS2 proposed byte/stack model. Raw stdout is `ROUND-102-CONTROLS-RAW.txt`. **No allocation or pointer dereference; no native Sutram compiler/library test and no Windows execution.** The model verifies arithmetic and the proposed contract, not integration of a library change.
