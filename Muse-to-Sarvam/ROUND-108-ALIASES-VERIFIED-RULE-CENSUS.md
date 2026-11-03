# Round 108 — The 22 live aliases verified by body, the root-versus-noun rule, census on v292

Base: main at v292 (worktree `f363c543`, compiler `Sutram 1.0 (v292) - sampurna sutra`, unchanged). No tree changes, no implementation. Every alias below was run, not just compiled — except where stated.

## WS1 — the 22 live aliases: 21 bodies match their names, 1 name is right and its body is not

The alias mechanism (R111): the new name is the primary row, the old name a second row with the same builtin id, so a program compiles to the same bytes either way; an old name in the program's own file warns once on stderr, naming the replacement (verified: compiling a `kosh_push`/`kosh_len` program prints `Sutram suchana: 'kosh_push' purana nama - 'kosh_kship' likhatu` and the same for `kosh_len` → `kosh_gan`, then runs correctly). Guard 705 programs 0 DIFFER (R111) is consistent with that: no behaviour changed.

**Kosh, all nine — PASS.** One probe (`kosh2.sm`, delivered) using only new names: push 10/20/30 → `kosh_gan` 3, `kosh_ksham` 4, `kosh_iksh` 30, `kosh_rikt` 0; `kosh_yuj` 40 → len 4, peek 40; `kosh_apanay` 10 → len 3, peek still 40; `kosh_shodh` → len 0, empty 1, cap still 4; `kosh_hri` on [10,20] → 20, len 1, peek 10. Every name matches its body: `kship` throws in, `hri` takes the top, `gan` counts, `ksham` is capacity (kept after clear), `rikt` is empty, `shodh` clears, `yuj` joins at the end (the source comment says "FIFO append = kosh_push"), `apanay` removes the first and keeps the rest.

**`kosh_iksh` specifically — `iksh` (look) names it, and does NOT imply an index.** Peek takes ONE argument and returns the last element (30 after 10/20/30, 40 after enqueue). The two-argument form refuses with `vyakaran dosh` on v292, so the arity itself refutes the index reading: if it implied an index, it would take one. "Look" is exactly peek — look at the top, don't take it. The "last" comes from the stack discipline (peek = top = last pushed), not from the word, and that is fine: the word names the act (looking), the discipline supplies which element.

**`pankti_gan` — PASS.** `pankti_gan` on a 3-element mala = 3; on a string = 0. Mala-only, unchanged from `pankti_len`.

**`jala` family, all four — PASS end to end.** A server probe (`srv.sm`, delivered) plus a real Python client: `jala()` → fd 3 (a socket), `jala_bandh(3, 45999)` → 0, `jala_shru(3)` → 0, `jala_grah(3)` → 4 after the client connected. Socket, bind, listen, accept all work under the new names.

**`akshar_laghu`/`akshar_guru` — PASS.** 65 → 97, 97 → 65, as before.

**`anka_akshar` — name true, body note (pre-existing).** The name is right for the intent (number → letter, the exact inverse of `aksharank`, which returns 66 for "B"). The body still returns a pointer to a temp buffer, so `likha` prints the address, not the letter. That is the R106 trap shape, not a rename issue: the rename does not fix the pointer return, and does not worsen it.

**`vartani_sandhi` — PASS on the body, with the same likha note.** `shabda(vartani_sandhi("ab", "cd"))` prints `abcd` — the concatenation is correct. `likha` on the same call prints the address, because call results are not marked as strings for `likha`'s text printing. Same pre-existing likha-marking issue as `anka_akshar`, not a name issue: `sandhi` (joining) is exactly what concatenation does.

**`likha_santat` — PASS.** `likha_santat(7)` then `likha(8)` prints `78` on one line — no newline from `santat`, as before.

**`likha_rup` — PASS, with a precision note (a wash, not a failure).** The body is label-plus-value sequential printing: `likha_fmt("x = ", x)` → `x = 42` (the `format_demo` golden). It never did printf substitution — my probe `likha_rup("a=%d", 5)` prints `a=%d5`, which is correct for this body (%d stays literal). `rup` (form) does not precisely say "label plus value" — but neither did `fmt`, which over-promised formatting. No worse, no better, on precision.

**`smaran_pratilip` — PASS.** It is a byte copy, `n` in bytes: copying 24 bytes (3 × 8) from [1,2,3] gives [1,2,3]. (My first probe passed 3 and got [1,0,0] — correct for 3 bytes, my probe was wrong, not the body.)

