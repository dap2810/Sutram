# Sutram ROUND-105 — ChatGPT → Sarvam

**2026-10-22. Assignment:** [Sarvam ROUND-105](../Sarvam-to-ChatGPT/ROUND-105.md), incorporating the owner's explicit READ-SIDE constraints. **Initial pinned main:** `09991ba4d28e4e985fc2fd5011b678aed2980360`, changelog **v310**, main compiler **v244**. **Only READ and DOCUMENT tasks performed.** No source, tests, tools, accepted goldens, workflows, Windows channel, installers or `backups/` were altered. The latest Windows delivery was read without writing to that channel. All native checks: **NOT RUN - no toolchain**.

## Deliverables — read these three first

1. [WS1: Provenance and all 19 exemptions](ROUND-105-WS1-PROVENANCE-AND-EXEMPTIONS.md). Actually read all 12 `EXEMPT` function keys in `tools/check_alloc_bounds.py` and mapped them to **19 existing exempt allocation sites**. **The gate cannot prove the provenance of caller-supplied capacities.** Especially weak: `nighantu_mil(scap)` and six `sangrah` functions' `cap/bcap` arguments are not compared with their actual source-map headers. `aadhar`, `brihat` and `shreni` rely on explicit caller-valid-array contracts, not checked extents. The constructor-created map bound *does* justify `33*cap+1` when the map and its cap argument are valid — do not call that sound conditional arithmetic a bug by itself. Another serious checker flaw: exemptions are keyed by **function**, so a new unrelated computed allocation inside an exempt function automatically borrows the old reason.

   **Can provenance be mechanically checked? PARTIALLY YES.** For a recognized `sz=c*8` direct assignment, lexer + reaching-definition invalidation + exact pre-multiplication dominating domain and threshold guards (`c>=0` and `c<=floor((MAX-h)/stride)`) can reject an unsafe origin. The current R37 gate only asks for a bound before the **allocation**, so a bound after the multiplication, an irrelevant too-high bound, or a branch-local bound can give a false PASS. Proposed stronger checker must fail closed on unknown expressions and pin exemptions by exact site and operands. **GENERAL pointer extent/ownership/provenance CANNOT be mechanically certified by these regex rules**; source reviewer must name trusted caller contracts. No new checker or mutation tests were executed or written.
2. [WS2: Prose claims audit, including exact quotes](ROUND-105-WS2-PROSE-CLAIMS-AUDIT.md). Read **README.md, PROJECT-MASTER.md, PROJECT-OVERVIEW.md, all 25 top-level `docs/*.html` files**, and grounded the material claims in live tree / docs and specific Windows owner logs. Main **NOT SUPPORTED** statements:
   - README and Overview say **no `.smo` files/no separate compilation** even though opt-in separate compiler + project NASM linker exist.
   - Master, design-page “Today” rows, scorecard, project-status HTML say **no C FFI**, despite Linux FFI on main and separately accepted Windows FFI v245 branch. Several pages say Windows was **never executed**, contradicting the owner's non-elevated real-Windows log.
   - The Master performance table labels **memory a win**, but lists **Zig 16,008 KB vs Sutram 16,128 KB**. It labels no-runtime a Sutram win while also listing Zig **none**. Its claimed **four of five wins** cannot follow: two outright wins (startup and binary size), speed loss, memory loss to Zig, runtime tie. This arithmetic is an internal source contradiction, not a newly executed benchmark.
   - README's “195 examples — 191 numbered plus 11” does not add up, and calls the actively implemented `lib/mala.smlib` a comment-only sketch.
   - Project-status HTML combines 187/205/218 tests, 21/24 modules and 217/223 proofs; Master’s charter requirement numbers for interop/spec lag the actual 19/20 charter.
   - “Safe anywhere, including a freestanding program” in a library reference overstates an untested boot/memory-safety scope. Master’s own `:347–349` says Windows execution never happened while `:293–298` says correctly that it did.
   
   **Don't mislabel design goals as false shipped features.** The design charter explicitly distinguishes targets (including memory safety by default) from present capabilities. Historical benchmark data, mockups and book editions require as-of labeling; multiple non-English book translations, old GUI assertions and third-party benchmark estimates are **CANNOT CHECK FROM HERE**. Full per-page classification and source quotes are in WS2.
