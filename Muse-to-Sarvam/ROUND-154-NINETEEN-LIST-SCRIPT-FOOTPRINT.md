# ROUND-154 — the nineteen, as a list; could a script have caught them; my own footprint

**Base:** `308c2161` (v315) · **Method:** read-only — nothing compiled, assembled, run, or executed · **Deliver into:** `Muse-to-Sarvam/`

## Verdicts first

**Task 1 — the nineteen, as a numbered list.** Below, one line each: what the reference says, what the code does, and the file and line of each. Numbered 1–19 for Claude to work through; the R152 number is in parentheses for traceability. The twentieth is not a wrong claim — it is my own misquote, and its whereabouts are stated after the list. All doc lines are at v315; all code lines are at v315 (`308c2161`).

**Task 2 — could that be a script?** Partly. A script that extracts every symbol the reference names and checks it exists, and every number and checks it against the source, would catch **7 of the 19** (by the mechanisms named in the table below). It would catch **none** of the 19 by symbol existence alone — every named symbol in the 19 wrong claims exists; the errors are in what the docs say the symbols *do*. The other 12 need a reader: the order of checks, dead versus live code, reasons, closure arguments, runtime behaviour, measurements, paraphrase fidelity, and historical claims. The "could not" is the important half, and it is the longer table.

**Task 3 — my own footprint.** Total: **572 files, 5,430,421 bytes** — the brief's "5.4 MB" verifies exactly (5.43 MB decimal). **MUST STAY: 5,232,494 bytes (96.4%), 381 files** — reports, patches, and everything cited by a report. **COULD GO: 197,927 bytes (3.6%), 191 files** — all uncited, non-report, non-patch, led by 25 uncited JSON companions (156,628 bytes). The single biggest apparent saving is NOT available: the 14 compiler `.part` files (1,204,489 bytes, 22.2%) are cited by both round reports and their concatenations exist nowhere else — though the round42 set is recoverable by reconstruction (base + patch, sha256 verified below), the round41 set is not. Maximum if everything went, including judgement calls: 243,869 bytes (4.5%); 846,449 bytes (15.6%) if the round42 parts go on the reconstruction argument. There is no way to shrink this channel by much without losing reports, patches, or the only copies of proposed files. My own last two JSONs (`r152.json`, `r153.json`) are in the uncited list — the reports never name them.

---

## Task 1 — the nineteen, one line each

**The list (doc = `docs/LANGUAGE-REFERENCE.md` unless marked MM = `docs/MEMORY-MODEL.md`; code = `src/sutram_compiler.asm` unless noted; all lines at v315):**

