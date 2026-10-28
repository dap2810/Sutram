# ROUND-125 — pinned source extracts (raw GitHub reads)
main: 5059e61c6d4058727a0a8a70767b82c624f8c047
Source lines returned verbatim with 1-based original line numbers. No code or native tests executed by ChatGPT.

=== docs/VOCABULARY-TABLE.md, blob 3cd01b4b6052b10a88f2492a339dcd375c12e158, lines 209-235 ===
209: ## 6. The English left — with English meaning, and a verdict
210: 
211: | Name | Module | English | Verdict |
212: |---|---|---|---|
213: | `fib` | `ank` | Fibonacci | **CHANGE: `meru_sankhya`** - **Fibonacci IS the Meru sequence in Indian mathematics; the name is both shorter in meaning and more accurate** |
214: | `fnv1a` | `gudh` | the FNV-1a hash | **KEEP** - **a published algorithm; renaming hides which hash** |
215: | `fnv1a_varna` | `gudh` | FNV-1a over bytes | **KEEP** - same reason |
216: | `simpson` | `kalana` | Simpson's rule | **KEEP** - **a published method; renaming hides which rule** |
217: | `skalar` | `samanvaya` | scalar | **CHANGE: `ekank`** - "single number", and `sadish` (vector) already sits beside it |
218: | `util_chinha` | `sadhan` | utility sign | **CHANGE: `upayog_chinha`** - `upayog` is "use" |
219: | `bit_gan` | `ganit` | bit count | **CHANGE: `ansh_gan`** - `ansh` is "part" |
220: | `asti_sorted` | `shreni` | is sorted | **CHANGE: `asti_shrenit`** - from `shreni` |
221: | `suchi_asti_sorted` | `suchi` | is sorted | **CHANGE: `suchi_asti_shrenit`** |
222: | `roop_sign_akshar` | `roop` | sign character | **CHANGE: `roop_chinha_akshar`** - `chinha` is the project's word for sign |
223: | `pehchan` | `samanvaya` | identity (Hindi) | **CHANGE: `abhigyan`** - "recognition" in Sanskrit; **`pehchan` is Hindi** |
224: | `nishan` | `samanvaya` | mark (Hindi) | **CHANGE: `chinha`** - **`nishan` is Hindi** |
225: | `chay_khip` | `suchi` | stack insert | **CHANGE: `chiti_khip`** - **`chay` is not a Sanskrit stem; `chiti` is "heap", which is a stack** |
226: | `chay_apanay` | `suchi` | stack remove | **CHANGE: `chiti_apanay`** |
227: | `chay_avalok` | `suchi` | stack look | **CHANGE: `chiti_avalok`** |
228: | `chay_rikta` | `suchi` | stack empty | **CHANGE: `chiti_rikta`** |
229: | `avali_nishkas` | `suchi` | row remove | **CHANGE: `avali_apanay`** - the project's own remove word |
230: | `samanvaya_akar_na` | `samanvaya` | matrix shape | **CHANGE: `samanvaya_akar`** - the space is a truncation |
231: | `nirnaya2`, `nirnaya3` | `samanvaya` | decision, 2 and 3 | **CHANGE - need real names.** **Ask what they compute** |
232: | `laghu2`, `adhik2` | `ganit` | less-than, greater-than | **CHANGE: `laghutar`, `adhikatar`** - the comparative forms, both real words |
233: | `pravan2` | `kalana` | slope, second | **CHANGE: `pravan_dwi`** - "second slope" |
234: | `roop_ank_aadhar2` | `roop` | second base | **CHANGE: `roop_ank_aadhar_dwi`** |
235: 

