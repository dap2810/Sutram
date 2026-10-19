# ROUND-03 / WS3 — documentation that quotes compiler messages; the ROUND-01 claims re-checked

**Date:** 2026-10-19 · **Base:** main `85d6c5f` (v169) · **Code:** branch `claude/round-03`, commit `6f13c93e`

---

## 1. What I did

1. Scanned `README.md`, `PROJECT-MASTER.md`, `PROJECT-OVERVIEW.md`, `AGENTS.md`, `ROADMAP.md`,
   `INSTALL-WINDOWS.md`, `docs/*.md` and `docs/*.html` (excluding `CHANGELOG.md` and the handoff
   folders). I looked for every quoted compiler, shell or runtime message: each "before" string of the
   R2-03 translation table, plus 48 more fragments (`OK: compiled`, `near token`, `Hint:`, the shell
   banner, `Language pack loaded`, …). That gave 121 raw hits, each read in context.
2. **Triggered every replacement message with the compiler** rather than copying it from source, except
   where noted.
3. Applied the corrections on the branch. Book transcripts were **re-taken from the compiler**, not
   edited by hand (§3).
4. Re-measured every ROUND-01 WS3 claim on v169 (§5).

## 2. Current text, observed (the evidence for every correction)

```
$ sutram namaste.sm n.bin                 → Siddh: 97 byte sankalit
$ sutram --lang gujarati … ; --lang nosuchpack …
                                           → Bhasha pak prapt: gujarati  /  Chetavani: bhasha pak nahi mila: nosuchpack
$ sutram -i   (in a PTY)                   → Sutram khol v1.0 - sampurna sutra
                                             Sutram kathan likho aur Enter dabao. Turant chalega.
                                             Aadesh: sahayata (sahay) | nirgat (nikas) | sarvam (dekho)
                                             sutra> vitti x = 21   → Siddh: 54 byte sankalit
                                             sutra> likha(x / 3)   → Siddh: 201 byte sankalit / 7
                                             sutra> nirgat         → Namaste! Satra samapt.
$ sutram galat.sm g.bin   (mukhya() { vitti x = 5 / vitti y = (x / likha(x) })
                                           → Sutram Error: vyakaran dosh, pankti 4:5, shabd 'likha'
                                                   likha(x)  /  ^  /  Sanket: is sthan par shabd aur vyakaran dekho.
runtime: kosh_pop / kosh_peek / kosh_dequeue on empty → Sutram Error: rikta kosh se kosh_pop / …_peek / …_dequeue
kosh_len on a vitti      → Sutram Error: kosh prakriya hetu kosh-vitti avashyak
kosh_push on kosh param  → Sutram Error: kosh tark par kosh_push asamarthit
trap build, a+1 at MAX   → Sutram Error [E_INTEGER_TRAP] <path>:3: yog atipravah
```
The interactive shell and piped stdin give **different** byte counts (piped: one `Siddh: 204` for both
lines). The books show an interactive session, so I used the PTY numbers.

## 3. Corrections applied (branch commit `6f13c93e`)

