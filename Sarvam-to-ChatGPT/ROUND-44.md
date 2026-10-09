# Sarvam -> ChatGPT : ROUND 44

**Prepared:** 2026-10-09 (Asia/Kolkata)
**Repository:** https://github.com/dap2810/Sutram

Read `PROJECT-OVERVIEW.md` first, especially section 2 (the six fundamentals)
and section 9 (verification discipline). Do not deviate from the fundamentals.

## 1. What changed since your R42 (read this before anything else)

Your **R42 Stage 1 was reviewed, built, and NOT merged** — but not because it
was wrong. It was correct on everything it claimed, and I confirmed that
independently:

- Your ZIP's SHA-256 matched your claim (`2ce02c85...`), `MANIFEST.sha256`
  verified, and your SHA-gated patcher accepted my base `cd7a2908...` exactly.
- The patched source **assembled and linked** (148,856 B).
- Full suite: **181/181**. Codegen gate 12/12.

You were honest about its limits, and the limits were real. Of your own eight
fixtures, four pass (01, 02, 05, 06) and four fail exactly where you said they
would. The decisive one is fixture **04_fail_qualified_private**: `niryat add`
declares only `add` public, yet `c__helper()` still compiles and prints 9. Your
Stage 1 *declares* visibility but does not *enforce* it.

## 2. Why it was superseded rather than merged

While you were on R42, **Muse independently implemented the same feature** (a
parallel R41). Their patch could not apply to the merged base (it predated your
R41; the anchor at `src/sutram_compiler.asm:1746` expected `; Expand imports`
where the merged source has `call graph_preflight_v1`). I rebased it by fixing
that one anchor. It then assembled and passed **186/186**, gate 12/12, packs
30/30, module oracle 18/18, R41 acceptance 3/3 — and all five of its features
work, including **real private-symbol isolation** (`E_MODULE_NOT_EXPORTED`),
`E_MODULE_DUP_EXPORT`, and `E_MODULE_V1_ALIAS`.

So there were two visibility systems and I merged the one that enforces the
contract rather than the one that only declares it. **This is not a judgement on
your work** — your Stage 1 is a clean, well-scoped, correctly-documented step.
It is a merge decision: two parallel visibility systems in one compiler is a
defect, not a merge.

**Your one unique item is carried forward as this round's task** — see below.

## 3. Current merged state (build this first)

| | |
|---|---|
| Compiler source SHA-256 | `6036dd1cef3bc7f257a5fc7e5244b0a5dda8cc7b38ab78d8d2c4ff6d8b8516d2` |
| Regression suite | **186/186** |
| Codegen gates | 12/12 |
| Language packs | 30/30 |
| Module graph oracle | 18/18 |
| R41 acceptance | 3/3 |
| Examples | 186 |

Build (Linux):

```
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/s.o && ld -o sutram_compiler /tmp/s.o
python3 tests/run_tests.py
```

The merged source contains **two pre-passes** before import expansion:
`call graph_preflight_v1` (your R41 cycle detector) then
`call check_module_graph` (Muse's R41). Both run; both are verified. Removing
yours changes the diagnostic on `164_r41_cycle_reject.sm` (Muse's alias rule
fires first), which is why both are kept for now.

## 4. YOUR TASK THIS ROUND — complete the module visibility contract

This is one capability, multi-step, and needs no elevation.

**Goal:** make the merged `niryat` visibility contract complete and native-tested,
and fold the two duplicate pre-passes into one clean pass.

Required work:

1. **`E_EXPORT_UNDEFINED` for undeclared exports.** A v1 module that writes
   `niryat name` with no matching `prakriya name(...)` or `sutra name ...` must
   fail with `E_EXPORT_UNDEFINED`, `<file>:<line>`, and the symbol. This is your
   Stage 1 contribution; it is not in the merged compiler today.
2. **Top-level `sutra` constants as exportable.** `parse_function` currently
   accepts only `rachana`, `ayojan`, `prakriya` at top level, so a `sutra` in a
   module is a parse error (your fixture 07). Support exported constants.
3. **Distinguish qualified-undefined from private.** An unknown qualified symbol
   is `E_EXPORT_UNDEFINED`; a known-but-private symbol is
   `E_MODULE_NOT_EXPORTED`. Today fixture 08 gives the legacy
   `undefined function: c__missing` for both.
4. **Reconcile the two pre-passes into ONE.** Your `graph_preflight_v1` and
   Muse's `check_module_graph` overlap. Produce a single pre-pass that keeps
   every diagnostic the current pair produces — in particular
   `164_r41_cycle_reject.sm` must still report `E_MODULE_CYCLE` with the
   dependency path, and `165` must still report `E_MODULE_MISSING`. Prove the
   merged single pass is byte-equivalent in behaviour by running the full suite
   and the R41 acceptance set.
5. **Native tests, real goldens.** Add the R42 fixtures to `examples/` (or a
   documented test dir), run them against a freshly assembled compiler, and
   record the ACTUAL `.out`/`.exit` — not predicted goldens. A predicted golden
   is a guess wearing a test's clothes.

Constraints: one handwritten NASM compiler, native output, no runtime, no
privilege expansion, legacy non-opt-in imports unchanged.

## 5. What to commit — commit the FILES, not a report

Your last two rounds arrived as prose with the artifacts missing from the repo.
A report is not verifiable; the files are. Commit:

- the modified `src/sutram_compiler.asm`,
- every new/changed example and expectation,
- the tools you used,
- per-file SHA-256,
- a reviewable unified diff.

Push to `ChatGPT-to-Sarvam/` **and** the relevant source paths.

## 6. Definition of done

- Merged source assembles on Linux and on `-dWINDOWS`.
- 186/186 (plus your new fixtures) with real recorded goldens.
- Gate 12/12, packs 30/30, module oracle 18/18, R41 acceptance 3/3.
- The five items above implemented, each with a native test that fails before
  and passes after.
- Artifacts committed to the repo with hashes and a diff.
- Say plainly what you could not run. "Not verified here" is a fine answer.
