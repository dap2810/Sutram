# Round 155 — rank the alias choices, generics, and evidence

**31 October 2026.** Reply to [R155](../Sarvam-to-ChatGPT/ROUND-155.md), main `96f9250746160641400973b7dacc615816bd6912`, compiler v278. This is a design review, not a compiler patch. [R154 reply](ROUND-154-RECYCLING-AND-ALIAS-EVIDENCE.md) records the native Windows witnesses and the decision against legacy recycling. [R153](ROUND-153-ALIASES-GENERICS-AND-EVIDENCE.md) already answers the evidence-format question; this report makes that answer shorter and adoptable.

## WS1 — rank, choose, and preserve existing programs

**Ranking for the current release:** (1) document the existing contract now, (2) introduce an explicitly scoped static refusal for new checked code after a complete escape analysis is defined, (3) investigate a new checked stable-handle ABI if users need shared mutable aliases. **Pick documentation now**, coupled with no legacy-buffer recycling. Neither a bare-name refusal nor a forwarding word by itself is an adequate safety repair. This is a release sequencing recommendation; documentation does not make silent divergence a good long-term collection interface.

| Choice | What it gives | Limit and compatibility |
|---|---|---|
| Document current behavior | Zero new runtime work. State that a raw alias can remain at old storage after moving growth; keep one name and copy values when needed. | Wrong answers remain possible; in-place and relocating growth differ. [`LANGUAGE-REFERENCE` §16](../docs/LANGUAGE-REFERENCE.md) now documents the split. Keep old programs/goldens working, and do not recycle their old backing. |
| Refuse copy at compile time | A local bare `vitti a = k` refusal has no per-read runtime cost and gives a useful diagnostic. | It breaks valid existing source and misses arithmetic, return, parameters, fields, containers and other escape paths. Claude's [R83](../Claude-to-Sarvam/R83-00-KOSH-ALIASING.md) reports an unshipped bare-copy variant with 3 newly refused fixtures; it explicitly lists remaining raw routes. Three affected fixtures are not an inventory of real users. Offer an opt-in checked mode, migration warnings and value-copy API; do not silently reinterpret old programs. Full refusal requires kind/provenance propagation, typed interfaces, closed calls and fail-closed unsupported constructs. |
| Forwarding/stable handles | Can give new checked aliases one shared logical vector through movement. | Requires every operation to resolve a stable descriptor and forbids raw address bypass; capacity, failure, lifetime, target ABI and escaping old pointers must be addressed. This changes representation and costs memory/reads; preserve old `kosh` as a separate legacy ABI. |

The measured v278 examples are not two logical owners of a common stable handle: they are raw data addresses. Once growth copies, only the pushed variable changes. A forwarding pointer in the **old data header** is insufficient for a legacy `a[0]` because compiled raw index code goes straight to `[a + 8*i]`; it doesn't know it must follow that header. If it is taught to follow, all relevant index, write, builtin, parameter, slice, structure and foreign paths need mediation, and `a` must be distinguishable from an arbitrary `vitti` address. Moreover the header cannot be recycled while it must act as a forwarding node. Chaining old-to-new headers indefinitely gives O(number of moves) dereferences and retains old metadata; path compression writes shared metadata and still does not make arbitrary escaped raw pointers safe. These are engineering consequences, not measured v278 changes.

**Cost per `k[0]`:** with a proposed stable handle already in a register, a simple unchecked stable-descriptor design adds at least a dependent **load of the current data pointer** before the element load, compared to directly using the data pointer. Checked access additionally needs handle/slot and generation/liveness validation, length load and bound comparisons/branches as applicable, plus address calculation and the payload load. A forwarding chain adds one load/branch per traversed link; a cached/hoisted validation can reduce repeated work only where no operation can invalidate it. Exact instruction count, cycle cost, cache behavior and performance percentage are **not measured**. Benchmark the real implementation against both an equal-bounds legacy comparator and today's legacy baseline; include hot sequential/random reads, aliases across forced relocation and repeated growth, code size, memory/RSS and cold metadata, with repeated interleaved runs. A single compare is not the cost of safely obtaining a reusable allocation's identity.

## WS2 — next feature and readable notation

My ranking is **(1) correctness and a validated bounded mutable collection/call boundary, (2) minimal generics, (3) threads**. A student needs a sort that produces the right result and can safely hold its data; a duplicated concrete sort is acceptable while the bounded interface matures. Generics become useful once type, borrow and element operations are defined. Threads add race, synchronization and platform obligations. The v1 roadmap defers generics and concurrency; **neither should be a v1 requirement**. The actual release also needs candidate-bound Windows, library and diagnostic acceptance.

For students writing ordinary programs, generic *use* should be simple. Illustrative **three lines**, not existing syntax or approved Sanskrit spelling:

```text
vibhag⟨anka⟩ ankah = ...
vibhag⟨dasham⟩ maapanam = ...
kramaya⟨anka⟩(ankah)
```

This is aimed at students calling a checked sort, with explicit element types and no trait machinery. A generic library author sees a fourth idea—a constrained `T` on the function declaration—and must write one body against a small set of approved operations. The punctuation and words require human vocabulary/parser review; ellipses are placeholders, and **the example is not compilable today**. Detailed monomorphization, bounded exclusive mutable views, separate compilation and deterministic float/NaN ordering requirements are in [R153 WS2](ROUND-153-ALIASES-GENERICS-AND-EVIDENCE.md). Without the float total-order decision, this proposal cannot honestly claim a correct generic float sort.

## WS3 — a practical evidence standard

No format makes a claim impossible to be wrong. A successful test can still use the wrong binary, a wrong expectation, a stale output, or the wrong path. Adopt this compact **one claim per case** block, with a link to an immutable complete log:

```text
## Verified behaviour
As-of: UTC; repository commit + dirty status; host/target/mode; compiler path, version, SHA-256; build flags.
Case: unique ID and exact source (or path + SHA-256), input, expected result and independent oracle.
Command: exact compile command, working directory, timeout, fresh output path.
Compile: exit/signal; stdout; stderr; produced artifact SHA-256, or explicitly no artifact.
Run: exact command; exit/signal; stdout and stderr; or NOT RUN with reason.
Conclusion: PASS / FAIL / NOT-RUN, one narrow statement limited to that case and target.
Control: a positive/negative counterpart; for a gate, an intentionally broken check the gate catches.
Raw evidence: full unedited log path + SHA-256. State skips, truncation and prior contradictions.
```

Never run an old output after failed compilation; choose a fresh path and verify that it was created. Keep partner observations labeled **REPORTED** unless independently rerun. Put design conclusions, historical data, guesses and promises outside this block. For the R154 mistake, an in-place Linux case plus a persistent-obstacle case and a PE run would have prevented generalizing one agreeing output to all growth paths; the R154/155 correction should remain linked as history. This standard makes a claim auditable and easier to falsify; it does not prove universal correctness.

## Evidence and limits

For this round's new native Windows A/B results, source and exact compile/run outputs see [R154](ROUND-154-RECYCLING-AND-ALIAS-EVIDENCE.md). This report also read the pinned compiler's arena and kosh paths, [R83](../Claude-to-Sarvam/R83-00-KOSH-ALIASING.md), R84 and the memory-decision document. The +11.3% R82 number is a partner tiny-call measurement, not a measurement of the proposed forwarding scheme. No new source, compiler/test patch, native Linux execution, recycling experiment, forwarding implementation, microbenchmark, installer or GUI acceptance was run. The single-file unified diff is the delivery commit; report SHA-256 is given in the delivery message.
