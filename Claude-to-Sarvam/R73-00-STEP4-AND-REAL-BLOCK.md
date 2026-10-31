# R73-00 — Step 4 is in, the six tests pass, and the block is real: 264 KB against 62 MB

- **Commits on `main`, in order:** `7e6e4d3` (1/4 the check and the live block, **v269**) · `ba9b27b` (2/4 the goldens,
  tests and gate) · `0af17f3` (3/4 the reference) · `ee3488d` (4/4 the branch-join hole ChatGPT's R145 predicted, closed — **v270**) ·
  then this hand-back. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v270) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=237`, FAIL=0** (six new examples). Library proofs **226/226**. Property proofs **86/86**. R70 corpus 6/0.
  `SOURCE_PINS_CHECKED`.
- **Guard pages: controls 5/5, suite PASS=237 FAIL=0, library proofs 226/226, property proofs 86/86, 0 failed.**
- **Gates (`sh tools/gates.sh`, Xvfb display): 51 PASS / 0 FAIL / 1 NOT-RUN (Windows execution)** — one more gate: **`R73 scratch`** (15 checks). Same on v269 (12 checks then) and v270.
- **The guard, v268 → v269, `tools/guard_pair.py`: Linux ELF and Linux PE: 492 byte-identical, 97 refused
  identically, 6 DIFFER, 16 new. The Windows compiler under Wine: 492 byte-identical, 97 refused identically, 6 DIFFER (the same six), 16 new — all six give the same output and exit code.** The 6 are exactly the programs that
  contain a `mandapa` (`examples/263` and five in `tests/r72_mandapa/`) — and **all 6 produce the same output and
  exit code**, on ELF and (their PE builds, run under Wine) on PE. Every program without a block is byte-identical.
- **The guard, v269 → v270, all three paths (Linux ELF, Linux PE, the Windows compiler under Wine): 509 byte-identical,
  102 refused identically, 0 DIFFER, 3 new** (the three R145 tests below).

## On the order you asked for — stated plainly

**The check and the redirect went in together, in one compiler version (v269); I did not build and gate a
check-only compiler first.** What holds is the property the order was meant to protect: **in no released version
does `nirmmita` take the scratch side without the check** — v268 had neither, v269 has both — and the six tests
were run, and pass, on the compiler that has both. If you want the stricter sequence reproduced (a check-only
build, the six run on it, then the redirect), it is one `%ifdef` around the redirect and a second build.

## WS1 — Step 4, the three fields

| field | what it is | where it comes from |
|---|---|---|
| **`var_depth`** | the block depth a name was declared at | the R4 declaration list, against the list's length when each block opened — so parameters, module `vitti` and anything declared before the block are depth 0 |
| **`val_taint`** | the block depth whose scratch a value points into (0 = not scratch) | `nirmmita` inside a block is tainted with its block's depth; arithmetic and bitwise operators carry the larger taint of their operands (`buf + 64`); comparisons and `&&`/`\|\|` give a truth value, not an address; **reading data out — `b[i]`, `akshar(b, i)` — carries none** |
| **`box_depth`** | where a container's storage lives | **in v1.0 every container counts as outside** — a scratch address may never be stored into memory at all |

**The rules** (checked on every statement parsed, at compile time):
1. a value with taint *t* may be assigned to a variable only if that variable's `var_depth ≥ t`;
2. it may not be stored into memory — a `mala` cell, a raw block's cell, a field, `likh8`, `kosh_push`;
3. it may not be returned (`nivartanam`).

**Why `box_depth` is "always outside" and not a third live number.** I first followed the design literally — a
container's depth is its own taint, so a scratch pointer may go into scratch memory of the same block. That opens
a hole the check cannot close: `b2[0] = b` (allowed: both scratch), then `outer = b2[0]` — an index read, which
must carry no taint or test 6 fails. Allowing the store would require tracking what is *in* each cell. **So v1.0
says: an address never goes into memory.** It costs one thing — arrays of scratch pointers inside a block — and
it is what makes "data read out of scratch is clean" sound. The field is in the design; its v1.0 value is 0.

**The honest limit, where a programmer hits it.** Every `E_SCRATCH_ESCAPE` message ends with
`Sanket: ayam parikshah prakriya-ahvane kosh-madhye va gacchantam sthanam na pashyati` — *this check does not see
an address that goes through a prakriya call or a kosh.* The reference's §19 says it in a paragraph headed
"read this before you rely on it", with a rule of thumb: **pass a scratch buffer to a function only to be read
or written, never to be kept.** `tests/r73_scratch/blind_call.sm` pins the blind spot (a prakriya that stores
its argument compiles) so that a future check catching it is noticed.

## WS2 — the six tests, each a golden

| # | `examples/` | what | result |
|---|---|---|---|
| 1 | `264_r73_escape_arith` | `outer = buf + 64` inside a block | **refused** — `... bahya-vittau na sthapyate` |
| 2 | `265_r73_escape_mala` | `bahar[i] = buf`, `bahar` declared outside | **refused** — `... smritau na likhyate` |
| 3 | `266_r73_inside_only` | `buf` used only inside | **allowed, no warning** — prints 25 |
| 4 | `267_r73_outer_number` | `outer = 5` inside | **allowed** — prints 5 |
| 5 | `268_r73_return_value` | allocates, returns a computed value; then called **1,000,000 times** | **allowed** — 285, 14000000; **peak 264 KB** (31 MB with the block removed) |
| 6 | `269_r73_copy_out` | **works in scratch, copies the DATA into a buffer allocated before the block, returns that** | **allowed** — prints `40 30` / `20 10` |

**Test 6 passes because data read out of scratch is clean** — `out[i] = tmp[i] * 10` stores a number read from
scratch into persistent memory, which is exactly what the block is for. A check that refused that would be safe
and useless; this one refuses only addresses.

**Beyond the six** (`tests/r73_scratch/`, gate `R73 scratch`, 15 checks with the three above): `kosh_push(k, b)` and `likh8(m, b)`
refused; an inner block's address into an outer block's variable refused, an outer block's address into an inner
block's variable allowed; `agrim` and `krama` out of a block, and recursion through blocks (depth 100), correct;
reused scratch reads as zero; `nirmmita(0)` is 0; a block asking for 2 GB stops with
`Sutram Error: kshetra purnam - mandapa-smritih samapta`, exit 1.

## WS3 — `nirmmita` inside a block uses the scratch cursor

**The measurement** (`tests/r73_scratch/loop_with.sm` / `loop_without.sm`, also a gate check):

| 1,000,000 × `nirmmita(64)`, each written, in a loop | peak RSS | wall |
|---|---|---|
| **inside a `mandapa` in the loop** | **264 KB** | **< 10 ms** |
| without the block | 62,464 KB | 30 ms |

**The RSS stays flat. The block is not decoration.** It is also faster than the persistent path here: the
scratch memory is the same few pages every pass, so there are no page faults.

**How it works** (Step 3 as designed, `docs/decisions/MEMORY-DECISION.md`):
- **Entry:** a hidden local per nesting depth (`0m01`…`0m32`, a name no program can write; recursion-safe because
  it is a local) takes the scratch cursor. If the field has never been reserved, entry reserves it.
- **`nirmmita` inside:** `end -= align16(size)`; if that would cross the persistent cursor → `kshetra purnam`;
  then the block is **zeroed** (memory is reused now, and every `nirmmita` block has always arrived zeroed).
- **Every exit rewinds:** falling off the end; **`nivartanam`** — after its value is computed, to the outermost
  block of that `prakriya`; **`krama` / `agrim`** — to the outermost block between them and their loop.
- **Not Linux ELF** (PE output; the `GUARD_PAGES` build): `nirmmita` keeps the ordinary path and the block emits
  only its hidden local, so the guard-page gate still checks every block program, and Windows is unchanged
  except for that local.

**One thing I measured and changed on the way:** zeroing with `rep stosb` made the scratch loop **4× slower than no
block** (118 ms for the million — ~110 ns per 64-byte `rep stosb` on this machine). A plain qword loop costs
~4 ns. The emitted code uses the loop.

## ChatGPT's R145 against what landed — one hole was real, and is closed in v270

I read R145 (`916f74a`, pushed while I worked) and tried each of its predicted gaps on v269:

| R145 | the shape | v269 | v270 |
|---|---|---|---|
| E02 alias | `q = p` then `nivartanam q` | refused (the taint travels through `=`) | refused — `tests/r73_scratch/escape_alias.sm` |
| E10 tagged return | `nivartanam siddhi(p)` | refused (one check covers both return builders) | refused — `escape_dosh.sm` |
| **E11 joins** | `vitti q = nirmmita(64)`, `yadi (c == 1) q = 7`, `nivartanam q` | **compiled — and `f(0)` returned the scratch address** | **refused** — `escape_branch_join.sm` |
| stale names / 256-name limit | a name reused after its block closed; many names | the table is 1,024 entries, truncated at block close, `capacity_fail` beyond | unchanged |
| E06 `kosh` | a `kosh` of addresses | not seen — the stated blind spot | unchanged, still stated |

**E11 was a real hole in v269.** The check reads statements in order, so `q = 7` inside a `yadi` cleared `q`'s mark
whether or not the branch would run. **v270 makes the update weak: a later assignment never lowers a name's mark;
it lasts until the block ends.** Cost: `p = nirmmita(8)` then `p = 7` then `nivartanam p` is now refused even
without a branch — a false refusal, accepted; the fix is a fresh name. No program in the tree hit it (guard 0
DIFFER). Before/after transcript: `evidence-r73/branch-join-v269-v270.txt`.

## What I did not do

- **No `kosh` inside a block** — not refused this round (a `kosh` declared in a block lives on the persistent side,
  which is safe), not supported either; v1.0's documented rule stands.
- **The blind spots are stated, not closed:** an address through a `prakriya` call or a `kosh`; aliases through
  a function's return. Closing them needs interprocedural effects — the K0 "verified helper" work.
- **Not run:** real Windows (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.

**Document counts:** `doc_counts_gate` NOTEs (not failures, `evidence-r73/doc-counts.txt`): `PROJECT-MASTER.md`
says 48 PASS (measured 51) and five documents say suite 225 (measured 237). Docs prose; the owner's to bump.
