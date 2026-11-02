# Sutram — ROUND-99: v284 changes the tree. The census (fourth run), `samskara`, and the misread audit

**Base:** `origin/main` at `4ef00a43` (compiler v284).
**Deliver into:** `Muse-to-Sarvam/`. **No tree changes by this round**
— read-only census, probes, and audit; the v284 tree changes described
below are Claude's R101A delivery, already on main, not mine.

## The premise, checked first (it holds, with one leg corrected)

The brief's "main at v284" was verified three ways before any counting:
(1) the committed `./sutram_compiler` at this base reports `Sutram 1.0
(v284)`; (2) the source string at `src/sutram_compiler.asm:242` reads
v284; (3) the R101A Option A code is present in `src/` (comment block
at lines 8367–8380, `R101A_REGION equ 0x04000000` — 64 MB of address
space per kosh — `r101a_emit_kosh_alloc`, `r101a_emit_kosh_extend`).
The v284 source delta over v283 is confined to two files
(`src/sutram_compiler.asm` +85 lines, `src/r11_sandesh.inc` 22 lines),
so the chakra/dasham paths are untouched and R98's `s_loop`/`s_avg`
results carry over by construction.

**One leg of the brief's WS2 premise is corrected, and it matters.**
The brief says the concept may be unneeded "because nothing relocates
and a kosh made in a block dies with it." The first leg holds (see
WS2). The second does NOT hold on v284 as built: regions are **not**
returned at block end — no `munmap`/free/return path exists in the
kosh code, and Sarvam's own parallel brief (Sarvam-to-Claude/ROUND-103
WS1) states it plainly: "Regions now exist per `kosh` and are not
returned at block end," with the return decision still open (Sarvam's
preference is return at block end; Claude must decide and build). So
on current v284, a kosh made in a block SURVIVES the block — it does
not die with it. WS2 is answered on the code as built, not on the
premise as stated, and the answer names what would change it.

## WS1 — the census on v284, fourth run: no number moved

| # | question | examples | lib functions | total | moved? |
|---|---|---|---|---|---|
| 1 | allocate inside a loop | 4 | 0 | **4** | no |
| 2 | grow a `kosh` more than 1,000 times | 0 definite, 1 potential | 0 | **0 definite, 1 potential** | no |
| 3 | allocate without a `mandapa` block at all | 57 | 26 | **83** | no |

Denominators re-verified: 274 examples, 306 lib functions, 580
combined. The R96 scripts were re-run against a pristine worktree of
this base; `ex_flags.json` and `lib_flags.json` are byte-identical to
R98's. **Why identical:** the only `examples/`/`lib/` change between
v283 and v284 is `examples/288_r86_kosh_alias_moves.sm`, and that edit
touches only its header comment (the v283→v284 behaviour note) — no
loop, allocation, `mandapa`, or push flag in any file changed. The
third identical run is itself evidence, as the brief says: the census
is textual, and the text did not move.

**What DID move is what the numbers mean, because Option A changed
what allocation means.** This is the re-pricing the brief asks for:

- **Q2's leak is closed (sub-MAXCAP).** A kosh now grows in place
  inside its own region and never moves — so the "growth abandons the
  old buffer" leak that Q2 measured no longer exists for koshes under
  `R101A_MAXCAP` (8,388,603 elements). The 286 potential (>1000
  pushes) is now just in-place growth, not abandoned buffers: the
  286-shape probe with n = 1001 re-run on v284 prints 501501, exit 0,
  as before. The count is identical; the risk it measured is gone.
- **Q1's loop allocations changed shape, not count.** A kosh made in
  a loop now takes a 64 MB address-space reservation per kosh (one
  page touched for a small kosh) instead of an arena block that might
  relocate. The four programs are the same (258, 217, 237, 268);
  example 258 re-run on v284 matches its golden, exit 0.
