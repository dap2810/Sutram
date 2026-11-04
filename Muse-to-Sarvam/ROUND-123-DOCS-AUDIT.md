# Muse Round 123 — Do the docs describe v297, or a language that no longer exists?

- **Base:** main at v297 (`c803cc07`, compiler `Sutram 1.0 (v297)`).
- **Deliverables:** this report, `r123.json`, `r123_docs.md` (full audit, 557 lines).
- **Scope:** every file in `docs/` (117 files) plus all 6 root `*.md` files, by grep
  plus context-read of every hit in a living doc. The collaboration folders
  (`Claude-to-Sarvam/`, `ChatGPT-to-Sarvam/`, `Muse-to-Sarvam/`, `Sarvam-to-*/`,
  `Windows-to-Sarvam/`) were NOT audited as living docs — they are historical
  records. Inside `docs/`, `decisions/`, `reports/`, `rounds/`,
  `ai-handoff-notes/` and `CHANGELOG-ARCHIVE.md` were likewise classified as
  historical records: their old-token/old-name quotes are version-pinned history,
  not findings, and must not be rewritten. Round 119 findings (MEMORY-MODEL whole
  file, LANGUAGE-REFERENCE §16 `:958,961` and escape prose `:1162,1195,1227`,
  VOCABULARY-TABLE `:108`, OPEN-ISSUES `:86`, `_newchapter_en.html`) were
  re-verified as still present on v297 and are carried forward, marked as such;
  everything below marked NEW is new to this round.
- **Audit only.** No doc was edited, no code was changed, nothing was pushed or
  merged by this round.

## Headline: the docs mostly describe v297 — with four live lies, one missing paragraph, and one wrong count premise

The language changed enormously in two weeks (22 builtins renamed, `asti`/`nasti`
added, `Sutram Error` became `Sutram truti`, `sankhya_bindu` withdrawn, 15 library
contracts now refuse, `patra_asti` still broken). The audit's headline is
reassuring on the token and the withdrawal, and damning on the names, the
library table, and the Windows paragraph.

## WS1 — The six checks, file and line

### (1) Does it still say `Sutram Error` where the compiler now says `Sutram truti`? NO living doc does this.

