# ROUND-36 — the cosmetic layer

**Base:** `origin/main` at `cf203355` (v337; round written against v335). Compiler v246.
**Environment:** Linux x86-64 (this VM), nasm 2.16.03, Python 3.12.
**Delivery note:** `git push` has no credentials here; files were delivered directly
to `main` via the GitHub API (round-authorized fix), plus this report in the outbox.

## WS1 — cosmetic layer, in one pass (comments and headers only)

**Fixed, 20 lib files, 47 comment lines changed, 0 code lines changed:**
- **18 headers** with old file names → current names (baseconv→aadhar, num→ank,
  serial→anukram, bigint→brihat, math→ganit, hash→gudh, strb→khand, array→mala,
  map→nighantu, file→patra, result→phal, fmt→roop, util→sadhan, set→sangrah,
  sort→shreni, list→suchi, strconv→vakyank, string→varna).
- **2 Usage lines** — `lib/sadhan.smlib:4` (`ayojan util` → `yoj sadhan`),
  `lib/suchi.smlib:211` (`ayojan sort` → `yoj shreni`).
- **19 `pankti` comment lines** → `mala` (aadhar 5/15/74, ganita 188, gudh 12/28,
  nighantu 4, phal 4, roop 8, sankhyiki 120, shreni 4, suchi 4/33, vakyank
  6/12/81/83/235, varna 127).
- Also fixed, on the same lines / in the same headers: old-file references in
  comment bodies (`lib/hash.smlib` → `lib/gudh.smlib`, `lib/strconv.smlib` →
  `lib/vakyank.smlib`, `lib/sort.smlib` → `lib/shreni.smlib`,
  `lib/baseconv.smlib` → `lib/aadhar.smlib`, `lib/string.smlib` →
  `lib/varna.smlib`, `fmt`/`strconv` module prose → `roop`/`vakyank`,
  `` `strb` idiom`` → `` `khand` idiom``).
- **No identifier changes.** `util_chinha` stays, per the round (owner's decision).
- Left alone as historical: `lib/varna.smlib` R7/R8 notes naming baseconv/strconv
  as they were at that time.

**Verification — the guard, proved two ways:**
- Before/after compile, same compiler, all 551 programs: **0 differ** (exit code,
  stdout, stderr, and executable bytes all identical). A comment change altered
  not a single compiled byte.
- Full guard on v337 (committed compiler vs fresh build): **551 programs, 470
  byte-identical, 81 refused identically, 0 DIFFER.** (The round's "476" is the
  Windows session's count; Linux holds at 470.)
- `proof_lib` 224/224, `proof_props` 86/86 still pass.
- Post-fix grep: 0 `pankti`, 0 `ayojan`, 0 old `lib/<old>.smlib` headers left in `lib/`.

## WS2 — regenerated page

`docs/sutram-stdlib.html` regenerated via `tools/gen_stdlib_ref.py` from the
fixed library: **24 modules, 305 functions, `meru_mala` present, `meru_pankti`
absent.** Not 303, not the old name — no generator defect.

## WS3 — stale-claims count

`tools/doc_stale_claims.py`: **160 hits on v337**, unchanged from v334 (R35).
The one known FALSE from R34 (`docs/sutram-design-parameters.html:365`,
"there is no FFI", 2 hits) is still present; the rest are TRUE limits,
policies, design proposals, or HISTORICAL entries.

## Files delivered (direct to main)

20 lib files (cosmetic only) + `docs/sutram-stdlib.html` (regenerated) + this report.