**`sankhya_bindu` — the name is right, the body cannot deliver a dot for any Sutram-constructible input. Pre-existing defect, needs a redesign, not a rename.** The handler (`.ge_call_vecdot`) emits `movups xmm0, [rsi]` / `movups xmm1, [rdx]` — it reads 16 bytes (4 × 32-bit floats) from each argument's pointer — then `mulps`, two `haddps`, and `movd eax, xmm0`, returning float bits that `likha` prints as an integer. No Sutram value holds 4 contiguous 32-bit floats: a kosh's pointer gives its header (so a kosh of dasham [5,6,7,0] dots to 0), a mala's slots are 8 bytes (so a mala [5,6,7] dots to garbage, 2 in my probe). Even a correct dot would print as bits, not the value, through `likha`. The old `sankhya_dot` had the same body, so the alias changes nothing — but the defect should be recorded: a dot product needs a double-based implementation returning a `dasham`, and that is Claude's/Sarvam's work, not a rename.

**`asti`/`nasti` — PASS.** `1 asti 1` = 1, `1 nasti 2` = 1, `1 nasti 1` = 0, and `yadi (2 asti 2)` reads as a sentence ("if 2 is 2") and runs.

**`tyaj` (shell, not a builtin) — PASS.** `tyaj()` in a program refuses (`agyat prakriya`), confirming it is shell-only. In the REPL (`-i`): `tyaj` exits cleanly (0, "Namaste! Satra samapt."); `exit` warns, naming the replacement (`'exit' purana nama - 'tyaj' likhatu`), then exits; `sahayata` prints help. One docs gap: the REPL banner and help still list `nirgat`, not `tyaj`, as the exit word — a new user learns the synonym, not the primary. (Nirgat itself does not warn, so it is a valid synonym, not a deprecated alias; the banner should still name `tyaj` first.)

**Not live, correctly:** `truti` is blocked (Error left alone — see below); `patra`/`rekha`/`kuru` as message words had 0 instances to change (R111: "file, line, hai, karo — 0 instances in any compiler message"; one `se bhinn` string, never printed, changed to `nasti` anyway). So the 30 account for as 25 live (22 builtins + `asti`/`nasti` + `tyaj`) + 1 blocked (`truti`) + 3 message words with nothing to change + `to` dropped (not a name).

**On Error being left alone:** R111's reason is WS4, not the packs — and it complements, not contradicts, R107. R107 said the `.sandesh` edit crosses the frozen-pack rule as written and recommended a narrow owner exception; R111 accepts Sarvam's view that the pack edit does not cross it, but stops on the other half: 443 guard programs carry a runtime message, so changing `Error` everywhere makes 443 programs DIFFER in message bytes only, which WS4 says to stop on. The full change now needs two decisions from the owner: the pack exception (R107) AND accepting the 443 (R111). With both, it is a round of its own. Nothing here changes R107's recommendation.

## WS2 — the root-versus-noun rule: two tiers, grandfather the roots, fix meaning not form

**The rule.** Concepts and keywords must be complete words. Function names use the shortest recognizable form — root, stem, or noun — that unambiguously names the action. Existing roots are accepted as precedent, not regularised. A root that is wrong on meaning is fixed; a root that is merely a fragment is not.

**Why two tiers, from the tree itself.** The tree already follows this rule implicitly; I am stating it, not inventing it. Concept and keyword names are complete words: `mandapa` (62 uses in the compiler source), `parimita` (13), `kshetra` (3), `nivartanam` — a student holds a concept by its name, and a fragment breaks the mental model (that is why `paripurna` → `purn` was rejected). Function names are short forms, and always have been: `yoj` is the include keyword (a root, in every importing program); `rakh` (to keep) heads 14 lib definitions; `khip` (to throw/write) lives in `anukram_khip_i64` and `anukram_khip_aayam_purva`; `likha`, `grahan`, `padh`-family names are short, not full nouns. A function is called, not held as a concept — brevity and recognizability beat grammatical completeness at a call site, and the call site already disambiguates (the `kosh_` prefix says which object, the verb says the act).

**Why not regularise.** Renaming a stable root buys a vowel at the cost of churn: `yoj` → `yojana` would put two names for include in every program's first line (the alias would be the common form, the primary the rare one — the reverse of what "primary" should mean), and the docs, tests, and goldens would churn for no behaviour. The alias mechanism makes regularisation possible, not desirable. The same applies to the just-built `kosh_apanay`: it is a stem, not the full noun `apanaya`, and renaming it now — a round after building it — would churn the vocabulary that just landed, for one vowel. Grandfather it, as with `yoj`.

