# R68-00 — `pad_vam`: the contract was wrong, not the body; the library audited for "allocate n, use more than n"

- **Commits on `main`, in order:** `a5c6596` (1/3: `pad_vam`'s contract says `width + 1`; the roop padders' capacity
  stated — comments only) · `58335cd` (2/3: `217_r12_report` allocates the 22 cells its callees ask for) · `37afdf0`
  (3/3: a property proof's own buffer one cell short — found by the audit, below) · then this hand-back. Pushed with git, not `--force`. **No compiler change: `Sutram 1.0 (v263) - sampurna sutra`**, same binary
  as `ace0a4e`. Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=225`, FAIL=0.** Library proofs **226/226**. Property proofs **86/86**.
  R28 208/0, R29 0 failed (152 byte-identical), R30 8/8, R32 50/50, R38 115/115, R45 8/8, R46 20/20, alloc bounds
  26/0 (13 bounded, 13 exempt).
- **Gates (`sh tools/gates.sh`, Xvfb display): 48 PASS / 0 FAIL / 1 NOT-RUN** (Windows execution).
  `evidence-r68/gates.txt`.
- **The guard, `tools/guard_pair.py`, old tree `ace0a4e` vs this tree, the same v263 compiler on both sides, three
  paths — Linux ELF, Linux PE, the Windows compiler under Wine: 577 programs, 485 byte-identical, 91 refused
  identically, 1 DIFFER, 0 new — on each path.** The one DIFFER is `examples/217_r12_report.sm`, whose source
  changed (commit 2/3); its output is byte-identical to the original example's output on v261
  (`evidence-r68/217-fixed-output.txt`). Commit 1/3 changes comments only, so every program that calls `pad_vam` or
  the roop padders compiles to the same bytes: 0 DIFFER from it. `evidence-r68/guard-*.txt`.
- **One measurement this round that is new: a guard-page compiler** (every `nirmmita` block ends flush against a
  `PROT_NONE` page, so one byte written or read past a block is SIGSEGV) **runs the whole suite, all 226 library
  proofs and all 86 property proofs with 0 faults**, and faults on the two known bugs as controls. §WS2b.
- **The audit's one live finding beyond `217`: `tools/proof_props.py`'s pack/unpack proof gives `khand_mukt` 8
  cells for lengths up to 8, and `khand_mukt` writes cell `n`** — one cell past the block for `n = 8`, which the
  fixed seed never draws (it draws 6, 1, 5, 3, 4, 3, 1, 5). Fixed in 3/3; the proofs read 86/86 before and after.
  **Across 305 library functions, 371 write sites and 419 call sites, nothing else writes past a block.**

## WS1 — `pad_vam` (`lib/vakyank.smlib:238`)

**1. Does it write cell `w`? Yes.** The loop bounds, from the body:

| Write | Loop | Index range |
|---|---|---|
| `dst[p + shift] = dst[p]` | `p = cnt - 1`, `yavat (p >= 0)`, `p = p - 1` | `shift .. w - 1` (reads `0 .. cnt - 1`) |
| `dst[q] = f` | `q = 0`, `yavat (q < shift)`, `q = q + 1` | `0 .. shift - 1` |
| `dst[w] = 0` | — | **`w`** |

with `shift = w - cnt`, reached only when `w > cnt`. The two loops stay inside `0 .. width - 1`; the terminator is
cell `width`, one past the contract's "`>= width` cells". ChatGPT's R139 is exact; Muse's ROUND-68 count agrees.

**2. The contract is wrong, not the body.** The `0` at `out[width]` is the terminator every writer in the library
leaves: `ank_tak_varna` writes `out[count] = 0` and says so (*"out[count] is set to 0 as a terminator. Caller
allocates >= 22 cells"* — 22 for at most 20 characters plus the terminator), `ank_tak_aadhar_varna` writes
`dst[rlen] = 0`, and `lib/roop.smlib`'s header states it for the whole module (*"every function writes packed bytes
into `out` with a 0 terminator and returns the byte count"*). `pad_vam`'s input is such a buffer — `217`,
`strconv_pad` and the property proof all call it on `ank_tak_varna`'s output — and without the write the padded
result would be the one unterminated buffer in the library, because the move loop overwrites the old terminator at
cell `cnt`. So the body keeps the module's invariant and the contract line was one short. **Fixed in the contract:
"Caller must allocate >= width + 1 cells"**, with the terminator stated (`lib/vakyank.smlib:234-240`).

Muse's note puts the other choice on the table: delete the write, since no in-tree caller reads `dst[w]`. Two
reasons I did not: it would make `pad_vam` the one writer that does not terminate, and it changes the bytes of the
four programs that call it (two tests, the example, the property proof) for a write that costs nothing. Either way
is a one-line change; if the owner prefers the deletion, `tests/stdlib/strconv_pad` and `r11_misc_edges` keep
passing (checked: neither reads the cell).

**3. Siblings.** `roop_pad_vam`, `roop_pad_dakshin`, `roop_pad_madhya` (`lib/roop.smlib:253-361`) each write
bytes `0 .. width - 1` and then `akshar_rakh(dst, w, 0)`; on the `width <= sn` path they copy `sn` bytes and write
the terminator at byte `sn`. The module header states the terminator, so they are not off by one — but no line
stated their capacity. **Stated now at the head of the padding section: `out` must hold `width + 1` bytes
(`sn + 1` when `width <= sn`).** Their only caller, `tests/stdlib/fmt_pad.sm`, gives 128 bytes for widths <= 6.
No other function in `lib/` pads.

**4. `217`.** It also calls `ank_tak_varna(scores[i], koshtha)`, whose contract asks for 22 cells; 4 cells
satisfied neither contract (Muse's count: three cells past the block per iteration, not two). **It now allocates
`nirmmita(22 * 8)`** and prints what it printed on v261, byte for byte.

## WS2 — the audit: every write in `lib/`, every contract, every caller

**Method.** A census script (`evidence-r68/census.py`) lists, for each of the 305 library `prakriya`, every write
into a buffer — `x[i] = …` (cell) and `akshar_rakh(x, i, …)` (byte) — with its index expression, the enclosing
loop/branch headers, and the buffer's origin: a parameter (the caller's), the function's own `nirmmita`, a declared
`mala`/`kosh` (compiler-checked), or a container field. **371 write sites in 112 prakriya across 16 modules**
(the other 193 prakriya write nothing). Each body was then read in full, in four independent passes over disjoint
module groups (`evidence-r68/audit-*.md`, with line numbers for every claim), and I spot-checked the findings
below against the source myself. Callers were traced in `examples/`, `tests/**` (not `tests/negative/`), `lib/`
and the programs embedded in `tools/proof_props.py`.

### The numbers

| | count |
|---|---|
| prakriya with writes or allocations audited | **112** (all) |
| (prakriya, buffer) rows judged | **146** |
| **OVER — a body writes past its stated capacity or its own allocation, on contract-valid input** | **0** |
| TERMINATOR — one `0` at `count`/`width`, stated by the contract or the module header, no capacity line | **15** (named below) |
| UNDOC — a caller-supplied buffer with no stated capacity | **17** (named below, with the capacity each needs) |
| NEG — an index that can go negative on contract-valid input | **0** (the three roop padders write `dst[sn]` for a negative `sn`, which no contract allows — noted below) |
| call sites checked against a contract or a needed capacity | **419** |
| **callers that allocate less than the function's stated constant** | **5 sites in 4 places** (named below) |
| **callers that allocate less than the body can write** | **2, both fixed this round:** `217` (2/3) and the pack/unpack proof (3/3) |

**Every function with a "caller must allocate >= N" contract stays within N** (Muse's note counted 4 explicit
contracts; reading every comment block finds 16 functions with a capacity in some phrasing — `pad_vam`,
`ank_tak_varna`, `chakravala`, `samasa`, `brihat_ank_tak`, the five `samanvaya` matrix functions,
`avali_tak_mala`, `nighantu_mulya`, `nighantu_kunjika_ashtak`, `anukram`'s `cap`, `meru_mala`'s `a[0..n]`,
`ganit_yadricch`'s 1-cell `state` — and after commit 1/3 all hold). **Every `dst[i]` loop is bounded by
the capacity it has** — the stated one, the function's own allocation, or a container's header field set together
with the allocation in its constructor and every growth path (the `suchi`/`avali`/`nighantu`/`sangrah` invariant
`cells(data) == cap` was checked at each of those sites).

### Callers below a stated constant (contract violations; none writes past its block with today's values)

| caller | allocates | contract asks | note |
|---|---|---|---|
| `tests/stdlib/strconv_pad.sm:3` (two `ank_tak_varna` calls) | 10 cells | `ank_tak_varna`: 22 | values 42 and 12345 write cells 0..5 |
| `tools/proof_props.py:471` (`prop_strconv_pad_left`) | 12 cells | 22 | values 0..9999 write cells 0..4 |
| `tests/stdlib/r8_map_edges.sm:12` | 64 bytes | `nighantu_kunjika_ashtak`: cap·33 = 132 | one 2-byte key: 3 bytes written |
| `tests/stdlib/map_clear.sm:4` | 200 bytes | 264 | empty map: 0 bytes written |

These are `217`'s class before its fix — the same as allocating 32 bytes for a contract that said 22 cells — and
each is a one-number change in a test. **Not fixed: the brief said count and name them.** The guard-page run (WS2b)
confirms none of them writes past its block with the values it uses, and the static audit confirms the values
cannot reach the block's end (the generators' ranges are bounded well below it).

### The one that could: `prop_strb_pack_unpack` (fixed, commit 3/3)

`tools/proof_props.py:1006` allocated `back = nirmmita(8*8)` and called `khand_mukt(out, n, back)` and
`khand_mukt("…", n, back)` for strings of length 1..8 drawn at random. `khand_mukt` writes cells `0..n-1` and
`back[n] = 0` (`lib/khand.smlib:74`); for `n = 8` that is one cell past the block, into `out`, the next allocation
(`evidence-r68/proof-pack-unpack-short.txt`). **The fixed seed `20261009` draws 6, 1, 5, 3, 4, 3, 1, 5 — never 8 —
which is why 86/86 held on every compiler and under the guard pages.** A direct `khand_mukt("abcdefgh", 8, back)`
with 8 cells faults under the guard-page compiler; with 9 it runs. The proof now allocates 9 cells; 86/86 before
and after on v263 and under guard pages. Same class as R65's bigint proof: the library is right, the proof's own
buffer was short.

### UNDOC — caller-supplied buffers with no stated capacity, and what each needs

| function | buffer | capacity the body needs |
|---|---|---|
| `vakyank.ank_tak_aadhar_varna(n, base, out)` | `out` | `digits(n, base) + 1` cells — 64 for any `n` (base 2) |
| `varna_pratisthap(src, sn, find, fn, repl, out)` | `out` | `sn + ⌊sn/fn⌋·max(0, rlen − fn) + 1` cells (`sn + 1` when `fn <= 0`) |
| `varna_bhed(src, sn, sep, sepn, parts, maxparts)` | `parts` | `sn + 1` cells |
| `varna_yuj(parts, count, sep, sepn, out)` | `out` | `Σ len_i + max(0, count − 1)·max(0, sepn) + 1` cells |
| `varna_chhid`, `varna_unnat`, `varna_avanat`, `varna_viparyay(src, sn, out)` | `out` | `sn + 1` cells each |
| `anukram_grah_aayam_purva(buf, pos, cap, dst, out_n)` | `dst` | the decoded length — up to `cap − pos − 8` bytes, whatever the stream says |
| `nighantu_kunjika(m, out)` | `out` | `Σ(1 + kl_i) + 1` cells, worst `33·cap + 1` (a trailing `0` cell from `khand_mukt`) |
| `sangrah.rakh_tak_mala(s, cap, out)` | `out` | `Σ(1 + l_i) + 1` cells, worst `33·s[0] + 1` (same trailing `0`; the `cap` argument is unused) |
| `shreni.vinimay(a, i, j)` | `a` | `max(i, j) + 1` cells, `i, j >= 0` — no count parameter, no check |
| `khand_pratisthap(src, sn, find, fn, repl, out)` | `out` | `sn + ⌊sn/fn⌋·max(0, strlen(repl) − fn) + 1` bytes (`sn + 1` when `fn <= 0`) |
| `khand_bhed(src, sn, sep, sepn, parts, maxparts)` | `parts` | `sn + 2` cells, whatever `maxparts` is (the last segment's `khand_mukt` terminator) |
| `khand_yuj(parts, count, sep, sepn, out)` | `out` | `Σ len_i + (count − 1)·max(0, sepn) + 1` bytes |
| `roop_varg_sahaya` and its wrappers `roop_varg`, `roop_varg_bharatiya`, `roop_varg_vishwa(src, sn, out)` | `out` | Indian `sn + max(0, ⌊(sn−2)/2⌋) + 1` bytes, international `sn + max(0, ⌊(sn−1)/3⌋) + 1` |
| `roop_varg_ank(v, indian, out)` | `out` | 29 bytes (Indian) / 27 for the worst int64 |

**TERMINATOR without a capacity line — 15 functions** whose only write at `count` is the terminator the module
header promises, and whose contracts say "terminator at `out[n]`" or nothing: `khand_bandh`, `khand_mukt`,
`khand_pratilip`, `khand_chhid`, `khand_unnat`, `khand_avanat`, `khand_viparyay` (each needs `n + 1`);
`roop_ank` (20 bytes worst), `roop_ank_aadhar` (65), `roop_ank_aadhar_saral` (66), `roop_ank_dhvaj` (68, with
prefix and sign), `roop_sthir_mool` (22), `roop_chinhit` (21), `roop_sign_akshar` (21); and `pad_vam`, now with
its line. The `khand` header's *"the caller allocates generously"* is not a number; these are the numbers.

ChatGPT's R140 (`5aa0c13`, landed while this ran, source-only) reaches the same numbers independently where it
looked: `pad_vam` width + 1, `217` at 176 bytes, `khand_bhed` sn + 2, `nighantu_kunjika` and `rakh_tak_mala` at
`33·cap + 1`, `ank_tak_aadhar_varna` at 64 cells; it did not run anything, so the pack/unpack proof's short buffer
is new here.

Every caller of every one of these was traced and allocates enough (the tables in `evidence-r68/audit-*.md`).
The tightest: `tools/proof_props.py:945` gives `nighantu_kunjika` 32 cells for a random worst case of 31.
**These are contract lines to write, not bodies to change; the library's prose is not mine, so they are listed.**

### Found on the way, not bounds bugs, reported

- **`nighantu`'s `cap` is the caller's parameter, not the header's `m[0]`.** `nighantu_khip`, `nighantu_apanay`,
  `nighantu_grah`, `nighantu_antah`, `nighantu_grah_mool` and `nighantu_mil` trust it; with `cap > m[0]` the key
  region's base `(2 + 3·cap)·8` alone lies past the block (`m = nighantu_srij(1); nighantu_khip(m, 2, "a", 1, 5)`
  writes bytes 72..95 of a 72-byte block). The authors know (`nighantu_rikta`'s contract says so). **A scan of all
  399 `(map, cap)` argument pairs in the tree finds no caller passing a cap larger than the map's** — the two
  mismatches are deliberate edge tests that are rejected or unused. Latent by API, not exercised.
- `avali_tak_mala`'s contract says "cap cells"; the body writes `avali_maap(q)` cells and no capacity accessor
  exists (`tests/stdlib/r8_list_model.sm:51` sizes by `maap + 1`, enough for the body).
- `varna_tak_ank:95` and `varna_tak_dashm:285` read `buf[0]` when `n < 0` (a contract-invalid count); `varna_yuj`
  trusts the segment lengths stored in `parts`; `varna_pratisthap` scans `repl` to its terminator (documented).
- `pad_vam` with a negative `count` below −1 (contract-invalid) would write past `width + 1`.
- `rakh_samroop_diff` leaks `tmpa` when `tmpb`'s allocation fails (return −1).
- **The three roop padders have no `sn < 0` guard** (`khand_unnat:364` has one): a negative `sn` writes
  `dst[sn]` — a negative index — on the `width <= sn` path, and `roop_pad_vam`/`roop_pad_madhya` pad past
  `width + 1` for `sn <= −2`. No contract allows a negative length and no caller passes one; the guard is one line
  each if the owner wants it.
- `khand_bhed` with `sn < 0` stores a negative length cell; `khand_yuj` walks backwards on a negative stored
  length; `roop_varg_sahaya` reads `s[0]` for any `sn != 0` and groups any bytes, not only digits;
  `roop_ank_aadhar_saral`/`roop_ank_dhvaj` touch `out[1]` on a bad base with negative `v` while returning 0.
- Six roop formatters allocate scratch with `nirmmita` on every call and never release it (`roop_ank`,
  `roop_ank_aadhar`, `roop_varg_ank`, `roop_sthir_mool`, `roop_chinhit`, `roop_sign_akshar`) — Muse's WS3 counted
  the `ank_tak_varna` instance of this for `217`; it is the `mandapa` population, not a bounds matter.

## WS2b — the dynamic half: a guard-page compiler over the whole corpus

The static audit reads every path; it cannot run them. So I built, in scratch (never shipped, never in `src/`), a
compiler whose `nirmmita` is a 94-byte sequence: `mmap` the block's pages plus one, `mprotect` the last page
`PROT_NONE`, return `guard − size` — the block ends on the last byte before the unreadable page, so **writing or
reading one byte past any `nirmmita` block is SIGSEGV**. `nirmmita(0)` is 0 as today. No arena, no `kosh`
extension, nothing else changed (`evidence-r68/r68_efence.inc`, `guard-page-sequence.asm`, `guard-pages-how.sh`).

| corpus under the guard-page compiler | result |
|---|---|
| regression suite (229 examples) | `NO-EXPECTATION=4 PASS=225`, **0 FAIL** |
| library proofs (226 programs) | **226 passed, 0 failed** |
| property proofs (86) | **86/86** |
| **control:** the original `217` (`ace0a4e`) | **SIGSEGV** at the first `pad_vam` over-write |
| **control:** `tools/proof_props.py` as of `8e6ae35` (before R65's proof fix) | **85/86** — *bigint divmod reconstruct* fails, the over-read R65 found |

**So on every path the 541 programs execute, no block is written or read past its end — to the byte, not to the
page.** What this does not cover: paths no program takes (the static audit's job, above), writes before a block
(negative indices; the static audit found none reachable), and declared `mala`/`kosh` storage (compiler-checked).
This is the measurement I would make a gate of — see WS3.

## WS3 — would extending `check_alloc_bounds.py` catch the class?

**Not by extension: it is the wrong instrument.** It reads `nirmmita` *size* expressions and asks whether a count
was bounded before the multiply; it never reads an index, and `pad_vam` contains no `nirmmita` at all (Muse's WS2
says the same). A write-bounds checker is a new, second tool sharing only the line reader.

**Priced, with a prototype** (`evidence-r68/check_write_bounds-prototype.py`, 192 lines, and its output):

- **Input:** a stated capacity per function, read from the existing contract phrasing (`>= <expr> cells|bytes`,
  `out must hold <expr> elements`) — **7 functions carry one today**; the roop padders' is in a section header the
  tool would need to be told about, and the 17 UNDOC functions above have none, so each needs a line first.
- **Method:** aliases followed (`dst = out`, `w = width`), loop variables given the range their header and step
  imply (`yavat (q < shift)` from `q = 0` → `0 .. shift − 1`; `yavat (p >= 0)` from `p = cnt − 1` → `cnt − 1 .. 0`),
  path conditions kept (`yadi (w <= cnt) { nivartanam }` means `w > cnt` after it), and every write's index
  evaluated against the capacity over a grid of small parameter values with loop variables at both ends of their
  ranges. Anything it cannot read is reported `UNREAD`, never skipped.
- **Result on the tree:** the 7 contracts **WITHIN**; **on `ace0a4e`, where `pad_vam` still said `width`, it
  reports `OVER: out[w] = index 1, capacity 1 at count=0, width=1`** — the bug, with the input that shows it.
- **Its honest limit:** a grid is a bounded model check, not a proof. It is sound for affine indices against affine
  capacities (the padding and matrix families); for a constant capacity against a counter the body computes
  (`ank_tak_varna`'s 22 against the number of digits) it proves nothing and must say `UNREAD`, and the hash-table
  invariants (`nighantu`) are beyond it altogether.
- **Price as a gate:** ~250 lines (the prototype plus `UNREAD` for non-affine indices, byte-string writes through
  `akshar_rakh`, section-header contracts, and the gate line), **plus one contract line on each of the 17 UNDOC
  functions** (and the 15 TERMINATOR ones to make the +1 explicit), which is where the real work is. It would have caught `pad_vam` on the day it was written. It
  would not have caught `217` (a caller) or the proof's over-read (a reader).

**What catches the whole class, including callers and readers, is WS2b**: ~100 lines of Python to build the
guard-page variant from `src/` with the 94-byte sequence swapped in (the proof tools already build their own
compiler) and run the three corpora — every executed over-write and over-read, to the byte, with no annotations.
It found both known bugs in this round's controls — and it would not have found the pack/unpack cell on its
own, because the seed never draws the length that overruns: the dynamic gate sees what runs, the static audit
sees what can run, and this round needed both. **My recommendation: the guard-page gate first (it is cheap and
exact for everything the tests run), the write-bounds checker second for the paths tests do not run, and the 32
contract lines either way.** Neither is built in the tree this round; the brief asked for the price.

## What I did not do

- **Not started:** Step 2, chunking, anything in `src/`. The compiler binary is `ace0a4e`'s.
- **Not fixed:** the five callers below a stated constant (named above); the 17 UNDOC and 15 TERMINATOR contract
  lines; the `nighantu` cap-parameter hazard; the roop padders' missing `sn < 0` guard; `avali_tak_mala`'s wording.
- **Not run:** real Windows (Wine only). The guard-page compiler was not run on PE output (Linux `mprotect`).
- **Not touched:** `src/`, `lang/`, `backups/`, `Windows-to-Sarvam/`, the frozen packs, `docs/` prose.
