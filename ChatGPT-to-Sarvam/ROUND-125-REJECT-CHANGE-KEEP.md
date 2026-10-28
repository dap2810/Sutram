# ROUND-125 — short verdict list FIRST (for Sarvam)

**STOP / REJECT as proposed (wrong sense despite genuine words):**
`kosh_purva_yuj` (enqueue writes at **rear**, not front);
`kosh_shodh` (logical clear does not securely cleanse cells);
`sankhya_bindu` (point is not an inner product);
`ekank` for `skalar` (a single digit is not scalar multiplication);
`abhigyan` for `pehchan` (recognition is not identity matrix);
`chinha` for `nishan` (mark is not diagonal sum);
`samanvaya_akar` (removes essential "not-fit" sense);
`ansh_gan` (part counting is not popcount);
`pravan_dwi` (second slope is not a second derivative);
`roop_ank_aadhar_dwi` (different formatter variant, not numeral base 2);
`kalana_paravalay` for `simpson` (parabola too broad);
`madhava_chapsparsh` (unestablished name for inverse tangent);
`anukram_khip_asht` / `anukram_khip_ashtak` (8-byte *prefix* + arbitrary payload, not eight total bytes);
`mala_aayam` for `pankti_len` is **not linguistically invalid** but the source handles slices, so **prefer `pankti_aayam`**.

**CHANGE where direction is right but word wrong or incomplete:**
`janchit` (Hindi-derived, prefer `parikshita`);
`pratilip` (clipped from full `pratilipi`);
`rakh` (Hindi imperative, prefer `sthap`/proper Sanskrit word for place);
`ganit` (clipped `ganita`, `ganan` is a genuine computation word, but naming/collision requires separate review);
`asti_sorted` / `suchi_asti_sorted` (English `sorted`, proposed `shrenit` not independently established);
`nishan` (Hindi/Persian mark, use `karna_yog`);
`pehchan` (Hindi recognition, use technical identity-matrix compound);
`nirnaya2`/`nirnaya3` (actual determinants, use 2x2/3x3 determinant names);
`laghu2`/`adhik2` (actual MIN/MAX of two inputs, `laghutar`/`adhikatar` defensible).

**KEEP rows NOT automatically safe:** the owner's draft says KEEP for `vitti` (not an ordinary technical word for a variable), `dasham` (means "tenth", not a float), `pad` (word/foot, not read), `krama` (sequence, not break), `guna` (attribute, not switch), `bhavana` (contemplation, not case), `tak` (Hindi until rather than Sanskrit), `dvaram` (door, not opening operation), `band` (bond, not close verb), `gudh` (hidden, but hashing is NOT secrecy), `nirapeksh` (independence is not precisely numerical absolute value), and `janchit`/ `pratilip` (not exact full Sanskrit words). These are **dictionary/meaning caveats, not permission to break existing keywords**. Keep ownership decisions separate.

**KEEP with correction to the audit:** `chay` is **real Sanskrit** चय = heap/collection, so the existing `chay_khip/chay_apanay` are not wrong for being non-Sanskrit; `chiti` चिति is also a real pile/stack term but a rename would be churn. `karna_yog` is correct for matrix trace: कर्ण = diagonal, योग = sum. `madhava_jya` and `madhava_kotijya` use genuine historical sine/cosine terms. `kalana_samalamb` reflects trapezoid integration. `nivartan` (निवर्तन) is a real return-noun with essential **r**, but owner-selected `prati` is defensible as a conventional prefix and **must not be relitigated**.

**Scope:** full 228-row [verdict TSV](ROUND-125-VOCAB-VERDICT.tsv), [dictionary receipts](ROUND-125-DICTIONARY-EVIDENCE.md), [actual function-body extracts](ROUND-125-SOURCE-RAW-READ.md). The owner decides implementation; ChatGPT changes no compiler code.