=== lib/samanvaya.smlib, blob 8de0d29f2619d38f4f639728a1220a21996211bb, lines 20-46 ===
20: # samanvaya_akar_na(m, n, len) - R37: 1 when an m x n shape does NOT fit len
21: # elements (or m or n is negative), else 0. It divides, never multiplies, so it
22: # holds for every m and n: m x n fits exactly when n == 0 or m <= len / n.
23: prakriya samanvaya_akar_na(m, n, len) {
24:     yadi (m < 0) { prati 1 }
25:     yadi (n < 0) { prati 1 }
26:     yadi (n == 0) { prati 0 }
27:     yadi (m > len / n) { prati 1 }
28:     prati 0
29: }
30: 
31: # identity matrix: n x n, out must hold n*n elements
32: prakriya pehchan(n, kosh dasham out) {
33:     vitti i = 0
34:     yavat (i < n) {
35:         vitti j = 0
36:         yavat (j < n) {
37:             yadi (i == j) {
38:                 out[i * n + j] = 1.0
39:             } anya {
40:                 out[i * n + j] = 0.0
41:             }
42:             j = j + 1
43:         }
44:         i = i + 1
45:     }
46:     prati n * n

=== lib/samanvaya.smlib, blob 8de0d29f2619d38f4f639728a1220a21996211bb, lines 109-132 ===
109: 
110: # trace of an n x n matrix
111: prakriya nishan(kosh dasham a, n) {
112:     dasham t = 0.0
113:     vitti i = 0
114:     yavat (i < n) {
115:         t = t + a[i * n + i]
116:         i = i + 1
117:     }
118:     prati t
119: }
120: 
121: # determinant of a 2 x 2 matrix (a holds 4 elements)
122: prakriya nirnaya2(kosh dasham a) {
123:     prati a[0] * a[3] - a[1] * a[2]
124: }
125: 
126: # determinant of a 3 x 3 matrix (a holds 9 elements), by cofactor expansion
127: prakriya nirnaya3(kosh dasham a) {
128:     dasham t1 = a[0] * (a[4] * a[8] - a[5] * a[7])
129:     dasham t2 = a[1] * (a[3] * a[8] - a[5] * a[6])
130:     dasham t3 = a[2] * (a[3] * a[7] - a[4] * a[6])
131:     prati t1 - t2 + t3
132: }

=== lib/kalana.smlib, blob 5de30858e4e663f4be1fa46f28c3ee38d5e6e6de, lines 14-94 ===
14: # Integration over sampled data
15: # ---------------------------------------------------------------
16: 
17: # Trapezoidal rule. xs and ys are sample points and values; uses the shorter length.
18: prakriya kalana_trapiz(kosh dasham xs, kosh dasham ys) {
19:     vitti n = kosh_len(xs)
20:     yadi (kosh_len(ys) < n) { n = kosh_len(ys) }
21:     yadi (n < 2) { prati 0.0 }
22:     dasham total = 0.0
23:     vitti i = 0
24:     yavat (i < n - 1) {
25:         dasham h = xs[i + 1] - xs[i]
26:         total = total + h * (ys[i] + ys[i + 1]) / 2.0
27:         i = i + 1
28:     }
29:     prati total
30: }
31: 
32: # Simpson's 1/3 rule over equally spaced samples. Needs an odd number of points
33: # (even intervals); for usable even n >= 4 drops the final sample; n < 3 uses kalana_trapiz.
34: prakriya simpson(kosh dasham xs, kosh dasham ys) {
35:     vitti n = kosh_len(xs)
36:     yadi (kosh_len(ys) < n) { n = kosh_len(ys) }
37:     yadi (n < 3) { prati kalana_trapiz(xs, ys) }
38:     # if the count is even, drop the last point so the rule applies
39:     yadi ((n - 1) - ((n - 1) / 2) * 2 == 1) { n = n - 1 }
40:     dasham h = (xs[n - 1] - xs[0]) / (n - 1)
41:     dasham total = ys[0] + ys[n - 1]
42:     vitti i = 1
43:     yavat (i < n - 1) {
44:         yadi (i - (i / 2) * 2 == 1) {
45:             total = total + 4.0 * ys[i]
46:         } anya {
47:             total = total + 2.0 * ys[i]
48:         }
49:         i = i + 1
50:     }
51:     prati total * h / 3.0
52: }
53: 
54: # ---------------------------------------------------------------
55: # Differentiation over sampled data
56: # ---------------------------------------------------------------
57: 
58: # Central difference at interior point i; one-sided at the ends.
59: prakriya pravan(kosh dasham xs, kosh dasham ys, i) {
60:     vitti n = kosh_len(xs)
61:     yadi (kosh_len(ys) < n) { n = kosh_len(ys) }
62:     yadi (n < 2) { prati 0.0 }
63:     # Neighbouring pair: first, last, or centred. The two
64:     # sequential yadi (not yadi/anyatra) matter: for n == 2,
65:     # i == 0 satisfies the first but not the second, and the
66:     # centred branch would index xs[-1].
67:     vitti lo = i - 1
68:     vitti hi = i + 1
69:     yadi (i <= 0) { lo = 0; hi = 1 }
70:     yadi (i >= n - 1) { lo = n - 2; hi = n - 1 }
71:     # Zero spacing (duplicate x): no pravan is defined — return
72:     # 0.0 instead of inf / NaN (the old code divided by zero).
73:     dasham dx = xs[hi] - xs[lo]
74:     yadi (dx == 0.0) { prati 0.0 }
75:     prati (ys[hi] - ys[lo]) / dx
76: }
77: 
78: # Second derivative at an interior point (central, equally spaced assumption relaxed).
79: prakriya pravan2(kosh dasham xs, kosh dasham ys, i) {
80:     vitti n = kosh_len(xs)
81:     yadi (kosh_len(ys) < n) { n = kosh_len(ys) }
82:     yadi (i <= 0) { prati 0.0 }
83:     yadi (i >= n - 1) { prati 0.0 }
84:     dasham hl = xs[i] - xs[i - 1]
85:     dasham hr = xs[i + 1] - xs[i]
86:     # Zero spacing on either side (or hl == -hr, so the mean
87:     # spacing is 0): the second difference is undefined — 0.0.
88:     yadi (hl == 0.0) { prati 0.0 }
89:     yadi (hr == 0.0) { prati 0.0 }
90:     dasham dl = (ys[i] - ys[i - 1]) / hl
91:     dasham dr = (ys[i + 1] - ys[i]) / hr
92:     dasham hm = (hl + hr) / 2.0
93:     yadi (hm == 0.0) { prati 0.0 }
94:     prati (dr - dl) / hm

=== lib/suchi.smlib, blob eca929ace7cbf98b15d611c64155970c1638e2ff, lines 320-365 ===
320: }
321: 
322: # --- stacks (built on the same list storage) ---
323: 
324: # chay_khip(l, v) — push v. Returns 1 ok / 0 allocation failure.
325: prakriya chay_khip(l, v) {
326:     prati suchi_khip(l, v)
327: }
328: 
329: # chay_apanay(l, ok) — pop the top value; sets ok[0] to 1 on success,
330: # 0 when the stack is empty (returns 0 then).
331: prakriya chay_apanay(l, ok) {
332:     vitti lst = l
333:     vitti okp = ok
334:     vitti d = 0
335:     vitti val = 0
336:     yadi (lst[0] == 0) {
337:         okp[0] = 0
338:         prati 0
339:     }
340:     d = lst[2]
341:     lst[0] = lst[0] - 1
342:     val = d[lst[0]]
343:     okp[0] = 1
344:     prati val
345: }
346: 
347: # chay_avalok(l, ok) — top value without removing it; ok[0] 1/0.
348: prakriya chay_avalok(l, ok) {
349:     vitti lst = l
350:     vitti okp = ok
351:     vitti d = 0
352:     yadi (lst[0] == 0) {
353:         okp[0] = 0
354:         prati 0
355:     }
356:     d = lst[2]
357:     okp[0] = 1
358:     prati d[lst[0] - 1]
359: }
360: 
361: # chay_rikta(l) — 1 if the stack is empty, else 0.
362: prakriya chay_rikta(l) {
363:     yadi (l[0] == 0) { prati 1 }
364:     prati 0
365: }

=== lib/suchi.smlib, blob eca929ace7cbf98b15d611c64155970c1638e2ff, lines 432-451 ===
432:     prati 1
433: }
434: 
435: # avali_nishkas(q, ok) — remove and return the front value; sets
436: # ok[0] to 1 on success, 0 when the queue is empty (returns 0 then).
437: prakriya avali_nishkas(q, ok) {
438:     vitti qu = q
439:     vitti okp = ok
440:     vitti d = 0
441:     vitti val = 0
442:     yadi (qu[0] == 0) {
443:         okp[0] = 0
444:         prati 0
445:     }
446:     d = qu[2]
447:     val = d[qu[3]]
448:     qu[3] = (qu[3] + 1) % qu[1]
449:     qu[0] = qu[0] - 1
450:     okp[0] = 1
451:     prati val

=== lib/anukram.smlib, blob b14d9c9259df0e96f143092fbe33fff3f6aa217c, lines 83-105 ===
83: }
84: 
85: # anukram_khip_ashtak(out, pos, cap, src, n) — write n as an 8-byte
86: # LE length followed by n payload bytes from src. Returns the new
87: # cursor, or -1 on overrun (n < 0 is also an error: -1).
88: prakriya anukram_khip_ashtak(out, pos, cap, src, n) {
89:     vitti dst = out
90:     vitti p = pos
91:     vitti c = cap
92:     vitti s = src
93:     vitti cnt = n
94:     yadi (cnt < 0) { prati 0 - 1 }
95:     yadi (p < 0) { prati 0 - 1 }
96:     yadi (p > c - 8) { prati 0 - 1 }   # R37: subtract; never add, the sum wraps
97:     yadi (cnt > c - 8 - p) { prati 0 - 1 }
98:     vitti p2 = anukram_khip_i64(dst, p, c, cnt)
99:     vitti i = 0
100:     yavat (i < cnt) {
101:         akshar_rakh(dst, p2 + i, akshar(s, i))
102:         i = i + 1
103:     }
104:     prati p2 + cnt
105: }

