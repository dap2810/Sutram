# Sutram ROUND-113 WS2 — standard-library description-layer audit

**Read pin** main `1ccec720dccc53ae8ed344e4f58f87fba727682a`, `docs/sutram-stdlib.html` blob `212d6c97a31455361607b4b797d504b3061f05d9`. Read: the generated sections `ganita`, `mala`, plus `kalana`, `samanvaya`, `khand`, `sadhan`, `nighantu`, `roop`; source `lib/ganita.smlib`, `lib/mala.smlib`, `lib/kalana.smlib`, `lib/samanvaya.smlib` and related tests. `vartani` and `kosh` have **no individual module sections** in the generated 24-module page; the latter is a built-in array type, not `lib/kosh.smlib`. The former is a builtin/string-surface name, not `lib/vartani.smlib`. Do not invent an HTML section.

## Reader-impact findings

**P1 — Incorrect API meaning: `samanvaya.sadish_yoga`.**
- HTML section `samanvaya` describes a dot product of "row i of a with column j of b".
- `lib/samanvaya.smlib:135-144` takes **only two vectors `u,v`**, calculates `n=min(kosh_len(u),kosh_len(v))`, and sums `u[i]*v[i]`. There are no row/column indices or matrix strides. **FAIL: materially misleading**, can prompt a reader to use wrong shape/values. Correct description: "dot product of two flat float vectors over the shorter logical length"; note behavior on unequal lengths.

**P1 — Missing caller-extent contract in a likely beginner entry point: `ganita.chakravala` and `ganita.samasa`.**
- HTML lists writes to `out[0]`, `out[1]`, but does not explicitly say `out` must address **two allocated 8-byte cells**. Source `lib/ganita.smlib:76-84,151-152,160-167` writes both. These are raw pointer parameters; a typed `kosh` bound check is no substitute.
- The `ganita_janchit_*` HTML says it writes `ok[0]` (correct), but provide a prominent example allocating one qword as in `tests/stdlib/ganita_checked.sm`. Do not manufacture default allocation.

**P1 — Misleading category / incomplete contracts: `mala`.**
- HTML section calls `lib/mala.smlib` "dynamic arrays", but its own header states `mala_nava` *only allocates* and **caller tracks length**; `lib/mala.smlib:9-16` allocates a fixed raw qword buffer. True growable `kosh` is a language builtin. Distinguish raw fixed buffer helpers from auto-growing typed `kosh`.
- The HTML's eight per-function description cells are **empty**. Critical contrasts are undiscoverable from the function rows: raw `mala_grah`/`mala_sangrah` do not validate extent, while `mala_grah_surakshit` returns zero on invalid access (ambiguous with a stored zero) and `mala_sangrah_surakshit` returns 1 on success/0 on rejection. Source `lib/mala.smlib:20-87`. The safe variants validate the *supplied n*, not actual allocation identity. This is **incomplete/ambiguous prose**, not a name/arity drift.
- Correct in source, leave code alone. Recommend revised source-comment descriptions by authorized `lib/` writer followed by exact regeneration.

**P2 — Incomplete sampling rule: `kalana.simpson`.**
- HTML says Simpson requires an odd number of points and if fewer "falls back to the kalana_trapiz." Source `lib/kalana.smlib:33-40` **drops the final sample when the common length is even**, and falls back only for fewer than 3. Callers with 4 samples could assume all were used. Add explicit truncation behavior and truncated-length rule.
- `kalana.bahu_mula` correctly documents that `ok` must already have one element, and `tests/stdlib/kalana_bahu_mula.sm` follows that contract. **PASS (do not report as a new docs defect).**

**Other sampled prose:** `khand` warns of byte-packed versus qword-cell representations, `nighantu` warns of signed sentinel and exact buffer format, `sadhan` now correctly says `Usage: yoj sadhan` after Muse R36. No further *verified* misleading instruction in the selected snippets; not a complete behavioral proof for all 305.

## Guard boundary

`tools/check_doc_signatures.py` only compares module, function name, arity and parameter-label/kinds. These description defects pass it. The generator copies source comments; fixing HTML by hand is temporary and will be overwritten. Send source-comment fixes to authorized Muse/Claude `lib/` scope and regenerate with receipts.

**Status:** prose/source comparison FAIL (specific P1/P2 findings); module/sample scope PASS (read); descriptions for all 305 functions NOT AUDITED; native behavior NOT RUN - no toolchain.