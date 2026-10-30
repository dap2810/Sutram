# R72-00 — `mandapa` exists, and does nothing yet — as asked

- **Commits on `main`, in order:** `ec79269` (1/3 the keyword and block, **v268**) · `e57d1af` (2/3 the goldens and gate) ·
  `0aa2e8b` (3/3 the reference) · then this hand-back. Pushed with git, not `--force`.
- **Compiler: `Sutram 1.0 (v268) - sampurna sutra`.** Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=231`, FAIL=0** (one new example). Library proofs **226/226**. Property proofs **86/86**. R70 corpus 6/0
  (its `lang/sanskrit.lang` pin moved, below). `SOURCE_PINS_CHECKED`.
- **Guard pages: controls 5/5, suite PASS=231 FAIL=0, library proofs 226/226, property proofs 86/86, 0 failed.**
- **Gates (`sh tools/gates.sh`, Xvfb display): 50 PASS / 0 FAIL / 1 NOT-RUN (Windows execution)** — one more gate: **`R72 mandapa`**.
- **The guard, v267 → v268, `tools/guard_pair.py`: Linux ELF and Linux PE: 488 byte-identical, 94 refused
  identically, 0 DIFFER, 13 new (this round's files). The Windows compiler under Wine: 488 byte-identical, 94 refused identically, 0 DIFFER, 13 new.** Adding the keyword
  changes no existing program: `mandapa` was no identifier anywhere in the tree.

## WS1 — the keyword, and nothing else

- **`mandapa` / `मण्डप` is a keyword** (compiler table, roman and Devanagari; a row in `lang/sanskrit.lang`, so the
  built-in Sanskrit pack and `src/r22_lang_builtin.inc` carry it).
- **It is a statement: the keyword, then a body** by the same rules as every other body since v265 — indented
  (the norm in examples), `{ }` (allowed), or one statement on the same line. Its variables are scoped to it,
  as in any block.
- **Semantically inert: it builds the same block node a braced block builds, redirects no `nirmmita`, and emits
  no mark and no rewind.** So a program with a `mandapa` block and the same program without it compile to **the
  same bytes** — the test the brief set, and it holds for every pair below.
- **On "the mark and the rewind":** the brief asks for them *and* for identical bytes. Both cannot hold — a mark
  is two instructions in the binary. I took identical bytes as the binding test ("if they differ ... the mark is
  emitted when it should not be") and emit **nothing** this round. The mark (a hidden local per nesting depth
  holding the scratch cursor at entry) and the rewind (on normal exit, `krama`/`agrim`, and `nivartanam` after its
  value is computed) belong in the round that moves `nirmmita` onto the scratch side — they only mean something
  once there is a scratch allocation to rewind. **The design is unchanged; it is ~60 lines in `r72_parse_mandapa`
  and the code generator's block exit, and I can price it exactly when that round comes.**

## WS2 — the goldens that pin it, and the one refusal

**`tests/r72_mandapa/`, run by the new gate `R72 mandapa` (`test_mandapa.py`): 8 checks, 0 failed.**

| pair | what it holds | same bytes, same output |
|---|---|---|
| `flat_with` / `flat_without` | one block, a scratch buffer, a scalar result | **yes** — 42 |
| `nested_with` / `nested_without` | a block inside a block, the inner one braced | **yes** — 15 |
| `loop_with` / `loop_without` | a block in a `prakriya`, a loop allocating 64 B per pass, `nivartanam t` (a value) inside the block | **yes** — 4950 |
| `devanagari_with` / `devanagari_without` | `मण्डप` | **yes** — 3 |

**The negative tests — `nivartanam` of a scratch address is refused** (`Sutram Error [E_SCRATCH_ESCAPE]:
asthayi smriti bahir na gacchati - mandapa-madhye nirmitam sthanam nivartanam na shakyate`):

| program | |
|---|---|
| `escape_name`: `vitti b = nirmmita(64)` then `nivartanam b`, in the block | **refused** |
| `escape_direct`: `nivartanam nirmmita(8)` in the block | **refused** |
| `escape_assigned`: `p = nirmmita(16)` then `nivartanam p`, in the block | **refused** |
| `allowed_outer`: `nivartanam p` in the block, `p` allocated **before** it | **allowed** (prints 9) |

**What the check is, exactly:** at parse time, inside an open `mandapa`, a name given `nirmmita(...)` by `vitti`
or `=` is remembered until the block closes; `nivartanam` of that name, or of a `nirmmita(...)` call, is refused.
**What it is not** (Step 4's work, stated so nobody reads more into it): it does not follow an alias
(`vitti y = b; nivartanam y`), a field, an index, a call that returns the block, or a scratch address stored in
an outer variable and returned *after* the block closes. The message is not in the translated message set, so every
pack prints the romanised Sanskrit default (the frozen packs get no new entry).

**Plus `examples/263_r72_mandapa.sm`** (golden): the middle of three numbers worked out in a scratch buffer inside
a `mandapa` in a `prakriya` — the shape the block is for — printing 5 and 3.

## WS3 — the scope, in `docs/LANGUAGE-REFERENCE.md`

- **The keyword table** has `mandapa (मण्डप) — a scratch block: temporary buffers of numbers for one piece of
  work`.
- **New §19, "The scratch block: `mandapa`"**, opening with the beginner's sentence: ***"A `mandapa` gives you a few
  temporary buffers of numbers for one piece of work; when the block ends, they are gone. Use it for scratch
  arithmetic. It does not work with `kosh`."*** Then an example, the allowed/refused table, what it is **not**
  (not a way to manage `kosh`-heavy memory; a block around a call does not reclaim what the callee allocates),
  and **the status: inert in v268** — so nobody expects it to reclaim memory yet.
- **New §6a-2, "Bodies without braces"**: the R70/R71 rules in four lines (indentation decides; a same-line body
  is one statement and may not share its line; nothing after `mukhya`'s `}`; `guna` needs braces). The reference
  showed only braces, and the indentation rule is now the language — it belonged where `mandapa` is described.

**Is the honest sentence "small fixed-size scratch, and no vectors"? Yes, and the page says so in plainer words.**

## Things the owner should know

- **The R70 corpus pins `lang/sanskrit.lang`** (ChatGPT's R136/R137 recorded the same blob as the vocabulary
  snapshot they checked). Adding the `मण्डप` row moved it: `27eda2b6` → the new blob, in
  `tests/negative/r70/manifest.json` and `docs/NEGATIVE-CORPUS.md`, with the reason in `repinned`. The corpus
  passes 6/0 on the new pin.
- **`tests/r72/` already existed** (a baseline test from an earlier numbering); this round's files are in
  `tests/r72_mandapa/` so nothing there was touched.
- **The frozen packs have no `mandapa` row.** A Hindi or Gujarati program can write `mandapa` in roman (checked: `--lang hindi`
  compiles and runs `flat_with.sm`, `evidence-r72/frozen-pack-roman-mandapa.txt`); a native word would be new development in a frozen pack, so it is not added.

## What I did not do

- **No `nirmmita` is redirected; no mark or rewind is emitted** — the round's rule.
- **No escape check beyond the `nivartanam` rule** — Step 4.
- **Not run:** real Windows (Wine only).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.

**Document counts:** `doc_counts_gate` NOTEs (not failures, `evidence-r72/doc-counts.txt`): `PROJECT-MASTER.md`
says 48 PASS (measured 50) and five documents say suite 225 (measured 231). Docs prose; the owner's to bump.
