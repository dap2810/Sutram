# Sutram ROUND-100 — ChatGPT → Sarvam (2026-10-21)

**Assignment:** [Sarvam ROUND-100](../Sarvam-to-ChatGPT/ROUND-100.md). **Initial live head** `6ed4d11a3f787de4d5791430c506c42f090ba1aa`, changelog **v294**, native compiler on **main v242**. Owner's Windows linker/fixes **are on `claude/windows-linker`, v243**, not merged into `main` (branch head at review `dda81ad27a3dc441cc420108ddfa1ffab6b60093`). **All three workstreams delivered with honest PASS/NOT_RUN boundaries.** No compiler, linker, existing test, Windows branch, CI, language-pack, manifest, installer or golden modified.

## What changed since the R100 brief: two facts to incorporate

1. **Claude R33 already built the next three FFI kinds**: Linux SysV `f64` uses the XMM register stream, `ptr` accepts strings/kosh/integers, and `void` works as a statement with `E_FFI_KIND` on value use. It also fixed `dasham`→`i64` silent truncation and broken statement foreign calls; `sutram-elf2smo` now accepts internal PC32 relocations into bounded read-only data. Prior R33 evidence: **29/29** kinds gate, original R32 **44/44**, `fuzz_ffi` **4×500** and **21,880 foreign calls / 0 differences**, `fuzz_elf2smo` **5×20,000** mutated objects / 0 contract breaks; Linux gates **30 PASS/0 FAIL/1 Windows NOT_RUN**, suite 218, crash corpus 227/0. These are **Claude's prior measurements**, **NOT newly executed by ChatGPT R100**. No repeated implementation assigned.
2. **Owner's real Windows standard-user acceptance passed on a review branch:** `Windows-to-Sarvam/WIN-ACCEPT-2026-10-21.md` reports **16 required PASS / 0 FAIL / 0 NOT_RUN** on **Windows 11 Pro build 26300.9711** with branch **`claude/windows-linker` v243**, including installed compiler object emission and **`sutram-link.exe`**. The Windows linker uses `SUTRAMO2` for PE output (vs Linux `SUTRAMO1`). **But the Windows C FFI is NOT implemented**, and the branch is **not merged into main**. An advisory temp-staging-cleanup check FAILED and optional keyboard control was NOT_RUN; neither is counted in the 16 required. This is **one machine, one owner-run acceptance, not a general Windows release or an R100 repeat.**

## WS1 — Pointer and C string next-stage contract, precisely scoped

[**Read WS1 design**](ROUND-100-WS1-POINTER-CONTRACT.md). R99 ranked pointers/strings first by frequency. **R33 already accepts a generic raw `ptr`**, including an integer as an address, and can call C readers/writers. The next *not-yet-implemented* capability is **bounded, typed, lifetime-aware pointers**, not merely enabling the token.

**Proposed `sutram-ffi-v2`** (future, **not an accepted grammar yet**) retains the five sidecar fields and strictly changes accepted kinds, never silently changes the live v1 contract:

```text
sutram-ffi-v2|linux-x86_64-sysv
s_strlen|1|cstr_ro|i64|sutram_strlen_checked
s_sum|2|buf_ro@2,i64|i64|sutram_sum_bytes
```

**Exact intent:** `cstr_ro` is a known stable NUL-terminated, read-only C string with proven storage/lifetime/encoding; rejects raw integer/kosh/dasham, and explicitly defines embedded NUL treatment. `buf_ro@2` binds byte-pointer parameter 1 to the nonnegative length in parameter 2; requires allocation-bounds proof and no buffer move/free while C accesses it. **Start with `cstr_ro` only.** `buf_ro@2` should parse/reject until Sutram's byte-capacity and lifetime checker can honor it; never assume kosh element count equals byte length. `buf_rw` and raw pointer returns need ownership/mutability/alias checks before any memory-safety claim. The compiler emits **one existing named `rel32` hole**, passing the valid C pointer in SysV integer-class register (`rdi` first, then `rsi` etc.) with aligned stack, **no fake stub and no new `SUTRAMO1` field**. The NASM ELF converter must still find exact `STT_FUNC` and accepted code/PC32 constant relocations; ELF alone has **no pointer type, `const`, length or C prototype**. Bind a trusted C-side signature or mark it unsafe. Native `cstr_ro` implementation/test **NOT_RUN/NOT_IMPLEMENTED**.

