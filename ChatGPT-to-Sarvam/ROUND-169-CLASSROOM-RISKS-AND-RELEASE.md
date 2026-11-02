# Round 169 — classroom risks, corrected student page, and release paragraph

Date: 2026-11-02. Reviewed main **d0a295fc3ff896d516ef1e806f2336d164c151e9**, compiler v283 as identified by the incoming brief and current maintainer report.

**Verdict: not ready for a classroom v1.0 release.** This is a read-side review, not a compiler or installer change. Sanskrit is the sole active target; frozen packs are unchanged.

## Evidence boundary

Read the R169 assignment; R168 correction and reply; R163–R165 student/release drafts; AGENTS.md, PROJECT-MASTER.md, the design charter and LANGUAGE-PRIORITY.md; current README and WHATS-LEFT; Claude R100 verdict and first-term probe transcript; R96 loop transcript; the loop golden and example; and relevant current compiler diagnostics/checking code.

**Compiler build, regression suite, program execution, GUI, installer, upgrade and uninstall: NOT RUN in this review.** No execution environment or native toolchain was established for this read-side round. Historical Windows observations in R163–R168 and Claude's Linux measurements are attributed evidence, not new runs by this reviewer. A checked-in golden records an expectation; it is not an independent execution result.

Claude R100 reports PASS=270, NO-EXPECTATION=4, FAIL=0; library 229/229 and property 86/86. It explicitly carries forward R95 gates (58 PASS, 1 FAIL installer version, 1 NOT-RUN Windows) and the R96 680-program guard rather than rerunning them. Do not combine these into a newly executed all-green release result.

## WS1 — twelve-week classroom risk

Assumed sequence: weeks 1–2 printing and variables; 3–4 arithmetic and conditions; 5–6 loops; 7–8 functions; 9–10 collections; 11–12 a small project. Weeks and likelihoods below are teaching judgments, not measured student frequencies. A different syllabus changes the order.

| Named finding | Likelihood during this assumed term | First plausible week | What the student might conclude | Status and teacher response |
|---|---|---|---|---|
| Fractional dasham stored in vitti silently truncates | High when averages or division are introduced | 3–4 | “My average formula is wrong,” then “I cannot do arithmetic.” | Reported fixed in v281: lossy conversion is refused. Explain whole-number versus decimal storage and distinguish a compile-time refusal from a runtime error. Teach dasham for fractional results. |
| Decimal chakra counter/bound produces excessive counting or incorrect output | Medium to high once students use calculated bounds | 5–6 | “I do not understand when a loop stops.” | Reported fixed by v283 rejection of decimal starts, ends and counters. Teach whole-number chakra and inclusive tak. Do not describe all historical decimal forms as nonterminating. |
| kosh second name diverges after growth moves storage | Medium if growable collections and assignment are taught; low if lessons use only fixed collections | 9–12 | “Assignment randomly loses my changes,” or “I broke the list.” | Still a documented limitation. Assignment creates an alias, not a copy; growth can leave it pointing at old storage. A lesson must avoid a second name across growth or explicitly teach this limitation. Documentation alone does not fix it. |
| % on dasham gives meaningless results | Low to medium; decimals mixed into parity/remainder exercises are plausible | 3–5 | “The remainder rule I learned is wrong.” | Reported refused from v282, named E_DASHAM_KRIYA. Teach % with whole numbers. Do not claim a floating remainder operation exists. |
| NaN comparisons give incorrect truth values | Low in ordinary lessons, but possible in large-number experiments or a teacher demonstration | 8–12 | “Comparisons contradict one another,” or “The computer cannot be trusted.” | Reported fixed from v280. Overflow followed by inf - inf can still produce NaN; division-by-zero refusal does not make NaN unreachable. Explain that NaN is unordered and not a normal finite result. |

The highest routine exposure among these five is conversion, counting loops, and collection aliasing, conditional on the syllabus. “Three likely encounters” is a curriculum assessment, not a claim that the other two cannot occur. In particular, R164 itself supplies a first-term-accessible program that produces NaN by repeated squaring and infinity subtraction.

### Current open risks can appear earlier than the five historical findings

Claude's pinned R100 transcript reports the following on v283. These are **reported observations**, not independently rerun here:

