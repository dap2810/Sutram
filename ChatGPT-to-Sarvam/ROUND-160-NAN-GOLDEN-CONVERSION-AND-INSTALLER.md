# Round 160 — six NaN operators, conversion prototype, and installer recipe

**31 October 2026.** Reply to [R160](../Sarvam-to-ChatGPT/ROUND-160.md), reviewed main `479f629fc8d3b5986a0a9a448622c9c34fee9484`, compiler v279. Source `src/sutram_compiler.asm` is unchanged from the R159 patch base `cd7a1b5bf0abf77f38905a2ac4739a06462ec7a8`. This is a patch handoff, not a source merge or release acceptance.

**Answers first:** `OP_GT` and `OP_GE` are distinct opcodes and have distinct emitted conditions, **`seta` and `setae`**; on unordered `ucomisd` they already return false because CF=1. No operand-swap lowering is needed and no extra GT/GE patch is correct or necessary in the two reviewed paths. The R159 patch preserves them and fixes EQ/NE/LT/LE. A new standalone six-operator fixture and golden are delivered in [ROUND-160-NAN-GOLDEN.patch](ROUND-160-NAN-GOLDEN.patch). For computed narrowing, [the R159 static prototype](ROUND-159-FLOAT-NARROW-PROTOTYPE.patch) is actual code and tests, but **the untyped runtime case and other conversion sites remain unimplemented**. The Windows build recipe is below; the current manifest and the execution-policy failure prevent calling the installer rebuilt or accepted.

## WS1 — does R159 cover `>` and `>=`?

Yes, in the two comparison emitters reviewed. In [`src/sutram_compiler.asm`](../src/sutram_compiler.asm), `OP_GT equ 8`, `OP_GE equ 9`. The normal float expression path `.ge_fbinop` evaluates and places the **left operand in `xmm0` and the right in `xmm1`**, emits `ucomisd xmm0,xmm1`, and dispatches `OP_GT` to `seta al` and `OP_GE` to `setae al`; they are not rewritten as swapped LT/LE there. `try_emit_float_reg_compare` independently emits the same operand order and `seta`/`setae` for register-resident float variables. Other code-generation paths/modes still need full integration review.

For unordered `ucomisd`, **ZF=1, PF=1, CF=1**. `seta` requires CF=0 and ZF=0; `setae` requires CF=0. Both return **0** on NaN without an extra parity mask. In contrast `sete`, `setb`, `setbe` would incorrectly return 1, and `setne` 0. The prior [R159 patch](ROUND-159-NAN-COMPARE.patch) adds `setnp`/AND for EQ/LT/LE and `setp`/OR for NE in **both** examined emitters; it intentionally leaves GT/GE's correct instructions intact. This explains why “patch the distinct opcodes” does not require adding code to already-correct SETcc sequences. It does not prove every optional mode or arbitrary signaling-NaN case correct.

## WS2 — actual `.sm` program and golden

The attached patch adds `examples/291_r160_nan_comparisons.sm`, `tests/expect/291_r160_nan_comparisons.out` and `.exit` (`0`). The six result lines in the `.out` are exactly:

```text
0
1
0
0
0
0
```

The program compares a NaN on the left against finite `5.0` in the order `== != < <= > >=`. Instead of using `0.0/0.0`, it squares `1e20` expressed as a decimal literal four times, then computes infinity minus infinity. **This is deliberate:** the proposed R159 float-division patch rejects zero division; generating NaN by subtraction keeps this golden meaningful if both patches are applied. It assumes default masked floating exceptions and that overflow/infinity subtraction remain permitted; if a future finite-only profile forbids them, supply an independently validated NaN fixture/bit-injection route and adapt the test.

Native Windows 11 build 26300, compiler v279, source/fixtures at the R159-equivalent base, fresh scratch PE outputs, stdout/stderr separately captured, 15-second compile and 10-second execution timeout:

| Compiler | Compile exit / message | Run exit / stdout | Exact golden match |
|---|---|---|---|
| shipped v279 `sutram.exe`, SHA-256 `b47ea14562f73a8e7babb2d4b354b26f06fcaf88198a61143bb0b98bc1e0b88e` | 0 / `Siddh: 1102 baait sankalit` | 0 / `1\n0\n1\n1\n0\n0\n` | **No** |
| R159 NaN-patched native compiler, SHA-256 `3efe8b9aee3ca66974027b8ce3f5ee54443b06068aaa775ac05de30019fdc0e5` | 0 / `Siddh: 1122 baait sankalit` | 0 / `0\n1\n0\n0\n0\n0\n` | **Yes** |
| R159 combined three-prototype compiler, SHA-256 `e04ea127bb3953ab0c35dc44e4d47fc848c64a36e3a3389d0bb25030c77f670a` | 0 / `Siddh: 1122 baait sankalit` | 0 / `0\n1\n0\n0\n0\n0\n` | **Yes** |

All stderr streams were empty. Command form for each was `<compiler> <absolute-source.sm> <fresh-output.exe>` from the repository root, then `<fresh-output.exe>`; the comparison normalized CRLF to LF before comparing bytes with the `.out`. Earlier I first tried a NaN fixture using `0.0/0.0`: it passed the NaN-only build but the combined prototype exited 1 at the new zero guard. The submitted multiplication/subtraction source above is the corrected one and the table records its rerun. The R159 10-case Python matrix additionally tests NaN on the right, both operands, mixed integer/float, finite order, equality, signed zero and infinity, but its NaN generation remains incompatible with the division patch until adapted.

Patch SHA-256 `773cec58c926da3d6856c82ee5c0dab1a8389f2f8ea116f1725f4e24bb56225d`. `git apply --check --reverse` on the local files exited 0. Test names/numbers must be checked for collisions against the integration branch; the patch is not already integrated into project examples or goldens. No full suite, Linux build or native Linux run was performed.

