# Sutram — Clean-Project handover: Sarvam → ChatGPT

**Date:** 2026-10-16
**Repo:** `https://github.com/dap2810/Sutram` (public, owner `dap2810`, branch `main`)
**This round's folders:**
- **`Sarvam-to-ChatGPT-Clean-Project/`** — this brief and the clean project archive
- **`ChatGPT-to-Sarvam-Clean/`** — where you return your work

## What this round is

This is **not** a feature round. For this one round the job is different, and deliberately broader:

> **Take the whole project, build it, audit it for mistakes, fix them, and bring every project file up to date with the current state.**

You are being asked to be the reviewer of the whole thing, not the author of the next slice. That is a
temporary change of role, agreed with the project owner.

## What you have been given

`SUTRAM-CLEAN-PROJECT.zip` in this folder is the **complete, current project tree** — 1,546 files, with
the collaboration folders deliberately removed so nothing from the handoff history confuses the audit.
It contains:

| Path | What it is |
|---|---|
| `src/sutram_compiler.asm` | the compiler — one pure-NASM file |
| `src/r66_indic_lexer.inc`, `src/r67_stack_pair.inc` | the includes the compiler consumes |
| `ide/sutram_gui_linux.asm` | the Linux X11 IDE |
| `windows/` | the Windows compiler, GUI and native installer **sources** |
| `lang/*.lang` | 11 language packs |
| `lib/*.smlib` | 21 standard-library modules, 278 functions |
| `examples/` | 216 example programs |
| `tests/` | the regression corpus, goldens, and the R66/R67 helper tests |
| `tools/` | every verification gate and per-round acceptance script |
| `docs/` | the books, the language reference, the stdlib reference, the CHANGELOG |
| `benchmarks/`, `win/`, `icons/`, `compiler/` | supporting trees |

**Build it yourself before judging anything:**

```sh
nasm -f elf64 -I. src/sutram_compiler.asm -o /tmp/c.o && ld -o sutram_compiler /tmp/c.o
nasm -f elf64 ide/sutram_gui_linux.asm -o /tmp/g.o && ld -o sutram-gui /tmp/g.o
```

You need only NASM and a linker. No C compiler, no runtime.

## The state I measured, so you can check my work

I built and ran the clean tree before sending it. **These are my numbers — verify them, and tell me if
any is wrong:**

| Gate | My result |
|---|---|
| Regression suite | **187 pass, 4 no-expectation** |
| Codegen gate | **12 / 12** |
| Language packs | **33 / 33** |
| Module graph | **OK** |
| Library proofs (`proof_lib`) | **177 / 177** |
| Property proofs (`proof_props`) | **69 / 69** |
| R67 helper tests | **OK (9 skipped)** |
| R66 helper tests | **FAILED — 1 failure, 17 skipped** |
| Library reference | **21 modules, 278 functions** |
| GUI tests | **15 / 15** |
| Compiler binary | **190,144 bytes** |
| GUI binary | **37,352 bytes** |

## A real defect I already found — fix it, and find its siblings

**`tests/r66/test_prepare_review.py::PackTests::test_counts_and_uniqueness` fails:**

```
AssertionError: 44 != 45
```

R66 added a Gujarati keyword that **collided with an accepted test** (`37_native_gujarati` used the word
as a variable name). R67 resolved that collision by **omitting the reservation**, which left the Gujarati
pack at **44 entries** — but R66's own test still asserts **45**. R67 changed the pack and never updated
R66's test.

That is the shape of mistake this round exists to find: **a change in one round silently invalidating an
assertion from another.** Fix it — and then look for its siblings across the whole test tree.

## What I want you to do

### 1. Build everything that can be built on your machine, and report honestly
Compiler, IDE, and the Windows sources where a toolchain exists for you. State exactly what you built and
what you could not.

### 2. Audit the whole project for mistakes
In rough priority order:
- **Tests that assert stale numbers** — the R66 case above is one. Sweep for others.
- **Docs that assert stale numbers** — test counts, function counts, module counts, pack counts,
  example counts, version numbers. I fixed a batch of these by hand; find what I missed.
- **Dead or contradictory claims** — a doc describing behaviour the code no longer has, two docs
  disagreeing, a README describing a file that no longer exists.
- **Invisible or unreadable content in the HTML docs** — I found one real case: `.legend` set a cream
  background inside `.cover` which sets a cream text colour, so the text was invisible. Check for others.
- **Anything that simply does not work** — a gate that cannot pass, a script that errors, a broken link.

### 3. Fix what you find
Make the fixes. Prefer the smallest correct change. **Do not rewrite accepted goldens** — if a golden is
genuinely wrong, say so and explain why rather than quietly editing it.

### 4. Bring every file up to date
The project's own docs must describe the project as it actually is. Where a number is stale, correct it
where it is a *current claim* — and **leave the CHANGELOG alone**, because its old numbers are history.

### 5. Report
For every fix: what was wrong, what you changed, and how you verified it. For everything you could not
fix: say so plainly. **A verified partial beats a claim.**

## The rule that has mattered most in this project

**Check the check.** More than once, the thing that was wrong was the tool doing the checking — a test
reading the wrong byte offset, a grep that could not match, a fetch that served a stale file. Before
reporting a defect, confirm the check itself is right. I have made that mistake; you should assume you
will too.

## Hard constraints — these do not bend

- **Least privilege.** No admin, no root, no UAC, no elevation, no HKLM, no registry beyond HKCU, no
  disabling any safeguard. Do not run anything that needs privileges you do not have.
- **No credentials** anywhere — placeholders only, including in tests, CI and commit messages.
- **No new network access.** The compiler and library stay self-contained.
- **No push-triggered workflows.** `workflow_dispatch` only.
- **Fail closed.** If an input does not match what a tool expects, refuse — do not guess.
- **The fundamentals do not change:** the Sanskrit keyword core, the `.sm` extension, one pure-NASM
  compiler source, native machine code, no runtime dependency, and an end user who needs no toolchain.

## What to return, and where

Put your work in **`ChatGPT-to-Sarvam-Clean/`**, containing:
1. `REPORT.md` — what you found, what you fixed, what you could not fix, and your measured gate numbers.
2. `SUTRAM-CLEAN-PROJECT-FIXED.zip` — the corrected tree, so I can diff it against what I sent.
3. A `SHA256.txt` covering every file you changed.

I will verify your numbers by building and running the tree myself, the same way I verified this one.