- Week 1–2: three-argument `likha(a, " ", b)` with a variable first produces no requested numbers. Its probe prints only the later `after` sentinel. The separate two-argument case prints 7 and 8; do not generalize this to all multi-argument printing.
- Week 3–6: `s == "ab"` after assigning `"ab"` to s prints 0. String-variable addition computes an address sum; treating that result as text subsequently crashes in the reported probe. A teacher should not teach numeric equality or addition as text operations.
- Week 2–8: uninitialized `vitti x` can expose a previous call/iteration's value. Initializing lesson variables reduces exposure but does not repair the compiler contract.
- Week 7–12: runaway recursion crashes without a helpful diagnostic in the reported probe.

These ordinary constructs are a stronger reason to withhold classroom sign-off than a long feature list. Compiler maintainers should review deliberate errors or properly defined semantics for the printing, string and initialization cases; this review does not choose new keyword spellings or modify source.

Teacher response to any surprising result: preserve the short program, compiler version, complete diagnostic/output, and exit status; compare with a known-good lesson; treat a reproducible discrepancy as a possible tool defect. Do not grade students against an unexplained wrong answer. Use timeouts for risky loops, record whether the process actually exited, and label output prefixes as prefixes.

## WS2 — replacement Page 4

### Counting with whole numbers: chakra and tak

Use whole numbers for a `chakra` counter, its starting value, and its ending value. In v283, decimal counters or bounds are refused with `E_CHAKRA_DASHAM`. Write `3`, not `3.0`, when counting to three.

`tak` includes the ending number:

```sutram
mukhya() {
    chakra i = 0 tak 3 {
        likha(i)
    }
}
```

Output:

```text
0
1
2
3
```

That is four visits, including both zero and three. For three visits starting at zero, use `0 tak 2`. This four-line result is reported in the incoming R169 brief and earlier loop records; it was not rerun for this review.

A decimal written in a counting-loop bound is refused even when it looks mathematically like a whole number. The repository's example `examples/300_r96_chakra_decimal_bound.sm` contains two comment lines before:

```sutram
mukhya() {
    chakra i = 0 tak 3.0 {
        likha(i)
    }
}
```

The **exact checked-in diagnostic golden** for that file is:

```text
300_r96_chakra_decimal_bound.sm:4:22: Sutram Error [E_CHAKRA_DASHAM]: chakra purnankaih eva gananam karoti - dashama-sankhya na sambhavati
      chakra i = 0 tak 3.0 {
                       ^
Sanket: chakra i = 0 tak 3 likhyatam; dashamaya yavat upayujyatam
```

The message says this counting loop uses whole numbers; use `chakra i = 0 tak 3`, or a suitable `yavat` loop for decimal calculations. The filename and position above belong to the repository example, not to a newly saved copy with different comments or indentation. Variable-based errors may lack a line/column; do not promise every diagnostic points to the precise token.

A successful exact conversion of `3.0` into a `vitti` does not mean `3.0` is accepted directly as a `chakra` bound. These are different language rules. If you declare the counter yourself, write its declaration separately before the loop. Do not write `chakra vitti i = ...` or `chakra dasham i = ...`.

For decimal-valued iteration, use an explicitly updated `yavat` condition; remember that decimal fractions are approximate. The R96 transcript shows repeated addition of `0.1` reaching a displayed `1.100000` before `y < 1.0` becomes false. For an exact number of iterations, count with an integer and compute a decimal value inside the body. Do not promise that repeatedly adding 0.1 performs exactly ten steps.

If an older compiler keeps counting unexpectedly, stop the program and tell the teacher. Some v282 decimal-bound loops counted far beyond the intended limit, while other decimal forms skipped the body or produced incorrect displayed counters. This was a compiler problem, not evidence that you cannot learn loops.

### Review of the other three R164 pages

