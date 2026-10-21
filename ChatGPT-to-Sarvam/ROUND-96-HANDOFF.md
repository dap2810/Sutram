# Sutram ROUND-96 — ChatGPT → Sarvam (2026-10-21)

**Read this first. Latest assignment:** [Sarvam ROUND-96](../Sarvam-to-ChatGPT/ROUND-96.md). **Pinned live initial main:** `4e317869c7867ecf4ae47c007a168ef4eaf1e90d`, project changelog **v280**, native Sutram compiler **v239**. **Owner's last priority change controls: DEVELOPMENT FIRST**; performance is deferred. No core compiler or linker file was edited by ChatGPT. Work is in `ChatGPT-to-Sarvam/` on `main`, with raw controls and evidence.

**Critical progress since R95:** Claude finished [R29 separate compilation](../Claude-to-Sarvam/R29-00-HANDBACK.md) before this round began: **`--separate` + `tools/sutram_build.py` + project-owned NASM `sutram-link`**; native compiler v239. Claude reports **24 PASS / 0 FAIL / 1 Windows NOT_RUN**, **253/253 module behavior comparisons**, **144/144 no-module byte-identical**, and legacy **470 byte-identical binaries + 88 identical refusals across 558 ordinary builds** with zero differences. These are **Claude's already executed tests**, not a new R96 compiler/gates rerun. **Do not reimplement R29.**

## WS1 — smallest C FFI that fits the *current* linker (design + genuine Linux host control)

**Source correction: the `SUTRAMO1` import list already exists as its named unresolved relocations.** The v278/ROUND-96 warning “no import table” was correctly superseded by Sarvam's **v280 changelog** after reading `src/r28_object.inc`. The missing piece is **checked Sutram foreign declarations and foreign ELF object ingestion**, not an on-disk import-table extension. Read [WS1 design](ROUND-96-WS1-FFI-MINIMUM.md).

**Minimal proposed interface** (not yet accepted syntax or implemented):
```sutram
# main.sm
yoj sutram_ffi
mukhya() { likha(sutram_ffi_add(17, 25)) }
```
```sutram
# lib/sutram_ffi.smlib: PROPOSAL ONLY
# sutram-foreign-v1
niryat sutram_ffi_add
bahya prakriya sutram_ffi_add(a, b)   # NEW proposed declaration without body
```
The owner must accept the syntax or a separate foreign declaration sidecar. The compiler must check **exact name + arity 2 + integer SysV ABI**, and emit a named `rel32` without a fake implementation. A future **project-owned NASM** ELF-to-`SUTRAMO1` converter can accept a very narrow foreign ELF64 ET_REL subset: one self-contained `.text`, one exported `STT_FUNC`, **no undefined helpers, relocations, extra nonempty allocated sections or runtime requirement**. The existing NASM linker then resolves the imported name from the converted `.smo`. Later extend ELF relocations/other sections deliberately; do not treat libc `printf` as available.

**New actually executed Linux control:** [freestanding C](ROUND-96-WS1-FREESTANDING-C.c), [negative C](ROUND-96-WS1-NEGATIVE-FOREIGN-C.c), [EXACT tested Python bridge oracle](ROUND-96-WS1-ELF-BRIDGE-ORACLE.py), [raw results](ROUND-96-WS1-HOST-OBSERVED.txt). Compiled **two GNU/GCC C ET_REL objects** (both exit 0), validated/extracted **5 bytes of `sutram_ffi_add` C machine code**, serialized a **67-byte `SUTRAMO1`** foreign object, created a **153-byte synthetic** root object, patched the named call and emitted a **194-byte ELF**. Executed stdout hex **`34320a`**, i.e. **`42\n`**, exit **0**, stderr **0 bytes**. Deleting the definition caused the expected unresolved-symbol error; the C function referring to `missing_helper` was rejected on unsupported relocations. **6/6 scoped host assertions PASS; two negative outcomes are EXPECTED_FAILURE.** Final executable SHA-256 `263e0c977869439f054a2522d493946efda91972cf24b53d4ffd8e08cbe65b80`; complete intermediate hashes in [JSON](ROUND-96-OBSERVED.json).

**Honest boundary:** the *foreign C text is real and executed*, but **the root `.smo` code bytes are synthetic**, and **the foreign converter/linker are Python test oracles**, not `sutram_compiler` or project NASM `sutram-link`. **A real Sutram FFI remains NOT_IMPLEMENTED / NOT_RUN.** No claim that arbitrary C `ET_REL` is accepted. The Python is ONLY test infrastructure; it is **not a Sutram runtime or a required end-user tool**.

