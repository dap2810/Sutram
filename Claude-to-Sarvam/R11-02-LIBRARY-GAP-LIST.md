# R11-02 — WS2: Step 5, the 48 open functions

**303 of 303 functions are closed** (R10: 255). Boundary mutants killed: **935 of 1,119** (R10: 889).

**Every survivor that is left has a verdict:**

| Verdict | Survivors |
|---|---|
| EQUIVALENT | 117 |
| LIKELY-EQ | 58 |
| NO-CONTRACT | 6 |
| OUT-OF-CONTRACT | 3 |

**There is no GAP, OVERRUN, REVIEW or FINDING left.** The list is `evidence-r11/gap-list/`. The run is the
same pipeline as R8–R10: `lib_proof_gaps.py --deep`, then `lib_mutant_witness.py`, then
`lib_gap_report.py`, on the branch.

## How the 48 closed

**29 by new proofs alone, 14 by written argument alone, 5 by both.**

**Seven new proof files** in `tests/stdlib/`:

- `proof_lib` is **217 / 217** (210 + 7)
- **every golden was recorded from the unchanged library**
- no library source changed this round

| Proof | What it pins | Closes |
|---|---|---|
| `r11_khand_varna` | a suffix test on a slice; the cell after `count` segments; the cell after a trailing empty segment; an empty find, needle and separator; a needle at index 0 | khand: `khand_ant`, `khand_yuj`, `khand_bhed`, `khand_pratisthap`. varna: `varna_antah`, `varna_gan`, `varna_pratisthap`, `varna_bhed` |
| `r11_brihat_guards` | a guard cell after every operand and result; an exact multiple (`num == shesh`); a digit equal to the base | brihat: `brihat_gun`, `brihat_bhajshesh`, `brihat_shesh` (2 of its 3). aadhar: `brihat_ank_se` |
| `r11_page_edges` | **page-edge canaries** (below) | `brihat_ank_tak`, and `brihat_shesh`'s last one |
| `r11_nighantu_edges` | a 1-slot map; growing to exactly the count; a removal whose probe chain wraps past the last slot; a 33-byte key next to a live slot; a canary after an exactly-two-page map | `nighantu_anwesh`, `nighantu_grah_mool`, `nighantu_mulya`, `nighantu_kunjika`, `nighantu_vardh`, **`nighantu_apanay`** (R10's one GAP), `nighantu_rikta` |
| `r11_sets_lists` | the empty element; the cell after the sorted output's terminator; a full 512-element set; canaries after a grown list and a grown queue | `rakh_rikta`, `rakh_sampat`, part of `rakh_tak_mala`, **`suchi_rikta`**, **`avali_rikta`** |
| `r11_kalana_edges` | two samples; the last index; a bisection over ±10³⁰, where the 80-step limit decides the answer | parts of `pravan`, `pravan2` and `bahu_mula` |
| `r11_misc_edges` | a payload that exactly fills the buffer and the byte after it; the 2⁶³ edge; padding to the same width; the digit 9; nineteen 9s; a slice followed by a `.` | `anukram_khip_ashtak`, `anukram_grah_ashtak`, `roop_sthir_mool`, `pad_vam`, `varna_tak_dashm` |

## The new technique: page-edge canaries

**The problem: some overruns are invisible to a caller.** The extra pass writes one cell past a
**private** scratch block (`brihat_ank_tak`'s `w`, `brihat_shesh`'s `tr`), or one cell past a list's own
data block. No caller-visible guard cell exists.

**Why a canary works:**

- `nirmmita` maps whole pages, and consecutive maps are adjacent, the newer one just below. I measured
  it: two consecutive allocations sit exactly 4,096 and 8,192 bytes apart.
- So a block of **exactly** 4,096 bytes ends where the block allocated just before it begins.
- The proof sizes the operand so the scratch block is exactly a page (`n = 512`), and allocates a canary
  right before the call.
- A mutant that writes one cell too far overwrites the canary. **The real functions never touch it.**

**For the list and the queue:**

- The data block is allocated only when the structure grows.
- So the proof grows it from 256 to 512 cells with the canary allocated just before.

**The limits:**

- **The killing power is Linux's mmap placement,** which is deterministic.
- **On Windows** (64 KiB allocation granularity) the canaries simply stay intact, so the goldens hold
  there too. They prove less there.

## The 14 closed by argument, and the 5 closed by both

Each argument is in `tools/lib_gap_reviewed.json`, prefixed "R11". There are 26 new entries.

| Function(s) | Verdict | The argument, briefly |
|---|---|---|
| `kalana_trapiz`, `simpson`, `pravan`, `pravan2`, `sadish_yoga` (C1) | EQUIVALENT | clamp: at `kosh_len(ys) == n` the assignment stores the value `n` already has. The rule's pattern only misses it because of the call. |
| `bahu_mula` C3, C5, C8, C10 | EQUIVALENT | the zero (and NaN) cases return on the line before, so `< 0.0` equals `<= 0.0` there |
| `khand_unnat`, `khand_avanat`, `varna_unnat`, `varna_avanat` | EQUIVALENT | the extra pass writes `out[n]`, which the terminator store right after the loop overwrites. It also reads one byte past the input. |
| `khand_viparyay`, `varna_viparyay` (C2) | EQUIVALENT | the extra pass happens only at the middle of an odd length and stores what the odd-length store stores anyway |
| `varna_viparyay` C1 | EQUIVALENT | `n == 0` down the main path does exactly what the guard does |
| `nighantu_kunji_gudh` | EQUIVALENT | `h % 1 == 0` |
| `nighantu_koshtha_likh` (R) | NO-CONTRACT | an internal helper; its one caller ignores the return |
| `roop_varg_mool` C4, C12 | EQUIVALENT | C4 can only set `dot` to its starting value. C12 sits inside the `anya` of `rem == 3`. |
| `rekha_manak` | EQUIVALENT | abs-zero with a float literal: `row + -0.0 == row + 0.0` for every `row` it can hold |
| `rakh_tak_mala` C2, C3, C5 | EQUIVALENT | C2: the extra byte is overwritten, or lands where nothing reads. C3: the extra pass is empty. C5: set elements are distinct. |
| `purna_vyapti` | EQUIVALENT | `n == 0` gives `0 - 0` |
| `varna_chhid` C2, C5 | EQUIVALENT | they only read past the end; the copy loop copies nothing either way |

**Two notes:**

- **R10's GAP verdict for `nighantu_apanay` C12 is deleted.** The new proof kills that mutant, so the
  hand verdict no longer applies.
- **Four of the arguments say "it also reads one byte past the input."** That read cannot change an
  output. It could fault only if the input ended exactly at the end of a mapping. The real code never
  makes that read, so these are equivalent in output, not in memory access. Read them that way.

## Gates

**Linux, fresh clone of the branch:**

- proof_lib **217 / 217**
- proof_props 86 / 86
- suite 205 / 4
- the gap pipeline: **303 closed, 0 open**

**Not run:** Windows.
