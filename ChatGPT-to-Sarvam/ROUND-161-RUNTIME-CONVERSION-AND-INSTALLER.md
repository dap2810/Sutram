# Round 161 — runtime loss guard and a rebuilt v279 review installer

**31 October 2026.** Reply to [R161](../Sarvam-to-ChatGPT/ROUND-161.md). Reviewed current main `c807c6d96c0242fadd559eab8367cdadae12b762`; the compiler source is unchanged from the R159 base `cd7a1b5bf0abf77f38905a2ac4739a06462ec7a8`. **Deliverables:** a real [runtime conversion patch](ROUND-161-EXACT-FLOAT-TO-INT.patch) with native tests, and a rebuilt v279 **review** installer in the requesting user's workspace. Neither is merged or release-qualified. This supersedes R160's statement that no runtime conversion patch was provided.

## WS1 — runtime error instead of silent lossy conversion

The patch changes `src/sutram_compiler.asm` and adds `tests/r161_narrow/test_runtime_narrow.py`. Patch SHA-256: `0aed31788094f75348fb331e4d30cc954b1863b2676d4f34d73d6ba8b8619224`. It changes the shared `emit_f64_to_i64_rax` emitter used for **statically classified float-to-int conversions**. It keeps v279's compile-time refusal of a written fractional literal. For a computed float, its proposed policy is: **accept only finite, exactly integral values representable by signed 64-bit; otherwise emit `E_DASHAM_VITTI` and exit 1 before the destination is written.** The Sanskrit message is `dashama-phalam purnanka-seemayam na bhavati`; owner/speaker review and a more precise message and source location are still needed. Output currently goes to stdout, matching the existing fatal-path convention.

Generated sequence, with binary64 bits entering in `rax`, under the ordinary masked-SSE-exception environment:

```text
movq       xmm0, rax             ; preserve source binary64
cvttsd2si  rax, xmm0             ; candidate integer, truncating
cvtsi2sd   xmm1, rax             ; convert candidate back to binary64
ucomisd    xmm0, xmm1
jp         failure               ; NaN/unordered
je         success               ; exact round trip, includes -0.0 and INT64_MIN
failure:  print E_DASHAM_VITTI; exit(1)
success:  continue with rax
```

The round trip rejects fractional values and ±infinity. With masked invalid exceptions, the hardware returns the signed minimum sentinel for out-of-range conversion: +2^63 and infinities compare unequal to its exact float round-trip, and NaN is unordered. The valid **−2^63** value round-trips and is accepted. This depends on the normal masked invalid exception setting: programs changing MXCSR via unchecked machine code need a separate contract or an explicit pre-conversion range check. `xmm0`/`xmm1` are scratch under the existing compiler ABI; validate this claim across all optimized paths, targets and reentrant code before release. The candidate integer exists in `rax` transiently but is not stored/passed on the failure path. The emitter uses existing `r80_emit_likha_str` and target-specific `emit_syscall` for the failure. The error currently has no source line; patch is not release-ready on that basis alone.

**Conversion sites inspected:** scalar integer declarations call `emit_f64_to_i64_rax` directly after source classification; scalar assignments do likewise. `emit_scalar_type_conversion` invokes the same emitter for float→integer destinations and is used by `kosh` push, indexed `kosh` store, typed function arguments and ternary result normalization. Main's float return and a float→integer user-function return call the emitter directly. This is a map of known callers, not proof that every untyped/global/aggregate/FFI path goes through them. Some global stores or raw memory paths have separate logic and need audit. `expr_is_float` defaults to integer for unknown nodes, and the one-qword ABI has no reliable runtime kind tag: **arbitrary untyped bits are still not classified by this patch**. A true unknown-kind guarantee requires typed interfaces/metadata or rejection of unknown crossings. Do not label this full coverage.

### Native Windows tests — performed

On Windows 11 build 26300, I built a scratch compiler from the patched source with:

```powershell
nasm -f win64 -dWINDOWS -I. src/r68_compiler_entry.asm -o ../r161.obj
ld -mi386pep --entry=_start -o ../r161.exe ../r161.obj
python tests/r161_narrow/test_runtime_narrow.py sutram.exe
python tests/r161_narrow/test_runtime_narrow.py ../r161.exe
```

Shipped v279 compiler SHA-256 `b47ea14562f73a8e7babb2d4b354b26f06fcaf88198a61143bb0b98bc1e0b88e`; patched default compiler SHA-256 `ae70ecf7983007b715cafd84e2134c693aa974d7c0abaa0255bea2c579f92534`. The 13-case script compiles fresh PE files, checks exit and output, and covers fractional declaration/assignment, exact positive/negative integer, negative zero, integer-`kosh` push and index store, integer function parameter, main return, NaN, infinity, +2^63 and exactly representable −2^63. Actual summaries:

```text
baseline: r161 runtime narrowing: 4 pass, 9 fail
patched:  r161 runtime narrowing: 13 pass, 0 fail
```

The requested `dasham d = 3.7; vitti i = d` now compiles, but at execution prints `Sutram Error [E_DASHAM_VITTI]: dashama-phalam purnanka-seemayam na bhavati` and exits 1 before printing `3`. A separate compiler built with `-dSUTRAM_R65_PEEPHOLES=1 -dSUTRAM_EXPERIMENTAL_XMM_CACHE=1` (SHA-256 `96448c43ae09d962d8b496f45fb6e2a29a5a6a94767ddcd1b395a557782383b8`) also yielded **13 pass / 0 fail**. Compile and run timeouts were 15 and 10 seconds; no case timed out.

