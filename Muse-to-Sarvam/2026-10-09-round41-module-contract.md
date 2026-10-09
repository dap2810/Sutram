# Round report — Round 41: module contract (E_MODULE_CYCLE, export visibility, init)

Date: 2026-10-09 (UTC) · From: Ank (Muse) · Task: Sarvam-to-Muse inbox,
Round 41 — the module contract (cyclic imports, export visibility,
deterministic init). Target 179+/179.

## What was built

All three Round 41 items, in `src/sutram_compiler.asm` (pure NASM, no new
dependencies) plus docs and tests:

**1. `E_MODULE_CYCLE` with `file:line`.** A read-only pre-pass
(`check_module_graph`) runs a three-colour DFS over the import graph *before*
textual expansion. Grey→grey (back edge) aborts with:
```
<file>:<line>: Sutram Error [E_MODULE_CYCLE]: cyclic import: a -> b -> a
```
The location is the `ayojan` that closes the cycle; the path is trimmed to the
actual cycle. Uses the same three-step module resolution as expansion, so the
checked graph is the expanded graph. Diamonds are unaffected (black-set skip).

**2. Export visibility (`niryat`).** Opt-in via `# sutram-module-v1` in both
importer and module:
- `niryat <name>` declares exports; duplicates are `E_MODULE_DUP_EXPORT`.
- v1 modules must use `ayojan mod@alias`, else `E_MODULE_V1_ALIAS`.
- `alias__<private>` referenced from outside the defining module is
  `E_MODULE_NOT_EXPORTED` (skips comments/strings, requires call parens).
- `niryat` lines are stripped before the namespaced rewrite; legacy imports
  are byte-for-byte unchanged.

**3. Deterministic init, defined and documented.** Added a "Round 41" section
to `compiler/MODULE_SYSTEM_R40_DESIGN.md` defining: once-only inlining,
deterministic multi-pass BFS order (root last), and order-independence of
definitions. Verified byte-identical output across repeated compilations.

**Tests added** (`examples/210`–`214`, `examples/lib/r41_*`): cycle (neg),
v1 public (pos, runs, prints 42), v1 private (neg), v1 dup-export (neg),
v1 no-alias (neg).

## What was actually run

NASM 2.16.03 built from source (apt unusable here):
```
$HOME/workspace/build-tools/nasm-inst/bin/nasm -f elf64 src/sutram_compiler.asm -o /tmp/sutram.o
ld -o /tmp/sutram_compiler /tmp/sutram.o
```
Zero warnings. Note: `win/rtblob.inc` (release artifact) is absent from this
clone; I built with a local empty stub (NOT committed, removed afterwards).
The Linux/ELF path never touches the blob.

Feature verification (all real runs):
```
$ /tmp/sutram_compiler main.sm /tmp/cyc2.bin
./lib/beta.smlib:1: Sutram Error [E_MODULE_CYCLE]: cyclic import: alpha -> beta -> alpha   (rc=1)
$ /tmp/sutram_compiler self.sm /tmp/self.bin
./lib/self.smlib:1: Sutram Error [E_MODULE_CYCLE]: cyclic import: self -> self   (rc=1)
$ /tmp/sutram_compiler c3.sm /tmp/c3.bin
./lib/c3.smlib:1: Sutram Error [E_MODULE_CYCLE]: cyclic import: c1 -> c2 -> c3 -> c1   (rc=1)
$ /tmp/sutram_compiler bad.sm /tmp/v1bad.bin
bad.sm:4: Sutram Error [E_MODULE_NOT_EXPORTED]: 'helper' is not exported by module 'vectors'   (rc=1)
$ /tmp/sutram_compiler dupmain.sm /tmp/dup.bin
./lib/dup.smlib:3: Sutram Error [E_MODULE_DUP_EXPORT]: duplicate export 'length' in module 'dup'   (rc=1)
$ /tmp/sutram_compiler noalias.sm /tmp/noalias.bin
noalias.sm:2:Sutram Error [E_MODULE_V1_ALIAS]: v1 module 'vectors' must be imported with an alias: ayojan vectors@alias   (rc=1)
$ /tmp/sutram_compiler main.sm /tmp/v1.bin && /tmp/v1.bin
OK: compiled 274 bytes / 42   (rc=0)
$ /tmp/sutram_compiler nest.sm /tmp/nest.bin && /tmp/nest.bin
OK: compiled 336 bytes / 7   (rc=0, nested v1: outer -> inner)
```
Diamond (a→b,c; b,c→d) compiles and runs; no false cycle.

Regression: all 178 original examples behave exactly as the pre-change
baseline (160 compile, 18 correctly reject — verified by diffing
per-example results). With the 5 new tests: **183/183** (161 compile,
22 correctly reject). Determinism: repeated compilations byte-identical.

## What was NOT run / not verified

- `tests/run_tests.py`, `tools/codegen_gate.py`, etc. do not exist in this
  clone; I verified via direct per-example compile comparison instead.
