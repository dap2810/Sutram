# R68 audit — lib/phal, nighantu, sangrah, chandas, ganit, kalana

Read-only audit of `/home/claude/sutram/lib/{phal,nighantu,sangrah,chandas,ganit,kalana}.smlib`
against the census `census-phal-nighantu-sangrah-chandas-ganit-kalana.txt` (30 prakriya, 61 write
sites). Every body was read in full; helper semantics were taken from `lib/khand.smlib`
(`khand_mukt` :61-76 writes cells `dst[0..n-1]` plus a 0 cell at `dst[n]`; `khand_tul` :438 reads
`min(an,bn)` bytes) and `lib/gudh.smlib` (`fnv1a` :15-27 reads bytes `0..len-1`, returns 0..2^32-1).

## Map layout facts used throughout (nighantu.smlib :11-21, :107-125)

A map `m = nighantu_srij(c)` (c clamped to >= 1) is ONE `nirmmita(sz)` block,
`sz = (2 + 3c)*8 + 32c` bytes (:114). Cells: `m[0]` = c, `m[1]` = count, `m[2+i]` state,
`m[2+c+i]` keylen, `m[2+2c+i]` val (i in 0..c-1), then the key region at byte offset
`(2+3c)*8 + 32*slot`, 32 bytes per slot. Last valid cell index = `1 + 3c`; last valid byte index =
`sz - 1 = (2+3c)*8 + 32c - 1`.

