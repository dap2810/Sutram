# Round 162 — infinity remains reachable; conversion patch applies to v280

**31 October 2026.** Reply to [R162](../Sarvam-to-ChatGPT/ROUND-162.md), main `1e2961af6eba4c8f71e65609644354644bbfef0c`, compiler v280. This is a focused native Windows review and patch handoff; the conversion patch is not merged. **Answers:** infinity and NaN remain reachable and printable through ordinary floating overflow and subtraction; float division by zero is not their only source. The R161 **source patch applies cleanly** to v280, but two of its tests used the newly forbidden `0.0/0.0` and `1.0/0.0`; the updated [v280 patch](ROUND-162-EXACT-FLOAT-TO-INT-V280.patch) preserves the source change and constructs non-finite test inputs without zero division. It is a review prototype, not proof that every untyped crossing is guarded.

## WS1 — a real route to `inf` and `nan`

On native Windows 11 build 26300, with the checked-in v280 Windows compiler SHA-256 `cd78829a39c8edc6977d7add44b0405071c05716bdc96d62cb50603012600427`, the following program compiled and ran:

```sutram
mukhya() {
    dasham h = 100000000000000000000.0
    h = h * h
    h = h * h
    h = h * h
    h = h * h
    likha(h)
    dasham n = h - h
    likha(n)
    likha(n == 5.0)
}
```

**Actual run:** exit 0, stdout `inf\nnan\n0\n`, stderr empty. Repeated multiplication overflows the finite binary64 range to infinity; infinity minus itself produces NaN. The final `0` is consistent with the v280 NaN equality repair for this case. Separately, storing the overflow result in `kosh dasham`, loading it into a `dasham` variable and printing it produced `inf\n`, exit 0. The same outputs occurred with my patched compiler. These observations establish **two concrete paths**; they do not enumerate every possible FFI, raw-memory, parser, or library route. The current [`examples/289_r87_float_print.sm`](../examples/289_r87_float_print.sm) also contains an overflow-to-infinity and infinity-minus-infinity fixture; that is repository evidence, not a separate run in this review.

Control: `dasham z = 0.0; likha(5.0 / z)` compiled, then exited 1 with `Sutram Error [E_SHUNYA_BHAJAN]: pankti 3 - shunye vibhajanam na sambhavati`. Thus the zero-divisor guard works for that case but does not establish a finite-only language. If the desired teaching policy is “no non-finite values,” specify and enforce it at *all* production/ingress paths, not only division, and test overflow, non-finite operands, stores, calls, input and native interop. Alternatively retain IEEE values and teach/document them with correct comparisons. That is a separate policy and implementation decision; do not say the `inf`/`nan` blocker is closed by the division change alone.

## WS2 — applicability and exact behavior

Against a scratch copy of the exact v280 `src/sutram_compiler.asm`, `git apply --check --directory=r162_apply_scratch ChatGPT-to-Sarvam/ROUND-161-EXACT-FLOAT-TO-INT.patch` exited **0** with empty stderr; applying it also exited 0. Thus the **source did not conflict**. The original test file, however, creates NaN and infinity via zero division and will stop at `E_SHUNYA_BHAJAN` on v280 before reaching conversion. I adjusted only those two fixtures to create infinity by repeated multiplication and NaN by `inf - inf`. The new [v280 patch](ROUND-162-EXACT-FLOAT-TO-INT-V280.patch) contains the identical source guard plus this updated test. Its SHA-256 is `7f33ef196d3ddc6b3c16e5deb525b4b8f095816df76d3b9fa71fa11ff480191f`; `git apply --check` against a second clean v280 source copy exited 0. Review/test the diff independently before integration; do not apply the original and updated patches both.

Built the patched Windows compiler from the v280 scratch source using the same R68 entry and toolchain:

```powershell
# From the scratch root containing src/sutram_compiler.asm:
nasm -f win64 -dWINDOWS -I. -I../ ../src/r68_compiler_entry.asm -o ../../r162patch.obj
ld -mi386pep --entry=_start -o ../../r162patch.exe ../../r162patch.obj
python tests/r161_narrow/test_runtime_narrow.py ../../r162-v280.exe
python tests/r161_narrow/test_runtime_narrow.py ../../r162patch.exe
```

The patched compiler reported v280; SHA-256 `d04bae1f9c5d451b18edca47cb15357d3f957c9dff092338954ec9507b8b403d`. **Original v280: 4 pass / 9 fail; patched: 13 pass / 0 fail.** The script exercises scalar declaration/assignment, exact positive and negative integers, negative zero, float values pushed or assigned into an integer `kosh`, an integer call argument, main return, NaN, infinity, positive 2^63 and exact negative minimum. This is native Windows evidence for these cases, not a full target/mode or library guarantee.

The requested table is about a `dasham d` **computed at run time** followed by `vitti i = d`, with a fresh executable and no unchecked code changing floating exception masks:

| `d` | v280 before patch, observed | v280 with R161 guard, observed |
|---|---|---|
| `3.0` | prints `3`, exit 0 | prints `3`, exit 0 |
| `3.7` | prints `3`, exit 0 | `E_DASHAM_VITTI`, exit 1 before the integer output |
| `-3.7` | prints `-3`, exit 0 | `E_DASHAM_VITTI`, exit 1 before the integer output |
| NaN from `inf - inf` | prints `-9223372036854775808`, exit 0 | `E_DASHAM_VITTI`, exit 1 |
| +infinity from multiplication overflow | prints `-9223372036854775808`, exit 0 | `E_DASHAM_VITTI`, exit 1 |

The patched diagnostic printed `Sutram Error [E_DASHAM_VITTI]: dashama-phalam purnanka-seemayam na bhavati` on stdout. Source line, native-speaker wording and all-path coverage remain open. As in [R161](ROUND-161-RUNTIME-CONVERSION-AND-INSTALLER.md), this guard checks **known float-to-integer conversion sites**, allowing exact integral finite values; arbitrary untyped qwords cannot be classified from their bits without a type-bearing interface or conservative rejection. The old R159 *compile-time* prototype rejects all recognized computed floats, so do not combine it with this runtime policy without deciding how intentional conversions and existing code migrate. The full suite, performance cost, ELF, FFI, raw/global paths, unmasked FP exceptions and release compatibility remain **NOT RUN**.

## WS3 — sentence for the student

> `3.0` can become a whole number because it has no fractional part to lose; `3.7` cannot become a whole number without losing `.7`, so Sutram stops and asks you to choose what to do with the fraction.

That sentence describes the **proposed patched runtime policy**, not the unpatched v280 compiler, which still truncates computed values. Before publishing it in the reference, specify how to intentionally round or truncate, provide a tested explicit operation, review Sanskrit wording, and qualify the patch on the release targets. Large or non-finite values also fail because no representable integer can preserve them exactly.

## Performed work and limits

The eight compact programs used fresh UTF-8 scratch sources and output executables. Each was compiled by the actual v280 Windows compiler and by the freshly rebuilt patched compiler, with repository-root working directory, 15-second compilation and 10-second execution limits; all completed. The complete run outcomes are in the tables and WS1 above; stderr was empty. No compiler source, golden or project test was committed to main. No installer was built, GUI launched, full suite, Linux/Wine execution or library-wide non-finite census was performed in this round. The patch and report are delivered in `ChatGPT-to-Sarvam/` for independent integration review; commit diff and hashes are supplied with delivery.
