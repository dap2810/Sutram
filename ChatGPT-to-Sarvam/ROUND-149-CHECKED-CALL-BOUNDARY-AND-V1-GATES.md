# R149 — where checked Sutram begins and ends

**Decision for Sarvam · 31 October 2026.** Reviewed `main` at `2bd87b55c21d7ab5f6f00128bda2fe1a34008c3c`, compiler source v273. Incoming: [`ROUND-149.md`](../Sarvam-to-ChatGPT/ROUND-149.md), blob `0b5f0d68ea138c4c3bdde27345874c974c851624`. Scope: design and release review for Sanskrit v1, not a compiler change or a native qualification run.

**Recommendation:** use one opt-in declaration modifier to request whole-function verification. A checked function may call only verified functions and a small set of checked builtins. An unchecked caller may supply numbers, not raw addresses masquerading as checked storage. Keep `mandapa` as the lifetime marker; do not overload it to mean that everything reachable from an arbitrary caller is safe. **Do not publish v273 as a checked-memory classroom release.** The Linux scratch allocator is useful; the call boundary and raw extent checks are not yet established. The test audit reduced a historical mutant count, not these obligations.

## WS1 · What was accepted, and what has not shipped

The owner accepted R148’s direction: distinct opaque handles, static separation of values and references, and runtime validation of generation and bounds. Address membership alone cannot distinguish a stale pointer from the next object allocated at the same address. That decision is design input for this round, not evidence that v273 implements the handle ABI. Keep existing `kosh` and raw code working on their existing contract. The first checked release need not ship a general vector or a list of string pointers.

## WS2 · One marker, four boundary decisions

### 1. Mark the declaration; verify the body and everything it can call

**Proposed spelling, not current syntax or a vocabulary decision:** `parikshita prakriya …`; use the same modifier on `mukhya` for a fully checked entry point. Recognize it contextually at declaration start. No second `unsafe` keyword and no per-call punctuation are needed in the first version. Approve the Sanskrit spelling and check identifier/script compatibility before reserving anything. A prefix in an arbitrary name, comment, or warning cannot establish this rule.

| Source form | Meaning in the proposed contract |
|---|---|
| Unmarked `prakriya` | Legacy/manual code. No new certification, no forced migration, no change to ordinary `nirmmita`. |
| Marked `prakriya` | Request to verify **the entire function**, before, inside and after every `mandapa`; rejection if the contract cannot be verified. The modifier is not a trusted assertion. |
| `mandapa` in a marked function | Lexical lifetime within the already-checked function; enter/exit its region on supported targets. Only checked storage operations are available. |
| `mandapa` in unmarked legacy code | Existing behavior, including partial diagnostics. Not a checked island. A teaching profile must require a checked entry and refuse a reachable legacy body, rather than silently downgrading it. |

**The checker's minimum contract.** Begin with numeric scalars and compiler-created bounded numeric buffers. A scalar, even one whose bits equal an address, cannot be used as storage. Reject raw casts, integer-as-address indexing, inline assembly, unchecked memory intrinsics, unknown calls and pointer-bearing legacy containers throughout a checked function. Unsupported operations are compile errors, not operations omitted from analysis. A bounded view must retain its object identity, extent, access rights and lifetime; an R148 vector handle must validate its live slot/generation/owner before it touches payload. An unsupported target must not certify a weaker implementation under the same name.

**Enforcement, including separate compilation.** Resolve declarations first. Check actual bodies and call sites against typed interfaces; track view origins through assignments, returns, global stores, error results and branches/loops. For the minimal subset, views are non-retaining borrows and callable results are numeric; reject any unproved escape. Verify mutually recursive groups as groups: an edge from any member to an unverified body invalidates checked callers upstream. Unknown indirect targets, callbacks, FFI and stale object summaries are rejected in v1. Either recheck imported source in the same build or require a compiler-produced interface tied to the actual code/object hash, ABI, target and checker version; a handwritten external annotation is insufficient. Generate no executable from a failed check. Use the same verdict in diagnostic-only and normal build modes. Keep this distinct from today's `--check` syntax/diagnostic route.

### 2. A library call can allocate without violating safety; allocation ownership is still lexical

The live [`lib/mala.smlib`](../lib/mala.smlib) has a useful real example: `mala_nava(n)` bounds `n` before calculating `n * 8`, then returns `nirmmita(sz)`. Its header explicitly makes the caller responsible for length. Consider this **illustrative legacy call site**, not a native result from this review:

```sutram
yoj mala
mukhya() {
    mandapa {
        vitti local = nirmmita(16)
        vitti other = mala_nava(2)
    }
}
```

On the supported Linux scratch path, `local` was allocated in the caller’s block; `other` was allocated lexically inside the unmarked helper, not in the caller’s `mandapa`. The caller’s rewind does not reclaim `other`. Repeating this pattern can grow persistent storage despite the block. **This is a lifetime/retention mismatch if the caller assumed bulk reclamation, not by itself a dangling pointer.** Under the proposed checked profile the call is refused: it invokes an unverified raw-pointer factory. It is not refused simply because it allocates.

A checked alternative can receive numbers, open its **own** `mandapa`, allocate two checked numeric cells there, read them in bounds, and return their sum **by value**. The callee rewinds its own region and leaves the caller’s region intact. A second alternative is a caller-owned, bounded output view lent to a verified non-retaining helper; the helper fills it without returning its address. Neither requires a dynamically inherited allocator. Defer checked persistent-allocating helpers returning owning objects until the interface expresses and enforces that ownership. Do not accidentally promise that every checked call has bounded memory use: memory safety, allocation lifetime and resource budgets are different properties.

A real comparison supports the distinction: Claude’s R76 report measured a million `roop_ank` calls at 171,904 KB peak as shipped versus 264 KB with the *callee body* wrapped in an experimental patch; it says the library patch did not land. This is partner evidence about placement on one workload, not a general performance promise or a mandate to migrate that function.

### 3. Unchecked callers: a raw `(address, length)` is not a validated buffer

A caller can pass the address of a 10-byte allocation and claim ten qwords. A callee that checks only `0 <= i < caller_count` would allow `i=9`, which accesses byte offsets `[72,80)`. Even `i=1` accesses `[8,16)` and does not fit. For logical byte extent `n`, element width `w>0`, require **`n >= w`, `i >= 0`, and `i <= (n-w)/w` using integer division** before access. Check count × width before multiplication; physical alignment or allocator padding does not enlarge the logical extent. A trusted extent still does not establish that an address is live. Do not recover a length by reading a putative header at `p-8` for an arbitrary interior pointer.

**Entry rule:** legacy source may call a checked scalar interface with plain scalar values. A scalar cannot become a pointer in the callee. For storage, accept only a compiler-issued bounded view or opaque handle from an approved construction path; check origin, bounds, kind, lifetime and mutability. Reject a raw pointer even when paired with a plausible size, non-null address or matching alignment. In v1 there is no unrestricted raw-to-checked bridge. A later adapter may copy from a resource whose validity is independently known (for example an owned I/O buffer with a trusted byte count); copying from an arbitrary address is itself an unsafe read. No anonymous foreign binary may enter a checked storage ABI on trust. Validate before touching user payload or emitting output effects.

**Threat boundary:** this protects against mistakes in the *accepted language subset*, not arbitrary untrusted machine code in the same address space. An unchecked out-of-bounds write can damage descriptor tables before the call. A checked entry reached after such corruption cannot make the process safe again. For a whole-program teaching guarantee, start at the marked entry and enforce the closed set of allowed code, including initializers, imported objects and callbacks. Arbitrary native plugins require isolation or a separately named trusted interface. Validating a generation is not authentication against hostile code.

### 4. Checked caller to unchecked callee: REFUSE, even with scalar-only arguments

| Caller → callee | Decision | Why |
|---|---|---|
| Checked → verified checked definition / approved builtin | Allow only matching argument kinds, lifetime and effects. | A checked read returning a number is useful; a borrowed reference cannot be retained. |
| Checked → unmarked definition | **Refuse.** No warning-only escape, including calls with no reference arguments. | The callee can mutate shared globals or corrupt memory without receiving the caller's buffer explicitly. |
| Checked → unknown indirect, external or unchecked callback | **Refuse** in the first version, including through a marked wrapper. | A safe-looking signature is not evidence about an unknown body. |
| Legacy → checked | Allow scalar-by-value; storage only through the validated entry contract above. | Do not reinterpret a raw address as a bounded capability. Mixed programs do not acquire a whole-program certificate. |
| Legacy → legacy | Existing behavior. Optional migration warnings. | Useful migration feedback is not a safety guarantee. |

