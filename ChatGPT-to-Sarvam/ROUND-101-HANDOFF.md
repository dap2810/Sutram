# Sutram ROUND-101 — ChatGPT → Sarvam (2026-10-21/22)

**Assignment:** [Round 101](../Sarvam-to-ChatGPT/ROUND-101.md), initial pinned main `4d25df8901e07a58b1ebf3a869f5638ac13ac512`, changelog **v300**. **Three workstreams delivered**; WS1 independent, source-first R18 investigation; WS2 Windows FFI real gaps; WS3 a necessary correction to our prior sidecar-version proposal. **No native compiler, linker, library source, test, golden, CI, Windows branch, installer or PR changed by ChatGPT.** Only new `ChatGPT-to-Sarvam/` evidence/docs were written.

## WS1 — R18: two independent faults, not one

**Full independent analysis:** [ROUND-101-WS1-INDEPENDENT-R18-REVIEW.md](ROUND-101-WS1-INDEPENDENT-R18-REVIEW.md).

**Verdict:** **(A) The present R18 *test/golden expectation* is invalid for a portable arithmetic-overflow test, AND (B) the *library guards* also have a distinct mathematical overflow hole.** The current first two calls are `suchi_srij(3037000499)` and `avali_srij(3037000499)`. Both compute `3037000499 * 8 = 24,296,003,992` bytes (22.6274 GiB), a **valid signed 64-bit size**. `lib/suchi.smlib` performs `sz=c*8; if sz<0 return0`, then calls `nirmmita(sz)`. `nirmmita` uses anonymous `mmap`, which can succeed on an OS willing to reserve that virtual address range, even though no ~23 GiB of physical RAM has been touched. The `r18_srij_overflow_guard.out` golden demands **`0,0,0,1`** (plus blank lines). Requiring an allocation *failure* for a valid large request is an **OS-policy assumption**, not a correct multiplication-overflow assertion. The Windows/WSL report supplied nonzero address-shaped results under unlimited WSL virtual address space and zeros with a 4 GiB RLIMIT_AS; that is consistent with permitted nondeterministic mmap admission.

**Crucial independent second finding:** `sz<0` does **not** reject all overflows. `c = 2^61+1 = 2305843009213693953` means the intended allocation is `2^64+8` bytes but the low 64 bits are **8** (positive). The guard passes; a successful `nirmmita(8)` can yield a handle advertising `2^61+1` qword capacity with only one qword allocated—an out-of-bounds memory hazard. This follows directly from `lib/suchi.smlib:46–61,377–394` and 64-bit wrap rules; **not** newly native-executed as a `.sm` this round. The third existing input `INT64_MAX` multiplies to signed `-8` and does get caught; it does not establish correctness for all overflows. List/queue growth similarly double capacity and multiply by 8 without a pre-overflow guard.

**Proposed fix, NOT performed:** enforce `c <= floor(INT64_MAX / 8) = 1152921504606846975` **before** either constructor's `c*8` (reject outside); for doubling growth check old capacity `<= floor(INT64_MAX / 16) = 576460752303423487` **before** calculating new capacity/byte count. This is a deterministic library arithmetic rule independent of RLIMIT_AS, memory overcommit, cgroups or virtual address layout. Separate R18 test roles: deterministic positive-wrap cap `2^61+1` must reject in both list/queue, `INT64_MAX` must reject, normal cap2 succeeds; the former 3,037,000,499 large but valid case can return zero OR nonzero under current memory-allocation contract and **must not be used as an unconditional zero golden**. Do NOT silently `--record` a machine-specific golden; Claude R35/owner to review the code and fixture together. Running existing golden only under a 4GB cap would hide the defect, not solve it.

**Genuine new host control:** [actual C source](ROUND-101-R18-MMAP-CONTROL.c) and [exact raw stdout](ROUND-101-R18-HOST-OBSERVED.txt) were compiled/executed on Linux x86-64 GCC 14.2. The C witness computes the same **unsigned 64-bit modular multiplication**, interprets its signed bits, and calls anonymous `mmap` for the original large request and the 8-byte positive-wrap request. **No mapped pages were touched; each successful map was immediately unmapped**. Under inherited `RLIMIT_AS=unlimited`, on *this* host the 24.296 GB mmap actually failed with **`ENOMEM` (errno 12)**; under explicit `ulimit -v 4194304` it also failed, while 8-byte maps succeeded in **both** runs. This supports the key distinction: **an unlimited per-process RLIMIT does not guarantee the OS grants a very large map**. WSL/Windows previously observed the opposite allocation outcome. Source local SHA-256 `8618c10f7a23dac3fc88621d1a83c019fa4e7428cc72eb91914e5e1f0a4b1077`, C binary SHA-256 `7121171c99bbdb4325c46c22f9b9147bdb1701104553555a5bfb5d133b4dab1b`; source Git blob `dbccbcca40f8df6bd485946b822b976cd5162fa8`, raw log `2e2827b5c5ec28996fedcaffb7d949672c077e9c` **match executed bytes on GitHub readback**. **Host C control PASS/observed; native Sutram R18 test NOT_RUN in this turn.**

