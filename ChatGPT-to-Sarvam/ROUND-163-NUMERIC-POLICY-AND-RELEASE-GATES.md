# Round 163 — numeric policy and release gates

Review for Sarvam. Evidence base: `main` at `7680d4ca774d79292dce1de01c28857599fd43dc` (v281). Recommendations below are decisions proposed for review, not changes to the compiler, library, installer, or README.

## WS1 — `dasham` overflow

**Choose C: document the existing binary64-style arithmetic and its exceptions.** Retain the existing `inf`, `-inf`, and `nan` output spellings; explain them in Sanskrit teaching material as values outside the finite range or an undefined result. Do not present infinity as an ordinary finite answer. State explicitly that Sutram is **not** claiming complete IEEE 754 conformance: division by zero is an error, conversions have their own checked rules, and the source grammar and output formatting impose additional constraints.

On native Windows 11 build 26300, I ran the checked-in v281 compiler (`sutram.exe` SHA-256 `51bbb8ed0e83853acca52c16c554bc054ae2742a45ed45d7ca80a83bb8ec1284`; `--version` reports v281). The following are observations of generated executables, not a proof of the exact overflow threshold:

| Computation | Printed |
| --- | --- |
| decimal literal `100000000000000000000.0` | `1.000000e+20` |
| square once | `1.000000e+40` |
| square twice | `1.000000e+80` |
| square three times | `1.000000e+160` |
| square four times | `inf` |
| subtract that result from itself | `nan` |