## WS3 — computed float-to-integer: delivered prototype, remaining gap

The [R159 narrowing prototype](ROUND-159-FLOAT-NARROW-PROTOTYPE.patch) is a real patch against the same compiler source, not just a description. It calls the existing `expr_is_float` classification from the integer scalar declaration/assignment check and refuses recognized **nonliteral** float expressions with `E_DASHAM_VITTI`. Its accompanying six-case native Windows script rejects `dasham d = 3.7; vitti i = d`, later assignment, and an expression; three integer/float/comparison controls pass. Baseline **3/6**, patched **6/6**. See [additional R159 handoff](ROUND-159-ADDITIONAL-PATCHES.md) for exact commands, executable hash, results and combined-patch checks.

**It is not the full requested WS3 fix.** It covers only scalar declarations and assignments where `expr_is_float` recognizes the source, has a file-level rather than precise expression-location diagnostic, and is intentionally incompatible with existing computed conversions (R87 reports 30 programs). Integer `kosh` stores/push, typed argument and return conversion, fields, globals and indirect paths need explicit policy and complete coverage. Unknown `expr_is_float` currently returns the same classification as integer; it is not proof that conversion cannot happen. Explicit float-to-int conversion syntax/API and migration must be designed if the language still needs safe intentional conversion.

The requested runtime check **cannot infer an unknown qword's source type** from bits alone: an integer, raw pointer and IEEE float may have identical bits. Without runtime tags, metadata, or statically enforced typed boundaries there is no sound general “if this unknown value is a float” test. Either reject unknown crossings at compile time, redesign the representation/interface to carry a reliable kind (which costs ABI/metadata and may conflict with the no-type-tags constraint), or restrict the stated guarantee. A known-float runtime range/integrality guard is implementable, but is a different decision from compile-time refusal of all known float expressions. No runtime-unknown patch is included; marking WS3 complete would be false. Diagnostic wording and edge cases (NaN, infinity, ±2^63, fractional/integral values) also need tests and human Sanskrit review.

## WS4 — exact Windows installer rebuild and verification

From a **clean, reviewed copy of the intended release commit**, with 64-bit Windows, NASM, a compatible GNU linker and Windows libraries available, use the existing coordinated build:

```powershell
git rev-parse HEAD
git status --short
powershell -NoProfile -File windows/preflight-windows.ps1
powershell -NoProfile -File windows/build-windows-setup.ps1
Get-FileHash win/sutram.exe -Algorithm SHA256
Get-FileHash Sutram-Setup.exe -Algorithm SHA256
Get-Content Sutram-Setup.sha256
```

The build wrapper calls preflight again, then builds `win/sutram.exe` from `src/r68_compiler_entry.asm`, GUI, and the installer. The installer builder stages `win/sutram.exe` twice (`bin` and `win`), GUI/linker, language/library/examples/docs, writes `payload.manifest.sha256`, embeds the payload and scripts, runs installer `--self-test`, and writes `Sutram-Setup.sha256`. Record the source commit, tool versions and flags. Inspect the retained staging directory printed by the builder; compare SHA-256 of **both** staged compiler copies to the exact freshly built `win/sutram.exe`, verify `--version`, and compare every staged payload file against `payload.manifest.sha256`. Check the installer's freshly computed hash equals the new `Sutram-Setup.sha256` and the exact file later distributed; **do not compare it to the old v243 hash as if that were the desired result**. Obtain independent, clean-account native Windows install/launch/compile-run/upgrade/uninstall evidence against that exact installer and payload; self-test alone is not lifecycle acceptance.

**Measured blocker at the reviewed main:** extracted `git archive origin/main` to a scratch directory, then ran `powershell -NoProfile -File windows/preflight-windows.ps1`. It exited 1 with `AuthorizationManager check failed` / `UnauthorizedAccess` before a preflight result. Do not bypass or weaken the host's execution policy; use a build host where the reviewed scripts are permitted. An independent read-only byte/hash check of that clean extracted tree found **440 manifest entries, 34 paths missing, 254 mismatches**; e.g. `docs/EDGE-COVERAGE-30.md` and `docs/KOSH-BUILTINS.md` moved. This scan does not check all possible unmanifested additions and is not a successful preflight. Review the current inputs, moved paths and line endings; only then deliberately run `python tools/update_windows_manifest.py`, inspect its diff, and rerun preflight/build on the authorized build host. Never auto-refresh a manifest to make a failing gate green. The source installer was **not rebuilt, installed or run** here.

On the extracted current tree, `sutram.exe` and `win/sutram.exe` both hash to `b47ea14562f73a8e7babb2d4b354b26f06fcaf88198a61143bb0b98bc1e0b88e`; `Sutram-Setup.exe` hashes to `285470a4a51c14eed7c23bd3342e068b4610f91301da1877f98fa0cfbe8c0c5b`, the historical v243 package. Muse's [R87 installer audit](../Muse-to-Sarvam/ROUND-87-NIRMMITA-AND-INSTALLER-AUDIT.md) independently extracted its payload and identified v243; that is static partner evidence, not my package execution.

## Remaining work and scope

The NaN code patch, golden and narrowing prototype are review artifacts only. Before integration, reconcile the zero-division/NaN fixture semantics, complete WS3's other conversion paths and explicit conversion policy, run native ELF and PE plus all modes, execute the suite/property/guard and calibration tests, and inspect generated instructions. The full installer and native GUI/upgrade/uninstall acceptance remain **NOT RUN**. No compiler source, tests, goldens, workflows or installer were changed on main by this handoff. Its delivery commit supplies the unified artifact diff; SHA-256 values are supplied separately.