| File | What changed |
|---|---|
| `docs/KOSH-BUILTINS.md:107–109, 119` | `kosh pop/peek/dequeue from empty mala` → `rikta kosh se kosh_pop/peek/dequeue`; `kosh builtin requires a kosh variable` → `kosh prakriya hetu kosh-vitti avashyak` |
| `docs/KOSH-REUSE.md:42` | → `kosh tark par kosh_push asamarthit` |
| `docs/LANGUAGE-REFERENCE.md:374–375` | the three empty-kosh messages |
| `docs/LANGUAGE-REFERENCE.md:182, 188, 295` | `chakra i = 1 to 5`, `chakra j = 5 to 1`, pack-table row `to` → `tak`. **Sample 007 now compiles** (`Siddh: 1190 byte sankalit`, prints `big 1 2 4 …`). It failed in ROUND-01 and on v169. |
| `docs/OVERFLOW-SAFETY.md:85`, `docs/SPECIFICATION.md:158` | `<patra>:<line>` → `<file>:<line>` (rename damage inside a placeholder; the real format was observed with a trap build) |
| `docs/NEGATIVE-CORPUS.md:22–27` | the six expected diagnostics now match the re-pinned `manifest.json` (R3-01 §4.2); "Unterminated varna" / "diagnostic varna" → "string" |
| `docs/NEGATIVE-CORPUS.md:64–71` | pin table regenerated from the manifest; `.vardh` → `.inc` |
| `docs/BUILDING.md:11, 13` | core blob → the re-pinned value; "Neither patra" → "Neither file" |
| `docs/sutram-book-english.html:622` | troubleshooting row `language pack not found` → `Chetavani: bhasha pak nahi mila` |
| **six books** (en, gu, hi, sa, ta, te) | first-compile line → `Siddh: 97 byte sankalit` (the book's own namaste program, compiled); shell banner → the real three-line banner, then `Siddh: 54` / `Siddh: 201`; pack transcript → `Bhasha pak prapt: <pack>` + `Siddh: N byte sankalit`, with N from **compiling that book's own pack program with that pack** (en 228, gu 456, hi 415, ta 426, te 322; sa has no pack transcript); error transcript → now **shows `$ cat galat.sm`** (it never showed the program, so its output could not be checked) followed by its exact output; the line `Run 'sutram -i' and type 'sahayata' for help.` is **removed — the compiler never prints it** (it is an unlabelled, unreferenced string at `src/sutram_compiler.asm:401`) |

**Flagged and deliberately left as written.** These are historical records of what a round's compiler
printed:
- `docs/R63-KOSH-BUILTINS.md:15`, `R64-KOSH-DIAGNOSTICS.md:15–17`, `R65-SOURCE-REVIEW.md:25`,
  `R68-LEXICAL-DIAGNOSTICS.md:8,26,48`, `sutram-audit.html:110–147`
- `docs/CHANGELOG.md` (17 lines)

Two notes on that list:
- `R68-LEXICAL-DIAGNOSTICS.md` is also the only specification of those two diagnostics. A one-line
  "translated in v169 (ROUND-02)" note at its top may be better than leaving it silent. Your call.
- `sutram-audit.html` quotes `'end of patra'`. The compiler never printed that; it is rename damage
  inside a historical quote.

**Matches source, no change:** `docs/R71-MEMORY-BOUNDARY.md:66,72`. The R71 boundary messages are still
English in `src/r71_unsafe_integration.inc:5–9`. R71 is outside the canonical build, and ROUND-02 did not
translate it.

**A claim to fix, not a quote:** `sutram-book-english.html:293` says "Errors also localize
automatically." Only the five `tbl_*` families follow `--lang`: the parse-error line/near/EOF/hint and
input-file-open messages. Every other diagnostic is compiled-in Sanskrit-register text whatever the
pack. Partly true. I left the wording to you.

**And one claim in PROJECT-MASTER that has moved:** `PROJECT-MASTER.md:204–205` illustrates the Windows
console defect with the en-dash in `Sutram 1.0 (v29) – the complete thread`. The banner is now pure
ASCII (`Sutram 1.0 (v160) - sampurna sutra`), so the example no longer reproduces. The defect itself
stands, and it now affects every pack message. It would be better to cite a current non-ASCII string.

## 4. Verification

```
book code blocks with chakra, all six books + English:  30 / 30 compile   (18 programs; 12 fragments wrapped in mukhya())
book code blocks still using ' to ' after chakra:        0   (25 before)
LANGUAGE-REFERENCE.md sample 007:                        compiles (was FAIL in R1 and on v169)
sh tools/gates.sh on the branch:                         suite 189/4 … (R3-01 §7)
```

## 5. The ROUND-01 WS3 claims on v169 — the delta, not the list

**Key fact:** `git diff --stat feef075 85d6c5f` over every audited document lists only
`docs/CHANGELOG.md`. **Not one audited document was edited between ROUND-01 and v169.** So every
ROUND-01 text finding was still present word for word on v169. Only claims whose truth depends on the
code could move.

| ROUND-01 claim | On v169 | After this branch |
|---|---|---|
| PROJECT-MASTER:145 "Module graph OK" | **now true** (18/18 — fixed in R2/v168) | true |
| PROJECT-MASTER:149 "GUI tests 18/18" | reproducible via `gates.sh`; measures **17/18** (`edscroll` times out; fails on the `feef075` GUI too) | 17/18 |
| PROJECT-MASTER:150 "R70 6/6, native_status PASS" | **still false** (`fixture drift: bad_type`) | **now true** (R3-01 §4.2) |
| BUILDING:13 core pin; `r69_build.py` refuses main | still false | **now true** (R3-01 §4.1) |
| LANGUAGE-REFERENCE:182,188 `to` | still false | **fixed** |
| LANGUAGE-REFERENCE:374–375, KOSH-BUILTINS, NEGATIVE-CORPUS:27 quotes | **wrong in a new way** (now quote the pre-R2 English) | **fixed** |
| PROJECT-MASTER:140, 238; OVERVIEW:97; README:140 — suite 187 | **newly stale** (188 on v169) | 189 on the branch |
| PROJECT-MASTER:148 — 207 examples | **newly stale** (208) | 209 on the branch |
| PROJECT-MASTER:151–152 sizes, file count; OVERVIEW:54, 57, 99, 134–139, 147; README:56, 64 | still stale | still stale — not mine to choose the new numbers; `gates.sh` should own them |
| PROJECT-MASTER:238–243 §11 expectations (183/76/12·9); :257 "0 std" open item | still stale | still stale |
| README:60–61 "`mala`, `io`, `net` are comment-only sketches" | **still false** (`mala.smlib` has 8 `prakriya`; no `io`/`net` exist) | still false |
| LANGUAGE-REFERENCE:134–136 "at most two modules" | **still false** (four `yoj` compile and run) | still false |
| LANGUAGE-REFERENCE:127–132 per-module counts | still stale | still stale |
| `sutram-vocabulary.html` E_VYAKARAN… / `--janch`… | **still not implemented** (R2 kept every `[E_…]` tag, as the brief required) | still not implemented — a plan presented as done |
| the ~58 prose-damage sentences (R1 §4.8) | **all still present** | still present, except the ones in files I touched for quotes (NEGATIVE-CORPUS, BUILDING, OVERFLOW-SAFETY, SPECIFICATION) |
| **new prose damage R1 missed** | PROJECT-MASTER:62 "One hand-written NASM patra", :273 "gap suchi"; README:100 "or sangrah `SUTRAM_LANG`" (= set); book-english:260 "added *to* a growing session" with *to* in a keyword span | still present |

**Counts:** of the ROUND-01 claim rows, on v169 **1 had become true**, 1 partly true, **6 were newly
stale or wrong in a new way**, and the rest were unchanged. This branch makes **5 more true** (R70, the
build pin, sample 007, the three quoted-message families). The remaining stale numbers and prose are
listed above. I have **not** fixed them. They are Sarvam's documents, and the brief asked for a
re-check. If you want them done, it is one documentation-only commit and I will send it.

## 6. What I did not do

- Did not edit historical round docs or the CHANGELOG.
- Did not run the Hindi, Tamil or Telugu books' pack programs *as shown in those books* with anything
  but their own pack. Each was compiled once with its pack, and that number is what the book now shows.
- Did not change the stale counts or the non-quote prose damage (§5).
- Windows docs: NOT-RUN.
