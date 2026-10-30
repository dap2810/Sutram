# R68 buffer audit — lib/roop.smlib and lib/khand.smlib

Read-only audit. Sources quoted: /home/claude/sutram/lib/roop.smlib (676 lines),
/home/claude/sutram/lib/khand.smlib (589 lines), the census at
/tmp/claude-0/-home-claude/e35834e8-b611-5238-b1df-59668dfdca3d/scratchpad/r68/census-roop-khand.txt,
and every call site under examples/, tests/ (not tests/negative/), lib/, tools/proof_props.py,
tools/proof_lib.py (proof_lib.py contains no call to any roop_* or khand_* function).

Allocator fact used throughout (src/r65_arena.inc:16-17): `nirmmita(N)` bumps the cursor by
`align16(N)`, so a block whose size is a multiple of 16 has ZERO slack before the next block;
any other size has `16 - N % 16` bytes of accidental slack. "Needed" below never relies on slack.

Stated conventions treated as contracts:
- roop header, lib/roop.smlib:5-7: "every function writes packed bytes into `out` with a 0
  terminator and returns the byte count."
- roop padding header, lib/roop.smlib:246-249: "The three padders write bytes 0 .. width - 1 of
  `out` and then the 0 terminator at byte `width` (when width <= sn: the sn bytes copied, then
  the terminator at byte `sn`) ... `out` must hold width + 1 bytes (sn + 1 when width <= sn)."
- khand header, lib/khand.smlib:15-16: "lengths are explicit; out-buffers get a 0 terminator;
  the caller allocates generously."

Notation: `digits_b(x)` = number of base-b digits of x (x > 0); `D(v)` = decimal digits of |v|
(1..19 for int64, 19 for INT64_MIN); `strlen(repl)` = bytes before the first 0 in repl.

---------------------------------------------------------------------------------------------

## Part A — every (prakriya, buffer)

Columns: module | prakriya | buffer | unit | MAX INDEX WRITTEN (worst case; reads past count noted) | CAPACITY STATED / own size | VERDICT | note

### khand.smlib

| module | prakriya | buffer | unit | max index written | capacity stated | verdict | note |
|---|---|---|---|---|---|---|---|
| khand | khand_bandh(cells, n, out) :39-54 | out (PARAM) | byte | `max(n,0)` — data at 0..n-1 (:49), terminator at `n` (:52); n <= 0 writes only out[0] (:45) | contract :33 "Writes a 0 terminator at out[n]"; no byte capacity stated | TERMINATOR | Capacity line does NOT exist, so the +1 is implied only by "terminator at out[n]". Needed: `max(n,0) + 1` bytes. Reads: cells c[i] for i < n only (:49) — within given count. |
| khand | khand_mukt(bytes, n, out) :61-76 | out (PARAM) | cell | `max(n,0)` — cells 0..n-1 (:71), terminator cell at `n` (:74); n <= 0 writes out[0] (:67) | contract :57-58 "Writes a 0 terminator cell at out[n]"; no cell capacity stated | TERMINATOR | Needed: `(max(n,0) + 1) * 8` bytes. Reads bytes s[i], i < n (:71) — within. Used as the inner writer of khand_bhed, sangrah.rakh_tak_mala, nighantu_kunjika; its trailing 0 cell is what makes those need one extra cell (see Part B). |
| khand | khand_pratilip(src, n, out) :81-96 | out (PARAM) | byte | `max(n,0)` (data :91, terminator :94, n<=0 -> out[0] :87) | contract :79 "Writes a 0 terminator at out[n]"; no capacity | TERMINATOR | Needed `max(n,0) + 1` bytes. Reads s[i], i < n only. |
| khand | khand_pratisthap(src, sn, find, fn, repl, out) :142-194 | out (PARAM) | byte | fn <= 0: `max(sn,0)` (copy :160, terminator :164). fn > 0: `sn + M*(strlen(repl) - fn)` where M = number of non-overlapping matches, worst `M = floor(sn/fn)`; terminator at that index (:192). Worst over all inputs: `sn + floor(sn/fn) * max(0, strlen(repl) - fn)` | contract :141 "Caller allocates generously." — no expression; header :16 same words | UNDOC | Needed: `sn + floor(sn/fn) * max(0, strlen(repl) - fn) + 1` bytes (for fn <= 0: `sn + 1`). READ PAST COUNT: repl is scanned to its 0 terminator at :155 (`yavat (akshar(r, rlen) != 0)`) — by contract (:137-139), so a slice repl over-reads. Reads of src are guarded by `rpos + flen > slen` (:169) — within. sn < 0: only out[0]. |
| khand | khand_bhed(src, sn, sep, sepn, parts, maxparts) :201-277 | parts (PARAM) | cell | sn == 0: 0 (:222). sepn <= 0: `sn + 1` (dst[0]=sn :228, khand_mukt writes cells 1..sn and a 0 cell at `1 + sn` :229). Main loop: each stored segment k writes dst[wpos]=len (:254) then cells wpos+1..wpos+len and a trailing 0 cell at `wpos+1+len` (:258); trailing empty segment dst[wpos]=0 (:269). Since every separator consumes sepn >= 1 bytes, final wpos <= sn + 1, so max index written = `sn + 1` (reached when the last segment is non-empty and runs to the end, e.g. no separator found, maxparts >= 1). maxparts does NOT lower this bound (one segment already reaches it). | contract :197-200 describes the format only; no capacity. Header :16 "caller allocates generously" | UNDOC | Needed: `(sn + 2) * 8` bytes, independent of maxparts (for maxparts >= 1; maxparts == 0 still writes dst[0] when sn == 0 (:222) or the whole sn+2 cells when sepn <= 0 (:228-229)). The extra cell is the khand_mukt terminator the comment at :255-256 calls "trails harmlessly" — harmless only if the caller allotted it; tests/stdlib/r11_sets_lists.sm:19 shows the analogous trailing 0 cell is observed behaviour. sn < 0 with sepn > 0: writes dst[0] = sn (negative length!) and dst[1] = 0, returns 1 — no out-of-bounds, but a malformed segment. Reads: s[si+sj] guarded by `si + splen <= slen` (:236); sp[sj], sj < sepn — within. |
| khand | khand_yuj(parts, count, sep, sepn, out) :282-315 | out (PARAM) | byte | `sum(len_i for i < count) + (count - 1) * max(sepn,0)` = final wpos; bytes 0..wpos-1 via khand_bandh (:300) and separator writes (:306); terminator at wpos (:313). Intermediate khand_bandh 0-bytes at dst[wpos+len_i] are <= the final index. count <= 0: out[0] only. | contract :280-281 "Returns the new byte count" — no capacity | UNDOC | Needed: `sum(len_i) + (count-1)*max(sepn,0) + 1` bytes. Reads parts cells p[rpos] (:295) driven by `count` and the embedded lengths — the caller gives no cell count, so a `count` larger than the stored segments reads past the real data (contract shape). If an embedded length cell is NEGATIVE, `wpos` and `rpos` go backwards (:301-302) and later `akshar_rakh(dst, wpos, ...)` writes at a negative index — malformed-input NEG, not reachable from well-formed parts. |
| khand | khand_chhid(src, sn, out) :320-353 | out (PARAM) | byte | `hi - lo` <= `max(sn,0)`; data :347, terminator at the returned count :351. Max over inputs: `sn` (no leading/trailing spaces). sn < 0: out[0] only. | contract :317-319 "Returns the new byte count"; terminator only via header :15 | TERMINATOR | Needed: `max(sn,0) + 1` bytes; the contract never says so. Reads s[lo], s[hi-1], s[k] all within 0..sn-1. |
| khand | khand_unnat(src, sn, out) :358-378 | out (PARAM) | byte | `sn` (data :373 for i < sn, terminator :376 at sn); sn < 0: out[0] (:365) | contract :355-357 "Returns the byte count. sn < 0: empty output (the old code wrote the terminator at out[-1], out of bounds)."; terminator via header :15 | TERMINATOR | Needed `max(sn,0) + 1` bytes; capacity not stated. The sn<0 guard (:364) is what removed the earlier NEG. |
| khand | khand_avanat(src, sn, out) :381-401 | out (PARAM) | byte | `sn` (:396, :399); sn < 0: out[0] (:388) | contract :380 "... NUL-terminated; returns sn (0 for sn < 0)" — terminator stated, capacity not | TERMINATOR | Needed `max(sn,0) + 1` bytes. |
| khand | khand_viparyay(src, sn, out) :466-491 | out (PARAM) | byte | `sn` — swaps write dst[i], dst[j] with 0 <= i < j <= sn-1 (:481-482), middle dst[sn/2] (:487), terminator at `sn` (:489); sn <= 0: out[0] (:474). Min index 0. | contract :462-463 "Writes a 0 terminator at out[sn]"; capacity not stated | TERMINATOR | Needed `max(sn,0) + 1` bytes. In-place claim checked: t = s[i] saved before dst[i] and dst[j] are written (:480-482) — correct for src == out. Reads s[0..sn-1] only. |

