# ROUND-63 — close the last three items, then development starts

Base: origin/main `4c556029`, CHANGELOG v414, compiler v261.
Read first: `docs/MEMORY-UNIQUE-HYBRID.md`, my ROUND-61 critique
and ROUND-62 finish, `ChatGPT-to-Sarvam/ROUND-134-KSHETRA-REVIEW.md`
and `ROUND-135-KSHETRA-CHECK.md`, `Claude-to-Sarvam/R62-00-
KSHETRA-STEPS-3-4.md`.

Design only. No tree changes. All three items are closed below
to the point where development can start; the two things that
remain are a Sanskrit check (ChatGPT's, per the owner's rule)
and a small follow-up reword round, neither of which blocks
steps 1–4 development (see §5).

## Item 1 — the word collision: `kshetra` stays for the region; the field diagnostics become `avayava`

### 1.1 The inventory (lens 1–3, counted and named)

The three diagnostics, exactly as the brief lists them, plus
the fourth string the brief does not name but the reword must
cover:

| Source line | String |
|---|---|
| `src/sutram_compiler.asm:313` | `Sutram Error [E_UNKNOWN_FIELD]: agyat kshetra '` |
| `:317` | `Sutram Error [E_AMBIGUOUS_FIELD]: kshetra '` |
| `:328` (hint, `Sanket:`) | `' kasyashchid api rachanayah kshetram nasti` |
| `:827` | `Sutram Error: rachana kshetra seema atikram` |

The hint at :328 uses `kshetram` for the same concept. A
reword that changes the three errors but leaves the hint
saying `kshetram` would be inconsistent — the hint is part of
the change surface, and it is easy to miss because the brief
lists three diagnostics, not four strings.

**Goldens and test files pinning them (lens 1–2):**

| File | What it pins |
|---|---|
| `tests/expect/224_unknown_field.out` | `E_UNKNOWN_FIELD` + hint, for `examples/224_unknown_field.sm` |
| `tests/expect/234_ambiguous_field.out` | `E_AMBIGUOUS_FIELD`, for `examples/234_ambiguous_field.sm` |
| `tests/expect/106_rachana_field_capacity.out` | capacity error, for its example |
| `tests/sandesh/expect/default/unknown_field.out` | Latin diagnostic under the default pack |
| `tests/sandesh/expect/sanskrit/unknown_field.out` | Devanagari diagnostic under the Sanskrit pack |
| `tests/r23/test_capabilities.py:62,66` | Two assertions on the Latin strings |

That is the complete list: **3 example programs, 5 golden
files, 2 test assertions**. No other test file asserts on
these strings (a full-tree grep for `agyat kshetra` /
`rachana kshetra` returns only the r23 test, plus handoff
documents quoting them).

**Library and docs (lens 3): no quotes.** No `lib/` function
and no user-facing doc quotes any of the three strings.
`docs/` prose uses `kshetra` only in
`docs/MEMORY-UNIQUE-HYBRID.md`, in the *region* sense — which
is the sense being kept, so no doc change is needed there.
(The ROUND-62 handoff quotes the old strings; handoff
documents are history, not user docs, and are not updated.)

**Frozen packs need no change.** The other sandesh packs have
their own `unknown_field.out` files, but they contain their
own scripts' words for "field" (Bengali ক্ষেত্র, Tamil
புலம், Telugu క్షేత్రం) — they translate the *concept*,
not the Latin label, and none contains the Latin word
`kshetra`. Rewording the Latin diagnostic therefore does not
touch any frozen pack's golden. The one pack golden that does
change is the **Sanskrit** pack's (Devanagari) — and the
Sanskrit pack is the live pack, not a frozen one, so updating
it is ordinary development, not frozen-pack work. (No sandesh
goldens exist for the ambiguous-field or capacity diagnostics
in any pack — only `unknown_field` is sandesh-tested.)