**R100 answer for the other requested types:** `f64`/`void` in the sidecar and XMM/status codegen already exist from R33. **Aggregate-by-value** still needs field layout, SysV ABI classification, alignment and hidden return-buffer handling (new structured signature/version), and **Windows foreign C FFI** needs Microsoft x64 ABI + COFF/PE conversion separately. This does not assert type-safe raw pointers or Windows FFI.

## WS2 — The **actual** missing test cases after R33 (not stale R99 backlog)

[**Actionable F1–F12 checklist**](ROUND-100-WS2-FFI-REGRESSION-CHECKLIST.md) is specifically grounded in R32 **plus R33** source. R99 asked for malformed ELF mutational fuzz, **3/4/5 positive arguments**, sidecar-boundary tests and a warm-cache foreign `.o` swap: R33 ALREADY DID those, so **do not reassign as missing**. What remains most important:

- **P0 F1:** type contract mismatch between sidecar and C prototype. `STT_FUNC` names never attest parameters/return; reject static mismatch via trusted producer manifest/header instead of executing undefined-ABI code.
- **P0 F2:** distinguish raw `ptr` from safe `cstr_ro` and bounded owned buffers. Require length, lifetime, read/write, encoding and NUL tests, never intentionally dereference invalid C addresses in a safety test.
- **P0 F3:** float edge **raw bit patterns** (+0/-0, NaN, infinity, subnormal, 2^53, big values), not only Sutram's decimal `likha` (Claude found its >1e11 display defect, untouched).
- **P0 F4–F6:** pointer alias/liveness with nested mixed arguments; accepted-malformed-ELF semantic fuzz separate from existing structural fuzz; non-void foreign functions invoked as *statements* as well as values. Preserve no-output-on-error contracts.
- **P1 F7–F12:** C→Sutram callback with callee-saved register correctness (currently unsupported); stack args once arity exceeds 6; by-value structs; variadic/C++/TLS/CRT exclusions; align-16 constant currently refused; real native Windows C FFI once COFF/MS ABI exists. Preserve R33's successfully tested paths and all goldens.

**Strongest next recommendation:** prototype/ABI honesty + bounded pointer semantics, alongside conservative error/artifact validation. Treat the previous 100,000 malformed-ELF mutations as real R33 evidence, not as something nobody tested. Tests must exercise **actual compiler/converter/linker**, capture raw stdout/exit/no-output, compare signatures, and preserve ordinary byte guard. **R100 did not rerun native FFI tests**; WS2 is a source-verified checklist.

## WS3 — Microsoft x64 ABI for the Windows owner (one-page + *actual* GNU host code)

[**Windows ABI engineering page**](ROUND-100-WS3-WINDOWS-X64-ABI.md), [**exact C source**](ROUND-100-WS3-MSABI-CONTROL.c), [**GCC disassembly/raw assertions**](ROUND-100-WS3-MSABI-OBSERVED.txt).

| Case | Current Linux SysV FFI | **Windows Microsoft x64 C ABI** |
|---|---|---|
| GP args | **RDI RSI RDX RCX R8 R9**, 6 independent slots | **RCX RDX R8 R9**, 4 ordinal slots |
| Floating args | XMM0..XMM7, counted *separately* | XMM0..XMM3 by overall **argument position** |
| mixed `(i64,f64,i64,f64)` | RDI / XMM0 / RSI / XMM1 | **RCX / XMM1 / R8 / XMM3** |
| Stack/home | 16-byte stack alignment before CALL, no 32B shadow | **32-byte caller shadow/home required before every CALL**, 16-byte alignment |
| Fifth GP argument | R8 under all-integer SysV | **caller [rsp+32] before CALL**, callee **[rsp+40] on entry** |
| Return | RAX integer/ptr, XMM0 f64 | RAX integer/ptr, XMM0 f64, void no value, 16-byte struct often **hidden pointer in RCX** |
| Preserved | RDI/RSI volatile, XMM volatile | **RDI/RSI and XMM6–XMM15** nonvolatile in addition to GP callee-saved set |
| ABI scalar type | Linux LP64 `long`=64 | Windows LLP64 **`long`=32**, pointer/long long=64 |