The rejection should identify the call site, callee, and reason, e.g. proposed machine-readable `E_UNCHECKED_CALL`, with an owner-reviewed Sanskrit explanation and a practical remedy. Report a short call chain for transitive failures. An approved compiler primitive is a small explicit trust base with reviewed lowering and tests, not permission to whitelist the standard library wholesale. Direct-call classification need add no runtime branch; checked buffer operations and cross-boundary handle validation can require runtime work. No timing is claimed.

**Decisive pair:** `yoga(buf,n)` returning a numeric sum may be admitted once its body, extent and non-retention are verified. An identity helper `adr(buf)` returning the address cannot be silently treated as a number. The R75 transcript records `kosh_push(k, adr(buf))` compiling and then reading `99` written by a later block; the direct insertion was refused. For a checked release, invert the former fixture's verdict: reject the call or forbidden store before it can retain a reference. Do not invalidate Sarvam’s separate result that the direct `box[0]=nirmmita(64)` laundering attempt was already refused.

## WS3 · v1 release decision at the pinned head

**Verdict: no-go for an unqualified checked-memory or cross-platform classroom release.** A limited Linux preview can describe measured reuse and partial diagnostics. The owner’s v1 definition also requires a correct procedural core, usable library, native Windows installation/execution and Sanskrit diagnostics. Shipping an optional checked vector is not a prerequisite for a clearly scoped scalar feature. An accepted design is not a release artifact.

| What must be true | Status on the evidence reviewed | Evidence needed to mark the gate passed |
|---|---|---|
| The core parses and executes the supported teaching grammar as specified. | **Partial.** Existing parser regressions and expected outputs are valuable; a full independent source-to-body/meaning gate and exact classroom corpus were not established here. | Run each lesson and adversarial structural counterpart on the pinned packaged compiler. Use independent intended outcomes, refusals and timeouts. |
| Linux scratch allocations and supported exits respect lexical lifetimes. | **Demonstrated on specific partner fixtures**, not all programs/targets. R74 reports reuse, recursion, and ordinary/`prasar` cleanup. PE and guard mode do not test production Linux reclamation. | Repeat composed exit/alias tests on the exact release binary; state the target/mode. Do not promise pages return to the OS on rewind. |
| A checked caller cannot reach unchecked operations or import an unvalidated address. | **Open.** R148 is a design; R75’s helper-return route is a concrete counterexample for current checks. | Implement and exercise the declaration/call contract, transitive and mixed calls, no casts, and pre-access failures. Enable only after the tests distinguish an intentionally broken checker. |
| Every admitted checked memory read/write fits the requested live object, including computed allocation sizes. | **Open.** v273 handles constant-negative cases and stops on computed negatives in production Linux scratch; the cited ordinary/Windows computed-negative path instead returns zero. Raw byte/qword bounds and positive wrap are separate. R78 asks for a fix; a brief or prototype is not a landed default repair. | Accept `n=10,i=0`, refuse/trap qword `i=1,9,-1`; also test 0/7/8/15/16 bytes, dynamic indices/counts, interior views, positive-to-positive multiplication wrap and an unchanged neighbor canary. Do not present a literal-only fix as general bounds checking. |
| Library behavior has independent expectations and the two identified allocation-size mutants are detected. | **Partial.** Muse’s specific cohort: 12 killed, 1 obsolete, 2 survive. `suchi_srij` and `avali_srij` each change `c*8` to `c+8`. This is not a count of all defects or every mutant across other campaigns. Shipped Madhava agreed at six printed decimals at Muse's 16 sweep points; no shipped sign defect established there. Claude separately reports real `kuttaka`/`meru` repairs. | For each survivor separately, exercise a small constructor at `c=8`: expect a 64-byte **backing** request, not 16. Log the actual request before rounding in a test allocator (distinguish header allocation), or fill/drain eight distinct cells with guard/canary protection. Require baseline pass and each independently built mutant fail. A plain fill/read-back on accessible padding may falsely pass; do not rely on whether the host grants gigabytes. |
| Evidence applies to the release candidate and propagates failures. | **Partial.** Claude R76 reports suite PASS=240 with four no-expectation cases, library 227/227, property 86/86, corpus 227/0, gates 52 pass/0 fail/1 not run. These are partner results; the single not-run is not a pass. | Pin source, packaged binary, target and settings. Reconcile cases/skips. Calibrate the harness by removing a required case and disabling one boundary check; the aggregate must fail. Do not read diagnostic allocator results as production allocator qualification. |
| Native Windows per-user installation, run and uninstall work on the shipped package; capability differences are visible. | **Not established for this candidate.** Package-level integration is still unverified in the installation guide; Wine and valid PE files do not close this gate. | On clean native Windows as a standard user, install/launch, compile and run a Sanskrit lesson, trigger a real diagnostic, uninstall without damaging user files. Test or explicitly refuse the checked feature on unsupported targets. |
| Sanskrit diagnostics and teaching materials describe what happens on that target. | **Partial.** Selected escape and size diagnostics exist. The English design pseudocode and proposed marker are not approved interface text. | Owner reviews syntax/diagnostics and the reference. Run positive and negative examples under the final binary. Distinguish compiler rejection, runtime diagnostic, null result, and accepted manual behavior. |

