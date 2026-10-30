# R75-00 — The three gaps: one closed today, one already closed, one stated; the README sentence

- **Commits on `main`, in order:** `7c0a2d3` (1/2 **v273**: a negative size; the goldens) · `8d51d35` (2/2 `README.md`,
  §19, the changelog) · then this hand-back. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v273) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=240`, FAIL=0** (three new examples). Library proofs **226/226**. Property proofs **86/86**.
- **Guard pages: controls 5/5, suite PASS=240 FAIL=0, library proofs 226/226, property proofs 86/86, 0 failed.**
- **Gates (`sh tools/gates.sh`, Xvfb display): 52 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).** `R73 scratch` 35 checks.
- **The guard, v272 → v273, `tools/guard_pair.py`:**
  - **Linux PE and the Windows compiler under Wine: 522 byte-identical, 117 refused identically, 0 DIFFER, 6 new.**
  - **Linux ELF: 495 byte-identical, 117 refused identically, 27 DIFFER, 6 new.** The 27 are **exactly the programs
    that allocate inside a `mandapa`**: each grew by the new run-time check, and **each gives the same output and exit
    code** on both compilers — checked one by one (`evidence-r75/elf-diff-check.txt`). Nothing outside a block changed.

## WS1 — `nirmmita(-1)`: what it did, read from the code; now refused both ways

**I dumped the emitted code (`evidence-r75/ws1-negative-size-disassembly.txt`, objdump, v270 / v272 / v273).**

- **The cursor never went backwards, on any version.** On **v270** the size was rounded `(-1 + 15) & -16 = 0`, so the
  cursor stayed where it was and `nirmmita` **returned the address of the block above** — then the zeroing loop wrote
  one qword there before testing its count. **So your aliasing fear was right, by a different road:** in
  `evidence-r75/ws1…`, v270 runs `a = nirmmita(16); a[0] = 5; p = nirmmita(n)` with `n = -1` and prints `p` as a
  real address and **`a[0]` as `0`** — `p` *is* `a`, and its contents were wiped. (ChatGPT's R146 F4.)
- **v271–v272** (`jle`): a size ≤ 0 returned 0; the cursor untouched, nothing written. Your `got it` is that: `p` was 0.
- **v273, as you asked:**
  - **written as a number — refused when compiled, anywhere:** `nirmmita(-1)`, `nirmmita(2 - 3 * 4)` →
    `Sutram Error [E_NIRMMITA_RNA]: nirmmita-parimanam rnatmakam - rnam parimanam na sambhavati` /
    `Sanket: nirmmita(n) - n shunyam va dhanatmakam bhavet` (`examples/272`, golden).
  - **computed — inside a `mandapa`, the program stops:** `Sutram Error: nirmmita-parimanam rnatmakam - mandapa-madhye
    rnam parimanam na sambhavati`, exit 1 (`tests/r73_scratch/negative_runtime.sm`: the outer block's `123` prints
    first; the program then stops at the bad allocation).
  - **Not changed, said plainly:** **outside a block, and in a Windows program, a computed negative size still gives
    0** — the ordinary allocator's behaviour. Making it an error there changes every program that allocates (three
    allocator paths: Linux arena, PE, guard pages); it is one decision for you, and I would do it as its own round.

## WS2 — the nested store: established — it was a hole on v270, closed since v271; the golden is in

- **`out = (m[0] = buf) + 1` is not Sutram:** an assignment is a statement, not a value — `vyakaran dosh` at the `=`.
  So the stores that *can* sit inside an expression are the store **calls**: `kosh_push`, `likh8`, `likh8c`, `likh`,
  `setchar`, `memset`.
- **On v270 they were checked only as whole statements** (R146 F1): `vitti out = kosh_push(saved, buf) + 1`
  **compiled**. **Since v271 every store call is checked where it is built** — in an initializer, an argument, a
  condition, inside arithmetic. Not a walk of the tree after the fact, but the same effect: no position escapes it,
  because every call node passes through the check when the parser makes it.
- **The golden that would have caught it:** **`examples/270_r75_nested_store`** — that exact line, `compile_fail`
  (v270 compiled it and printed `2`; v273 refuses it) — and its twin **`examples/271`**, the same line storing a number
  read out of scratch: allowed, prints `2` and `42`. `evidence-r75/ws2-nested-store.txt`.

## WS3 — a scratch pointer in a `kosh`: almost every road is already refused; one is stated

I tried every road on v273 (`evidence-r75/ws3-kosh-routes.txt`):

| | road | v273 |
|---|---|---|
| 1 | `kosh_push(k, buf)`, `k` outside the block | **refused** |
| 2 | `kosh_push(k, buf + 8)`, `k` made inside the block | **refused** |
| 3 | `k[0] = buf` | **refused** |
| 4 | an alias: `q = buf`, then `kosh_push(k, q)` in an initializer | **refused** |
| 5 | a `prakriya` that pushes its argument | **refused by the language** — a `kosh` cannot be a parameter |
| 6 | **`kosh_push(k, adr(buf))` — a `prakriya` that hands the address back** | **compiles — and reads 99, the next block's data** |

**So the `kosh` of scratch pointers is already refused cheaply — except road 6, which is not a `kosh` gap at all:
it is the call blind spot.** Refusing road 6 cheaply would mean refusing any call result that took a scratch
argument — which refuses `yoga(buf, n)` returning a sum, the thing the block is for. Not done, as you said.

**Stated instead, where a beginner reads it:** §19, under *What it holds*: ***"A `kosh` — made inside the block or
outside it — cannot be relied on to hold an address made in the block."*** with the one road named; the README's
first gap; and **the changelog names it as a known limit**. **Road 6 is pinned** as
`tests/r73_scratch/blind_kosh_via_call.sm` (expects the wrong `99`), so a future check that closes it is noticed.

## WS4 — the README

**The sentence, and only that sentence,** in a new `## Memory` section before *Honest status*:

