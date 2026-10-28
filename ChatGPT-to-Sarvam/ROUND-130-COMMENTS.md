# Sutram — ROUND 130: the 33 surprising contracts, four shorter names, and the `sadish_yoga` verdict

**Incoming:** `Sarvam-to-ChatGPT/ROUND-130.md` (blob `57b47a9f76f7f2f74dce1841b38ef65a8086c489`). **Pinned initial `main`:** `8236bdd4c036dc6f5a89e0dcc5e5370a570cef95`, changelog v409. **Scope:** Sanskrit-only review; exactly one new round. **Do NOT edit source**; partner Muse has concurrent library-comment work.

## WS1 — exactly 33 ready-to-insert comment lines (TSV)

**Application rule:** Match the `prakriya <function>(` declaration in the named file. Insert its proposed `#` comment immediately above the declaration **only after checking whether Muse already added an equivalent comment**. Prefer replacing/reconciling duplicate existing contract comments rather than stacking inaccurate/repetitive prose. This TSV is not a patch and makes **no source changes**. Inline `#` comments are Sutram syntax; any future application requires a build/gate rerun by the source owner.

```tsv
file	function	comment_line
lib/brihat.smlib	brihat_ank_se_laghu	# brihat_ank_se_laghu: writes the absolute value as LSB-first decimal cells; the sign is lost, INT64_MIN is handled specially, and insufficient digits return 0.
lib/brihat.smlib	brihat_ank_tak_laghu	# brihat_ank_tak_laghu: converts LSB-first digit cells to a native integer; the caller must ensure the value fits signed int64 (no overflow status).
lib/brihat.smlib	brihat_bhajshesh	# brihat_bhajshesh: writes both quotient q and remainder r; for divisor zero it leaves q=0 and copies a into r, without a distinct failure status.
lib/brihat.smlib	brihat_shesh	# brihat_shesh: reduces a 2*n-digit dividend modulo an n-digit divisor; zero modulus preserves the low n digits, and scratch-allocation failure returns -1.
lib/gudh.smlib	fnv1a	# fnv1a: computes a 32-bit FNV-1a hash of the first len packed bytes; it is non-cryptographic and is NOT encryption or a secure digest.
lib/ganita.smlib	ganita_paripurna_bhaj	# ganita_paripurna_bhaj: returns 0 for division by zero (also a valid quotient), and saturates INT64_MIN / -1 to INT64_MAX; no error flag is returned.
lib/ganita.smlib	ganita_paripurna_shesh	# ganita_paripurna_shesh: returns 0 on divisor zero (also a valid remainder); INT64_MIN % -1 returns the exact zero without hardware trapping.
lib/ganita.smlib	ganita_paripurna_nirapeksh	# ganita_paripurna_nirapeksh: returns abs(a), except abs(INT64_MIN) saturates to INT64_MAX because the exact positive magnitude is unrepresentable.
lib/ganit.smlib	ganit_yadricch	# ganit_yadricch: updates state[0] using a deterministic 64-bit linear-congruential recurrence; not seeded from entropy and NOT secure randomness.
lib/ganit.smlib	ghat	# ghat: calculates integer base^e for e>=0; for a negative exponent the loop does not run and returns 1 (not a reciprocal).
lib/kalana.smlib	simpson	# simpson: uses Simpson's 1/3 rule with equally spaced samples; even usable sample counts discard the last sample, and fewer than 3 use trapezoids.
lib/kalana.smlib	pravan	# pravan: estimates first derivative by central or endpoint difference; zero x-spacing yields sentinel 0.0 rather than an undefined-derivative error.
lib/kalana.smlib	bahu_mula	# bahu_mula: bisects a bracketed polynomial root; ok must ALREADY have element 0, which receives 1 on success or 0 if no sign bracket exists.
lib/khand.smlib	khand_chhid	# khand_chhid: removes leading and trailing ASCII SPACE byte 32 only; tabs, newlines and multi-byte Unicode whitespace remain unchanged.
lib/nighantu.smlib	nighantu_grah	# nighantu_grah: returns -1 when a key is absent, but -1 is also storable; call nighantu_antah to distinguish absence from a stored -1.
lib/nighantu.smlib	nighantu_vardh	# nighantu_vardh: rehashes into a NEW map allocation and returns its handle (or 0 on failure); the original handle is not resized in place.
lib/nighantu.smlib	nighantu_kunjika	# nighantu_kunjika: exports keys as length-prefixed qword CELL sequences [len, byte-cell...], not packed byte strings; returns the key count.
lib/nighantu.smlib	nighantu_kunjika_ashtak	# nighantu_kunjika_ashtak: exports each key as [one length byte, packed key bytes...] without terminators; returns key count, unlike cell-form kunjika.
lib/patra.smlib	patra_asti	# patra_asti: tests whether a path can be opened read-only; 0 may indicate a missing file OR access denied, not guaranteed non-existence.
lib/phal.smlib	phal_mulya	# phal_mulya: reads the Result value cell even for failure; first check phal_asti_siddhi, since value 0 alone is not a success signal.
lib/roop.smlib	roop_sthir_mool	# roop_sthir_mool: formats fixed decimals with half-away-from-zero rounding (not ties-to-even); requested places are clamped to 0..9.
lib/roop.smlib	roop_varg	# roop_varg: groups digits in Indian style (for example 12,34,567); use roop_varg_vishwa for international 1,234,567 grouping.
lib/sadhan.smlib	bhaj_urdhva	# bhaj_urdhva: performs signed integer ceiling division; divisor zero returns sentinel 0 and cannot be distinguished from a legitimate quotient.
lib/sankhyiki.smlib	purna_prasaran	# purna_prasaran: integer population variance uses a truncated integer mean and integer division; do not treat result as exact float variance.
lib/shreni.smlib	asti_sorted	# asti_sorted: returns 1 for NON-DECREASING array order (equal adjacent elements are allowed); it does not sort or mutate the array.
lib/sangrah.smlib	rakh_tak_mala	# rakh_tak_mala: exports set keys in bytewise lexicographically SORTED length-prefixed qword-cell form; output is not insertion order.
lib/suchi.smlib	chay_apanay	# chay_apanay: pops stack top; on empty returns 0 and sets ok[0]=0, while a valid popped zero sets ok[0]=1.
lib/suchi.smlib	avali_pravesh	# avali_pravesh: appends at the ring-buffer TAIL; normal insertion avoids shifting, but full capacity may allocate and copy to grow.
lib/suchi.smlib	avali_nishkas	# avali_nishkas: removes the ring-buffer HEAD in O(1) without shifting; on empty returns 0 and sets ok[0]=0.
lib/suchi.smlib	suchi_rikta	# suchi_rikta: resets list length and zeroes all allocated data cells, preserving capacity; unlike kosh_clear, it erases old cell contents.
lib/varna.smlib	gan_swar	# gan_swar: counts only lowercase ASCII a/e/i/o/u bytes; it does not count uppercase vowels, UTF-8 Sanskrit vowels or Devanagari letters.
lib/varna.smlib	varna_maap	# varna_maap: counts packed NUL-terminated text BYTES, not Unicode code points or grapheme clusters; multi-byte characters occupy multiple bytes.
lib/vakyank.smlib	varna_tak_dashm	# varna_tak_dashm: parses decimal digits with optional minus, decimal point and e/E exponent from character-code CELLS, setting ok[0] on success/failure.
```