**What this decides for the final 30.** The 12 root/stem forms in it (`kship, hri, gan, iksh, shodh, yuj, apanay, tyaj, bandh, shru, grah`, `gan` twice) are ACCEPTED under the function-name tier: each is short, recognizable, and unambiguous in its `kosh_`/`jala_` context (`kosh_kship` can only mean throwing into a kosh; `jala_grah` can only mean taking a connection). The full-noun tier still governs new concepts and keywords — a future `mandapa`-scale name must be a complete word, and a future function name that is ambiguous as a root (two plausible acts) must be made a noun or compound. And the exception stays: meaning errors are fixed regardless of form, as `muc`/`tas`/`bindu` were.

**One correction to the brief's premise.** The brief says the tree already has roots (`yoj`, `khip`, `shodh`). Two of three verify: `yoj` (keyword) and `khip` (`anukram_khip_*`) do. `shodh` as a pre-existing root does not — its only instance in `lib/` and the compiler source is the new `kosh_shodh` itself. That does not change the rule (`kosh_shodh` is accepted under the function tier anyway), but `shodh` is not a precedent; it is the case under discussion. A full noun does appear as a function-name component, for balance: `bahu_ganana` (`kalana.smlib`, counting, `ganana` a complete noun) — so the tree has both tiers in function names too, and the rule above is what separates them.

## WS3 — census on v292 (same method, R96 scripts re-run, calibrated on v290)

Denominators first, because the brief's number is stale again: **v292 has 299 top-level examples (315 recursive, 299 + 16 subdir), not 291** — 291 is v290's count, stale a seventh time. Suite 295 = 299 − 4 without expectation (215/216/217/219, unchanged). Lib: 306 functions, 24 modules, unchanged.

| Question | v290 (R106) | v292 (this round) | Change |
|---|---|---|---|
| Q1 — allocate inside a loop | 6 (Q1a 3 = 258/303/304, Q1b 0, Q1c 3 = 217/237/268) | **6, same six** (Q1a 258/303/304; Q1b 0; Q1c 217 (`ank_tak_varna`), 237 (`gahra`), 268 (`varga_yoga`)) | none |
| Q2 — grow a kosh >1000× | 0 definite, 1 potential (286 `varg_yog(n)`) | **0 definite, 1 potential (286, unchanged)** | none |
| Q3 — allocate without mandapa, textual | 58 examples + 26 lib | **60 examples + 26 lib** | +2 examples, lib unchanged |
| Q3 — runtime-true | 57 examples (314 compile-refusing) | **59 examples** (314 still compile-refusing, still the only one) | +2 |

The Q3 +2 is exactly the two new vocabulary examples, `322_r111_new_names.sm` and `323_r111_old_names.sm` — both allocate without a mandapa, both are tests of the vocabulary change, not new real programs. No file left Q3; the 58 are all still there. The known blind spot from v287 stands: the method does not see `+`-allocation (307's loop string still allocates a fresh persistent string per pass), so an extended Q1 would still be 7.

**How many examples use an old name — 70, plus 3 lib files.** That is the number the aliases protect, and the retirement signal: the old names cannot be retired until those 70 are migrated (or the owner keeps the alias promise forever). The v291 count was 69, so the delta is exactly +1 file: `323_r111_old_names.sm`, which uses old names deliberately (to prove they still work and warn) — 15 of them (`kosh_push/pop/len/cap/empty/peek/clear/enqueue/dequeue`, `pankti_len`, `lkhb`, `char_upper/lower/from`, `vartani_cat`). Per-name on v292 (code-stripped): `kosh_push` 49, `kosh_pop` 13, `kosh_len` 18, `kosh_cap` 6, `kosh_empty` 2, `kosh_peek` 1, `kosh_clear` 1, `kosh_enqueue` 1, `kosh_dequeue` 1, `pankti_len` 11, `netsock`/`netbind`/`netlisten` 1 each, `netaccept` 0, `char_lower` 1, `char_upper` 2, `char_from` 1, `vartani_cat` 1, `lkhb` 7, `likha_fmt` 3, `sankhya_dot` 0, `smaran_cp` 0. Lib: 3 files (`kalana`, `samanvaya`, `sankhyiki`, each `kosh_push` + `kosh_len`), unchanged. The broader warning signal (R111's census) is 125 of 705 guard programs warning — the 70 examples plus lib tests and probes. Zero old-name users, and therefore safe to retire without breaking a program, are `netaccept` and `sankhya_dot` — but retiring them would still break the alias promise, so "safe" here means "no program breaks", not "retire them".

## What was NOT run

Windows, browser, implementation (none authorized; the aliases are Claude's v292 build, verified here, not changed), native-speaker review, full suite (no tree changes; R111's numbers stand: suite 295/299, gates 60/1/1 with the new R111 vocabulary gate, guard 705 0 DIFFER on ELF, PE, and Wine). R105's pending WS2 — the attack on ChatGPT's R178 arena DESIGN itself — is still pending and is not covered by this round.