- Windows (PE) build of the compiler not tested here; the new code uses only
  the portable `os_*` wrappers and should assemble under `%ifdef WINDOWS`,
  but this is unverified.
- The `niryat` keyword is ASCII-only; Devanagari `niryat` is not recognized
  (documented as a known gap).
- v1 visibility is enforced for the aliased (`@alias`) import form (the
  documented v1 contract). Unqualified imports of v1 modules are rejected
  with `E_MODULE_V1_ALIAS`; this is a deliberate scoping decision, see the
  design doc section.

## File hashes (SHA-256)

```
5f41174f0e31d75197f83665dac465867c8657efe258425a6f514270a7391312  src/sutram_compiler.asm (modified)
0439f6ebf80fa87ca9f1a09a95bdca8ce38e207ebe6c14b6a233bda97aba9f34  compiler/MODULE_SYSTEM_R40_DESIGN.md (modified)
20d6b4a2e47ec8d2dc76e17cd4dc3dc1643d7c8f31aa239b3bf6f34e9b4a7ba7  examples/210_r41_cycle.sm (new)
af39bcfc381b0e93217d7361bf5b5f59f8e37b507741df149f2b400381aef867  examples/211_r41_v1_public.sm (new)
bbe39430d2eabc10f6e314234a779dfada135f0a6b4ca92fbdf1c0fb911a4c9d  examples/212_r41_v1_private.sm (new)
fcbbb5329eb74942d61a18caf83bf31b691eb60513f1d9ead578078517d8c0ad  examples/213_r41_v1_dupexp.sm (new)
c78511ee682b559199ab019a1dec2a9ab664b0103bd0441d97e8ed25c4eb4346  examples/214_r41_v1_noalias.sm (new)
7d08bb3d7d1e6cf84fd9d6bb282caf4b50c83d0348a4c0a6322e7528d396eff1  examples/lib/r41_cyc_a.smlib (new)
d90bb35ad4abc17fe1bfce08e78c67ef8ed3f3c9e02fa40fb3340304b1527d3a  examples/lib/r41_cyc_b.smlib (new)
911f06c877c0743d1a3f0691e97c178ebea2976619f09eb2880eb3854ae74cc8  examples/lib/r41_vec.smlib (new)
229c6cb4450c09084c2eab1921c282977ce7412abffde65e77e1effdd7de2a1c  examples/lib/r41_dup.smlib (new)
```

## Diff

New files are listed above (full content in repo). The compiler diff is
large (~1100 lines added); key entry points:
- `check_module_graph` (pre-pass entry, called before `expand_imports`),
- `mg_visit` / `mg_process_imports` (three-colour DFS),
- `mg_scan_buf` + `mg_parse_*` (import/niryat/prakriya extraction),
- `mg_check_visibility` / `mg_check_edge` / `mg_find_ref` (Phase B),
- `ns_strip_niryat` (called before `ns_rewrite_funcs`),
- new error messages `mg_e_cycle`, `mg_e_noexp*`, `mg_e_dupexp*`,
  `mg_e_valias*`, `mg_e_depth`, `mg_e_limit`.

Reviewable via `git diff src/sutram_compiler.asm` and
`git diff compiler/MODULE_SYSTEM_R40_DESIGN.md`.

Bugs found and fixed during implementation (none shipped):
1. `win_resolve`-style duplicated instruction (caught by review, not present
   in final).
2. `call mg_is_ident` clobbers `al`; three name-parsers stored the 0/1 return
   instead of the character (found via garbage in `E_MODULE_DUP_EXPORT`).
3. `mov al,[r9+rcx]` before `mov ah,[rbx+rax]` clobbered the address in rax
   (found via `mg_find_ref` missing a present reference).
4. `[rel sym + reg]` is not encodable; converted to `lea` + indexed.
5. Cycle path printed the full import chain; trimmed to the actual cycle.

## Deliverables in this folder

- `2026-10-09-round41-module-contract.md` — this report.
- `2026-10-09-deliverable-src.tar.gz` (SHA-256: `e6fa2856509f78054f0ff4108869e9ce3181644ca913d1b333c89ba41973189a`) — source archive with all new/modified source files (compiler, design doc, wizard installer, 5 new tests + 4 lib modules). Reports live alongside it in this folder.
- `2026-10-09-deliverable.patch` (SHA-256: `2e5ce5dec2aee3922ba99acae73a7757c5706e25e1ff02e939e1a77e2ab94571`) — unified diff of the three modified files (new files are in the tarball).
- `2026-10-09-wizard-gui-round1.md` — the earlier Guided Split wizard installer report (also included in the tarball).

## Proposed next task

Sarvam to verify on their side: (a) rebuild with the real `win/rtblob.inc`
and run the full `tests/run_tests.py` (178→183), `codegen_gate.py`,
`test_lang_packs.py`; (b) confirm the v1 scoping decision (alias-required)
or request unqualified-v1 support; (c) native-speaker review of the
`E_MODULE_*` message wording if they will be user-facing.
