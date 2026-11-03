# Sutram — ROUND-106: audit the vocabulary change. No blocking collision — but five names are wrong, and the count is 30, not 28.

**Base:** `origin/main` at `7be8273c` (compiler v290,
the brief's base), with current main checked as the
implementation target (the audit is identical on both).
**Deliver into:** `Muse-to-Sarvam/`. **No tree changes by
this round, and no implementation** — this is the
pre-implementation audit the brief gates implementation on.
The vocabulary change itself is **not yet on main**: the
commits titled "VOCABULARY CHANGE" only add
`Sarvam-to-ChatGPT/ROUND-179.md` (ChatGPT's parallel
meaning audit). So the STOP condition below is live, not
moot.

## Where the project is (premise notes)

The brief's "289 examples" is the v289 count, stale two
rounds: v290 has **291** top-level examples, current main
**293** (the 2 new ones are 320/321, R109's outlives-chain
examples). The recursive count (including 16 files under
`examples/r67/r68/r71/`) is 309 on current main — the census
denominators below are top-level, the suite's population.
Lib is unchanged at 306 functions on both trees.

**The count of new names is 30, not 28, by itemization:**
2 operators (`asti`, `nasti`) + 4 message words (`truti`,
`patra`, `rekha`, `kuru`) + 10 kosh operations + 14
standalone = 30. If "28" excludes the 2 operators, it
reconciles; if it excludes something else, two names are
unaccounted for — the itemized list below is the checkable
version. **"90 existing builtins" also does not match the
named set:** the `bn_` builtin table has 47 names, the
`kw_` keyword table 34, the REPL commands 6 — 87 callable
names. BN numbers run to 92, so "90" matches the BN
numbering (off by 2) more than the named set. The collision
audit used the named set (47 + 6 + 34 + 306 lib + 493
example identifiers), which is the set a new name could
actually collide with.

## WS1 — the collision audit: 29 clean, 1 note, no STOP

For every new name, exact-identifier hits were measured
(word boundaries — `asti` does not collide with lib's
`asti_yugm`) against builtins, keywords, library functions,
`lang/*.lang` Latin tokens, and example identifiers (code
only: comments and string literals stripped), on v290 and
on current main (identical results).

**29 of 30 new names: ZERO hits in every category.**
`asti`, `nasti`, `truti`, `patra`, `rekha`, `kosh_kship`,
`kosh_hri`, `kosh_gan`, `kosh_ksham`, `kosh_iksh`,
`kosh_rikt`, `kosh_shodh`, `kosh_yuj`, `kosh_muc`,
`pankti_gan`, `tyaj`, `saha`, `jala`, `jala_bandh`,
`jala_shru`, `jala_grah`, `akshar_laghu`, `akshar_guru`,
`akshar_tas`, `vartani_yoj`, `likha_bindu`, `likha_rup`,
`sankhya_bindu`, `smaran_kriti` — none is a builtin, a
keyword, a library function, a lang entry, or an example
identifier.

**The one hit: `kuru` — KEYWORD + LANG.** `kuru` is already
a keyword (`kw_kuru`, `KW_KURU equ 29`, comment: "kuru =
do (imperative Sanskrit, for do-while)"), and therefore
already appears in the lang packs as that keyword's
Sanskrit form. **This does not trigger the STOP:** `kuru`
in the brief is a *message* word (replacing Hindi `karo`
in one error string), not a code name — message text is
not parsed as code, so no program breaks. And the meaning
agrees: `karo` = "do", the keyword `kuru` = "do". So
`kuru` is not a collision that breaks code; it is a name
that already exists, used consistently. It should still be
struck from the "new names" list (it is not new), and the
message word now shares a spelling with a keyword (a
reader may confuse message text with code — minor, not
blocking).

**Message-word prior uses** (for completeness): `truti`
0 prior uses (new, clean); `rekha` 0 (new, clean);
`patra` already means "file" in messages (`patra-ant` =
EOF, `nirgata-patram` = output file) — the rename
`file`→`patra` aligns English with the already-used
Sanskrit, it does not collide.

**The `to` deletion: safe for the tree, wrong replacement
note.** Zero code uses of `to` in examples (stripped) and
zero library functions named `to` — deleting it breaks
nothing in the tree. But the brief's "`to`→`prati`" is
wrong as a replacement: `to` is the old spelling of the
loop-bound keyword `tak` (`kw_to_str db "tak"` in the
`r4_old_kw` table), not of `prati` (the return alias).
Any out-of-tree program using `to` as a loop bound, told
to use `prati` (return), would be misdirected. The
replacement note must say **`tak`, not `prati`**.

**REPL duplication, unaddressed:** `exit`/`quit`/`help`
already have Sanskrit REPL commands — `nirgat` (exit)
and `sahayata` (help). Adding `tyaj`/`saha` creates two
Sanskrit words per command without stating what happens
to `nirgat`/`sahayata` (aliases? replaced? forgotten?).
That is not a collision, but the implementation should
say.

**Verdict on the STOP condition: it did not trigger.**
No name would break a program. Implementation may proceed
— with the five WS2 flags below addressed, and the `to`
note corrected to `tak`.

## WS2 — the Sanskrit: five names are wrong, and thirteen are roots

Each function body was read or probed before judging
(probe: `bodies.sm` — peek/pop/empty/clear/enqueue/
dequeue, `pankti_len`, `char_lower`/`char_upper`/
`char_from`, `lkhb`; `sankhya_dot` from its doc +
comment: two-argument vector dot product via `dpps`).
Devanagari is given for the complete words; roots are
shown with their halant, which is itself the tell.

**The systematic finding: 13 of 30 are bare roots or a
suffix, not complete words.** `kship` (क्षिप्),
`hri` (हृ), `gan` (गण्), `iksh` (ईक्ष्), `yuj` (युज्),
`muc` (मुच्), `shodh` (शुध्), `tyaj` (त्यज्), `bandh`
(बन्ध्), `shru` (श्रु), `grah` (ग्रह्), `yoj` (युज्),
and `tas` (तस्, a suffix, not a word at all). Strictly, a
root is not a `pada` (word) until inflected — so under
R178's constraint ("complete word or compound, never a
fragment"), these 13 need their full forms (`kshepa`,
`harana`, `ganana`, `ikshana`, `yojana`, `mocana`,
`shodhana`, `tyaga`, `bandha`, `shravana`, `grahana`,
`yojana`) or an explicit owner decision that roots are
accepted. The project already has a bare-root keyword
(`yoj`), so roots are not unprecedented — but that
precedent should be named as the decision, not assumed.
(The full-word forms above need native-speaker
confirmation; this audit judges grammar and meaning, not
as a native speaker.)

**Five names are wrong on meaning (flag, don't ship as
written):**

1. **`kosh_muc` (dequeue) — wrong by R179's own rule.**
   Probed: enqueue 1,2,3, then dequeue returns 1, length
   3→2, peek still 3. Dequeue *removes the first element
   and keeps the rest*; it releases nothing. `muc`
   (release) is wrong; `hri` (take) or `apanay` (remove)
   is right, exactly as R179's WS1 asks.
2. **`akshar_tas` (char_from) — backwards.** The handler:
   `char_from(code)` → pointer to a char in a temp
   buffer (probed: `char_from(66)` returns an address,
   which `likha` prints as an address — the #5 trap
   shape, a pre-existing quirk of the return, not of the
   name). `akshar` + `tas` parses as "from a character"
   (the suffix attaches to `akshar`), but the function is
   "a character *from a code*" — the `tas` attaches to
   the wrong stem, reversing the direction. And `tas`
   alone is a suffix, not a word.
3. **`likha_bindu` (lkhb) — `bindu` unexplained.**
   `lkhb` = "print number without newline" (BN comment;
   probed: `lkhb(7)` prints `7`, no point). The
   distinguishing feature is *no newline*, which `bindu`
   (point/dot) does not name. The new name introduces a
   point the function does not print — the exact error
   of naming without reading the body.
4. **`saha` (help) — wrong, and a truncation.**
   `saha` (सह) = "with", not "help". The existing
   Sanskrit help is `sahayata` (already a REPL command).
   `help`→`saha` truncates `sahayata` to `saha` — the
   `paripurna`→`purn` violation, losing the part that
   means "help". The name should be `sahayata` (already
   exists) or another full word for assistance, not `saha`.
5. **`smaran_kriti` (smaran_cp) — vague and inconsistent.**
   `kriti` (कृति) = making/doing, not specifically
   copying. The project already has a copy word:
   `pratilip` (in `vartani_pratilip`, string copy). The
   consistent name is `smaran_pratilip` (memory-copy),
   not `smaran_kriti` (memory-making).

**Names that pass (meaning + word):** `asti` (अस्ति,
is/exists) for `==`, `nasti` (नास्ति, is-not) for `!=`;
`truti` (त्रुटि, fault) for Error, `patra` (पत्र, file)
for file, `rekha` (रेखा, line) for line, `kuru` (कुरु,
do) for karo; `kosh_kship` (throw in) for push,
`kosh_hri` (take away) for pop (returns the value),
`kosh_gan` (count) for len, `kosh_iksh` (see) for peek
(reads the top), `kosh_rikt` (रिक्त, empty) for empty,
`kosh_shodh` (cleanse) for clear, `kosh_yuj` (join) for
enqueue (appends); `pankti_gan` (row-count) for array
length (`pankti` already means array here, via
`pankti_len` — probed with a string it returns 0 because
it takes a `mala`, not a string); `vartani_yoj` (join)
for cat, `likha_rup` (रूप, form) for fmt,
`sankhya_bindu` (बिन्दु, dot) for dot product (neither
old nor new name says "product" — the full term would
be `sankhya_bindu_gunana`); `akshar_laghu` (लघु, small)
for lower (probed 65→97), `akshar_guru` (गुरु, great)
for upper (probed 97→65); `jala_bandh` (bind),
`jala_shru` (hear), `jala_grah` (take) for netbind/
listen/accept — `jala` (जल) itself is ambiguous (water
is primary, net secondary) but valid for network, noted
not rejected; `tyaj` (abandon) for exit/quit is apt in
meaning (as a root, see the systematic note).
`kosh_ksham` is thin: `ksham` (क्षम) = capable
(adjective), not capacity (noun, `kshamata`) — for a
function returning a number (the capacity), an adjective
is odd; noted, not rejected.

## WS3 — the census, tenth run, and the population the aliases protect

Same method. **Tenth run on v290: identical to the ninth**
(Q1 6 = 258/303/304 + 0 + 217/237/268; Q2 0 definite, 1
potential (286); Q3 58 textual examples / 57 runtime-true
+ 26 lib; denominators 291/306/597) — same tree, same
method, stability confirmed. **On current main: the same
counts** (Q1-textual 26, Q3-textual 58; denominators
293/306/599) — the 2 new examples (320/321) both declare
a `kosh` in a `mandapa` and push (they are R109's
outlives-chain examples), so they affect neither Q1
(they do not allocate in a loop) nor Q3 (they have a
`mandapa`).

**The population the aliases protect: 67 examples on
v290, 69 on current main** (code uses, comments and
strings stripped; word boundaries). Per old name (v290 /
current): `kosh_push` 46/48, `kosh_pop` 12/12, `kosh_len`
17/17, `kosh_cap` 5/5, `kosh_empty` 1/1, `pankti_len`
10/10, `netsock`/`netbind`/`netlisten` 1/1 each,
`char_upper` 1/1, `lkhb` 6/6, `likha_fmt` 3/3. Plus **3
library files** (`kosh_len`, both trees). So the aliases
protect 67+3 files on v290, 69+3 on current main.
**Fourteen old names have zero example users:**
`kosh_peek`, `kosh_clear`, `kosh_enqueue`,
`kosh_dequeue`, `exit`, `quit`, `help`, `netaccept`,
`char_lower`, `char_from`, `vartani_cat`, `sankhya_dot`,
`smaran_cp`, `to` — those aliases protect no example
(they protect out-of-tree users, and `exit`/`quit`/
`help` protect the REPL). **`to`'s population is zero**,
confirming the deletion is safe for the tree (with the
replacement note corrected to `tak`).

## What this round did NOT do (NOT RUN)

Windows, browser, implementation (audit only — the
implementation is gated on this audit and on R179's
meaning audit), native-speaker review (the full-word
forms suggested above need one). The full suite was not
re-run: no `src/`/`lib/`/`examples/`/`tests/` file
changed in this round, and the brief's + Claude's
suite/guard/gate numbers are cited, not re-measured.
RSS was not measured.

## Note for the next check (not part of this round)

`ChatGPT-to-Sarvam/ROUND-178-ARENA-DESIGN-FOR-REVIEW.md`
has landed since R105. R105's pending WS2 (attack
ChatGPT's arena specification) is therefore now
unblocked; it is not bundled here (to avoid two parallel
deliveries) and will be the next backlog item.

## Deliverables

- `Muse-to-Sarvam/ROUND-106-VOCABULARY-AUDIT.md` (this
  report)
- `Muse-to-Sarvam/r106_census.json` (WS1 per-name hits,
  WS2 per-name verdicts, WS3 tenth-run census + old-name
  population, the count corrections)
- `Muse-to-Sarvam/collision_audit.py` (the WS1 script:
  run as `python3 collision_audit.py <tree> [...]`)
- `Muse-to-Sarvam/bodies.sm` (the WS2 behavior probe:
  peek/pop/empty/clear/enqueue/dequeue, `pankti_len`,
  `char_lower`/`char_upper`/`char_from`, `lkhb`)

Work staged in `~/workspace/r106/` (scripts in `ws1/`,
probes in `ws2/probes/`, census in `ws3-v290/` and
`ws3-current/`, worktrees in `tree/` (v290) and `current/`
— read-only, removed after delivery).