=== lib/ganit.smlib, blob 9bc5897d72172573007f638168d9272c7ebc8b4a, lines 25-37 ===
25: prakriya laghu2(a, b) {
26:     vitti x = a
27:     vitti y = b
28:     yadi (x < y) { prati x }
29:     prati y
30: }
31: 
32: prakriya adhik2(a, b) {
33:     vitti x = a
34:     vitti y = b
35:     yadi (x > y) { prati x }
36:     prati y
37: }

=== lib/sadhan.smlib, blob 4f20d8e89721953fed1ed775204da210db899f9f, lines 39-43 ===
39: 
40: prakriya util_chinha(n)
41:     prati (n > 0) - (n < 0)
42: 
43: prakriya satya_tak_ank(b)

=== lib/roop.smlib, blob e439b22b90f0adff5d61294e7f31dbe3c3ad3ce2, lines 146-168 ===
146: # roop_ank_aadhar2(v, base, out) — write v in `base` (2..36), lowercase
147: # digits, '-' for negatives, no prefix. Returns the byte count.
148: # Base outside 2..36: terminator only, returns 0. Digits are written
149: # directly at dst + neg, so the util_chinha just fills position 0.
150: prakriya roop_ank_aadhar2(v, base, out) {
151:     vitti val = v
152:     vitti dst = out
153:     vitti neg = 0
154:     vitti n = 0
155:     yadi (val < 0) {
156:         neg = 1
157:         val = 0 - val
158:     }
159:     n = roop_ank_aadhar(val, base, 0, dst + neg)
160:     yadi (n == 0) {
161:         akshar_rakh(dst, 0, 0)
162:         prati 0
163:     }
164:     yadi (neg == 1) {
165:         akshar_rakh(dst, 0, 45)
166:     }
167:     prati n + neg
168: }

