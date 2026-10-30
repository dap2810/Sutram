# R68 audit — lib/vakyank.smlib, lib/varna.smlib, lib/aadhar.smlib, lib/anukram.smlib

Read-only audit against /home/claude/sutram (nothing modified). Census: 19 prakriya, 108 write
sites. Every body was read in full; every loop's start/step and every branch was followed.
Line numbers are from the files as they stand today.

Conventions used in the verdict column (applied uniformly):
- WITHIN only when a capacity is actually stated (or the buffer is the function's own) and the
  maximum index is below it on every path.
- TERMINATOR when the contract states a capacity AND the terminator at index == count/width is
  the only thing that reaches or passes "count".
- UNDOC whenever the caller-supplied buffer has no stated capacity, even if the contract
  mentions a terminator (the needed size is given in the row). This is the case for all seven
  varna text writers, for ank_tak_aadhar_varna, and for anukram_grah_aayam_purva's dst.

## Part A — one row per (prakriya, buffer)

Columns: module | prakriya | buffer | unit | MAX INDEX WRITTEN (worst case; "READ" = reads of a
caller buffer past the given count) | CAPACITY STATED / own size | VERDICT | note

### aadhar.smlib

| # | module | prakriya | buffer | unit | max index written | capacity stated / own size | verdict | note |
|---|---|---|---|---|---|---|---|---|
| 1 | aadhar | brihat_ank_tak(x, n, base, out) :20 | out (PARAM) | cell | `0` when n < 1 (:28) or x == 0 (:40); otherwise `rlen - 1 <= 4n - 1` (:67, p < rlen). rlen = number of base-b digits of the value, value < 10^n < 2^(4n), so rlen <= 4n. No terminator written. READ: x[0..n-1] only (:36). | "at least 1 writable output cell when n <= 0, or at least 4*n cells when n > 0" (:16-17) | WITHIN | Bound assumes x holds canonical decimal digits 0..9 (an x with digit values > 9 represents a larger value and can need more than 4n digits — a precondition violation, not a bug). Base outside 2..16 and the two alloc-failure paths (-1) write nothing. |
| 2 | aadhar | brihat_ank_tak | w (OWN `nirmmita(c * 8)` :32) | cell | `c - 1` (:36 i < c; :57 k from c-1 down to 0) | own c cells | WITHIN | c >= 1 here (c < 1 returned at :27). |
| 3 | aadhar | brihat_ank_tak | rev (OWN `nirmmita(c * 4 * 8)` :45) | cell | `rlen - 1 <= 4c - 1` (:61) | own 4c cells | WITHIN | Same canonical-digit assumption as row 1; the :43-44 comment states the 4n bound. `c > 288230376151711743` guard (:31) keeps c*4*8 from wrapping. |
| 4 | aadhar | brihat_ank_se(d, count, base, x, n) :78 | x (PARAM) | cell | `n - 1` (:97, k < c); brihat_shunyank(dst, c) (:86 → brihat.smlib:17-18) also writes exactly cells 0..n-1. n <= 0 writes nothing. READ: d[0..count-1] only (:89). | "into n-digit bigint x" (:74) — n cells implied; no explicit "caller allocates" line | WITHIN | Base outside 2..16 returns before any write. Value overflow past 10^n is silently truncated (carry dropped at :98) — not a bounds issue. |

### anukram.smlib

| # | module | prakriya | buffer | unit | max index written | capacity stated / own size | verdict | note |
|---|---|---|---|---|---|---|---|---|
| 5 | anukram | anukram_khip_i64(out, pos, cap, v) :36 | out (PARAM) | byte | `pos + 7 <= cap - 1` (:52, i < 8), after guards `p < 0 → -1` (:41) and `p > c - 8 → -1` (:42) | header :11-12 "cap is the buffer size in bytes" | WITHIN | Caveat only: a cap in [-2^63, -2^63+7] makes `c - 8` wrap positive and the guard pass — an absurd input, listed for completeness. |
| 6 | anukram | anukram_grah_i64(buf, pos, cap, out) :61 | out (PARAM) | cell | `0` (:81) | "write the value into out[0]" (:60) — 1 cell | WITHIN | Reads buf bytes pos..pos+7 <= cap-1 (guards :66-67). |
| 7 | anukram | anukram_khip_aayam_purva(out, pos, cap, src, n) :88 | out (PARAM) | byte | `pos + 8 + n - 1 <= cap - 1` (:101, i < cnt; p2 = pos + 8), after guards n >= 0 (:94), pos >= 0 (:95), pos <= cap - 8 (:96), n <= cap - 8 - pos (:97). READ: src[0..n-1] only. | cap (header) | WITHIN | The inner anukram_khip_i64 cannot return -1 here (its guards were already satisfied). |
| 8 | anukram | anukram_grah_aayam_purva(buf, pos, cap, dst, out_n) :110 | dst (PARAM) | byte | `cnt - 1` (:125, i < cnt) where cnt is the length DECODED FROM buf, bounded only by `cnt <= cap - pos - 8` (:122). | none — "payload into dst" (:108); the header's cap applies to buf, not dst | UNDOC | dst must hold the decoded length: `cnt` bytes, i.e. `cap - pos - 8` bytes to be safe against any stream. A corrupt or hostile length up to cap - pos - 8 passes every check and is copied into dst. Reads buf bytes pos..pos+8+cnt-1 <= cap-1 (within cap). |
| 9 | anukram | anukram_grah_aayam_purva | out_n (PARAM) | cell | `0` (:128; also :81 via anukram_grah_i64) | "length into out_n[0]" (:108) — 1 cell | WITHIN | Written even when -1 is returned for a negative/oversize length (documented in header :15-16). |

### vakyank.smlib

| # | module | prakriya | buffer | unit | max index written | capacity stated / own size | verdict | note |
|---|---|---|---|---|---|---|---|---|
| 10 | vakyank | ank_tak_varna(n, out) :15 | out (PARAM) | cell | `20`: MIN path writes dst[0..20] (:22-42, terminator at 20); general path writes dst[0..pos+rlen] with pos <= 1, rlen <= 19 (INT64_MAX has 19 digits), terminator at `pos + rlen <= 20` (:77). rev-alloc failure writes dst[0] (:53). | ">= 22 cells" (:14); terminator at out[count] stated (:14) | WITHIN | The 22-cell constant covers the terminator (max count 20, max index 20, one spare cell). No caller buffer is read. Part B checks every caller against the constant 22. |
| 11 | vakyank | ank_tak_varna | rev (OWN `nirmmita(22 * 8)` :51) | cell | `rlen - 1 <= 18` (:62; 19 digits max; MIN handled before) | own 22 cells | WITHIN | |
| 12 | vakyank | varna_tak_ank(buf, n, ok) :84 | ok (PARAM) | cell | `0` (:88, :90, :99, :107, :111, :115, :121, :126) | "ok is a 1-cell mala" (:83) | WITHIN | READ past count: `src[0]` is read at :95 whenever n != 0, so for n < 0 (zero cells given) one cell is read; otherwise reads buf[0..n-1]. n < 0 returns 0 with ok = 1. |
| 13 | vakyank | ank_tak_aadhar_varna(n, base, out) :142 | out (PARAM) | cell | terminator index `rlen` = number of base-`base` digits of n = floor(log_base(n)) + 1 (:180); worst case `63` for n = 9223372036854775807, base 2 (:177 writes 0..62, :180 writes 63). n == 0: index 1 (:162). n < 0, bad base, or alloc failure: index 0 (:148, :153, :157). | none — "write n in any base 2..36 into out ... Returns count" (:138-139); no capacity line, terminator stated only for the bad-base path (:140) | UNDOC | Needed: `digits(n, base) + 1` cells; a caller that does not know n must give **64 cells**. No caller buffer is read. |
| 14 | vakyank | ank_tak_aadhar_varna | rev (OWN `nirmmita(70 * 8)` :146) | cell | `rlen - 1 <= 62` (:168/:170) | own 70 cells | WITHIN | |
| 15 | vakyank | varna_tak_ank_aadhar(buf, n, base, ok) :186 | ok (PARAM) | cell | `0` (:191, :193, :211, :215, :219, :224) | "Sets ok[0]" (:185) — 1 cell | WITHIN | Reads buf[0..n-1] only (:199); n <= 0 reads nothing. `d >= b` (:214) precedes `/ b` (:218), so base 0 cannot divide by zero. |
| 16 | vakyank | pad_vam(out, count, width, fill) :241 | out (PARAM) | cell | For count >= -1: `width` (terminator, :260); the shift loop (:251) tops out at `count - 1 + shift = width - 1`, the fill loop (:257) at `shift - 1 = width - count - 1 <= width`. For count < -1 (invalid): the fill loop reaches `width - count - 1 > width`. width <= count writes nothing (:246). READ: dst[0..count-1] (:251). | ">= width + 1 cells" (:239-240, corrected in R68) | TERMINATOR — the capacity line accounts for the +1 | Known row (contract already corrected). Conditional OVER only for a contract-invalid negative count: `pad_vam(out, -2, 5, f)` writes out[0..6] and out[5]=0, i.e. index 6 in a 6-cell (width+1) buffer. For every count >= -1 the body stays within width + 1. |
| 17 | vakyank | varna_tak_dashm(buf, n, ok) :274 | ok (PARAM) | cell | `0` (:278, :280, :289, :304, :308, :331, :335, :350, :360, :372, :380, :384, :394, :404, :411, :437) | "ok[0]" (:270) — 1 cell | WITHIN | READ past count: `src[0]` at :285 whenever n != 0, so n < 0 reads one cell of a zero-cell buffer (then falls to :349 seen == 0, ok = 0). Otherwise every read is guarded by p < cnt. |

### varna.smlib

| # | module | prakriya | buffer | unit | max index written | capacity stated / own size | verdict | note |
|---|---|---|---|---|---|---|---|---|
| 18 | varna | varna_pratisthap(src, sn, find, fn, repl, out) :189 | out (PARAM) | cell | terminator index = output length: `sn` when fn <= 0 (:205-209); otherwise `sn + m*(rlen - fn)` with m <= floor(sn/fn) matches, i.e. worst case `sn + floor(sn/fn) * max(0, rlen - fn)` (:227, :233, :238). rlen = length of repl up to its 0 cell (:198). sn < 0: index 0 only. READ: repl is scanned to its terminator (documented :185); src reads are guarded by `rpos + flen > slen` (:215). | "Caller allocates generously" (:188) — not a capacity | UNDOC | Needed: `sn + floor(sn/fn) * max(0, rlen - fn) + 1` cells (fn > 0), `sn + 1` cells (fn <= 0). |
| 19 | varna | varna_bhed(src, sn, sep, sepn, parts, maxparts) :248 | parts (PARAM) | cell | `sn` for sn >= 0: sn == 0 → index 0 (:257); sepn <= 0 → `1 + sn - 1 = sn` (:263, :266); main loop writes `nseg + sum(seglen)` cells where the written segments are disjoint pieces of src separated by >= 1 cell each, so total <= sn + 1 cells, max index `sn` (e.g. "a,b" → [1,a,1,b]; "a," → [1,a,0] via :322). maxparts caps nseg but never raises the bound. sn < 0: index 0 only (:263 or :305 with a negative length). No terminator. | none (:242-247 describe the layout, not a size) | UNDOC | Needed: `sn + 1` cells. Side note: the sn == 0 path (:257) and sepn <= 0 path (:263) write parts[0] and return 1 even when maxparts == 0 — a 0-cell parts buffer is written. |
| 20 | varna | varna_yuj(parts, count, sep, sepn, out) :334 | out (PARAM) | cell | terminator index = `sum_{i<count} len_i + max(0, count - 1) * max(0, sepn)` (:348, :356, :363), where len_i are the lengths read from parts. count <= 0: index 0. | none ("Returns new count" :333) | UNDOC | Needed: that sum + 1 cells. READ: parts[0 .. sum(1 + len_i) - 1] — the lengths come from parts itself, so a count larger than the segments actually present reads past the data the caller filled. |
| 21 | varna | varna_chhid(src, sn, out) :369 | out (PARAM) | cell | terminator index `hi - lo <= sn` (:394 k < hi, :398); equals sn when src has no leading/trailing spaces. sn < 0: index 0 (:398 with wpos 0). | none ("Returns new count" :368) | UNDOC | Needed: `sn + 1` cells. Reads src[lo], src[hi-1] only inside 0..sn-1 (:376/:385 guards). |
| 22 | varna | varna_unnat(src, sn, out) :405 | out (PARAM) | cell | `sn` (:419 i < slen, :422 terminator at slen); sn < 0: index 0 (:411). | none (:402-404 states only the sn < 0 behaviour) | UNDOC | Needed: `sn + 1` cells. Reads src[0..sn-1]. |
| 23 | varna | varna_avanat(src, sn, out) :427 | out (PARAM) | cell | `sn` (:441, :444); sn < 0: index 0 (:433). | none — "NUL-terminated" is stated (:426) but no capacity | UNDOC | Needed: `sn + 1` cells. Reads src[0..sn-1]. |
| 24 | varna | varna_viparyay(src, sn, out) :506 | out (PARAM) | cell | `sn` (:521/:522 i < j < sn, :527 n/2, :529 terminator at n); sn <= 0: index 0 (:514). | none — "Writes a 0 terminator cell at out[sn]" (:503-504) states the index but no "caller allocates" line | UNDOC | Needed: `sn + 1` cells (derivable from the contract's own words, so arguably the best-documented of the seven). Reads src[0..sn-1]. In place (src == out) is safe as stated. |

Reads of caller buffers past the given count, collected: varna_tak_ank :95 and varna_tak_dashm
:285 read `buf[0]` when n < 0 (contract-invalid count); varna_pratisthap :198 reads repl to its 0
terminator (documented); varna_yuj :344-348 trusts the lengths stored in parts. No other
function reads past its count.

## Part B — call sites

Functions needing Part B: ank_tak_varna (constant ">= 22 cells"), pad_vam (TERMINATOR,
width + 1), ank_tak_aadhar_varna (UNDOC), anukram_grah_aayam_purva dst (UNDOC), varna_pratisthap,
varna_bhed, varna_yuj, varna_chhid, varna_unnat, varna_avanat, varna_viparyay (all UNDOC).
Searched: examples/*.sm, tests/**/*.sm (tests/negative/ skipped — it contains no call anyway),
lib/*.smlib (no lib module calls any of these; the only lib hits are comments), tools/proof_props.py
(embedded programs), tools/proof_lib.py (no references at all). nirmmita memory is zeroed
(Claude-to-Sarvam/R61-00-KSHETRA-CRITIQUE.md:101), which the two repl-terminator-dependent calls
below rely on.

Row: file:line | call | buffer allocation | needed | OK / SHORT

### ank_tak_varna — needs the constant 22 cells

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| examples/217_r12_report.sm:51 | `ank_tak_varna(scores[i], koshtha)` | `koshtha = nirmmita(22 * 8)` :47 = 22 cells | 22 | OK |
| tests/stdlib/strconv_int_str.sm:6 | `ank_tak_varna(12345, buf)` | `buf = nirmmita(30 * 8)` :3 = 30 cells | 22 | OK |
| tests/stdlib/strconv_int_str.sm:14 | `ank_tak_varna(0 - 987, buf)` | same 30 cells | 22 | OK |
| tests/stdlib/strconv_int_str.sm:20 | `ank_tak_varna(0, buf)` | same 30 cells | 22 | OK |
| tests/stdlib/strconv_overflow.sm:164 | `ank_tak_varna(MIN, buf)` | `buf = nirmmita(32 * 8)` :4 = 32 cells | 22 (writes 0..20) | OK |
| tests/stdlib/strconv_overflow.sm:249 | `ank_tak_varna(123, buf)` | same 32 cells | 22 | OK |
| tests/stdlib/strconv_overflow.sm:266 | `ank_tak_varna((0 - 456), buf)` | same 32 cells | 22 | OK |
| tests/stdlib/strconv_overflow.sm:287 | `ank_tak_varna(0, buf)` | same 32 cells | 22 | OK |
| tests/stdlib/strconv_pad.sm:5 | `ank_tak_varna(42, buf)` | `buf = nirmmita(10 * 8)` :3 = 10 cells | 22 | **SHORT by 12 cells** (actual writes reach only index 2, so no corruption today) |
| tests/stdlib/strconv_pad.sm:16 | `ank_tak_varna(12345, buf)` | same 10 cells | 22 | **SHORT by 12 cells** (actual writes reach index 5) |
| tools/proof_props.py:429 (prop_strconv_roundtrip) | `ank_tak_varna({v}, buf)`, v in [-999999, 2147483647] | `buf = nirmmita(30*8)` :426 = 30 cells | 22 | OK |
| tools/proof_props.py:476 (prop_strconv_pad_left) | `ank_tak_varna({v}, buf)`, v in 0..9999 | `buf = nirmmita(12*8)` :471 = 12 cells | 22 | **SHORT by 10 cells** (actual writes reach at most index 4) |
| tools/proof_props.py:3742 (prop_min26) | `ank_tak_varna(minv, buf)` | `buf = nirmmita(32 * 8)` :3733 = 32 cells | 22 (writes 0..20) | OK |
| tools/proof_props.py:3905 (prop_safety27, part3) | `ank_tak_varna({0,1,-1,maxv,minv}, buf)` | `buf = nirmmita(32 * 8)` :3805 = 32 cells | 22 | OK |

### pad_vam — needs width + 1 cells (and count cells readable)

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| examples/217_r12_report.sm:53 | `pad_vam(koshtha, cnt, 6, 32)` | 22 cells (:47) | 7 | OK |
| tests/stdlib/r11_misc_edges.sm:31 | `pad_vam(p, 3, 3, 32)` | `p = nirmmita(8 * 8)` :26 = 8 cells | width <= count: writes nothing (contract 4) | OK |
| tests/stdlib/strconv_pad.sm:6 | `pad_vam(buf, 2, 5, 48)` | 10 cells (:3) | 6 | OK |
| tests/stdlib/strconv_pad.sm:17 | `pad_vam(buf, 5, 3, 48)` | 10 cells (:3) | writes nothing (contract 4) | OK |
| tools/proof_props.py:477 (prop_strconv_pad_left) | `pad_vam(buf, c, width, 48)`, width in 1..10 | 12 cells (:471) | <= 11 | OK |

### ank_tak_aadhar_varna — needs digits(n, base) + 1 cells; 64 for an unknown n

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| tests/stdlib/r8_base_digits.sm:5 | `ank_tak_aadhar_varna(10, 16, out)` | `out = nirmmita(70 * 8)` :4 = 70 cells | 2 (worst case 64) | OK |
| tests/stdlib/r8_base_digits.sm:7 | `ank_tak_aadhar_varna(9, 16, out)` | 70 cells | 2 | OK |
| tests/stdlib/r8_base_digits.sm:9 | `ank_tak_aadhar_varna(35, 36, out)` | 70 cells | 2 | OK |
| tests/stdlib/r8_base_digits.sm:11 | `ank_tak_aadhar_varna(35, 37, out)` | 70 cells | 1 (bad base, terminator only) | OK |
| tests/stdlib/strconv_base.sm:6 | `ank_tak_aadhar_varna(255, 16, buf)` | `buf = nirmmita(70 * 8)` :3 = 70 cells | 3 | OK |
| tests/stdlib/strconv_base.sm:16 | `ank_tak_aadhar_varna(255, 2, buf)` | 70 cells | 9 | OK |
| tests/stdlib/strconv_base.sm:22 | `ank_tak_aadhar_varna(64, 8, buf)` | 70 cells | 4 | OK |
| tools/proof_props.py:455 (prop_strconv_base_roundtrip) | `ank_tak_aadhar_varna({v}, {b}, buf)`, v <= 999999, b in {2,8,10,16} | `buf = nirmmita(70*8)` :451 = 70 cells | <= 21 (20 binary digits + 1) | OK |
| tools/proof_props.py:4100 (prop_numeric28) | `ank_tak_aadhar_varna(0 - 5, 10, buf)` | `buf = nirmmita(32 * 8)` :4032 = 32 cells | 1 | OK (fixed small inputs; 32 < the 64 an unknown n would need) |
| tools/proof_props.py:4101 (prop_numeric28) | `ank_tak_aadhar_varna(255, 16, buf)` | 32 cells | 3 | OK |
| tools/proof_props.py:4446 (prop_edge30_conv) | `ank_tak_aadhar_varna(10, 0, out)` | `out = nirmmita(128 * 8)` :4434 = 128 cells | 1 | OK |
| tools/proof_props.py:4447 | `ank_tak_aadhar_varna(10, 1, out)` | 128 cells | 1 | OK |
| tools/proof_props.py:4448 | `ank_tak_aadhar_varna(10, 0 - 2, out)` | 128 cells | 1 | OK |
| tools/proof_props.py:4449 | `ank_tak_aadhar_varna(10, 37, out)` | 128 cells | 1 | OK |
| tools/proof_props.py:4450 | `ank_tak_aadhar_varna(255, 16, out)` | 128 cells | 3 | OK |

### anukram_grah_aayam_purva — dst needs the decoded length, at most cap - pos - 8 bytes

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| tests/stdlib/r11_misc_edges.sm:17 | `anukram_grah_aayam_purva(buf, 0, 11, dst, on)` | `dst = nirmmita(32)` :14 = 32 bytes; `on = nirmmita(8)` :16 = 1 cell | <= 3 bytes (11 - 0 - 8); actual 3 | OK |
| tests/stdlib/r37_bounds.sm:16 | `anukram_grah_aayam_purva(buf, 0, 16, dst, n)` | `dst = nirmmita(64)` :13 = 64 bytes; `n = nirmmita(8)` :14 | <= 8 bytes; actual: length INT64_MAX is rejected (-1), nothing written | OK |
| tests/stdlib/r37_bounds.sm:26 | `anukram_grah_aayam_purva(buf, 0, 64, dst, n)` | 64 bytes | <= 56 bytes; actual 7 | OK |
| tests/stdlib/serial29.sm:48 | `anukram_grah_aayam_purva(buf, 0, 64, dst, n)` | `dst = nirmmita(16 * 8)` :5 = 128 bytes; `n = nirmmita(8)` :6 | <= 56; actual 5 | OK |
| tests/stdlib/serial29.sm:62 | same call | 128 bytes | <= 56; actual 0 | OK |
| tests/stdlib/serial29.sm:69 | `anukram_grah_aayam_purva(bad, 0, 16, dst, n)` | 128 bytes | <= 8; actual: length -1 rejected, nothing written | OK |
| tools/proof_props.py:4213 (prop_serial29) | `anukram_grah_aayam_purva(buf, 0, 64, dst, n)` | `dst = nirmmita(16 * 8)` :4182 = 128 bytes | <= 56; actual 5 | OK |
| tools/proof_props.py:4219 | same | 128 bytes | <= 56; actual 0 | OK |
| tools/proof_props.py:4227 | same, after a -1 length was stored | 128 bytes | rejected (-1), nothing written | OK |

### varna_pratisthap — needs sn + floor(sn/fn)*max(0, rlen - fn) + 1 cells (fn > 0), sn + 1 (fn <= 0)

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| tests/stdlib/r11_khand_varna.sm:46 | `varna_pratisthap(h, 3, nd, 0, r, o3)` | `o3 = nirmmita(8 * 16)` :45 = 16 cells | fn = 0 → 4 | OK (repl `r` = 4 zeroed cells with r[0] = 88, so rlen = 1 is read correctly) |
| tests/stdlib/string_replace.sm:26 | `varna_pratisthap(src, 11, find, 3, repl, out)` | `out = nirmmita(30 * 8)` :25 = 30 cells | rlen 3 = fn → 11 + 0 + 1 = 12 | OK |
| tools/proof_props.py:565 (prop_string_replace) | `varna_pratisthap(src, <=10, find, 2, repl, out)`, repl 1..3 | `out = nirmmita(30*8)` :556 = 30 cells | 10 + 5*1 + 1 = 16 worst | OK |
| tools/proof_props.py:4402 (prop_edge30_text) | `varna_pratisthap(s, 2, s, 0 - 1, s, out)` | `out = nirmmita(8 * 8)` :4380 = 8 cells | fn < 0 → 3 | OK |

### varna_bhed — needs sn + 1 cells

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| tests/stdlib/r11_khand_varna.sm:50 | `varna_bhed(h, 3, nd, 0, p3, 4)` | `p3 = nirmmita(8 * 16)` :48 = 16 cells | 4 | OK |
| tests/stdlib/r8_split_model.sm:65 | `varna_bhed(s, n, sp, spn, parts, maxp)`, n in 0..9, spn in {0,1,2}, maxp in 0..4 | `parts = nirmmita(40 * 8)` :35 = 40 cells | <= 10 | OK |
| tests/stdlib/string_split_join.sm:12 | `varna_bhed(src, 5, sep, 1, parts, 10)` | `parts = nirmmita(20 * 8)` :11 = 20 cells | 6 | OK |
| tools/proof_props.py:601 (prop_string_split_join) | `varna_bhed(src, <=10, sep, 1, parts, 10)` | `parts = nirmmita(40*8)` :595 = 40 cells | <= 11 | OK |
| tools/proof_props.py:4404 (prop_edge30_text) | `varna_bhed(s, 2, s, 0 - 1, parts, 8)` | `parts = nirmmita(16 * 8)` :4381 = 16 cells | 3 | OK |

### varna_yuj — needs sum(len_i) + (count - 1)*sepn + 1 cells

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| tests/stdlib/string_split_join.sm:16 | `varna_yuj(parts, nc, sep, 1, jout)` (nc = 3, segments "a","b","c") | `jout = nirmmita(10 * 8)` :15 = 10 cells | 3 + 2 + 1 = 6 | OK |
| tools/proof_props.py:602 (prop_string_split_join) | `varna_yuj(parts, nc, sep, 1, out)` round-trip of s (<= 10 cells, no trailing sep) | `out = nirmmita(20*8)` :596 = 20 cells | <= 11 | OK |

### varna_chhid — needs sn + 1 cells

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| tests/stdlib/string_case_trim.sm:27 | `varna_chhid(sp, 6, tout)` | `tout = nirmmita(8 * 8)` :26 = 8 cells | <= 7 (actual 3) | OK |
| tools/proof_props.py:650 (prop_string_trim_case) | `varna_chhid(src, <=8, out)` | `out = nirmmita(10*8)` :643 = 10 cells | <= 9 | OK |

### varna_unnat — needs sn + 1 cells

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| tests/stdlib/r8_text_edges.sm:15 | `varna_unnat(s, 8, out)` | `out = nirmmita(9 * 8)` :14 = 9 cells | 9 | OK (exact fit) |
| tests/stdlib/string_case_trim.sm:10 | `varna_unnat(src, 5, out)` | `out = nirmmita(10 * 8)` :9 = 10 cells | 6 | OK |
| tools/proof_props.py:655 (prop_string_trim_case) | `varna_unnat(src, <=8, out)` | 10 cells (:643) | <= 9 | OK |
| tools/proof_props.py:4398 (prop_edge30_text) | `varna_unnat(s, 0 - 1, out)` | 8 cells (:4380) | 1 | OK |

### varna_avanat — needs sn + 1 cells

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| tests/stdlib/r8_text_edges.sm:21 | `varna_avanat(s, 8, out)` | 9 cells (:14) | 9 | OK (exact fit) |
| tests/stdlib/string_case_trim.sm:15 | `varna_avanat(src, 5, out)` | 10 cells (:9) | 6 | OK |
| tools/proof_props.py:660 (prop_string_trim_case) | `varna_avanat(src, <=8, out)` | 10 cells (:643) | <= 9 | OK |
| tools/proof_props.py:4400 (prop_edge30_text) | `varna_avanat(s, 0 - 1, out)` | 8 cells (:4380) | 1 | OK |

### varna_viparyay — needs sn + 1 cells

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| tests/stdlib/strb_cell_pairs.sm:31 | `varna_viparyay(cells, 3, out)` | `out = nirmmita(6 * 8)` :27 = 6 cells | 4 | OK |
| tools/proof_props.py:2572 (prop_strb_cell_pairs) | `varna_viparyay(h, <=6, out)` | `out = nirmmita(64)` :2542 = 8 cells | <= 7 | OK |

### Outside the brief's file list (for completeness, not counted)

tests/r38/test_fail_alloc.py embeds three relevant calls: `ank_tak_varna(42, o)` with
`o = nirmmita(24 * 8)` (:99, 24 >= 22, OK); `ank_tak_aadhar_varna(42, 2, o)` with
`o = nirmmita(72 * 8)` (:101-102, OK); `brihat_ank_tak(x, 4, 2, o)` with `o = nirmmita(16 * 8)`
(:76-80, 16 = 4*4, OK). The two brihat_ank_tak callers in proof_props (:408 digits = 70 cells for
n = 8 → 32 needed; :4469 out = 128 cells for n = 30 → 120 needed) are also OK; brihat_ank_tak is
WITHIN with a stated capacity, so Part B was not required for it.

## Part C — the numbers

- prakriya audited: **19** (aadhar 2, anukram 4, vakyank 6, varna 7).
- (prakriya, buffer) rows: **24** (PARAM 20, OWN 4; OTHER: none — brihat_ank_se's x is also
  written through brihat_shunyank, folded into row 4).
- rows per verdict: **WITHIN 14** (rows 1-7, 9-12, 14, 15, 17), **TERMINATOR 1** (row 16,
  pad_vam), **UNDOC 9** (rows 8, 13, 18-24), **OVER 0**, **NEG 0**.
- call sites checked (Part B): **66** — ank_tak_varna 14, pad_vam 5, ank_tak_aadhar_varna 15,
  anukram_grah_aayam_purva 9, varna_pratisthap 4, varna_bhed 5, varna_yuj 2, varna_chhid 2,
  varna_unnat 4, varna_avanat 4, varna_viparyay 2.
- call sites SHORT: **3**, all against ank_tak_varna's constant ">= 22 cells":
  1. tests/stdlib/strconv_pad.sm:5 — buf 10 cells, SHORT by 12 (actual writes reach index 2).
  2. tests/stdlib/strconv_pad.sm:16 — buf 10 cells, SHORT by 12 (actual writes reach index 5).
  3. tools/proof_props.py:476 (prop_strconv_pad_left) — buf 12 cells, SHORT by 10 (values
     0..9999, actual writes reach at most index 4).
  None of the three writes past its block with the values it uses today; each violates the
  contract and would overrun for a 20-character value.
- OVER: **none** on any contract-valid input. One conditional case is recorded in row 16:
  pad_vam with count < -1 (e.g. `pad_vam(out, -2, 5, f)`) writes out[6] in a width+1 = 6-cell
  buffer; a negative count is outside the contract ("the `count` character codes").
- NEG: **none**. pad_vam's `p = cnt - 1` is only used while `p >= 0` (:250); varna_viparyay's
  `j = n - 1` is reached only for n > 0 (:513).
- UNDOC buffers and the capacity each actually needs:
  - anukram_grah_aayam_purva dst: decoded length, <= cap - pos - 8 bytes.
  - ank_tak_aadhar_varna out: digits(n, base) + 1 cells; 64 for any n.
  - varna_pratisthap out: sn + floor(sn/fn)*max(0, rlen - fn) + 1 cells (sn + 1 when fn <= 0).
  - varna_bhed parts: sn + 1 cells.
  - varna_yuj out: sum(len_i) + max(0, count - 1)*max(0, sepn) + 1 cells.
  - varna_chhid, varna_unnat, varna_avanat, varna_viparyay out: sn + 1 cells.
- Reads past the given count: varna_tak_ank :95 and varna_tak_dashm :285 read buf[0] for n < 0;
  varna_yuj trusts the segment lengths stored in parts; varna_pratisthap scans repl to its 0
  (documented). None in anukram or aadhar.