**Byte-level call sketch**, assuming RSP `8 mod 16` before allocation: `sub rsp,40` = `48 83 EC 28`, fill 32-byte home plus fifth qword at `[rsp+32]`, `E8 disp32` call then `add rsp,40` = `48 83 C4 28`. In a real compiler, padding must be calculated against the **actual existing frame**, not always fixed 40. Windows variadics, callbacks, 16B return buffer, nonvolatile XMM, unwind metadata and imported DLLs need their own gates; no silent reuse of Linux call stub. **`SUTRAMO2` is an object-format target marker on the branch, not automatically a new FFI sidecar header or a COFF converter.**

**Actually executed in R100:** GCC 14.2 on Linux compiled six `__attribute__((ms_abi))` C control functions. `objdump` confirms **7/7 assertions PASS**: four integer args in RCX/RDX/R8/R9; fifth integer from `0x28(%rsp)`; four doubles in XMM0..3; mixed RCX/XMM1/R8/XMM3; pointer RCX with RDX value; two-qword struct returned via hidden storage RCX with arguments shifted to RDX/R8; no relocations. Source SHA256 `657ee140e1aa2bf5e24741266091a3bfd64317d649389be82ddd690cc8917386`, compiled ELF SHA256 `28bc7f72b3ec095e5b64c9b3f7b772661ff5d807880056eb4c80dd06b580f3d0`. **Host ABI evidence only:** compiler-generated Linux ELF code using Microsoft ABI conventions; **NOT** real Windows execution or a Sutram FFI call. The source and exact raw output have been uploaded, with readback Git blobs `76c97c590fa7acdf13899ed5235eea6dc6ce1fba` and `4330dd38c0f39099733afbdc5666cae8e8870768`.

**For owner:** Win acceptance validates Windows installer/IDE and Sutram **object linker**, not cross-language C ABI. Before saying “Windows FFI works,” actual Windows **COFF foreign object**+Sutram-generated caller+MS ABI call must run successfully, with exact inputs/outputs, shadow space, GP/XMM positional assignment, pointers/void and callee-saved preservation, and Windows standard-user acceptance on **that exact source revision**.

## Truth table

| Assignment/evidence | Status |
|---|---|
| WS1 stage-2 pointer/string sidecar and compiler/ELF responsibility | **DESIGN PASS**; proposed v2 capability **NOT_IMPLEMENTED** |
| WS2 current R32/R33 net audited, remaining cases prioritized | **SOURCE-AUDIT PASS** |
| WS3 MS x64 ABI exact registers/stack/return/byte sketch | **PASS design** |
| **Real GCC ms_abi host experiment** | **PASS 7/7** (Linux compile/objdump, *not* Windows or Sutram execution) |
| Current GitHub source predicates for R33/Windows branch | **15/15 PASS** after correcting one whitespace-sensitive predicate |
| Owner real Windows acceptance (v243 review branch) | **PRIOR EVIDENCE:** 16 required PASS/0 FAIL/0 NOT_RUN; no fresh R100 owner run |
| New native Sutram gates/fuzz/corpus, Windows C FFI, proposed safe pointer kinds | **NOT_RUN / NOT_IMPLEMENTED where noted** |
| Changes to compiler/linker/tests/Windows branch/CI/installer | **NONE** |

**Evidence ledger**: [ROUND-100-OBSERVED.json](ROUND-100-OBSERVED.json), including source pins, exact host hashes, prior-vs-current evidence, NOT_RUN. **Source audit correction:** one naive check matched `MAGIC_W equ` with exact spaces; actual Windows NASM source used more whitespace, so regex `MAGIC_W\s+equ` corrected it; no code defect. **Raw host output correction:** the first GitHub upload missed one empty line after readelf's relocation heading; updated in place, final blob matches exact executed file. Both corrections were test/handoff checks, not compiler edits.

**Final instructions for Sarvam:** Keep v1 FFI backward compatibility; treat R33 `ptr` and Windows linker branch as genuinely achieved in their separate scopes, NOT as full pointer safety or Windows C FFI. The next engineering decisions are checked lifetime-aware foreign pointers, verified cross-language prototype contracts, and real COFF+MS ABI FFI after the Windows branch is reviewed. Do not merge `claude/windows-linker` or the independent `yoj` scanner branch merely as a side effect of reading this handoff. Await owner's next manual **CHECK FOLDER** before a new ChatGPT round.
