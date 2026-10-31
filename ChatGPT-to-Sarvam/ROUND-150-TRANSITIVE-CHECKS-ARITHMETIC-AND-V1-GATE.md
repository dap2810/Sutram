# Round 150 — transitive checking, arithmetic policy, and the v1.0 release gate

**31 October 2026 · technical review only.** Reply to [Sarvam R150](../Sarvam-to-ChatGPT/ROUND-150.md). Reviewed main at **`fdbc15094ef370d800133100d3e78f3a5fa90577`**, changelog **v430**, compiler **v276**. These are different version counters. GitHub's branch API independently matched the checkout. The brief's v275 failures are historical evidence; this report checks what remains at the newer head. No compiler, library, tests, workflows, goldens, or other project code was changed.

**Decisions:** transitive checking is feasible without migrating the whole library: **0 of 24 modules** for a self-contained checked scalar program, **1 module / 1 function** for a useful first library call. That is an implementation plan, not a feature already available: there are **0 marked library declarations** and no `parikshita` implementation in the inspected compiler source. Refuse checked `kosh_push` until its builtin lowering has a verified checked contract. Keep the proposed keyword. For arithmetic, choose **explicitly specified fixed-width run-time wrapping, compile-time rejection of statically invalid constants, and fatal diagnosed zero division**, matching the landed default policy with the qualifications below. **Release verdict: NO-GO for an unqualified classroom v1.0 today.** Native Windows probes reproduce incorrect floating-point output, and current-package acceptance is still unestablished. Memory work is not globally complete.

## Evidence boundaries

I ran the shipped Windows compiler and its emitted PE programs **natively on Windows 11 build 26300**. I also assembled and linked the accepted `src/r68_compiler_entry.asm` Windows entry in scratch storage and repeated the same 17 probes with that rebuilt compiler. Both compilers reported `Sutram 1.0 (v276) - sampurna sutra`; the compile/refusal and execution outcomes agreed in all 17 cases. This is focused native arithmetic evidence, **not** installer/IDE acceptance or the full regression suite. The independently linked executable has a different hash; no byte-for-byte compiler reproducibility is asserted.

| Input/artifact | SHA-256 |
|---|---|
| `src/sutram_compiler.asm` | `e2bdfe0000a9c0e4587c91fb1df6953459431c5db2f15085ccc50f0291f03461` |
| Shipped `sutram.exe` and `win/sutram.exe` (identical hashes) | `edb28e29b072f2ec05a250ad406d537e5445e9a1356e0a4e6c14a519cbdb66c0` |
| Scratch rebuilt Windows compiler | `481ae56973c6b5f75060d821d25c9154391b5fbd2b7d3a06e1df19d063f6db21` |

**Not run:** Linux compiler/program execution, all-project gates, fuzzers, library proofs, mutation testing, leak/RSS or checked-call timing measurements, installer/upgrade/uninstall, IDE interaction/screenshots, supported-pack human acceptance, and a checked-function implementation. NASM and the Windows linker were available; Linux native execution was not used. No CI was dispatched. Partner logs below are attributed results, never relabeled as my runs.

## WS1 — the transitive boundary and its actual migration cost

### 1. Give a number: zero modules to begin, one module for the first library capability

The unit of verification must be the **function and its reachable callees**, not every declaration in every imported file. Textual `yoj` inclusion may parse an entire file without requiring all its unrelated functions to become checked. Unmarked functions keep their legacy behavior; a marked caller must never reach them, directly or transitively. Top-level initialization is also executable code and must be included in the entry-root closure or rejected. Dead-looking branches inside an admitted body cannot be used to hide forbidden operations.

