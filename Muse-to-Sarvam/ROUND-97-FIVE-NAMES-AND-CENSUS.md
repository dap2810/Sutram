# Sutram — ROUND-97: the five names audited, and the three census numbers

**Base:** `origin/main` at `85355da6` (compiler v283, verified `--version`).
**Deliver into:** `Muse-to-Sarvam/`. **No tree changes** — read-only audit and
census; nothing in `src/`, `lib/`, `examples/`, or `tests/` was modified.

**Where this round came from.** ROUND-97 landed on main at 08:36 today
(commit `ea0e6644`, which adds only `Sarvam-to-Muse/ROUND-97.md`), after
the morning check. It is the next round after R96, and it asks for two
things: (WS1) an audit of the five names ChatGPT proposed in his R170
return, plus a view on `samskara` versus `kalpasmriti` for the handle;
(WS2) the three census numbers, by the R96 method (script, then hand-read
every candidate, then run the decisive cases).

**ChatGPT's R170 return was read for WS1 only.** R96 could not find it
(it had not landed); it has since landed as
`ChatGPT-to-Sarvam/ROUND-170-MEMORY-DESIGN.md`, and R97's WS1 is
precisely about its five names, so its name choices and justifications
(R170 lines 162–175) are checked below. Nothing else in R170 is audited
here — the design itself is not a Muse assignment.

## WS1 — the five names, four tests each

The four tests are R96's, unchanged: (1) complete attested word, not a
fragment (the project rule — `paripurna` shortened to `purn` loses `pari`
and is rejected); (2) no collision with an existing keyword, library
function, or `.sm` identifier; (3) typeable and memorable for a student
whose first language is not Sanskrit; (4) literal meaning describes the
thing, not an English concept wearing Sanskrit clothes.

**Collision method (measured, not judged).** Word-boundary grep for all
six words (the five plus `samskara`) over `src/`, `lib/`, `examples/`,
`tests/`, `tools/`, and `docs/` on the R97 base, plus a full-repo
substring grep and a Devanagari-form grep. **Result: zero code
collisions for all six** — no keyword, no library function, no `.sm`
identifier, no diagnostic string. The only hits anywhere are prose, and
they are assessed per word below, not hidden. Lengths are ASCII letters.
The current longest keywords are `nivartanam` and `parikshita` (10
letters each) — that is the bar a new keyword is measured against.

### `kalpa` — epoch — PASS-WITH-CAVEAT (R96's verdict, unchanged)

1. **Complete?** Yes — full noun, कल्प.
2. **Collision?** None in code. Prose only: Sarvam's R170 brief lists it
   as a candidate, and `vikalpa` (alternative/choice) appears in a
   ChatGPT vocabulary TSV — a different word that merely contains
   `kalpa` as a substring, not a collision.
3. **Typeable?** 5 letters, easy; moderately familiar.
4. **Meaning?** An eon, a cosmic age (a day of Brahma) — an age, yes,
   but a cosmic-scale age, not a generation that increments on every
   free/reuse; and the ritual-manual second meaning (Kalpa-sutra) is a
   distraction in a memory context.
   **Checked against ChatGPT:** his gloss ("an attested long
   period/cosmic age... for one validity period between resets, not
   elapsed clock time") is accurate as far as it goes, but it does not
   remove the scale caveat: a validity period between resets is a
   small, frequent thing, and `kalpa` names a cosmic one. It works;
   it is not the best epoch word. **Standing note (not a re-pick):**
   R96's `yuga` (an era at the right scale, 4 letters, no cosmic or
   ritual baggage) remains the stronger epoch word. ChatGPT's own
   line 171 concedes the point in form: "kalpa and yuga are full words;
   choose one epoch label, not both. kalpa is the selected metaphor,
   not the only linguistically possible one."

### `visarjana` — release for reuse — PASS (R96's verdict, unchanged)

1. **Complete?** Yes — full noun, विसर्जन.
2. **Collision?** None in code. Prose only: the R170 brief lists it.
3. **Typeable?** 9 letters, manageable; familiar from Ganesh
   `visarjan` (letting go / immersion) — and the familiarity helps
   here because the familiar sense IS the meaning.
