# R208 — arithmetic slice escape, coverage, and payload bytes

**Base:** main `bf8b53dc0e93c358eca2fc37cc8cdae134b6bfb5` (v308). **Role:** read-side. Compiler/build/suite/Wine/native Windows/installer/GUI: **NOT RUN — no toolchain used by this reviewer.** Source-derived claims below are predictions unless explicitly attributed to the committed Windows evidence. No production changes.

## 1. The worst outcome is an outdated element, observed

The distinction in the brief is already resolved by the Windows handoff committed on main: `Windows-to-Sarvam/win-v307-fixes-2026-11-06/wrapper-comparison/results.json` records the **upstream v308** compiler SHA-256 `9a15a7f25b6f4825c9bca40debb53899c9f8a772b780286bed0efb5d086f81f1`. Both `keep(k[0:1] + zero)` and `keep(k[0:1] ^ zero)` compile, exit 0 and print **7, then 99** after the kosh grows and its current element is changed. That is an outdated element read, not merely a decimal address. The v307 repair candidate in PR #67 rejects both; it is **not** merged into v308. These are the Windows contributor's observed runs, not mine. The two programs Sarvam ran and reported as addresses show the *other* possible symptom when the descriptor pointer is printed directly. An address-only result cannot dismiss the stale-read case.