**Where the write index comes from.** Every slot index is derived from
`nighantu_kunji_gudh` = `fnv1a(key, kn) % cap` (:38-42; fnv1a is non-negative, so the result is in
`0..cap-1`), then advanced by `idx = idx + 1; yadi (idx >= cap) { idx = 0 }` (:96-97, :148-149,
:199-200, :235-236). So the slot IS reduced modulo `cap` and wraps. The key length is clamped
`kn > 32 -> 32` and `kn < 0` is rejected before any write (:89-91, :137-139). **BUT `cap` here is
the caller's PARAMETER, not the header `m[0]`.** Nothing in `nighantu_khip`, `nighantu_apanay`,
`nighantu_grah`, `nighantu_antah`, `nighantu_grah_mool`, `nighantu_mil`'s `dcap/scap`, or the
sangrah `cap/bcap` arguments compares the parameter with `m[0]`. Only `nighantu_rikta`,
`nighantu_mulya`, `nighantu_kunjika`, `nighantu_kunjika_ashtak`, `nighantu_vardh` (`oldcap = m[0]`,
`nc = newm[0]`) and the sangrah `out` writes (`ocap = out[0]`) read the capacity from the header.
The contract for `nighantu_rikta` (:241-243, "no cap parameter, so a mismatched cap cannot corrupt
the map") shows the authors know this. Consequence: every WITHIN verdict below for a `(m, cap)`
function is **conditional on `cap == m[0]`**; with `cap > m[0]` the key-region base
`(2+3cap)*8` alone moves past the block end. Exact OVER input (never required by any contract to
be rejected):

```
m = nighantu_srij(1)                       # block = (2+3)*8 + 32 = 72 bytes
nighantu_khip(m, 2, "a", 1, 5)             # fnv1a("a") = 0xe40c292c, % 2 = 0 -> slot 0
   -> nighantu_koshtha_likh(m, 0, 2, ...): base = (2+6)*8 = 64; writes bytes 64..95;
      bytes 72..95 are 24 bytes past the 72-byte block (and m[4], m[6] land on the
      real map's val[0] / key bytes).
```

I audited every call site in the repo for this (see Part B, section B.5): **no caller passes a
cap different from its `nighantu_srij`/`rakh_srij` cap** except deliberate `cap = 0` edge tests
(rejected by `cap < 1`) and `r39_scratch_from_set.sm` passing `1` to functions that do not use
that argument for writes. The hazard is therefore latent, not exercised.

---

## Part A — every (prakriya, buffer)

Columns: `module | prakriya | buffer | unit | MAX INDEX WRITTEN (worst case; max READ of caller
buffers past given count if any) | CAPACITY STATED / own size | VERDICT | note`.

### chandas.smlib

| module | prakriya | buffer | unit | max index written | capacity stated | VERDICT | note |
|---|---|---|---|---|---|---|---|
| chandas | meru_mala(a, n) :98-104 | a (PARAM) | cell | `n` (loop `i = 0; yavat (i <= n)`, :99-100); no write when n < 0 | ":97 fills a[0..n]" = n+1 cells | WITHIN | writes exactly the stated range; caller must give n+1 cells, which "a[0..n]" states. No reads of caller buffers. |

### ganit.smlib

| module | prakriya | buffer | unit | max index written | capacity stated | VERDICT | note |
|---|---|---|---|---|---|---|---|
| ganit | ganit_yadricch(state) :162-166 | state (PARAM) | cell | 0 (:164) | ":156 `state` is a 1-cell array" | WITHIN | reads state[0] only. |

### kalana.smlib

| module | prakriya | buffer | unit | max index written | capacity stated | VERDICT | note |
|---|---|---|---|---|---|---|---|
| kalana | bahu_mula(c, lo, hi, ok) :120-144 | ok (OTHER: `kosh dasham`) | cell | 0 (:124,:125,:126,:133,:142) | ":116 `ok` must already contain ONE element" | WITHIN | `kosh` is compiler bounds-checked (brief), so a violated precondition traps rather than corrupting. `c` is only read via `bahu_ganana` (`c[n-1]..c[0]`, n = kosh_len, :104-110), no read past count. |

### nighantu.smlib

| module | prakriya | buffer | unit | max index written | capacity stated / own size | VERDICT | note |
|---|---|---|---|---|---|---|---|
| nighantu | nighantu_koshtha_likh(m, slot, cap, key, keyn, val) :62-77 | m (PARAM) | cell | `2 + 2*cap + slot` (:67) = `1 + 3cap` at slot = cap-1 | layout :11-17: `2 + 3*m[0]` cells | WITHIN (given slot < cap, cap == m[0]) | internal helper; callers (`nighantu_khip` :152) pass slot in 0..cap-1 and keyn <= 32. |
| nighantu | nighantu_koshtha_likh | m (PARAM) | byte | `base + 31` with `base = (2+3cap)*8 + 32*slot` (:64, loops :68-75 cover i = 0..31 exactly: first `i < keyn`, then `i < 32` continuing from i = keyn) = `sz - 1` at slot = cap-1 | layout: sz = (2+3cap)*8 + 32cap bytes | WITHIN (given keyn <= 32, cap == m[0]) | reads `key[0..keyn-1]` (:69) — never past the count given. If keyn > 32 were passed un-clamped the first loop would write 32+ bytes into the NEXT slot; all callers clamp (:139). |
| nighantu | nighantu_srij(cap) :107-125 | m (OWN `nirmmita(sz)`) | cell | `2 + i`, i < c -> `1 + c` (:120-121); plus m[0], m[1] | own sz = (2+3c)*8 + 32c bytes = 2+3c cells + key region | WITHIN | overflow guard :113 is exact: 56*164703072086692424 + 16 = 9223372036854775760 fits; +1 wraps. Only state cells are zeroed (keylen/val/key bytes untouched) — not a bounds issue. |
| nighantu | nighantu_khip(m, cap, key, keyn, val) :132-155 | m (PARAM) | cell | direct: `2 + 2*cap + slot` (:142, slot from `nighantu_anwesh` in 0..cap-1) and `m[1]` (:153); via `nighantu_koshtha_likh(m, idx, ...)` (:152) idx in 0..cap-1 (:145-151) -> worst `1 + 3cap` cells / `sz - 1` bytes | layout, via parameter cap | WITHIN (given cap == m[0]) | cap < 1 and keyn < 0 rejected before any write (:137-138); kn clamped to 32 (:139). Full table: loop :147-151 returns 0 when idx wraps to start. Reads of caller `key`: bytes 0..kn-1 only (fnv1a, khand_tul, copy). Contract never says cap must equal m[0]: see header hazard. |
| nighantu | nighantu_apanay(m, cap, key, keyn) :181-239 | m (PARAM) | cell | `2 + pos` (:196, pos in 0..cap-1), `m[1]` (:197), `2 + 2*cap + i` (:224, i = pos or a previous j, all in 0..cap-1 by the wrap :199-200, :235-236), `2 + j` (:232) -> worst `1 + 3cap` | layout, via parameter cap | WITHIN (given cap == m[0]) | no explicit cap/keyn guard, but `nighantu_anwesh` returns -1 for cap < 1 or kn < 0 (:89-90) -> `pos < 0 -> return 0` before any write (:195). Loop :201 terminates: the hole at i is always state 0, so j reaches it after at most cap-1 steps. `m[1] - 1` cannot go negative because pos >= 0 implies a live entry. |
| nighantu | nighantu_apanay | m (PARAM) | byte | `base_i + 31`, base_i = (2+3cap)*8 + 32i, i <= cap-1 (:221, :228-231) = `sz - 1` | layout | WITHIN (given cap == m[0]) | reads bytes `base_j + 0..31` (:229) and `fnv1a(m + base_j, kl)` with kl = stored keylen <= 32 (:202-205): inside slot j. |
| nighantu | nighantu_rikta(m) :250-269 | m (PARAM) | cell + byte | cells `2 + 2*cap + i`, i < cap = m[0] -> `1 + 3cap`; bytes `(2+3cap)*8 + 32i + 31` -> `sz - 1` | capacity read from m[0] (:251) | WITHIN (unconditional) | the one mutator that cannot be mis-capped. |
| nighantu | nighantu_vardh(m, newcap) :279-305 | tmp (OWN `nirmmita(oldcap*33 + 1)`, oldcap = m[0]) | byte | via `nighantu_kunjika_ashtak(m, tmp)` (:296): `Σ(1+kl_i) - 1 <= 33*oldcap - 1` | own 33*oldcap + 1 | WITHIN | 2 bytes spare. Reads `tmp[pos]`, `tmp[pos+1..]` only within what was written. |
| nighantu | nighantu_vardh | newm (OTHER: fresh map, written via `nighantu_khip(newm, nc, ...)` :300 with `nc = newm[0]` :293) | cell+byte | as nighantu_khip with cap == newm[0] | newm's own layout | WITHIN | `newcap < n` rejected (:290), so every key fits (linear probing fills every slot). `m[2 + 2*oldcap + slot]` (:300) slot >= 0 guaranteed (key just enumerated); oldcap = m[0], consistent. |
| nighantu | nighantu_mil(dst, dcap, src, scap) :333-353 | tmp (OWN `nirmmita(src[0]*33 + 1)`) | byte | `<= 33*src[0] - 1` (:336) | own 33*src[0] + 1 | WITHIN | R39: sized from src[0], not scap. |
| nighantu | nighantu_mil | dst (PARAM, written via `nighantu_khip(dst, dcap, ...)` :345) | cell+byte | as nighantu_khip with cap = dcap | dst layout, via parameter dcap | WITHIN (given dcap == dst[0]) | reads src via `nighantu_grah(src, scap, ...)` (:344): with scap != src[0] the READ `src[2 + 2*scap + slot]` can leave src's block. Same header hazard. |
| nighantu | nighantu_mulya(m, out) :360-372 | out (PARAM) | cell | `n` before increment, n counts live slots -> max `nighantu_maap(m) - 1 <= cap - 1` (:364-368) | ":357-358 Caller allocates cap cells" | WITHIN | cap = m[0] (:361). |
| nighantu | nighantu_kunjika(m, out) :383-406 | out (PARAM) | cell | `out[wpos] = kl` (:395) then `khand_mukt(m+base, kl, out + (wpos+1)*8)` (:399) writes cells `wpos+1 .. wpos+kl` AND a 0 cell at `wpos+1+kl`; wpos advances by 1+kl. Max index written = **`Σ_live (1 + kl_i)`** (the last terminator cell) `<= 33*cap`. kl = 0 key: khand_mukt's `cnt <= 0` branch writes `dst[0]` = out[wpos+1], same formula. | **none** — contract :374-382 names the shape but no size | **UNDOC** | Needed capacity: `Σ(1+kl_i) + 1` cells, worst case **`33*cap + 1` cells = (33*cap+1)*8 bytes**. The trailing 0 cell is mentioned only in a body comment (:396-397, "or it trails harmlessly"), not in the contract or module header, so it does not qualify as TERMINATOR under the brief; it is an extra write one cell past the segment data. Reads of m: key bytes within slot. |
| nighantu | nighantu_kunjika_ashtak(m, out) :417-441 | out (PARAM) | byte | `wpos` (:429) and `wpos + 1 + k`, k < kl (:432); final wpos = Σ(1+kl_i); max index = `Σ(1+kl_i) - 1 <= 33*cap - 1` | ":411 Caller allocates cap * 33 bytes" | WITHIN | no terminator (contract :410 says so, body agrees). kl <= 32 because `nighantu_koshtha_likh` only ever stores the clamped kn and negative keyn is rejected. |

Read-only functions (not in census, noted for the cap hazard): `nighantu_anwesh` :85-101,
`nighantu_kunji_sam` :47-54, `nighantu_grah` :159-166, `nighantu_antah` :169-174,
`nighantu_grah_mool` :312-319 read `m[2+idx]`, `m[2+cap+slot]`, `m[2+2cap+slot]` and key bytes at
`(2+3cap)*8 + 32*slot` with the PARAMETER cap; with cap > m[0] these are reads past the block.

### phal.smlib

Module header :4: "A Result is a 2-cell mala supplied by the caller: [ok, value]". Every function
below writes `o[0]` and/or `o[1]` of `vitti o = out` and nothing else; the `ganita_janchit_*`
callees (ganita.smlib :217-239, :243-265, :270-305, :307-324, :328-345, :419-436, :442-458,
:534-545) write only `okp[0]`.

| module | prakriya | buffer | unit | max index written | capacity stated | VERDICT | note |
|---|---|---|---|---|---|---|---|
| phal | phal_siddhi(out, v) :33-38 | out | cell | 1 (:35-36) | 2-cell mala (:4) | WITHIN | |
| phal | phal_dosh(out) :41-46 | out | cell | 1 (:43-44) | 2-cell mala | WITHIN | |
| phal | phal_se_siddhi(out, v, ok) :69-79 | out | cell | 1 on both branches (:72-73, :75-76) | 2-cell mala | WITHIN | reads `ok[0]` only (1-cell ok convention). |
| phal | phal_janchit_yuj(out, a, b) :85-97 | out | cell | 1 (:92/:94); `o[0]` written by callee | 2-cell mala | WITHIN | |
| phal | phal_janchit_nyun(out, a, b) :100-112 | out | cell | 1 (:107/:109) | 2-cell mala | WITHIN | |
| phal | phal_janchit_gun(out, a, b) :115-127 | out | cell | 1 (:122/:124) | 2-cell mala | WITHIN | |
| phal | phal_janchit_bhaj(out, a, b) :130-142 | out | cell | 1 (:137/:139) | 2-cell mala | WITHIN | |
| phal | phal_janchit_shesh(out, a, b) :145-157 | out | cell | 1 (:152/:154) | 2-cell mala | WITHIN | |
| phal | phal_janchit_ghat(out, a, e) :161-170 | out | cell | 1 (:165/:167) | 2-cell mala | WITHIN | callee re-uses `okp` as the ok cell of the inner `ganita_janchit_gun` (:430) — still index 0. |
| phal | phal_janchit_kramgun(out, n) :174-183 | out | cell | 1 (:178/:180) | 2-cell mala | WITHIN | |
| phal | phal_janchit_nirapeksh(out, a) :187-196 | out | cell | 1 (:191/:193) | 2-cell mala | WITHIN | |

### sangrah.smlib

All set ops enumerate with `nighantu_kunjika_ashtak(x, tmpx)` into a scratch of `x[0]*33 + 1`
bytes (R39, :4), which needs at most `33*x[0]` bytes -> WITHIN with 1 byte spare in every case.
All writes into `out` go through `nighantu_khip(out, ocap, ...)` with `ocap = out[0]` (:64, :97,
:127, :149), so `out` is written only inside its own block (the cap is read from the header; a too
small `out` loses elements, :20-23, it is never overrun).

| module | prakriya | buffer | unit | max index written | capacity stated / own size | VERDICT | note |
|---|---|---|---|---|---|---|---|
| sangrah | rakh_samroop_diff(a, cap, b, bcap, out) :63-92 | tmpa (OWN `a[0]*33+1`) | byte | `<= 33*a[0] - 1` (:68) | own | WITHIN | |
| sangrah | rakh_samroop_diff | tmpb (OWN `b[0]*33+1`) | byte | `<= 33*b[0] - 1` (:69) | own | WITHIN | if tmpa != 0 and tmpb == 0 the function returns -1 and leaks tmpa (not a bounds issue). |
| sangrah | rakh_samroop_diff | out (PARAM via nighantu_khip, cap = out[0]) | cell+byte | within out's layout | ":60 capacity >= cap + bcap" (advisory: too small = dropped elements) | WITHIN | `cap`/`bcap` are used only for READS `nighantu_antah(b, bcap)` / `(a, cap)` (:75, :85): a mismatch is a read-past hazard on a/b, not a write. |
| sangrah | rakh_sangam(a, cap, b, bcap, out) :96-121 | tmpa (OWN) | byte | `<= 33*a[0] - 1` | own | WITHIN | |
| sangrah | rakh_sangam | tmpb (OWN) | byte | `<= 33*b[0] - 1` | own | WITHIN | |
| sangrah | rakh_sangam | out (PARAM via nighantu_khip, ocap = out[0]) | cell+byte | within out's layout | ":95 capacity >= cap + bcap" | WITHIN | `cap` and `bcap` are **unused** in this body. |
| sangrah | rakh_sampat(a, cap, b, bcap, out) :126-143 | tmpa (OWN) | byte | `<= 33*a[0] - 1` | own | WITHIN | |
| sangrah | rakh_sampat | out (PARAM via nighantu_khip, ocap = out[0]) | cell+byte | within out's layout | ":124 capacity >= min(cap, bcap)" | WITHIN | `cap` unused; `bcap` read-only via nighantu_antah (:136). |
| sangrah | rakh_bhed(a, cap, b, bcap, out) :148-165 | tmpa (OWN) | byte | `<= 33*a[0] - 1` | own | WITHIN | |
| sangrah | rakh_bhed | out (PARAM via nighantu_khip, ocap = out[0]) | cell+byte | within out's layout | ":146 capacity >= cap" | WITHIN | `cap` unused; `bcap` read-only (:158). |
| sangrah | rakh_asti_upasamuh(a, cap, b, bcap) :194-210 | tmpa (OWN) | byte | `<= 33*a[0] - 1` | own | WITHIN | `cap` unused; `bcap` read-only (:203). |
| sangrah | rakh_tak_mala(s, cap, out) :217-278 | tmp (OWN `s[0]*33+1`) | byte | `<= 33*s[0] - 1` (:224) | own | WITHIN | `cap` parameter is **unused** anywhere in the body (R39). |
| sangrah | rakh_tak_mala | scratch (OWN `s[0]*32+1`) | byte | `woff + k`, total bytes copied = Σ kl_i <= 32*nk <= 32*s[0] -> max `32*s[0] - 1` (:242-246) | own 32*s[0]+1 | WITHIN | 2 bytes spare. khand_tul reads `scratch + ptrs[j]` for `lens[j]` bytes: inside. |
| sangrah | rakh_tak_mala | ptrs (OWN `s[0]*8`) | cell | `i < nk <= s[0]` (:239) and `j + 1` with `j < nk - 1 - i`, i >= 0 -> `<= nk - 1 <= s[0] - 1` (:257-258) | own s[0] cells | WITHIN | nk = 0 or 1: outer loop `i < nk - 1` does not run (:252). |
| sangrah | rakh_tak_mala | lens (OWN `s[0]*8`) | cell | same bounds as ptrs (:240, :260-261) | own s[0] cells | WITHIN | |
| sangrah | rakh_tak_mala | out (PARAM) | cell | `out[wpos] = lens[i]` (:272), then `khand_mukt(scratch+ptrs[i], lens[i], out + (wpos+1)*8)` (:273) writes cells `wpos+1 .. wpos+lens_i` and a 0 at `wpos+1+lens_i`; max index = **`Σ(1 + l_i)`** (the trailing 0 cell) `<= 33*nk <= 33*s[0]` | **none** — contract :212-216 names the shape only | **UNDOC** | Needed capacity: `Σ(1+l_i) + 1` cells, worst case **`33*s[0] + 1` cells**. The trailing 0 cell is documented only in a body comment (:267-268); the parameter `cap` plays no part, so the needed size is in terms of `s[0]` (which equals the cap the caller gave rakh_srij). |

Reads of caller buffers past the given count: **none** in these six modules. All key reads are
bounded by the (clamped) length argument; fnv1a/khand_tul/khand_mukt take explicit lengths; no
function in these modules assumes a 0 terminator on a caller string.

---

## Part B — callers

B.1 and B.2 are the required ones (PARAM buffers with a non-WITHIN verdict). B.3-B.4 are extra
checks of the two "caller allocates N" dumpers whose stated capacity is a formula. B.5 is the cap
consistency scan for the header hazard. Scope searched: `examples/*.sm` (no matches),
`tests/**/*.sm` minus `tests/negative/`, `lib/*.smlib`, `tools/proof_props.py`,
`tools/proof_lib.py` (no matches). `tests/r38/test_fail_alloc.py` is outside the brief's list but
was found by grep and is included as an extra row.

"needed" = `Σ(1+len) + 1` cells for the actual contents at the call (worst case for that set's
capacity in parentheses).

### B.1 nighantu_kunjika(m, out) — UNDOC; needs Σ(1+kl_i)+1 cells (<= 33*cap+1)

| file:line | call | buffer allocation | needed | OK / SHORT |
|---|---|---|---|---|
| tests/stdlib/map_remove.sm:33 | `nighantu_kunjika(m, out)` | `out = nirmmita(16 * 8)` (:5) = 16 cells | m (cap 8) holds 1 key "abaed" (5) after two removals: 1+5+1 = 7 cells (worst 265) | OK |
| tests/stdlib/r11_nighantu_edges.sm:15 | `nighantu_kunjika(m, keys)` | `keys = nirmmita(8 * 16)` (:14) = 128 bytes = 16 cells | m (cap 1) holds "a": 1+1+1 = 3 cells (worst 34) | OK |
| tools/proof_props.py:953 (prop_map_keys_count) | `nk = nighantu_kunjika(m, out)` | `out = nirmmita(32*8)` (:945) = 32 cells | 5 keys from `_distinct_keys(rng, 5)` (:818-824, length 2..5): max Σ(1+5)*5 + 1 = **31** cells (worst for cap 16: 529) | OK (1 cell spare at the random worst case) |
| tools/proof_props.py:2034 (prop_map_keys_bytes_roundtrip) | `nighantu_kunjika(m, cells)` | `cells = nirmmita((32 * 33 + 1) * 8)` (:2022) = 1057 cells | 5 fixed distinct keys (1,5,3,4,32) + up to 6 random keys of 1..8: max (2+6+4+5+33) + 6*9 + 1 = 105 cells (worst 1057 — the caller used exactly the worst-case formula) | OK |

### B.2 rakh_tak_mala(s, cap, out) — UNDOC; needs Σ(1+l_i)+1 cells (<= 33*s[0]+1)

| file:line | call | buffer allocation | needed | OK / SHORT |
|---|---|---|---|---|
| tests/stdlib/set_intersect.sm:18 | `rakh_tak_mala(inter, 16, arr)` | `arr = nirmmita(64 * 8)` (:16) = 64 cells | inter = {fig, pear}: 4+5+1 = 10 | OK |
| tests/stdlib/set_union.sm:16 | `rakh_tak_mala(u, 32, arr)` | `arr = nirmmita(64 * 8)` (:14) = 64 cells | u = {pear, apple, fig}: 5+6+4+1 = 16 | OK |
| tests/stdlib/set_to_array.sm:11 | `rakh_tak_mala(s, 16, arr)` | `arr = nirmmita(64 * 8)` (:9) = 64 cells | {cherry, apple, banana}: 7+6+7+1 = 21 | OK |
| tests/stdlib/set_to_array.sm:27 | `rakh_tak_mala(e, 16, arr)` | same arr, 64 cells | empty set: 0 writes | OK |
| tests/stdlib/set_to_array.sm:32 | `rakh_tak_mala(one, 16, arr)` | same arr, 64 cells | {solo}: 5+1 = 6 | OK |
| tests/stdlib/set_difference.sm:18 | `rakh_tak_mala(diff, 16, arr)` | `arr = nirmmita(64 * 8)` (:16) = 64 cells | diff = {apple}: 6+1 = 7 | OK |
| tests/stdlib/r11_sets_lists.sm:29 | `rakh_tak_mala(t, 4, cells)` | `cells = nirmmita(8 * 16)` (:23) = 16 cells | {a, b}: 2+2+1 = 5 (the test then checks cells[4] == 0 terminator and cells[5] == 55 guard, :30-32) | OK |
| tests/stdlib/r11_sets_lists.sm:50 | `rakh_tak_mala(big, 512, sorted)` | `sorted = nirmmita(8 * 2048)` (:49) = 2048 cells | 512 elements: 26 of len 1 + 486 of len 2: 26*2 + 486*3 + 1 = 1511 | OK |
| tests/stdlib/r39_scratch_from_set.sm:25 | `rakh_tak_mala(s, 1, out)` | `out = nirmmita(300 * 40 * 8)` (:23) = 12000 cells | 200 elements of len 32: 200*33 + 1 = 6601 | OK (cap arg 1 != s[0] 300 is the deliberate R39 probe; `cap` is unused by the body) |
| tools/proof_props.py:1246 | `rakh_tak_mala(u1, 32, arr1)` | `arr1 = nirmmita(64*8)` (:1231) = 64 cells | union of 6 distinct words of len 2..5: max 6*6 + 1 = 37 | OK |
| tools/proof_props.py:1247 | `rakh_tak_mala(u2, 32, arr2)` | `arr2 = nirmmita(64*8)` (:1232) = 64 cells | same: max 37 | OK |
| tools/proof_props.py:1286 | `rakh_tak_mala(a, 16, arr0)` | `arr0 = nirmmita(64*8)` (:1273) = 64 cells | 4 keys len 2..5: max 25 | OK |
| tools/proof_props.py:1287 | `rakh_tak_mala(o1, 16, arr1)` | `arr1 = nirmmita(64*8)` (:1274) = 64 cells | o1 = a ∩ a, 4 keys: max 25 | OK |
| tools/proof_props.py:1321 | `rakh_tak_mala(d, 16, arr)` | `arr = nirmmita(64*8)` (:1313) = 64 cells | d = words[:4] - words[2:] = 2 keys: max 13 | OK |
| tools/proof_props.py:1392 | `rakh_tak_mala(a, 16, arr1)` | `arr1 = nirmmita(64*8)` (:1353) = 64 cells | a = 2 keys: max 13 | OK |
| tools/proof_props.py:1393 | `rakh_tak_mala(d, 16, arr2)` | `arr2 = nirmmita(64*8)` (:1354) = 64 cells | d = same 2 keys: max 13 | OK |
| tests/r38/test_fail_alloc.py:56 (extra, outside brief scope) | `rakh_tak_mala(a, 4, t)` | `t = nirmmita(64 * 8)` = 64 cells | a = {x, y}: 2+2+1 = 5 | OK |

### B.3 (extra) nighantu_kunjika_ashtak(m, out) — WITHIN, stated "cap * 33 bytes"

| file:line | call | buffer allocation | needed (content / stated) | OK / SHORT |
|---|---|---|---|---|
| tests/stdlib/r8_map_edges.sm:14 | `nighantu_kunjika_ashtak(n, out)` | `out = nirmmita(64)` (:12) = 64 bytes | n (cap 4) holds "ab": 3 bytes; stated bound 4*33 = 132 | OK by content; **68 bytes below the documented cap*33 bound** (not a SHORT: nothing written past 3) |
| tests/stdlib/map_clear.sm:17 | `nighantu_kunjika_ashtak(m, keys)` | `keys = nirmmita(200)` (:4) = 200 bytes | m (cap 8) is empty after rikta: 0 bytes; stated 264 | OK by content; **64 bytes below the documented bound** |
| tests/stdlib/map_keys_bytes.sm:26 | `nighantu_kunjika_ashtak(m, tmp)` | `tmp = nirmmita(8 * 33 + 1)` (:25) = 265 bytes | 48 bytes actual; stated 264 | OK |
| tests/stdlib/map_keys_bytes.sm:54 | `nighantu_kunjika_ashtak(m2, tmp)` | same tmp, 265 bytes | m2 cap 4 empty: 0; stated 132 | OK |
| tools/proof_props.py:2025 | `nighantu_kunjika_ashtak(m, tmp)` | `tmp = nirmmita(32 * 33 + 1)` (:2021) = 1057 | stated 1056 | OK |
| tools/proof_props.py:2252 | `nighantu_kunjika_ashtak(m, keys)` | `keys = nirmmita(600)` (:2238) | m cap 16 empty after rikta: 0; stated 528 | OK |
| lib/nighantu.smlib:296 (nighantu_vardh) | `nighantu_kunjika_ashtak(m, tmp)` | `tmp = nirmmita(oldcap * 33 + 1)`, oldcap = m[0] | 33*oldcap | OK |
| lib/nighantu.smlib:336 (nighantu_mil) | `nighantu_kunjika_ashtak(src, tmp)` | `nirmmita(src[0] * 33 + 1)` | 33*src[0] | OK |
| lib/sangrah.smlib:68, :69, :101, :102, :130, :152, :197, :224 | `nighantu_kunjika_ashtak(a|b|s, tmpa|tmpb|tmp)` | `nirmmita(x[0] * 33 + 1)` for the same x | 33*x[0] | OK (8 sites) |

### B.4 (extra) nighantu_mulya(m, out) — WITHIN, stated "cap cells"

| file:line | call | buffer allocation | needed | OK / SHORT |
|---|---|---|---|---|
| tests/stdlib/r11_nighantu_edges.sm:12 | `nighantu_mulya(m, vals)` | `vals = nirmmita(8 * 8)` (:11) = 8 cells | cap 1 | OK |
| tests/stdlib/containers21.sm:64 | `nighantu_mulya(m, vals)` | `vals = nirmmita(8 * 8)` (:63) = 8 cells | cap 8 | OK |
| tools/proof_props.py:2807 | `nighantu_mulya(m, vals)` | `vals = nirmmita(8 * 8)` (:2802) = 8 cells | cap 8 | OK |

### B.4b (extra) meru_mala(a, n) — WITHIN, stated "a[0..n]"

| file:line | call | buffer allocation | needed | OK / SHORT |
|---|---|---|---|---|
| tests/stdlib/chandas_meru_pankti.sm:4 | `meru_mala(a, 4)` | `mala a[10]` (:3, compiler-checked) | 5 cells | OK |

### B.5 cap-parameter consistency scan (header hazard from Part A)

Scripted scan (`/tmp/claude-0/-home-claude/e35834e8-b611-5238-b1df-59668dfdca3d/scratchpad/r68/capcheck.py`)
over the same scope: every `(buffer, cap)` argument pair passed to `nighantu_khip/grah/grah_mool/
antah/apanay`, `rakh_yuj/antah/apanay`, `nighantu_mil`, the five sangrah set ops and
`rakh_tak_mala` was compared with the cap the buffer got from `nighantu_srij`/`rakh_srij`/
`*_vardh` in the same file: 399 pairs. Mismatches after removing regex false positives (comment
lines, cross-function f-string `{cap}`, `nc = newm[0]`):

- `tools/proof_props.py:4546, :4550, :4551` — `nighantu_khip/grah/antah(m, 0, ...)` on a cap-8 map:
  deliberate cap-0 edge probes, rejected at `cap < 1` before any access. Safe.
- `tests/stdlib/r39_scratch_from_set.sm:25, :35` — `rakh_tak_mala(s, 1, out)`,
  `rakh_sangam(s, 1, e, 1, ...)` on cap-300 sets: deliberate; neither function uses that argument
  (rakh_tak_mala: unused; rakh_sangam: cap/bcap unused, out written via out[0]). Safe.
- No caller anywhere passes a cap LARGER than the map's real capacity. The OVER input in the
  header is reachable by API but not exercised in the repo.

---

## Part C — the numbers

- prakriya audited: **30** (chandas 1, ganit 1, kalana 1, nighantu 10, phal 11, sangrah 6).
- (prakriya, buffer) rows: **44** (chandas 1, ganit 1, kalana 1, nighantu 14, phal 11, sangrah 16;
  census-listed buffers plus the indirect `out`/`dst`/`newm` map writes that go through
  `nighantu_khip`).
- rows per verdict: **WITHIN 42**, **UNDOC 2**, TERMINATOR 0, OVER 0, NEG 0, UNSURE 0.
  - Of the 42 WITHIN, 6 are conditional on the caller's `cap` equalling the map header `m[0]`
    (nighantu_koshtha_likh x2, nighantu_khip, nighantu_apanay x2, nighantu_mil/dst); see header.
- UNDOC rows (both: caller-supplied cell buffer, no capacity in the contract, plus an unstated
  trailing 0 cell from `khand_mukt`):
  1. `nighantu.smlib:383 nighantu_kunjika(m, out)` — needs `Σ(1+kl_i) + 1` cells, worst
     `33*m[0] + 1` cells.
  2. `sangrah.smlib:217 rakh_tak_mala(s, cap, out)` — needs `Σ(1+l_i) + 1` cells, worst
     `33*s[0] + 1` cells (`cap` parameter unused).
- call sites checked: **41** (B.1: 4, B.2: 17 incl. one extra from tests/r38, B.3: 16, B.4: 3,
  B.4b: 1); cap-consistency pairs scanned: 399.
- call sites SHORT: **0**. Two sites are below the documented bound but safe by content
  (`tests/stdlib/r8_map_edges.sm:14` 64 < 132 bytes; `tests/stdlib/map_clear.sm:17` 200 < 264
  bytes); the tightest real margin is `tools/proof_props.py:953` (32 cells allocated, up to 31
  needed).
- OVER: none within the stated contracts. Latent OVER by API: any `nighantu_khip(m, cap, ...)`,
  `nighantu_apanay(m, cap, ...)` or `nighantu_mil(dst, dcap, ...)` with `cap > m[0]` (exact input
  in the header: `m = nighantu_srij(1); nighantu_khip(m, 2, "a", 1, 5)` writes bytes 72..95 of a
  72-byte block). Not exercised by any repo caller.
- NEG: none (`m[1] - 1` in nighantu_apanay :197 is guarded by pos >= 0; every loop variable starts
  at 0 and only increases or wraps to 0).
- SHORT: none.