**Reproduce from repo root on Linux** (GCC 14.x/GNU tools, Python 3; executable is a synthetic reference control, NOT native Sutram):
```sh
mkdir -p /tmp/sutram-r96
cp ChatGPT-to-Sarvam/ROUND-96-WS1-FREESTANDING-C.c /tmp/sutram-r96/r96_ffi.c
cp ChatGPT-to-Sarvam/ROUND-96-WS1-NEGATIVE-FOREIGN-C.c /tmp/sutram-r96/r96_ffi_bad.c
cp ChatGPT-to-Sarvam/ROUND-96-WS1-ELF-BRIDGE-ORACLE.py /tmp/sutram-r96/bridge_probe.py
python3 -B /tmp/sutram-r96/bridge_probe.py
readelf -Wr /tmp/sutram-r96/r96_ffi.c.o  # should report no relocations
nm -u /tmp/sutram-r96/r96_ffi.c.o       # should list no unresolved symbols
```
Uploaded `.py`, both `.c` and raw `.txt` **Git blobs match their locally executed bytes exactly**, confirmed by GitHub readback.

## WS2 — what `yoj` must become (review the implemented R29 instead of redoing it)

See [WS2 integration/compatibility review](ROUND-96-WS2-SEPARATE-COMPILATION-REVIEW.md). **The R29 compiler still parses flattened dependencies** for arity/`dasham`/`phal` signatures, and uses the source-origin map to **suppress imported code emission**. The graph driver compiles each owner module's code once and hands objects to `sutram-link`. This is genuine **separate machine-code emission/linking**, not “compiled headers and bodies once without rereading” or incremental compilation. It is compatible because the ordinary one-pass path is **unchanged**. R29 deliberately rejects `yoj m@alias` separately (10 programs), module-level `vitti`, and Windows; callbacks from module to root lack root-signature checking; the optional driver is Python. Those are explicit boundaries, not regressions against ordinary Sutram.

**Next `yoj` work:** move opt-in graph discovery onto canonical lexer/graph data, preserve alias-to-module identity and `niryat` visibility, dedupe diamonds by canonical module IDs, provide checked stable interfaces (no reparse all sources), only then cache/reuse compiled objects and add globals/data relocs and Windows. A globally name-only `SUTRAMO1` linker cannot represent true alias privacy without a versioned interface/symbol strategy. **No forced default-path switch.**

**New, concrete driver scanner issue reproduced:** the live `tools/sutram_build.py:yoj_names` scanner searches all non-comment bytes, **including string literals**. A literal `likha("yoj bogus")` produces false dependency **`bogus")`**. Uploaded [source-equivalent scanner control](ROUND-96-WS2-BUILDER-SCANNER-PROBE.py) with exact [raw output](ROUND-96-WS2-BUILDER-SCANNER-OBSERVED.txt): real `yoj ganita` → `['ganita']` PASS, hash/slash comments → empty PASS, but **quoted string expected empty and got `['bogus")']` — FAIL**. Both raw Git blobs **match the executed files**. **This is tested driver-scanner logic, NOT_RUN as a native end-to-end direct-vs-separate compiler test.** Sarvam/Claude should add that negative then make the builder token-aware while preserving the compiler's accepted syntax.

## WS3 — non-flattering benchmark set preserved; performance code deferred

[Seven-program benchmark matrix](ROUND-96-WS3-DEFERRED-BENCHMARK-MATRIX.md) covers (1) loop reduction, (2) recursion and many small calls, (3) array/slice work, (4) `kosh` growth, (5) string parsing/building, (6) checked standard-library math, (7) streaming file I/O. It predicts probable weak spots **without inventing new timings** and defines equivalent input, safety-policy, compiler-option, checksum, RSS and statistical measurement rules. **No benchmark executed or optimiser changed in R96**, consistent with the latest owner priority. A finite suite can support comparisons **on those workloads**, not a universal “faster than C/Zig in all aspects.”

## Status / handoff

| Item | Status |
|---|---|
| WS1 exact current-format FFI design | **PASS — architecture/source**; native FFI **NOT_IMPLEMENTED** |
| Host C-ELF-to-`SUTRAMO1` bridge/executable reference control | **PASS 6/6**, Linux + GCC/Python (NOT native Sutram) |
| Host negatives: missing symbol / undefined C helper | **EXPECTED_FAILURE**, rejection observed |
| WS2 source audit of R29 separate compilation | **PASS — reading**; earlier R29 native tests **reported by Claude** |
| WS2 builder scanner: literal `yoj` in quotes | **FAIL** semantic expectation, reproduced source-equivalent control; native run **NOT_RUN** |
| WS3 benchmark matrix | **PASS — deferred document**; benchmarks **NOT_RUN** |
| Fresh full compiler/gates/fuzz/corpus, native NASM FFI and Windows this round | **NOT_RUN** |

**No compiler, linker, standard library, accepted golden, language pack, installer, CI workflow, or source lock was modified.** Only new `ChatGPT-to-Sarvam/` docs/test-oracle/raw-evidence files were added to `main`; no PR merges/force pushes/CI launches.

**Sarvam's next steps:** Read the source code, raw results and [machine-readable ledger](ROUND-96-OBSERVED.json). Assign a bounded **NASM ELF foreign-object adapter + opt-in foreign signature** phase, explicitly separate from today's working R29 module system; require an actual Sutram-generated caller before declaring C FFI. Prioritize the builder literal-import negative and keep the ordinary 558-program behavior/byte guard. Windows native acceptance remains with the owner. End Round 96 and await the user's next **CHECK FOLDER**.
