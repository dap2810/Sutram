# ROUND-106 WS2 — Verdict on the historical 19 exemptions, and the CURRENT 13

**Review pinned to main `e6914bc598958053817f7c61133d579f1ba19bc2` (v318).** This is not the R105 v310 tree. Direct read of current `tools/check_alloc_bounds.py` (blob `1083706f804271e0943cbda71bbe1cbe210e03ef`), `lib/nighantu.smlib` (blob `4c5f4255ef9cf6caa59acb117f2d545e80767e5c`), `lib/sangrah.smlib` (blob `c0889298884655116f9950d79b6c1190d9098189`), other allocation-bearing library modules, and Claude `R39-00-HANDBACK.md` (blob `110b9bf2838a2b804b72b3a3de2349fe9b94b747`).

## Immediate answer Sarvam needs

**YES: the original 19 included a demonstrably unsound reason. No: those 12 affected sites are not still unfixed.** In R37/R38, the exemption rationale for set/map scratch allocations was “`cap` is the capacity of the set/map, so cannot exceed the constructor bound.” For API callers, `cap`, `bcap`, and `scap` were independently supplied numbers, with no check against the actual handle. **That reason DID NOT survive scrutiny.** A caller passing the wrong cap caused an observable overwrite and silent wrong value, measured by Claude R39.

**Round 39 fixed the class on current main**: allocations now read the *container's own bounded capacity*—`a[0]`, `b[0]`, `s[0]` or `src[0]`—rather than taking the caller's integer as a trusted memory extent. The authoritative gate's `EXEMPT` keys now include the **exact expression** as well as module/function and cannot automatically excuse a new expression in the same function. It reports **26 computed sites: 13 bounded / 13 exempt / 0 failed** on Claude's prior Linux run (not independently executed by ChatGPT).

## Reconcile all old 19 sites in three groups

| Old R105 classes | Old site count | Is original reason sound? | Current v318 disposition |
|---|---:|---|---|
| `nighantu_vardh` — `oldcap=m[0]` and `oldcap*33+1` | **1** | **YES, conditional** on a valid map handle constructed by `nighantu_srij` | **STILL EXEMPT**, with exact expression. Earlier R36 also checks allocation failure and leaves caller state intact on refusal. |
| `nighantu_mil` (1) and `sangrah` set functions (11), which used caller-provided `scap` / `cap` / `bcap` | **12** | **NO, not for arbitrary public calls.** Function input numbers do not prove the metadata or the allocated extent. R39 reproduced data corruption, not merely theoretical wrapping. | **FIXED**: scratch expressions use `src[0]`, `a[0]`, `b[0]` or `s[0]`, and are now exempt only under those exact expressions. |
| `aadhar.brihat_ank_tak` (2), `brihat.brihat_shesh` (1), `brihat.brihat_ghatmod` (2), `shreni.mil_shreni` (1) | **6** | **ONLY a caller-precondition, not a machine-checkable bound.** “The caller's own digit count/array length” never proves arbitrary raw `n` and actual allocation size. | **HARDENED IN R39**: these are no longer `EXEMPT` entries; source now checks upper/lower count bounds. Actual caller-owned pointer extent is still not verifiable, so they are not memory-safe in the general sense. |
| **Historical total** | **19** | **12 rejected outright as trusting caller capacities; 6 conditional/unproved raw extents; 1 conditional under a constructed map** | **Current gate's remaining 13 exemptions are DIFFERENT site expressions and cannot be equated with the old 19.** |

## Exact current 13 source-checked exempt allocation instances

The current checker declares **12 distinct exact-expression keys**, covering **13 call sites** because `rakh_tak_mala` allocates *two* separate pointer/length scratch arrays with `s[0] * 8`.

| Function | Current exact expression(s) and instances | Current justification |
|---|---|---|
| `nighantu_vardh` | `oldcap * 33 + 1` (1) | `oldcap` comes from `m[0]` |
| `nighantu_mil` | `src[0] * 33 + 1` (1) | `src[0]` comes from source map's own header |
| `rakh_samroop_diff` | `a[0] * 33 + 1` and `b[0] * 33 + 1` (2) | both source sets' actual header values |
| `rakh_sangam` | `a[0] * 33 + 1` and `b[0] * 33 + 1` (2) | both source sets' actual header values |
| `rakh_sampat`, `rakh_bhed`, `rakh_asti_upasamuh` | `a[0] * 33 + 1` each (3) | source set's actual header |
| `rakh_tak_mala` | `s[0] * 33 + 1` (1), `s[0] * 32 + 1` (1), `s[0] * 8` (2) | source set's actual header |
| **Total** | **13 site instances, 12 distinct keys** | **All derive from a container field rather than an independent caller count.** |

### Arithmetic proof — sound *under stated preconditions*

`nighantu_srij(cap)` clamps cap >= 1 and checks that its stored capacity is at most `floor((INT64_MAX-16)/56) = 164703072086692424` before allocating the `16+56cap`-byte map. For a map whose `m[0]` truly came from this constructor and has not been corrupted, `33*m[0]+1 <= 5.44e18 < INT64_MAX`, and `32*m[0]+1` and `8*m[0]` are smaller. **Thus none of these 13 exact-size formulas can overflow for a valid, unmodified library-created container.**

**Verdict on the current 13: SOUND AS CONDITIONAL CONTRACT EXEMPTIONS.** They are not evidence that an arbitrary pointer `m` is valid, or that an application cannot modify public header cells with raw memory operations. There is no ownership/memory-safety model or runtime pointer extent metadata to prove that. Likewise output destination size is a separate caller promise; a scratch-size check alone cannot prove it. The gate must say **“exempt by constructor invariant”**, not **“all memory accesses safe.”**

## What changed from the old provenance audit?

- **Closed**: filename/spelling-based R103 review-only allowlist is not the authoritative gate; current R39 checker keys exemptions to exact expressions and rejects new unrelated sites in those functions.
- **Closed**: caller-provided map capacities driving internal scratch allocations (R39 native witness).
- **Closed for specified arithmetic**: former `aadhar`/`brihat`/`shreni` source-count exemptions now have bounded checks.
- **Open by design**: general raw-pointer/header provenance; integer arithmetic checks cannot attest pointer ownership or actual writable buffer capacity.
- **Open in other language area**: owner must decide whether compiler-level typed variables and bounded references provide the type/evidence needed to eliminate the residual raw-pointer promise. Do not request a second duplicate gate in this round.

**Evidence/status:** **PASS — static/current-tree exemption inventory and mathematical proof, versioned partner report cross-check. NOT RUN - no toolchain — native Sutram programs, R39 regression reproduction, full gates, Windows FFI, proof suite.** No code/tests/gate/backup/Windows-channel files changed.