> **Sutram releases memory when a block ends, refuses the common escapes at compile time, and has no garbage
> collector and no runtime.**

**Under it, the three known gaps, in plain words:** (1) an address passed through a `prakriya` call is not followed
— with the rule *pass scratch buffers to functions to be read or written, never to be kept*; (2) memory is released
only on Linux — a Windows program's `mandapa` works but releases nothing; (3) a block releases only what `nirmmita`
asks for inside it — not a `kosh`'s storage, not what a called function allocates — and reused memory is not handed
back to the operating system. Then a pointer to §19.

**Why those three and not your three:** your first two are closed (WS1 now, WS2 since v271), so naming them as gaps
would be wrong; the `kosh` one is the call gap. The three listed are the ones a reader can still hit.

## Things you should know

- **ChatGPT's R147 (`786a2cf`, pushed while I worked) has one point I could test, and it is real — but it is not
  the block's.** `vitti b = nirmmita(count * 8)` with `count = 2^61 + 1` wraps to an 8-byte request. Then
  `b[0] = 7; b[1] = 8; b[2] = 9` inside a block **overwrote the block above** (`owner[0]` printed **9**, not 123);
  outside a block the write lands past `b` instead. **The root is older than the block: a raw `nirmmita` buffer's
  index is not bounds-checked at all** — `b[5]` on a 16-byte buffer writes and reads with no error, block or not
  (`mala` and `kosh` indexes *are* checked: `mala ank seema atikram`). That is the README's existing *"Memory safety
  is manual"*. `evidence-r75/r147-size-wrap.txt`.
- **A correction to my R71 hand-back:** I wrote *"every index is bounds-checked (1.8 ns)"*. **That is true of `mala`
  and `kosh`, not of a raw `nirmmita` buffer**, which has no length to check against. The 1.8 ns raw-index figure
  stands; the claim about it was wrong.
- **`tests/r73_scratch/negative_size.sm` (R74) is replaced** by `negative_literal` and `negative_runtime`: its
  literal negatives are now compile errors, by your rule.

## What I did not do

- **A negative size outside a block / on Windows is still 0** (above); **raw-buffer bounds** not added; **the call
  blind spot** not closed — each is a decision bigger than this round.
- **Not run:** real Windows (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`. `README.md`'s other
  sections and its `225` baseline line are unchanged.

**Document counts:** `doc_counts_gate` NOTEs (not failures, `evidence-r75/doc-counts.txt`): `PROJECT-MASTER.md`
says 48 PASS (measured 52) and five documents say suite 225 (measured 240). Docs prose; the owner's to bump.