**Readback provenance:** Each of the 33 names matches exactly one function in the pinned 305-function Round-129 source-body receipts `ROUND-129-RAW-BODIES-PART1.json` and `ROUND-129-RAW-BODIES-PART2.json`. The 24 live `lib/*.smlib` Git blobs at this Round-130 head are **byte-for-byte identical** to the blobs used in Round 129; **0 changed**. Thus the earlier full-source body evidence remains applicable. The short comment lines are additional explanatory contracts; not assertions that the existing comments are missing. Round 129 independently identified 33 such surprises, and this TSV has 33 matching rows.

## WS2 — four shorter names examined

| Current name | Shorter exact Sanskrit alternative? | Decision and lexical reason |
|---|---|---|
| `ganit.mahattam` (GCD) | **No verified under-15-character unambiguous noun/compound** | `mahattam` by itself means 'greatest', omits *common divisor*. The established mathematical formulation is **महत्तम समापवर्तक** / `mahattama_samapavartaka` (greater length). In Sutram's transliteration, `mahattam_samanya_bhajak` is a semantically clear project-specific compound. A hypothetical short `maha_samabhaj` is **not** verified as a Sanskrit term, so reject any false claim of precision to save keystrokes. **Keep the long precise proposal** pending owner approval. |
| `ganit.laghuttam` (LCM) | **No verified under-15-character exact noun/compound** | `laghuttam` by itself says least, not *common multiple*. The established school-mathematics term is **लघुत्तम समापवर्त्य** / `laghuttama_samapavartya`. A short form would need a documented Sanskrit technical convention; none established here. **Keep a clear longer compound** (prefer `laghuttama_samapavartya` as the precise technical concept, if owner approves the length), rather than invent a misleading short name. |
| `sankhyiki.bindu` (dot product) | **YES: `bindu_gunan`**, 11 Latin characters | `bindu` ('point/dot') alone is vague; **`bindu` + `gunan` (गुणन, multiplication)** transparently means *dot product* in the mathematical technical register, shorter than `antar_gunana` (12). Not claimed to be an independently attested **classical Sanskrit headword**; it is a precise modern technical compound. The result is a **scalar** `sum(a[i]*b[i])`, not vector addition. Reserve the name within `sankhyiki`; check for collisions before any rename. |
| `ank.asti_vilom` (numeric palindrome test) | **YES, a shorter clear project compound: `asti_viloma_sam`**, 15 Latin characters | `asti` = 'is', `viloma` = 'reversed/opposite', project `sam` = 'equal': literally **is reverse-equal**. This is **shorter** than R129's `asti_viparyay_sam` (17) and encodes comparison, not just reversal. It is **not asserted as a dictionary-attested single Sanskrit word**; the literary term `vilomapada` is also known for palindromic text but would wrongly suggest a word/text predicate rather than an integer-digit predicate. Do not replace `asti_vilom` with merely `viloma`: that omits the equality test. |

