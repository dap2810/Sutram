# R68 audit — lib/suchi.smlib, lib/ganita.smlib, lib/shreni.smlib, lib/samanvaya.smlib

Read-only audit. Census: 39 prakriya, 95 write sites. Every body was read in full
(lib/suchi.smlib 1-530, lib/ganita.smlib 1-577, lib/shreni.smlib 1-230,
lib/samanvaya.smlib 1-165). Nothing under /home/claude/sutram was modified.

## Preliminary facts established from the repo (used by several rows)

1. **Container data buffers (`d = l[2]` / `d = q[2]`, census origin OTHER).** The capacity
   field and the allocation are set together, in the constructor and in every grow path:
   - `suchi_srij` (suchi.smlib:53-61): `sz = c * 8`, `d = nirmmita(sz)`, `l[1] = c`, `l[2] = d`
     → data has exactly `l[1]` cells.
   - `suchi_vardh` (suchi.smlib:74-82): `ncap = lst[1] * 2`, `nd = nirmmita(ncap * 8)`,
     `lst[2] = nd`, `lst[1] = ncap` → still exactly `l[1]` cells.
   - `avali_srij` (suchi.smlib:388-397): same pattern, `q[1] = c`, `q[2] = d`.
   - `avali_pravesh` grow branch (suchi.smlib:416-427): `ncap = qu[1] * 2`,
     `nd = nirmmita(ncap * 8)`, `qu[2] = nd`, `qu[1] = ncap`.
   So the invariant **cells(l[2]) == l[1]** (resp. **cells(q[2]) == q[1]**) holds after every
   public operation; the rows below check each write index against `l[1]`/`q[1]`.
   The length invariant **0 <= l[0] <= l[1]** is maintained: every append/insert grows first
   when `l[0] == l[1]` (suchi.smlib:90, 136, 413) and `suchi_vardh`/grow fail leaves the
   structure unchanged (suchi.smlib:76, 418).
2. **Handles (PARAM `l` / `q`).** Module header suchi.smlib:10-16 states the layouts:
   list/stack handle = `[len, cap, data_ptr]` (3 cells, allocated `nirmmita(3 * 8)` at :55),
   queue handle = `[len, cap, data_ptr, head]` (4 cells, `nirmmita(4 * 8)` at :390).
   All header writes below are at index <= 2 (list) or <= 3 (queue).
3. **`ok` cells.** ganita.smlib:189-190: "reads ok[0] (the varna_tak_ank ok-pattern: ok is a
   1-cell mala)". suchi.smlib:32-34: "set ok[0] (a 1-cell mala) to 1 on success, 0 when
   empty". Every ok-writing contract comment says "ok[0] 1, or 0 ...". Capacity 1 cell is
   therefore stated, and every body writes only index 0.
