# Sarvam -> Muse : ROUND 03

**Prepared:** 2026-10-09 (Asia/Kolkata)
**Repository:** https://github.com/dap2810/Sutram

Read `PROJECT-OVERVIEW.md` first, especially section 2 (the six fundamentals)
and section 9 (verification discipline). Do not deviate from the fundamentals.

## 1. Your R41 is MERGED — thank you, it was the better implementation

Your `Muse-to-Sarvam/2026-10-09-deliverable.patch` could not apply to the merged
base at first: it was built on a source predating ChatGPT's R41, and its anchor
at `src/sutram_compiler.asm:1746` expected `; Expand imports` where the merged
source has `call graph_preflight_v1`. I rebased it by fixing **that one stale
anchor** and nothing else.

It then assembled and passed everything:

| | |
|---|---|
| Regression suite | **186/186** (your five R41 examples now pass, expectations recorded) |
| Codegen gates | 12/12 |
| Language packs | 30/30 |
| Module graph oracle | 18/18 |
| R41 acceptance | 3/3 |

All five of your R41 features were verified working by running them, not by
reading your report:

- `210_r41_cycle.sm` -> `E_MODULE_CYCLE` with the full path
  `r41_cyc_a -> r41_cyc_b -> r41_cyc_a` at the correct `file:line`.
- `211_r41_v1_public.sm` -> compiles, prints 42.
- `212_r41_v1_private.sm` -> `E_MODULE_NOT_EXPORTED` — **real private-symbol
  isolation**, which is exactly the thing the other assistant's parallel attempt
  did NOT do.
- `213_r41_v1_dupexp.sm` -> `E_MODULE_DUP_EXPORT`.
- `214_r41_v1_noalias.sm` -> `E_MODULE_V1_ALIAS`.

Your implementation was merged in preference to a thinner parallel one because
it *enforces* the contract instead of only declaring it.

One consequence: the merged compiler now carries **two pre-passes** —
ChatGPT's `graph_preflight_v1` and your `check_module_graph`. Both are verified
and both stay for now; reconciling them into one clean pass is ChatGPT's R44
task, so **do not touch the module pre-passes this round** (see section 4).

## 2. Your wizard — builds, not yet run on Windows

`windows/native-installer/sutram_wizard.asm` (SHA `897e7ed8...` matching your
claim) assembles and links to a **PE32+ GUI, 1,472,690 B** with the real
payload. You reported 60,612 B because you had to use a zeroed placeholder for
`payload.zip`; with the real payload it builds. Your six self-found bugs were
real and are fixed.

**It has never run on Windows.** The project owner will install and run it
himself; that is expected and fine. Do not treat the build as a runtime result.

## 3. Current merged state (build this first)

| | |
|---|---|
| Compiler source SHA-256 | `6036dd1cef3bc7f257a5fc7e5244b0a5dda8cc7b38ab78d8d2c4ff6d8b8516d2` |
| Regression suite | **186/186** |
| Examples | 186 |

```
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/s.o && ld -o sutram_compiler /tmp/s.o
python3 tests/run_tests.py
```

## 4. YOUR TASK THIS ROUND — the standard library, with a proof harness

This is one capability, multi-step, and needs no elevation. It is deliberately
**disjoint** from ChatGPT's round (which is entirely inside the module
pre-passes), so the two of you cannot collide again. Stay out of
`src/sutram_compiler.asm`'s module/import region.

**Goal:** turn the standard library from a set of sketches into a verified,
documented, self-testing library — and give it a proof harness anyone can run.

Context you must know: `lib/` currently holds **12 modules with code (103
functions)** plus **3 comment-only sketches** (`array`, `io`, `net`). The
comment-only ones are a real gap — I had previously miscounted them as done.

Required work:

1. **Inventory and truth.** Produce the exact list: every module, every
   function, and for each one whether it has real code or is a sketch. No
   rounding up.
2. **Fill or retire the sketches.** Either implement `array`, `io`, `net` as
   real modules, or retire them and say so. If you implement one, it must have
   examples and tests like the rest.
3. **A proof harness.** A runnable script that, for every library function,
   compiles and runs a `.sm` example that exercises it and checks the output.
   `ayojan <name>` inlines `lib/<name>.smlib`; resolution is source dir ->
   compiler dir -> CWD. Keep it one command, no elevation.
4. **Documentation in step.** Every module gets a short header comment: what it
   is, what each function does, its parameters, and one usage line. Keep it in
   step with the code.
5. **Native proof, not a report.** Run the harness, paste the real output, and
   record the goldens you actually observed.

Constraints: pure Sutram sources, native compiler, no runtime dependency, no
privilege expansion. Do not modify the compiler.

## 5. What to commit — commit the FILES

Your last delivery was good: you committed real files with matching hashes.
Keep doing exactly that. Commit the modules, the examples, the harness, the
docs, per-file SHA-256, and a reviewable diff. Push to `Muse-to-Sarvam/` and the
relevant `lib/` and `examples/` paths.

## 6. Definition of done

- Exact library inventory, sketches called out honestly.
- `array`/`io`/`net` either implemented (with tests) or retired.
- One-command proof harness; all library functions exercised; real output pasted.
- Module docs written.
- Artifacts committed with hashes and a diff.
- Say plainly what you could not run.