Every hit is an explicit historical quote ("up to v293 it was…", "a program
built by v293 or earlier still prints…"). The current token `Sutram truti` is
used consistently (`LANGUAGE-REFERENCE.md:222-233`, `:933`, `:1232`, `:1333`;
`SPECIFICATION.md:158`). Documented exception: the linker still prints
`Sutram Error` (`decisions/R114-SUTRAM-TRUTI.md:30`) — a current compiler fact,
not a doc error. One footnote suggestion: `decisions/MEMORY-DECISION.md:68`
quotes the old token in a decision record and should gain a "token now
`Sutram truti`; rule unchanged" footnote. **What it should say: nothing needs
changing in any living doc on this check.**

### (2) Does it list `kosh_push` as the primary name rather than an alias? YES, in four living places (plus the Round 119 §16/escape cases).

NEW findings, each with what it should say:

- `LANGUAGE-REFERENCE.md:343-353` — a whole §4a subsection headed
  `likha_fmt(fmt, v)` with code `likha_fmt("x = ", 42)`, while `:167` correctly
  gives `likha_rup` (was `likha_fmt`). Should say: `likha_rup`, with
  `likha_fmt` noted as the retired alias.
- `LANGUAGE-REFERENCE.md:456` — an `E_KOSH_GANIT` hint says `kosh_len(k)`.
  Should say: `kosh_gan(k)`.
- `LANGUAGE-REFERENCE.md:980,1232,1240,1270` — `kosh_len(k)` / `kosh_push` in
  Windows advice, hint quotes, and the +3.5% cost note. Should say: the new
  names, with aliases noted. Caveat: `:1232` quotes a compiler hint verbatim,
  so verify the hint itself before editing the doc (if the hint still says
  `kosh_len`, the compiler message is the thing to fix, not the doc).
- The `sutram-book-*.html` kosh chapter in all six language editions
  (`sutram-book-english.html:431,680-682,684,693-694,702,706,710` — 5×
  `kosh_push`, 3× `kosh_len`, 1× `kosh_pop`, 1× `pankti_len`, no alias note).
  One shared chapter, one fix six times. Should say: the v292 names, with a
  one-line alias note.
- `sutram-stdlib-reference.html` — 11 pre-v297 names listed as current (see
  check (6)). Should say: the v297 names, or the file should be retired (see
  the fix order below).

NOT findings: `MEMORY-MODEL.md` old names (labelled R70 snapshot);
`SPECIFICATION.md:208` (`kosh_clear` emission — an inspected-emission name, not
a student-facing primary); `LANGUAGE-REFERENCE.md:933,939-940` (quote runtime
messages verbatim — accurate, and the underlying old-spelling messages are the
already-known R111-00 issue). `OPEN-ISSUES.md:86-87,92,169` and
`WHATS-LEFT.md:56-57` still list the v292-resolved vocabulary as an OPEN issue
— needs a "resolved in v292" status, not deletion.

### (3) Does it mention `asti`/`nasti` at all? Present in exactly two student-facing places; missing where it matters most.

Present: `LANGUAGE-REFERENCE.md:219` ("`asti` / अस्ति is `==` and `nasti` /
नास्ति is `!=` — the same token… byte for byte (examples 324–327)") and
`sutram-vocabulary.html:122-123` (rows: `==` → bold `asti`, `!=` → bold
`nasti`). Should mention but don't: `SPECIFICATION.md:96` (lists `== !=` with
no token note — the normative spec, highest priority), the book operator table
(`sutram-book-english.html:132`, teaches only `==`), and
`vocabulary/VOCABULARY-RULE.md` / `DERIVATION.md` (never mention the tokens).
Partial: `VOCABULARY-TABLE.md:175` / `VOCABULARY-SHORT.md:97` mention `asti`
only as a stem/boolean marker — should add "(also the `==` token since v292)".
Deliberate non-findings: `sutram-stdlib*.html`, `ERROR-CONVENTION.md`,
`NUMERIC-CONTRACT.md`, `MEMORY-MODEL.md`, `OPEN-ISSUES.md`, `README.md`,
`PROJECT-MASTER.md` are not operator references and need no token table.
(`patra_asti` and `asti_*` predicates were excluded from the counts; they are
not the tokens.)

### (4) Does the memory section mention `parimita` and `parimana`, and does it say they are Linux-only? Yes, in the reference — and nowhere else that matters.

`LANGUAGE-REFERENCE.md` §19 states both, correctly Linux-scoped: parimana
`:1287-1313`, `:1308` — "adds one counter update. **Linux ELF only; in a
Windows program it returns 0.**"; parimita `:1315-1359`, `:1352-1353` —
"**Linux ELF only, as the block.** In a Windows program a `mandapa` releases
nothing, and its budget is not checked."; general mandapa line `:1184`
("**Linux only.** … a `mandapa` is an ordinary block: everything works, nothing
is reclaimed."). Root `README.md:188,192` states both, correctly Linux-scoped.
`MEMORY-MODEL.md` mentions NEITHER word (0 hits) — but it is a labelled R70
snapshot, so the finding is the live link hazard: `LANGUAGE-REFERENCE.md:10`
links to it for "the memory question" with no "historical snapshot; current
model is §19" annotation. **What it should say: add that annotation to `:10`.**

### (5) Does it still describe `sankhya_bindu` as available? NO clean case in a living doc.

The reference `:188,217` correctly says withdrawn (v295, `E_PRATYAHRITA`,
alternative `yoj sankhyiki, bindu_gunan(a, b)`). Ambiguous/proposal cases,
which need a banner, not a silent edit:

- `sutram-vocabulary.html:120` — gloss says "withdrawn in v295" but the
  new-name column still bolds `sankhya_bindu`. Should say: struck through (as
  `:217` does), or replaced with `bindu_gunan`.
- `VOCABULARY-TABLE.md:108` (Round 119, still present) — proposes
  `sankhya_bindu` for `sankhya_dot` with zero "withdrawn" mentions in the file.
- `VOCABULARY-SHORT.md:145` — proposes a different unadopted name,
  `sankh_bindu`.

Both vocabulary tables need a "superseded by v292/v295" banner. Both stdlib HTML
files omit both names entirely — correct for a withdrawn builtin.

### (6) Does the library reference list 306 functions when there are 310? The premise needs correcting.

No v297 reference lists 306. Verified actual library: `grep -c "^prakriya "
lib/*.smlib` sums to **310** (24 modules: aadhar 2, ank 10, anukram 5, brihat 13,
chandas 6, ganit 18, ganita 27, gudh 2, kalana 6, khand 22, madhava 5, mala 8,
nighantu 17, patra 3, phal 14, roop 23, sadhan 7, samanvaya 11, sangrah 14,
sankhyiki 16, shreni 14, suchi 34, vakyank 6, varna 27).

- `sutram-stdlib.html:479` is EXACT: "24 modules, 310 functions. Generated from
  library sources." (0 missing, 0 extra by set diff.) Recommendation: add a
  "generated at v297" stamp, so the next reader knows it is current.
- `sutram-stdlib-reference.html:61,66,767` claims **303**, not 306 — a pre-v297
  snapshot, reconciled exactly (310 − 18 missing + 11 extra = 303). Missing 18:
  `asti_kramabaddha`, `bk_gunan`, `bk_kaarak`, `bk_khand`, `bk_na_adhik`,
  `brihat_shesh_sahaya`, `ekanka_gan`, `kuttaka_gun_shesh`, `meru_mala`,
  `purti_vam`, `rakh_ubhaya_bhed`, `roop_ank_upasarga`, `roop_chihna_akshar`,
  `roop_purti_dakshin`, `roop_purti_madhya`, `roop_purti_vam`,
  `samanvaya_akar_ayogya`, `suchi_asti_kramabaddha`. Extra 11 (pre-v297 names):
  `asti_sorted`, `bit_gan`, `meru_pankti`, `pad_vam`, `rakh_samroop_diff`,
  `roop_ank_pre`, `roop_pad_dakshin`, `roop_pad_madhya`, `roop_pad_vam`,
  `roop_sign_akshar`, `suchi_asti_sorted`. Per-module: ganita listed 22 vs lib
  27 (exactly the 4 `bk_*` + `kuttaka_gun_shesh`), brihat 12 vs 13, samanvaya 10
  vs 11; other counts match but swap old for new names.
- The only surviving "306" is two stale sentences: `LANGUAGE-REFERENCE.md:1396`
  ("63 of its 306 functions could be marked") and `CHANGELOG.md:368` ("0 of 306
  library functions marked, 63 eligible") — both should say 310, and the
  63-eligible count needs re-verification against 310 (whether the 4 new `bk_*`
  helpers are eligible is unstated).
- `LANGUAGE-REFERENCE.md:363-367` §4b is a misleading subset: 6 modules, "60
  functions across six modules", but even those six total 101 in lib (ganit 15
  vs 18, missing `ekanka_gan`, `ganit_yadricch`, `ganit_seemit`; ganita 6 vs 27;
  varna 13 vs 27, missing all 14 `varna_*`-prefixed functions; shreni 11 vs 14,
  missing `nivesh_shreni`, `mil_shreni_punar`, `mil_shreni`), the other 18
  modules (209 functions) are absent with no "excerpt" label, and its "at most
  two modules — the inliner's buffer overflows at three or more" limitation is
  stale (the cap bites near ~10 modules). Should say: labelled as an excerpt,
  with the current per-module counts.
- `VOCABULARY-COMPLETE.md:3` (305 at v253) is correctly pinned, not current.
- Bonus count staleness: `sutram-book-english.html:435` says "Twelve modules
  ship today" and `:715` says "Fifteen modules ship" — the library has 24.

## WS2 — The Windows gap in the docs. Answer: no single doc says both halves together, and that is the single most important missing paragraph

The halves exist 44 lines apart in §19 (`:1308` parimana returns 0;
`:1352-1353` parimita not checked), and `README.md:182-192` states release +
both features' Linux scope but never the two Windows values in one sentence.
The doc a Windows student opens first, `WINDOWS-SETUP.md` §6–§7 (`:120-149`),
mentions NEITHER parimana nor parimita (0 hits); `WINDOWS-PORT-PLAN.md` is
likewise silent. The single most important missing paragraph (drafted here as
a proposal only, not an edit) belongs in `WINDOWS-SETUP.md` §7 or as a §19
Windows box, and reads in substance:

> On Windows, `parimana()` always returns 0 and a `mandapa parimita N` budget is
> never enforced — the program still compiles and runs, so the student gets no
> error telling them the feature is absent; do not rely on either to catch a
> Windows memory problem.

This is the only finding whose absence causes silent mis-trust (a 0, a
non-refusal) rather than a warning. Version-scoping note: this paragraph is
correct for main (v297/v298); if the Windows round-4 branch (Round 124) merges,
it must be updated, because there `parimana()` and `parimita` work on PE.

## WS3 — The memory reference section and the five gaps

| Gap | Verdict | What the reference should say |
|---|---|---|
| (i) A block `kosh` outlives its block | STATED — but split across two lifetimes | Storage: `:1272-1273` ("the block does not take a `kosh`'s memory back; the `kosh` keeps it for the program's life") and `:1312` (same, "even one made in the block"). Reference: `:1223` ("lives as long as the block") + `:1225-1260` (`E_KOSH_MANDAPA` refusal). No single sentence says "storage outlives, reference must not" — a student reading either line alone misreads. Needs one reconciling sentence at `:1223`. |
| (ii) The arena is built but unmerged | OMITTED from §16/§19 | 0 hits for `claude/r108-arena-review`, "arena branch", or "unmerged". The arena appears only as parimana's counter source (`:1300,1310`). Branch status appears only in `CHANGELOG.md:43,50,117`. Needs one §19 status line ("exists on `claude/r108-arena-review`, fixed at the branch tip, not merged; §19 describes main"). Note: Round 121 finds the branch tip is NOT fixed (two defects live), so that status line must not say "fixed" without qualification. |
| (iii) No reuse inside a live block | IMPLIED, NOT STATED | §19 states reuse *across* blocks (`:1172` "A later block reuses the same memory, and sees zeros"; `:1180` "Pages are reused, not returned… the next block uses them again") and implies the bump (`:1168-1169` entry cursor, `:1171` "Every exit gives it all back"), but never states dead scratch is NOT reused mid-block. Needs one sentence ("Inside a live block there is no reuse: memory taken is held until the block ends"). Round 121 WS3 confirms no library function needs mid-block reuse, so this sentence is a limit statement, not a library complaint. |
| (iv) 64 MiB per kosh is invisible | PARTIALLY STATED | Size stated: §16 `:951-952` ("64 MB of address space, of which only the pages it touches are used") + cost paragraph (≥1 4 KB page per kosh, one `mmap`). Invisibility not stated: §19 parimana (`:1300-1306`) counts header + capacity and says "It is not the resident memory…", but never says the 64 MB reservation itself is excluded from parimana and absent from RSS until touched. Needs one clause in the "What it counts" list. Round 121 WS2 measured the numbers (64 MB VSZ, ~4 KB RSS per kosh). |
| (v) No threads | OMITTED from §16/§19 | 0 hits for thread/parallel/concurrent in the reference. The only concurrency statement in the tree is `MEMORY-MODEL.md:89,102,162` (no memory model, no happens-before, no shared-mutation discipline) — a labelled R70 snapshot, not the reference. Needs one line ("no thread model: `mandapa`, `nirmmita`, and `kosh` regions assume a single thread; concurrent use is unspecified"). |

**A gap that is documented is a limitation. A gap that is not is a surprise.**
On that test, the reference currently documents one gap fully (with a split
lifetime sentence to reconcile), one partially, one by implication, and two not
at all.

## Prioritised fix order (audit opinion only — no edits made)

1. Regenerate or retire `sutram-stdlib-reference.html` — point at the
   already-exact `sutram-stdlib.html` rather than hand-patching 29 rows.
2. Fix the two student-facing places teaching the alias as primary (book kosh
   chapter; §4a `likha_fmt` block).
3. Add the WS2 Windows paragraph to `WINDOWS-SETUP.md` §7.
4. Add `asti`/`nasti` to `SPECIFICATION.md` and the book operator table (one
   row each).
5. Label §4b as an excerpt and fix the two 306 sentences.
6. Add the five WS3 one-liners to §16/§19.
7. Status banners, not rewrites, for OPEN-ISSUES §C, WHATS-LEFT C5/C6, the
   `vocabulary/` proposal tables, and the v253 COMPLETE extraction.

## NOT RUN / caveats

No doc was edited, no compiler was run for this audit (all counts are
grep/set-diff verified against the v297 sources); whether the compiler hint
quoted at `LANGUAGE-REFERENCE.md:1232` still says `kosh_len(k)` was not verified
and must be checked before that line is edited; the 63-eligible parikshita
count was not re-measured against 310; native-speaker review of any new
Sanskrit strings is out of scope for this audit; Windows, browser, full suite
(no tree changes).
