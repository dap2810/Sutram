# ROUND-44 — rename checklist + pankti breakdown (no code changes)

**Base:** `origin/main` at `307520c1` (v363; round written against v362),
compiler v249.
**Environment:** Linux x86-64 (this VM).
PASS / FAIL / NOT-RUN separately throughout.
**No code changes made. No files added or modified in the tree.**

## WS1 — every caller of the three renaming builtins, independently

Method: `grep -rn "vartani_len|vartani_cmp|vartani_cp"` over every
`.sm` under `examples/` and `tests/` (recursive), on current main.
Every hit below is a call (name followed by `(`), none is a comment
or a definition.

### The list — 9 call sites in 7 files

| File | Line | Call | Renames to |
|---|---|---|---|
| `examples/250_r26_dosh_handler.sm` | 16 | `vitti n = vartani_len(s)` | `vartani_aayam` |
| `examples/full_demo.sm` | 26 | `likha(vartani_len("Sutram"))` | `vartani_aayam` |
| `examples/import_demo.sm` | 22 | `likha(vartani_len(s))` | `vartani_aayam` |
| `tests/r50_check/byte_truncation.sm` | 8 | `likha(vartani_len(buf))` | `vartani_aayam` |
| `tests/r50_check/runtime_hi.sm` | 8 | `likha(vartani_len(buf))` | `vartani_aayam` |
| `tests/r50_check/runtime_hi.sm` | 9 | `likha(vartani_cmp(buf, "hi"))` | `vartani_tul` |
| `tests/r54_check/raw_valid.sm` | 18 | `vartani_cp(b + 48, "YES")` | `vartani_pratilip` |
| `tests/r54_check/raw_valid.sm` | 21 | `likha(vartani_len(b + 48))` | `vartani_aayam` |
| `tests/r56_check/global_string_pointer.sm` | 2 | `prakriya length() { prati vartani_len(greeting) }` | `vartani_aayam` |

Totals: `vartani_len` 7 sites, `vartani_cmp` 1 site, `vartani_cp`
1 site. **Check Claude's rename against these 9 lines, not only
against his own list.**

### Separately, outside WS1's scope but needed for a complete rename

The brief asked for `.sm` files only. The library itself also calls
`vartani_len` in code (not comments) — 9 sites, all `vartani_len`,
which a rename must also update or the library breaks:

- `lib/gudh.smlib:30` — `prati fnv1a(s, vartani_len(s))`
- `lib/khand.smlib:99` — `prati vartani_len(s)`
- `lib/varna.smlib:19, 55, 69, 80, 90, 113, 114` — 7 sites
  (`prati vartani_len(s)`; `vitti n = vartani_len(s)` ×4;
  `vitti na = vartani_len(a)`; `vitti nb = vartani_len(b)`)

No `vartani_cmp` or `vartani_cp` calls in `lib/` code. The compiler
source itself defines the three builtin names (`bn_vartlen`,
`bn_vartcmp`, `bn_vartcp`); that is the definition side of the same
rename, not a caller.

## WS2 — `pankti` in the compiler: breakdown of all 34 occurrences

Method: `grep -n "pankti" src/sutram_compiler.asm` on current main.
Count confirmed: **34 occurrences on 33 lines** (line 331 contains
two: `r4_o_pankti` and `kw_pankti`).

### Headline

- **Line sense (correct Sanskrit, keep): 2**
- **Array sense: 32**
- **Retired array word that should now be `mala` as a defect: 0.**
  The array keyword's Latin spelling is already `mala`, its
  Devanagari spelling (पङ्क्ति) is still the current Devanagari form,
  and the one live user-visible `pankti` name (`pankti_len`) is a
  deliberate builtin, not a leftover — renaming it would be a breaking
  rename round, like `vartani`, not a cleanup.

### The 34, classified

**A. Line sense — 2 (keep, correct Sanskrit in error messages)**
- 345: `msg_err_line db "... vyakaran dosh, pankti "` — "grammar
  error, line N"
