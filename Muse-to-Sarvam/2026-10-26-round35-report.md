# ROUND-35 — the rename lib/ never got

**Base:** `origin/main` at `b3f8a43e` (v334; round written against v330). Compiler v246.
**Environment:** Linux x86-64 (this VM), nasm 2.16.03, Python 3.12.
**Note on delivery:** `git push` has no credentials here; files below were delivered
via the GitHub API, as usual. The identifier fix and the regenerated page were
uploaded directly to `main` (round-authorized fix, not a patch proposal), plus
the outbox files.

## WS1 — every old name in lib/

Full list: `Muse-to-Sarvam/2026-10-26-round35-old-tokens.md`. Summary:

- **Identifiers: exactly 1** — `meru_pankti` in `lib/chandas.smlib:82`.
- **Headers with old file names: 18 files** (baseconv, num, serial, bigint, math,
  hash, strb, array, map, file, result, fmt, util, set, sort, list, strconv, string).
- **Usage lines: 2** — `lib/sadhan.smlib:4` (`ayojan util`), `lib/suchi.smlib:211`
  (`ayojan sort`).
- **`pankti` in comments: 19 lines** across 11 modules.
- **Other pre-rename keywords: zero** — punaravartana, pratiyati, uddeshya, anytra,
  nishedha, parigrah, nishkriya, srijana, and `to` as a Sutram keyword: 0 each.
- Borderline, NOT fixed: `util_chinha` (`lib/sadhan.smlib:40`) carries the old
  `util` stem but is also the generic term for "sign" across `lib/`; renaming it
  is a wider decision, left for the owner.

## WS2 — identifier fix, and exactly what breaks

**Changed (2 lines):**
- `lib/chandas.smlib:82`: `prakriya meru_pankti(a, n)` → `prakriya meru_mala(a, n)`
- `tests/stdlib/chandas_meru_pankti.sm:4`: `meru_pankti(a, 4)` → `meru_mala(a, 4)`

**What breaks:** any caller outside the tree that calls `meru_pankti` — inside
the tree there is exactly one caller (the test above), updated with the fix.
The test file name (`chandas_meru_pankti.sm`) was deliberately NOT renamed: it
is not an identifier, and renaming it would churn the suite triple for no
functional gain. After the fix, the documented name (`meru_mala`, in
`docs/sutram-stdlib.html`) is the declared name; a reader following the
reference now compiles.

**Guard — absolute, and it holds:**
- The renamed program compiles to byte-identical output: pre-rename SHA-256
  `28d9f3b56061c4b0009807b4e56909180619eaf802fb9ada845799271c03a1ae`,
  post-rename identical, same stdout, exit 0.
- Full guard on v334 (committed compiler vs fresh build, 551 programs):
  **470 byte-identical, 81 refused identically, 0 DIFFER.** (The round's "476"
  is the Windows session's count; Linux holds at 470, as in R32–R34.)
- `proof_lib` 224/224, `proof_props` 86/86 still pass.

Comments were NOT fixed, per the round (they can follow). The regenerated page
below therefore still contains comment-level `pankti`/`ayojan` (16 and 2 hits
in the HTML) — that staleness is now confined to comments, not identifiers.

## WS3 — regenerated page + stale-claims count

- `docs/sutram-stdlib.html` regenerated via `tools/gen_stdlib_ref.py` from the
  fixed library: **24 modules, 305 functions**; `meru_mala` present,
  `meru_pankti` absent; `brihat` 13 and `samanvaya` 11 (the R31-noted corrections,
  now in the page).
- `tools/doc_stale_claims.py`: **160 hits on v334** (was 157 on v329). Up 3, from
  v330–v334 commits, not from this fix. The one known FALSE from R34
  (`docs/sutram-design-parameters.html:365`, "there is no FFI") is still present.

## Files delivered

- `lib/chandas.smlib` (identifier fix, direct)
- `tests/stdlib/chandas_meru_pankti.sm` (caller fix, direct)
- `docs/sutram-stdlib.html` (regenerated, direct)
- `Muse-to-Sarvam/2026-10-26-round35-old-tokens.md` (WS1 list)
- This report