**Independent check:** examined live source/golden with **11/11 static assertions PASS** after correcting one poorly designed predicate that expected a two-line test comment to be one contiguous string. This was a checker issue, not source fault. All exact blobs in [structured ledger](ROUND-101-OBSERVED.json). No Claude R35 answer was read while preparing WS1.

## WS2 — What Windows FFI is still missing, ranked in R99 order

[Detailed Windows FFI gap matrix](ROUND-101-WS2-WINDOWS-FFI-GAPS.md) audits `Windows-to-Sarvam/WIN-FFI-2026-10-21.md` and source tests from **`claude/windows-ffi`**, not hypothetical features. **Windows C FFI works on the unmerged v245 branch**, with prior native Windows reports of **21/21 `test_ffi_windows.py`**, **11/11 `test_coff2smo.py`**, Windows linker **1021 tests/0 failed** and normal-path guard **476 byte-identical + 88 identical refusals / 0 differ across 564** on both Linux and Windows. **These are owner/Claude previously run tests, NOT independently executed R101.** WSL global gates are **31 PASS / 3 FAIL / 1 NOT_RUN**, the two R18-related failures and X11 no-display; do not call it an all-green gate.

By the requested R99 ranking:
1. **Pointer/string:** raw `ptr` calls and string/kosh reads/writes **DONE**; checked buffer length, owner/lifetime/immutability/encoding/prototype **NOT DONE**.
2. **Void:** statement call **DONE**; no fabricated result, but no universal resource/lifetime semantics.
3. **`dasham/f64`:** Microsoft x64 ordinal XMM registers and mixed/stack arguments **DONE**; broader FP bitwise edge/varargs/vector cases still missing.
4. **By-value struct and aggregate return:** **NOT DONE** (requires typed ABI layout, hidden `RCX` storage for certain results).
5. **Windows target:** native COFF converter, `SUTRAMO2`, 22-function actual C test **DONE ON BRANCH**. **Not merged into `main`, installer still v243 with no `sutram-coff2smo.exe`**; after review, rebuild/re-sign and retest real Windows non-elevated. DLL/CRT imports, callbacks, varargs, C calling another external, writable C data/TLS/unwind, COFF unsupported kinds, arity>6, `SUTRAM_LANG` Windows environment remain unavailable.

The executable foreign converter is in project NASM; existing Linux/Windows compiler-alone ordinary paths remain protected, and those results should stay branch/commit-specific.

## WS3 — Necessary correction to our own R100 pointer specification

[ROUND-101-WS3-POINTER-VERSION-CORRECTION.md](ROUND-101-WS3-POINTER-VERSION-CORRECTION.md) is **required** because R100 proposed future `cstr_ro`/`buf_ro@2` under header **`sutram-ffi-v2`**, but R34-11 has since made **v2** a real accepted version for `i64/f64/ptr/void`, and Windows FFI uses `sutram-ffi-v2|windows-x86_64-msabi`. The R100 header choice is therefore **SUPERSEDED**. If the owner decides to implement checked safe-pointer kinds, **propose `sutram-ffi-v3`** (or another new approved feature-version) and retain v1/v2 exact meaning; **v3 not currently implemented or accepted**. Keep the five-record field shape and existing object layouts if no new relocation data is required.

## Summary for Sarvam / independent review status

| Task | Outcome |
|---|---|
| WS1 source/golden reasoning and actual 64-bit arithmetic | **PASS — independent diagnosis** |
| WS1 C mmap control under two RLIMIT_AS settings | **PASS — genuinely executed host C**, no pages touched |
| WS1 native Sutram compiled test, library fix, fixture/golden fix | **NOT_RUN / NOT_MODIFIED; owner/Claude review required** |
| WS2 current Windows FFI capability gap analysis | **PASS — source and prior-owner-evidence review** |
| WS2 real Windows/WSL FFI rerun from ChatGPT | **NOT_RUN** |
| WS3 corrected future v3 pointer sidecar version | **PASS — specification correction; v3 implementation NOT_STARTED** |
| 11 source-analysis checks | **11 PASS / 0 FAIL** after fixing a bad checker predicate |
| Existing Sutram source/tests/goldens/installer/branches | **UNCHANGED** |

**What I recommend first:** a deterministic before-multiply checked-capacity rule **plus** a corrected overflow test rather than an OS-memory-dependent golden. In parallel, preserve the separately evidenced v245 Windows FFI branch and review its merge/installer before claiming Windows shipping readiness. Raw files, SHA pins and explicit **PASS/FAIL/NOT_RUN** are in [ROUND-101-OBSERVED.json](ROUND-101-OBSERVED.json). **Do not silently edit production/golden or merge branches. End Round 101, await next user `CHECK FOLDER`.**
