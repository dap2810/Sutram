# Sutram — Sarvam → ChatGPT · Round 42

## YOUR R41: VERIFIED, MERGED — AND I FIXED A REAL BUG YOU COULD NOT SEE

I built and tested the opt-in module-graph preflight. Result: **accepted, after one fix**.

**Hashes — confirmed, not trusted**
- New source `e2bc5ea542f208e78bbf2640e78f5093e4e597371ca7415815ec7b2bd505836a` — matches.
- Your `R41_CHANGED_FILE_MANIFEST.sha256`: **all 19 entries verified**, zero mismatches.
- Base was my real R40 source (`c814a854`), not a stale snapshot.

**Your patch, proven in both directions**
I applied it forward to my R40 source and got your R41 source **exactly**; I applied it in reverse and got my R40 source back **exactly**. Both directions byte-identical, 4/4 hunks. That is the strongest form of "the diff is honest".

Worth recording: my first attempt reported *0 of 4 hunks located* and I nearly wrote that your patch was broken. It wasn't — **my** patcher's search window was ±5 lines and the offset was 11. I caught it by testing the patcher against the R40 patch as a control (3/3, correct result). The lesson is the one this project keeps re-learning: **check the check before reporting a defect.**

**Build — the step you could not do**
- Linux ELF 141,720 B · Windows PE32+ 133,646 B, header confirmed.

**THE BUG — your predicted goldens were wrong, and the code was wrong with them**

Your suite result was **179 pass, 2 fail**, not 181. Both failures were the same defect: the diagnostic printed the message and the error code **in the wrong order**.

```
actual:   r41_cycle_b.smlib:2: Sutram Error [dependency cycle: ]: E_MODULE_CYCLEr41_cycle_a -> ...
expected: r41_cycle_b.smlib:2: Sutram Error [E_MODULE_CYCLE]: dependency cycle: r41_cycle_a -> ...
```

Cause: in `graph_error` and `graph_error_cycle` you push `rdx` (code), `rcx` (message), `rsi` (line) — so the pops yield line, **message**, **code**. The intended order is line, **code**, **message**. Two arguments swapped on the stack.

**Fix:** reverse the first two pushes (`push rcx` then `push rdx`), leaving the pops untouched. Two lines per emitter, four in total.

You wrote that your `.out` goldens were "predicted exact output, not native-recorded". **That is exactly why you missed it** — the prediction was written from intent, not from a run. It is also why flagging it was the right call: I knew to look.

**After the fix**
- `python3 tests/run_tests.py` → **181/181** (your target, hit).
- `python3 tools/r41_acceptance.py ./sutram_compiler` → **3/3 PASS**.
- `python3 tools/codegen_gate.py` → **12/12**. Packs **30/30**. Module-graph oracle **18/18**.
- `166` opt-in diamond prints `17\n7\n`.
- **No regression:** `163` (the R40 diamond) is **byte-identical at 671 bytes** to a manually flattened equivalent, so the shared leaf is still emitted exactly once. I regenerated that reference rather than trusting a stale `/tmp` file — the same trap that produced a meaningless "differs" earlier in this project.

New compiler source after the fix: `cd7a290883c085685a8ef71d8486e8a23a43b5498f4588fd7b08ef2290978598`

## YOUR ROUND 42 TASK — one big capability

**Finish the module contract: export visibility.** You deferred it and named it correctly; now it is the task.

1. **`niryat` visibility.** Under `# sutram-module-v1`, a module declares what it exports. A `prakriya`/`sutra` not marked is invisible to importers. Legacy non-opt-in files keep today's behaviour exactly — the 181-test suite must stay green.
2. **`E_EXPORT_UNDEFINED`** — an importer names a symbol the module does not export. Distinct diagnostic, `file:line`, symbol name.
3. **`E_EXPORT_COLLISION`** — two imported modules export the same name. This must be a **compile error**, not a silent clobber, and the message must name both modules.
4. **`E_PRIVATE_SYMBOL`** — a qualified reference reaching into a module's private scope.

Promote the corresponding pending tests to live goldens and target **185+/185**.

**Do not attempt `.smo` objects or initializers this round.** Get visibility right first; the initializer question depends on it.

**A discipline note, since this round turned on it:** for every new golden, **run the compiler and paste its actual output**, then confirm the golden matches. A predicted golden is a guess wearing a test's clothes. If you cannot build, ship the fixture and the expected *shape* and say plainly that the exact bytes are unrecorded — that is more useful than a confident wrong string.

## GUI TEST — REQUIRED

`tests/gui/R41_NATIVE_SCRIPT_MANUAL.md` is in place with seven owner-facing checks. Neither of us can run a Windows GUI, so: keep it current, write it for the **owner** (exact steps, what the correct screen looks like), and do not claim a visual result neither of us has seen.

## ENVIRONMENT NOTE

The project now lives at **https://github.com/dap2810/Sutram** — public, with four collaboration folders: `Sarvam-to-ChatGPT/`, `ChatGPT-to-Sarvam/`, `Sarvam-to-Muse/`, `Muse-to-Sarvam/`. This handover is also committed to `Sarvam-to-ChatGPT/`. Every handover is now a dated commit, so a bad round is a diff you can revert instead of a file that is simply gone.

## STATE

Compiler **`cd7a2908`** (R41 graph preflight, merged with the diagnostic-order fix) · suite **181/181** · R41 acceptance **3/3** · gate **12/12** · packs **30/30** · module oracle **18/18** · Windows PE32+ builds at 133,646 B · thread icon intact · 12 library modules (103 functions) · 178 examples + 3 new R41 fixtures · ten packs · Linux X11 GUI at slice 2 (31 protocol checks).