=== examples/05_func_params.sm, blob d0a2b81c4f3571b85b4e9c08b1eb83b294039d05, lines 1-14 ===
1: # Function with parameters
2: prakriya yog(a, b)
3:     prati a + b
4: 
5: prakriya gun_tray(a, b, c)
6:     prati a * b * c
7: 
8: mukhya()
9:     vitti x = yog(10, 32)
10:     likha("yog(10, 32) = ")
11:     likha(x)
12:     likha("\n")
13:     likha("gun_tray(3, 4, 5) = ")
14:     likha(gun_tray(3, 4, 5))

=== lang/sanskrit.lang, blob b7bbbe1e07d258cc67f05e9dad81bca9379e59a6, lines 11-47 ===
11: मुख्य mukhya
12: वित्ति vitti
13: अङ्क anka
14: यदि yadi
15: अन्यत्र anya
16: यावत् yavat
17: पुनरावर्तन chakra
18: प्रतियाति prati
19: प्रक्रिया prakriya
20: लिख likha
21: पूर्ण purna
22: शून्य shunya
23: सूत्र sutra
24: क्रम krama
25: उद्देश्य agrim
26: गुण guna
27: भावना bhavana
28: पङ्क्ति mala
29: सृजन ganana
30: निषेध abhava
31: रचना rachana
32: आयोजन yoj
33: परिग्रह satya
34: ग्रहण grahan
35: पर्यन्त tak
36: शब्द shabda
37: दशम dasham
38: कोश kosh
39: विभाग vibhag
40: सिद्धि siddhi
41: दोष dosh
42: प्रसार prasar
43: कुरु kuru
44: निष्क्रिय yantra
45: सङ्ख्या sankhya
46: 
47: # R65: Additional native Devanagari aliases for existing compiler builtins.