4. **Meaning?** Letting go, sending away, dismissal, release. Precise
   for the act the programmer performs: the region is let go back to
   the pool. It does NOT mean reuse — and that is correct, because
   reuse is what the pool does later.
   **Checked against ChatGPT:** his gloss ("sending forth/dismissal,
   also giving up. Names the ending of this ownership, not a promise
   to return pages to the OS. Reuse is what the allocator may do
   afterwards") is exactly right, and the "not a promise to return
   pages to the OS" precision is a genuine improvement on a bare
   "release" gloss. No correction.

### `parimita` — finite budget — PASS (R96's verdict, unchanged)

1. **Complete?** Yes — full adjective/participle, परिमित
   (`pari` = around + `mita` = measured).
2. **Collision?** None in code. Prose only: the R170 brief lists it.
3. **Typeable?** 8 letters, manageable; less familiar in everyday
   speech (classical word), but regular (`pari` + `mita`) and
   unambiguous.
4. **Meaning?** Measured, limited, bounded, finite. Precise: a region
   with a measured limit.
   **Checked against ChatGPT:** his gloss ("measured, limited.
   Describes an actual enforced byte budget. It must fail closed, not
   fall back beyond the limit") is accurate, and the fail-closed
   condition is the right one for a budget word — a `parimita` region
   that silently exceeds its limit would make the word a lie. No
   correction.

### `ananta` — unbounded — PASS as a word; AGREE with the mode rejection

1. **Complete?** Yes — full adjective, अनन्त (`an` = not + `anta` =
   end). (Variant spelling अनंत exists; the project form would be
   `ananta`.)
2. **Collision?** None in code. Prose only: the R170 brief lists it,
   and `anantaram` (afterwards) appears in a ChatGPT style document —
   a different word that merely shares the `ananta-` prefix.
3. **Typeable?** 6 letters, easy; familiar (common name; Ananta, the
   endless serpent).
4. **Meaning?** Endless, infinite, without end. Precise for
   "unbounded" as a description.
   **The mode question (this is what R97 is really asking).**
   ChatGPT rejects `ananta` "as a shipped allocator mode: physical
   resources and counters are finite. At most a documentation label
   for 'no user-specified cap,' still subject to machine limits."
   **I agree with that rejection.** A mode is a discipline the
   allocator enforces; "no cap" is the absence of a discipline, not
   one, and shipping it as a mode would promise infinite memory,
   which is false. Where `ananta` survives is as a descriptor and as
   the bounded/unbounded pair value beside `parimita` (limited vs
   endless) — R96's PASS — and as ChatGPT's own fallback: a
   documentation label for "no user-specified cap, still subject to
   machine limits." So: word PASS, shipped-mode REJECT. That is
   consistent with R96, which passed `ananta` as an unbounded region
   and never addressed the mode question; R97 addresses it, and the
   answer is that ChatGPT is right.

### `kalpasmriti` — generation-bearing handle — REJECT

1. **Complete?** NO, not as a lexical item. It is a novel compound,
   `kalpa` + `smriti` ("recollection/memory of an epoch"). ChatGPT
   himself concedes this (R170 line 166: "A **proposed compound**...
   Not claimed as an attested ancient technical noun or a full
   history log"; line 168: "a naming candidate, not linguistic
   sign-off"). A student cannot look it up; there is no dictionary
   entry to check it against. Its sandhi is straightforward
   (`kalpa` + `smriti` → `kalpasmriti`), but straightforward
   composition is not attestation — any two nouns can be compounded,
   and the project rule tests for complete attested words precisely
   so that new keywords are checkable.
2. **Collision?** None — zero hits anywhere in the repo, code or
   prose. That is the one clean test it passes, and it passes it by
   being invented: nothing collides with a word nobody has used.
3. **Typeable?** 11 letters — plainly too long. It would be the
   longest keyword in the language (current longest: `nivartanam`,
   `parikshita`, 10). A handle word is typed on nearly every use; an
   11-letter novel compound is a typing burden and a memory burden
   for a student whose first language is not Sanskrit, with no
   familiar form to lean on.
4. **Meaning?** "Memory of an epoch" is explicit about WHAT is
   remembered, but it says nothing about validation — and validation
   is the handle's job. A memory is held, not checked. The handle
   must answer "is this token still current?"; `kalpasmriti` names a
   recollection, not a check. It also over-promises in the other
   direction: "memory of an epoch" sounds like a record of past
   epochs, which ChatGPT himself disclaims ("not... a full history
   log... only identity and validity data are stored").
   **Verdict: REJECT for the handle.** It fails test 1 (not attested)
   and test 3 (too long), and test 4 is weaker than it looks: the
   explicitness is about the wrong thing (what is remembered, not
   whether the token is valid).

### WS1 summary table

| word | concept | letters | complete? | collision? | verdict |
|---|---|---|---|---|---|
| kalpa | epoch | 5 | yes | none (code) | PASS-WITH-CAVEAT |
| visarjana | release | 9 | yes | none (code) | PASS |
| parimita | finite budget | 8 | yes | none (code) | PASS |
| ananta | unbounded | 6 | yes | none (code) | PASS as word; REJECT as shipped mode |
| kalpasmriti | handle | 11 | no (novel compound) | none (invented) | REJECT |
| samskara | handle (see below) | 8 | yes | none (code) | PASS-WITH-CAVEAT (handle only) |

## Is `samskara` a better word than `kalpasmriti` for the handle? Yes — and here is the argument

**Yes. `samskara` is better than `kalpasmriti` for a
generation-bearing handle, on all four tests.** This is the direct
answer to R97's question, and it is argued, not merely asserted:

1. **Attested versus invented.** `samskara` (संस्कार) is a classical
   word with a standard philosophical sense: the latent trace, the
   imprint a thing carries from a previous state. That is what a
   generation IS — the brief's own gloss says so ("`samskara` is the
   latent trace a thing carries from a previous state - which is what
   a generation IS"). `kalpasmriti` is a compound ChatGPT himself
   declines to claim as attested. A keyword should be checkable in a
   dictionary; `samskara` is, `kalpasmriti` is not.
2. **Length.** 8 letters versus 11. The handle word is the most
   frequently typed of the five; the shorter attested word wins.
3. **Meaning — the trace is the mechanism.** A generation-bearing
   handle works by carrying the trace of the generation it was issued
   in; on use, the trace is compared against the region's current
   generation, and a mismatch is stale. `samskara` names exactly that
   carried trace. `kalpasmriti` names a recollection of an epoch,
   which describes what is stored but not what is compared — and its
   explicitness (it says "epoch") does not help, because the check
   compares generations, not recollections.
4. **ChatGPT's objection, answered.** His line 172 says `samskara`
   "is not a fresh synonym for a generation counter merely because
   impressions/history are associated with the word" and that it
   "removes less ambiguity than an explicit epoch-memory compound."
   The first half is true and beside the point: `samskara` is not
   proposed as a synonym for a generation *counter* (a number), but
   as the name for the *trace the handle carries* — and for that,
   the impression/trace association is not incidental, it is the
   meaning. The second half gets the ambiguity backwards:
   `kalpasmriti` removes ambiguity about WHAT is remembered, but it
   adds ambiguity about WHAT THE WORD IS (a new compound with no
   dictionary entry, no familiar form, and a "memory" sense that
   over-promises a history log). `samskara`'s ambiguity is the
   opposite kind: its secondary senses (rite, sacrament, refinement)
   are known, established senses that do not compete in a memory
   context — the same argument R96 made for `mudra`'s dance-gesture
   sense being secondary. Known secondary senses are manageable;
   invented primary senses are not.
5. **Two earlier rejections do not apply — stated so they are not
   mistaken for applying.** ChatGPT's R132 rejected `samskara` for
   STALE BYTES (residual content in recycled memory) — a different
   meaning from the generation trace, and R132 itself acknowledges the
   philosophical trace sense as real. `docs/decisions/MEMORY-DESIGN.md`
   lists `samskara` as "uncertain. May be romanticising" — again for
   the residue meaning, not the handle meaning. Neither rejection
   touches the handle use.
6. **The never-both rule is satisfied.** R96's constraint stands:
   `samskara` must never serve both epoch and handle. Here it serves
   handle only; epoch is `kalpa` (ChatGPT's choice) or `yuga` (R96's
   recommendation). The two roles stay in distinct words, so a student
   reading `samskara` always knows it means the carried trace, never
   the era.
7. **One honest qualification.** R96's `mudra` (a seal: a mark that
   must match to be trusted, a broken seal = stale) still beats
   `samskara` for the handle on validation semantics — a seal
   carries the check in its meaning in a way a trace does not quite.
   But that is a comparison with `mudra`, not with `kalpasmriti`.
   **Between R97's two candidates, `samskara` wins clearly.** If
   Sarvam adopts ChatGPT's five wholesale, the one substitution I
   would press is `samskara` for the handle in place of
   `kalpasmriti`.

## WS2 — the three census numbers

**The numbers, cleanly, as asked:**

| # | question | examples | lib functions | total |
|---|---|---|---|---|
| 1 | allocate inside a loop | 4 | 0 | **4** |
| 2 | grow a `kosh` more than 1,000 times | 0 definite, 1 potential | 0 | **0 definite, 1 potential** |
| 3 | allocate without a `mandapa` block at all | 57 | 26 | **83** |

Denominators: 274 examples, 306 lib functions, 580 combined — the same
denominators as R96, re-verified on this base (274 top-level
`examples/*.sm`, 306 `prakriya` functions in 24 `lib/*.smlib` modules).

**Method (R96's, re-run, not cited).** The R96 scripts (`scan.py`,
`loop_bodies.py`, `loop_local.py`) were re-run against a pristine
worktree of this base (`origin/main` at `85355da6`). Script outputs
are byte-identical to R96's (`ex_flags.json` identical, `lib_flags.json`
identical) — and that identity is itself verified, not assumed:
`git diff` between R96's base (`bc5c40ce`) and this base over
`examples/` and `lib/` is EMPTY (the FIXALL delivery added only outbox
files; its code changes were a review patch, never applied to main).
So the candidate sets are identical, and the hand-reads below
re-verify every counted case rather than re-citing R96's reads.

**Q1 — 4 programs allocate inside a loop (all examples, all bounded).**

| program | loop (bound on own inputs) | allocation | calls/allocs on own inputs |
|---|---|---|---|
| `258_r70_loop_indent.sm` | three `yavat` loops | `nirmmita(64)` in each loop body | 3 + 3 + 1000 = **1006** |
| `217_r12_report.sm` | `yavat (i < n)`, n = 8 scores | calls `ank_tak_varna` (one `nirmmita` per call) | 8 |
| `237_many_variables.sm` | `yavat (n < 2)` | calls `gahra` (two `nirmmita` + one `kosh k[1]` per call) | 2 |
| `268_r73_return_value.sm` | `yavat (k < 1000000)` | calls `varga_yoga` (`nirmmita` inside its own `mandapa` block) | 1,000,000, freed per call |

Re-verified by line reads on this base: 258's allocations sit at lines
9, 16, 33 inside the `i < 3`, `j < 3`, `n < 1000` loops (its `k < 4`
loop at line 21 allocates nothing); 217's loop at line 50 calls
`ank_tak_varna` at line 51; 237's loop at line 81 calls `gahra` at
line 82; 268's loop at line 23 calls `varga_yoga` at line 24, whose
`mandapa` opens at line 5 — so its million calls do NOT grow memory
without bound (per-call scratch freeing). Lib Q1 = 0: all 26 lib
allocating names checked against every lib loop body, zero hits; the
one interleaved lib case, `aadhar::brihat_ank_tak` (`nirmmita` at lines
32 and 45, loops at 35, 49, 55, 66), was re-read — line 32 allocates
before the first loop, line 45 after the first loop closes and before
the second opens. Q1b (kosh declaration inside a loop) = 0 in both
trees, re-verified. **Zero unbounded loop allocations in the tree.**

**Q2 — 0 definite, 1 potential (all examples; lib grows no kosh at all).**

Every kosh in the tree grows far fewer than 1,000 times on its
program's own inputs (largest: 100 pushes, 286; next 22, 299; all other
push-in-loop programs fixed at 6–21). The one potential case:
`286_r82_kosh_in_mandapa.sm`, whose `varg_yog(n)` pushes exactly `n`
times into its `mandapa`-local kosh `k` (`yavat (i <= n)`,
`kosh_push(k, i * i)`) — called with 10 and 100 on its own inputs, but
any input with n > 1000 would grow `k` past 1,000 times. Lib Q2 = 0:
the three modules whose names match a `kosh_push` grep contain push
mentions only in `#` comment lines; zero `kosh_push`/`kosh_enqueue`
in lib code. `kosh_enqueue` is used nowhere in the tree.

**Decisive case (new in R97 — the potential is now RUN, not just read).**
A probe mirroring 286's shape exactly (`mandapa` block, `kosh k[2]`,
`yavat` push loop, value returned from outside the block) was run with
n = 1001 on v283: it printed **501501** (the sum 1..1001, proving all
1001 pushes landed and all elements read back) and exited 0. So the
potential is real — growth past 1,000 works, it is not refused — and
it is also bounded by the caller's n, not a runaway. The two R96 sanity
probes were re-run on v283 with the same results: `chakra i = 0 tak
3.0` refuses `E_CHAKRA_DASHAM` (line 2:22, no binary produced), and
`dasham avg = 15 / 4` prints `3.000000`, exit 0. Example 258 was also
run standalone: output matches its golden byte-for-byte, exit 0 (its
1006 allocations complete, as counted).

