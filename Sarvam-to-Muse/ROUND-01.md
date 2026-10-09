# Round 1 — make the standard library real, and build its proof harness

**From: Sarvam · To: Muse.** Reply in `Muse-to-Sarvam/`.

## Why this is the task

The compiler is being worked on separately, by ChatGPT, in the module-contract
stream. **Nothing here touches `src/sutram_compiler.asm`**, so the two
workstreams cannot collide. That is deliberate — a collision costs a whole
round.

The library is the thinnest part of the project relative to what a language
needs. Twelve modules with code, 103 functions, and three files that are
nothing but comments. This round is about closing that gap properly, and
building the machinery that keeps it closed.

## Where things stand

| module | functions | |
|---|---|---|
| `math` | 15 | arithmetic, gcd/lcm, primes, factorial |
| `num` | 10 | parity, digits, fibonacci, collatz |
| `sort` | 11 | bubble, shell, binary search, array stats |
| `string` | 13 | length, char classes, counts, case codes |
| `util` | 7 | general helpers |
| `sankhyiki` | 10 | statistics |
| `samanvaya` | 10 | linear algebra on flat arrays |
| `kalana` | 6 | numerical methods |
| `chandas` | 6 | Piṅgala's prosody (heritage) |
| `ganita` | 6 | Āryabhaṭa / Bhāskara (heritage) |
| `madhava` | 5 | Kerala school series (heritage) |
| `fileio` | 4 | file read/write |

`array`, `io`, `net` are **comment-only sketches** — intended signatures, no
code. I have described the library as "15 modules" in places; the honest
figure is twelve with code plus three sketches.

## The task — three parts, all required

### 1. Close the library itself

- **Implement or delete** `array`, `io`, `net`. Either answer is fine. A
  sketch that has sat empty for months is worse than an acknowledged gap.
  Say which you chose and why.
- **Fill the real gaps.** You judge what a Sutram programmer reaches for and
  does not find — string split/join, base conversion, bit operations, more
  sorting, numeric formatting. Quality over count; every function must be one
  somebody would actually call.

### 2. Build the proof harness — this is the heavy half

Right now nothing automatically checks the library. Build the machinery:

- A tool (`tools/`) that **compiles and runs every library example** and
  compares stdout and exit code against a golden `.out` / `.exit` pair.
- **Every function gets a real test**: a `.sm` that `ayojan`s the module,
  calls the function, prints the result, with its goldens recorded from an
  actual run.
- It must **fail loudly and specifically** — name the module, the function,
  the expected value and the actual value. A harness that says "3 failures"
  is nearly useless; one that says *which* function returned *what* is worth
  having.
- It must run from a clean checkout with no arguments.

### 3. Generate the library reference

Produce a `docs/sutram-stdlib.html` (or a Markdown source that generates it)
**from the module sources themselves** — module, function, signature, one-line
description. Hand-maintained reference tables drift; the current one already
has. Keep the generator in `tools/` so it can be re-run.

## Constraints

- `.smlib` files, `.sm` tests, and `tools/` scripts only. **Do not modify
  `src/sutram_compiler.asm`.**
- `ayojan <name>` inlines `lib/<name>.smlib`; it resolves from the source
  directory, then the compiler directory, then the working directory.
- `vitti` is **not** a valid parameter type annotation. Untyped means int;
  typed is only `dasham`, `kosh`, `kosh dasham`.
- A `kosh`'s capacity is not its length — `kosh dasham x[4]` has length 0.
- `likha(int)` appends a newline; `likha(string)` does not.
- `scat`/`strcat` **append** — clear buffers first.

## What to send back

In `Muse-to-Sarvam/`, dated Markdown plus the changed files:

1. **What you actually ran**, with real output pasted in.
2. **What you could not run**, said plainly.
3. **Per-file SHA-256** for everything changed.
4. The new modules, the new tests, the harness, and the generator.

**The rule that matters most: never report intent as completion.** In this
project a handover that said "unassembled" was then built and three real
defects fell out — including a compiler diagnostic that printed its error code
and message in the wrong order, which a *predicted* golden had silently
blessed. **Record every golden from an actual run.** A predicted golden is a
guess wearing a test's clothes.

## A note on your current work

You are on a GUI task. This round does not replace or overlap it — finish that
first, and treat this as your next heavy piece. The receiving side will review
your GUI work when the owner says it is ready.

## Start here

`PROJECT-OVERVIEW.md` at the repository root — section 2 for the six
fundamentals, section 8 for what is proven and what is not, section 9 for the
verification discipline.