**Total change surface for the reword: 15 touch points** — 4
Latin strings in `src/`, 4 Devanagari strings in
`lang/sanskrit.sandesh` (lines 39, 45, 65, 195, with the Latin
originals as comments on lines 38, 44, 64, 194), 5 golden
files, 2 test assertions. Zero library changes, zero
user-doc changes, zero frozen-pack changes.

### 1.2 The replacement word: `avayava`, checked against the compiler

Sarvam's requirement is that the replacement be checked
against the compiler, not only against a dictionary — because
that is exactly how `kshetra` slipped through (dictionary-clean,
compiler-colliding). I checked five classical candidates as
standalone words across `src/`, `lib/`, `tests/`, `examples/`,
`docs/`, and `lang/`:

| Candidate | Sense | Compiler result |
|---|---|---|
| `avayava` (अवयव) | constituent part, member, limb of a whole | **Zero hits — clean** |
| `anga` (अङ्ग) | limb, part, member | Zero hits — clean, but see note |
| `bhaga` (भाग) | part, portion, share | Zero hits — clean, weaker sense |
| `amsa` (अंश) | part, portion, share | Zero hits — clean, weaker sense |
| `sadasya` | member (of an assembly) | Zero hits — clean, wrong nuance |
| `guna` (for contrast) | quality, attribute | **COLLIDES — it is a keyword** (`guna` = switch, `KW_GUNA`, `:166`, `:712`, used in `:822` `guna seema atikram`) |

The `guna` elimination is the proof the compiler check
matters: a dictionary-plausible word for "attribute" is
already a statement keyword in this compiler, and a
dictionary-only check would have missed it exactly as it
missed `kshetra`.

**Recommendation: `avayava`.** It is the most precise
classical word for the concept: a constituent part of a
structured whole (Nyaya usage: a member/part of an argument;
anatomy: a limb). `anga` is shorter and also classical, but
it carries a second technical sense in Paninian grammar (the
stem/base to which suffixes attach), which is a needless
ambiguity in a language that cares about grammar. `bhaga`
and `amsa` mean "share/portion" more than "member of a
structure". `sadasya` means membership in a group of people,
not a part of a structure. `avayava` has no competing
technical sense in this tree and no hits anywhere in it.

Proposed new Latin strings (the Sanskrit pack's Devanagari
forms are drafts — see §1.3):

- `Sutram Error [E_UNKNOWN_FIELD]: agyat avayava 'w'`
- `Sutram Error [E_AMBIGUOUS_FIELD]: avayava 'x'`
- Hint: `' kasyashchid api rachanayah avayavam nasti`
  (accusative `-am`, parallel to `kshetram`)
- `Sutram Error: rachana avayava seema atikram`

### 1.3 What still needs ChatGPT (stated, not skipped)

Per the owner's rule, no Sanskrit word enters the compiler
until ChatGPT checks it. Two things need that check:

1. **`avayava` itself** — dictionary attestation and sense
   (constituent part vs the alternatives above). My
   compiler-side evidence is complete; the dictionary side is
   ChatGPT's.
