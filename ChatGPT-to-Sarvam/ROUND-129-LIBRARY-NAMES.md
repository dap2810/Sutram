# Sutram ROUND-129 — all 305 library names checked against their BODIES

**Assigned:** `Sarvam-to-ChatGPT/ROUND-129.md`, blob `23729c8a163f0205c57af58fc3351005c95d90f9`.
**Pinned start `main`:** `bbc7609f9eae370a46d3b8595849d5bb2797c581` (per brief changelog v404/compiler v258; later changelog may advance).
**Scope:** 24 live `lib/*.smlib` files, 305 actual `prakriya` declarations; **no source edits**. Memory-vocabulary assignment was superseded by this library-name audit.

## Result and methodology

**285 names Y / 20 names N** under a strict **semantic precision** rubric; this is a *static, read-side judgment*, not a number of proved runtime defects. Each TSV row contains the live module/function, a compact description grounded in its source body and adjoining function comment, and a Y/N judgment. A Y means the name plausibly describes the computation in the module's technical context. It does **not** mean perfect classical Sanskrit, numeric correctness, memory safety, or complete documentation. A N means the name's sense is materially vague/wrong for the actual body. **Only the N rows contain a proposed alternative.** The N alternatives are recommendations, **NOT approved renames**.

The two files `ROUND-129-RAW-BODIES-PART1.json` and `ROUND-129-RAW-BODIES-PART2.json` preserve **all 305 pinned full source-body slices**, declaration line, adjacent comments and the original Git blob SHA for independent checking. They are evidence, not runtime traces. Function slices may contain *comments leading into the next declaration* because parsing stops at the next `prakriya`; for individual review use `source line` and the blob. No claims rely on a next-function comment as if it were the current function's behavior.

## WS1 — Required six-column TSV (305 rows)