4. **`kosh dasham out` parameters (samanvaya, census origin OTHER).** These are not raw
   blocks. The compiler marks a `kosh`/`kosh dasham` parameter as a kosh variable
   (src/sutram_compiler.asm:12336-12354, `mark_kosh_var` + `mark_kosh_param_var`), and every
   index store on a kosh variable emits a runtime bounds check against the logical length at
   `[ptr-16]` (src/sutram_compiler.asm:13272-13273 "T8/T18 array store with generated bounds
   check", 13351-13369, 13393-13395 `emit_array_bounds_check`); index loads likewise
   (15153-15168). A call site may only pass a named `kosh dasham` variable to such a
   parameter (20537-20555; otherwise "Sutram Error: kosh tark: tatv prakar bhinn"). So an
   out-of-range `out[...]` in samanvaya traps with a diagnostic instead of corrupting a
   neighbouring block; the module header (samanvaya.smlib:9-10) states the same.

---

## Part A — every (prakriya, buffer)

Columns: `module | prakriya | buffer | unit | MAX INDEX WRITTEN (worst case; max READ of a caller buffer if relevant) | CAPACITY STATED / own size | VERDICT | note`

### ganita.smlib

| # | module | prakriya | buffer | unit | max index written | capacity stated / own size | verdict | note |
|---|---|---|---|---|---|---|---|---|
| 1 | ganita | chakravala(out, n) :77 | out (PARAM) | cell | 1 (out[0], out[1] at :84-85 and :152-153; every other path returns 0 without writing) | ":76 caller must supply at least 2 writable qword cells" | WITHIN | constant capacity 2 → Part B done |
| 2 | ganita | samasa(out, a, b, c, d, n) :161 | out (PARAM) | cell | 1 (:167-168) | ":160 requires 2 writable qword cells" | WITHIN | constant capacity 2 → Part B done |
| 3 | ganita | ganita_janchit_yuj :217 | ok (PARAM, via okp) | cell | 0 (:225, :232, :237) | ":215 ok[0] 1, or 0"; header :189-190 "ok is a 1-cell mala" | WITHIN | |
| 4 | ganita | ganita_janchit_nyun :243 | ok | cell | 0 (:251, :258, :263) | ":241 ok[0]"; :189-190 1-cell | WITHIN | |
| 5 | ganita | ganita_janchit_gun :270 | ok | cell | 0 (:277, :281, :286, :292, :298, :301) | ":267 ok[0]"; :189-190 1-cell | WITHIN | |
| 6 | ganita | ganita_janchit_bhaj :307 | ok | cell | 0 (:313, :318, :322) | ":305 ok[0]"; 1-cell | WITHIN | |
| 7 | ganita | ganita_janchit_shesh :328 | ok | cell | 0 (:334, :339, :343) | ":326 ok[0]"; 1-cell | WITHIN | |
| 8 | ganita | ganita_janchit_ghat :419 | ok | cell | 0 (:426, :434; also passed through to ganita_janchit_gun at :430 which writes index 0 only) | ":414 ok[0]"; 1-cell | WITHIN | |
| 9 | ganita | ganita_janchit_kramgun :442 | ok | cell | 0 (:448, :456; pass-through at :452) | ":439 ok[0]"; 1-cell | WITHIN | |
| 10 | ganita | ganita_janchit_nirapeksh :534 | ok | cell | 0 (:539, :542) | ":531 ok[0]"; 1-cell | WITHIN | |

### samanvaya.smlib (all `kosh dasham out`; compiler bounds-checked, see fact 4)

| # | module | prakriya | buffer | unit | max index written | capacity stated | verdict | note |
|---|---|---|---|---|---|---|---|---|
| 11 | samanvaya | ekaka_matrika(n, out) :32 | out (OTHER: kosh dasham param) | cell (binary64) | `i*n + j` with 0<=i<n, 0<=j<n → `n*n - 1` (:38/:40); n<=0 writes nothing | ":31 out must hold n*n elements" | WITHIN | runtime-checked against kosh_len(out); a short kosh traps, does not corrupt |
| 12 | samanvaya | vivartana(a, m, n, out) :50 | out | cell | `j*m + i`, 0<=i<m, 0<=j<n → `n*m - 1` (:55); reads `a[i*n+j]` max `m*n - 1` (also checked) | ":49 out must hold n*m elements" | WITHIN | |
| 13 | samanvaya | matrika_yoga(a, b, m, n, out) :66 | out | cell | `k < m*n` → `m*n - 1` (:72); pre-checked by samanvaya_akar_ayogya against kosh_len(a), kosh_len(b), kosh_len(out) (:68-70) so m*n is never formed unless it fits | ":63 out must hold m*n elements"; R37 returns -1 otherwise | WITHIN | reads a[k], b[k] <= m*n-1, also pre-checked |
| 14 | samanvaya | skalar(a, c, m, n, out) :79 | out | cell | `m*n - 1` (:84); pre-checked :81-82 | ":78 out must hold m*n elements"; R37 -1 | WITHIN | |
| 15 | samanvaya | matrika_gunana(a, b, m, n, p, out) :91 | out | cell | `i*p + j`, i<m, j<p → `m*p - 1` (:102); reads a up to `m*n - 1`, b up to `n*p - 1` | ":90 out must hold m*p elements" | WITHIN | no R37 pre-check here, but every index is compiler-checked |

### shreni.smlib

| # | module | prakriya | buffer | unit | max index written | capacity stated / own size | verdict | note |
|---|---|---|---|---|---|---|---|---|
| 16 | shreni | vinimay(a, i, j) :6 | a (PARAM) | cell | `max(i, j)` (:8-9), also reads a[i], a[j] (:7-8); **indices are caller-chosen, no count parameter, no check** | none (vinimay has no contract comment; module header :4-5 "Operates on mala integer arrays, in place" gives no capacity) | UNDOC | body needs `max(i, j) + 1` cells with `i, j >= 0`; a negative i or j would also be NEG. Both lib callers stay in range (Part B). |
| 17 | shreni | shankh_shreni(a, n) :120 | a (PARAM) | cell | `j` starts at `i` (gap <= i <= n-1) and only decreases by gap while `j >= gap` → max written `n - 1` (:131, :140), min 0; reads a[i] <= n-1, a[j-gap] >= 0 | ":119 sorts a[0..n-1]" → n cells | WITHIN | n <= 1: gap = n/2 <= 0, no iteration |
| 18 | shreni | nivesh_shreni(a, n) :148 | a (PARAM) | cell | `arr[j + 1]` with `-1 <= j <= i-1`, `1 <= i <= len-1` → max `n - 1` (:161, :168), min 0 (j = -1 → index 0); reads arr[j] only when j >= 0 (:157-160) | ":147 sorts a[0..n-1]" → n cells | WITHIN | |
| 19 | shreni | mil_shreni_punar(a, tmp, lo, hi) :174 | tmp (PARAM, internal; from mil_shreni it is OWN `nirmmita(n * 8)`) | cell | `k` runs from lo, incremented once per element of a[lo:hi] → max `hi - 1` (:193, :199, :204, :207); with (lo, hi) = (0, n) → `n - 1`; recursion only narrows [lo, hi) | own n cells (shreni.smlib:226) | WITHIN | private helper, only caller is mil_shreni :228 |
| 20 | shreni | mil_shreni_punar(a, tmp, lo, hi) :174 | a (PARAM) | cell | `a[c]`, lo <= c < hi → `hi - 1` = `n - 1` (:216); reads a[i] < mid, a[j] < hi | mil_shreni :222 "mil_shreni(a, n) — merge sort" — n is the element count (the comment does not spell "a[0..n-1]" the way :119/:147 do, but (a, n) is the module-wide convention) | WITHIN | n cells needed; n < 2 returns before any write (:224) |
| 21 | shreni | mil_shreni(a, n) :223 | tmp (OWN `nirmmita(n * 8)` :226) | cell | written only inside mil_shreni_punar: max `n - 1` | own n cells; n > 2^60-1 rejected at :225 so n*8 cannot wrap; nirmmita 0 → -1 at :227 | WITHIN | |

### suchi.smlib

| # | module | prakriya | buffer | unit | max index written | capacity stated / own size | verdict | note |
|---|---|---|---|---|---|---|---|---|
| 22 | suchi | suchi_srij(cap) :46 | l (OWN `nirmmita(3 * 8)` :55) | cell | 2 (:59-61) | own 3 cells | WITHIN | d = nirmmita(c*8) is allocated but not written here; c clamped >= 1 (:51), c*8 wrap rejected (:52-54) |
| 23 | suchi | suchi_vardh(l) :67 | nd (OWN `nirmmita(ncap * 8)`, ncap = 2*cap :74-75) | cell | `i < lst[0]` → `len - 1` <= `cap - 1` < 2*cap (:78); reads old[i] <= len-1 <= cap-1 (old has cap cells, fact 1) | own 2*cap cells; cap*16 wrap rejected :73 | WITHIN | |
| 24 | suchi | suchi_vardh(l) :67 | l handle (PARAM) | cell | 2 (:81 lst[2], :82 lst[1]) | header :10-12 list handle = 3 cells | WITHIN | |
| 25 | suchi | suchi_khip(l, v) :87 | l handle (PARAM) | cell | 0 (:95) | 3-cell handle | WITHIN | |
| 26 | suchi | suchi_khip(l, v) :87 | d = lst[2] (OTHER) | cell | `d[lst[0]]` = `len` (:94); when len == cap, suchi_vardh runs first (:90-91) so len <= cap-1 at the write | `l[1]` cells (fact 1) | WITHIN | |
| 27 | suchi | suchi_sangrah(l, i, v) :110 | d (OTHER) | cell | `idx`, 0 <= idx <= len-1 (:114-115) → `len - 1` (:117) | `l[1]` cells, len <= cap | WITHIN | |
| 28 | suchi | suchi_nivesh(l, i, v) :128 | d (OTHER) | cell | shift loop `d[k] = d[k-1]` for k from `lst[0]` down to idx+1 → max written `len` (old len) (:142), reads d[k-1] <= len-1; `d[idx]` <= len (:145); grow first when len == cap (:136-137) so len <= cap-1 at the writes | `l[1]` cells | WITHIN | idx range checked 0 <= idx <= len (:134-135) |
| 29 | suchi | suchi_nivesh(l, i, v) :128 | l handle (PARAM) | cell | 0 (:146) | 3-cell handle | WITHIN | |
| 30 | suchi | suchi_apanay(l, i) :152 | d (OTHER) | cell | `d[k]` for idx <= k < len-1 → max `len - 2` (:162); reads d[k+1] <= len-1 | `l[1]` cells | WITHIN | idx checked 0 <= idx < len (:157-158), so len >= 1 before `lst[0] - 1` (:165) |
| 31 | suchi | suchi_apanay(l, i) :152 | l handle (PARAM) | cell | 0 (:165) | 3-cell handle | WITHIN | |
| 32 | suchi | suchi_vinimay(l, i, j) :173 | d (OTHER) | cell | `max(a, b)` <= `len - 1` (:185-186) after checks :179-182 | `l[1]` cells | WITHIN | |
| 33 | suchi | suchi_viparyay(l) :193 | d (OTHER) | cell | `j` starts at `len - 1`, `i` at 0, loop while i < j → max `len - 1`, min 0 (:201-202); len = 0 → j = -1, loop body never runs | `l[1]` cells | WITHIN | |
| 34 | suchi | suchi_laghu(l, ok) :223 | ok (PARAM) | cell | 0 (:225, :228) | ":218 ok[0] 1, or 0"; header :33 "ok[0] (a 1-cell mala)" | WITHIN | reads l[2] via laghu(l[2], l[0]) — n = len, guarded n <= 0 in laghu |
| 35 | suchi | suchi_adhik(l, ok) :234 | ok (PARAM) | cell | 0 (:236, :239) | ":232 ok[0]"; :33 1-cell | WITHIN | |
| 36 | suchi | suchi_rikta(l) :285 | d (OTHER) | cell | `i < l[1]` → `cap - 1` (:289) | `l[1]` cells (fact 1) | WITHIN | zeroes the whole capacity, exactly the allocation |
| 37 | suchi | suchi_rikta(l) :285 | l handle (PARAM) | cell | 0 (:292) | 3-cell handle | WITHIN | |
| 38 | suchi | chay_apanay(l, ok) :331 | ok (PARAM, via okp) | cell | 0 (:337, :343) | ":329 sets ok[0]"; :33 1-cell | WITHIN | reads d[len-1] after len >= 1 check (:336, :341-342) |
| 39 | suchi | chay_apanay(l, ok) :331 | l handle (PARAM) | cell | 0 (:341) | 3-cell handle | WITHIN | |
| 40 | suchi | chay_avalok(l, ok) :348 | ok (PARAM) | cell | 0 (:353, :357) | ":347 ok[0] 1/0"; 1-cell | WITHIN | reads d[len-1], len >= 1 (:352) |
| 41 | suchi | avali_srij(cap) :381 | q (OWN `nirmmita(4 * 8)` :390) | cell | 3 (:394-397) | own 4 cells | WITHIN | |
| 42 | suchi | avali_pravesh(q, v) :404 | nd (OWN `nirmmita(ncap * 8)`, ncap = 2*cap :416-417) | cell | `k < qu[0]` with len == cap → `cap - 1` < 2*cap (:422); reads old[(head+k) % cap] <= cap-1 | own 2*cap cells; wrap rejected :415 | WITHIN | |
| 43 | suchi | avali_pravesh(q, v) :404 | q handle (PARAM) | cell | 3 (:425 qu[2], :426 qu[1], :427 qu[3], :432 qu[0]) | header :14 queue handle = 4 cells | WITHIN | |
| 44 | suchi | avali_pravesh(q, v) :404 | d = qu[2] (OTHER) | cell | `tail = (head + len) % cap` → <= `cap - 1` (:430-431); after growth head = 0, len = old cap, cap = 2*old cap → tail = old cap < new cap | `q[1]` cells (fact 1) | WITHIN | |
| 45 | suchi | avali_nishkas(q, ok) :438 | ok (PARAM) | cell | 0 (:444, :451) | ":436 sets ok[0]"; :33 1-cell | WITHIN | reads d[head], head < cap by :449 invariant |
| 46 | suchi | avali_nishkas(q, ok) :438 | q handle (PARAM) | cell | 3 (:449 qu[3], :450 qu[0]) | 4-cell handle | WITHIN | |
| 47 | suchi | avali_avalok(q, ok) :456 | ok (PARAM) | cell | 0 (:461, :465) | ":455 ok[0] 1/0"; 1-cell | WITHIN | |
| 48 | suchi | avali_tak_mala(q, out) :475 | out (PARAM) | cell | `k < qu[0]` → `len - 1` (:480); reads d[(head+k) % cap] <= cap-1 | ":471 Caller allocates cap cells" (cap = q[1] >= len) | WITHIN | body needs only `avali_maap(q)` cells; the stated `cap` is an over-approximation. There is no `avali_cap`-style accessor, so a caller must remember the srij cap or use avali_maap(q). |
| 49 | suchi | avali_rikta(q) :508 | d = q[2] (OTHER) | cell | `i < q[1]` → `cap - 1` (:512) | `q[1]` cells (fact 1) | WITHIN | |
| 50 | suchi | avali_rikta(q) :508 | q handle (PARAM) | cell | 3 (:515 q[0], :516 q[3]) | 4-cell handle | WITHIN | |

Reads of caller buffers past the given count: none found in these four modules. Every read
index is bounded by the same count the write is (rows 12-15, 17-20, 23, 26-33, 38, 40, 42,
44-45, 48). No terminator convention exists in these modules (all element data is qword
cells; no byte strings are written), so no TERMINATOR rows.

---

## Part B — callers

Required by the brief: PARAM buffers whose verdict is not WITHIN-with-stated-capacity
(`vinimay`), plus functions whose stated capacity is a constant (`chakravala` and `samasa`:
2 cells; the ok-channel family: 1 cell). Also included as a courtesy: `avali_tak_mala`,
whose stated capacity ("cap cells") is larger than what the body needs.

Search scope: `examples/*.sm`, `tests/**/*.sm` minus `tests/negative/`, `lib/*.smlib`,
embedded programs in `tools/proof_props.py` and `tools/proof_lib.py` (proof_lib.py has no
call to any of these). Definitions and contract-comment mentions in lib are excluded.

### B.1 vinimay(a, i, j) — UNDOC; needs max(i, j) + 1 cells

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| lib/shreni.smlib:19 | `vinimay(a, j, j + 1)` in budbud_shreni(a, n), inside `yavat (j < n - 1 - i)`, i >= 0 | a passed through from budbud_shreni's caller (contract :12 "sorts a[0..n-1]" → n cells) | `j + 2` <= `n` | OK (within a[0..n-1]) |
| lib/shreni.smlib:32 | `vinimay(a, i, j)` in viparyay_mala(a, n), i from 0, j from n-1, while i < j | a passed through (contract :27 "reverses a[0..n-1]" → n cells) | `n` | OK |
| tests/stdlib/sort_swap.sm:7 | `vinimay(a, 0, 2)` | `mala a[3]` (tests/stdlib/sort_swap.sm:3, compiler bounds-checked) | 3 cells | OK |

### B.2 chakravala(out, n) / samasa(out, ...) — constant capacity 2 cells

| file:line | call | buffer allocation | needed | result |
|---|---|---|---|---|
| examples/91_indian_number_theory.sm:9 | `chakravala(r, 13)` | `mala r[2]` (:8) | 2 | OK |
| examples/91_indian_number_theory.sm:13 | `chakravala(r, 61)` | `mala r[2]` (:8) | 2 | OK |
| examples/91_indian_number_theory.sm:17 | `samasa(r, 8, 1, 8, 1, 61)` | `mala r[2]` (:8) | 2 | OK |
| tests/stdlib/ganita_samasa.sm:4 | `samasa(out, 1, 1, 2, 1, 2)` | `mala out[2]` (:3) | 2 | OK |
| tests/stdlib/chakravala29.sm:4 | `chakravala(out, 4)` | `nirmmita(8 * 8)` = 8 cells (:3) | 2 | OK |
| tests/stdlib/chakravala29.sm:11 | `chakravala(out, 2)` | same 8 cells | 2 | OK |
| tests/stdlib/chakravala29.sm:18 | `chakravala(out, 61)` | same 8 cells | 2 | OK |
| tests/stdlib/chakravala29.sm:25 | `chakravala(out, 9223372036854775807)` | same 8 cells | 2 | OK |
| tests/stdlib/numeric29.sm:9 | `samasa(out, 1099511627776, 0, 1099511627776, 0, 0)` | `nirmmita(8 * 8)` = 8 cells (:8) | 2 | OK |
| tests/stdlib/ganita_chakravala.sm:4 | `chakravala(out, 2)` | `mala out[2]` (:3) | 2 | OK |
| tests/stdlib/ganita_chakravala.sm:9 | `chakravala(out, 3)` | `mala out[2]` (:3) | 2 | OK |
| tests/stdlib/r8_chakravala_sweep.sm:19 | `chakravala(out, c[0])` in a loop | `nirmmita(2 * 8)` = 2 cells (:11) | 2 | OK (exactly the constant) |
| tools/proof_props.py:4260 (prop_numeric29) | `samasa(out, 1099511627776, 0, 1099511627776, 0, 0)` | `nirmmita(8 * 8)` (:4244) | 2 | OK |
| tools/proof_props.py:4291 | `chakravala(out, 4)` | same (:4244) | 2 | OK |
| tools/proof_props.py:4298 | `chakravala(out, {n})` for n in 2, 3, 5, 13, 61 (5 generated calls) | same (:4244) | 2 | OK |
| tools/proof_props.py:4306 | `chakravala(out, 9223372036854775807)` | same (:4244) | 2 | OK |
| tools/proof_props.py:4659 (chakravala limit program) | `chakravala(out, 9223372030926249006)` | `nirmmita(8 * 8)` (:4658) | 2 | OK |

### B.3 ok-channel family — constant capacity 1 cell

Functions: ganita_janchit_{yuj,nyun,gun,bhaj,shesh,ghat,kramgun,nirapeksh}, suchi_laghu,
suchi_adhik, chay_apanay, chay_avalok, avali_nishkas, avali_avalok. Every call site in scope
was located (138 call lines); the ok argument's allocation per file:

| file:line(s) | calls | ok allocation | needed | result |
|---|---|---|---|---|
| lib/ganita.smlib:430 | `ganita_janchit_gun(r, base, okp)` inside ganita_janchit_ghat | okp = ok passed through from ghat's caller (1 cell by ghat's own contract) | 1 | OK (pass-through) |
| lib/ganita.smlib:452 | `ganita_janchit_gun(r, i, okp)` inside ganita_janchit_kramgun | pass-through | 1 | OK |
| lib/phal.smlib:90, 105, 120, 135, 150, 163, 176, 189 | `ganita_janchit_*(…, o)` with `o = out` | out is a phal Result, lib/phal.smlib:4 "A Result is a 2-cell mala supplied by the caller: [ok, value]" | 1 | OK (2 >= 1; phal's callers are another module's audit) |
| tests/stdlib/safety24.sm:21, 25, 29 | ganita_janchit_nirapeksh(…, ok) | `nirmmita(8)` (:3) = 1 cell | 1 | OK |
| tests/stdlib/gaps19.sm:62, 66, 70, 74, 78, 82 | ganita_janchit_ghat(…, ok) | `nirmmita(8)` (:6) | 1 | OK |
| tests/stdlib/gaps20.sm:4, 8, 12, 16, 20 | ganita_janchit_kramgun(…, ok) | `nirmmita(8)` (:3) | 1 | OK |
| tests/stdlib/r9_guard_cells2.sm:35 | avali_nishkas(qq, ok) | `nirmmita(8)` (:29) | 1 | OK |
| tests/stdlib/ganita_checked.sm:10, 15, 20, 25, 30, 35, 41, 47, 53, 58, 63, 68 | ganita_janchit_{yuj,nyun,gun,bhaj,shesh} | `nirmmita(8)` (:5) | 1 | OK |
| tests/stdlib/list_queue.sm:11, 21, 26, 28, 30, 35, 39 | avali_nishkas / avali_avalok | `nirmmita(8)` (:4) | 1 | OK |
| tests/stdlib/r8_list_model.sm:40, 44 | avali_nishkas / avali_avalok | `nirmmita(8)` (:11) | 1 | OK |
| tests/stdlib/containers_clear.sm:39, 43, 51 | avali_nishkas | `nirmmita(8)` (:4) | 1 | OK |
| tests/stdlib/r48_srij_fill.sm:30 | avali_nishkas | `nirmmita(8)` (:8) | 1 | OK |
| tests/stdlib/containers23.sm:26 | `avali_nishkas(q, nirmmita(8))` | inline `nirmmita(8)` | 1 | OK |
| tests/stdlib/safety25.sm:6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62, 66, 70, 74 | all eight ganita_janchit_* | `nirmmita(8)` (:3) | 1 | OK |
| tests/stdlib/containers21.sm:17, 21, 37, 41, 52 | suchi_laghu / suchi_adhik / avali_nishkas | `nirmmita(8)` (:4) | 1 | OK |
| tests/stdlib/list_stack.sm:14, 18, 21, 23, 25, 30, 34 | chay_avalok / chay_apanay | `nirmmita(8)` (:4) | 1 | OK |
| tools/proof_props.py:1761, 1774, 1787, 1792 | chay_avalok / chay_apanay | `vitti ok = nirmmita(8)` (:1755) | 1 | OK |
| tools/proof_props.py:1821, 1834, 1843, 1852, 1857, 1876 | avali_nishkas / avali_avalok | :1812 `nirmmita(8)` | 1 | OK |
| tools/proof_props.py:2140 | ganita_janchit_gun | :2135 `nirmmita(8)` | 1 | OK |
| tools/proof_props.py:2174, 2183 | ganita_janchit_bhaj / shesh | :2166 `nirmmita(8)` | 1 | OK |
| tools/proof_props.py:2371, 2377, 2394 | avali_nishkas | :2324 `nirmmita(8)` | 1 | OK |
| tools/proof_props.py:2494 | ganita_janchit_ghat | :2439 `nirmmita(8)` | 1 | OK |
| tools/proof_props.py:2708 | ganita_janchit_kramgun | :2700 `nirmmita(8)` | 1 | OK |
| tools/proof_props.py:2754, 2762, 2790 | suchi_laghu / suchi_adhik / avali_nishkas | :2746 `nirmmita(8)` | 1 | OK |
| tools/proof_props.py:2893 | `avali_nishkas(q, nirmmita(8))` | inline | 1 | OK |
| tools/proof_props.py:3090 | avali_nishkas | :3062 `nirmmita(8)` | 1 | OK |
| tools/proof_props.py:3246 | ganita_janchit_nirapeksh | :3224 `nirmmita(8)` | 1 | OK |
| tools/proof_props.py:3355, 3358, 3393 (+ check_checked-generated calls in parts a-d) | ganita_janchit_* | each part starts with `nirmmita(8)` (:3300) | 1 | OK |
| tools/proof_props.py:3507, 3514, 3533, 3556, 3581 (+ agree_binop-generated calls) | ganita_janchit_* | each part starts with `nirmmita(8)` (:3453) | 1 | OK |
| tools/proof_props.py:3837, 3843, 3855, 3857, 3859, 3896, 3912 | ganita_janchit_yuj / nyun / gun | :3799, :3804, :3809 `nirmmita(8)` (one per part) | 1 | OK |
| tools/proof_props.py:3969-3971, 3980, 3987, 3993, 3999, 4006, 4012 | chay_apanay, chay_avalok, avali_nishkas, avali_avalok, suchi_laghu, suchi_adhik | :3960 `nirmmita(8)` | 1 | OK |

