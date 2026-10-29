# ROUND-64 — the `avayava` reword

Base: origin/main `2bc54c3a` (v415 work in progress; compiler
v261 at this base — see §5), built and verified locally.
Delivered as patch + report. **Not applied to main by this
round** — the patch awaits Sarvam's review, per the standing
delivery rule (no direct-to-main authorization in this brief).

Read first: `docs/MEMORY-DECISION.md` (owner's decision:
`kshetra` for the region, `avayava` for the member),
`docs/VOCABULARY-RULE.md` (the three rules), ChatGPT's
`ROUND-136-FINAL-DECISIONS.md` (dictionary check, masculine
nominative `avayavah`), my ROUND-63 inventory.

## WS3 first — no third collision (no STOP)

`avayava` (Latin and Devanagari अवयव) appears **nowhere**
in the compiler source, the packs, `lib/`, `tests/`, or
`examples/` on this base — a full-tree grep returns zero
hits in `src/`, `lang/`, `win/*.inc`, `tools/*.py`, `lib/`,
`tests/`, `examples/`. Its only appearances in the tree are
prose decision documents (`docs/CHANGELOG.md`,
`docs/MEMORY-DECISION.md`, `docs/VOCABULARY-RULE.md`, the
ROUND-63 report, R136, and the ROUND-64 brief itself) —
which is the decision being implemented, not a collision.
The reword proceeds.

## WS1 — the reword, with the case endings stated

Four strings, in both registers. Latin first (the default
pack, from `src/sutram_compiler.asm`):

| Line | Before | After |
|---|---|---|
| `:313` (`r5_msg_field`) | `agyat kshetra '` | `agyat avayava '` |
| `:317` (`r7_msg_field_amb`) | `kshetra '` | `avayava '` |
| `:328` (`r5_msg_field_hint2`) | `' kasyashchid api rachanayah kshetram nasti` | `' kasyashchid api rachanayah avayavam nasti` |
| `:827` (`msg_rachana_fields_overflow`) | `rachana kshetra seema atikram` | `rachana avayava seema atikram` |

Devanagari (`lang/sanskrit.sandesh`), with the grammar
stated explicitly rather than assumed:

| Key | Before | After | Case reasoning |
|---|---|---|---|
| `r5_msg_field` | `अज्ञातं क्षेत्रम् '` | `अज्ञातः अवयवः '` | Masculine nominative singular, adjective agreeing: `avayava` is masculine (R136), so the neuter `अज्ञातं क्षेत्रम्` becomes `अज्ञातः अवयवः`. |
| `r7_msg_field_amb` | `क्षेत्रम् '` | `अवयवः '` | Masculine nominative singular. The old neuter form hid nominative vs accusative (they coincide in the neuter); I choose nominative by parallel with `:313` and by subject role — the message names the field that is ambiguous. Flagged for ChatGPT's confirmation (see §4). |
| `r5_msg_field_hint2` | `' कस्याश्चिदपि रचनायाः क्षेत्रं नास्ति` | `' कस्याश्चिदपि रचनायाः अवयवो नास्ति` | Rewritten as a sentence, not a substitution (per the brief and R136): `avayavaḥ` + `nāsti` → `avayavo nāsti` by visarga sandhi before the voiced `n`. Reads: "'w' is not a member of any structure." |
| `msg_rachana_fields_overflow` | `{kw:rachana}-क्षेत्र-सीमातिक्रमः` | `{kw:rachana}-अवयव-सीमातिक्रमः` | Compound stem form, uninflected inside the compound — as `क्षेत्र` was. |

Error IDs, source locations, member identifiers, structure
layout, and pack mappings are unchanged (R136 §53). The
ambiguous-field hint (`' dvayoh rachanayoh bhinne sthane
asti...`) contains no `kshetra` and is untouched.

### The vocabulary rule (checked, not assumed)