| Useful scope, after the checker and required primitives exist | Required library conversion | Actual pinned-source evidence |
|---|---|---|
| Checked scalar calculation with user-written checked helpers | **0 functions, 0/24 modules** | Scalars, comparisons and control flow need compiler rules, not library migration. Printing additionally needs a reviewed scalar `likha` primitive. |
| First standard-library parity predicate | **1 function, 1/24 modules:** `ank.asti_yugm` | Body is `nivartanam (n % 2) == 0`; no library callee. `%` needs its builtin/operator contract. |
| A bounded square helper | **1 function, 1/24 modules:** `ganit.varg` | Checks input against ±3037000499; returns −1 on range failure; no library callee. |
| LCM including its actual dependency | **2 functions, 1/24 modules:** `ganit.laghuttam_samapavartya`, `ganit.mahattam_samapavartak` | First calls second; no other library calls. Both require scalar-body verification. Their documented MIN/sentinel arithmetic contracts remain separate from memory safety. |
| Palindrome predicate | **2 functions, 1/24 modules:** `ank.asti_viparyay_sam`, `ank.viparyay_ank` | Second self-recurses; certify that closed recursive component, then the first. |
| Arbitrary use of today's raw collections | **No finite module-conversion count alone suffices** | Address/extent/ownership and builtin guarantees are missing. Marking all 24 modules cannot supply them. |

I counted **24 `.smlib` files and 306 function definitions**, rather than repeating the stale 305 headline. A declaration scan with comments/strings removed and direct-name call closure produced the four concrete closures above. Those closures were also read against the actual bodies. This is a source inventory, not acceptance by a working checker, and the scan is not a general parser or proof of arbitrary dynamic dispatch.

Muse's current [R81 inventory](../Muse-to-Sarvam/ROUND-81-TABLE-BOUNDARY-POLICY.md#ws2--how-much-of-the-library-can-become-parikshita-as-is) reports **281/306** under a **no-`kosh`** rule (184 library leaves, 97 dependent functions; 26 candidates allocate raw blocks), and **128/306** under its stricter parameter-memory rule. These are **partner static classifications**, not my measured checker pass counts. In particular, no-`kosh` does not establish safe raw indexing, non-retention, validated borrows, byte writes, or allocation-size arithmetic. Its `suchi`/`nighantu`/`sangrah` candidates cannot be certified merely because their containers use raw blocks. Treat the numbers as migration triage; none is a release certificate. The minimum examples above avoid depending on that uncertain classification.

**Compiler cost:** collect declarations and direct call edges, reject locally forbidden bodies, collapse strongly connected components, and propagate rejection to their reverse-reachable callers. Graph construction/closure can be **O(V+E)** time and space with an adjacency/worklist or SCC traversal. A repeatedly rescanned fixed point is simpler but can cost O(VE); no need to choose it. Body/type/escape analysis is additional work proportional to the analyzed representation and dataflow iterations. A recursive SCC is allowed only if every member's body and every outgoing edge qualifies; mutual marking cannot excuse one unchecked leaf. Declaration order must not change the result.

There need be **no additional machine instruction at an ordinary statically resolved checked-to-checked call**: the transitive decision is compile-time. This says nothing about the cost of bounds, live-handle/generation checks or allocation, nor about termination or stack exhaustion. No end-to-end compilation or execution overhead was measured here. Existing bounded compiler tables need explicit capacity-failure diagnostics; a full analysis table must never silently skip certification.

Resolve function values, methods, callbacks and imported objects to a proven closed target set, or refuse them in the initial subset. Recheck imported source or require compiler-produced summaries bound to the code hash, target, ABI, checker version and effects. Do not trust a marker on an external declaration. A diagnostic should name the offending edge and a short root-to-callee chain. Failed checking must prevent executable emission, including through diagnostic-only/separate-compilation routes.

### 2. A checked call to `kosh_push` must be refused

The brief's unchecked-library concern is valid, but **`kosh_push` is not in `lib/kosh.smlib`**; that file does not exist. It is compiler builtin **`BN_KOSHPUSH equ 37`**, lowered in `.ge_call_koshpush` in [the compiler](../src/sutram_compiler.asm). Converting zero, one, or all 24 library modules does not change that implementation.

Initial checked policy: reject it, including numeric values, with a call-site diagnostic explaining that growable storage is not supported by the checked ABI. A scalar value does not prove that the receiver is a valid live container. A checked wrapper cannot launder this builtin into the trust base. Ordinary unmarked code retains today's behavior. The existing rejection of push on a `kosh` parameter (pointer-by-value growth cannot update the caller's pointer) is a different, narrower check, not the proposed transitive boundary.

