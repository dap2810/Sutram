# Sutram ROUND-116 WS1 — exact before/after source-comment replacements

**Pinned main**: `1884e8a327dca73a3b56db19b4197e1baac3ee06`; **source scope**: 15 library files. **No source file changed.** Each `old line` was checked against the exact source file from this commit, with **exactly one occurrence** (including punctuation and whitespace). The **new line is a proposal**, not tested compiler behavior. **Apply replacements on a fresh pin only if the old text still matches exactly once**, never by blind global replacement.

| File and source line on pin | OLD line (exact) | NEW line (exact) |
|---|---|---|
| `lib/aadhar.smlib:16` | `# Caller allocates out with >= 4*n cells (70 cells sufficed for` | `# Caller provides at least 1 writable output cell when n <= 0, or` |
| `lib/aadhar.smlib:17` | `# n <= 21 in base 2; n >= 22 overflowed the internal buffer).` | `# at least 4*n cells when n > 0 (base-2 worst case).` |
| `lib/aadhar.smlib:18` | `# Base outside 2..16: returns 0 (base 0 trapped with SIGFPE).` | `# Base outside 2..16 returns 0 without dividing (older code could trap).` |
| `lib/brihat.smlib:253` | `# brihat_shesh(num, shesh, res, n) — res = num % shesh, where num has 2n digits` | `# brihat_shesh(ank, shesh, res, n) — res = ank % shesh, where ank has 2n digits` |
| `lib/brihat.smlib:269` | `# brihat_shesh_tr(num, shesh, res, n, tr) — brihat_shesh with the caller's n-digit scratch tr.` | `# brihat_shesh_tr(ank, shesh, res, n, scratch) — brihat_shesh with caller's n-digit scratch.` |
| `lib/ganita.smlib:75` | `# Fills out[0] = x and out[1] = y.` | `# Writes out[0] = x and out[1] = y; caller must supply at least 2 writable qword cells.` |
| `lib/ganita.smlib:159` | `# Fills out[0] = a*c + n*b*d  and  out[1] = a*d + b*c.` | `# Writes out[0] = a*c + n*b*d and out[1] = a*d + b*c; requires 2 writable qword cells.` |
| `lib/gudh.smlib:12` | `# fnv1a(s, len) — FNV-1a 32-bit hash of first \`len\` chars of mala \`s\`.` | `# fnv1a(s, len) — FNV-1a hash of the first len BYTES of a packed byte-string pointer s.` |
| `lib/gudh.smlib:13` | `# Returns an unsigned 32-bit value (may print as negative via likha).` | `# Returns an unsigned 32-bit value in the integer range 0..4294967295.` |
| `lib/gudh.smlib:28` | `# fnv1a_varna(s) — FNV-1a of NUL-terminated mala \`s\` (uses vartani_len).` | `# fnv1a_varna(s) — FNV-1a of a NUL-terminated packed byte string (uses vartani_len).` |
| `lib/kalana.smlib:33` | `# (an even number of intervals); if there are fewer it falls back to the kalana_trapiz.` | `# (even intervals); for usable even n >= 4 drops the final sample; n < 3 uses kalana_trapiz.` |
| `lib/khand.smlib:6` | `# string.smlib) because the compiler has a fixed AST ceiling.` | `# lib/varna.smlib) because the compiler has a fixed AST ceiling.` |
| `lib/khand.smlib:20` | `# larger buffer, with NO terminator at the slice end. Every strb_*` | `# larger buffer, with NO terminator at the slice end. Explicit-length khand_*` |
| `lib/mala.smlib:1` | `# lib/mala.smlib — Sutram standard library: dynamic arrays` | `# lib/mala.smlib — Sutram standard library: fixed-size raw qword-array helpers` |
| `lib/mala.smlib:6` | `# allocates. Safe variants take the element count and return 0 / do` | `# allocates without tracking length. Count-checked variants take caller's n;` |
| `lib/mala.smlib:7` | `# nothing on out-of-bounds access.` | `# n must not exceed allocated cells. Raw variants do no allocation bounds check.` |
| `lib/nighantu.smlib:5` | `# KEY REPRESENTATION: byte strings (the R10 strb_* surface), NOT` | `# KEY REPRESENTATION: byte strings (the current khand_* byte surface), NOT` |
| `lib/nighantu.smlib:328` | `# the return is less than nighantu_maap(src) — check nighantu_maap(dst)` | `# the return is less than nighantu_maap(src), the merge is incomplete.` |
| `lib/nighantu.smlib:329` | `# afterwards to detect a partial merge. (nighantu_grah's -1 sentinel is not a hazard here: the keys come` | `# Destination map size alone cannot detect this: updates need not change it.` |
| `lib/nighantu.smlib:330` | `# from nighantu_kunjika_ashtak, so every key is known to exist.)` | `# Keys come from nighantu_kunjika_ashtak, so each is known to exist (no -1 ambiguity).` |
| `lib/phal.smlib:7` | `# directly (result_checked_*), and phal_se_siddhi bridges the older` | `# directly (phal_janchit_*), and phal_se_siddhi bridges the older` |
| `lib/roop.smlib:309` | `# roop_pad_madhya(src, sn, width, padbyte, out) — npad on BOTH sides;` | `# roop_pad_madhya(src, sn, width, padbyte, out) — pad both sides to width;` |
| `lib/roop.smlib:310` | `# when width-sn is odd, the extra npad byte goes RIGHT.` | `# when width-sn is odd, the extra padding byte goes RIGHT.` |
| `lib/samanvaya.smlib:134` | `# dot product of two flat vectors (row i of a with column j of b) — convenience` | `# dot product of flat vectors u and v over min(kosh_len(u), kosh_len(v)) entries.` |
| `lib/sangrah.smlib:10` | `# ELEMENTS ARE BYTE STRINGS — the same choice as \`map.smlib\`'s keys:` | `# ELEMENTS ARE BYTE STRINGS — the same choice as \`lib/nighantu.smlib\` keys:` |
| `lib/suchi.smlib:220` | `# the min loop by hand or called sort.smlib's laghu on l[2] — which` | `# the min loop by hand or called shreni.smlib's laghu on l[2] — which` |
| `lib/suchi.smlib:245` | `# the sum loop by hand or called sort.smlib's yog on l[2].` | `# the sum loop by hand or called shreni.smlib's yog on l[2].` |
| `lib/suchi.smlib:252` | `# sort.smlib's gan on l[2].` | `# shreni.smlib's gan on l[2].` |
| `lib/suchi.smlib:258` | `# form of sort.smlib's anwesh_sarak; before, the caller called` | `# form of shreni.smlib's anwesh_sarak; before, the caller called` |
| `lib/suchi.smlib:266` | `# List-shaped form of sort.smlib's asti_sorted.` | `# List-shaped form of shreni.smlib's asti_sorted.` |
| `lib/suchi.smlib:272` | `# (WS2, R23). List-shaped form of sort.smlib's dwi_anwesh. The` | `# (WS2, R23). List-shaped form of shreni.smlib's dwi_anwesh. The` |
| `lib/vakyank.smlib:81` | `# varna_tak_ank(buf, n) — parse first n character codes of mala buf as a` | `# varna_tak_ank(buf, n, ok) — parse first n character codes of mala buf as a` |
| `lib/vakyank.smlib:138` | `# ank_tak_aadhar_varna(n, base, out) — write n in \`base\` (2/8/10/16) into out` | `# ank_tak_aadhar_varna(n, base, out) — write n in any base 2..36 into out` |
| `lib/vakyank.smlib:139` | `# as character codes (0-9, a-f). Returns count. No util_chinha handling; n >= 0.` | `# as character codes (0-9, a-z). Returns count. No util_chinha handling; n >= 0.` |
| `lib/varna.smlib:13` | `# slice has no terminator at its end. Use the explicit-length strb_*` | `# slice has no terminator at its end. Use the explicit-length khand_*` |

