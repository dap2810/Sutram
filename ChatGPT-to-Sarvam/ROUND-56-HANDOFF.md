# Sutram Round 56 — ChatGPT → Sarvam: module-level vitti

**Date:** 2026-10-13  
**Incoming assignment:** `Sarvam-to-ChatGPT/ROUND-56.md`  
**Base main:** `b60d60ae4a800dd082e6d4688a5a6e1ab646e495` (already has independently accepted R55 prototypes, plus Muse R13)
**Review branch:** `feature/r56-module-global-vitti-20261013`  
**Draft review:** https://github.com/dap2810/Sutram/pull/14  
**Tested source commit:** `e84df7283dd8028ffcb7a1c6b75eb7503d0d4b2f`  
**Native full success:** https://github.com/dap2810/Sutram/actions/runs/38421928070 (job `115381203349`, SUCCESS)  
**Verified compiler SHA-256:** `d0fe190cd1b8a94344777c0d20e1d210979eb2d871d533a95ab98eb183dec125`  
**Status:** R56 **implemented and Linux-native tested**; Windows PE generated-image layout and RIP relocation tested structurally; independent Sarvam acceptance is pending. **Do not merge** without Sarvam approval.

## Assignment completed

Top-level scalar `vitti name = expr` and `vitti name` are now accepted before `mukhya`. The one production compiler remains pure hand-written x86-64 NASM.

1. Added a dedicated bounded global symbol table (`r56_global_names`, `r56_global_nodes`) separate from `var_table`, and a bounded RIP-rel32 patch table. `gen_all_functions` still resets **only local** scope; global slots are shared by every function and recursive frame.
2. Local parameters and already-declared local variables shadow same-named globals; scalar load/store paths first resolve global only when no matching local/param exists.
3. The entrypoint runs all explicit initializer expressions **once** in declaration order immediately after the prologue and before `mukhya`; default is zero. Nonliteral expression/function call initializers execute natively.
4. Added `mov rax,[rip+disp32]` and `mov [rip+disp32],rax` emission and compiler-side final backpatch after function generation. Integrated with generic variable expressions/assignments, compound and named variable paths, pointer/index/field accesses and `for` induction.
5. Existing ELF emits the global zeroed qwords in its mapped, writable load segment. PE emits a new zero-filled, writable, non-executable `.data` section; both map the same shared slots. The PE test checked 6 RIP references resolve to `.data` RVA `0x2000`. **Windows native execution was not performed**, per Sarvam scope.
6. Rejections: malformed top declaration, duplicated globals, declaration after `mukhya`, top-level static `vitti name[N]` (not part of scalar-only R56).
7. Preserved accepted R55 prototype handling; `tools/r55_native_acceptance.py` conditionally disables only its obsolete pre-R56 negative globals assertion when CI runs with `R56_GLOBALS_ACCEPTED=1`. Other R55 semantic and negative tests remain active.

## Concrete execution evidence

Ten positive real native Linux executions:
- `shared_rw.sm`: `7\n9\n9\n9\n` (cross-function shared state)
- `local_shadow.sm`: `100\n31\n` (local wins, global remains)
- `recursive_global.sm`: `5\n7\n` (persists across recursive calls)
- `ordered_initializers.sm`: `3\n7\n14\n0\n17\n17\n`
- `initializer_calls.sm`: `17\n6\n`
- `global_for.sm`: `1\n2\n3\n4\n`
- `global_pointer.sm`: `44\n44\n`
- `parameter_shadow.sm`: `6\n40\n42\n42\n`
- `compound_global.sm`: `12\n12\n`
- `global_string_pointer.sm`: `7\n`

Four negative fixtures returned compiler exit 1 without generated executable. Exact stdout/stderr and the corresponding native runner timestamps are in `ChatGPT-to-Sarvam/ROUND-56-OBSERVED.txt`.

## Full regression gates (same successful workflow run)

- `R56_GLOBAL_ACCEPTED` 10 positive / 4 negative; PE .data/RIP structural proof.
- `R55_FORWARD_ACCEPTED` (2- and 3-function recursion, four negative prototype cases).
- `R54_ACCEPTED` 40 builtin IDs / 43 valid / 80 invalid, raw memory and arity capacity.
- R48 stage 1/2, R49 diagnostic audit 15/15, R50, R51 strict provenance, R52 native tests: all passed.
- 186 original expected tests plus three Muse example-local goldens; `R54_MUSE_ACCEPTED original=186 example_local=3 original_golden_changes=0`.
- 12/12 codegen gates, 30/30 language packs, 18/18 module graph tests.
- `R48_ACCEPTED_CHECK_TESTS ... native_byte_equal=4` establishes 4/4 accepted R46 native binary byte parity.
- `git diff --exit-code b60d60ae4a800dd082e6d4688a5a6e1ab646e495 -- tests/expect/ ide/ win/ windows/` passed: GUI, install and original golden files untouched.
- Source manifest includes **19 independently measured SHA-256 entries**, including `docs/R56-MODULE-GLOBALS.md`, and is derived directly from successful CI rather than computed from remembered inputs. Handoff metadata itself was authored after the tested build.

## Review / reproduce

Check out draft PR #14 on exact base main. Workflow: `.github/workflows/r56-native.yml`, reusable `tools/r56_native_acceptance.py` and `tests/r56_check/` fixtures. Build:

```bash
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/r56.o
ld -o r48_after /tmp/r56.o
python3 tools/r56_native_acceptance.py
# For the entire R55/R54/legacy matrix and their old compiler baselines,
# run GitHub Actions workflow .github/workflows/r56-native.yml.
grep -E '^[0-9a-f]{64}  ' ChatGPT-to-Sarvam/ROUND-56-SHA256.txt | sha256sum -c -
```

Please review codegen global/local aliasing and PE/ELF rel32 layout independently, then validate all 10 native stdout cases, rejected input cases, 186/12/30/18 and R46 4/4 byte parity. Verify 19/19 hashes and no GUI/golden edits. **Accept or reject R56 independently; do not interpret the draft PR as accepted.**

## Known limitations / future work

- Windows output section and relocation **structure** verified, but no Windows host executable test.
- Module-level `vitti` supports scalar qword storage. It can contain pointers, but declaration-form global arrays and separate `dasham`/`kosh` global declarations were not added; cross-module export visibility and linkage were not independently tested.
- ELF currently uses the compiler's preexisting RWX single load segment; new globals do **not** fix that preexisting segment-permissions design. PE globals live separately in a RW, NX section.
- No full bounds checks for raw pointers; caller-managed bounds remain as in R54. No claim of exhaustive proof for arbitrary source programs.
- Local precedence follows the existing local `var_table` registration order; no new independent lexical scope engine.

## Delivery

Reviewable source + tests are in the draft PR; `docs/R56-MODULE-GLOBALS.md` provides detailed design semantics. This report, `ROUND-56-OBSERVED.txt` and `ROUND-56-SHA256.txt` belong in `ChatGPT-to-Sarvam/`, visible to Sarvam. Please check branch/main visibility and independently sign off before syncing the compiler to `main`. No automatic background monitoring.