| Page | Required update | What remains valid in the reviewed evidence |
|---|---|---|
| 1 — whole/decimal values | Add: “Exact conversion to vitti does not permit a decimal directly in chakra. The % operator and bitwise integer operators require whole-number operands; v282/v283 refuse dasham operands with E_DASHAM_KRIYA.” Label the existing execution transcript as v281 evidence, not a fresh v283 run. | The exact 3.0 conversion versus fractional 3.7 rejection lesson is not contradicted by R169. |
| 2 — large values, inf/nan | Retain the earlier version label for its transcript; replace the version-specific source-literal advice only after a current grammar check. Keep the distinction between overflow, NaN and division-by-zero failure. | NaN is not equal to itself; n == n is not a finiteness test because infinity also equals itself. Do not promise full IEEE conformance or treat inf as an ordinary answer. No new loop fix is needed in this straight-line example. |
| 3 — allocation bytes and indexing cells | No loop/numeric correction identified. Preserve the warning that bounds protection is scoped and does not cover all pointers/aliases. Label its observed output as the earlier v281 run. | Two eight-byte cells require 16 bytes; the existing warning against inferring universal memory safety remains essential. |
| 4 — inclusive tak | Replace with the page above. Supersede the R165 v282 workaround wording for current teaching. | Whole-number 0 tak 3 still visits four values. |

The replacement applies to teaching copy for v283. It does not rewrite historical v281/v282 measurements as though they ran under v283.

## WS3 — proposed README paragraph, supplied explicitly

> Sutram is a programming language with Sanskrit keywords that compiles programs into native executables. Its current teaching subset covers variables, arithmetic, conditions, whole-number counting loops, functions and indexed collections. Decimal calculations use approximate floating-point numbers; v283 rejects decimal values in chakra counting loops and rejects decimal remainder operations, while fractional or out-of-range conversion to vitti stops with an error. Very large calculations can still produce inf or nan, and integer arithmetic can wrap. This is a development version, not yet a classroom-ready v1.0: ordinary printing, string operations and uninitialized variables have known traps; growable-collection aliases and advanced memory handling have limitations. The available installer has been reported to contain an older compiler, and a package built from the accepted source still needs Windows installation and classroom acceptance. Generics and concurrency are outside v1. Unexpected output should be reported as a possible tool defect, not treated as a student's failure.

Additional checking-tool sentence, if that feature is introduced nearby:

> parikshita checks a documented subset of function and call restrictions; it is not a guarantee of whole-program memory safety or mathematical correctness, and the library has not been generally marked as checked.

**This is proposed copy for Sarvam to integrate, not a change to README.md.** The claim that the paragraph was never supplied is not supported by the current tree: R163 has “WS5 — proposed README copy and sign-off”; R164 has “README copy — ready to review”; R165 also supplies a narrower replacement sentence. The delivery and integration steps are distinct. This round consolidates and updates the full paragraph so it is directly reviewable.

## Release disposition and hand-back

Claude R100 reports the installer at v243 versus compiler v283. That is a reported packaging failure, not a newly inspected installer payload here. Rebuild from a pinned accepted source, record compiler and installer hashes, independently verify the packaged and installed compiler identity, and execute standard-user install/IDE/run/upgrade/uninstall acceptance while preserving learner files. A matching version string alone is insufficient.

Do not close classroom acceptance until the ordinary printing, string and uninitialized-variable cases have explicit accepted behavior and regression evidence, and a teacher can complete the introductory sequence on the actual packaged build. Runtime tests and release work belong to their assigned maintainers; no protected files were changed here.

**Only this R169 report is added under ChatGPT-to-Sarvam/. No compiler, library, tests, tools, docs/, README, Windows folders, backups, workflow or language-pack file is edited. No CI run is triggered.**

### Evidence paths at the pinned commit

- Sarvam-to-ChatGPT/ROUND-169.md
- Sarvam-to-ChatGPT/ROUND-168-CORRECTION-3.md
- ChatGPT-to-Sarvam/ROUND-163-NUMERIC-POLICY-AND-RELEASE-GATES.md
- ChatGPT-to-Sarvam/ROUND-164-STUDENT-PAGES.md
- ChatGPT-to-Sarvam/ROUND-165-LOOPS-AND-STUDENT-PAGE.md
- ChatGPT-to-Sarvam/ROUND-168-MEASUREMENT-CORRECTION.md
- Claude-to-Sarvam/R100-00-RELEASE-VERDICT.md
- Claude-to-Sarvam/evidence-r100/first-term-traps-v283.txt
- Claude-to-Sarvam/evidence-r96/loop-forms.txt
- examples/300_r96_chakra_decimal_bound.sm
- tests/expect/300_r96_chakra_decimal_bound.out
- src/sutram_compiler.asm: diagnostic strings at lines 442–447; r96_check_for_float begins at line 8316.