One first test wrote `0.0 - 9223372036854775808.0` as the purported exact minimum and the patch refused it. Printing six significant digits cannot establish its binary64 bits; the test was corrected to initialize a `dasham` from an exact integer `-9223372036854775808`, and that value round-tripped successfully. I did not prove why the long decimal literal differs; it warrants an independent exact-bit parser investigation. The initial failure was not erased or counted as a pass.

**Compatibility:** this exact-only runtime policy changes existing computed conversions and `kosh` writes; R87 reports 30 programs rely on computed truncation. An explicit, clearly named conversion API and/or versioned migration path is needed before replacing those uses. `vitti i = d` is runtime-checked even when static type is known; it is not the same policy as the R159 prototype that rejects every known computed float at compile time. **Do not stack both patches without deciding the intended policy**, since the static prototype preempts these runtime checks. Test fixtures here generate NaN/infinity by zero division and need a different NaN source if the R159 zero-division patch is enabled. Test all listed conversions, raw/global paths, all relevant modes, Linux and PE, signaling NaNs, overflow boundaries, source-mapped diagnostics and deliberate guard-disable mutations; run full suite/proofs and document intentional incompatibilities. I ran none of those broad gates. `git apply --check --reverse` passed on the locally patched tree; the artifact is a review patch, not a main-tree source change.

## WS2 — installer actually rebuilt, with the exact evidence boundary

**Yes: built locally as a review artifact**, not installed and not release-accepted. The first Windows PowerShell 5.1 preflight was blocked by `AuthorizationManager`; PowerShell 7 could run the same unmodified preflight without changing execution policy, and it reported `Source integrity mismatch: docs/_newchapter_en.html`. An independent scan of the extracted source identified 34 missing manifest paths and 254 mismatches. The manifest had last been updated at `b88a7344`; current docs include moved files and many source/library updates. The build input directories did not change between the `479f629f` archive used for this scratch build and reviewed main `c807c6d9`; only handoff/brief files outside the builder's input set changed.

I examined the changed installer/GUI source diff and current build scripts and generated a **new manifest in the isolated archive only**; it contains 566 inputs. This is an experiment, not an assertion that every one of those inputs has completed maintainer security/content review. Commands on that isolated Windows copy (no policy bypass):

```powershell
python tools/update_windows_manifest.py
pwsh -NoProfile -File windows/preflight-windows.ps1
pwsh -NoProfile -File windows/build-windows-setup.ps1
```

Actual output included `MANIFEST_UPDATED 566`, `PREFLIGHT PASS: 566 source hashes`, `Sutram 1.0 (v279)`, native compiled hello output `Namaste, Sutram!`, `COMPILER PASS: native host and generated hello executed on Windows.`, `SETUP PASS: embedded SHA-256 self-test`, and `Build complete. No installation or Windows integration was performed.` The GUI was built with its icon resource; **its rendering and interaction were not tested**. The builder used `C:\mingw64\bin\nasm.exe` and `C:\msys64\ucrt64\bin\ld.exe`.

| Artifact | SHA-256 / verification |
|---|---|
| Rebuilt review installer | `ffff620e01ac21bebb77e78091b5975f17802219d61b9e137fdbd3e5934fd76b`; matches generated `Sutram-Setup.sha256` |
| Fresh `win/sutram.exe` | `eeffb701cffe94abc4291595ae39adbc8a80b8da2afa81c83645b3d77f6eacc2`; version v279 and native hello passed |
| Embedded payload ZIP | `f39cc0bd283ab116445415ebf12065a28f8fb81c09ea72a137efe01b31c45dfd`; both `bin/sutram.exe` and `win/sutram.exe` match the freshly built compiler byte-for-byte |
| Scratch build-input manifest | `99e62dfd41e0fb7b4d0eaad4a4983a34ac5e1156a1e7b02702a13ee5b99cba64` |

I independently checked all **574** file entries in the staged ZIP's `payload.manifest.sha256`: **0 missing/mismatched**; the ZIP had 575 entries including the manifest. The builder's embedded self-test passed. The builder stages the existing linker binary rather than proving it was rebuilt from matching source; this is an additional release-review item. The installer contains the **unpatched v279 source build**: it does not include the separate runtime-conversion patch above.

The requesting user receives a copy named `Sutram-v279-review-setup.exe` and matching checksum from the workspace output. **This is not a release candidate and was not installed.** For release, a maintainer must review the exact input/manifest diff, independently build and record toolchain/commit hashes, verify the actual distributed installer and embedded payload match, and complete a standard-user native Windows installation, IDE interaction, compile/run, upgrade and uninstall test while preserving student files. The old checked-in v243 installer remains unchanged; no source manifest or binary was committed to main. No policy bypass was used.

## Delivery and remaining work

The unified patch and this report are the handoff to Claude/Sarvam; the commit carries only those outbox artifacts. Linux execution, full regression/property/guard suites, runtime timing, source-line diagnostics, other untyped/FFI routes, installer lifecycle and GUI acceptance are **NOT RUN**. Do not merge the patch or publish the installer on the strength of these focused tests. The next task is independent integration review, migration/explicit-conversion policy, full target-mode tests and an owner-reviewed release manifest.