### B.4 avali_tak_mala(q, out) — stated "cap cells", body needs avali_maap(q) cells (courtesy check)

| file:line | call | buffer allocation | needed (len) / stated (cap) | result |
|---|---|---|---|---|
| tests/stdlib/r10_roop_suchi_edges.sm:46 | `avali_tak_mala(q, o)` | `o = nirmmita(4 * 8)` (:44), q = avali_srij(4) with 2 pushes | 2 / 4 | OK (the test deliberately checks o[2] survives: writes exactly len cells) |
| tests/stdlib/r8_list_model.sm:52 | `avali_tak_mala(q, out)` | `nirmmita((avali_maap(q) + 1) * 8)` (:51) | len / cap | OK for the body (len+1 >= len); may be < the stated cap — the contract's "cap cells" is stricter than needed |
| tests/stdlib/containers23.sm:29 | `avali_tak_mala(q, arr)` | `arr = nirmmita(8 * 8)` (:28); q = avali_srij(4), 4 pushes and 1 dequeue → len 3, cap 4 | 3 / 4 | OK |
| tools/proof_props.py:2895 | `avali_tak_mala(q, arr)` | `arr = nirmmita(8 * 8)` (:2888); q = avali_srij(8), 0-6 pushes (:2854) | <= 6 / 8 | OK |
| tools/proof_props.py:3077 | `avali_tak_mala(q, a1)`, `avali_tak_mala(q, a2)` | `nirmmita(8 * 8)` each (:3073-3074); avali_srij(8), 0-6 pushes (:3054) | <= 6 / 8 | OK |