| Requested expression | Current evidence / source prediction |
|---|---|
| `k[0:1] + 0` | Sarvam observed a decimal address. The exact value depends on allocation; literal identity folding and use context matter. |
| Conditional slice versus numeric arm, then stored | Existing `m_r136_ws2_ternary` control is reported refused with `E_KOSH_DVARA`; `r126_value_kind` marks a collection/noncollection ternary mixed kind 6. This does **not** prove every conditional shape safe. |
| Echo through an untyped function then arithmetic | A direct slice argument to an untyped function is refused by `r126_check_untyped_arg`; wrapping it in arithmetic first erases the kind. Windows' `keep(k[0:1] + zero)` then indexing observes 7/99. |
| Comparison result used as an index | `rfx_is_kosh_operand` sees bare kosh variables, not slice nodes. A comparison of a slice can compare descriptor addresses and yield a numeric Boolean; indexing with that Boolean is an index of 0 or 1, not an element conversion. **Prediction, NOT RUN** for this exact program. |
| Decimal expression/conversion | No evidence here that it dereferences the slice. Generic expression generation produces a descriptor address; a decimal conversion would consume that value unless a separate specialized path intervenes. **Exact expression and result NOT RUN; do not label it an element.** |
| Multiplication | A binop on a slice is not rejected by the bare-variable `rfx_is_kosh_operand` check; generic arithmetic can scale the address, yielding an address-derived number, not a defined element. **Prediction, NOT RUN** for this exact program. |
| Slice into fixed-size array cell, read back | The direct slice RHS is rejected by `r126_check_assign` through `r134_holds_kosh` (Muse's cell gate). An arithmetic-wrapped RHS evades that shallow recognition; whether a later indexing operation reads an old element depends on the cell contents and descriptor use. **Wrapped cell variant NOT RUN.** |
| `likha(k[0:1])` | A builtin argument passes through `r126_check_builtin`; its non-kosh-specific position sees the direct slice and rejects it. **Source prediction, NOT RUN**, rather than an assertion that it prints an address. Check this exact program before documentation claims. |

The compiler's `r126_value_kind` maps BINOP to raw kind 5; `r134_kosh_slice` recognizes VAR/SLICE only; `rfx_is_kosh_operand` recognizes bare VAR only. An arithmetic wrapper can carry the descriptor address across an untyped boundary. Later interpreting it as a slice permits an outdated read. The repair PR's recursive check is useful evidence for a fix, but should be reviewed and ported onto v308 without replacing its journal engine.

## 2. Decision: reject slice arithmetic

Reject **every arithmetic, bitwise, shift, comparison and logical operator whose operand may be a borrowed slice**, before folding or numeric lowering erases provenance. Do not define a slice as its first element: that silently discards length, makes empty slices awkward, and hides an address/element distinction. Students can write `s[0]` when they intend an element, then ordinary element arithmetic remains valid. Keep the established typed direct `vibhag` view operations. Apply the same rule to slices of uncertain provenance until a precise non-borrowed contract exists. A diagnostic should name the slice and suggest explicit indexing; tests must cover variable-zero wrappers, nested binops, both operand positions, comparisons and legitimate scalar element arithmetic. Require nonzero compiler exit as well as diagnostic and no output binary.

## 3. Storage coverage and the future-door gap

The current explicit checks are:

| Destination / boundary | Current check |
|---|---|
| Cell, kosh element, record field | `r126_check_assign` calls `r134_holds_kosh` on RHS |
| Module/global variable | Same assignment check |
| Local name | `r127_check_slice_value` catches only a top-level AST_SLICE of a kosh; `r126_value_kind`/`r126_bind` bind the classified kind, but BINOP becomes raw 5 |
| Raw memory write (address and value) | `r126_check_writemem` calls the predicate on both |
| Ordinary/untyped parameter and indirect function value | `r126_check_untyped_arg` calls it when the callee is recognized or indirect; typed parameter rules also apply elsewhere |
| Builtin argument | `r126_check_builtin` calls it for up to six arguments and permits selected kosh-first positions |
| Return / phal result | `r126_check_return` calls it for phal; plain returns use kind agreement plus other slice-specific checks |

These are the visible semantic doors; there are also expression lowering paths that pass values through registers/stack without a named destination. `tests/r134/test_one_predicate.py` only asserts that the *five known check bodies* contain a call and that `r126_is_kosh_value` has one call site. It cannot detect a sixth store path that calls neither predicate, or an expression wrapper that hides the slice. The most plausible future omission is a new builtin/intrinsic, raw/inline-assembly storage path, or assignment form dispatched outside `r126_check_assign`. Put the rejection at the common expression classification/validation boundary, and add an AST-walk coverage gate that enumerates all store and call node kinds and fails on an unclassified node; review still matters for newly introduced AST kinds. A text search for one old call is not a completeness proof.

## 4. Line endings: hash the bytes actually shipped, distinguish builds

The root `.gitattributes` forces LF for `*.sm, *.smlib, *.asm, *.inc, *.lang, *.sandesh, *.sffi`; it does **not** set `eol=lf` for `*.md`, `*.txt`, HTML or other prose. A Windows checkout with `core.autocrlf=true` can therefore have CRLF prose while Git's blobs are LF. The installer builder copies compiler/linker/GUI/icon (binary), LICENSE/README, and the `lang/`, `lib/`, `examples/`, `docs/` trees into its payload. Its manifest is created by `Get-FileHash` **after copying the staged files**, and verification checks extracted payload against that same manifest. Thus a package's internal hash check can pass on either convention; it does not prove its text bytes match Git or an earlier package. Cross-build hashes and ownership decisions can differ solely because of newline conversion.

Concrete comparison of the committed v307 repair **candidate manifest** (not the v308 embedded manifest): `lang/sanskrit.lang` records SHA-256 `0b194086...` and matches the Git LF bytes; hypothetical CRLF would hash `af4af0b7...`. `README.md` records `ab0ea01b...` and matches Git LF; a CRLF checkout would hash `9e08391a...`. `lib/mala.smlib` records `d64d9ef5...` and matches LF; CRLF would hash `873be6bc...`. Those first seven digits distinguish the conventions. `docs/MEMORY-MODEL.md` changed in the repair candidate, so its committed-main Git hash cannot be compared directly to that candidate manifest. The final v308 setup's full embedded manifest was **not independently extracted by this reviewer**.

The Windows handoff records 153 first-build payload differences attributed to CRLF and a successful normalized rebuild retaining 654/657 files. That is evidence of byte drift and a successful run, **not proof that CRLF caused Acronis to suspend the previous run**; the smaller replacement set is an alternative causal factor. Normalize every payload text file explicitly to the intended LF bytes before manifest generation, or declare exact attributes for each text type, then compare staged manifest entries against the bytes in the ZIP and against the intended source at a pinned commit. Never normalize binary files. A generated manifest is a record of staged bytes, not a portable promise about an arbitrary checkout.

## 5. Checkable release conditions, still NO

1. Port/review a class-level slice-expression rule into the final v308 candidate. The Windows 7/99 add/XOR cases must refuse with nonzero compiler exit, while direct typed views and scalar element arithmetic pass; repeat across operators, expression nesting and escape destinations.
2. Resolve the installer ownership findings from the R207 follow-up **in the final v308 journal engine**: legacy partial suffix deletion, pre-lock state reads, and changed-target revalidation. PR #67's tested v307 installer is a different implementation; its clean/upgrade/retry results do not establish these v308 conditions.
3. Build one exact final package with deterministic text bytes and a manifest verified against its embedded ZIP; pin package/compiler hashes and rerun native clean install, same-folder upgrade, interruption at publish/finalize/commit boundaries, user-file preservation, PATH/new terminal, IDE and uninstall. The Windows 36/36 v308 OOM matrix is valuable direct-runtime evidence; final-package native OOM and failure-path checks must be tied to its exact compiler.
4. Update release notes to match measured behavior and the final test record. Do not claim that all slice expressions are closed or that CRLF alone is the proved security-product cause.

**Verdict on pinned main: NO.** The release conditions apply to the integrated candidate, not the successful v307 repair run. No source, tests, release binaries, or installer were altered by this response.
