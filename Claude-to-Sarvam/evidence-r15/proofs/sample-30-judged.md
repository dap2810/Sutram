# R15-03: 30 undecided survivors, drawn at random (seed 15), read by hand

Drawn from the NOT-TRIED survivors in lib-mutant-witness.json. My verdict after each. These are my readings, not checked by running.

```
#1 khand.khand_avanat K:0@L385  doc:
   L385  - akshar_rakh(dst, 0, 0)
        + akshar_rakh(dst, 1, 0)
        => UNDECIDED (terminator at 0; may be overwritten later)
#2 anukram.anukram_khip_i64 K:0@L49  doc: anukram_khip_i64(out, pos, cap, v) — write v as 8 LE bytes at out+pos. Returns pos + 8, or -1 if it would overrun cap.
   L49  - yadi (val < 0) {
        + yadi (val < 1) {
        => UNDECIDED
#3 shreni.adhik C3:>->>=@L56  doc:
   L56  - yadi (a[i] > best) { best = a[i] }
        + yadi (a[i] >= best) { best = a[i] }
        => EQUIVALENT: the maximum is the same
#4 brihat.brihat_ank_se_int C6:<-><=@L50  doc: brihat_ank_se_int(val, arr, n) — convert int to digit array (LSB first) Returns 1 if val fit in n digits, 0 if truncated. MIN: |MIN| does not fit in i
   L50  - yavat (j < c) {
        + yavat (j <= c) {
        => OVERRUN: one more digit cell written
#5 khand.khand_mukt K:0@L67  doc: khand_mukt(bytes, n, out) — the inverse: expand n contiguous bytes into qword cells (one byte value per cell). Writes a 0 terminator cell at out[n]. R
   L67  - dst[0] = 0
        + dst[1] = 0
        => UNDECIDED (terminator; may be overwritten later)
#6 khand.khand_gan_swar K:105@L524  doc: khand_gan_swar(s, n) — count lowercase vowels (a e i o u) in the first n bytes (WS1, R20). Explicit-length form of gan_swar: unlike gan_swar (which sc
   L524  - yadi (ch == 97 || ch == 101 || ch == 105 || ch == 111 || ch == 117) {
        + yadi (ch == 97 || ch == 101 || ch == 106 || ch == 111 || ch == 117) {
        => MISSED DEFECT: "i" is no longer counted
#7 anukram.anukram_grah_i64 N@L77  doc: anukram_grah_i64(buf, pos, cap, out) — read 8 LE bytes at buf+pos, write the value into out[0]. Returns pos + 8, or -1 on overrun.
   L77  - yadi (top >= 128) {
        + yadi ((top >= 128) == 0) {
        => UNDECIDED
#8 brihat.brihat_gun A:+@L174  doc: brihat_gun(a, b, res, n) — res = a * b; res must have 2n digits Returns 0 on success.
   L174  - likh8(r + (i + c) * 8, pad8(r + (i + c) * 8) + carry)
        + likh8(r + (i + c) * 8, pad8(r + (i + c) * 8) - carry)
        => MISSED DEFECT: the top-digit carry is subtracted
#9 varna.varna_chhid K:0@L383  doc: varna_chhid(src, sn, out) — strip leading/trailing ASCII spaces (32). Returns new count.
   L383  - dst[wpos] = 0
        + dst[wpos] = 1
        => TERMINATOR: only the 0 after the output changes
#10 kalana.bahu_mula K:0@L124  doc: Bisection root of a polynomial on [lo, hi]. CONTRACT: `ok` must already contain ONE element (call kosh_push(ok, 0.0) first). A kosh's capacity is not
   L124  - yadi ((flo < 0.0) == (fhi < 0.0)) { ok[0] = 0.0; prati 0.0 }
        + yadi ((flo < 0.0) == (fhi < 0.0)) { ok[1] = 0.0; prati 0.0 }
        => UNDECIDED (failure path)
#11 varna.varna_avanat K:0@L428  doc:
   L428  - dst[slen] = 0
        + dst[slen] = 1
        => TERMINATOR
#12 roop.roop_pad_vam C2:<-><=@L245  doc: --- padding / alignment --- roop_pad_vam(src, sn, width, padbyte, out) — pad on the LEFT with `padbyte` (32 space, 48 '0') to `width`. width <= sn: co
   L245  - yavat (i < cnt) {
        + yavat (i <= cnt) {
        => OVERRUN: one more pad byte written
#13 khand.khand_gan_swar K:117@L524  doc: khand_gan_swar(s, n) — count lowercase vowels (a e i o u) in the first n bytes (WS1, R20). Explicit-length form of gan_swar: unlike gan_swar (which sc
   L524  - yadi (ch == 97 || ch == 101 || ch == 105 || ch == 111 || ch == 117) {
        + yadi (ch == 97 || ch == 101 || ch == 105 || ch == 111 || ch == 118) {
        => MISSED DEFECT: "u" is no longer counted
#14 ganita.ganita_janchit_gun K:0@L284  doc: ganita_janchit_gun(a, b, ok) — a * b; ok[0] 1, or 0 on overflow (returns 0 then). The check is m / a == b, with the INT64_MIN * -1 case handled explic
   L284  - yadi (y == 0 - 1) {
        + yadi (y == 1 - 1) {
        => UNDECIDED
#15 roop.roop_ank D@L60  doc: --- integer digits (private helper) --- roop_ank(v, out) — write the decimal digits of |v| (no util_chinha) into out as packed bytes. Returns the digi
   L60  - akshar_rakh(dst, rlen, 0)
        +
        => UNDECIDED (terminator deleted; may be written later)
#16 sangrah.rakh_samroop_diff K:1@L79  doc: rakh_samroop_diff(a, cap, b, bcap, out) — add every element that is in exactly one of a, b into out (fresh, empty, capacity >= cap + bcap for the wors
   L79  - nighantu_khip(out, ocap, tmpa + pos + 1, seglen, 1)
        + nighantu_khip(out, ocap, tmpa + pos + 1, seglen, 2)
        => UNDECIDED (flag 2 for 1)
#17 varna.varna_viparyay C2:<-><=@L502  doc: varna_viparyay(src, sn, out) — copy the cell array reversed into out (WS1, R20). Cell-array form of khand_viparyay: the same two-pointer vinimay, so i
   L502  - yavat (i < j) {
        + yavat (i <= j) {
        => EQUIVALENT: swapping the middle cell with itself
#18 roop.roop_ank_aadhar2 A:-@L148  doc: roop_ank_aadhar2(v, base, out) — write v in `base` (2..36), lowercase digits, '-' for negatives, no prefix. Returns the byte count. Base outside 2..36
   L148  - val = 0 - val
        + val = 0 + val
        => UNDECIDED
#19 nighantu.nighantu_rikta K:0@L253  doc: nighantu_rikta(m) — reset the map to empty IN PLACE (WS1, R19): same handle, same capacity, no leak, no re-allocation. Capacity is read from m[0]; no
   L253  - vitti k = 0
        + vitti k = 1
        => UNDECIDED
#20 roop.roop_pad_dakshin K:0@L296  doc: roop_pad_dakshin(src, sn, width, padbyte, out) — pad on the RIGHT.
   L296  - akshar_rakh(dst, w, 0)
        + akshar_rakh(dst, w, 1)
        => TERMINATOR
#21 nighantu.nighantu_khip K:0@L134  doc: nighantu_khip(m, cap, key, keyn, val) — insert or update key; returns 1 on success, 0 if the table is full (then the map is unchanged). Updating an ex
   L134  - vitti start = 0
        + vitti start = 1
        => UNDECIDED
#22 roop.roop_ank_aadhar K:0@L77  doc: --- integer digits in a base (private helper) --- roop_ank_aadhar(v, base, upper, out) — write |v| in `base` (2..36) into out as packed bytes, no util
   L77  - vitti ch = 0
        + vitti ch = 1
        => EQUIVALENT: the initial value is overwritten before use
#23 khand.khand_viparyay D@L470  doc: khand_viparyay(src, sn, out) — copy src reversed into out (WS3, R19). Two-pointer vinimay, so it is SAFE IN PLACE (src == out works). Writes a 0 termi
   L470  - akshar_rakh(dst, 0, 0)
        +
        => UNDECIDED
#24 khand.khand_avanat K:0@L383  doc:
   L383  - vitti c = 0
        + vitti c = 1
        => UNDECIDED
#25 roop.roop_ank_aadhar2 K:0@L145  doc: roop_ank_aadhar2(v, base, out) — write v in `base` (2..36), lowercase digits, '-' for negatives, no prefix. Returns the byte count. Base outside 2..36
   L145  - vitti n = 0
        + vitti n = 1
        => UNDECIDED
#26 phal.phal_janchit_bhaj K:1@L136  doc:
   L136  - o[1] = 0
        + o[2] = 0
        => UNDECIDED
#27 khand.khand_viparyay K:0@L466  doc: khand_viparyay(src, sn, out) — copy src reversed into out (WS3, R19). Two-pointer vinimay, so it is SAFE IN PLACE (src == out works). Writes a 0 termi
   L466  - vitti i = 0
        + vitti i = 1
        => UNDECIDED
#28 nighantu.nighantu_kunjika_ashtak K:0@L419  doc: nighantu_kunjika_ashtak(m, out) — R17. Same segments as nighantu_kunjika, but PACKED BYTES: [len-byte, bytes..., len-byte, bytes...], one length byte
   L419  - vitti base = 0
        + vitti base = 1
        => UNDECIDED
#29 sankhyiki.purna_vyapti C1:<=-><@L175  doc: --- integer range (max - min) ---
   L175  - yadi (n <= 0) { prati 0 }
        + yadi (n < 0) { prati 0 }
        => UNDECIDED
#30 roop.roop_sthir_mool C2:>->>=@L472  doc: --- fixed decimals (private helper) --- roop_sthir_mool(dasham x, places, always_sign, out) — |x| rounded HALF AWAY FROM ZERO to `places` digits after
   L472  - yadi (pl > 9) { pl = 9 }
        + yadi (pl >= 9) { pl = 9 }
        => EQUIVALENT: pl = 9 either way
```

EQUIVALENT 4 · MISSED DEFECT 3 · OVERRUN 2 · TERMINATOR 3 · UNDECIDED 18