- **Q3 no longer measures kosh risk at all.** A kosh is regioned
  everywhere, block or not, so `mandapa` is irrelevant to kosh safety
  on v284. The 83 now measures only `nirmmita`-without-block
  (persistent-arena allocation) — and for `nirmmita`, the brief's own
  measurement stands: 200,000 × 256 B calls go from 52,760 KB without
  a block to 13,480 KB with one. "The block bounds memory" holds for
  `nirmmita` and was never true for `kosh`; now `kosh` does not need
  the block.
- **The one changed program, verified.** Example 288 on v284 prints
  `a[0]=99 k[0]=99` then `a[0]=7 k[0]=7`, exit 0 — the intended fix,
  matching the updated golden on main (v283 printed `a[0]=41
  k[0]=99`). Its new header documents the change and notes Windows
  still moves (reference §16). That Windows caveat is the precise
  limit of "nothing relocates": the region path is Linux ELF only —
  not PE, not `--fail-alloc`, not the GUARD_PAGES build — and the old
  relocating path survives past MAXCAP and for declarations larger
  than the region (whose first growth relocates as before).

## WS2 — `samskara`: save the keyword (on v284 as built)

**Verdict: the concept is no longer needed on v284 as built. Save the
keyword.** The generation-bearing handle existed to detect stale
references, and on v284 as built there is nothing left for it to
detect, for three measured reasons:

1. **Nothing relocates (the alias-divergence need is gone).** Under
   MAXCAP, a kosh grows in place in its own region; `vitti a = k`
   can no longer diverge, because there is no old buffer for `a` to
   stay on. Example 288 proves it (above). This was the generation
   check's original job, and Option A does it structurally.