**Sources outside the repo (terminology check only, not test evidence):** [SATHEE mathematical GCD/LCM](https://sathee.iitk.ac.in/hi/sathee-jee/article/maths/hcf-and-lcm/) for greatest common factor vs least common multiple; [SATHEE vector product](https://sathee.iitk.ac.in/hi/sathee-jee/crash-course-notes/maths/day-36-vector-algebra-study_notes/) distinguishes scalar dot product from vector sum; [Sanskrit palindrome composition study](https://so04.tci-thaijo.org/index.php/jasu/article/view/239304) for `viloma` reversal terminology. These are **predominantly modern Hindi mathematical register or scholarly Sanskrit studies**, not classical dictionary proof that a coined API name is ancient Sanskrit.

**Length/counting note:** count actual Latin letters, not Sarvam's approximate figures: `mahattam` is 8, `laghuttam` is **9** (not 8), `bindu` 5, `bindu_gunan` 11, `asti_viloma_sam` 15 and `asti_viparyay_sam` 17.

## WS3 — does `sadish_yoga` ever mean dot product?

**Decisive body:** `lib/samanvaya.smlib`, function `sadish_yoga(kosh dasham u, kosh dasham v)`, returns one `dasham` scalar `s = sum_{i=0}^{min(len(u),len(v))-1} u[i]*v[i]`. It **does not** produce a vector, nor does it add vectors component-by-component. Unlike a whole-array sum, a dot product involves **pairwise multiplication then scalar accumulation**.

**Charitable reading:** `yoga` can mean joining, addition, or summation, and a dot product *contains* a summation. One could call this 'sum [of products] of vectors' in an expanded explanatory phrase. That is not an exact reading of **bare `sadish_yoga`** in a mathematical API, where **सदिश योग** means **vector sum/addition**. It omits both the product and scalar-result aspects and invites the wrong computation.

**Verdict:** **FAIL as a public operation name; not defensible as a precise identifier for dot product.** Rename recommendation stands, with `sadish_antar_gunana` or `sadish_bindu_gunan` as fuller candidates, subject to owner decision, collision scan and compatibility aliases. **No code or public API changed in this round.** `sankhyiki.bindu_gunan` above is a shorter context-specific equivalent, but may have collision risks if the libraries are jointly imported.

## Verification status and boundaries

- **PASS / read-only:** 33/33 original WS3 targets extracted from Round 129; each name resolves to a distinct pinned library declaration; 24/24 `lib/*.smlib` Git blob hashes unchanged from the Round-129 evidence; exact 3-column TSV generated.
- **PASS / source analysis:** checked the specific implementation of `sadish_yoga`, the four target names' semantics, and relevant edge cases for comments against retained full body source text.
- **NOT RUN - no toolchain:** compiler, test suite, raw output, byte-parity guard, Windows native acceptance. External mathematical references are not a substitute.
- **NOT APPLIED:** any source or naming change; `lib/`, `tests/`, `docs/`, `lang/`, `Windows-to-Sarvam/`, `backups/` remain untouched by ChatGPT.
- **Owner gate:** these comments and proposed names require Sarvam/Muse/Claude integration review, conflict checking, exact-head validation and tests before public release.

**Round 130 complete — one manually triggered assignment; stop.**