`docs/VOCABULARY-RULE.md` passes this reword on all three
rules, and the rule table names it explicitly: (1) it
replaces an existing word and removes a named confusion ("a
member is not a region; `kshetra` said the wrong thing");
(2) it is a replacement, not an addition — no new root is
introduced for the programmer to learn, and the keyword
count does not rise (the word appears only in diagnostics);
(3) it is a compiler-reported word, so it teaches the
system while being read rather than costing the programmer
a choice. `avayava` is not a keyword, not a builtin, and not
a reserved word — no new reserved word is needed (R136).

### Frozen packs: entries untouched, comments updated

**Decision: no frozen pack entry is touched.** Reasons:

1. Frozen means frozen (`/LANGUAGE-PRIORITY.md`): a frozen
   pack's entry is changed only if it is a defect. These
   entries are not defects — they translate the *concept*
   "field/member" correctly in their own languages (8 packs
   use the क्षेत्र cognate: Bengali, Gujarati, Hindi,
   Kannada, Marathi, Odia, Punjabi, Telugu; Malayalam uses
   മണ്ഡലം, Tamil uses புலம்). The Sanskrit label changed;
   the concept did not. A frozen pack that says "field" is
   not wrong, it is older — exactly the brief's framing.
2. The Latin reword does not affect frozen-pack output at
   all: a frozen pack renders its own translation, never the
   Latin string. Changing its entries would be gratuitous
   churn in frozen files for zero output difference.
3. The count: the brief's "32 entries" is the 8 cognate
   packs × 4 keys. The full frozen surface is 10 packs × 4
   keys = 40 entries, all untouched.

**One mechanical exception, stated plainly:** the `#`
comment line above each entry in all 11 `.sandesh` files
shows the romanised Sanskrit default, and those comments
still said `kshetra` after the reword. I updated the 4
comment lines in each of the 11 packs (44 lines, mechanical
substitution only). Comments do not affect output, the
binary, or `sandesh.py --check` — but leaving them stale
would show every future reviewer a default text that no
longer exists. Note the brief's premise needed correction:
`tools/sandesh.py --write` does **not** rewrite comment
lines (verified in source: `--write` regenerates only
`src/r11_sandesh.inc` and `windows/gui/r11_ide_sandesh.inc`;
comment rewriting is the separate `--format PACK` path,
which rewrites whole files and would have produced noise).
So the comment updates here are hand-applied, not tool
output — and the tool's `--check` still passes.

### Regeneration

`python3 tools/sandesh.py --write` regenerated
`src/r11_sandesh.inc` (4 Sanskrit entries changed; the
Windows IDE inc file is unchanged — these keys are not IDE
messages). `python3 tools/sandesh.py --check` passes: 119
compiler + 23 IDE messages × 11 packs: OK.

## WS2 — the proof

- **Suite: PASS=225, NO-EXPECTATION=4** (the same 4
  no-expectation examples as on base: 215, 216, 217, 219).
- **Gates: 47 PASS / 1 FAIL / 1 NOT-RUN** — with the one
  FAIL being pre-existing and unrelated to this patch (see
  below). The brief's "48 PASS / 0 FAIL" is the R61-era
  baseline quoted in `PROJECT-MASTER.md` itself; it no
  longer matches the tree.
- **Sandesh test: 5 tests, OK.**
- **Rebuilt compiler: zero NASM warnings**, and the new
  strings verified emitting directly: default-pack output
  for `224_unknown_field.sm`, `234_ambiguous_field.sm`,
  `106_rachana_field_capacity.sm`, and `--lang sanskrit`
  output for the sandesh `unknown_field` case all show the
  new text (see §3 for the exact strings).
- **Guard (old committed compiler vs fresh build, via the
  shipped `tools/guard_pair.py`): 577 programs, 486
  byte-identical, 91 refused identically, 0 DIFFER, 0 new.**
  The identical/refused split (486/91) differs from R48's
  489/88 — verified pre-existing, not caused by this patch:
  an old-vs-old guard run on the pristine tree gives the
  same 486/91 split. Total 577 unchanged, 0 DIFFER.
- **Diagnostic-text diff (old vs new compiler, direct):**
  exactly the four diagnostics differ, line for line —
  224 (error + hint), 234 (error), 106 (error), Sanskrit
  pack (error + hint). No other compiler output differs.
  (Note: `guard_pair.py` compares program bytes and exit
  codes, not compiler stderr text — so the stderr diff
  above is a separate, direct check, not something the
  guard's 0 DIFFER covers. Both are reported so the claim
  "output unchanged except the four diagnostics" is
  evidenced at both levels.)

### Goldens changed: 5 files, text-only

| File | Change |
|---|---|
| `tests/expect/224_unknown_field.out` | `agyat kshetra` → `agyat avayava`; hint `kshetram nasti` → `avayavam nasti` |
| `tests/expect/234_ambiguous_field.out` | `kshetra 'x'` → `avayava 'x'` |
| `tests/expect/106_rachana_field_capacity.out` | `rachana kshetra seema atikram` → `rachana avayava seema atikram` |
| `tests/sandesh/expect/default/unknown_field.out` | same as 224, for `'q'` |
| `tests/sandesh/expect/sanskrit/unknown_field.out` | `अज्ञातं क्षेत्रम्` → `अज्ञातः अवयवः`; `क्षेत्रं नास्ति` → `अवयवो नास्ति` |

Note: the brief's table lists 4 goldens; the 5th is the
Sanskrit-pack golden, which changes because the Sanskrit
pack's entry changed. The Hindi and Marathi sandesh goldens
match a grep for क्षेत्र but contain their own
translations — they are frozen-pack outputs and are
**unchanged**, correctly.

Plus `tests/r23/test_capabilities.py:62,66` (the two
assertions). A full-tree grep confirms no other golden or
test asserts on the old strings. Every change in the patch
is text-only: 4 compiler strings, 4 Sanskrit entries, 44
comment lines, 5 goldens, 2 assertions, and the regenerated
`.inc` (which is the byte-encoding of the same 4 entries).

### The one gates FAIL, attributed (pre-existing)

`tools/gates.sh` ends 47 PASS / 1 FAIL / 1 NOT-RUN. The
FAIL is the doc-counts gate: `PROJECT-MASTER.md` quotes
"48 PASS / 0 FAIL / 1 NOT-RUN" and "86/86", while the
checker counts 47 gates. **This FAIL is not caused by this
patch.** Evidence: `PROJECT-MASTER.md` and `tools/gates.sh`
are both unmodified by this patch (`git status` clean for
both), and running `tools/doc_counts_gate.py` against the
same gates transcript on the **pristine** tree produces the
identical 2 impossible claims as on the patched tree. The
stale claim is the R61-era baseline (48/0/1) surviving into
a tree whose gate set has since changed; fixing that doc
claim is a separate, small round — it is not folded into
this reword patch, because the reword must stay mechanical
and reviewable. The 1 NOT-RUN is Windows execution (cannot
run on Linux), as always.

### What was NOT done (WS3)

- No allocator change. No `kshetra` construct added. No
  program in `lib/` or `examples/` changed. No library
  function, no example, no doc, and no frozen-pack entry
  touched. The rebuilt `sutram_compiler` binary is **not**
  in the patch (rebuild with `tools/gates.sh` / the build
  script from source).

## §4 — remaining check

One item for ChatGPT's confirmation (not a blocker for
review of this patch, but it should be confirmed before the
word is treated as settled): the `:317` Devanagari case.
The old neuter `क्षेत्रम्` is ambiguous between nominative
and accusative; I chose nominative (`अवयवः`) by parallel
with `:313` and by subject role. If ChatGPT rules it
accusative (`अवयवम्`), that is a one-word change to one
pack entry + one golden + the regenerated `.inc`.

## §5 — base note

The brief says base "main at v414, compiler v261". By the
time this round ran, main had moved on (vocabulary commits,
v415 work, wave-1 inbox rounds); the patch is computed
against the current main head at the time of writing
(`2bc54c3a`, the `mandapa`/`danda` decision commits) and
the compiler still reports v261. The reword itself is
independent of those commits (the changed files are
diagnostics, packs, goldens, and the r23 test — no overlap
with the vocabulary commits).

## NOT RUN

- Windows / WSL: the Windows IDE inc file is unchanged and
  no Windows build was run (Windows is the owner's own work).
- Browser automation: no browser component in this round.
- Proof library as a separate run: the gates run includes
  "library proofs (226 passed, 0 failed, 226 total) PASS",
  so the proof count is covered by the gates, not left
  unrun.