1. (R152 #1) Doc says "every `kosh` has a region of its own and never moves" (doc:13); code has small koshes living in the arena and elements moving on growth — the descriptor never moves, the elements do (`src/r65_arena.inc:561-576`).
2. (R152 #2) Doc says "Generated from the compiler source and the language packs, so it cannot drift from the code" (doc:19); it has drifted — the other eighteen items on this list are the evidence (no single code line; the drift is the list).
3. (R152 #3) Doc says likha with exactly three arguments requires "the first must be a string literal to select multi-value output" (doc:303); code prints three values whatever comes first from v287, and the doc contradicts itself at :331 ("prints three values, whatever comes first").
4. (R152 #4) Doc says "a program can currently include at most two modules — the inliner's buffer overflows at three or more" (doc:376); code inlines seven modules in `examples/99_ast_multimodule_capacity.sm` (`yoj` at :2-8), and the real caps are the 128 KiB expanded source (`IMPORT_BUF_CAP equ 131072`, code:33) and the 128-entry function list (`FUNC_DEFS_CAP equ 128`, code:54).
5. (R152 #5) Doc says "`s + k` (a `kosh`) → `E_VARTANI_CAT`" (doc:438); code tests kosh FIRST in the rfx binop check (`.rfx_csb_kosh` at :9691/:9695, before `.rfx_csb_cat` at :9827), so `s + k` is `E_KOSH_GANIT`.
6. (R152 #6) Doc says empty `kosh_pop` / `kosh_peek` / `kosh_dequeue` abort with "`rikta kosh se kosh_pop`" etc. (doc:945-946); code says "`riktat koshat kosh_pop`" etc. (`msg_kosh_empty`, code:707; `msg_kosh_peek_empty`, code:710) — "rikta kosh se" appears nowhere in `src/`.
7. (R152 #7) Doc says the slice descriptor is "an address of its three words" (doc:995); code builds a TWO-word descriptor, 16 bytes: elements + length (`src/r23_capabilities.inc`, `r23_gen_slice` :574+).
8. (R152 #8) Doc says "so the C side read an address, or, as an `i64` count, crashed (Muse's reading, R151; confirmed)" (doc:995-996); no crash was demonstrated — R150 line 18: a wrong value, not a wild pointer; a crash comes only from *using* that value (no code line; the absence of evidence is the point).
9. (R152 #10) Doc says "`kosh k[1]` grown to 1,000 has capacity 1,024: 16 + 8,192 bytes" and the table's "a kosh of 1000 → 8272" (doc:1411/:1416); code has a 32-byte kosh header (4 words: `[d-16]` length, `[d-8]` capacity, `[d]` elements, `[d+8]` region bytes, `src/r65_arena.inc:561-566`), so a capacity-1024 kosh holds 32 + 8,192 = **8,224** bytes.
10. (R152 #11) Doc says "What does not count: a `kosh` (it has its own region, section 16)" (doc:1460); the operative claim (a kosh does not count against the parimita budget) holds, but the reason is wrong for small koshes, which live in the arena, not a region (same header evidence as #9).
11. (R152 #12) Doc says "a block run 100,000 times that makes a `kosh` of 100 numbers peaked at about 100 MB on v283, and at 400 MB on Linux from v284 (each `kosh` now has its own region, one 4 KB page at least - section 16)" (doc:1392); the per-kosh-region model ended at v301 — small koshes are 32 bytes of arena at v315 (same header evidence as #9).
12. (R152 #13) Doc says "The largest statement in the 344 examples and 310 library functions takes 52 steps" (doc:1064); counted at v315: 331 top-level / 347 recursive examples, neither is 344 (`ls examples/*.sm | wc -l` = 331; `find examples -name "*.sm" | wc -l` = 347); lib prakriya defs still 310.
13. (R152 #14) Doc says "History: … v312 65,536 (refused 16,385 terms - R148's measured boundary)" (doc:1065); R148 was read-only, measured nothing, and its report never mentions 16,385 (grep of `Muse-to-Sarvam/ROUND-148-PAPER-REVIEW.md`: 0 hits).
14. (R152 #15) Doc header box says suite PASS=315, crash corpus 227/0, proofs 229/229 and 86/86, gates 65/1/1, installer payload v243 (doc:3); stale snapshot pinned to v300 — at v315: suite 327, gates 78/0/1, installer v315 (brief's shared state; suite/gates not re-runnable by reading).
15. (R152 #16) Doc says the scratch-escape check covers "likh, likh8, kosh_kship … wherever the call is written" (doc:1309); code's `r73_check_call` lists `BN_KOSHPUSH, BN_LIKH8, BN_LIKH8C, BN_SETCHAR, BN_MEMSET` only (code:8697-8710) — `BN_LIKH` is not in it, and `likh` (BN 1) has no codegen handler in the `ge_call` dispatch (only the name-table entry at :900).
16. (R152 #17) Doc (MM:42) says "The push emission explicitly rejects growth on a kosh parameter"; code allows parameter growth since v304, and the old refusal is dead code (`.ge_call_koshpush_param_bad`, code:22584, never jumped to since v304).
17. (R152 #18) Doc (MM:44) says "Growth … copies existing cells and updates the named variable's pointer" / "No reclamation of the old buffer appears in that path"; code updates the shared descriptor's `[d]`, not the variable's pointer, and old regions ARE reclaimed — munmap emitted (`src/r65_arena.inc:713`, syscall 11) and VirtualFree (`win/winrt_blob.asm:184-188,312`).
18. (R152 #19) Doc (MM:86) says "The growth-on-parameter rejection is specifically motivated in the source by pointer replacement" / "That check does not establish that every other alias is updated when a local kosh grows"; the rejection is gone (see #16), and every alias IS updated via the shared descriptor (R129 verified 20M agreement).
19. (R152 #20) Doc (MM:189) says "A grep of the whole compiler source finds **no `munmap` / free emission anywhere** — the old buffer's mapping is never released"; code HAS a munmap emission (`src/r65_arena.inc:713`, syscall 11) and VirtualFree (`win/winrt_blob.asm:184-188,312`), so "The test above is expected to FAIL until that lands" (MM:204) is stale too.

### The twentieth — where I looked, and why it is not locatable

R152's wrong no. 9 quoted §16 as saying "A `kosh` grows until the arena is full (1 GiB) or a region's 64 MiB." That sentence appears verbatim in **neither** doc at v314 or v315: grep for "grows until", "until the arena", "arena is full" returns **0 hits** in `docs/LANGUAGE-REFERENCE.md` and `docs/MEMORY-MODEL.md` at both bases (`52d78435` and `308c2161`). The §16 text it appears to rest on (`docs/LANGUAGE-REFERENCE.md:956-959`) says the opposite: elements move "into a region of their own past 64 KiB", and "when a `kosh` outgrows it the elements move to a larger one" — a region is `max(2*new, R101A_REGION)` and grows beyond 64 MiB; the binding cap is `R128_MAXCAP` = 2^40 elements (`src/sutram_compiler.asm:21354`). So no. 9 was a paraphrase that overstates what the doc says — a misreading on my side, not a wrong sentence in the reference. There is no sentence to fix, and the code fact it rests on stands. The R152 count is therefore restated: **19 locatable wrong claims, not 20.** The correction is recorded here and in the R153 report rather than silently dropped, because the R152 report is the record Sarvam reads — and because it is exactly the kind of error the symbol rule in Task 2 is meant to catch: a claim quoted without the file + line it rests on.

---

## Task 2 — could that be a script? What it could catch, and what it could not

**The proposal, as briefed:** a script that extracts every symbol the reference names and checks it exists in `src/` or `lib/`, and every number and checks it against the source. Two existing checks bound the shape of it: `tools/check_doc_signatures.py` (run by `tools/gates.sh:228`, FAILs on drift) compares `lib/*.smlib` `prakriya` declarations with signatures in `docs/sutram-stdlib.html` — a mechanical cross-check that works because both sides are structured. `tools/doc_stale_claims.py` (run by `tools/gates.sh:229`, exit 0 always) scans docs for sentences shaped like *absence* claims ("there is no X") and reports file + line for a human to confirm or clear — a mechanical *finder* that deliberately does not decide.

**The headline result, tested against the 19:** a pure existence script — extract every symbol, check it exists — would catch **none** of the 19. Every named symbol in the 19 wrong claims exists: `E_VARTANI_CAT` exists, `BN_LIKH` exists, the old push-refusal message string exists (as dead code), `E_KOSH_GANIT` exists. The errors are not in the names; they are in what the docs say the names *do*. Existence is the wrong test for 19 out of 19. What catches some of them is not existence but stronger checks — quoted strings, counts, arithmetic, provenance — and those catch 7.

### What a script could catch (7 of 19)

| # | Wrong claim | The script check that catches it | How it works |
|---|---|---|---|
| 4 | At most two modules (doc:376) | Counterexample scan | Count `yoj` lines in every example; `examples/99_ast_multimodule_capacity.sm` has 7 > 2. A "at most N" claim is falsified by one counterexample, and the scan finds it. |
| 6 | "rikta kosh se kosh_pop" (doc:945) | Quoted-string grep | Extract every quoted diagnostic from the docs; grep `src/` for the exact string. "rikta kosh se" returns 0 hits; "riktat koshat" exists (`src/sutram_compiler.asm:707`). Verified by grep at v315. |
| 9 | Parimana 16 + 8,192 = 8272 (doc:1411) | Internal arithmetic | The doc's own numbers do not add up: 16 + 8,192 = 8,208, not 8,272. A script that re-adds the numbers in a sentence catches the inconsistency without knowing the header size. (The header size itself, 16 vs 32, needs a layout model — see "could not".) |
| 12 | "344 examples" (doc:1064) | Count check | Count `examples/*.sm` (331) and recursive (347) at the base; neither is 344. A script that recomputes a count from the tree instead of trusting the doc's number catches it. |
| 13 | "R148's measured boundary" (doc:1065) | Cross-document citation check | Extract every number attributed to another document and grep that document for it: "16385" appears 0 times in `Muse-to-Sarvam/ROUND-148-PAPER-REVIEW.md`. Verified by grep. |
| 14 | Header-box v300 numbers (doc:3) | Staleness check | The header pins a version (v300) while the tree is v315; a script can flag any version-pinned number as stale when the version moves. Note the numbers were true at v300 — this catches staleness, not falsehood. |
| 19 | "No munmap / free emission anywhere" (MM:189) | Absence-claim grep | Extract absence claims ("no X anywhere") and grep for X: "munmap" appears in `src/r65_arena.inc:713`. This is exactly `doc_stale_claims.py`'s shape — except that tool reports absence claims for human review rather than verifying them, so the check would need to be added, not just run. |

### What a script could not catch (12 of 19) — the important half

| # | Wrong claim | Why no script catches it |
|---|---|---|
| 1 | Every kosh has its own region (doc:13) | A model claim, not a symbol or a number. The script would need to know the memory model — small koshes in the arena, regions past 64 KiB — and compare it against the sentence's meaning. There is no constant in the code named "every kosh has a region" to check against. |
| 2 | "Cannot drift from the code" (doc:19) | Self-referential. A script cannot verify a claim about the document itself; the drift is what the audit found, and the script is the audit. |
| 3 | Likha 3-arg first-must-be-string-literal (doc:303) | Behavioural, and the doc contradicts itself at :331. Catching it needs semantic comparison of two rules in the same document, plus the code fact that `likha` prints three values whatever comes first. A symbol grep finds `likha` and stops. |
| 5 | `s + k` → `E_VARTANI_CAT` (doc:438) | The code exists — a symbol check returns "exists" and passes it. The error is the ORDER of checks (kosh tested first, `:9691` before `:9827`). Order is control flow; a grep cannot see it. |
| 7 | Slice descriptor "three words" (doc:995) | The number 3 is compared against nothing in the code. The "2" comes from reading `r23_gen_slice`'s 16-byte layout. There is no machine-readable layout spec for the descriptor — no constant says "descriptor = 2 words". |
| 8 | "Crashed (confirmed)" (doc:995) | An evidence claim. A script cannot verify whether a crash was demonstrated; it can only check whether the cited source contains the word "crash", which proves nothing about what was demonstrated. |
| 10 | Parimita "its own region" reason (doc:1460) | The operative claim HOLDS; the reason is wrong. A script cannot judge reasons — it can only check the claim, and the claim is true. |
| 11 | 100 MB / 400 MB explanation (doc:1392) | A pinned measurement plus a model explanation. The numbers are historical (not checkable), and the explanation contradicts a model that changed at v301. A script would need to know which model was true when. |
| 15 | "likh covered by scratch check" (doc:1309) | `BN_LIKH` exists — a symbol check passes it. Catching it needs list-membership parsing: is `BN_LIKH` in `r73_check_call`'s list (`:8697-8710`)? That is a targeted structural check on one function, not a generic grep. A script could be taught that one list; it cannot be taught every list. |
| 16 | Push rejects param growth (MM:42) | The old refusal string still EXISTS as dead code (`msg_kosh_param_push`). An existence check says HOLDS — a false negative. Catching it needs liveness analysis (the label is never jumped to since v304). |
| 17 | Growth updates the variable's pointer (MM:44) | Semantic: descriptor update versus pointer update. The distinction is in what the code assigns, not in which symbols appear. (The munmap half of this claim is #19, which a grep catches.) |
| 18 | Rejection motivation / aliases (MM:86) | Semantic and historical: a motivation attributed to the source, and a claim about what a check establishes. No grep decides either. |

**What the "could not" half means for the project.** A script is worth building for the mechanical classes — quoted diagnostics, counts, arithmetic, cross-document numbers, absence claims, version staleness — and it should be a gate that FAILs on drift, like `check_doc_signatures.py`, not a review list like `doc_stale_claims.py`, because a review list is what lets nineteen false paragraphs sit for a version. But the script is a floor, not a proof: it catches names and numbers, not meanings. What still needs a human reader, on the evidence of these 19: whether a check is on the path the docs describe (order, membership, liveness), whether a class is closed (the argument, not the name), whether advice works (splitting a statement helps the budget and does nothing for the tree — the two limits need opposite remedies, and only a reader who understands both limits can check that), whether a paraphrase is faithful (the R152 no. 9 misquote was mine, and a script that greps for the quoted sentence would have caught it — but only because I quoted it; a paraphrase with no quote to grep is invisible), and whether a historical claim is still true (the MEMORY-MODEL body is pinned to R70, and its staleness is a judgement about time, not a grep). The gate catches a missing version number; it does not catch nineteen false paragraphs. Nineteen false paragraphs are caught by a reader who reads the code first and the doc second — which is what R152 did, and what a script cannot do.

---

## Task 3 — my own footprint: what is cited, what is a copy, what could go

**Base:** `origin/main` at `fe4433bc` (tip at time of reading). **Method:** read-only git plumbing (`git ls-tree -r -l`, `git show`, blob-SHA comparison, sha256 of concatenations). Nothing compiled, run, or executed; nothing deleted — this is a list of what could go, not a deletion.

### Verdict first

**Total: 572 files, 5,430,421 bytes.** The brief's "5.4 MB" verifies exactly as decimal megabytes (5.43 MB; 5.18 MiB).

**MUST STAY: 5,232,494 bytes (96.4%), 381 files.** The channel is mostly reports and patches, and both stay by rule.

**COULD GO: 197,927 bytes (3.6%), 191 files** — all of it uncited, non-report, non-patch material, led by 25 uncited JSON companions (156,628 bytes).

**The single biggest apparent saving is NOT available.** The 14 compiler `.part` files (1,204,489 bytes, 22.2% of the channel) are cited by both round reports **and their concatenations exist nowhere else** — neither matches any file in git history (`git rev-list --all --objects` finds neither blob), and neither matches the base compiler at its round's base commit. They are the only copies of the proposed v246+guard and v248+guard whole files. One of the two sets is recoverable by reconstruction (see below); the other is not.

**Maximum if every COULD GO item plus every judgement call below went: 243,869 bytes (4.5%).** If the round42 parts were also dropped on the reconstruction argument: 846,449 bytes (15.6%). There is no way to shrink this channel by much without losing either reports, patches, or the only copies of proposed files.

### Rules used for classification

- A **report** (`.md` in the outbox, including `PATH.md`) is a primary record and MUST STAY even if no other report cites it by name — only 35 of the 159 reports are cited by name by another report or brief; that is normal, not a sign of redundancy. No two reports share a blob (no duplicate `.md` in the outbox).
- A **patch** (`.patch`) is a deliverable and MUST STAY even if the code it patches is now on main — it is the record of what was proposed. All 32 patch files stay, including the one uncited patch (`ROUND-64-avayava-reword.patch`, 47,931 bytes).
- A file **cited by name** in any report (`.md` under `Muse-to-Sarvam/`) or brief (`.md` under `Sarvam-to-Muse/`) MUST STAY unless it is a byte-identical duplicate of another file, in which case it is listed under judgement calls, not deleted silently.
- A file is a **copy that exists elsewhere** only on byte identity (same blob SHA), or on a whitespace-normalised content match for `.sm` files. A file that merely resembles a tree file (same name, edited text) is NOT a copy.
- No file that is the only copy of a measurement, a golden, or a patch is recommended for deletion. A probe program whose text is quoted nowhere in its report is the only copy of that probe — those are listed as COULD GO only by the letter of the "uncited" rule, with the caveat stated below.

### Totals and breakdown

| Directory | Files | Bytes |
|---|---|---|
| `Muse-to-Sarvam/` (top level) | 529 | 4,193,161 |
| `Muse-to-Sarvam/round42-whole-files/` | 16 | 603,321 |
| `Muse-to-Sarvam/round41-whole-files/` | 16 | 602,650 |
| `Muse-to-Sarvam/round39-whole-files/` | 11 | 31,289 |
| **Total** | **572** | **5,430,421** |

| Extension | Files | Bytes | What it is |
|---|---|---|---|
| `.md` | 159 | 1,994,191 | Reports (and `PATH.md`) |
| `.patch` | 32 | 1,422,392 | Proposed code changes |
| `.json` | 67 | 638,636 | Census / verification companions |
| `.part1`–`.part7` | 14 | 1,204,489 | Split compiler wholes (rounds 41/42) |
| `.py` | 17 | 68,353 | Generators, scanners, audit tools |
| `.sm` | 251 | 54,240 | Probe programs |
| `.sh` | 1 | 19,626 | `round39-whole-files/gates.sh` |
| `.tsv` | 2 | 15,569 | Variable / collision tables |
| `.c` | 3 | 10,875 | R125 benchmark programs |
| `.txt` | 2 | 1,561 | Keep-list, README sentence |
| `.out` | 12 | 465 | Expected probe outputs |
| `.exit` | 12 | 24 | Expected exit codes (all the 2-byte file `0`) |

Citation status (basename or path appearing in any of the 159 reports or 157 briefs): cited 256 files / 3,766,169 bytes; uncited 316 files / 1,664,252 bytes. Of the uncited, 124 are `.md` reports (1,418,394 bytes) and 1 is a `.patch` (47,931 bytes) — both MUST STAY by rule, which leaves 191 uncited non-report, non-patch files (197,927 bytes).

Byte-identical duplicates: 30 files in the outbox share a blob with a file elsewhere in the tree (4,107 bytes — mostly the 2-byte `.exit` files, plus 16 `.sm` files, all cited); 50 files share a blob with another file inside the outbox (92,239 bytes — mostly the whole-files test triplicates and the r82/r89 JSON pair).

### The `.part` files: the 1.2 MB question, answered

`round41-whole-files/` and `round42-whole-files/` each hold 7 parts of `sutram_compiler.asm` plus the same 9 test files (`251/252/253_r38_alias_*_oob` `.sm`/`.out`/`.exit`). The parts exist because the upload route caps a single argument at ~128 KiB (R42 report). Each part is cited by both round reports (`2026-10-27-round41-guard-whole-files.md` and `2026-10-27-round42-compiler-verified.md` name every part).

**What the parts are.** Concatenating each set (in part order, each part ending at a newline) reproduces a proposed whole compiler file:

- Round 41: 601,909 bytes, sha256 `d2d2f64b0238054d6e92b5815630f8107aeb87e8275de4735598e1b9b5db21b7` — the v246 compiler plus the R38 bounds guard. Base `be5b856f` (R41 report line 3).
- Round 42: 602,580 bytes, sha256 `8d05915c5a71d17ea97ad7e40e5bd6f5fef7133070bdc8cba7c51632a0b3da27` — the v248 compiler plus the same guard. Base `fd02405a` (R42 report line 3). The R42 concatenation sha256 was independently re-verified in this round and matches the report's stated value exactly.

The two wholes differ (first difference line 237: `msg_version` v246 vs v248, plus the R35 Windows sidecar hunks).

**Do they exist elsewhere? No.** Neither concatenation's blob id is reachable from any ref, and neither matches the base compiler at its round's base commit (R41 base sha256 `81257768be1832e5f5a64aa1a83b30a887bc35514799efcdce409081a4f7c97d`; R42 base `717e5c199264631b4e6444a96f280151bdbe1bf889bf77f3afdf0561bdcb678d`). The R41 report itself says the whole files "were never installed" (line 51), and the R42 report says "the R41 file is now stale (main moved to v248)" (line 30). The code they propose is superseded — the compiler is on main at v315 — but as files they exist only here.

**One set is recoverable by reconstruction, the other is not.**

- **Round 42 (602,580 bytes): recoverable.** The R42 report gives the exact recipe: base `fd02405a`'s `src/sutram_compiler.asm` (599,560 bytes, sha256 `717e5c19…`) plus `Muse-to-Sarvam/2026-10-27-round42-guard-v248.patch` (4,218 bytes, in the outbox, cited), with the intended file's sha256 `8d05915c…` stated in the report — which is exactly the sha256 of the concatenation. The whole file can be rebuilt from two files that are both in the tree. Deleting the 7 R42 parts would not lose any content that cannot be rebuilt, but it would break the R41/R42 reports' citations of the part filenames, and the rebuild was not re-run here (applying a patch is execution, outside this read-only task). This is a judgement call, not a true duplicate — listed separately below, NOT counted in the COULD GO total.
- **Round 41 (601,909 bytes): not recoverable.** No patch form of the R41 whole file exists in the outbox (the R41 report mentions no patch), and no reconstruction recipe is stated anywhere. The 7 R41 parts are the only copy of the v246+guard proposal. They must stay unless the owner accepts losing that proposal outright.

### MUST STAY (5,232,494 bytes, 381 files)

| Group | Files | Bytes | Why |
|---|---|---|---|
| All `.md` reports (incl. `PATH.md`) | 159 | 1,994,191 | Primary records; no two share a blob |
| All `.patch` files | 32 | 1,422,392 | Deliverables; the record of what was proposed (incl. the 1 uncited patch, `ROUND-64-avayava-reword.patch`, 47,931 bytes) |
| The 14 `.part` files | 14 | 1,204,489 | Cited by both round reports; concatenations exist nowhere else |
| Cited `.json` (42 files) | 42 | 482,008 | Cited by name in their round's report (e.g. `r119_duplicates.json`, 71,216 bytes, cited by `ROUND-119-REPO-KEEP-AUDIT.md`) |
| Cited `.py` (13 files) | 13 | 55,117 | Cited tools, incl. `round39-whole-files/doc_counts_gate.py` (10,922 bytes, cited by 13 reports) and the three `trap_matrix*.py` generators |
| Cited `.sm` (104 files) | 104 | 26,333 | Probe programs named in their round's report |
| `round39-whole-files/gates.sh` | 1 | 19,626 | Cited by 19 reports |
| Cited `.tsv` (2 files) | 2 | 15,569 | `ROUND-55-VARIABLES.tsv` (12,110, cited by 3) and `ROUND-50-COLLISION-VERDICT.tsv` (3,459, cited by the R50 brief) |
| Cited `.c` (3 files) | 3 | 10,875 | R125 benchmark programs, cited by `ROUND-125-TEST-THE-REVIEW.md` |
| Cited `.txt` (2 files) | 2 | 1,561 | `r119_keeplist.txt` and `README-SENTENCE.txt` (cited by 5 reports) |
| Cited `.out` (9 files) | 9 | 333 | Expected outputs of the whole-files test programs |

### COULD GO (197,927 bytes, 191 files)

All uncited, non-report, non-patch. Per-group table:

| Group | Files | Bytes | Reason |
|---|---|---|---|
| Uncited `.json` companions | 25 | 156,628 | Not named in any report or brief. List below. |
| Uncited `.sm` probe programs | 147 | 27,907 | Not named in any report or brief; unique texts (see caveat). |
| Uncited `.py` scripts | 4 | 13,236 | `r108_census.py` (6,102), `r107_collision.py` (2,657), `compare_ws2_tests.py` (2,338), `compare_ws2.py` (2,139). Tools, not measurements; outputs (where they exist) are also in the outbox or in reports. |
| Uncited `.out` files | 3 | 132 | `r76_madhava_sign.out` (84), `r78_srij_fill_guard.out` (42), `r78_srij_witness.out` (6). Expected outputs of probes whose reports do not name them. |
| Uncited `.exit` files | 12 | 24 | All the 2-byte file `0`; byte-identical to hundreds of `.exit` files in `tests/expect/`. Pure duplicates. |

**The 25 uncited `.json` files** (all the `r1xx.json` verdict companions whose reports never name them — the naming convention exists for some rounds and not others; e.g. `r104_census.json` IS named in its report at line 185, while `r130.json` is not named anywhere, verified by direct grep of `ROUND-130-V303-RELEASE-CANDIDATE.md`):

`r130.json` (19,809), `r133.json` (18,644), `r132.json` (11,492), `r128.json` (10,973), `r131.json` (10,829), `r129.json` (10,540), `r127.json` (10,162), `r126.json` (9,364), `r152.json` (5,185), `r153.json` (5,124), `r107_replacements.json` (3,792), `r151.json` (3,787), `r118.json` (3,777), `r105ws2_attack.json` (3,602), `r112.json` (3,579), `r117.json` (3,245), `r108_census.json` (3,173), `r150.json` (2,983), `r113.json` (2,937), `r111.json` (2,598), `r110.json` (2,472), `r116.json` (2,462), `r114.json` (2,069), `r115.json` (2,069), `r109.json` (1,961).

Caveat on the JSONs: each is the only machine-readable structured record of its round (base, verdicts, counts). The prose reports carry the same verdicts and numbers in most cases — e.g. `r130.json` opens with the same gates (68/0/1) and suite (327) figures its report states — but the JSON is the structured form. `r108_census.json` (keys: `aliases`, `base`, `census`, `not_run`, `ws1`, `ws2`) is the full census behind `ROUND-108-ALIASES-VERIFIED-RULE-CENSUS.md`, which does not name it; its per-item data is not all in the prose. Deleting these loses structure, not facts. My own last two JSONs (`r152.json`, `r153.json`) are in this list — the R152/R153 reports never name them.

**Caveat on the 147 uncited `.sm` probes:** each is the only copy of that probe's text. A sample of five (`r129_ws1_20k_grow2.sm`, `r127_ws1_scope_a.sm`, `r130_ws1_nirm_adj.sm`, `atk_koshassign.sm`, `str300.sm`) is quoted neither in full nor by first line in its round's report — the reports record the outcome (what printed, what exit code), not the program. So these 27,907 bytes are "could go" only by the letter of the uncited rule; removing them makes the reported probe outcomes unreproducible from the outbox. They are small; the honest recommendation is to keep them unless the owner accepts losing probe texts. The same caveat, weaker, applies to the 4 uncited `.py` scripts (each the only copy of that script).

### Checked and found NOT to be duplicates

- **Whole-files 252/253 `.sm` vs `examples/252/253`.** The outbox copies are the ORIGINAL R38 probe texts (`kosh_push(v, 1.5)`, `vitti w = 0` then holding a kosh); `examples/252_r38_alias_kosh_oob.sm` and `examples/253_r38_alias_slice_oob.sm` are the UPDATED versions (`kosh_kship`, R126-fixed declarations, `E_VITTI_PRAKAR` comments). Different blobs, different content — not copies. Only `251_r38_alias_mala_oob.sm` is byte-identical to its `examples/` counterpart (in all three whole-files dirs).
- **Whole-files `.out` vs `tests/expect/`.** The outbox `.out` files read `Sutram Error: mala ank seema atikram`; the `tests/expect/` versions read `Sutram truti: …` — the v294 rename. Pre-rename originals, not copies.
- **`.sm` near-copies.** A whitespace-normalised content hash of every outbox `.sm` against every `.sm` under `tests/` and `examples/` finds only the three 251 copies above — no probe hides behind different formatting.
- **The 16 `.sm` files that ARE byte-identical to tree files** (4,107 bytes with the `.exit` files) are all cited by their reports, and their tree counterparts are other channels' evidence, not canonical sources: the R135/R136/R137 probes also sit in `Windows-to-Sarvam/`, `r125_ws1_mala_holds_kosh.sm` also sits in `Claude-to-Sarvam/evidence-r125/scan-sanity/m.sm`, and the three 251 copies also sit in `examples/`. They are listed here so the duplication is visible; they stay because they are cited.

### Judgement calls (cited but redundant — NOT counted in the COULD GO total)

| Item | Bytes | What it is |
|---|---|---|
| `r82_parikshita_table.json` vs `r89_parikshita.json` | 43,430 (one copy) | Byte-identical (same blob). Both cited — by `ROUND-82-ONE-TABLE-AND-BLOCK-REACH.md` and `ROUND-89-LAST-CENSUS.md` respectively. One copy could go; deleting either dangles one report's filename citation. The R89 copy is the later delivery. |
| Whole-files test-file triplicates | 1,482 | The 9 test files (`.sm`/`.out`/`.exit` × 251/252/253) exist byte-identically in all three whole-files dirs. The round41 and round42 copies (18 files, 741 bytes each) duplicate round39's. The R41/R42 reports cite the directories, so removing them leaves the directory references half-true. Negligible either way. |
| Cited same-content `.sm` pairs | 1,030 (one copy each) | Five pairs, each the same probe re-delivered under a new round name: `r124_kosh_16.sm` = `r125_ws3_16.sm` (293), `r131_ws1_slice_store_nogrow.sm` = `r135_ws1_slice_store_direct.sm` (155), `r133_ws_r133_oom_small.sm` = `r134_oom_small.sm` (113), `r135_ws1_large_indirect.sm` = `r136_ws1_funcval_large.sm` (243), `r135_ws1_small_indirect.sm` = `r136_ws1_funcval_small.sm` (226). Each pair is cited by its rounds' reports. |
| Round 42 `.part` files (reconstruction) | 602,580 | Recoverable from base `fd02405a` + `2026-10-27-round42-guard-v248.patch` (4,218 bytes, in the outbox), per the R42 report's own recipe and expected sha256 `8d05915c…`, which matches the concatenation exactly (independently re-verified in this round). Not a copy that exists — a rebuild. The rebuild was not re-run here. |

Judgement-call subtotal: 45,942 bytes. Primary COULD GO (197,927) + judgement calls (45,942) = **243,869 bytes (4.5% of the channel)**. Adding the R42 parts on the reconstruction argument: **846,449 bytes (15.6%)** — but that breaks the R41/R42 reports' part citations and relies on a rebuild nobody has re-run.

### What must stay, restated as the short list

Reports (159 files, 1,994,191 bytes). Patches (32 files, 1,422,392 bytes). Everything cited by a report (256 files cited in total, 3,766,169 bytes — including the 14 part files, the cited JSONs, the cited probes and tools, and `round39-whole-files/gates.sh` and `doc_counts_gate.py`, cited by 19 and 13 reports respectively).

---

## NOT RUN

Windows execution, Wine, the full suite, the gates, any probe program, any build, any installer or uninstaller run, any patch application, any history rewrite, any deletion — all of it, by the brief's own direction ("Read only. Nothing to compile or run."). The 5.4 MB figure is the current tip's outbox only; the clone as a whole is larger (the R154 brief notes the Windows evidence at 67 MB and the repository at 112 MB — those are outside this task's scope).

## Could not determine from source (consolidated)

- Whether any report's prose fully duplicates any given uncited JSON's data (checked only for `r130.json`, whose headline figures match its report; the other 24 were classified on citation alone, not on a field-by-field prose comparison).
- Whether the R42 patch applies cleanly to base `fd02405a` today (the R42 report says it was verified with `git apply --check` at the time; re-running that is execution, outside this read-only task).
- Whether the R41 whole file could be rebuilt by applying the R38 guard hunks to the v246 base — no patch or recipe for it exists in the tree, so it is treated as unrecoverable.
- Whether Sarvam or the owner actually reads the uncited JSON companions (no usage record exists in the tree).
- Whether any native run has exercised the new `E_VRIKSHA_SEEMA` hint path, or the `r58_fold_tree` guard change (both are code facts; runtime behaviour needs execution, forbidden by the brief).
- Which document first cited `r23_check_call` (still undetermined; the name occurs in the tree only in the R148 report that corrects it).
- The measurements R152 already left unverifiable (the §3 "+5% to +282%" benchmark, the §6d 4,000-call and byte-count figures, the §16 200-million timing, the §19 measured figures) — unchanged at v315.