```tsv
module	function	what the body actually does	name_accurate(Y/N)	why_not	better_name
aadhar	brihat_ank_tak	render n-digit bigint x in `base` into mala `out` as digit values (MSB first). Returns digit count. Caller provides at least 1 writable output cell when n <= 0, or at least 4*n cells whe	Y		
aadhar	brihat_ank_se	parse `count` digit values from mala `d` (MSB first) in `base` into n-digit bigint x. Returns 1 on success, 0 if a digit >= base. Base outside 2..16 returns 0 (the old code accepted	Y		
ank	asti_yugm	Tests whether n is even using n % 2 == 0.	Y		
ank	asti_visham	1 if n is odd, 0 if even.	Y		
ank	ank_gan	number of decimal digits in n (sign ignored; MIN counts as 19).	Y		
ank	ank_yog	sum of the decimal digits of n (sign ignored; MIN counts as 89).	Y		
ank	viparyay_ank	n with its decimal digits reversed, sign kept (e.g. -123 -> -321).	Y		
ank	asti_vilom	1 if n reads the same backwards (a palindrome); negatives are never palindromes.	N	Tests decimal-digit palindrome, not whether a number merely is reversed.	asti_viparyay_sam
ank	seemit	n clamped into [lo, hi]: lo if n < lo, hi if n > hi, else n.	Y		
ank	fib	the nth Fibonacci number (fib(0) = 0, fib(1) = 1), iterative; wraps past int64.	Y		
ank	asti_sampurna	1 if n is a perfect number (equals the sum of its proper divisors), else 0.	Y		
ank	collatz_charan	steps for the Collatz sequence from n to reach 1; -1 if n < 1 or 3x+1 would overflow.	Y		
anukram	anukram_maap_ashtak	encoded size of an n-byte payload: 8 + n.	N	Returns encoded size 8+n for a variable-length payload, not size of a fixed octet.	anukram_maap_aayam_purva
anukram	anukram_khip_i64	write v as 8 LE bytes at out+pos. Returns pos + 8, or -1 if it would overrun cap.	Y		
anukram	anukram_grah_i64	read 8 LE bytes at buf+pos, write the value into out[0]. Returns pos + 8, or -1 on overrun.	Y		
anukram	anukram_khip_ashtak	write n as an 8-byte LE length followed by n payload bytes from src. Returns the new cursor, or -1 on overrun (n < 0 is also an error: -1).	N	Writes an eight-byte LENGTH PREFIX followed by n payload bytes, not just eight bytes.	anukram_khip_aayam_purva
anukram	anukram_grah_ashtak	read a length-prefixed payload: length into out_n[0], payload into dst. Returns the new cursor, or -1 on overrun / negative length.	N	Reads an eight-byte LENGTH PREFIX followed by variable payload, not an octet alone.	anukram_grah_aayam_purva
brihat	brihat_shunyank	set all n digits to 0	Y		
brihat	brihat_ank_se_laghu	convert int to digit array (LSB first) Returns 1 if val fit in n digits, 0 if truncated. MIN: /MIN/ does not fit in int64, so plain negation wraps and emits negative digits. Convert MAX	Y		
brihat	brihat_ank_tak_laghu	convert digit array back to int (for verification) Only correct if the value fits in an int.	Y		
brihat	brihat_pratilip	copy n digits	Y		
brihat	brihat_tul	compare: 1 if a > b, -1 if a < b, 0 if equal	Y		
brihat	brihat_yuj	res = a + b; returns final carry (0 or 1)	Y		
brihat	brihat_nyun	res = a - b (requires a >= b); returns final borrow	Y		
brihat	brihat_gun	res = a * b; res must have 2n digits Returns 0 on success.	Y		
brihat	brihat_asti_shunyank	1 if all digits are 0, else 0	Y		
brihat	brihat_bhajshesh	q = a / b, r = a % b (a,b,q,r are n-digit) Uses long division, one decimal digit at a time. Division by zero is defined, not a hang: q = 0, r = a (so q*b + r == a still holds).	Y		
brihat	brihat_shesh	res = ank % shesh, where ank has 2n digits Helper for powmod. Uses long division. shesh == 0 is defined, not a hang: no reduction is applied, so res is the low n digits of num. Returns	Y		
brihat	brihat_shesh_tr	brihat_shesh with caller's n-digit scratch.	N	Suffix `tr` does not describe caller-supplied n-digit scratch used in modular reduction.	brihat_shesh_sahaya
brihat	brihat_ghatmod	res = base^exp shesh shesh exp is a plain int and must be >= 0 (a negative exp returns 1: the loop never runs). shesh == 0 means "no reduction" (see brihat_shesh), so the result	Y		
chandas	dviguna	Computes 2 raised to n by repeated doubling; not n multiplied by two.	N	Body computes power of two (2^n); `dviguna` ordinarily suggests doubling n (2*n).	dwi_ghat
chandas	meru	the binomial coefficient C(n, k); 0 for k < 0 or k > n.	Y		
chandas	matra_meru	the nth Fibonacci number (matra_meru(0) = 0, matra_meru(1) = 1).	Y		
chandas	asti_guru	1 if bit i of the integer pattern pat is set; 0 for i < 0 or i >= 64.	Y		
chandas	guru_gan	count of set bits in pat (population count); negatives return 0.	Y		
chandas	meru_mala	fills a[0..n] with the nth row of Pascal's triangle: a[i] = meru(n, i).	Y		
ganit	varg	Computes n × n.	Y		
ganit	vargit	n squared (n * n).	Y		
ganit	ghan	n cubed (n * n * n).	Y		
ganit	nirapeksh_mulya	absolute value of n (MIN wraps to MIN, as it cannot be negated).	Y		
ganit	laghu2	the smaller of a and b.	Y		
ganit	adhik2	the larger of a and b.	Y		
ganit	mahattam	greatest common divisor of a and b, always non-negative (mahattam(0, 0) = 0).	N	Returns greatest common DIVISOR; name only means greatest and omits divisor relation.	mahattam_samanya_bhajak
ganit	laghuttam	least common multiple of a and b, always non-negative (laghuttam(0, 0) = 0).	N	Returns least common MULTIPLE; name only means least and omits multiplicity relation.	laghuttam_samanya_gunaja
ganit	ghat	base raised to the power e (e >= 0; negative e returns 1, as the loop never runs).	Y		
ganit	kramgun	n factorial (n!); 1 for n < 2; wraps past int64 for n >= 21.	Y		
ganit	asti_abhajya	1 if n is prime, 0 otherwise (n < 2 is not prime).	Y		
ganit	yog_tak	sum 1 + 2 + ... + n, closed form n*(n+1)/2; 0 for n <= 0.	Y		
ganit	dvigun	n doubled (n * 2).	Y		
ganit	trigun	n tripled (n * 3).	Y		
ganit	vardh	n incremented by 1 (n + 1).	Y		
ganit	bit_gan	count of set bits in n; negatives return 0.	Y		
ganit	ganit_yadricch	Knuth MMIX LCG — state = state * 6364136223846793005 + 1442695040888963407 (shesh 2^64, plain wrapping arithmetic). `state` is a 1-cell array holding the seed; it is updated in place and the…	Y		
ganit	ganit_seemit	lo if v < lo, hi if v > hi, else v. Requires lo <= hi. If lo > hi: lo when v < lo, otherwise hi (R9, F4: the old comment said lo always; ganit_seemit(4, 4, -2) is -2).	Y		
ganita	kuttaka	> x such that a*x is congruent to c (shesh b). Requires mahattam(a, b) to divide c. Returns x (a particular solution).	Y		
ganita	ganita_vargmool	Returns floor(sqrt(n)) using overflow-safe division comparisons; negative n maps to zero.	Y		
ganita	ganita_nirapeksh	absolute value of n (the ganita-module spelling of nirapeksh_mulya).	Y		
ganita	chakravala	solves x^2 - n*y^2 = 1 for least positive x, y. Writes out[0] = x and out[1] = y; caller must supply at least 2 writable qword cells.	Y		
ganita	samasa	Brahmagupta's composition law (bhavana / samasa). Given a^2 - n*b^2 = k1 and c^2 - n*d^2 = k2, composes them into a third: (a^2 - n*b^2)(c^2 - n*d^2) = (a*c + n*b*d)^2 - n*(a*d + b*c)^2 Writes	Y		
ganita	brahmagupta_kshetr	Brahmagupta's formula for the area of a cyclic quadrilateral (Brahma-sphuta-siddhanta, 628 CE): area = sqrt((s-a)(s-b)(s-c)(s-d)), s = (a+b+c+d)/2. With d = 0 this is Brahmagupta's trian	Y		
ganita	ganita_janchit_yuj	a + b; ok[0] 1, or 0 on overflow (returns 0 then).	Y		
ganita	ganita_janchit_nyun	a - b; ok[0] 1, or 0 on overflow (returns 0 then).	Y		
ganita	ganita_janchit_gun	a * b; ok[0] 1, or 0 on overflow (returns 0 then). The check is m / a == b, with the INT64_MIN * -1 case handled explicitly (the division itself would SIGFPE there).	Y		
ganita	ganita_janchit_bhaj	truncating a / b; ok[0] 1, or 0 on division by zero or INT64_MIN / -1 (both would SIGFPE; returns 0).	Y		
ganita	ganita_janchit_shesh	truncating a % b (remainder takes the dividend's util_chinha); ok[0] 1, or 0 on b == 0 or INT64_MIN % -1.	Y		
ganita	ganita_paripurna_yuj	a + b, SATURATING: on overflow returns INT64_MAX (positive overflow) or INT64_MIN (negative overflow).	Y		
ganita	ganita_paripurna_nyun	a - b, saturating (see ganita_paripurna_yuj).	Y		
ganita	ganita_paripurna_gun	a * b, saturating (see ganita_paripurna_yuj). The overflow direction is the util_chinha of the true product.	Y		
ganita	ganita_janchit_ghat	a^e for e >= 0 via repeated checked multiplication (WS3, R19); ok[0] 1, or 0 if e < 0 (no integer ghat) or the result overflows (returns 0 then). 0^0 = 1 by the empty-product convention. O	Y		
ganita	ganita_janchit_kramgun	n! via repeated checked multiplication (WS3, R20); ok[0] 1, or 0 if n < 0 (no integer factorial) or the result overflows (returns 0 then). 0! = 1. 20! is the largest that fits (20! = 24329	Y		
ganita	ganita_paripurna_ghat	a^e, saturating (WS3, R20): on overflow returns INT64_MAX (positive overflow) or INT64_MIN (negative overflow). e < 0 returns 0 (no integer ghat; the saturating form has no ok channel, so 0	Y		
ganita	ganita_paripurna_bhaj	truncating a / b, saturating (WS4, R24): the sat_* companion of ganita_janchit_bhaj. INT64_MIN / -1 saturates to INT64_MAX (the true quotient 2^63 does not fit); b == 0 returns 0 (the satura	Y		
ganita	ganita_paripurna_shesh	truncating a % b (WS4, R24). Remainder never overflows mathematically (INT64_MIN % -1 is exactly 0), but the hardware operation still traps on MIN % -1 (same SIGFPE as MIN / -1), so this gu	Y		
ganita	ganita_janchit_nirapeksh	/a/ (WS4, R24); ok[0] 1, or 0 on abs(INT64_MIN), which overflows (returns 0 then). The unary overflow the checked family did not cover: plain ganita_nirapeksh(MIN) silently wraps to MIN.	Y		
ganita	ganita_paripurna_nirapeksh	/a/, saturating (WS4, R24): abs(INT64_MIN) saturates to INT64_MAX.	Y		
ganita	ganita_paripurna_kramgun	n!, saturating (WS3, R21): on overflow returns INT64_MAX (factorials are positive, so saturation is always MAX). n < 0 returns 0 (no integer factorial; the saturating form has no ok channel,	Y		
gudh	fnv1a	FNV-1a hash of the first len BYTES of a packed byte-string pointer s. Returns an unsigned 32-bit value in the integer range 0..4294967295.	Y		
gudh	fnv1a_varna	FNV-1a of a NUL-terminated packed byte string (uses vartani_aayam).	Y		
kalana	kalana_trapiz	Sums trapezoid areas over adjacent (x,y) samples; uses the shorter of the two vectors.	Y		
kalana	simpson	Applies Simpson's 1/3 weighted-sample integration; drops the last point when sample count is even.	Y		
kalana	pravan	Returns a numerical first derivative; central differences internally and one-sided differences at endpoints.	Y		
kalana	pravan2	Computes a numerical SECOND derivative at an interior sample; zero at endpoints or invalid spacing.	N	The function computes second numerical DERIVATIVE, not simply a second slope value.	dwitiya_avakalaja
kalana	bahu_ganana	Evaluates a polynomial with ascending coefficients via Horner's method.	Y		
kalana	bahu_mula	Bisects an interval for a polynomial root; writes status through a pre-populated ok[0] cell.	Y		
khand	khand_bandh	pack a qword-cell sequence (one byte value per cell, the varna_bhed/khand_bhed segment format) into contiguous bytes. Writes a 0 terminator at out[n]. Returns n. This is the boundary helper:	Y		
khand	khand_mukt	the inverse: expand n contiguous bytes into qword cells (one byte value per cell). Writes a 0 terminator cell at out[n]. Returns n. n <= 0 writes only the terminator, returns 0. POINTER ARITHM	Y		
khand	khand_pratilip	copy n bytes verbatim ("make me a real byte string from this"). Writes a 0 terminator at out[n]. Returns n. n <= 0 writes only the terminator, returns 0.	Y		
khand	khand_maap	byte length of the string s (via vartani_aayam).	Y		
khand	khand_anwesh	byte index of first occurrence of needle in hay, or -1. Empty needle matches at 0.	Y		
khand	khand_antah	1 if needle occurs in hay, else 0.	Y		
khand	khand_pratisthap	copy src to out, replacing every (non-overlapping) occurrence of find with repl. repl is 0-terminated (its length is derived, so a literal works) — repl cannot be a slice;	Y		
khand	khand_bhed	split src on sep. Same length-prefixed segment format as varna_bhed (R9): parts holds [len0, b0, b1, ..., len1, b0, ...]; cells hold one byte value each. Returns the segm	Y		
khand	khand_yuj	inverse of khand_bhed for the length-prefixed format. Joins `count` segments with sep into a byte string. Returns the new byte count.	Y		
khand	khand_chhid	strip leading/trailing ASCII spaces (32). Returns the new byte count.	Y		
khand	khand_unnat	khand_unnat(src, sn, out) / khand_avanat — ASCII case conversion on byte strings. Returns the byte count. sn < 0: empty output (the old code wrote the terminator at out[-1], out of bounds).	Y		
khand	khand_avanat	copies src (sn bytes) to out with A-Z lowercased to a-z, NUL-terminated; returns sn (0 for sn < 0).	Y		
khand	khand_aadi	khand_aadi(src, sn, pre, pn) / khand_ant — 0/1 on byte strings. A negative prefix/suffix length is invalid: 0 (the old code treated it as empty and returned 1).	Y		
khand	khand_ant	1 if the src byte string (sn bytes) ends with suf (sn2 bytes), else 0.	Y		
khand	khand_tul	-1 / 0 / 1 (lexicographic by byte value).	Y		
khand	khand_viparyay	copy src reversed into out (WS3, R19). Two-pointer vinimay, so it is SAFE IN PLACE (src == out works). Writes a 0 terminator at out[sn]. Returns sn. sn <= 0 writes only the terminator, retu	Y		
khand	khand_gan	count NON-OVERLAPPING occurrences of needle in hay (WS3, R19). Empty needle returns 0 (khand_anwesh would match at 0 forever). Before this, counting meant looping khand_anwesh over succes	Y		
khand	khand_gan_swar	count lowercase vowels (a e i o u) in the first n bytes (WS1, R20). Explicit-length form of gan_swar: unlike gan_swar (which scans to the NUL terminator), this stops at n, so it is correct on…	Y		
khand	khand_gan_akshar	count occurrences of byte `code` in the first n bytes (WS1, R20). Explicit-length form of gan_akshar; correct on slices. (For a substring, use khand_gan.)	Y		
khand	khand_anwesh_akshar	first index of byte `code` in the first n bytes, or -1 (WS1, R20). Explicit-length form of anwesh_akshar.	Y		
khand	khand_asti_sarv_ank	1 if all of the first n bytes are ASCII digits, else 0 (WS1, R20). Explicit-length form of asti_sarv_ank. Empty (n == 0) is 0, mirroring asti_sarv_ank.	Y		
khand	khand_sam	1 if the two byte strings are equal, else 0 (WS1, R20). Explicit-length form of varna_sam.	Y		
madhava	madhava_vargmool	Approximates square root via 1,000 iterations of Newton's method; nonpositive input gives 0.	Y		
madhava	madhava_pi	Approximates π using Madhava's alternating rapidly convergent series.	Y		
madhava	madhava_sin	Approximates sin(x) by a 16-term alternating power series with argument reduction.	Y		
madhava	madhava_cos	Approximates cos(x) by a 16-term alternating power series with argument reduction.	Y		
madhava	madhava_atan	Approximates atan(x) using reciprocal and half-angle reduction plus alternating series.	Y		
mala	mala_nava	Allocates n × 8 bytes for a raw qword array; checks negative/overflow size and returns pointer or 0.	Y		
mala	mala_sangrah	stores val at arr[i] (qword cells, no bounds check); returns 0.	Y		
mala	mala_grah	loads the qword at arr[i] (no bounds check).	Y		
mala	mala_purn	fills arr[0..n-1] with val; returns 0.	Y		
mala	mala_pratilip	copies n qwords from src to dst; returns 0.	Y		
mala	mala_yog	sum of arr[0..n-1].	Y		
mala	mala_sangrah_surakshit	bounds-checked store: 1 and stores if 0 <= i < n, else 0 and stores nothing.	Y		
mala	mala_grah_surakshit	bounds-checked load: arr[i] if 0 <= i < n, else 0.	Y		
nighantu	nighantu_kunji_gudh	home bucket of key (internal helper).	Y		
nighantu	nighantu_kunji_sam	1 if slot's key equals (key,keyn) (internal helper; keyn already truncated by the caller). Reworked in R13 to use khand_tul instead of a hand-rolled loop.	Y		
nighantu	nighantu_koshtha_likh	store key+val at slot and mark it live (internal helper; keyn already truncated by the caller). NOTE: this deliberately does NOT use khand_pratilip for the key copy:	Y		
nighantu	nighantu_anwesh	slot index holding key, or -1 if absent (internal helper; stops at the first empty slot — valid because deletion is backward-shift, so chains have no holes). cap < 1 or keyn < 0: not	Y		
nighantu	nighantu_srij	allocate and clear a map of capacity cap (clamped to >= 1). Returns 0 if cap is so large the allocation size overflows (a wrapped size allocated a small buffer and then wrote cap state cells…	Y		
nighantu	nighantu_khip	insert or update key; returns 1 on success, 0 if the table is full (then the map is unchanged). Updating an existing key keeps nighantu_maap unchanged. cap < 1 or keyn < 0: returns	Y		
nighantu	nighantu_grah	value stored for key, or -1 if absent (documented sentinel; use nighantu_antah to disambiguate).	Y		
nighantu	nighantu_antah	1 if key is present, else 0.	Y		
nighantu	nighantu_apanay	delete key; 1 if removed, 0 if absent. Backward-shift deletion (Knuth 6.4R): after clearing the slot, each following live entry whose home bucket is NOT cyclically past the hole is sh	Y		
nighantu	nighantu_rikta	reset the map to empty IN PLACE (WS1, R19): same handle, same capacity, no leak, no re-allocation. Capacity is read from m[0]; no cap parameter, so a mismatched cap cannot corrupt the map.…	Y		
nighantu	nighantu_vardh	copy the map into a fresh map of capacity newcap, rehashing every entry (WS2, R20). Returns the new handle. Returns 0 and changes nothing if newcap < nighantu_maap(m) (no partial copy), or (R3	Y		
nighantu	nighantu_grah_mool	value for key, or def if absent (WS3, R19). The -1 sentinel of nighantu_grah cannot distinguish "absent" from "stored -1"; this removes the contains-check dance for callers wh	Y		
nighantu	nighantu_maap	number of entries in the map m (its stored size cell).	Y		
nighantu	nighantu_mil	copy every entry of src into dst; src's values overwrite dst's on key conflict (WS3, R23). Returns the number of entries merged. If dst fills up, merging stops early and the return is	Y		
nighantu	nighantu_mulya	write the live values into out (one qword cell each), in the same slot order as nighantu_kunjika / nighantu_kunjika_ashtak (WS2, R21). Returns the value count, which equals nighantu_maap(m). Call	Y		
nighantu	nighantu_kunjika	write live keys into out in length-prefixed form [len0, b0, b1, ..., len1, b0, ...] (same shape as varna_bhed parts). Returns the key count, which equals nighantu_maap(m). NOTE: segments are QW	Y		
nighantu	nighantu_kunjika_ashtak	R17. Same segments as nighantu_kunjika, but PACKED BYTES: [len-byte, bytes..., len-byte, bytes...], one length byte followed by the key's bytes, no terminator. Returns the key count, whi	Y		
patra	patra_path_sarv	open path read-only, read up to cap bytes into out, close. Returns the byte count read (0 for an empty file, or cap == 0 on an existing file), -1 on any error. cap < 0 returns -1 without	Y		
patra	patra_likh_sarv	create/truncate path, write all n bytes from data, close. Returns n (0 for n == 0 on a creatable path), -1 on any error. n < 0 returns -1 without opening.	Y		
patra	patra_asti	1 if path opens read-only, 0 otherwise. (Open failure covers missing file, missing directory, and permission denial alike — the caller cannot distinguish them.)	Y		
phal	phal_siddhi	write the success Result [1, v] into out.	Y		
phal	phal_dosh	write the failure Result [0, 0] into out.	Y		
phal	phal_asti_siddhi	1 if r is a success Result, else 0.	Y		
phal	phal_mulya	the value of a success Result. Caller must check phal_asti_siddhi first: on a failure Result this returns 0, which is indistinguishable from a success value of 0.	Y		
phal	phal_mulya_va	the value if r is success, else def. The one-expression way to handle both branches.	Y		
phal	phal_se_siddhi	lift the ok convention into a Result: writes [ok[0], v] into out (value 0 on failure).	Y		
phal	phal_janchit_yuj	Runs checked addition and writes [ok, result-or-zero] into caller's result array.	Y		
phal	phal_janchit_nyun	checked subtraction: out[0] = ok flag, out[1] = a - b if ok else 0; returns out[0].	Y		
phal	phal_janchit_gun	checked multiplication: out[0] = ok flag, out[1] = a * b if ok else 0; returns out[0].	Y		
phal	phal_janchit_bhaj	checked division: out[0] = ok flag, out[1] = a / b if ok else 0; returns out[0].	Y		
phal	phal_janchit_shesh	checked remainder: out[0] = ok flag, out[1] = a % b if ok else 0; returns out[0].	Y		
phal	phal_janchit_ghat	ganita_janchit_ghat as a Result. Failure [0, 0] on e < 0 or overflow (see ganita_janchit_ghat).	Y		
phal	phal_janchit_kramgun	ganita_janchit_kramgun as a Result. Failure [0, 0] on n < 0 or overflow (21! overflows).	Y		
phal	phal_janchit_nirapeksh	ganita_janchit_nirapeksh as a Result. Failure [0, 0] on abs(MIN) (no int64 absolute value).	Y		
roop	roop_ank	write the decimal digits of /v/ (no util_chinha) into out as packed bytes. Returns the digit count. Internal; the public formatters below build on it.	Y		
roop	roop_ank_aadhar	write /v/ in `base` (2..36) into out as packed bytes, no util_chinha, no prefix. `upper` 1 -> A-F/A-Z. Base outside 2..36 writes on	Y		
roop	roop_ank_aadhar2	write v in `base` (2..36), lowercase digits, '-' for negatives, no prefix. Returns the byte count. Base outside 2..36: terminator only, returns 0. Digits are written directly at dst + neg	N	`2` is a format variant index, not base two: code accepts bases 2..36 and prints optional minus.	roop_ank_aadhar_saral
roop	roop_ank_dhvaj	roop_ank_aadhar2 plus flags: bit 0 (1) = prefix: "0b" / "0o" / "0x" for bases 2 / 8 / 16 (no prefix for other bases, including 10); bit 1 (2) = uppercase hex digits (the prefix itsel	Y		
roop	roop_dash	decimal, no prefix. roop_shodash / roop_shodash_unnat / roop_asht / roop_dwi — base 16 (lower / upper), 8, 2, no prefix.	Y		
roop	roop_shodash	formats v as lowercase hexadecimal into out (no prefix); returns the digit count.	Y		
roop	roop_shodash_unnat	formats v as UPPERCASE hexadecimal into out (no prefix); returns the digit count.	Y		
roop	roop_asht	formats v as octal into out (no prefix); returns the digit count.	Y		
roop	roop_dwi	formats v as binary into out (no prefix); returns the digit count.	Y		
roop	roop_ank_pre	any base with its prefix ("0b"/"0o"/"0x" for 2/8/16; none for other bases). `upper` 1 -> uppercase digits, prefix stays lowercase.	Y		
roop	roop_pad_vam	pad on the LEFT with `padbyte` (32 space, 48 '0') to `width`. width <= sn: copy unchanged.	Y		
roop	roop_pad_dakshin	pad on the RIGHT.	Y		
roop	roop_pad_madhya	pad both sides to width; when width-sn is odd, the extra padding byte goes RIGHT.	Y		
roop	roop_varg_mool	group the integer part of a digit string. step 2 = Indian (3, then 2s: 12,34,567), step 3 = international (3s: 1,234,567). A leading '-' or	N	Formats digit GROUPS (Indian/global), not a root/square root; `mool` is opaque here.	roop_ank_varg_sahaya
roop	roop_varg_bharatiya	1234567 -> 12,34,567.	Y		
roop	roop_varg_vishwa	1234567 -> 1,234,567.	Y		
roop	roop_varg	DEFAULT grouping: Indian (12,34,567). The default is Indian because the audience is Indian.	Y		
roop	roop_varg_ank	format integer v, then group it. `indian` 1 -> Indian grouping, 0 -> international.	Y		
roop	roop_sthir_mool	/x/ rounded HALF AWAY FROM ZERO to `places` digits after '.', exactly `places` digits emitted (zero-padded). places clamped to	Y		
roop	roop_sthir	fixed decimals, '-' for negatives only. 3.14159 at 2 places -> "3.14". Rounding: half away from zero.	Y		
roop	roop_sthir_chinhit	fixed decimals, always a util_chinha: "+3.14" / "-3.14".	Y		
roop	roop_chinhit	always a util_chinha: "+42" / "-42" / "+0".	Y		
roop	roop_sign_akshar	`signch` (a byte value, e.g. 32 for a blank, 43 for '+') in place of '+' for non-negative values; negatives always get '-'.	Y		
sadhan	antargam	Interpolates linearly between a and b with integer percentage t / 100.	N	Body computes linear interpolation by percentage; generic inward movement conceals the interpolation.	antara_prakshepan
sadhan	yog_seema	sum of the integers from start to end inclusive; 0 if end < start.	Y		
sadhan	shesh	remainder a % b computed as a - (a / b) * b; 0 if b == 0.	Y		
sadhan	bhaj_urdhva	ceiling division of a by b (rounds up when the remainder is nonzero); 0 if b == 0.	Y		
sadhan	util_chinha	sign of n: 1 if n > 0, -1 if n < 0, 0 if n == 0.	N	Returns mathematical signum −1/0/1, not a general utility symbol or mark.	ank_chihna
sadhan	satya_tak_ank	boolean b converted to an integer (b * 1).	Y		
sadhan	ank_adhik	the maximum int64 value, 9223372036854775807.	Y		
samanvaya	samanvaya_akar_na	R37: 1 when an m x n shape does NOT fit len elements (or m or n is negative), else 0. It divides, never multiplies, so it holds for every m and n: m x n fits exactly when n == 0 or m <= len	N	Tests if m×n DOES NOT FIT length (or negative sizes); `shape-not` does not identify the capacity predicate.	samanvaya_akar_ayogya
samanvaya	pehchan	Writes an n×n identity matrix: diagonal 1.0, off-diagonal 0.0.	N	Hindi 'recognition' is not a mathematical identity matrix; body constructs diagonal ones/off-diagonal zeros.	ekaka_matrika
samanvaya	vivartana	Transposes an m×n matrix into an n×m output: out[j*m+i] = a[i*n+j].	Y		
samanvaya	matrika_yoga	Performs element-wise matrix addition after verifying dimension/capacity fit.	Y		
samanvaya	skalar	Multiplies each matrix cell by scalar c after dimension/capacity checks.	Y		
samanvaya	matrika_gunana	Computes m×n times n×p matrix product into m×p output.	Y		
samanvaya	nishan	Computes matrix TRACE: sum of a[i*n+i] for i from 0 to n−1.	N	Hindi/Persian 'mark' does not name the matrix TRACE computed by summing the diagonal.	karna_yog
samanvaya	nirnaya2	Calculates determinant of a 2×2 matrix: a0*a3−a1*a2.	N	`nirnaya` = decision; code is specifically determinant of order 2, not general decision.	dwi_kram_nirdharak
samanvaya	nirnaya3	Calculates determinant of a 3×3 matrix by cofactor expansion.	N	`nirnaya` = decision; code is determinant of order 3, not general decision.	tri_kram_nirdharak
samanvaya	sadish_yoga	Computes DOT/INNER product of two float vectors, stopping at the shorter length.	N	The body multiplies corresponding coordinates and sums: scalar DOT product, not vector addition.	sadish_antar_gunana
samanvaya	rekha_manak	Returns the largest absolute row sum (matrix infinity norm).	Y		
sangrah	rakh_srij	allocate an empty set of capacity cap (clamped to >= 1).	Y		
sangrah	rakh_yuj	add elem; 1 on success, 0 if the set is full (then the set is unchanged). Adding an existing element keeps rakh_maap unchanged (idempotent).	Y		
sangrah	rakh_antah	1 if elem is in the set, else 0.	Y		
sangrah	rakh_apanay	remove elem; 1 if removed, 0 if absent.	Y		
sangrah	rakh_maap	number of elements.	Y		
sangrah	rakh_samroop_diff	add every element that is in exactly one of a, b into out (fresh, empty, capacity >= cap + bcap for the worst case, disjoint sets). (a - b) union (b - a). Returns rakh_maap(out).	Y		
sangrah	rakh_sangam	add every element of a and of b into out (fresh, empty, capacity >= cap + bcap). Returns rakh_maap(out).	Y		
sangrah	rakh_sampat	add every element of a that is also in b into out (fresh, empty, capacity >= min(cap, bcap)). Returns rakh_maap(out).	Y		
sangrah	rakh_bhed	add every element of a that is NOT in b into out (fresh, empty, capacity >= cap). Returns rakh_maap(out).	Y		
sangrah	rakh_vardh	copy the set into a fresh set of capacity newcap (WS2, R20). A set IS a map, so this is nighantu_vardh's copy with the same all-or-nothing rule: returns the new handle, or 0 if newcap <…	Y		
sangrah	rakh_rikta	reset the set to empty in place (WS2, R19): same handle, same capacity. A set IS a map, so this is nighantu_rikta's full zero (count, state, keylens, vals, key bytes) with no stale elements…	Y		
sangrah	rakh_sam	1 if a and b hold exactly the same elements, else 0 (WS3, R19). Both subset checks in one call; two empty sets are equal.	Y		
sangrah	rakh_asti_upasamuh	1 if every element of a is in b, else 0. Empty a is a subset of everything.	Y		
sangrah	rakh_tak_mala	write the set's elements into out in length-prefixed form [len0, b0, b1, ..., len1, b0, ...] (same shape as nighantu_kunjika / khand_bhed parts), SORTED lexicographically by byte value (khand	Y		
sankhyiki	yoga	Sums all float elements of the growable array.	Y		
sankhyiki	madhya	Returns float arithmetic mean; zero for empty input.	Y		
sankhyiki	laghutama	Returns minimum float element, or zero for empty input.	Y		
sankhyiki	adhikatama	Returns maximum float element, or zero for empty input.	Y		
sankhyiki	vyapti	Returns float maximum minus minimum (range).	Y		
sankhyiki	prasaran	Returns population variance using squared deviations from the float mean.	Y		
sankhyiki	sankhyiki_vargmool	Approximates positive float square root via Newton iteration; returns zero for nonpositive input.	Y		
sankhyiki	vichalan	Returns population standard deviation by square-rooting variance.	Y		
sankhyiki	bindu	Calculates inner/dot product by summing elementwise float products.	N	`bindu` means point/dot; the body computes a scalar INNER PRODUCT, not a point.	antar_gunana
sankhyiki	manak	Calculates Euclidean vector norm sqrt(dot(a,a)).	Y		
sankhyiki	purna_yoga	Sums first n integer array elements.	Y		
sankhyiki	purna_madhya	Computes truncated integer mean: integer sum / n; zero when n≤0.	Y		
sankhyiki	purna_laghutama	Computes integer minimum; initializes from xs[0] after n>0 check.	Y		
sankhyiki	purna_adhikatama	Computes integer maximum; initializes from xs[0] after n>0 check.	Y		
sankhyiki	purna_vyapti	Computes integer range (maximum − minimum).	Y		
sankhyiki	purna_prasaran	Computes truncated integer variance using truncated integer mean.	Y		
shreni	vinimay	Swaps a[i] and a[j] in place, with no bounds checks shown.	Y		
shreni	budbud_shreni	sorts a[0..n-1] in place, ascending, by bubble sort.	Y		
shreni	viparyay_mala	reverses a[0..n-1] in place.	Y		
shreni	laghu	smallest element of a[0..n-1]; 0 if n <= 0.	Y		
shreni	adhik	largest element of a[0..n-1]; 0 if n <= 0.	Y		
shreni	yog	sum of a[0..n-1].	Y		
shreni	anwesh_sarak	index of the first occurrence of target in a[0..n-1], or -1.	Y		
shreni	gan	count of occurrences of target in a[0..n-1].	Y		
shreni	asti_sorted	1 if a[0..n-1] is in non-decreasing order, else 0.	Y		
shreni	dwi_anwesh	binary search for target in sorted a[0..n-1]: its index, or -1.	Y		
shreni	shankh_shreni	sorts a[0..n-1] in place, ascending, by shell sort.	Y		
shreni	nivesh_shreni	sorts a[0..n-1] in place, ascending, by insertion sort.	Y		
shreni	mil_shreni_punar	Recursively merge-sorts the interval [lo,hi) using caller-supplied scratch.	Y		
shreni	mil_shreni	merge sort; returns 0, or -1 (a unchanged) if its scratch cannot be allocated.	Y		
suchi	suchi_srij	allocate an empty list. cap clamped to >= 1. Returns the list handle, or 0 on allocation failure — including a cap so large the data size overflows (a wrapped size returned a handle whose…	Y		
suchi	suchi_vardh	private helper: dvigun l's capacity, copying the data. Returns 1 ok / 0 allocation failure (list unchanged).	Y		
suchi	suchi_khip	append v. Returns 1 ok / 0 allocation failure.	Y		
suchi	suchi_grah	element i, or 0 if i is out of bounds.	Y		
suchi	suchi_sangrah	set element i. Returns 1 ok / 0 out of bounds.	Y		
suchi	suchi_maap	element count.	Y		
suchi	suchi_nivesh	insert v before index i (i == len appends). Returns 1 ok / 0 out of bounds or allocation failure.	Y		
suchi	suchi_apanay	remove element i, shifting the rest left. Returns 1 ok / 0 out of bounds.	Y		
suchi	suchi_vinimay	vinimay elements i and j (WS2, R20). Returns 1 ok / 0 if either index is out of bounds (then nothing changes). Before this, swapping meant a temp variable plus two suchi_sangrah calls at every ca	Y		
suchi	suchi_viparyay	reverse the list in place (WS3, R20). Two-pointer vinimay, same shape as khand_viparyay. Returns 1. Before this, reversing a list meant a hand-written two-index loop at every call site.	Y		
suchi	suchi_shreni	sort the list in place, ascending (WS2, R21). Merge sort (O(n log n)) over the list's data array. Before this, sorting a list meant `yoj shreni` plus a hand-written `mil_shreni(l[2],…	Y		
suchi	suchi_laghu	smallest element (WS2, R21); ok[0] 1, or 0 if the list is empty (returns 0 then). Before this, the caller wrote the min loop by hand or called shreni.smlib's laghu on l[2] — which reads a…	Y		
suchi	suchi_adhik	largest element (WS2, R21); ok[0] 1, or 0 if the list is empty (returns 0 then). See suchi_laghu.	Y		
suchi	suchi_yog	sum of the elements (WS2, R21); 0 for an empty list (well-defined, no ok channel needed). Before this, the caller wrote the sum loop by hand or called shreni.smlib's yog on l[2].	Y		
suchi	suchi_gan	number of occurrences of v (WS2, R21). Before this, the caller wrote the count loop by hand or called shreni.smlib's gan on l[2].	Y		
suchi	suchi_anwesh	first index of v, or -1 (WS2, R23). List-shaped form of shreni.smlib's anwesh_sarak; before, the caller called anwesh_sarak(l[2], suchi_maap(l), v) by hand.	Y		
suchi	suchi_asti_sorted	1 if the elements are in non-decreasing order, else 0; empty and single-element lists are sorted (WS2, R23). List-shaped form of shreni.smlib's asti_sorted.	Y		
suchi	suchi_dwi_anwesh	index of v in a SORTED list, or -1 (WS2, R23). List-shaped form of shreni.smlib's dwi_anwesh. The caller must sort first (suchi_shreni); on an unsorted list the result is undefined, exactly as wi	Y		
suchi	suchi_rikta	empty the list, keeping the allocated capacity. R19: also ZEROES the data cells (was: len reset only). The old elements were reachable after a clear to anyone reading the data array through…	Y		
suchi	suchi_antah	1 if any element equals v, else 0.	Y		
suchi	suchi_kramank	first index with value v, or -1 if absent.	Y		
suchi	chay_khip	push v. Returns 1 ok / 0 allocation failure.	Y		
suchi	chay_apanay	pop the top value; sets ok[0] to 1 on success, 0 when the stack is empty (returns 0 then).	Y		
suchi	chay_avalok	top value without removing it; ok[0] 1/0.	Y		
suchi	chay_rikta	1 if the stack is empty, else 0.	Y		
suchi	avali_srij	allocate an empty queue. cap clamped to >= 1. Returns the queue handle, or 0 on allocation failure — including a cap so large the data size overflows (as suchi_srij).	Y		
suchi	avali_pravesh	append v at the tail. Returns 1 ok / 0 allocation failure.	Y		
suchi	avali_nishkas	remove and return the front value; sets ok[0] to 1 on success, 0 when the queue is empty (returns 0 then).	Y		
suchi	avali_avalok	front value without removing it; ok[0] 1/0.	Y		
suchi	avali_tak_mala	write the queue's elements into out in logical (FIFO) order, one qword cell each, WITHOUT mutating the queue (WS2, R23). Returns avali_maap(q). Caller allocates cap cells. Before, reading a queue	Y		
suchi	avali_antah	1 if v is in the queue, else 0 (WS2, R21). Scans the ring WITHOUT mutating it (no dequeue loop). Before this, the caller hand-rolled the ring scan with (head + k) % cap arithmetic at every…	Y		
suchi	avali_rikta	empty the queue in place (WS2, R19): same handle, same capacity, head reset to 0, and the ring data ZEROED — the dequeued dead space held stale values readable through q[2], the same hazard…	Y		
suchi	avali_shunya	1 if the queue is empty, else 0.	Y		
suchi	avali_maap	element count.	Y		
vakyank	ank_tak_varna	write decimal representation of int n into mala out as character codes. Returns the character count (excluding terminator). out[ count ] is set to 0 as a terminator. Caller allocates >= 22 cells.	Y		
vakyank	varna_tak_ank	parse first n character codes of mala buf as a decimal integer. Leading '-' negates. Returns the value; sets ok[0] to 1 on success, 0 on malformed input (ok is a 1-cell mala).	Y		
vakyank	ank_tak_aadhar_varna	write n in any base 2..36 into out as character codes (0-9, a-z). Returns count. No util_chinha handling; n >= 0. Base outside 2..36: terminator only, returns 0 (base 0 trapped with S	Y		
vakyank	varna_tak_ank_aadhar	parse first n char codes of buf in `base` (2/8/10/16). Sets ok[0]. Returns value.	Y		
vakyank	pad_vam	left-pad the `count` character codes in mala `out` to `width` using fill character code `fill`, in place. Returns the new count (width if width > count, else count). Caller must allocat	Y		
vakyank	varna_tak_dashm	parse a decimal float from a byte string. Grammar: [-] digits [. digits] [(e/E) [-] digits]; at least one digit in the integer or fraction part. No leading/trailing whitespace, no '+', no "in	Y		
varna	varna_maap	Returns NUL-terminated packed string length (byte count), by vartani_aayam.	Y		
varna	akshar_sanket	byte code of s[i] (the akshar builtin on a string).	Y		
varna	asti_ank_akshar	1 if s[i] is a decimal digit ('0'-'9'), else 0.	Y		
varna	asti_unnat_akshar	1 if s[i] is an uppercase letter ('A'-'Z'), else 0.	Y		
varna	asti_avanat_akshar	1 if s[i] is a lowercase letter ('a'-'z'), else 0.	Y		
varna	asti_akshar_akshar	1 if s[i] is any letter (A-Z or a-z), else 0.	Y		
varna	asti_avakash_akshar	1 if s[i] is a space (code 32), else 0.	Y		
varna	gan_swar	count of lowercase vowels (a, e, i, o, u) in the string s.	Y		
varna	gan_akshar	count of occurrences of byte code in the string s.	Y		
varna	anwesh_akshar	index of the first occurrence of byte code in s, or -1.	Y		
varna	asti_sarv_ank	1 if s is non-empty and every character is a digit, else 0.	Y		
varna	unnat_sanket	byte code c converted to uppercase (a-z -> A-Z, other codes unchanged).	Y		
varna	avanat_sanket	byte code c converted to lowercase (A-Z -> a-z, other codes unchanged).	Y		
varna	varna_sam	1 if strings a and b are byte-identical (same length and bytes), else 0.	Y		
varna	varna_anwesh	index of first occurrence of needle in hay, or -1. Empty needle matches at 0. Negative needle length is invalid: -1 (the old code treated it as empty, matching at 0).	Y		
varna	varna_antah	1 if needle occurs in hay, else 0.	Y		
varna	varna_pratisthap	copy src to out, replacing every (non-overlapping) occurrence of find with repl. repl is 0-terminated (its length is derived) — repl cannot be a slice; copy the slice into	Y		
varna	varna_bhed	split src on sep. parts is a flat buffer holding length-prefixed segments: [len0, c0, c1, ..., len1, c0, ...] To recover segment i: walk from parts[0], skipping (1 + len)	Y		
varna	varna_yuj	inverse of varna_bhed for the length-prefixed format. Joins `count` segments with sep. Returns new count.	Y		
varna	varna_chhid	strip leading/trailing ASCII spaces (32). Returns new count.	Y		
varna	varna_unnat	varna_unnat(src, sn, out) / varna_avanat — ASCII case conversion. sn < 0: empty output (the old code wrote the terminator at out[-1], an out-of-bounds write before the buffer).	Y		
varna	varna_avanat	copies src (sn qword cells) to out with A-Z lowercased, NUL-terminated; returns sn (0 for sn < 0).	Y		
varna	varna_aadi	varna_aadi(src, sn, pre, pn) / varna_ant — 0/1. A negative prefix/suffix length is invalid: 0 (the old code treated it as empty and returned 1).	Y		
varna	varna_ant	1 if the src string (sn cells) ends with suf (sn2 cells), else 0.	Y		
varna	varna_tul	-1 / 0 / 1 (lexicographic by char code).	Y		
varna	varna_viparyay	copy the cell array reversed into out (WS1, R20). Cell-array form of khand_viparyay: the same two-pointer vinimay, so it is safe in place (src == out works). Writes a 0 terminator cell at o	Y		
varna	varna_gan	count non-overlapping occurrences of needle in hay, over cell arrays (WS1, R20). Cell-array form of khand_gan. Empty needle returns 0. (Pointer arithmetic is in bytes: the suffix at cell	Y		
```

## WS2 — Calibration (confirmed from actual bodies)

1. **`samanvaya.nishan` — N; body IS matrix trace** (`lib/samanvaya.smlib:111-119`): loop sums `a[i*n+i]` for i=0..n-1; `nishan` means a mark, not diagonal sum. Suggest `karna_yog` after linguistic signoff.
2. **`samanvaya.pehchan` — N; body IS identity-matrix construction** (`lib/samanvaya.smlib:32-46`): diagonal cells get 1.0, others 0.0; Hindi recognition/identification is not an apt Sanskrit matrix term. Suggest `ekaka_matrika`.
3. **`samanvaya.samanvaya_akar_na` — N; body IS inverse shape-fit predicate** (`lib/samanvaya.smlib:23-29`): returns 1 if m/n negative or m>len/n; returns 0 if valid, including n==0. Existing suffix `na` captures negation in part, **so do NOT rename to `samanvaya_akar`** (that would invert the meaning). Suggest `samanvaya_akar_ayogya` because the function means invalid/non-fitting shape.
4. **All four `suchi.chay_*` — Y; no rename:** `chay` (चय) is a genuine Sanskrit pile/heap. `chay_khip` pushes, `chay_apanay` pops with `ok[0]`, `chay_avalok` peeks, and `chay_rikta` tests emptiness (`lib/suchi.smlib:325-365`). Reject the earlier claim that `chay` was not Sanskrit.

### Y/N clarification on vocabulary

An English algorithm word can be semantically accurate: `gudh.fnv1a` truly computes FNV-1a, `kalana.simpson` implements Simpson's rule, and `ganit.bit_gan` counts set bits. These remain **Y**, even if Sanskrit-only vocabulary cleanup may eventually rename them. Conversely `sankhyiki.bindu` uses the word 'point' for a scalar dot product and is flagged **N** for this narrow precision rubric; traditional/technical idiom must be considered in owner review.

## Confirmed semantic mismatches and alternatives (the N rows)

- `ank.asti_vilom`: **N** — Tests decimal-digit palindrome, not whether a number merely is reversed. Suggested `asti_viparyay_sam`. `lib/ank.smlib:58`.
- `anukram.anukram_maap_ashtak`: **N** — Returns encoded size 8+n for a variable-length payload, not size of a fixed octet. Suggested `anukram_maap_aayam_purva`. `lib/anukram.smlib:30`.
- `anukram.anukram_khip_ashtak`: **N** — Writes an eight-byte LENGTH PREFIX followed by n payload bytes, not just eight bytes. Suggested `anukram_khip_aayam_purva`. `lib/anukram.smlib:88`.
- `anukram.anukram_grah_ashtak`: **N** — Reads an eight-byte LENGTH PREFIX followed by variable payload, not an octet alone. Suggested `anukram_grah_aayam_purva`. `lib/anukram.smlib:110`.
- `brihat.brihat_shesh_tr`: **N** — Suffix `tr` does not describe caller-supplied n-digit scratch used in modular reduction. Suggested `brihat_shesh_sahaya`. `lib/brihat.smlib:270`.
- `chandas.dviguna`: **N** — Body computes power of two (2^n); `dviguna` ordinarily suggests doubling n (2*n). Suggested `dwi_ghat`. `lib/chandas.smlib:12`.
- `ganit.mahattam`: **N** — Returns greatest common DIVISOR; name only means greatest and omits divisor relation. Suggested `mahattam_samanya_bhajak`. `lib/ganit.smlib:44`.
- `ganit.laghuttam`: **N** — Returns least common MULTIPLE; name only means least and omits multiplicity relation. Suggested `laghuttam_samanya_gunaja`. `lib/ganit.smlib:61`.
- `kalana.pravan2`: **N** — The function computes second numerical DERIVATIVE, not simply a second slope value. Suggested `dwitiya_avakalaja`. `lib/kalana.smlib:79`.
- `roop.roop_ank_aadhar2`: **N** — `2` is a format variant index, not base two: code accepts bases 2..36 and prints optional minus. Suggested `roop_ank_aadhar_saral`. `lib/roop.smlib:150`.
- `roop.roop_varg_mool`: **N** — Formats digit GROUPS (Indian/global), not a root/square root; `mool` is opaque here. Suggested `roop_ank_varg_sahaya`. `lib/roop.smlib:359`.
- `sadhan.antargam`: **N** — Body computes linear interpolation by percentage; generic inward movement conceals the interpolation. Suggested `antara_prakshepan`. `lib/sadhan.smlib:9`.
- `sadhan.util_chinha`: **N** — Returns mathematical signum −1/0/1, not a general utility symbol or mark. Suggested `ank_chihna`. `lib/sadhan.smlib:43`.
- `samanvaya.samanvaya_akar_na`: **N** — Tests if m×n DOES NOT FIT length (or negative sizes); `shape-not` does not identify the capacity predicate. Suggested `samanvaya_akar_ayogya`. `lib/samanvaya.smlib:23`.
- `samanvaya.pehchan`: **N** — Hindi 'recognition' is not a mathematical identity matrix; body constructs diagonal ones/off-diagonal zeros. Suggested `ekaka_matrika`. `lib/samanvaya.smlib:32`.
- `samanvaya.nishan`: **N** — Hindi/Persian 'mark' does not name the matrix TRACE computed by summing the diagonal. Suggested `karna_yog`. `lib/samanvaya.smlib:111`.
- `samanvaya.nirnaya2`: **N** — `nirnaya` = decision; code is specifically determinant of order 2, not general decision. Suggested `dwi_kram_nirdharak`. `lib/samanvaya.smlib:122`.
- `samanvaya.nirnaya3`: **N** — `nirnaya` = decision; code is determinant of order 3, not general decision. Suggested `tri_kram_nirdharak`. `lib/samanvaya.smlib:127`.
- `samanvaya.sadish_yoga`: **N** — The body multiplies corresponding coordinates and sums: scalar DOT product, not vector addition. Suggested `sadish_antar_gunana`. `lib/samanvaya.smlib:135`.
- `sankhyiki.bindu`: **N** — `bindu` means point/dot; the body computes a scalar INNER PRODUCT, not a point. Suggested `antar_gunana`. `lib/sankhyiki.smlib:99`.

## WS3 — Accurate name but SURPRISING body: add a comment, not a rename

These are *body-derived traps* whose names are generally reasonable but whose contracts need an explicit usage example or note:

- `brihat.brihat_ank_se_laghu` (lib/brihat.smlib:28): Works on absolute magnitude: negative input does not preserve a minus sign; INT64_MIN has special handling.
- `brihat.brihat_ank_tak_laghu` (lib/brihat.smlib:69): Reverse conversion assumes the big number fits in a native integer; overflow beyond that is not a representable result.
- `brihat.brihat_bhajshesh` (lib/brihat.smlib:194): Long division supplies quotient AND remainder; the modulus-zero path requires checked status handling.
- `brihat.brihat_shesh` (lib/brihat.smlib:257): Reduces a 2n-digit dividend modulo an n-digit divisor, not only equal-sized arrays.
- `gudh.fnv1a` (lib/gudh.smlib:14): Hashes packed bytes using FNV-1a; it is not encryption and should not be advertised as a secure hash.
- `ganita.ganita_paripurna_bhaj` (lib/ganita.smlib:501): When divisor equals zero it returns the SENTINEL zero, which is also a legitimate quotient.
- `ganita.ganita_paripurna_shesh` (lib/ganita.smlib:519): On divisor zero returns sentinel zero; there is no explicit ok channel.
- `ganita.ganita_paripurna_nirapeksh` (lib/ganita.smlib:549): Absolute value of INT64_MIN saturates to INT64_MAX rather than returning exact magnitude.
- `ganit.ganit_yadricch` (lib/ganit.smlib:162): Deterministic linear-congruential PRNG: caller supplies state; it is not cryptographic randomness or entropy.
- `ganit.ghat` (lib/ganit.smlib:75): Negative integer exponents return 1 by loop fallthrough instead of rational reciprocal.
- `kalana.simpson` (lib/kalana.smlib:34): With an even number of samples, drops final sample to use Simpson's 1/3 rule; n<3 calls trapezoid.
- `kalana.pravan` (lib/kalana.smlib:59): Identical consecutive x coordinates return 0.0 rather than infinity or an error.
- `kalana.bahu_mula` (lib/kalana.smlib:119): Status `ok` must ALREADY contain an element; caller must prefill before invocation.
- `khand.khand_chhid` (lib/khand.smlib:319): Trims ASCII space (0x20) only; it does not trim all Unicode whitespace.
- `nighantu.nighantu_grah` (lib/nighantu.smlib:159): Missing key returns −1, indistinguishable from a legitimate stored value −1; use nighantu_antah.
- `nighantu.nighantu_vardh` (lib/nighantu.smlib:279): Returns a NEW map handle; does not mutate/reallocate original map in place.
- `nighantu.nighantu_kunjika` (lib/nighantu.smlib:383): Exports keys in length-prefixed cell form, not packed NUL-terminated byte strings.
- `nighantu.nighantu_kunjika_ashtak` (lib/nighantu.smlib:417): Exports length-prefixed PACKED bytes and a single-byte length field, unlike nighantu_kunjika.
- `patra.patra_asti` (lib/patra.smlib:81): Tests whether path opens read-only: 0 can mean absent OR inaccessible due to permissions.
- `phal.phal_mulya` (lib/phal.smlib:56): On error Result, returns zero; callers should check phal_asti_siddhi rather than treating 0 as evidence of success.
- `roop.roop_sthir_mool` (lib/roop.smlib:473): Uses half-away-from-zero rounding of fixed-point output, not bankers' rounding.
- `roop.roop_varg` (lib/roop.smlib:445): Defaults to INDIAN digit grouping (12,34,567), rather than international grouping (1,234,567).
- `sadhan.bhaj_urdhva` (lib/sadhan.smlib:25): Ceiling division returns 0 on zero divisor; it cannot report division failure separately.
- `sankhyiki.purna_prasaran` (lib/sankhyiki.smlib:181): Integer variance uses truncated integer mean and result; not exact floating-point population variance.
- `shreni.asti_sorted` (lib/shreni.smlib:98): Accepts non-decreasing order; duplicate equal adjacent values are considered sorted.
- `sangrah.rakh_tak_mala` (lib/sangrah.smlib:217): Exports a SORTED list of length-prefixed set keys, not arbitrary insertion order.
- `suchi.chay_apanay` (lib/suchi.smlib:331): Returns 0 on empty but sets an `ok[0]` flag; zero can also be a legitimate popped value.
- `suchi.avali_pravesh` (lib/suchi.smlib:403): Queue enqueue appends to TAIL through ring-buffer indexing, not head; amortized O(1) rather than array shift.
- `suchi.avali_nishkas` (lib/suchi.smlib:437): Queue dequeue removes HEAD via ring-buffer pointer (O(1)), not array shifting.
- `suchi.suchi_rikta` (lib/suchi.smlib:285): Clears BOTH the logical count and the previous data cells, unlike `kosh_clear` which resets length only.
- `varna.gan_swar` (lib/varna.smlib:60): Counts lowercase ASCII vowels a/e/i/o/u only, NOT Devanagari Sanskrit vowels or uppercase vowels.
- `varna.varna_maap` (lib/varna.smlib:17): Computes BYTE length of packed NUL-terminated text, not Unicode character count.
- `vakyank.varna_tak_dashm` (lib/vakyank.smlib:270): Parses a decimal floating-point string including optional exponent, not a single decimal digit.

## Pinned source inventory

- `lib/aadhar.smlib` blob `03a29301d6b5528c0d981ad190c0bf880d9b2d7c`; 2 declarations.
- `lib/ank.smlib` blob `4fc90c1a10e4ef9eea17051f1552f08667191c00`; 10 declarations.
- `lib/anukram.smlib` blob `9a601739a7af9219a1846df254356afd35df8574`; 5 declarations.
- `lib/brihat.smlib` blob `2a34af6f9ab3793edd40ebf54f3f3e90f6b02091`; 13 declarations.
- `lib/chandas.smlib` blob `8637199d80fc80d51d0000693c153253fdf9a39a`; 6 declarations.
- `lib/ganit.smlib` blob `381c1c9a3a64f8f1c67b2b2ef52a4d3774371444`; 18 declarations.
- `lib/ganita.smlib` blob `803d6e64bb6dbda29f833fe274271b35225dad2a`; 22 declarations.
- `lib/gudh.smlib` blob `0fc90441ba7e8d6e5d7ea556e1f1189f926080f1`; 2 declarations.
- `lib/kalana.smlib` blob `975aedc7725cc2e3d87b6b8aba630b4bb8cc4744`; 6 declarations.
- `lib/khand.smlib` blob `3f2d4d485dd0a86d80faaa4566977135c41161f2`; 22 declarations.
- `lib/madhava.smlib` blob `28a13649c9b8442c93209ee0c2db130a78bb05f0`; 5 declarations.
- `lib/mala.smlib` blob `de4e247aeb862e0f8986ce04de47b08aac417fe4`; 8 declarations.
- `lib/nighantu.smlib` blob `53b584607efe8065bea4e7f59d18e782607905c0`; 17 declarations.
- `lib/patra.smlib` blob `84a164e5e809fb73cc546cce6333abf08195385e`; 3 declarations.
- `lib/phal.smlib` blob `9fd9dacffb9129f380ae97bd35a443be97fb5127`; 14 declarations.
- `lib/roop.smlib` blob `120860730beff981b95ff8da4e91130ff284b78a`; 23 declarations.
- `lib/sadhan.smlib` blob `2501566598d48c84c202fececf6c528d8777fd0d`; 7 declarations.
- `lib/samanvaya.smlib` blob `89714a1ac14b2bf5c7d87876470b18728f28ac37`; 11 declarations.
- `lib/sangrah.smlib` blob `539bc6e4b45efcb70096eae97339c35941649c07`; 14 declarations.
- `lib/sankhyiki.smlib` blob `e99c2e492f9f5202bf26a5c055c4365b4dd434f6`; 16 declarations.
- `lib/shreni.smlib` blob `b356405884c5f09cf1de8c806c22ce0bcc502b7d`; 14 declarations.
- `lib/suchi.smlib` blob `6ecdd24d8305be8d049225ce0128fdbf481e8e42`; 34 declarations.
- `lib/vakyank.smlib` blob `67f47ff392297cea4a911dd1e99a068700950f11`; 6 declarations.
- `lib/varna.smlib` blob `bd17f8bf59c1f04c92ff29c4604531da396a369e`; 27 declarations.

## Testing, provenance and handoff

- **PASS — STATIC:** inspected all 305 declarations and source-body content from 24 live pinned GitHub blob versions. Completeness: 119 declarations in Part1, 186 in Part2. Distinct (module,function) pairs: 305. No missing row in the two retained source receipts.
- **PASS — CALIBRATION:** read direct returns/writes/loop conditions of all requested known cases; record names and bodies separately.
- **NOT RUN - no toolchain:** native Sutram compile, runtime tests, regression suite, 577 guard, 226 proofs, Windows acceptance. None are silently treated as passed from this read-only audit.
- **NOT APPLIED:** names, docs, examples, source, compiler, `tests/`, `lang/`, frozen packs, `Windows-to-Sarvam/`, `backups/` untouched.
- **CAVEAT:** surrounding comments can be stale even at the pinned blob; the TSV is a static *semantics and naming screen*, not formal verification of all 305 mathematical contracts. Where a shorter name is a Sanskrit compound, a qualified Sanskritist and owner must confirm it before any API break. Any partner implementation must preserve legacy aliases and verify goldens.

Exactly **one** manual check round (129); stop and await next `CHECK FOLDER`.