### roop.smlib

| module | prakriya | buffer | unit | max index written | capacity stated | verdict | note |
|---|---|---|---|---|---|---|---|
| roop | roop_ank(v, out) :32-67 | out (PARAM) | byte | `D(v)` — digits at 0..D-1 (:62), terminator at D (:65); v == 0: out[0]='0', out[1]=0 (:43-44); INT64_MIN delegates to roop_ank_aadhar(val,10,0,dst) (:51) -> 19 digits, terminator at 19; alloc failure: out[0] (:37). Worst: 19. | none (header :5-7 convention only) | TERMINATOR | Needed: `D(v) + 1` bytes, worst 20. No capacity line, so the +1 is not accounted anywhere. (rev is never freed — leak, not a bounds issue.) |
| roop | roop_ank | rev (OWN, nirmmita(22*8) :35) | cell | `rlen` <= 18 (:56; 19 decimal digits for |v| <= 2^63-1; MIN never reaches this loop) | own 22 cells | WITHIN | 19 < 22. |
| roop | roop_ank_aadhar(v, base, upper, out) :73-144 | out (PARAM) | byte | general: `digits_b(|v|)` (digits :139, terminator :142). INT64_MIN: recursive hn = digits_b(2^63 / b) digits, then dst[hn] (:109/:112/:114) and dst[hn+1]=0 (:117) -> `digits_b(2^63)`; base 2: 64 (terminator at index 64). v == 0: 1 (:96-97). Bad base / alloc failure: 0 (:80, :88, :92). | none; contract :70-72 says "writes only the terminator" for bad base | TERMINATOR | Needed: `digits_b(|v|) + 1` bytes, worst 65 (base 2, INT64_MIN). |
| roop | roop_ank_aadhar | rev (OWN, nirmmita(70*8) :78) | cell | `rlen - 1` <= 62 (:133; 63 binary digits for 2^63-1, and 63 for the MIN recursion's hi = 2^62) | own 70 cells | WITHIN | 63 < 70. |
| roop | roop_ank_aadhar_saral(v, base, out) :150-168 | out (PARAM) | byte | `neg + digits_b(|v|)` via roop_ank_aadhar(val, base, 0, dst + neg) (:159), where for INT64_MIN `0 - val` wraps back to MIN and the callee's MIN path yields 64 digits in base 2 -> index 1 + 64 = 65. Bad base with v < 0: callee writes dst[1] = 0 then :161 writes dst[0] -> max index 1 while returning 0. | none | TERMINATOR | Needed: `(v<0) + digits_b(|v|) + 1` bytes, worst 66 (base 2, MIN). Subtle: a 0 return can still have touched out[1] (negative v, bad base). |
| roop | roop_ank_dhvaj(v, base, flags, out) :174-208 | out (PARAM) | byte | `neg + pre + digits_b(|v|)` (callee at dst + neg + pre :194; sign :200; prefix :202-205), pre = 2 only for b in {2,8,16}. Worst: 1 + 2 + 64 = 67 (base 2, MIN, prefix flag). Bad base: pre = 0, callee writes dst[neg] then :196 dst[0] -> max 1 with return 0. | none; contract :170-173 "Returns byte count" | TERMINATOR | Needed: `(v<0) + 2*(flags&1 && b in {2,8,16}) + digits_b(|v|) + 1` bytes, worst 68. Wrappers roop_dash/shodash/shodash_unnat/asht/dwi/ank_pre (:212-243) pass `out` straight through: decimal worst 21, hex 18 (+2 with prefix), octal 23 (+2), binary 66 (+2). |
| roop | roop_pad_vam(src, sn, width, padbyte, out) :252-282 | out (PARAM) | byte | sn >= 0: width <= sn -> `sn` (:263, :266); width > sn -> `width` (pads 0..npad-1 :272, src at npad..width-1 :277, terminator :280). sn < 0: width <= sn -> `dst[sn]` NEGATIVE (:266); width > sn -> pads at 0..`width - sn - 1` (>= width + 1 when sn <= -2) then dst[width] | stated :248-249 "`out` must hold width + 1 bytes (sn + 1 when width <= sn)" | NEG (sn < 0 only); WITHIN for every sn >= 0 | For all sn >= 0 the max index is exactly the stated capacity minus 1: WITHIN, the +1 is accounted. Negative sn: NEG example `roop_pad_vam(s, -1, -1, 32, out)` writes out[-1] = 0 (:266). OVER example `roop_pad_vam(s, -2, 0, 32, out)`: npad = 2, writes out[0], out[1] (:272) against a stated capacity of width + 1 = 1 byte, then out[0] = 0. Reads s[i] only for i < sn — none when sn < 0. The body has no sn < 0 guard like khand_unnat's (:364). |
| roop | roop_pad_dakshin(src, sn, width, padbyte, out) :285-315 | out (PARAM) | byte | sn >= 0: width <= sn -> `sn` (:296, :299); else `width` (src 0..sn-1 :305, pads sn..width-1 :310, terminator :313). sn < 0: width <= sn -> dst[sn] NEGATIVE (:299); width > sn -> pads start at index `sn` (:310, i = 0) -> NEGATIVE. | same stated capacity :248-249 | NEG (sn < 0 only); WITHIN for every sn >= 0 | Any sn < 0 writes a negative index on one path or the other: e.g. `roop_pad_dakshin(s, -1, 0, 32, out)` -> npad = 1, writes out[-1] (:310), then out[0] = 0. Max index never exceeds width (no OVER). |
| roop | roop_pad_madhya(src, sn, width, padbyte, out) :319-356 | out (PARAM) | byte | sn >= 0: width <= sn -> `sn` (:331, :334); else `width` (left pads 0..left-1 :341, src left..left+sn-1 :346, right pads left+sn..width-1 :351, terminator :354; npad - left right pads => last index width - 1). sn < 0: width <= sn -> dst[sn] NEGATIVE (:334); width > sn -> left = (width - sn)/2 pads at 0..left-1 (index left-1 > width when -sn > width + 2: OVER) and right pads from `left + sn` (negative when width + sn < 0: NEG). | same stated capacity :248-249 | NEG (sn < 0 only); WITHIN for every sn >= 0 | Examples: `roop_pad_madhya(s, -2, 0, 32, out)` -> npad = 2, left = 1, writes out[0] then out[-1] (:351). `roop_pad_madhya(s, -10, 0, 32, out)` -> left = 5, writes out[0..4] against capacity 1 (OVER) and out[-5..-1] (NEG). Odd-extra-goes-right claim (:318) checked: right count = npad - npad/2 >= left. |
| roop | roop_varg_sahaya(src, sn, step, out) :363-435 | out (PARAM) | byte | `sn + C` where C = commas: let d = integer digits (dot - start). step == 3: `C = floor((d-1)/3)` (:406); any other step (Indian): `C = max(0, floor((d-2)/2))` (:411-417; commas at rem = 3, 5, 7, ...). Worst d = sn (no sign, no '.'): Indian `sn + floor((sn-2)/2)`, international `sn + floor((sn-1)/3)`; terminator at that index (:433). sn == 0: out[0] (:375). sn < 0: reads s[0] (:378-379) and may write out[0] (sign copy :392) and out[1] (:433). | none (contract :359-362 silent; header convention) | UNDOC | Needed: Indian `sn + max(0, floor((sn-2)/2)) + 1` bytes (~1.5*sn), international `sn + max(0, floor((sn-1)/3)) + 1`. READ PAST COUNT: `akshar(s, 0)` at :378-379 is executed for every sn != 0, including sn < 0 where zero bytes were given. The function does not check that the bytes are digits — any byte string is grouped. Wrappers roop_varg_bharatiya / roop_varg_vishwa / roop_varg (:438-452) pass `out` through unchanged. |
| roop | roop_varg_ank(v, indian, out) :456-471 | out (PARAM) | byte | failure paths out[0] (:459, :464); otherwise roop_varg_sahaya(tmp, n, ...) with n = D(v) + (v<0) <= 20: Indian worst `20 + floor((19-2)/2) = 28` ("-9,22,33,72,03,68,54,77,58,08" for INT64_MIN), international worst `20 + 6 = 26`; terminator at that index | none (contract :454-455) | UNDOC | Needed: 29 bytes (indian == 1) / 27 bytes (otherwise) for the worst int64; expression `(v<0) + D(v) + C(D(v)) + 1`. |
| roop | roop_varg_ank | tmp (OWN, nirmmita(32) :457) | byte | roop_ank_aadhar_saral(v, 10, tmp) (:462): `(v<0) + D(v)` <= 20 (terminator at 20) | own 32 bytes | WITHIN | 21 <= 32. tmp never freed (leak). |
| roop | roop_sthir_mool(dasham x, places, always_sign, out) :478-589 | out (PARAM) | byte | `S + D(intpart) + (pl>0 ? 1 + pl : 0)` where S = (x<0 or always_sign) and pl = clamp(places,0,9); terminator at that index (:587). rounded < 2^63 (guard :535) has <= 19 digits, intpart = rounded / 10^pl, so D(intpart) + pl <= 19 for pl >= 1 and D(intpart) <= 19 for pl == 0. Worst: pl >= 1 -> 1 + 19 + 1 = 21; pl == 0 -> 20. Early exits write out[0] only (:496, :522, :536, :555). | none; header convention | TERMINATOR | Needed: 22 bytes worst case (expression above + 1). Sub-call roop_ank(intpart, dst + wpos) (:553) writes its own terminator at wpos + D(intpart), which is <= the final index. Wrappers roop_sthir / roop_sthir_chinhit (:593-601) pass `out` through. |
| roop | roop_sthir_mool | rev (OWN, nirmmita(22*8) :494) | cell | `rlen - 1` <= 8 (fracpart < 10^9 -> <= 9 digits, :569) or rev[0] (:565) | own 22 cells | WITHIN | 9 < 22. rev never freed (leak). |
| roop | roop_chinhit(v, out) :605-637 | out (PARAM) | byte | v < 0: n = 1 + D(v) <= 20 bytes copied (:623), terminator at `n` (:626) -> worst 20. v >= 0: '+' at 0 (:629), digits at 1..n (:632), terminator at `n + 1` (:635), n <= 19 -> worst 20. Failure paths: out[0] (:612, :617). | none; contract :604 "always a util_chinha" | TERMINATOR | Needed: `1 + D(v) + 1` bytes, worst 21. |
| roop | roop_chinhit | tmp (OWN, nirmmita(32) :608) | byte | roop_ank_aadhar_saral(val, 10, tmp) (:615): <= 20 (terminator at 20) | own 32 bytes | WITHIN | 21 <= 32. |
| roop | roop_sign_akshar(v, signch, out) :642-675 | out (PARAM) | byte | identical shape to roop_chinhit: v < 0 -> `n` <= 20 (:661, :664); v >= 0 -> signch at 0 (:667), digits 1..n (:670), terminator at `n + 1` (:673) <= 20 | none; contract :639-641 | TERMINATOR | Needed: `1 + D(v) + 1` bytes, worst 21. |
| roop | roop_sign_akshar | tmp (OWN, nirmmita(32) :646) | byte | <= 20 (:653) | own 32 bytes | WITHIN | 21 <= 32. |

### Reads of caller buffers past the given count (summary)

| where | read | why |
|---|---|---|
| khand_pratisthap :155 | `akshar(r, rlen)` until 0 | repl has no length parameter; contract (:137-139) says it is 0-terminated. A slice repl over-reads. |
| khand_yuj :295 | `p[rpos]` for `count` segments | parts has no cell count; `count` beyond the stored segments reads uninitialised/foreign cells; a negative stored length walks backwards. |
| roop_varg_sahaya :378-379 | `akshar(s, 0)` whenever sn != 0 | executed for sn < 0 too, where no bytes were given. |
| khand_bandh :49 / khand_mukt :71 / khand_pratilip :91 / khand_viparyay :480-487 / khand_unnat :369 / khand_avanat :392 / khand_chhid :334-347 / roop_pad_* :263-346 | s[i], i < given count | within — no over-read. |

No function in either module reads a terminator it was not told about except khand_pratisthap's repl (contractual).

---------------------------------------------------------------------------------------------

## Part B — callers

Scope: every prakriya above whose PARAM buffer verdict is TERMINATOR, UNDOC or NEG — i.e. all
ten khand writers and all roop writers (the three padders are included because of the sn < 0
NEG; for them the check is "allocation >= stated width+1 / sn+1 AND sn >= 0 at the site").
Wrappers that pass `out` straight through (roop_dash, roop_shodash, roop_shodash_unnat,
roop_asht, roop_dwi, roop_ank_pre, roop_varg, roop_varg_bharatiya, roop_varg_vishwa,
roop_sthir, roop_sthir_chinhit) are counted as calls of the underlying writer.
tools/proof_lib.py: zero calls to roop_* or khand_* (grep). tests/negative/ skipped.

Row: `file:line | call | buffer allocation | needed (bytes unless "cells") | verdict`

### khand — examples/

| file:line | call | buffer allocation | needed | verdict |
|---|---|---|---|---|
| examples/215_r12_wordfreq.sm:39 | `khand_bhed(text, tlen=51, " ", 1, parts, 64)` | parts = nirmmita(512*8) = 512 cells (:38) | 51 + 2 = 53 cells | OK |
| examples/215_r12_wordfreq.sm:57 | `khand_bandh(parts + (pos+1)*8, wlen, wbuf + wpos)` | wbuf = nirmmita(64*40) = 2560 bytes (:46); wpos advances only for unique words (:64), sum of all word bytes = 41 | wpos + wlen + 1 <= 42 | OK |

### khand — tests/stdlib/

| file:line | call | buffer allocation | needed | verdict |
|---|---|---|---|---|
| tests/stdlib/string_strb_split_join.sm:6 | `khand_bhed("a,b,c", 5, ",", 1, parts, 8)` | parts = nirmmita(64*8) = 64 cells (:3) | 7 cells | OK |
| tests/stdlib/string_strb_split_join.sm:10 | `khand_yuj(parts, nc=3, ",", 1, out)` | out = nirmmita(32) (:4) | 3 + 2 + 1 = 6 | OK |
| tests/stdlib/string_strb_split_join.sm:16 | `khand_bhed("abc", 3, "", 0, parts, 8)` | 64 cells | sepn <= 0 path: 1 + 3 + 1 = 5 cells | OK |
| tests/stdlib/string_strb_split_join.sm:19 | `khand_bhed("", 0, ",", 1, parts, 8)` | 64 cells | 1 cell | OK |
| tests/stdlib/string_strb_split_join.sm:22 | `khand_bhed("a,,b", 4, ",", 1, parts, 8)` | 64 cells | <= 6 cells (actual max index 5) | OK |
| tests/stdlib/string_strb_split_join.sm:25 | `khand_yuj(parts, nc2=3, ",", 1, out)` | 32 | 2 + 2 + 1 = 5 | OK |
| tests/stdlib/gaps19.sm:35 | `khand_viparyay("abcde", 5, out)` | out = nirmmita(32) (:33) | 6 | OK |
| tests/stdlib/gaps19.sm:43 | `khand_pratilip("hello", 5, buf)` | buf = nirmmita(32) (:42) | 6 | OK |
| tests/stdlib/gaps19.sm:44 | `khand_viparyay(buf, 5, buf)` (in place) | 32 | 6 | OK |
| tests/stdlib/string_strb_bridge.sm:6 | `khand_pratisthap("foo bar foo", 11, "foo", 3, "baz", out)` | out = nirmmita(32) (:5) | 11 + 2*(3-3) + 1 = 12 | OK |
| tests/stdlib/r8_bytes_edges.sm:15 | `khand_unnat("`az{@AZ[", 8, out)` | out = nirmmita(16) (:14) | 9 | OK |
| tests/stdlib/r8_bytes_edges.sm:21 | `khand_avanat("`az{@AZ[", 8, out)` | 16 | 9 | OK |
| tests/stdlib/set_difference.sm:24 | `khand_bandh(arr + (pos+1)*8, sl, buf)` | buf = nirmmita(64) (:17); sl = element length, elements "apple","pear","fig" (max 5) | sl + 1 <= 6 | OK |
| tests/stdlib/strb_cell_pairs.sm:5 | `khand_pratilip("hello world", 11, hay)` | hay = nirmmita(32) (:4) | 12 | OK |
| tests/stdlib/string_strb_trim_case.sm:5 | `khand_chhid("  hi  ", 6, out)` | out = nirmmita(32) (:3) | 7 | OK |
| tests/stdlib/string_strb_trim_case.sm:10 | `khand_chhid("   ", 3, out)` | 32 | 4 | OK |
| tests/stdlib/string_strb_trim_case.sm:13 | `khand_unnat("aBc xYz", 7, out)` | 32 | 8 | OK |
| tests/stdlib/string_strb_trim_case.sm:17 | `khand_avanat("aBc xYz", 7, out)` | 32 | 8 | OK |
| tests/stdlib/r11_khand_varna.sm:16 | `khand_yuj(parts, 1, ",", 1, out)` | out = nirmmita(64) (:15); parts[0] = 2 | 2 + 0 + 1 = 3 | OK |
| tests/stdlib/r11_khand_varna.sm:25 | `khand_bhed("a,", 2, ",", 1, p2, 8)` | p2 = nirmmita(8*16) = 16 cells (:19) | 4 cells | OK |
| tests/stdlib/r11_khand_varna.sm:31 | `khand_pratisthap("abc", 3, "", 0, "X", o2)` | o2 = nirmmita(64) (:30) | 4 | OK |
| tests/stdlib/set_to_array.sm:19 | `khand_bandh(arr + (pos+1)*8, sl, buf)` | buf = nirmmita(64) (:10); elements "cherry","apple","banana" (max 6) | sl + 1 <= 7 | OK |
| tests/stdlib/strb_pack_unpack.sm:8 | `khand_bandh(cells, 2, out)` | out = nirmmita(16) (:7) | 3 | OK |
| tests/stdlib/strb_pack_unpack.sm:16 | `khand_mukt(out, 2, back)` | back = nirmmita(8*8) = 8 cells (:15) | 3 cells | OK |
| tests/stdlib/strb_pack_unpack.sm:27 | `khand_bandh(cells, 4, out)` | 16 | 5 | OK |
| tests/stdlib/strb_pack_unpack.sm:28 | `khand_mukt(out, 4, back)` | 8 cells | 5 cells | OK |
| tests/stdlib/strb_pack_unpack.sm:38 | `khand_bandh(cells, 0, out)` | 16 | 1 | OK |
| tests/stdlib/strb_pack_unpack.sm:40 | `khand_mukt(out, 0, back)` | 8 cells | 1 cell | OK |
| tests/stdlib/set_union.sm:22 | `khand_bandh(arr + (pos+1)*8, sl, buf)` | buf = nirmmita(64) (:15); elements max 5 | <= 6 | OK |
| tests/stdlib/r8_split_model.sm:68 | `khand_bhed(sb, n, spb, spn, parts, maxp)` n = r % 10 <= 9, spn in {0,1,2}, maxp 0..4 | parts = nirmmita(40*8) = 40 cells (:35); sb = nirmmita(16) holds n <= 9 bytes | n + 2 <= 11 cells | OK |
| tests/stdlib/strb_dup.sm:4 | `khand_pratilip("hello", 5, out)` | out = nirmmita(16) (:3) | 6 | OK |
| tests/stdlib/strb_dup.sm:13 | `khand_pratilip("a b", 3, out)` | 16 | 4 | OK |
| tests/stdlib/strb_dup.sm:18 | `khand_pratilip("abc", 0, out)` | 16 | 1 | OK |
| tests/stdlib/set_intersect.sm:24 | `khand_bandh(arr + (pos+1)*8, sl, buf)` | buf = nirmmita(64) (:17); elements "fig","pear" | <= 5 | OK |
| tests/stdlib/slices23.sm:19 | `khand_pratilip(base + 6, 5, slice)` | slice = nirmmita(16) (:17) | 6 | OK |
| tests/stdlib/slices23.sm:20 | `khand_pratisthap("aaa bbb aaa", 11, "aaa", 3, slice, out)` | out = nirmmita(64) (:16); strlen(slice) = 5 | 11 + 2*(5-3) + 1 = 16 | OK |

### khand — lib/ (pass-through buffers)

| file:line | call | buffer allocation | needed | verdict |
|---|---|---|---|---|
| lib/khand.smlib:229 | `khand_mukt(s, slen, dst + 8)` inside khand_bhed | khand_bhed's own PARAM `parts` | accounted in khand_bhed's Part A row (sn + 2 cells) | pass-through (covered) |
| lib/khand.smlib:258 | `khand_mukt(s + segstart, seglen, dst + (wpos+1)*8)` inside khand_bhed | same | same | pass-through (covered) |
| lib/khand.smlib:300 | `khand_bandh(p + rpos*8, seglen, dst + wpos)` inside khand_yuj | khand_yuj's PARAM `out` | accounted in khand_yuj's row | pass-through (covered) |
| lib/sangrah.smlib:273 | `khand_mukt(scratch + ptrs[i], lens[i], out + (wpos+1)*8)` inside rakh_tak_mala(s, cap, out) | `out` is rakh_tak_mala's PARAM; its contract (sangrah.smlib:212-216) states no capacity | rakh_tak_mala's `out` must hold `nk + sum(lens) + 1` cells (the +1 is this call's trailing 0 cell, acknowledged at :267-268 "or trails") | pass-through — UNDOC at the outer level (sangrah is another auditor's module). In-scope external callers checked: tests/stdlib/set_difference.sm:18, set_to_array.sm:11/27/32, set_union.sm:16, set_intersect.sm:18 (arr = 64 cells vs <= 3 elements, needed <= 18) OK; tests/stdlib/r11_sets_lists.sm:29 (cells = 16 cells vs 2 + 2 + 1 = 5) OK; r11_sets_lists.sm:50 (sorted = 2048 cells vs 512 + 998 + 1 = 1511) OK; tests/stdlib/r39_scratch_from_set.sm:25 (out = 300*40 cells = 12000 vs 200 + 6400 + 1 = 6601) OK |
| lib/nighantu.smlib:399 | `khand_mukt(m + base, kl, out + (wpos+1)*8)` inside nighantu_kunjika(m, out) | `out` is nighantu_kunjika's PARAM; contract (nighantu.smlib:373-375) states no capacity | `n + sum(kl) + 1` cells (trailing 0 cell acknowledged at :396-397 "or it trails harmlessly") | pass-through — UNDOC at the outer level (nighantu is another auditor's module). In-scope external callers: tests/stdlib/r11_nighantu_edges.sm:15 (keys = 16 cells vs 1 + 1 + 1 = 3) OK; tests/stdlib/map_remove.sm:33 (out = 16 cells vs 1 + 5 + 1 = 7) OK |

### khand — tools/proof_props.py (embedded programs)

| file:line | call | buffer allocation | needed | verdict |
|---|---|---|---|---|
| tools/proof_props.py:718 | `khand_pratisthap("{src}", len<=10, "{needle}", 2, "{repl}", out)` repl 1..3 bytes; plus the literal case ("foo bar foo","foo","baz") | out = nirmmita(64) (:716) | <= 10 + 5*(3-2) + 1 = 16; literal 12 | OK |
| tools/proof_props.py:747 | `khand_bhed("{s}", len 1..10, "{sep}", 1, parts, 12)` | parts = nirmmita(40*8) = 40 cells (:745) | <= 12 cells | OK |
| tools/proof_props.py:748 | `khand_yuj(parts, nc, "{sep}", 1, out)` | out = nirmmita(32) (:746) | <= 10 + 1 = 11 | OK |
| tools/proof_props.py:790 | `khand_chhid("{s}", len 1..8, out)` | out = nirmmita(16) (:785) | <= 9 | OK |
| tools/proof_props.py:795 | `khand_unnat("{s}", len 1..8, out)` | 16 | <= 9 | OK |
| tools/proof_props.py:800 | `khand_avanat("{s}", len 1..8, out)` | 16 | <= 9 | OK |
| tools/proof_props.py:1017 | `khand_bandh(cells, n, out)` n = len(s), s from `rng.randint(1, 8)` (:987) | out = nirmmita(16) (:1011) | n + 1 <= 9 | OK |
| tools/proof_props.py:1021 | `khand_mukt(out, n, back)` n in 1..8 | back = nirmmita(8*8) = 64 bytes = 8 cells (:1010) | (n + 1) cells = up to 9 cells = 72 bytes | **SHORT by 1 cell (8 bytes) when n == 8**: khand_mukt writes the terminator cell back[8] (khand.smlib:74) at bytes 64..71, i.e. the first 8 bytes of the next arena block (64 is 16-aligned, so no slack; `out` is allocated right after `back` at :1011). n == 8 occurs with probability 1 - (7/8)^8 ~ 66% per run of the 8 cases. |
| tools/proof_props.py:1026 | `khand_mukt("{s}", n, back)` n in 1..8 | same back, 8 cells | up to 9 cells | **SHORT by 1 cell (8 bytes) when n == 8** (same buffer, same reason) |
| tools/proof_props.py:1027 | `khand_bandh(back, n, out2)` | out2 = nirmmita(16) (:1012) | <= 9 | OK |
| tools/proof_props.py:1058 | `khand_pratilip("{s}", n, out)` n 0..8 (:1041-1044) | out = nirmmita(16) (:1055) | <= 9 | OK |
| tools/proof_props.py:2468 | `khand_viparyay("{src}", len 0..8, rout)` (src :2417) | rout = nirmmita(32) (:2466) | <= 9 | OK |
| tools/proof_props.py:3033 | `khand_pratilip(base + start, slen, tmp)` slen <= 20 (:2998-3000) | tmp = nirmmita(64) (:3031) | <= 21 | OK |
| tools/proof_props.py:3035 | `khand_pratisthap("ab", 2, "b", 1, tmp, out)` | out = nirmmita(64) (:3032); strlen(tmp) = slen <= 20 | 2 + 1*(slen - 1) + 1 <= 22 | OK |
| tools/proof_props.py:4410 | `khand_unnat(b, 0 - 1, bout)` | bout = nirmmita(32) (:4383) | 1 | OK |
| tools/proof_props.py:4412 | `khand_avanat(b, 0 - 1, bout)` | 32 | 1 | OK |
| tools/proof_props.py:4414 | `khand_pratisthap(b, 2, b, 0 - 1, b, bout)` | 32 | fn < 0 path: 3 | OK |
| tools/proof_props.py:4416 | `khand_bhed(b, 2, b, 0 - 1, bparts, 8)` | bparts = nirmmita(16*8) = 16 cells (:4384) | sepn < 0 path: 2 + 2 = 4 cells | OK |

### roop — tests/stdlib/

| file:line | call | buffer allocation | needed | verdict |
|---|---|---|---|---|
| tests/stdlib/fmt_signed.sm:5 / :8 / :11 | `roop_chinhit(42 / -42 / 0, out)` | out = nirmmita(128) (:3) | 4 / 4 / 3 (worst-case 21) | OK (3 sites) |
| tests/stdlib/fmt_signed.sm:15 / :18 / :22 | `roop_sign_akshar(42,32 / -42,32 / 7,42, out)` | 128 | 4 / 4 / 3 | OK (3 sites) |
| tests/stdlib/fmt_group.sm:5 | `roop_varg_bharatiya("1234567", 7, out)` | out = nirmmita(128) (:3) | 7 + 2 + 1 = 10 | OK |
| tests/stdlib/fmt_group.sm:8 | `roop_varg_vishwa("1234567", 7, out)` | 128 | 7 + 2 + 1 = 10 | OK |
| tests/stdlib/fmt_group.sm:12 | `roop_varg("123456", 6, out)` | 128 | 6 + 2 + 1 = 9 | OK |
| tests/stdlib/fmt_group.sm:16 | `roop_varg_bharatiya("-1234567.89", 11, out)` | 128 | 11 + 2 + 1 = 14 | OK |
| tests/stdlib/fmt_group.sm:19 | `roop_varg_vishwa("-1234567.89", 11, out)` | 128 | 14 | OK |
| tests/stdlib/fmt_group.sm:23 | `roop_varg_bharatiya("123", 3, out)` | 128 | 4 | OK |
| tests/stdlib/fmt_group.sm:26 | `roop_varg_vishwa("12", 2, out)` | 128 | 3 | OK |
| tests/stdlib/fmt_group.sm:30 | `roop_varg_bharatiya("", 0, out)` | 128 | 1 | OK |
| tests/stdlib/fmt_group.sm:34 | `roop_varg_ank(0 - 1234567, 1, out)` | 128 | 11 (worst-case 29) | OK |
| tests/stdlib/fmt_group.sm:37 | `roop_varg_ank(1234567, 0, out)` | 128 | 10 | OK |
| tests/stdlib/fmt_group.sm:40 | `roop_varg_ank(999, 1, out)` | 128 | 4 | OK |
| tests/stdlib/r11_misc_edges.sm:23 | `roop_sthir_mool(9223372036854775807.0, 0, 0, o)` | o = nirmmita(64) (:22) | overflow guard path: 1 (worst-case 22) | OK |
| tests/stdlib/r10_roop_suchi_edges.sm:16 | `roop_ank_aadhar(minv, 29, 0, out)` | out = nirmmita(96) (:13) | digits_29(2^63) = 13, +1 = 14 | OK |
| tests/stdlib/r10_roop_suchi_edges.sm:19 | `roop_ank_aadhar(minv, 29, 1, out)` | 96 | 14 | OK |
| tests/stdlib/r10_roop_suchi_edges.sm:22 | `roop_ank_dhvaj(0, 10, 0, out)` | 96 | 2 | OK |
| tests/stdlib/fmt_fixed.sm:5 / :9 / :12 / :16 / :20 / :31 / :35 | `roop_sthir(...)` (7 sites) | out = nirmmita(128) (:3) | each <= 22 | OK (7 sites) |
| tests/stdlib/fmt_fixed.sm:24 / :27 | `roop_sthir_chinhit(+-3.1, 2, out)` | 128 | 6 | OK (2 sites) |
| tests/stdlib/fmt_pad.sm:6 | `roop_pad_vam("hi", 2, 5, 32, out)` | out = nirmmita(128) (:3) | width + 1 = 6; sn >= 0 | OK |
| tests/stdlib/fmt_pad.sm:10 | `roop_pad_dakshin("hi", 2, 5, 48, out)` | 128 | 6 | OK |
| tests/stdlib/fmt_pad.sm:14 | `roop_pad_madhya("hi", 2, 5, 45, out)` | 128 | 6 | OK |
| tests/stdlib/fmt_pad.sm:18 | `roop_pad_madhya("hi", 2, 6, 45, out)` | 128 | 7 | OK |
| tests/stdlib/fmt_pad.sm:22 | `roop_pad_vam("hello", 5, 3, 32, out)` | 128 | sn + 1 = 6 | OK |
| tests/stdlib/fmt_pad.sm:25 | `roop_pad_dakshin("hello", 5, 5, 32, out)` | 128 | 6 | OK |
| tests/stdlib/fmt_pad.sm:29 | `roop_pad_vam("", 0, 3, 42, out)` | 128 | 4 | OK |
| tests/stdlib/fmt_pad.sm:34 | `roop_dash(42, ank)` (-> roop_ank_aadhar_saral) | ank = nirmmita(32) (:33) | 3 (worst-case 21) | OK |
| tests/stdlib/fmt_pad.sm:35 | `roop_pad_vam(ank, nd=2, 5, 48, out)` | 128 | 6; nd >= 0 (return of roop_dash) | OK |
| tests/stdlib/numeric29.sm:41 | `roop_sthir(1000000000000000000.0, 2, buf)` | buf = nirmmita(40*8) = 320 (:40) | overflow path: 1 | OK |
| tests/stdlib/numeric29.sm:43 | `roop_sthir(0 - 1000000000000000000.0, 2, buf)` | 320 | 1 | OK |
| tests/stdlib/numeric29.sm:45 | `roop_sthir(9223372036854774784.0, 0, buf)` | 320 | 19 + 1 = 20 | OK |
| tests/stdlib/fmt_min.sm:5 | `roop_ank_aadhar_saral(minv, 10, out)` | out = nirmmita(80*8) = 640 (:3) | 1 + 19 + 1 = 21 | OK |
| tests/stdlib/fmt_min.sm:14 | `roop_ank_aadhar_saral(minv, 16, out)` | 640 | 1 + 16 + 1 = 18 | OK |
| tests/stdlib/fmt_min.sm:23 | `roop_ank_dhvaj(minv, 16, 1, out)` | 640 | 1 + 2 + 16 + 1 = 20 | OK |
| tests/stdlib/fmt_min.sm:32 | `roop_ank_aadhar(0 - 5, 10, 0, out)` | 640 | 2 | OK |
| tests/stdlib/fmt_min.sm:37 | `roop_ank(minv, out)` | 640 | 19 + 1 = 20 | OK |
| tests/stdlib/fmt_min.sm:46 | `roop_ank_aadhar_saral(minv, 2, out)` | 640 | 1 + 64 + 1 = 66 (the module-wide worst case) | OK |
| tests/stdlib/fmt_int_base.sm:6 / :43 | `roop_dash(0 - 255 / 0, out)` | out = nirmmita(128) (:3) | 5 / 2 | OK (2 sites) |
| tests/stdlib/fmt_int_base.sm:10 / :13 | `roop_shodash(255, out)`, `roop_shodash_unnat(255, out)` | 128 | 3 / 3 | OK (2 sites) |
| tests/stdlib/fmt_int_base.sm:17 / :20 / :27 / :33 | `roop_ank_pre(255,16,0 / -255,16,1 / 5,2,0 / 511,8,0, out)` | 128 | 5 / 6 / 6 / 6 | OK (4 sites) |
| tests/stdlib/fmt_int_base.sm:24 / :30 | `roop_dwi(5, out)`, `roop_asht(511, out)` | 128 | 4 / 4 | OK (2 sites) |
| tests/stdlib/fmt_int_base.sm:37 / :40 / :46 | `roop_ank_aadhar_saral(35,36 / 36,36 / 255,1, out)` | 128 | 2 / 3 / 1 | OK (3 sites) |
| tests/stdlib/fmt_int_base.sm:50 | `roop_ank_dhvaj(255, 16, 3, out)` | 128 | 5 | OK |

### roop — tools/proof_props.py (embedded programs)

| file:line | call | buffer allocation | needed | verdict |
|---|---|---|---|---|
| tools/proof_props.py:1456 | `roop_ank_aadhar_saral({v}, {b}, out)` v in [0, 1, -1, 255, -255, 99999, -99999, rand(-10^6..10^6)] (:1422), b in [2,8,10,16,36] (:1423) | out = nirmmita(128) (:1453) | <= 1 + 20 + 1 = 22 (binary of 10^6) | OK |
| tools/proof_props.py:1461 | `roop_ank_dhvaj(255, 16, 2, out)` | 128 | 3 | OK |
| tools/proof_props.py:1466 | `roop_ank_pre(255, 16, 0, out)` | 128 | 5 | OK |
| tools/proof_props.py:1472 | `roop_ank_dhvaj(255, 16, 3, out)` | 128 | 5 | OK |
| tools/proof_props.py:1477 / :1481 | `roop_ank_aadhar_saral(255, 1 / 37, out)` | 128 | 1 | OK (2 sites) |
| tools/proof_props.py:1523 | `roop_pad_vam("{s}", n 1..5, w 0..n+4, 42, out)` (:1494-1496) | out = nirmmita(64) (:1516) | max(w, n) + 1 <= 10; n >= 1 | OK |
| tools/proof_props.py:1537 | `roop_pad_dakshin("{s}", n, w, 42, out)` | 64 | <= 10 | OK |
| tools/proof_props.py:1546 | `roop_pad_madhya("{s}", n, w, 42, out)` | 64 | <= 10 | OK |
| tools/proof_props.py:1627 | `roop_varg_bharatiya / roop_varg_vishwa("{s}", n, out)` s in the fixed list at :1584-1585 (max len 10, "1234567.89") | out = nirmmita(64) (:1610) | <= 10 + 4 + 1 = 15 | OK |
| tools/proof_props.py:1641 | `roop_varg_ank({v}, {indian}, out)` v in [0, 999, 1234, -1234567, 1000000] | 64 | <= 11 | OK |
| tools/proof_props.py:1671 / :1677 | `roop_sthir({x}, {places}, out)`, `roop_sthir_chinhit(...)` cases :1654-1656 | out = nirmmita(64) (:1668) | <= 8 (worst-case 22) | OK (2 sites) |
| tools/proof_props.py:1706 / :1711 | `roop_chinhit({v}, out)`, `roop_sign_akshar({v}, 32, out)` v in [0,1,-1,42,-42,99999,-99999] | out = nirmmita(64) (:1702) | <= 7 | OK (2 sites) |
| tools/proof_props.py:3757 | `roop_ank_aadhar(0 - 5, 10, 0, out)` | out = nirmmita(80*8) = 640 (:3734) | 2 | OK |
| tools/proof_props.py:3766 | `roop_ank_aadhar_saral(minv, {b}, out)` b in [2,8,10,16,36] | 640 | <= 66 | OK |
| tools/proof_props.py:3776 | `roop_ank_dhvaj(minv, 16, 1, out)` | 640 | 20 | OK |
| tools/proof_props.py:4096 / :4097 / :4098 | `roop_ank_aadhar(123, 1 / 37 / 16, 0, out)` | out = nirmmita(40*8) = 320 (:4033) | 1 / 1 / 3 | OK (3 sites) |
| tools/proof_props.py:4284 / :4285 / :4287 | `roop_sthir(1e18, 2 / -1e18, 2 / 9223372036854774784.0, 0, buf)` | buf = nirmmita(40*8) = 320 (:4245) | 1 / 1 / 20 | OK (3 sites) |
| tools/proof_props.py:4619 | `roop_sthir(nan, 2, buf)` | buf = nirmmita(40*8) = 320 (:4565) | NaN guard path: 1 | OK |

Out-of-scope but seen while grepping: tests/r38/test_fail_alloc.py:87-97 calls roop_ank (o = 32),
roop_ank_aadhar(42, 2, ...) (o = 80), roop_varg_ank(1234567, 1, ...) (o = 40), roop_sthir(3.25, 2, ...)
(o = 40), roop_chinhit(42, ...) (o = 40), roop_sign_akshar(42, 32, ...) (o = 40) — all adequate
(needed 3, 7, 10, 5, 3, 3; module worst cases 20, 65, 29, 22, 21, 21 also fit).

Constant-capacity (ank_tak_varna-style) functions: neither module states a constant capacity
for any buffer, so that extra Part B rule has nothing to apply to here. For reference, the
constants a future contract would need are: roop_ank 20, roop_ank_aadhar 65, roop_ank_aadhar_saral
66, roop_ank_dhvaj 68, roop_varg_ank 29 (Indian) / 27, roop_sthir_mool 22, roop_chinhit 21,
roop_sign_akshar 21 bytes. Every in-scope caller already exceeds these.

---------------------------------------------------------------------------------------------

## Part C — the numbers

- Prakriya audited: **22** (10 khand, 12 roop — every entry in the census).
- (prakriya, buffer) rows: **28** (22 PARAM `out`/`parts` rows + 6 OWN scratch rows).
- Rows per verdict:
  - WITHIN: **6** (all OWN scratch: roop_ank/rev 22 cells, roop_ank_aadhar/rev 70 cells,
    roop_varg_ank/tmp 32, roop_sthir_mool/rev 22 cells, roop_chinhit/tmp 32, roop_sign_akshar/tmp 32).
  - TERMINATOR: **14** — khand_bandh, khand_mukt, khand_pratilip, khand_chhid, khand_unnat,
    khand_avanat, khand_viparyay; roop_ank, roop_ank_aadhar, roop_ank_aadhar_saral,
    roop_ank_dhvaj, roop_sthir_mool, roop_chinhit, roop_sign_akshar. In every one of these the
    only write at index == count is the terminator and no capacity line exists, so nothing
    "accounts for the +1" except the header convention (roop :5-7, khand :15) and, for
    khand_bandh/mukt/pratilip/viparyay/avanat, the per-function words "terminator at out[n]" /
    "NUL-terminated".
  - UNDOC: **5** — khand_pratisthap (needs `sn + floor(sn/fn)*max(0, strlen(repl)-fn) + 1`),
    khand_bhed (needs `(sn + 2)` cells regardless of maxparts), khand_yuj (needs
    `sum(len_i) + (count-1)*sepn + 1`), roop_varg_sahaya (needs `sn + floor((sn-2)/2) + 1`
    Indian / `sn + floor((sn-1)/3) + 1` international), roop_varg_ank (needs 29 / 27 bytes).
  - NEG: **3** — roop_pad_vam, roop_pad_dakshin, roop_pad_madhya, ONLY when sn < 0 (no guard
    like khand_unnat :364). For every sn >= 0 all three are WITHIN the stated `width + 1`
    (`sn + 1` when width <= sn) — the R68 header claim "the bodies were right" holds for
    non-negative lengths.
  - OVER: **0** as a primary verdict. (roop_pad_vam and roop_pad_madhya additionally exceed the
    stated capacity under sn <= -2, e.g. `roop_pad_vam(s, -2, 0, 32, out)` writes out[1] against
    a stated 1 byte; recorded inside their NEG rows.)
- Call sites checked: **148** — khand 61 (examples 2, tests 36, lib 5 incl. 3 internal
  pass-throughs, proof_props 18), roop 87 (tests 62, proof_props 25); proof_lib.py 0.
- Call sites SHORT: **2** — both in tools/proof_props.py, prop_strb_pack_unpack:
  - tools/proof_props.py:1021 `khand_mukt(out, n, back)` with `back = nirmmita(8*8)` (:1010) = 8 cells,
    n up to 8 (:987): terminator cell back[8] is 1 cell (8 bytes) past the block.
  - tools/proof_props.py:1026 `khand_mukt("{s}", n, back)` — same buffer, same overrun.
  Since 64 is 16-aligned the write lands in the first 8 bytes of the next block (`out`,
  :1011); the proof still passes only because `out` is dead by then.
- Every OVER / NEG / SHORT by name:
  - NEG: roop_pad_vam (lib/roop.smlib:266 `dst[cnt]` with width <= sn < 0; :272 pads past
    width+1 when sn <= -2), roop_pad_dakshin (:299 `dst[cnt]`, :310 `dst[cnt + i]` with sn < 0),
    roop_pad_madhya (:334 `dst[cnt]`, :351 `dst[left + cnt + i]` with width + sn < 0; :341 pads
    past width+1 when -sn > width + 2).
  - OVER: none for sn >= 0 anywhere; the sn < 0 overruns above are the only ones.
  - SHORT: tools/proof_props.py:1021, tools/proof_props.py:1026.
- UNSURE: none. (The two lib pass-through sites, sangrah.smlib:273 and nighantu.smlib:399, are
  not undecided — their inner khand_mukt is bounded — but the capacity of the OUTER `out`
  belongs to the sangrah/nighantu auditor; all in-scope external callers of those two were
  checked here and are OK.)

Side observations (not the bug class, not counted): roop_ank, roop_ank_aadhar, roop_sthir_mool,
roop_varg_ank, roop_chinhit and roop_sign_akshar allocate scratch with nirmmita on every call
and never release it; khand_bhed with sn < 0 stores a negative length cell; roop_varg_sahaya
groups any bytes, not just digits; roop_ank_aadhar_saral / roop_ank_dhvaj can touch out[1]
on a bad base with negative v even though they return 0.
