# R34 — namespaced import correctness and bounded diagnostics

## Design intent and compatibility

`ayojan name@alias` is an opt-in **compile-time** namespace for function definitions:
`alias__function(...)` is a regular Sutram identifier. `ayojan name` stays the existing
unqualified, source-inlined import. The Sanskrit keyword and Devanagari function-definition
alias remain supported; this is not a runtime linker, object module system, or security sandbox.

R34 hardens the R33 feature without adding a runtime dependency or elevated permissions.
It deliberately does not implement `alias.function()` because field access and decimals
already use `.` and need a separate parser design.

## R34 rules

1. **Alias ownership:** one alias can designate only one module. Repeating the exact
   `module@alias` is idempotent. Two different aliases for the same module remain valid.
   Reusing an alias for another module emits
   `Sutram Error: namespaced alias already assigned to another module` (exit 1).
   Plain/unqualified legacy imports keep their prior global-name collision behavior.
2. **Bounded names:** qualified module basenames must be 1–30 ASCII bytes in
   `[A-Za-z0-9_-]`; no slashes, dots or relative path segments. Alias must be a 1–31
   byte ASCII identifier (`[A-Za-z_][A-Za-z_0-9]*`); the original R33 scanner already
   imposes this alias grammar. This narrows **only qualified imports**: existing
   unqualified imports preserve path parsing semantics. No directory permissions change.
3. **Tracking limit:** the existing deduplication table has 16 slots. A seventeenth
   distinct qualified import now **fails explicitly** rather than silently disabling
   deduplication. Exact duplicates do not consume additional slots. Legacy behavior
   beyond 16 entries is unchanged this round.
4. **Legacy EOF boundary:** when an ordinary imported file exactly fills the
   allowable read region, the one-byte overflow probe returning EOF now jumps to
   normal close handling; it does not fall through into the qualified importer.

The table, scanner buffers, compiled executable format, function ABI, native Windows
installer and the normal-user security model are unchanged. `lib/`, `ide/`, `docs/`,
all six books, installers, and Sarvam's examples >=200 are untouched.

## New tests (examples 154–162)

| Example | Case | Result after NASM rebuild |
| --- | --- | --- |
| 154 | exact duplicate import | prints `13` |
| 155 | three aliases, two same-named modules | prints `13,203,12,200` on separate lines |
| 156 | one alias bound to two modules | named compile failure |
| 157 | missing qualified module | named compile failure |
| 158 | alias starts with digit | invalid-import compile failure |
| 159 | attempted `../` module traversal | invalid-import compile failure |
| 160 | empty alias | invalid-import compile failure |
| 161 | alias exceeds 31 bytes | invalid-import compile failure |
| 162 | seventeenth distinct qualified import | invalid-import compile failure |

`tools/test_namespace_contract_oracle.py` validates the **intended** behavior with a
separate Python reference expander, using the previously verified native compiler for
successful expanded examples. Python is not part of the Sutram compiler/runtime.
This oracle never exercises the changed NASM path and is **not** a replacement for the
rebuilt compiler's 177/177 golden suite. Expected compile failures require the explicit
`tests/expect/<case>.compile_fail` marker and exact message/exit code.

## Rebuild, benchmark, and merge requirements

- Rebuild the Linux and Windows compiler from `src/sutram_compiler.asm` with NASM, then
  run `python3 tests/run_tests.py` (target **177/177**) and `python3 tools/codegen_gate.py`
  (target **12/12**, experiment XMM cache off). Do not advertise unrebuilt results as passing.
- With a *known-good pre-R33* compiler, use `tools/module_namespace_ab.py` for 126,
  07 and 66 output-program **byte identity**, plus pinned interleaved min/p10 for 126.
  Namespace handling is compile-time, so do not claim an execution speedup.
- Sarvam's newer R33 package was metadata-visible but its raw download is blocked by
  Google Drive with **403 `cannotDownloadAbusiveFile`**. This work is based on the prior
  outgoing R33 package. **Do not wholesale replace** Sarvam's newer book/roadmap/IDE tree.
  Apply `compiler/ROUND34_NAMESPACE_HARDENING.patch` only to the R33 namespace source,
  then copy the added examples, expectations, test oracle, and this note. Preserve all
  Sarvam-owned directories and native installer. If the source has diverged, reconcile
  the patch, do not blindly replace.
- No administrator/root, antivirus-disable, security-policy change, system service,
  privileged install, or extra network port is used or requested.
