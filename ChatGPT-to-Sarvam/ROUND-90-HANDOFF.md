# Sutram ROUND-90 — ChatGPT → Sarvam (2026-10-20)

**Assignment:** [ROUND-90](../Sarvam-to-ChatGPT/ROUND-90.md), including appended **F8 WS4**. **Pinned compiler-source baseline:** main v253 `7ec9c9b58498bb34b826ea6abbcbc5cf2e2f7ec4`. **Classification: verified static/source analysis and deliverables, NOT native execution.** I read the newest actual GitHub files and avoided compiler, language-pack, Project Master and test changes. The user manually initiates each round; no monitor or CI was created.

## WS1 — R83's 36 excess markers versus Claude R21's zero

- [Machine-readable **all 36** original flagged rows](ROUND-90-WS1-36-PLACEHOLDERS.json), including pack, message key, line number, marker, current exact translated string, Sanskrit reference, literal romanized default and counts.
- [Single grouped comparison and decision](ROUND-90-WS1-PLACEHOLDER-RECONCILIATION.md).

Read `tools/r83_pack_structure.py`, `Claude-to-Sarvam/evidence-r21/pack_structure_check.py`, current canonical Sanskrit and all six impacted draft `.sandesh` packs; the six source blobs match R83's historical source identities. Verified current `.lang` word tables also include `vitti` and `mala` in all six.