2. **The Devanagari forms, which change beyond word
   substitution.** `kshetra` is neuter (`kshetram`), while
   `avayava` is masculine — so the Sanskrit pack's forms
   change gender as well as stem (e.g. `अज्ञातं क्षेत्रम्`
   becomes a masculine form, and the hint's `क्षेत्रं
   नास्ति` becomes the corresponding masculine construction).
   I do not present Devanagari forms as checked here, because
   getting the gender/case agreement wrong would repeat the
   original error in a new form. ChatGPT's check must cover
   the pack strings, not just the Latin word.

Until that check lands, the block documentation must note the
double meaning of `kshetra` explicitly (ROUND-62 §6), and the
reword itself is a small follow-up round (15 touch points,
§1.1) — it does not block steps 1–4 development, because the
block implementation reserves the keyword `kshetra` and does
not depend on the diagnostic strings.

## Item 2 — `nivartanam` inside a region: allow it (ChatGPT is right, for a precise reason)

### 2.1 The deciding question, answered specifically

Sarvam's question: does "restore before the jump/return"
handle Gemini's evaluation-order case — where the return
expression itself allocates, so restoring before the return is
too early and restoring after the expression is too late to be
simple?

The answer is that **"restore before the jump/return" is
ambiguous between two readings, and only one of them is
correct** — and ChatGPT's actual sequence is the correct one:

- **Wrong reading (Gemini's worry, valid against this
  reading):** restore the cursor *before evaluating* the
  return expression. If the expression allocates scratch, that
  allocation lands *below* the restored mark — i.e., in memory
  the enclosing context considers free, or in memory the
  enclosing block's exit will later free. The allocation's
  lifetime is misattributed: it survives the block it was
  written in, or it is freed by an outer rewind while still
  referenced. This is a real bug, and any implementation that
  restores before evaluation has it.
- **Correct reading (ChatGPT's R134 sequence):** evaluate the
  expression **first**, check the result, **then** restore,
  **then** execute the jump/return instruction — with the
  value preserved in `rax` (and `rdx` for `phal`) across the
  restore. The four cases:
  1. *Expression allocates scratch, value is scalar* (e.g.
     `nivartanam buf[0]` — read an integer out of a scratch
     buffer): evaluate (integer in a register), check (not
     block-kind — allowed), restore (frees `buf` and all
     temporaries), return the integer. Correct — this is
     ChatGPT's K09, and it is why scalar reads out of a region
     must be allowed.
  2. *Expression allocates scratch, value IS a scratch
     pointer* (e.g. `nivartanam nirmmita(64)` written inside
     the block): evaluate, then the **check refuses** (rule C
     / K0 return rule: block-kind results are rejected). The
     restore never runs on a dangling value because
     compilation fails first. The evaluation order is not the
     problem here; the check is what makes it safe.
  3. *Expression calls a constructor* (persistent allocation):
     under lexicality, the constructor's allocations are
     persistent (not textually inside the block), so the
     scratch restore does not touch them. Correct, and this
     is exactly why the lexical settlement matters for this
     question too.
  4. *Expression allocates scratch and hits scratch
     exhaustion mid-evaluation:* `nirmmita` returns 0 (the
     scratch policy, §3.3 of ROUND-62). The expression
     computes with 0 exactly as it would under today's
     0-contract; the check then applies to the computed value
     as usual. No new problem — exhaustion during evaluation
     behaves like exhaustion anywhere else.

So: **Gemini's worry is valid against the loose slogan and
invalid against ChatGPT's precise sequence.** The
implementation spec must therefore state the order
explicitly — "evaluate, check, restore, jump" — and not the
slogan "restore before the return", because an implementer
reading the slogan could place the restore before evaluation
and introduce Gemini's bug. The 14-byte emitter (via `r11`,
preserving `rax`/`rdx`) implements the correct order; the
`prasar` arm needs the same order (evaluate the failure
payload, check, restore, then the epilogue), and the
`yadi dosh` handled-failure arm must NOT rewind at all
(failure handled inside the region stays inside it).

One separation that must be kept clean: Gemini's
evaluation-order worry is **different** from the rule-D hole
(`nivartanam helper(buf)` where `helper` returns its
argument). In the latter, the order is correct (helper runs
before the restore) but the check is blind to the call result
(kind none) — so the restore dangles a value the check
allowed. That is a check-completeness problem (§3), not an
evaluation-order problem, and conflating them would let each
side claim the other side's issue is solved. They are solved
separately: order by the sequence above, call blindness by
K0's rejection of reference results (§3).

### 2.2 What banning would cost (lens 4, measured)

Gemini's points 1 and 3 are true: banning is simpler (two
fewer lines of compiler code, no return-edge restore), and it
breaks zero existing programs (the block is new). But the
cost is expressiveness for future code, and it is large —
measured on current main (same method as ROUND-62 §5.1,
same-line blocks included):

| `nivartanam` | Count |
|---|---|
| Total in `lib/` + `examples/` + `tests/` `.sm` | 909 |
| Inside an inner block | **444 (48.8%)** |
| — inside a `yadi` guard | 366 (82.4% of inner) |
| — inside a loop body | 75 (16.9% of inner) |
| — inside another block | 3 |
| Functions with ≥ 1 inner `nivartanam` | 215 / 1,032 (20.8%) |

Nearly **half** of all returns sit inside a block, and over
four-fifths of those are guard returns (`yadi (b < 2) {
nivartanam 0 }` — the dominant early-return style in `lib/`).
Banning `nivartanam` inside blocks would forbid the guard
pattern inside every block: a programmer writing a block
around a request handler could not early-return on a bad
input without restructuring into a flag-and-fall-through
shape, and 1 in 5 functions would need that restructuring
wherever a block is added. That is not a small cost — it is
a tax on the block's primary use case (request/loop bodies
with guards). Allowing costs 14 bytes per return-in-block
plus the return-value check, and it preserves the language's
existing early-return style. **Verdict: allow**, with the
explicit evaluate→check→restore→jump order above. Gemini's
ban would be the right call if the order could not be made
safe; it can, so the ban's simplicity is not worth its
expressiveness cost.

## Item 3 — the check: one converged rule set (K0), priced, with zero bytes for block-free programs

### 3.1 The convergence

The disagreement, stated exactly: **what to do with
UNKNOWN** — a call result, a load from unverified memory, an
indirect call, a value whose origin the checker cannot prove.

- **ChatGPT's K0 (R135): unknown = rejection** (compilation
  error, with an explicit unsupported-operation diagnostic).
  The checked subset is closed: fixed-size scalar scratch,
  immutable reference bindings, constant offsets, scalar-only
  buffers, verified value-only callees, scalar returns. What
  does not fit is rejected — and remains usable *outside*
  the construct (legacy path untouched).
- **Claude's rules A–E (R62-00): unknown = allow** (kind
  none), plus a debug fail-stop (no-rewind + `mprotect`).
  More permissive, cheaper — and unable to claim the
  guarantee, because an allowed unknown is an unchecked
  escape path.
- **Gemini's "documented contract":** the check's boundary
  must be documented — what is admitted, what is rejected,
  and what the guarantee covers — rather than implied.

**Converged rule set: K0, documented as a contract.** The
convergence is not a compromise that splits the difference
(allow *some* unknowns would reintroduce the hole); it is
the recognition that Gemini's documentation requirement and
ChatGPT's rejection rule are the *same* answer from two
sides: the contract **is** the list of what K0 admits and
rejects, and the rejections are explicit diagnostics, not
silent allowances. A programmer whose code does not fit K0
gets a diagnostic naming the unsupported operation and keeps
working outside blocks — that is the documented contract in
action, and it is friendlier than a silent allowance that
dangles in release builds.

This repositions, but does not discard, the other two
designs:

- **Claude's rules A–E become the K1 direction, not step-4
  v1.** Claude's skeleton (kind list, kind propagation,
  assignment/store/return hooks, pre-scan) is correct as far
  as it goes; K0 is the same skeleton with the holes closed
  by restriction (no pointer stores even in-region, no
  dynamic sizes, no call results, whole-function checking,
  immutable bindings — which also dissolve the loop-carried
  problem: a binding cannot *become* a pointer later in a
  loop if rebinding is rejected). K0's strictness is what
  buys its soundness argument (§3.3 of R135, by induction
  over admitted operations); Claude's permissiveness is what
  costs it.
- **My ROUND-62 retain-table proposal is revised: it belongs
  to K1, not K0.** I proposed a static table of retaining
  library functions to close rule D cheaply. Under K0 that
  table does not belong: K0 rejects *all* reference arguments
  (even to verified non-retaining helpers), because admitting
  a buffer pass requires a verified summary of the callee
  body *and all transitive callees* — which is exactly the
  call-graph verifier K0 deliberately avoids in v1. A retain
  table is sound only with that verifier, so it is K1 work
  (ChatGPT's "later K1 could admit borrowed-buffer functions
  with checked summaries"). Stating this correction plainly:
  my R62 proposal was right that the table is cheap to
  *write* and wrong that it preserves K0's argument — it
  preserves a *different, weaker* argument (verified summaries)
  that K0 does not make. K02 (`suchi_khip(outer_list,
  region_pointer)` must be rejected) passes under K0 by
  rejection of the reference argument, not by the table.

### 3.2 The converged rules, each with catches and lets-through

Adapted from K0's transfer table (R135 §4.4), stated as the
single rule set for step 4 v1. "Reject" means a compilation
error with an explicit unsupported-operation diagnostic and a
line number (the `pankti N` path — the slice refusal's
missing line number must not be repeated).

| Operation | Rule | Catches / refuses | Allows |
|---|---|---|---|
| Numeric literal / scalar input | Scalar; arithmetic never manufactures a Reference | Dereferencing a number, even if it equals an address | Ordinary arithmetic, counters, sums |
| Direct `nirmmita(C)`, constant C | Reference to a fresh scalar-only C-byte object; owner from the lexical site; possibly null | Unknown/overflowing/dynamic size in K0; treating the result as a plain integer | Constant-size persistent or scratch allocation, with failure handling |
| `vitti q = p` (Reference) | Copy the full abstract Reference (owner, object, extent, offset); destination lifetime must be contained; binding immutable thereafter | Alias to a longer-lived binding; later rebinding / class-changing assignment | Same-region/deeper local alias |
| `p + constant` | Require non-null base, constant offset within the object; retain owner/object/extent | `outer = note + 64`; out-of-object offset; wrapped offset | Bounded interior reference in a permitted local |
| Other arithmetic/bit ops on a Reference | Reject in K0 | XOR masking, float conversion, truncation, split/recombine address schemes | Scalar arithmetic on scalar operands |
| Reference `==` / `!=` 0 | Null test; yields Boolean; establishes a non-null fact on the continuing path | Treating an address comparison as scalar permission | Allocation-failure guards |
| Scalar assignment | Require scalar source; destination stays scalar | Assigning a reference into an integer slot as a disguise | Mutable scalar state |
| Scalar read through a Reference | Require live owner, non-null fact, static bounds; scalar-only invariant yields Scalar | Loading an address from unverified memory and treating it as safe | Reading numeric contents, returning/copying the number |
| Memory store | Require scalar-only destination, Scalar source, static bounds | Pointer retention in ANY memory object, even an inner one; local-alias store to outer storage | Numeric writes to proved buffers |
| `likh8`, byte-copy, field/slice/aggregate without checked lowering | Reject | Storage or reload evading the scalar-only invariant | A later explicitly verified intrinsic |
| Direct call | Verify value-only summary (scalar params, scalar result, no retention, no globals, no asm); result is the verified kind | `helper()` with unknown/pointer return; retaining `helper(p)` — including `suchi_khip`, whose integer return does not prove non-retention | Verified numeric helpers; checked helpers using only their own region |
| Return / `siddhi` / `dosh` payload | Require Scalar in K0; then emit cleanup (evaluate → check → restore → jump) | Direct/derived/wrapped reference returned from any exited region; persistent pointer returns also refused in this profile | Scalar success, scalar failure, numeric return |
| Unknown indirect call, FFI, `yantra` | Reject anywhere in the checked function unless a separately specified trusted intrinsic | Hidden retention, guessed addresses, callback escape, cleanup bypass | None in K0; legacy usage remains outside the construct |

**What K0 lets through — stated, not hidden:** nothing
through the check itself (that is the point of rejection over
allowance). What it does *not* cover, by design: arbitrary
unmodified raw code outside the checked function (a legacy
routine can guess an address independently — K0 is not a
whole-program sandbox, and claiming otherwise would be
dishonest); the debug fail-stop's role (§3.4) is to catch
misuse during development, not to extend the guarantee.
K0's soundness argument (R135 §5) holds by induction over
admitted operations only — and that boundary is the contract.

**Whole-function scope (K0 §4.2, endorsed).** K0 checks the
whole function containing a block, not just the block —
because checking only the block while the same function
reinterprets an exported number as an address afterward
proves nothing. Functions without a region keep the ordinary
language unless they opt in as verified K0 helpers. This is
stricter than Claude's block-scoped check, and it is the
reason K0 needs no pre-scan: immutable bindings + whole
function scope dissolve the loop-carried case rather than
patching it.

### 3.3 Pricing — and why ChatGPT's number is bigger than Claude's

| | Claude (R62-00) | K0 (R135) |
|---|---|---|
| Step 3 (block + lowering) | ~310 lines | 150–250 (identities/slots) + 180–320 (lowering/hooks) |
| Step 4 (check) | ~270 lines | 150–280 (values) + 180–350 (memory/bounds/null) + 180–350 (calls/summaries) + 120–250 (diagnostics/glue) |
| **Steps 3–4 total** | **~580** | **960–1,800** |

The gap is not a disagreement about counting — it is a
difference in what is being built. Claude's ~580 prices a
check that **allows** unknowns (kind none), allows pointer
stores into same-region containers, allows dynamic sizes,
and checks only the block. K0's 960–1,800 prices a check that
**rejects** unknowns, enforces scalar-only buffers with
static bounds and definite null facts, checks the whole
function, and verifies call summaries with a cache. You do
not get K0's guarantee at Claude's price, and you do not get
Claude's permissiveness at K0's price. **Budget for steps
3–4: 960–1,800 NASM lines** (ChatGPT's range, endorsed as
the realistic budget for the converged check), excluding
steps 0–2, test fixtures, Windows allocator work, and K1.
If the owner wants the cheaper check, the decision must name
the holes it accepts (rule D, memory laundering,
container-read laundering, dynamic sizes) — it must not
claim K0's guarantee at the cheaper price.

**Per-operation price (compile time; emitted provenance
instructions are zero — all decisions are compile-time):**
scalar assignment, one class check; alias binding, metadata
copy + lifetime test + rebinding rejection; constant offset,
class/null/range/overflow checks; verified call, summary
lookup + ~4–10 per argument; unsupported operation,
diagnostic, no code emitted. **Emitted code for lowering:**
2 instructions at entry, 2 per exit path (collapsed to the
outermost mark — R135's "2 per exited region" is the
conservative upper bound; for pure cursor restore the tight
figure is 2 per exit path, §2.2 of ROUND-62). The exit cost
is on exit paths, not in loop bodies' hot code — except
`agrim`, where 2 instructions per continue is the price of
the loop pattern itself.

### 3.4 Zero extra bytes for programs that do not use a block — confirmed structurally, to be verified by the guard

The brief asks to confirm the guard stays at 0 DIFFER. What
can be confirmed now, without an implementation, and what
cannot:

- **Structurally confirmed:** every step-3/4 hook is gated
  on block presence (`r62_depth > 0` in Claude's terms; K0's
  whole-function opt-in in ChatGPT's). A program containing
  no `kshetra` block takes no hook, emits no mark, no
  restore, no check code. The keyword itself breaks no
  existing program's identifiers: a full-tree grep for
  `kshetra` as an identifier in `lib/` / `examples/` /
  `tests/` code returns **zero** uses (excluding the field
  diagnostics themselves and the r23 assertions about them).
  Out-of-tree user code using `kshetra` as an identifier is
  the residual risk — which is why ChatGPT's R134 §4
  recommends a contextual construct over a global reservation
  where possible, and why the guard must include a
  `kshetra`-as-identifier legacy program (K25) if the keyword
  is reserved globally.
- **The one caveat, stated:** hidden mark locals can move a
  user variable from a register to the stack — but only in
  functions that *contain* a block (Claude). Block-free
  functions are unaffected by construction, so the guard's
  0 DIFFER for the 577 block-free programs follows from the
  gating, not from hope.
- **What the guard must still verify (cannot be confirmed by
  argument alone):** that the gating is actually implemented
  as specified — i.e., run the guard with the hooks in but
  before the block works, and require 0 DIFFER on all three
  paths. That run is the confirmation; this section is the
  argument that it should pass. Conflating the two would be
  exactly the kind of claim-as-completion the rulebook
  forbids.

## 4. Lens summary (all four items, counted)

| Item | Count |
|---|---|
| Field-diagnostic strings in `src/` (incl. hint) | 4 lines |
| Devanagari strings in `lang/sanskrit.sandesh` | 4 lines |
| Golden files pinning them | 5 (224, 234, 106, sandesh default + sanskrit `unknown_field`) |
| Test assertions pinning them | 2 (`tests/r23/test_capabilities.py:62,66`) |
| Library functions quoting them | 0 |
| User docs quoting them | 0 |
| Frozen-pack goldens needing change | 0 (their own scripts' words, concept translations) |
| `kshetra` used as an identifier in tree code | 0 |
| `nivartanam` total / inside inner blocks | 909 / 444 (48.8%) |
| — inside `yadi` guards / inside loops / other | 366 / 75 / 3 (loop takes precedence: a return inside a `yadi` inside a loop counts under loops) |
| Functions with ≥ 1 inner `nivartanam` | 215 / 1,032 (20.8%) |

## 5. What blocks development start now: nothing except the Sanskrit check and the reword round

- **Item 1:** specified exactly (§1). The reword round
  changes 15 touch points, needs ChatGPT's check on
  `avayava` + the Devanagari gender forms, and runs as a
  small follow-up. It does not block steps 1–4 development:
  the block implementation reserves `kshetra` and does not
  touch the diagnostic strings.
- **Item 2:** decided — allow, with the explicit
  evaluate→check→restore→jump order (§2.1). An implementer
  who reads only the slogan will get it wrong; the spec
  sentence above is the requirement.
- **Item 3:** converged — K0 as the check, documented as a
  contract (§3), priced at 960–1,800 lines, with zero bytes
  for block-free programs by gating (to be verified by the
  guard gate, §3.4).

Development of steps 1–4 together can start on this basis.
The gates from ROUND-62 still apply: ChatGPT's K01–K28
acceptance matrix (with K02 passing by rejection under K0),
the guard 0 DIFFER gate on the hooks, and the named holes
— now reduced to K0's explicit boundary (rejected code
remains usable outside blocks; no silent allowance
anywhere). The remaining named non-guarantee is the one K0
itself states: it is not a whole-program sandbox against
unmodified raw code outside the checked function.

## NOT RUN

- Windows / WSL: PE `.bss` behavior, `MEM_RESERVE` +
  chunked-commit behavior, and Windows exhaustion paths are
  analyzed from documentation and Linux measurements, not run
  on Windows (Windows is the owner's own work, per the
  brief).
- Browser automation: no browser component in this round.
- Implementation: no compiler code was changed and no
  `kshetra` program was run (the syntax does not exist yet);
  the guard was not re-run (no tree changes). ChatGPT's and
  Claude's figures cited here are their measurements and
  estimates, checked for consistency with the source (hook
  locations verified in ROUND-62; candidate-word greps run
  here) and with my own counts, not re-run as implementations.
- The Sanskrit in §1 is proposed, not checked; the Devanagari
  gender forms in particular need ChatGPT's check.