---

## Part C — the numbers

- prakriya audited: **39** (ganita 10, samanvaya 5, shreni 5, suchi 19) — matches the census.
- (prakriya, buffer) rows: **50**.
- rows per verdict: **WITHIN 49**, **UNDOC 1**, **OVER 0**, **NEG 0**, **TERMINATOR 0**, **UNSURE 0**.
- call sites checked: **3** (vinimay) + **17** (chakravala/samasa; the proof_props loop at :4298 counted once) + **138** (ok-channel family, listed per file above) + **6** (avali_tak_mala) = **164**.
- call sites SHORT: **0**.

Named findings:
- OVER: none.
- NEG: none as a verdict. The only index that could go negative is `vinimay`'s caller-chosen
  `i`/`j` (shreni.smlib:7-9); no caller in scope passes a negative or out-of-range index.
- SHORT: none.
- UNDOC: `shreni.smlib:6 vinimay(a, i, j)` — no contract comment, writes a[i] and a[j]
  unchecked; needs `max(i, j) + 1` cells and `i, j >= 0`. All three callers are in range.

Documentation observations (not bounds bugs):
- `lib/shreni.smlib:222` mil_shreni's comment says "merge sort" without the "a[0..n-1]"
  phrase used by :119 and :147; the body needs n cells of `a`.
- `lib/suchi.smlib:471` avali_tak_mala says "Caller allocates cap cells" but the body writes
  exactly avali_maap(q) cells and the module exposes no capacity accessor; one caller
  (tests/stdlib/r8_list_model.sm:51) sizes by avali_maap(q) + 1, which is sufficient for the
  body but may be below the stated cap.
- `lib/samanvaya.smlib` output parameters are compiler bounds-checked `kosh dasham` values
  (src/sutram_compiler.asm:13272-13395, 20537-20555); a short `out` traps with a diagnostic
  rather than overrunning. ekaka_matrika, vivartana and matrika_gunana rely on that trap
  (no R37 pre-check), matrika_yoga and skalar return -1 first.