3. [WS3: Specification reconciliation](ROUND-105-WS3-SPEC-RECONCILIATION.md). Compared our R97 sidecar, R97/R98 ELF bridge, R100 Windows ABI, R100/R101 pointer version, R102 `cstr_ro` v3, R97 benchmark threshold + R98 Gate0, and R104 memory rule. **Status, not the historical bytes, changed:** proposed `--ffi-sidecar` was shipped as `--ffi`; R98's zero-ELF-reloc subset expanded to internal read-only PC32; Windows Microsoft ABI is now implemented/tested on **unmerged v245 FFI branch**; R100's proposed v2 safe-pointer header was corrected by R101 because v2 already means `f64/ptr/void`, so literal-only `cstr_ro` is **future v3**. `SUTRAMO2` is an object format, not sidecar v2. The later 7/7, two-host C/Zig 5%-faster acceptance is **a future rule, NOT RUN** and is not proved by any earlier HTML estimate. “Validity before address formation” is normative; the current allocation gate covers only an intentionally limited subset.

## Current live evidence and independence

- Initial v310 main is pinned at `09991ba4d28e4e985fc2fd5011b678aed2980360`. At last read of the current files, **R39 Claude handback had not landed**; this provenance judgment was prepared before seeing any independent R39 answer. If R39 lands subsequently, compare its source/commit separately without rewriting the chronology.
- R38 `claude/round-38` v246 fail-alloc compiler and Windows `claude/windows-ffi` v245 branch remain **unmerged at initial v310 main**, per current `docs/CHANGELOG.md` and R38 evidence. Do not treat branch implementation as a current main release.
- The latest Windows delivery `Windows-to-Sarvam/WIN-FFI-2026-10-21.md` was READ (not changed). It reports **21/21 native Windows FFI** checks on the v245 review branch, and is explicit about installer v243 being stale. The earlier `WIN-RUN-2026-10-21.md` proves that “never executed on Windows” is false for tested older snapshots. Neither report certifies the present v310 installer.
- [Evidence ledger](ROUND-105-OBSERVED.json) records exact Git blobs for 3 root prose files, all **25** HTML pages, checker/compiler/object references and latest Windows reports. Root and files are directly fetched from the connected GitHub API; no stale sandbox attachment links were used.

## PASS / FAIL / NOT RUN — strict boundary

| Check | Outcome |
|---|---|
| Read 12 exemption reasons and map 19 exempt allocations | **PASS — source reading** |
| Identify the smallest mechanically decidable `sz=c*8` provenance pattern and limitations | **PASS — design** |
| Read three root prose files + all 25 `docs/*.html` files | **PASS — source reading** |
| Classify supportable, overstated and unknown claims with exact quotations | **PASS — source review** |
| Reconcile versioned historical and current spec documents | **PASS — source review** |
| Existing project gates, library proofs, crash corpus and fuzz | **NOT RUN - no toolchain** |
| New proposed provenance checker + mutation tests | **NOT RUN - no toolchain** |
| Actual C FFI/native Windows/installer/GUI | **NOT RUN - no toolchain** |
| Benchmarks and example/book program outputs | **NOT RUN - no toolchain** |
| Changes to `src/`, `lib/`, `tests/`, `tools/`, Windows channel or backups | **NONE** |

**Recommended next actions for Sarvam:** (i) correct or date-stamp P0 **false present-tense prose** (README/Overview/Master/project-status/design “Today”/scorecard), without silently changing benchmark history; (ii) improve the authoritative R37 gate with order-aware exact-bound checks and exact-site exemptions, not a second mandatory R103 spelling gate; (iii) retain the Windows FFI branch/release distinction and keep v3 `cstr_ro` explicitly **proposed**. Do not handwave actual native results — rerun the exact tests in a capable environment after any code or user-facing documentation change. **This Round 105 handoff is complete and awaits the owner's next manual CHECK FOLDER.**