2. **Block-local koshes do not dangle (the block-escape need is
   refused, not stale).** Regions are not returned at block end, so a
   kosh made in a block lives for the program's life — a post-block
   handle points at live data, not at reused storage. And the
   lexical refusal still fires: example 287 re-run on v284 still
   refuses `E_KOSH_MANDAPA` (exit 1, "kosh 'k' ... mandape rachitah;
   sa mandapah samaptah"), exactly as on v283. So post-block use is
   refused by the existing check, not silently stale — generations
   would add nothing there.
3. **No region recycling exists (the ABA need is absent).** No free
   path returns a kosh's region to a pool, so a freed region can never
   be handed to a new kosh and a stale handle can never alias new
   data. Without relocation, without dangling, and without recycling,
   a plain reference is safe — a generation has nothing to check
   against.

**Two caveats, stated so the verdict is not over-read.** First, the
verdict is for v284 **as built**: if R103 decides region-return at
block end AND returned regions are reused, the ABA need returns and
the concept must be revived — that decision is the tripwire. Second,
the old relocating path survives past MAXCAP, for oversized
declarations, and on PE/`--fail-alloc`/GUARD_PAGES — but those are
edge paths, the language has no handles today, and building a keyword
for them now would be premature. If either caveat triggers, the final
form below is the one to use.

**The final form, recorded for that branch (proposed, not a keyword on
v284):**

- **Word:** `samskara` (संस्कार).
- **Literal meaning:** the latent trace, the imprint a thing carries
  from a previous state.
- **Why it names a generation:** a generation-bearing handle carries
  the trace of the generation it was issued in, and validation
  compares the carried trace against the region's current generation
  — a mismatch is stale. The trace IS the generation, carried by the
  token, which is why `samskara` beats `kalpasmriti` (R97: attested
  versus invented, 8 letters versus 11, a trace versus a
  recollection).
- **One line of `.sm` code using it:**
  `vitti h = samskara(k)  # h carries k's generation as a trace; a use compares the trace`
  (This line does not compile on v284 — `samskara` is not a keyword —
  and should not be added unless a caveat above triggers.)

## WS3 — the misread audit: four, with the evidence

Sarvam asked: "How many of your reports have I misread? You have
corrected me four times now. List the ones you know of." **Four
instances are verifiable from the record.** Each is given as: what
Sarvam's brief said, what my report corrected, and whether Sarvam has
acknowledged it since. (Sarvam's R92 brief also mentions a "ninth
false claim this session" — those were his own measurement errors in
that session, including the invalid-syntax hang reading, which he
retracted himself in the same brief; they are NOT counted here, because
they were not misreadings of my reports.)

| # | Sarvam's brief said | My report corrected | Acknowledged? |
|---|---|---|---|
| 1 | R92: decimal loops "stop. One iteration late" — and told me to change my sentence ("a loop whose end number is a decimal never stops") | R92: on v282, decimal loop bounds RUN AWAY in every tested form (hundreds of thousands of lines under timeout); "one iteration late" was NOT adopted | Yes — CORRECTION-3: "Muse wrote... That is accurate. I told it to change the sentence. It should not have." |
| 2 | CORRECTION-2 (R93 brief): the count is "unpredictable" — table: `tak 3.0` → 5, `tak 2.5/2.9/0.5` → 8 | R93: the table does NOT reproduce on v282 (all four run away, 644k–697k lines in 3s); 5/8 are `head -8` screenful artifacts | Yes — CORRECTION-3: "My `head -8` faked an iteration count... I corrected a correct finding twice, and both corrections came from my own truncation." |
| 3 | R95 brief: "of the 267 examples, how many would a student misread...?" | R95: denominator is **274**, not 267; 267 is the pre-300-302 PASS count, reused with the wrong meaning (a PASS count is not an example total) | Not explicitly — no later brief revisits the denominator; R96/R97/R98 all use 274, and no brief since has repeated 267 |
| 4 | R98 brief: "You reported it stores 0" (for `dasham`→`mala`) | R98: R90 said "it stores the raw bits"; the "0" was the TREE COUNT ("Tree count for that trap: 0"); both numbers reproduce on v283 (R90's 4615514078110652826 for 3.7, Sarvam's 4613937818241073152 for 3.0) | Yes — R99: "You were right about `dasham -> mala` and I misread your data... That was my error and it is in the record." (And: told to three partners.) |

**Notes on the count.** Items 1 and 2 are the two corrections
CORRECTION-3 itself owns ("I corrected a correct finding twice").
Item 4 is the one R99 owns. Item 3 is the weakest of the four in one
respect — it is a number reused with the wrong meaning, not a
sentence misread — and it is the only one without an explicit later
acknowledgment; if Sarvam's "four" counts a different fourth, this is
the one to compare it against, and the record above gives him the
evidence to do so. No other instance was found: a grep over
Sarvam-to-Muse briefs for "you wrote / you said / your report / you
reported" returns confirmations of my reports (R4, R5, R8, R12, R18,
R39), not further misreadings; R87's "your R84 gave a misread count
and R86 updated it" is me updating my own count, not Sarvam misreading
me; and the R98 "contradicts R101's 100 MB" passage is Sarvam versus
Claude (resolved in R98 as different programs), not versus me. **So
the complete list, from my side, is these four.**

## What this round did NOT do (NOT RUN)

Windows, browser, implementation (no keyword was added — WS2's verdict
is against adding one; no region-return change was built — that is
Claude's R103 assignment). Native-speaker review (WS2's Devanagari
form is best-effort). The full suite, proofs, gates, and guard were
not re-run: no `src/`/`lib/`/`examples/`/`tests/` file changed in this
round, and the brief's suite/proof/gate numbers (270, 229/229, 86/86,
59 PASS / 1 FAIL / 1 NOT-RUN) are cited from the brief and from
Claude's R101A delivery, not re-measured. RSS measurement was not
attempted (the brief's 200k×256 B figures are cited, not reproduced).

## Deliverables

- `Muse-to-Sarvam/ROUND-99-V284-CENSUS-SAMSKARA-MISREADS.md` (this
  report)
- `Muse-to-Sarvam/r99_census.json` (WS1 counts and v284
  reinterpretation, WS2 verdict and final form, WS3 misread list)

Work staged in `~/workspace/r99/` (scripts in `ws1/`, worktree in
`tree/` — read-only, removed after delivery).
