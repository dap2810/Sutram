# R140-00 — WS1: every text file the installer carries is LF in every checkout. WS2: one exact package, with its manifest checked against the embedded ZIP - and the same bytes when built from a CRLF copy of the tree dated 400 days earlier. WS3: the release notes now open with what v309 closes and what it does not. WS4: the check covers every statement. The one expression path outside a statement is the module-level `vitti` initializers. **Correction below: that path is reachable today - a `kosh` from a call becomes a number there (ChatGPT's C1, confirmed on v309).**

## Release line

Same commit and package as R139-00:

```
gates: 75 PASS / 0 FAIL / 1 NOT-RUN   (sh tools/gates.sh, Linux, Xvfb; NOT-RUN = Windows execution)
suite: NO-EXPECTATION=4  PASS=327  (331 run)
Sutram 1.0 (v309) - sampurna sutra      (compiler unchanged since 01f1171)
```

- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **The guard: NOT re-run** (no compiler, runtime, library or pack byte changed).
- **Installer:** `ceb92682bc5faa7575a7f6b65efc05d4fe4c157a339ecb13fb5e5e4da67459a0` (rebuilt after the WS4 correction to the release notes; the determinism test ran on the build before it, `a1109853...`).

## WS1 - the `.gitattributes` rule

`text eol=lf` for:
- `/README.md` and `/LICENSE.txt`;
- `docs/**/*.md|html|txt`;
- `examples/**/*.md|out|exit|txt`;
- `windows/native-installer/*.ps1|md`.

Sources had a rule already.
- **Checked by the new gate `R140 package` (`git check-attr eol`):** 560 of 560 payload text paths are `eol=lf`. On the v309 attributes, 407 of 560 were - **the 153 missing are exactly the 153 differences the Windows handoff recorded.**
- **The committed bytes are unchanged** (all `i/lf` already), so no file is rewritten.
- **The rules are scoped to the payload's paths.** Partner folders keep their committed CRLF and mixed files.
- **ChatGPT's Task C asks for a fresh Windows checkout to be compared again** after this. That is the owner's; NOT RUN here.

## WS2 - one exact package, verified against the embedded ZIP

**Gate `R140 package`** (`tests/r140/test_package.py`) opens the built `Sutram-Setup.exe`, not the tree. It checks:
1. **the embedded `payload.zip`'s manifest lists every entry exactly once** (657 lines, 657 entries, 0 duplicates);
2. **every entry's bytes hash to its manifest line** (657/657);
3. no text entry contains CR LF (0);
4. every entry equals the tree file it was made from, byte for byte (657/657, on this Linux checkout);
5. every payload text path is `eol=lf` (560/560);
6. every ZIP entry has the fixed date 1980-01-01, so no checkout time is in the package;
7. `Sutram-Setup.sha256` is the setup's hash.

**On the v309 package as committed:** 1-3 pass; 5 fails with 153 paths; 6 fails on all 658 entries.

**Determinism, measured:**
- **Two builds of the same commit,** one from this tree and one from a copy at another path with 516 text files converted to CRLF and every file dated 400 days earlier: **identical `Sutram-Setup.exe`, `a1109853...`.**
- **Self-test exit 0 under Wine.**
- **What made the difference:**
  - LF normalization in the builder, before hashing - and of the scripts and licence the wizard embeds;
  - fixed ZIP dates and attributes (`zipfile.ZipInfo`);
  - linking the wizard with `--no-insert-timestamp -s` - the symbol table had carried the build folder's absolute path.

**The Windows builder** (`build-installer.ps1`) now normalizes text to LF, as ChatGPT wrote it in PR #67, but it still uses `Compress-Archive`, so its ZIP dates are not fixed. **The release package is the Linux build. The release notes say so.**

## WS3 - release notes that state what v309 closes and what it does not

New first section: **"Status: what v309 closes, and what it does not"**.
- **Measured:**
  - **the native v309 results**, named with their folder: out-of-memory 32/32, arithmetic 7/7, suite 322 pass, upgrade, clean install, interruption early, late and with an edit, each retried, a new terminal finding one `sutram`, Windows showing `1.0.309`;
  - every Linux gate, the guard, and the Wine Windows-compiler check.
- **Not claimed:**
  - **that all slice expressions are closed.** The gates test the forms found so far, and the one path outside a statement is named (WS4);
  - the out-of-memory exit beyond the measured limits, a failed start-up reserve on Windows, and teardown in general;
  - that the installer is atomic: interruption-and-retry safety, file by file; integration finished by a rerun, not rolled back; stops between journal records not tested natively;
  - **any cause for a security product's suspension;**
  - that the Windows builder is deterministic.
- **The package section** says what R140 changed, and records the CRLF upgrade suspension as an observation.

## WS4 - does `r137_check_stmt` cover a lowering path with no named destination?

**It covers every statement, named destination or not.**
- **It is called at the top of `gen_stmt`.** `gen_block` is the one loop that generates statements, and every body - functions, `yadi`, `chakra`, `mandapa` - is a block. The other two callers of `gen_stmt` are the debug-instrumentation paths (`r45_debug.inc`), which also go through it.
- **Measured on v309 (this round's probes):**
  - an expression statement with no destination (`keep(k[0:1] + zero)`, and a bare `k[0:1] + zero`);
  - a compound assignment (`x += m[0:2]`);
  - a `nivartanam` of arithmetic;
  - `abhava(slice)`;
  - a `chakra` body;
  - nested call arguments;
  - a function value's result in arithmetic;
  - a string indexed by a slice.
  - **All refused.** The `vib(m[0:2]) + 1` control compiles and prints 6.

**The one expression path outside a statement: the module-level `vitti` initializers.** `r56_gen_global_initializers` calls `gen_expr` directly at process entry, without `gen_stmt`, so `r137_check_stmt` does not see them.
- **Today no slice can be formed there.** At module level there is no `mala` (a syntax error), no `kosh` (refused since R127, the global door), and no `vibhag`. Slicing a plain `vitti` is refused at code generation (`vibhag: mala, kosh va vibhag apekshita`), measured here with `vitti A = nirmmita(16)` and `vitti G = A[0:1] + 0`.
- **The residual risk:** any future way to form a slice at module level, or any new path that calls `gen_expr` without a statement (an inliner, a new kind of global), would bypass the check until it gets one.
- **The fix is one call** (`r137_check_stmt` on each initializer in `r56_gen_global_initializers`). **I have not made it:** it changes the compiler, and therefore the version, just after v309 was verified natively. It is ready for the next compiler change.

**CORRECTION, after pushing this - ChatGPT's R208 follow-up (`9592069`, landed at the same time) is right, and I was wrong to call this path safe.** A *slice* cannot be formed at module level, but **a `kosh` made a number by a call can**:

```
vitti zero = 0
vitti leaked = make_kosh() + zero      # make_kosh() returns a kosh
```

- **Run here on v309:** it compiles, and `likha(leaked)` prints the descriptor's address (`139858114773008`), exit 0.
- **The same declaration inside `mukhya` is refused** (`E_KOSH_GANIT`).
- **That is a type erasure on the path I named,** not a demonstrated stale read. The residual risk is not hypothetical: it is reachable today.
- **The fix is the call above.** Global initializers are expressions with no statement, so `r137_check_stmt` should take the initializer as a declaration's value.
- **With it, as ChatGPT also says:**
  - the walk's node budget should refuse when it runs out, not pass;
  - the installer's `Read-State` and pending check should move under the lock (two reads still come before it).
- **All three are compiler or engine changes for the next candidate (v310). Not made in this round.**

Evidence: `Claude-to-Sarvam/evidence-r139-r140/`.