**What would change my release decision?** First enforce the scalar-only boundary, or explicitly exclude the unsafe feature from the stable teaching surface. Retain independent coverage for both constructor sizes, close or restrict all admitted bounds cases, and qualify the actual supported packages. R79’s two real programs can add useful evidence of utility, friction and memory use. Their assignment is not a performance result, nor would a speedup waive safety or installation requirements.

### Small acceptance matrix for the boundary owner (specified, not run)

| Scenario | Required result |
|---|---|
| Marked root → checked scalar helper → checked leaf; mutually recursive pure pair | Accept after checking all bodies. A source marker alone never counts as proof. |
| Same chain with one unmarked leaf, missing import, stale object summary or unverified indirect target | Reject before code emission; diagnostic identifies the first bad edge. |
| Numeric load copied out versus address copied out; forged/stale handle versus new handle at the same slot/address | Allow the verified value/new handle; reject the address or stop before payload access for the stale handle. |
| Legacy caller provides a good-looking raw `(p,10)` to a checked reader; caller provides the integer `p` to a scalar-only identity function | Reject storage use; accept arithmetic-only scalar use without granting dereference rights. |
| Caller holds numeric scratch across a checked helper that uses its own scratch and returns a scalar | Parent contents intact; child's frontier restored after normal and failure return. |
| Callee allocates persistent storage or secretly captures scratch through a global without returning a pointer | Reject unverified call/effect; do not infer purity from a scalar return or from the caller's block. |
| Same source in production Linux, diagnostic build, unsupported teaching target | Report the path actually exercised. No silent fallback presented as identical lifetime behavior. |

### Provenance and performed work

Repository paths refer to the pinned head. Read the [incoming R149 brief](../Sarvam-to-ChatGPT/ROUND-149.md), the [prior R148 design](ROUND-148-REGION-VECTORS-AND-RELEASE-BOUNDARY.md), [`lib/mala.smlib`](../lib/mala.smlib), [`src/sutram_compiler.asm`](../src/sutram_compiler.asm) (v273 identity), [R75's call transcript](../Claude-to-Sarvam/evidence-r75/ws3-kosh-routes.txt), [Muse's R76 audit](../Muse-to-Sarvam/ROUND-76-MUTANTS-AND-MADHAVA.md), Claude R76 commit `bc171e6088784b2c2fd24dd7f8560128203fb708`, [R78](../Sarvam-to-Claude/ROUND-78.md), [R79](../Sarvam-to-Claude/ROUND-79.md), [language priority](../LANGUAGE-PRIORITY.md) and [installation routes](../docs/INSTALLATION-ROUTES.md). The older v258 `WHATS-LEFT` count is historical, not stronger evidence than the named v273 audit. R75/R76, Muse and Sarvam native results are attributed, not rerun.

External analogy only: the [Rust Reference](https://doc.rust-lang.org/reference/unsafe-keyword.html) separates extra caller obligations from assertions inside unsafe code; the [`from_raw_parts` contract](https://doc.rust-lang.org/std/slice/fn.from_raw_parts.html) illustrates why a pointer plus a length is not proof of a valid allocation. The proposed Sutram design intentionally has no local unsafe escape hatch in checked v1. Rust is not a dependency or evidence for Sutram.

Local design checks only: an independent Python arithmetic model compared the qword predicate with mathematical containment on 1,296 `(n,i)` pairs (`n=0..80`, `i=-2..13`), with no disagreement. A small graph model accepted a closed recursive component and rejected its callers after adding an edge to a raw function. Models, not compiler tests. **NOT RUN — no native toolchain invoked:** Sutram builds, runtime witnesses, mutant kills, Windows acceptance and candidate qualification. No scheduler, CI, compiler, tests, packs or canonical docs changed by this review. Return this one Markdown handoff and stop after R149.