## Application discipline

- These are **35 one-line substitutions**. They amend documented callable signatures, buffer extents, return/representation descriptions and known obsolete file names. They do not rename a public declaration, add a library function or alter compiler behavior.
- Because `docs/sutram-stdlib.html` is generated from the source-comment lines, update the **authorized `lib/` comments first**, then run `tools/gen_stdlib_ref.py` and `tools/check_doc_signatures.py` using an exact pinned source tree. Do not hand-edit generated HTML.
- The previous R115 census found **100 empty per-function description cells**; those have **no old description line to replace**. The complete source and HTML location register is `ChatGPT-to-Sarvam/ROUND-115-ALL-305-DESCRIPTIONS.tsv`. A new descriptive line for any of the 100 needs source semantics and output/precondition review. They are **NOT INCLUDED in this exact-replacement table**; do not silently mark them fixed.
- For the two `brihat_shesh` rows, parameter names in comments now exactly match declarations. In `vakyank`, the old `varna_tak_ank(buf,n)` prose lacked the required `ok` parameter and is now explicitly corrected.
- The existing `lib/ganita.smlib` checked `ok` output-family requires a caller-owned writable cell. A dedicated cross-family header explaining this remains for the library owner to author; the two `out[0]/out[1]` corrections above cover confirmed two-cell output functions.
- Do not replace intentionally historical comments, negative-test fixtures, language packs, or files in `backups/`.

## Status

**PASS — 35/35 old lines found exactly once on pinned source; 0 ambiguous matches, 0 protected writes.**
**NOT RUN - no toolchain** — native Sutram execution/gates/Windows and regenerated current HTML.
**NOT APPLIED** — only proposals in `ChatGPT-to-Sarvam/`, pending authorized author and Sarvam integration.
