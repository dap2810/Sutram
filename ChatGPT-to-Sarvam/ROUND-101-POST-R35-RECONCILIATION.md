# ROUND-101 — POST-HANDOFF comparison with Claude R35 (separate from the independent WS1)

**Sequence and independence:** ChatGPT read the original R18 test/golden and library/allocator source, executed an independent GNU C `mmap` arithmetic control, and uploaded [WS1](ROUND-101-WS1-INDEPENDENT-R18-REVIEW.md) and the complete [R101 handoff](ROUND-101-HANDOFF.md) **before reading Claude's R35 handback**. On final verification, `Claude-to-Sarvam/R35-00-HANDBACK.md` appeared. This page is the subsequent cross-check, **not** retroactive evidence for the independent reasoning or a claim ChatGPT ran R35 tests.

## Agreement: both errors were identified independently

| Question | ChatGPT WS1 prior finding | Claude R35 later source/test result |
|---|---|---|
| Why original `3037000499` failed on some machines | `3037000499 * 8 = 24296003992` is valid signed 64-bit; mmap may legally return an address or failure depending on VM policy; unconditional golden 0 is invalid | **AGREES**. R35 confirms the test author mistakenly reused `sqrt(INT64_MAX)`, the *square* overflow edge, for a multiplication by **8** |
| Is `sz < 0` a complete overflow guard? | **NO**. `c=2^61+1` wraps byte size to **+8**, so a tiny allocation can produce an enormous-capacity handle | **AGREES and NATIVE REPRODUCED**. Old library returned a handle and list `SIGSEGV` on second push; new version returns 0 |
| Correct fix | Precheck `c > INT64_MAX/8` before multiplication, plus deterministic overflow fixtures | **AGREES and IMPLEMENTED** for the constructors; separate tests replacing invalid fixture, no arbitrary `--record` |
| Environment requirement | Checked arithmetic must behave identically independent of VM reservation rules | **AGREES**. Reported 221/221 library proofs under both 4 GiB and unlimited address space |

## Actual R35 implementation and test status (CLAUDE'S reports, not fresh ChatGPT execution)

- **Code landed on main**: Claude says implementation commit `46540309` and `R35-00-HANDBACK.md` Git blob `81d9dc9942f84acc23cc12433f6a555ec2fa9d43`. Compiler **v244 unchanged**; the standard library and approved test/golden files changed intentionally.
- The current `lib/suchi.smlib` Git blob **`0904406e1d55f876f27f5084b390fdd7a4b1bb71`** includes `yadi (c > 1152921504606846975) { prati 0 }` BEFORE multiplication in `suchi_srij` (also `avali_srij`); the first original test input has been replaced by `2305843009213693953`. The test now checks deterministic positive/negative wrapping and a small successful allocation.
- Claude also fixed additional constructors **`mala_nava` and `nighantu_srij`**. The dictionary has a different bound: `16 + 56c`, so precheck **`c > floor((INT64_MAX-16)/56)`**. Claude native check found `nighantu_srij(988218432520154552)` previously SIGSEGVed while initializing itself, now returns 0. This extends R101 WS1 rather than contradicting it.
- Prior executed by Claude: `tools/gates.sh` **32 PASS / 0 FAIL / 1 Windows NOT_RUN**, standard-library proofs **221/221** under **both** address-space regimes, suite **218 PASS / 0 FAIL**, crash corpus 227 + manifest/0 failed; both new guard tests deliberately fail under the old code, pass under new; Wine examples matched. No native Windows run of the changed library was claimed.
- The ordinary **compiler** does not change, but **39 library-using binaries intentionally differ** because their included library code now has the guard; report those as approved library behavior changes rather than calling them a compiler byte-identity regression. Claude reports 432 identical, 92 refused identically, 39 expected differences, 1 new test in its 564-program comparison.

## One independent follow-up from the source remains open

**Growth routines** were NOT covered by the constructor guard fix as far as source readback shows. In current `lib/suchi.smlib`:
- `suchi_vardh`: `ncap = lst[1] * 2` immediately followed by `nirmmita(ncap * 8)`;
- `avali_pravesh`: `ncap = qu[1] * 2` followed by `nirmmita(ncap * 8)`.

Both lack a verified **before-multiply bound** on old capacity. A robust precondition is `old_cap <= floor(INT64_MAX/16)=576460752303423487`, with error return leaving old state unchanged. **Source-review risk only; no new native growth counterexample reproduced by ChatGPT.** Other library families with growth should be audited independently. Do not take this as reason to revert the successful R35 constructor fix.

**Outcome:** Independent R101 classification **CONFIRMED by native R35 evidence**; owner/Sarvam can treat the deterministic overflow-guard issue as fixed in the current main standard library, while scheduling a separate growth-bounds audit if appropriate. The original R101 evidence remains pinned to the *pre-fix* main SHA `4d25df8901e07a58b1ebf3a869f5638ac13ac512`. This reconciliation is additional read-only documentation; no production files or existing R35 tests were edited by ChatGPT.