- 387: `r32_msg_ffi_bad db "... pankti "` — FFI error, line N

**B. Old-keyword compatibility table — 3 (intentional, keep)**
- 331 (×2): `r4_o_pankti, kw_pankti` in `r4_old_kw`, alongside the
  other retired spellings (`anyatra`, `punaravartana`, `pratiyati`,
  `uddeshya`, …)
- 338: `r4_o_pankti db "pankti",0` — the old spelling string itself
- Purpose: old programs using `pankti` still parse. Renaming these
  would break that compatibility, not fix a leftover.

**C. Array-keyword internal symbols — 4 (spelling already new)**
- 499: `kw_pankti` in the keyword table (symbol name only)
- 515: `kw_dev_pankti` in the Devanagari keyword table
- 707: `kw_pankti db "mala",0` — the Latin spelling is already `mala`
- 722: `kw_dev_pankti` bytes for पङ्क्ति — the Devanagari spelling,
  still the current Devanagari form for array per
  `lang/sanskrit.lang` (पङ्क्ति → `mala`)
- Renaming these symbols would be cosmetic only; the user-visible
  words are already correct.

**D. Builtin `pankti_len` — 13 (live builtin, not a leftover)**
- Definition/table: 214 (`BN_PANKTILEN equ`), 293 (comment),
  561 (builtin table), 764 (`bn_panktilen db "pankti_len",0`)
- Call handling: 15263, 16932, 16934, 16937, 16939, 16951, 16954,
  16958, 16970 (labels and comments for `pankti_len` calls)
- Verified live: `pankti_len(a)` compiles on a `mala a[3]`;
  `mala_len(a)` fails with `Sutram Error: agyat prakriya: mala_len`.
  `docs/LANGUAGE-REFERENCE.md` documents `pankti_len` as "length of
  a constant-length `mala`" — mixed vocabulary, but a live name.
  If the owner wants `mala_len`, that is a deliberate breaking
  builtin rename (with all its callers, in WS1's spirit), not a
  stale-word fix.

**E. Internal comments and labels, array sense — 12 (cosmetic only)**
- Comments: 900 (`pankti` names in scope), 8757 (historical example
  `pankti arr[10]`), 12885 (real `pankti` array), 13239 (fixed
  `pankti`), 15060 (1=fixed `pankti`), 16933 (real `pankti`
  declarations), 20538 (`pankti` array's element-0 pointer), 20983
  (not `pankti`)
- Labels: 13245, 13258 (`.gs_ai_check_pankti`), 15044, 15057
  (`.ge_index_check_pankti`)
- Renaming these to `mala` would change no user-visible behaviour.

### Summary table

| Class | Count | Action |
|---|---|---|
| Line sense | 2 | Keep |
| Old-keyword compat | 3 | Keep (deliberate) |
| Keyword symbols (spelling already new) | 4 | Cosmetic only |
| Builtin `pankti_len` (live) | 13 | Rename only as a deliberate breaking round, if wanted |
| Comments / labels | 12 | Cosmetic only |
| **Total** | **34** | **0 defects** |

## WS3 — the guard: this round's number

Method as in R40–R43: committed `./sutram_compiler` (from `HEAD`) vs a
fresh build from `src/r68_compiler_entry.asm` (byte-identical to the
committed binary), every `.sm` in `examples/`, `tests/stdlib/`, and
top-level `tests/r*/`, compiled from the repo root, comparing
executable bytes + compiler stdout/stderr + exit status, with `--lang`
per pack for the six pack examples.

**Current main `307520c1`: 576 programs, 488 byte-identical
executables, 88 refused identically, 0 DIFFER.** Unchanged from R43.

## Delivery

- This report: `Muse-to-Sarvam/2026-10-27-round44-rename-pankti.md`
- No other files. No tree changes.
- `git push` has no credentials here, as before; delivery via the
  GitHub API. The local tree was left at main, unmodified.