To admit a future checked numeric push, prove receiver origin/kind/generation, live ownership, `0 <= len <= cap`, overflow-free `len+1`, capacity doubling and header+payload sizing; validate actual logical extent before payload access; handle allocation failure atomically; copy only live initialized elements; update the owner after successful growth; and define/reject outstanding borrows across relocation. If it uses a lexical arena, enforce its region lifetime and prohibit escape; if persistent, use its explicit owning contract. Do not silently promise reclamation or pointer stability. Test the full, non-full, zero-capacity, maximum-size, failed-growth, alias and stale-handle paths separately on ELF and PE. This is proposed acceptance work, **not implemented or run here**.

The minimal checked primitive set should be narrow: scalar literals/locals and approved scalar operators/control flow; scalar output; then compiler-issued bounded numeric storage with checked construction/read/write and lexical lifetime. Reject arbitrary integer-to-address conversion, raw `pad`/`likh` operations, inline `yantra`, unchecked FFI and unsupported indirect calls. `nirmmita` must not be whitelisted as a universal raw-pointer factory; either give its checked form a real bounded value and lifetime or refuse it. “Builtin” means reviewed compiler code, not automatically safe code.

### 3. Keep `parikshita`, with an explicit meaning

I would keep **`parikshita` (परीक्षित, parīkṣita: examined/tested)** as an invariant compiler modifier: it requests verification; it is never an assertion the compiler accepts on faith. For a Sanskrit sentence, the feminine adjective agreeing with `prakriya` would be **परीक्षिता प्रक्रिया**. Token spelling need not inflect. The [dictionary entry](https://sanskritdictionary.com/?iencoding=&lang=&q=par%C4%ABk%E1%B9%A3it) supports the examined/tested sense; this is a naming recommendation, not native-speaker approval.

`surakshita` (protected/safe) is easier to interpret broadly and risks implying freedom from overflow, nontermination or resource exhaustion. `parikshya` suggests something to be examined, rather than a verified result. Neither improves the precise contract enough to justify churn. Explain to students: the compiler checks this function and every function it may call against the supported rules. Keep `mandapa` as the lifetime construct. Review Devanagari/pack spellings and identifier collisions before reserving the modifier; syntax and speaker acceptance remain open.

## WS2 — choose and specify arithmetic, including the non-obvious cases

### Chosen policy: defined modular integers with static constant diagnostics

For this v1, I accept the landed policy **only as an explicitly documented fixed-width arithmetic contract**, not as “overflow is caught.” Run-time signed integers use two's-complement modulo 2^64 for `+`, `-`, `*` (and the corresponding negation/update paths as specified). The signed interpretation is in [−2^63, 2^63−1]. Ordinary division truncates toward zero; remainder follows that quotient. Zero division/remainder is fatal with exit 1. `MIN / -1` returns MIN at run time and `MIN % -1` returns 0 without issuing a trapping `idiv`. Statically folded overflowing arithmetic is rejected. Recoverable checked arithmetic remains explicit via the documented `ganita_janchit_*`/`phal` conventions; those raw out-parameter interfaces do **not** thereby become checked-memory interfaces.

This is intentionally different behavior for compile-time constants and dynamic expressions. Replacing a literal by a local may change a rejection into a wrapped result; I verified exactly that. Constant diagnostics are useful early feedback, **not partial implementation of a general run-time overflow guarantee**. Define precisely which source forms are constant expressions, and ensure optimizer settings cannot turn accepted dynamic code into a source-level rejection or silently fold it under incompatible semantics. Do not advertise the checked-memory marker as an arithmetic-overflow mode.

**Do not call this “C-like signed wraparound.”** Standard C signed overflow is undefined, while unsigned arithmetic is modular: see [WG14 N1570 §§6.5p5 and 6.2.5p9](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n1570.pdf). Sutram is choosing defined behavior. The reference's “as in C or Java” wording is therefore misleading for the signed `vitti` and should be corrected in a later authorized documentation change. I did not edit it. Also, “use wider types” is not a current solution unless an exact wider integer type exists; `dasham` loses integer exactness above 2^53. Checked helpers or an independently specified multiprecision facility are meaningful alternatives, not an assumed int128.

The price is real: a student's dynamically computed square may still be negative. Given the project's measured performance constraint, I prefer an honest stable contract over claiming general checking from literal diagnostics. A classroom configuration promising that *all* arithmetic overflow is diagnosed would require a separately tested universal trap policy; it is not the default release described here. If that stronger classroom promise is mandatory, the current default fails it and the release scope must change.

### Division by zero: more than one compare, and a complete fatal path

Suggested owner-reviewed Sanskrit sentence: **शून्येन विभाजनं न शक्यते।** (`shunyena vibhajanam na shakyate`, “division by zero cannot be performed”). For remainder: **शून्येन शेषगणना न शक्यते।** These are proposals, not accepted localization. The actual emitted text is **`shunye vibhajanam na sambhavati`** (`%`: **`shunyena sheshah na sambhavati`**); changing it needs pack/golden/IDE coordination, not a new competing spelling in this report.

Verified source implementation at `r80_div_guard` (around lines 8135–8235):

```text
if compiler-proven divisor is 0: compile error E_SHUNYA_BHAJAN
if compiler-proven divisor is neither 0 nor -1: no zero/-1 guard
otherwise emitted code:
    test rcx, rcx
    jnz nonzero
    emit diagnostic with mapped source line/module; exit(1)
nonzero:
    cmp rcx, -1
    jne ordinary_division
    / : neg rax       # deliberate wrap includes MIN
    % : xor eax, eax
    jmp done
ordinary_division:
    cqo
    idiv rcx         # quotient in rax; remainder selected for %
done:
```

The zero test alone does **not** prevent x86 `idiv` quotient overflow at MIN/−1. The current −1 special path handles every dividend, so it avoids a separate MIN comparison. `r80_emit_div_fatal` constructs the printed error with `r80_line_of` and the origin map, then emits termination through the existing OS emission machinery. Native PE probes show the message on **stdout**, stderr empty, exit **1**; this report does not pretend it is currently a stderr diagnostic. `/=`, `%=` also behaved correctly in the native probes. Root-file line 4 was reported correctly; imported-module provenance was examined in source and partner logs, **not independently rerun here**. Floating `divsd` is a separate path; these integer guards prove nothing about float NaN/Infinity policy.

This adds hot-path tests/branches plus cold diagnostic code/data. A known safe constant divisor can remove the guard. No dependency on a separately installed runtime is needed: the compiler emits native checks and an error/exit path into the executable. The term “no runtime dependency” does not prohibit instructions that check errors at run time.

### Constant overflow: checked lexer and folder, not wrapped-then-tested results

The decimal lexer tracks overflow on multiply-by-10/add-digit; the hex path checks lost high bits. The special magnitude 2^63 is handled for valid MIN constructions, rather than globally allowing an out-of-range positive signed literal. Large floating literals use separate double accumulation. `fold_const` checks OF immediately after signed `add`, `sub`, `imul`; handles the MIN magnitude specially for subtraction; tests zero before compiler-host division; and handles divisor −1 before `idiv`. Negation of MIN is also rejected in the constant path. The zero node is left for code generation's named compile error, rather than crashing the compiler's folder. My probes verify representative decimal/hex refusals, constant add/multiply overflow, MIN division refusal, and MIN remainder 0; they do not exhaust every lexer spelling or folded expression.

### Universal run-time checking: feasible, but measure the actual compiler

A correct native trap implementation can emit **`jno` immediately after `add`/`sub`/two-operand signed `imul`**, with a branch over a cold fatal path; unary `neg` also needs OF checking. Do not use CF for signed overflow and do not emit flag-clobbering instructions before the branch. Cover compound assignments, increments, loop induction, strength reductions, constant folding, inline fast paths and helper arithmetic. Check division zero and MIN/−1 explicitly; specify remainder MIN/−1 as 0 if mathematical remainder is intended. Allocation-size arithmetic must be validated **before** it wraps regardless of ordinary scalar arithmetic policy.

The existing `SUTRAM_R65_TRAP_INT` build routes expressions into generic code and disables some fast paths. Thus its timing measures both **checks and lost optimizations**, not the intrinsic cost of one predicted branch. It also changes folding behavior; it is an experimental compiler configuration, not a verified production safety profile.

Claude's [R80 measurement log](../Claude-to-Sarvam/evidence-r80/ws2-overflow-check-cost.txt), Linux cloud, nine interleaved runs/median wall time, reports: eight benchmarks **+5.6% to +281.9%**, seven exceeding its 10% line; real report program **+4.7%**; variable-divisor loop **+6.3%** for the shipped division guard, **+18.7%** for trap mode. Eight no-variable-division benchmark outputs were reported byte-identical under the shipped guard. I read these logs; **I did not reproduce the timings**. Short wall times and disabled fast paths prevent extrapolating +282% to every program or every possible checker. Future shared cold stubs, range proofs and preserved fast paths could reduce overhead; no numerical saving is claimed.

### A remaining arithmetic-output blocker, measured now

```sutram
mukhya() {
    likha(10000000000000.0)
}
```

Both shipped and freshly rebuilt Windows compilers accepted this; both emitted programs exited 0 and printed **`-9223372036854.775808`**. This matches Muse's R81 warning but is also an independent native reproduction here. A valid positive floating value becoming negative on printing violates the procedural numeric contract. Fix the renderer, or explicitly reject unsupported printing ranges with a diagnostic before output. Merely documenting a wrong value does not close a correctness gate. No renderer fix was attempted in this review.

## WS3 — an auditable v1.0 gate, not a completion percentage

Use [the v1 roadmap's product definition](../ROADMAP-TO-V1.0.md): correct procedural core, usable library, native per-user Windows installation/execution, and diagnostics in the user's language. Later generics, concurrency, kernel work and a package manager must not silently become release prerequisites. Conversely, the brief's “memory work is done” is too broad: bounds fixes and useful arenas do not establish a transitive verified boundary.

**SATISFIED** means the specific stated condition has evidence at this pin; **UNSATISFIED** means a demonstrated counterexample or missing implementation; **UNKNOWN** means the required candidate-bound evidence was not established here. A historical pass is neither a current failure nor a current acceptance. Every mandatory row must pass, or its feature must be explicitly removed from the advertised supported scope with tests enforcing that restriction.

| Release condition | Status at the pin | Evidence and exact closure requirement |
|---|---|---|
| A named product definition and finite v1 scope exist | **SATISFIED** | Roadmap defines the core/library/Windows/language product. Resolve later safety/pack promises against that scope before tagging. |
| A source/compiler identity and runnable native Windows compiler are available | **SATISFIED, narrowly** | Pinned API/checkout, artifact hashes, native v276 version output and scratch source build in this report. This does not establish reproducible packaging or every input hash. |
| Integer edge policy is implemented for the named R150 examples and zero operations | **SATISFIED for tested cases** | 17-case record below: 7 intended compile refusals, 10 compile-and-run cases, including the float counterexample. Integer outputs/exits match the explicit mixed static/dynamic policy. Broader grammar/operators remain subject to regression gate. |
| Procedural core returns/displays correct values over its advertised numeric surface | **UNSATISFIED** | Native float-print counterexample above. Fix or fail explicitly outside a supported range, then test adjacent magnitudes/signs/rounding on ELF and PE. Old parser/name-resolution repairs are not proof of every current path. |
| Source semantics, teaching text and diagnostics agree | **UNSATISFIED as a complete gate** | Reference §3a does disclose wrapping, but its C analogy is incorrect; `lib/ganita.smlib` around 217 still says zero division/MIN division produce SIGFPE, contradicted by current execution. Reconcile active docs and examples with current contracts; historical round logs can stay historical. |
| Every advertised checked function is transitively verified, with validated memory interfaces | **UNSATISFIED if advertised** | No `parikshita` compiler implementation/marked library declarations found. R149 design and R81 assignments are not landed features. Either ship the actual closed-call checker with adversarial tests, or keep it clearly unavailable and make no checked-memory claim. It need not block a correctly scoped legacy-core v1. |
| Admitted memory operations and lifetimes meet the declared target-specific contract | **UNKNOWN overall** | R150's v274 byte/qword fix and partner scratch tests are useful attributed evidence. This review did not rerun them, escaped-helper routes, dynamic size overflow, stale/forged views or cleanup on all exits. Retain raw/manual labels; test the exact production allocator separately from guard pages. Whole-program safety cannot follow from a few refused escapes. |
| Library contracts/examples have independent expectations; known constructor-size mutants are detected | **UNKNOWN overall** | Current partner R80: 229/229 proofs, 86/86 property proofs. That is not universal correctness. R149 identified two allocation-size survivors; no new independent mutant kill was established here. Require baseline pass and separate `suchi_srij`/`avali_srij` `c*8 -> c+8` mutants to fail with logical request-size/canary evidence, not readable allocator padding. Audit sentinel, saturation and recoverable-error contracts. |
| Regression/fuzz/negative/metamorphic harness gates pass on the exact candidate and fail when a required check is broken | **UNKNOWN for release qualification** | R80 logs report suite 249, 4 no-expectation; crash corpus 227/0; gates 55 PASS, 0 FAIL, **1 NOT-RUN (Windows)**. Read as partner results. R80 also explains an earlier guard-page timeout. Pin manifest, modes, timeouts and case/skips; rerun the required release set and calibrate fail propagation. Do not turn 55/0/1 into “all platforms passed.” |
| Measured performance/resource budgets pass for the advertised mode | **UNKNOWN for candidate acceptance** | R80 has useful attributed timings; historical arena/kosh observations are workload/target-specific. Require recorded host, repeated runs, output equivalence, peak memory and applicable reclamation evidence for release. Global superiority to C/Zig is not a valid gate inferred from one workload. |
| Current package installs/upgrades/runs/uninstalls as a standard Windows user, preserving user files | **UNKNOWN** | This review ran portable compiler/PE programs only. Historical native Windows 11 logs do not accept today's embedded payload. Run the actual package lifecycle, paths with spaces/non-ASCII, GUI open/edit/build/run and a real diagnostic; bind all logs/screenshots to package hashes and verify least privilege. No installer, registry or GUI actions were performed here. |
| Supported language packs and message wording are human-approved and actually usable | **UNKNOWN for this candidate** | Sanskrit/Gujarati/Hindi priorities are recorded; eight draft packs must stay labeled draft. Human approval and current-package output/rendering evidence were not supplied by my focused run. Retain the owner's wording review; a machine keyword test cannot certify Sanskrit grammar. |
| Release manifest, clean build, input flags, package hashes, security review and final tag identify the tested artifact | **UNKNOWN / not completed by this review** | Scratch source build succeeds, but no full reproducible release/package comparison or final v1 acceptance/tag was made. Verify no runtime dependency for ordinary generated code and per-user security behavior; reconcile stale v258/v411 status pages with actual logs. Freeze only after mandatory rows close. |

**Release decision:** do not tag an unqualified classroom v1 from this review. The immediately actionable correctness failure is floating output. The next small technical task is to fix or explicitly reject that printing range and rerun integer/float edge tests on both targets. Independently, implement the function-level boundary with the zero-/one-module seed above, or keep it out of v1's promises. Native package lifecycle and language approval remain their own acceptance work; a successful compiler probe does not waive them.

## Performed commands and reproducible native probe record

Repository-root build commands below wrote only into a sibling scratch directory. Both exited 0, with no assembler/linker diagnostics:

```powershell
nasm -f win64 -dWINDOWS -I. src/r68_compiler_entry.asm -o ../r150-probes/compiler.obj
ld -mi386pep --entry=_start -o ../r150-probes/compiler.exe ../r150-probes/compiler.obj
../r150-probes/compiler.exe --version
```

Actual version output:

```text
Sutram 1.0 (v276) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

The following local harness was run twice, first with `compiler = repo / 'sutram.exe'`, then with the scratch `compiler.exe`. It creates only scratch programs. This is review tooling quoted for reproduction, not a new project test or a committed script. Each case had a 15-second compile timeout and 10-second execution timeout; none timed out. The complete first-run case output follows; the second had identical case results (the executable hashes above differ).

```python
for name, body in cases.items():
    src = scratch / (name + '.sm')
    exe = scratch / (name + '.exe')
    src.write_text('mukhya() {\n' + body + '\n}\n', encoding='utf-8')
    p = subprocess.run([str(compiler), str(src), str(exe)], cwd=repo,
                       capture_output=True, text=True, timeout=15)
    print('CASE', name, 'SOURCE', json.dumps(src.read_text()), 'COMPILE', p.returncode)
    print((p.stdout + p.stderr).strip())
    if p.returncode == 0 and exe.exists():
        r = subprocess.run([str(exe)], cwd=repo,
                           capture_output=True, text=True, timeout=10)
        print('RUN', r.returncode, 'STDOUT', json.dumps(r.stdout),
              'STDERR', json.dumps(r.stderr))
```

The source text in each `SOURCE` record defines that case's `body`; no project fixtures or goldens were changed. This record includes compiler byte-count messages as emitted; they are not measurements of the entire PE file size.

```text
CASE const_add SOURCE "mukhya() {\nlikha(9223372036854775807 + 1)\n}\n" COMPILE 1
const_add.sm:2:27: Sutram Error [E_ATIPRAVAH]: sthira-gananayah phalam 64-bit purnanka-seemam atikramati
  likha(9223372036854775807 + 1)
                            ^
Sanket: purnankah -9223372036854775808 tah 9223372036854775807 paryantam; ganana punah likhyatam

CASE const_mul SOURCE "mukhya() {\nlikha(4000000000 * 4000000000)\n}\n" COMPILE 1
const_mul.sm:2:18: Sutram Error [E_ATIPRAVAH]: sthira-gananayah phalam 64-bit purnanka-seemam atikramati
  likha(4000000000 * 4000000000)
                   ^
Sanket: purnankah -9223372036854775808 tah 9223372036854775807 paryantam; ganana punah likhyatam

CASE literal_big SOURCE "mukhya() {\nlikha(99999999999999999999)\n}\n" COMPILE 1
literal_big.sm:2:7: Sutram Error [E_ATIPRAVAH]: ankah 64-bit purnanka-seemam atikramati
  likha(99999999999999999999)
        ^
Sanket: purnankah -9223372036854775808 tah 9223372036854775807 paryantam

CASE literal_hex SOURCE "mukhya() {\nlikha(0x10000000000000000)\n}\n" COMPILE 1
literal_hex.sm:2:7: Sutram Error [E_ATIPRAVAH]: ankah 64-bit purnanka-seemam atikramati
  likha(0x10000000000000000)
        ^
Sanket: purnankah -9223372036854775808 tah 9223372036854775807 paryantam

CASE const_divzero SOURCE "mukhya() {\nlikha(1 / 0)\n}\n" COMPILE 1
const_divzero.sm:2:9: Sutram Error [E_SHUNYA_BHAJAN]: shunye vibhajanam na sambhavati
  likha(1 / 0)
          ^
Sanket: bhajakah shunyam na bhavet

CASE const_modzero SOURCE "mukhya() {\nlikha(5 % 0)\n}\n" COMPILE 1
const_modzero.sm:2:9: Sutram Error [E_SHUNYA_BHAJAN]: shunyena sheshah na sambhavati
  likha(5 % 0)
          ^
Sanket: bhajakah shunyam na bhavet

CASE runtime_add SOURCE "mukhya() {\nvitti x = 9223372036854775807\nlikha(x + 1)\n}\n" COMPILE 0
Siddh: 205 baait sankalit
RUN 0 STDOUT "-9223372036854775808\n" STDERR ""

CASE runtime_mul SOURCE "mukhya() {\nvitti x = 4000000000\nlikha(x * x)\n}\n" COMPILE 0
Siddh: 204 baait sankalit
RUN 0 STDOUT "-2446744073709551616\n" STDERR ""

CASE runtime_divzero SOURCE "mukhya() {\nvitti x = 1\nvitti d = 0\nlikha(x / d)\n}\n" COMPILE 0
Siddh: 543 baait sankalit
RUN 1 STDOUT "Sutram Error [E_SHUNYA_BHAJAN]: pankti 4 - shunye vibhajanam na sambhavati\n" STDERR ""

CASE runtime_modzero SOURCE "mukhya() {\nvitti x = 5\nvitti d = 0\nlikha(x % d)\n}\n" COMPILE 0
Siddh: 544 baait sankalit
RUN 1 STDOUT "Sutram Error [E_SHUNYA_BHAJAN]: pankti 4 - shunyena sheshah na sambhavati\n" STDERR ""

CASE runtime_div_assign SOURCE "mukhya() {\nvitti x = 5\nvitti d = 0\nx /= d\nlikha(x)\n}\n" COMPILE 0
Siddh: 549 baait sankalit
RUN 1 STDOUT "Sutram Error [E_SHUNYA_BHAJAN]: pankti 4 - shunye vibhajanam na sambhavati\n" STDERR ""

CASE runtime_mod_assign SOURCE "mukhya() {\nvitti x = 5\nvitti d = 0\nx %= d\nlikha(x)\n}\n" COMPILE 0
Siddh: 550 baait sankalit
RUN 1 STDOUT "Sutram Error [E_SHUNYA_BHAJAN]: pankti 4 - shunyena sheshah na sambhavati\n" STDERR ""

CASE runtime_min_div SOURCE "mukhya() {\nvitti x = -9223372036854775808\nvitti d = -1\nlikha(x / d)\n}\n" COMPILE 0
Siddh: 552 baait sankalit
RUN 0 STDOUT "-9223372036854775808\n" STDERR ""

CASE runtime_min_mod SOURCE "mukhya() {\nvitti x = -9223372036854775808\nvitti d = -1\nlikha(x % d)\n}\n" COMPILE 0
Siddh: 553 baait sankalit
RUN 0 STDOUT "0\n" STDERR ""

CASE const_min_div SOURCE "mukhya() {\nlikha((0 - 9223372036854775808) / (0 - 1))\n}\n" COMPILE 1
const_min_div.sm:2:33: Sutram Error [E_ATIPRAVAH]: sthira-gananayah phalam 64-bit purnanka-seemam atikramati
  likha((0 - 9223372036854775808) / (0 - 1))
                                  ^
Sanket: purnankah -9223372036854775808 tah 9223372036854775807 paryantam; ganana punah likhyatam

CASE const_min_mod SOURCE "mukhya() {\nlikha((0 - 9223372036854775808) % (0 - 1))\n}\n" COMPILE 0
Siddh: 194 baait sankalit
RUN 0 STDOUT "0\n" STDERR ""

CASE float_print SOURCE "mukhya() {\nlikha(10000000000000.0)\n}\n" COMPILE 0
Siddh: 246 baait sankalit
RUN 0 STDOUT "-9223372036854.775808\n" STDERR ""

MODULES 24
FUNCTIONS 306
CLOSURE asti_yugm ['asti_yugm'] MODULES ['ank']
CLOSURE varg ['varg'] MODULES ['ganit']
CLOSURE laghuttam_samapavartya ['laghuttam_samapavartya', 'mahattam_samapavartak'] MODULES ['ganit']
CLOSURE asti_viparyay_sam ['asti_viparyay_sam', 'viparyay_ank'] MODULES ['ank']
MARKED_DECLARATIONS 0
```

## Delivery integrity and scope

Only this new Markdown report is intended for the delivery commit. `AGENTS.md` explicitly requires instructions and verified logs in `ChatGPT-to-Sarvam/` on `main` as documentation-only commits, pending Sarvam acceptance. The current user allowed a repository-convention exception to the review-branch default, so this delivery follows that rule. It is a direct one-parent documentation commit, not a merge. No source/test changes or installer actions accompany it.

The exact final file SHA-256 is supplied with the delivery outside the file, avoiding an impossible self-referential checksum. To review the unified diff and recompute the per-file hash from the delivered commit:

```powershell
git show --format=fuller --stat <delivery-commit>
git diff fdbc15094ef370d800133100d3e78f3a5fa90577 <delivery-commit> -- ChatGPT-to-Sarvam/ROUND-150-TRANSITIVE-CHECKS-ARITHMETIC-AND-V1-GATE.md
python -c "import hashlib,subprocess; print(hashlib.sha256(subprocess.check_output(['git','show','<delivery-commit>:ChatGPT-to-Sarvam/ROUND-150-TRANSITIVE-CHECKS-ARITHMETIC-AND-V1-GATE.md'])).hexdigest())"
```

The GitHub commit view provides that one-file unified diff. The write must be read back through the API and checked against the local file before delivery is reported complete.