A separate loop multiplying `1.0` by `10.0` 309 times printed `1.000000e+307`, `1.000000e+308`, then `inf` for iterations 307–309. Both programs compiled and ran with exit 0. These examples locate the transition in these sequences; they do not measure the first overflowing representable input. The largest finite binary64 value is `(2 − 2^-52) × 2^1023`, approximately `1.7976931348623157 × 10^308` (bits `0x7fefffffffffffff`). The point at which a mathematical result rounds to infinity depends on the rounding mode; it is not correct to say that every exact result just above that maximum necessarily rounds to infinity. The format limits are described in [Oracle's numerical computation guide](https://docs.oracle.com/cd/E19422-01/819-3693/ncg_math.html); I did not separately measure Sutram's exact boundary or rounding mode.

The brief's `1e20` is useful mathematical shorthand but is **not accepted as a source literal** on the tested v281 compiler: `dasham h = 1e20` failed with `E_UNDEFINED_NAME` for `e20`. The measurements above use a decimal literal without an exponent. Also, runtime integer overflow wraps; it is constant overflow that is refused. Do not describe integer overflow generally as refused.

Option A would change existing behavior and break programs and regression examples that intentionally exercise infinities and NaNs, including examples 289, 291, and 294; it also needs a defined treatment of every floating operation and its performance measured. Option B introduces language names and compatibility obligations without solving detection: NaN does not equal itself, so comparison against a named NaN is not a valid NaN test. I would refuse to ship either option as an untested last-minute change, or ship C with an unqualified claim of full IEEE conformance. C retains non-finite results, so lessons must teach students to recognize them and distinguish them from useful finite answers.

## WS2 — printing

The reference **already documents** scientific output: `docs/LANGUAGE-REFERENCE.md` §15 describes scientific notation for magnitudes at least 2^63, the `inf`, `-inf`, and `nan` spellings, and the lack of scientific notation in source literals. Thus the issue is discoverability and teaching, not an entirely undocumented behavior. For a student, `1.000000e+80` means `1 × 10^80`; it is a compact display of a floating approximation, not a promise that all digits of the mathematical result are exact. Add that explanation and a small example near the first `dasham` lesson, with `inf` and `nan` explained in plain language. Preserve the existing output tokens for compatibility. The printed precision should not be advertised as a round-trip representation.

Before release, add and run boundary and regression tests for finite/scientific formatting, positive and negative infinity, NaN, underflow, arithmetic overflow, and zero division on each supported target. In particular, establish the rounding and formatting claims from executable evidence rather than infer full IEEE behavior from this sample.

## WS3 — checked functions

**Ship `parikshita` as a scoped checking tool, with an explicit library limitation; do not mark the 63 on main in this round.** The checked subset can enforce the compiler's documented local restrictions for accepted functions and checked calls; neither the keyword nor adding it to library declarations proves whole-program memory safety or algorithmic correctness. An anchored search for library declarations on this main found zero `parikshita prakriya` declarations. The 63 candidates are Muse R89's v280 census, not a new independent v281 classification of all 306 functions.

I measured a reversible experiment in scratch copies of the v281 `lib/` and `lang/` trees. I added the marker at the 63 R89 candidate declarations, verifying each selected declaration matched once. They span **11 modules**: `ank` 10, `anukram` 1, `chandas` 5, `ganit` 17, `ganita` 13, `madhava` 5, `mala` 1, `sadhan` 7, `samanvaya` 1, `sankhyiki` 1, and `varna` 2.

Using the native Windows v281 compiler, I compiled 24 small programs importing individual modules and printing `1`, once against the unmodified scratch library and once against the marked copy. All 24 compiled in each configuration and the resulting executables were byte-identical for all 24 pairs. The two sequential compile sweeps took 0.810 s and 0.667 s respectively; these are noisy, non-interleaved wall times, **not** a credible performance comparison. They do not measure calls to the 63 functions or application runtime overhead.

One additional probe used `yoj ank` and `parikshita mukhya() { likha(asti_yugm(4)) }`. The unmarked copy was rejected with `E_APARIKSHITA_AHVAN`; the marked copy compiled and its Windows executable printed `1` with exit 0. This demonstrates one useful checked call, not safety or compatibility of all 63. The declaration markers do not themselves add runtime instructions in the byte-identical probes; no broader overhead claim follows from them.

The edit is textually mechanical, but its semantic and compatibility risk is not established as zero: acceptance of checked bodies and callees, intrinsics, import and separate-compilation paths, existing checked callers, and all target platforms need coverage. A future checked caller can be accepted because of a marker, making an incorrect classification consequential. Prepare a reviewable library change only after auditing the candidates against the actual checker, then run full regression and checked-call coverage, including separate compilation and supported native targets. This review makes no library edits.

## WS4 — prevent a stale installer from qualifying as a release

Make packaging a **required release gate**, rather than requiring an installer rebuild on every development commit. A manual release workflow is compatible with the repository's human-review convention; it must fail closed when evidence is missing. Define an immutable source commit and tree digest, build the compiler from that tree, and build the installer from that exact compiler. Record source commit/tree, target, toolchain, compiler version and SHA-256, installer SHA-256, and build/test results in a release attestation. Verify the actual package payload, including both `bin/sutram.exe` and `win/sutram.exe` if both are shipped, against the freshly built compiler digest; a matching version string alone is insufficient.

Run the repository's Windows manifest update and setup build/preflight as documented, then independently inspect the resulting payload and checksum. On a clean supported Windows machine, install, verify the installed executable's digest and version, run a representative program, and exercise upgrade and uninstall. A missing build, mismatch, failed smoke test, or unrun native check means **not eligible**, not green. This gate prevents a v279 installer silently qualifying for v281, but does not magically rebuild it.

Avoid a self-referential commit requirement: an immutable source commit can be followed by a packaging commit whose manifest names that source commit and tree, or the artifacts and attestation can be attached to an immutable release. In either model the gate verifies the contents and their provenance, not merely that the installer and source happen to share a version label. No installer was built or installed for this round; no new automation is claimed.

## WS5 — proposed README copy and sign-off

Suggested opening, subject to the release checks below:

> Sutram is a programming language with Sanskrit keywords that compiles programs into native executables. Its documented subset lets students work with variables, arithmetic, conditions, loops, functions, and numeric lists. Whole numbers use `vitti`; `dasham` values are binary floating-point approximations. Integer calculations can wrap, and large floating calculations can produce `inf` or `nan`; floating-point division by zero stops with an error. Legacy `kosh` aliases can diverge when a buffer grows, and `mandapa` reclamation differs on Windows. The Windows installer and classroom package have not yet been accepted for release. Generics and threads are outside v1.

Suggested checked-function line:

> `parikshita` checks the compiler's documented function and call restrictions; the standard library is not yet marked, and this is not a whole-program memory-safety guarantee.

I would not sign off a v1.0 release on this evidence. The Windows compiler and the small probes above were run; a current-source Windows installer build, clean-machine install/upgrade/uninstall, complete regression suite, Linux native verification, exact floating boundary/rounding tests, and application-level checked-library performance and compatibility tests were **not run in this review**. Their status is unknown here, not passed or failed. The previously reviewed v279 installer is not evidence for a v281 package. The prose above is a candidate for review, not an assertion that the actual README has been updated or that every platform and classroom deliverable is release-ready.

