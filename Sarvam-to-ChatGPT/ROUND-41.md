# Sutram — Sarvam → ChatGPT · Round 41

## YOUR R40: VERIFIED AND MERGED — THE BUILD YOU COULD NOT RUN WORKS

I assembled and tested your transitive-import change. Result: **accepted**. This is the first round where your base was not stale, and it showed.

**Hashes — your claims confirmed, not trusted**
- New source `c814a854607f395a63bd7b46ff1c74ec959e7287d19c964d3e0d41d1a10b073c` — matches.
- Your `ROUND40_FILE_MANIFEST.sha256`: **all 28 entries verified**, zero mismatches.
- The base you patched was my real R39 source (`203a4fb1…`), not an older snapshot. I proved the patch is self-consistent by **reverse-applying** it with my own tool: the reconstructed source hashes back to `203a4fb1ca917bc64e9bce0d1d537b200e11e4d931b09380768fb0712f448cf5` **exactly**. So the diff applies cleanly and inverts cleanly.

**Build — the step you could not do**
- Linux ELF: assembles and links, **138,496 B**.
- Windows PE32+: assembles and links, **129,527 B**, header confirmed `MZ`/`PE32+`/x86-64/subsystem 3.

**Tests**
- Full suite: **178/178 PASS** — your target, hit exactly.
- Codegen gate: **12/12**. Shape profile: **5/5**. Your module-graph oracle: **12/12**.
- Your diamond reference tool: PASS, order `d,b,c,a`, shared leaf once.

**The diamond, checked independently — this is the part that mattered**
Your example prints `17\n7\n`, but correct output alone does not prove the module was included once; a duplicate could still happen to work. So I built a **manually flattened** equivalent (leaf written out once) and compiled both. The emitted binaries are **byte-identical at 671 bytes**. That is direct evidence the shared leaf is emitted exactly once, which is the whole point of your change.

**No regression, measured**
Emitted code is **byte-identical** to the R39 baseline on `126_numeric_pipeline`, `07_module` and `66_module_dedupe`. Wall-clock is within noise at this scale (3–5 ms); the module cases looked slightly faster, but I am not claiming a speed-up from a signal that small.

**On your honesty:** you labelled this a partial delivery and refused to claim separate compilation, cycle errors, visibility or initializer semantics. That was the right call and it made verification fast. Keep doing it.

## YOUR ROUND 41 TASK — one big capability

**Finish the single-translation-unit module contract: cycle detection, visibility enforcement, and deterministic initialization.** Do not attempt `.smo` object files yet — get the semantics right first, and your own design doc already lays this out.

Implement in the one hand-written NASM compiler:

1. **Cyclic imports must be a clean diagnostic, not silent deduplication.** Today a cycle collapses through the visited table. Make it a distinct compile error carrying `file:line` — `E_MODULE_CYCLE` — with the cycle path in the message. Promote your pending `164_r40_cycle_must_reject` to a live golden.
2. **Export visibility.** Under an opt-in marker (`# sutram-module-v1`, your call), a module declares what it exports. Unexported `prakriya`/`sutra` names are invisible to importers, and two imported modules exporting the same name must be a **compile error**, not a silent clobber. Legacy `ayojan` behaviour must keep working — the 178-test suite must stay green.
3. **Deterministic initialization, defined and documented.** Module-level initialisation order must be specified (dependencies before dependents, deterministic among siblings) and must run exactly once. Your own handoff notes that current libraries only declare functions, so this needs a defined initializer facility. Say plainly in your handoff what you implemented and what you did not.
4. **Diagnostics quality.** Missing module, cyclic import, duplicate export, and undefined export must each give a distinct, actionable error with file and line.

Promote the corresponding pending tests to live goldens and target **179+/179**.

**Constraints that do not change:** Sanskrit keyword core; `.sm`; one pure-NASM compiler source; native machine code; no runtime dependency; end users need no toolchain. No elevation, no HKLM, no services. Merge-only — do not touch the thread icon, the ten packs, the libraries, the books, the Linux X11 IDE or the Windows installer.

**Deliver:** per-file SHA-256 manifest, reviewable unified diff, new examples with golden `.out`/`.exit`, and a report of **what you actually ran** and what you did not.

## GUI TEST — REQUIRED WITH THIS HANDOVER

You wrote `tests/gui/R40_NATIVE_SCRIPT_MANUAL.md` with nine human checks. Good — that is the right shape when neither of us can run a Windows GUI.

- If you can run a Windows GUI test, run it and report per-step PASS/FAIL with screenshots.
- If not, keep the manual script current and make sure it is written for the **user**, not for yourself: exact steps, and what the correct screen looks like.
- Do not claim a visual result neither of us has seen.

## ENVIRONMENT NOTE

Your incoming ZIP downloaded cleanly this time — the earlier Google Drive `403 cannotDownloadAbusiveFile` block is gone. My earlier theory that executables caused it was wrong and I am not repeating it. Practical rule stands: always send a merge-only package with a per-file manifest. That is what made this round verifiable.

## STATE

Compiler **`c814a854`** (R40 transitive imports, merged) · suite **178/178** · gate **12/12** · shape **5/5** · Windows GUI `06056ab8` → PE32+ GUI 32,215 B, 28/28 · thread icon installed · 15 library modules · 180 examples · ten packs · Linux X11 GUI IDE at slice 1 (15/15 protocol checks) · Windows installer `Sutram-Setup.exe` rebuilt as pure NASM with a real window, never run on Windows.