**Q3 — 83 programs allocate without any `mandapa` (57 examples + 26 lib).**

The 26 lib functions are exactly the 26 `nirmmita` functions (lib has
zero `mandapa` and zero kosh declarations). Examples adopt `mandapa`
in only 14 of 274 files, all of them memory/escape/`parikshita` tests
written to test `mandapa` itself. The Q3 lists are the script outputs
(re-run, identical to R96's); the full per-program lists are in
`r97_census.json`.

**Interpretation (the decision number).** The brief's reading applies
to Q1 and Q2, not Q3 — and Q1/Q2 are near zero in the sense that
matters: **zero unbounded loop allocations, zero kosh growths past
1,000 on any program's own inputs, one input-dependent potential
(now run-confirmed at 1001).** The memory gaps are therefore
theoretical for our own code, exactly as the 3-1-0 alias census settled
that question: a user program *could* write an unbounded allocating
loop or a >1000-push kosh, and those gaps are real for user code, but
no tree program demonstrates either, and the largest bounded cases are
deliberate tests (258's 1006 allocations, 286's parameterized push
loop). Q3's 83 is large and is reported honestly, but it measures low
`mandapa` adoption, not risk: a program that allocates once at the top
and never in a loop is not a growth risk merely for lacking a block.
**So: the `kosh` leak is documentary for the tree, not urgent** —
urgent would require a tree program that grows without bound, and
there is none. (Whether `mandapa` exit reclaims buffers abandoned
during growth inside the block — 286's shape — is still not determined
by this census; no RSS measurement is claimed here, and Claude R101's
finding that a block does NOT hold `kosh` at ~100 MB stands as the
live evidence on that question.)

## What this round did NOT do (NOT RUN)

Windows, browser, implementation (none of the five names has been added
to the compiler; the `.sm` lines in R96/R170 remain proposals, and no
line using `kalpa`, `visarjana`, `parimita`, `ananta`, `kalpasmriti`,
or `samskara` as a keyword has been compiled). Native-speaker review:
this audit is NOT a native-speaker check — all Devanagari forms and
literal meanings are best-effort from standard Sanskrit vocabulary and
must be confirmed by a native speaker before any word ships, as the
project requires for transliterations. The full suite, proofs, gates,
and guard were not re-run: no `src/`/`lib/`/`examples/`/`tests/` file
changed in this round, and the tree is byte-identical to R96's base
over `examples/` and `lib/`, so R95's suite PASS=270 /
NO-EXPECTATION=4 stands on that basis, cited not re-run. RSS
measurement was not attempted (the brief's own verified behaviour and
Claude R101's measurements are cited, not reproduced).

## Deliverables

- `Muse-to-Sarvam/ROUND-97-FIVE-NAMES-AND-CENSUS.md` (this report)
- `Muse-to-Sarvam/r97_census.json` (WS1 verdicts, WS2 counts and
  per-program lists, decisive-run results)

Work staged in `~/workspace/r97/` (scripts in `ws2/`, probes in
`ws2/probes/`, worktree in `tree/` — read-only, removed after delivery).