**Independent count:** 6 affected draft packs × 6 flags per pack = **36 occurrences**, over five distinct message keys (six key/marker combinations because `msg_shell_help` contributes two flags). For every row, the translated marker count is one greater than **Sanskrit's placeholder count** (R83's extra candidate), but **does not exceed** the number of printed instances of the same roman keyword in the original default comment (Claude R21's rule). Example: default `vitti x = 5 ... vitti-ghoshana` has two `vitti` words; Sanskrit leaves one `{kw:vitti}` and translates the prose occurrence; Tamil has two `{kw:vitti}`, reusing the local keyword in prose.

**Judgment: Claude's criterion is the appropriate automatic *structural validity* rule here.** Our 36 extra-versus-Sanskrit flags are true numerical differences but **not structural errors** or mandatory changes. Keep them optional *editorial/linguistic* review suggestions if a speaker is ever available; do not block any DRAFT pack over them. Neither checker claims human grammar correctness. Both previously found zero hard violations over 1,408 entries and agree on the other five identical-short-string heuristics. No historic report was rewritten or hidden.

## WS2 — DRAFT review form

**PASS; no changes needed.** [Round-87's one-pass DRAFT sheet](ROUND-87-WS1-DRAFT-PACK-REVIEW.md) matches the purpose of the [Round-86 supported sheet](ROUND-86-WS3-PACK-REVIEW.md): eight pack sections, **33** distinct exact message strings from source, **39** original review flags, explicit current wording, doubtful wording/question and KEEP/REPLACE fields. The 36 flags from WS1 remain optional stylistic review, not confirmed defects. See [WS2/WS3 independent source check](ROUND-90-WS2-WS3-REVIEW.md).

## WS3 — Project Master boundary

**PASS: Sarvam already inserted it on main in v250; no further insertion needed.** The current `PROJECT-MASTER.md` Git blob `fc949af4120bff06dbf1de66527623a2b6458659` contains the boundary paragraph **exactly once** in Section 6, immediately after Era 4 (the Sanskrit rename) and before `Where the numbers stand now`. It correctly states R85's pinned v229 scope: **202 / 978 live eligible files audited, 776 NOT audited**, not a whole-tree guarantee. [R88's insertion instructions](ROUND-88-WS1-MASTER-INSERT.md) were already acted on. **Draft PR #56** remains open even though the text is already on main; Sarvam should examine it as superseded and **not blindly merge a duplicate paragraph**. I did not edit or merge it.

## WS4 — F8's self-contradictory “language pack not found” warning (source diagnosis)

**Detailed report:** [ROUND-90-WS4-F8-DIAGNOSIS.md](ROUND-90-WS4-F8-DIAGNOSIS.md); **16 independently matched source landmarks and excerpted lines:** [ROUND-90-WS4-F8-SOURCE-TRACE.json](ROUND-90-WS4-F8-SOURCE-TRACE.json).

### Exact mechanism, not a guess at ZIP contents

1. `src/sutram_compiler.asm:1990–1995` calls `try_load_lang` for `--lang hindi`.
2. `src/sutram_compiler.asm:1115` calls `set_lang_id` **before** opening any native-script keyword alias file; the language name is matched at **6940–6960**.
3. `try_load_lang` attempts **`lang/<name>.lang` relative to cwd** (1120–1133), then **Windows-only executable-relative `lang/<name>.lang`** (1134–1169), then a HOME user-share path (1170–1189). `load_lang_file` (1214–1417) opens/reads and recognizes native-script keyword mappings; it returns success only when `lang_kw_cnt > 0`. A file that is absent, unreadable or fails to populate keywords may cause **`.tll_fail`** (1191–1197).
4. The **diagnostic text is a different asset**: all message variants are compiled into `src/r11_sandesh.inc`; `src/sutram_compiler.asm:23179` routes every compiler message through `r11_tr`, which selects the column using the already-set `cur_lang_id` (6888–6925). The generated `r11_keys` registers **`msg_lang_fail`** (in `src/r11_sandesh.inc:73–74`) and the pack columns at 132–133.
5. Hence the warning **does not test for missing embedded Hindi error translations**, and its being in Hindi does **not** prove that `lang/hindi.lang` loaded. The source proves a semantic mismatch/ambiguous “pack not found” wording. No failed filename/error code/directory listing from the owner's ZIP was supplied, so the actual cause of that **particular** file-open/parse failure remains **UNKNOWN**. All eleven `.lang` files exist in the Git repo, but Git contents do not prove contents of the owner's portable Windows ZIP.

**Linux versus Windows:** The warning decision is cross-platform. Linux can also warn if the relative `.lang` file and HOME fallback are unavailable, even while diagnostics display in the chosen language. Windows adds an executable-relative attempt. That is a **static code-path conclusion**, not an actual Linux warning observed here; **Linux reproduction NOT_RUN**. Linux tests normally run from the repository root, where the `lang/` files exist. Moreover, `tools/test_lang_packs.py:32–44` discards compiler stdout/stderr whenever the generated binary exists; the previous gate does **not assert warning absence**, so a warning could have escaped detection on either platform.

**For Claude (source owner):** first distinguish `lang/<name>.lang` alias load from built-in messages; trace actual filename, file presence, read/parse results and `lang_kw_cnt` on the owner's Windows layout before choosing a fix. Test installed aliases and selected native-script keyword programs on **both** platforms, from repo-root and external CWD, then assert no warning when aliases genuinely load. Do **not** simply suppress a legitimate missing-keyword-file warning because messages are translated.

## Raw status / safety

[ROUND-90-OBSERVED.json](ROUND-90-OBSERVED.json) includes nine measured source/data consistency checks PASS. Additional F8 trace **16/16 source landmarks PASS**; R83 excess-marker reconciliation **36/36 rows**; R87 review **8 pack groups, 33 messages, 39 historical flags**; Master boundary **already in place exactly once**.

| Work | Outcome |
|---|---|
| Source/pack/checker files read at pinned main | PASS |
| 36 marker rows and both multiplicity rules independently compared | PASS; Claude's rule preferred for structural severity |
| F8 warning path, static translations, OS branch and test blind spot identified | PASS (static) |
| Actual reason the owner's Windows ZIP lacks/unloads native aliases | **UNKNOWN** from logs |
| Actual Linux execution reproducing F8 | **NOT_RUN** |
| Native compiler, Windows acceptance, human translation quality | **NOT_RUN** |
| Compiler, packs, Project Master, lock, accepted tests, CI, merges | **UNCHANGED** |

**End of Round 90.** Evidence and instructions are now in `ChatGPT-to-Sarvam/` for Sarvam and Claude. Do not launch the next round until the owner again says `CHECK FOLDER`.
