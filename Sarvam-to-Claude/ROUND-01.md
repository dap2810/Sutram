# Sutram — ROUND-01: Sarvam → Claude

**Date:** 2026-10-18 · **Base:** main at **v162** · **Repo:** `dap2810/Sutram`
**Deliver into:** `Claude-to-Sarvam/`
**Orientation:** read `Sarvam-to-Claude/START-HERE.md` first — what Sutram is, the aim, the fundamentals,
and what is NOT true.

---

## Part 1 — Where the project stands (read this first)

Sutram is a **native-compiling programming language with Sanskrit keywords** — one hand-written NASM file
that emits native x86-64 with no runtime. **The aim is that someone who knows no English can learn and use
it.** Sanskrit is canonical; 11 packs render every keyword into the other Indian languages.

**The language is now fully Sanskrit** (v157–v162): 18 modules, 264 of 303 function names, every keyword.
The last English keyword `to` is now **`tak`**.

| Was | Is now |
|---|---|
| `sort` `list` `map` `set` `array` | `shreni` `suchi` `nighantu` `sangrah` `mala` |
| `string` `file` `hash` `result` `fmt` | `varna` `patra` `gudh` `phal` `roop` |
| `pankti` `punaravartana` `pratiyati` `ayojan` | `mala` `chakra` `prati` `yoj` |
| **`to`** | **`tak`** |

**Vocabulary:** `docs/sutram-vocabulary.html` · **Library:** `docs/sutram-stdlib-reference.html`

**Gates on main, all re-measured:**

| Gate | Result |
|---|---|
| Regression suite | 187 PASS / 4 NO-EXPECTATION |
| Code generation | 12 / 12 |
| Language packs | 33 / 33 over 11 packs |
| Library proofs | 191 / 191 |
| Property proofs | 86 / 86 |
| Layers | 14 core / 9 alloc / 1 std |
| Standard library | 24 modules / 303 functions |
| IDE protocol tests | 18 / 18 |

**Build:** `nasm -f elf64 -I. src/r68_compiler_entry.asm -o s.o && ld -o sutram_compiler s.o`
— that entry is the **only supported one** (`docs/BUILDING.md`).

**Division of labour.** ChatGPT owns the compiler internals, systems, specification and Windows. Muse
owns the standard library, proofs and contracts. **Your work is deliberately independent of both** — see
below.

---

## Part 2 — The language directive (permanent, applies to all new work)

**Every new identifier must be Sanskrit.** No new English names. Use `docs/sutram-vocabulary.html`. The
criterion is **easy to remember and easy to type** — short, no diacritics, no heavy consonant clusters.

**One warning, learned four times over:** `to` is an ordinary English word that is also a keyword.
Renaming it damaged English prose in the markdown docs, the HTML docs, the Python tools and the compiler's
own help text before it was caught. **When renaming, never touch string literals or prose — only code.**
And when you audit prose, look for words that **read wrong**, not just words spelled wrong.

---

## Part 3 — The work

Five workstreams. Each is independently useful. **Do them in order — the first unblocks the rest.**

### WS1 — an inventory of the compiler's diagnostics *(the most valuable thing here)*

The compiler's **banners and help text are now Sanskrit**, but **its diagnostic messages are still
English** — `parse error at line 1:1 near token`, the hints, the error text.

**For a language whose entire purpose is that a non-English speaker can use it, a user who makes a mistake
still reads English.** That is the largest remaining gap in the aim.

**Deliver:** a complete inventory of **every user-facing string the compiler can print**, each classified:

- **(a) already Sanskrit** — leave alone
- **(b) still English** — needs replacing
- **(c) a code, identifier or path** — must stay as it is

For every (b), propose a Sanskrit replacement using the frozen vocabulary, and note where it appears
(`src/sutram_compiler.asm` line, and whether it is emitted at lex, parse, codegen or runtime).

**Do not implement.** Inventory and proposal only. Whether diagnostics route through the language packs or
are compiled in is a **design decision** I want to make with your evidence, not have made silently.

### WS2 — find what the rename missed

The rename broke **three** hardcoded constants that spelled a keyword in raw bytes — the module expander
(`cmp dword [rsi], 0x6A6F7961` = "ayoj"), the for-range parser (`cmp ecx, 0x6F74` = "to"), and the
module-graph parser (`add r8, 6`). **I found them only by running the suite. Assume more exist.**

**Deliver:** every hardcoded length, byte comparison or offset in `src/sutram_compiler.asm` that assumes a
particular keyword spelling or length — with its line, what it assumes, and whether it is **now wrong**.

### WS3 — audit the documentation against the code

An advisory found **three real errors in my own documents**: a code sample using a keyword that does not
exist (`samapt`), a wrong build path, and stale counts. **Every gate passed while the documents were
wrong**, because the gates test code and nobody was testing the documents.

**Deliver:** every factual claim in `README.md`, `PROJECT-MASTER.md`, `PROJECT-OVERVIEW.md` and `docs/*.md`
that is **not supported by the code** — file, line, the claim, and what the code actually does. Include
counts, build commands, feature claims, and **every code sample** (compile it and see).

### WS4 — a real Sutram program

Every example in the repo is a test fixture. **Write a program that does something useful** — 100+ lines,
at least three library modules, that compiles and runs on the real compiler.

**Deliver:** the `.sm` file, its expected output, and the exact command that produces it. This will show
what the language is actually like to use, which no test suite shows.

### WS5 — what you need

Tell me plainly what was missing that would have made this work easier: a document, a tool, a decision, an
environment. Put it in your delivery.

---

## Part 4 — Constraints (hard)

- **Least privilege.** No admin/root, no elevation, no credentials.
- **No new network access.**
- **Do not rewrite accepted goldens.**
- **Do not touch files another owner has.** ChatGPT owns the compiler internals, Muse owns the library. If
  you need a change outside your scope, **say so in your delivery** rather than making it.
- **Keep the fundamentals:** one pure-NASM compiler source, `.sm`, native machine code, no runtime, end
  users need no toolchain.

## Part 5 — What to deliver, and how

Into **`Claude-to-Sarvam/`**, one document per workstream plus a `README.md` index:

```
README.md
01-DIAGNOSTICS-INVENTORY.md
02-HARDCODED-CONSTANTS.md
03-DOCUMENTATION-AUDIT.md
04-REAL-PROGRAM.md  +  the .sm file
05-WHAT-I-NEED.md
```

For each workstream state four things plainly: **what you did, what you actually ran, what you observed
(paste real output), and what you did not do.**

Report **PASS, FAIL and NOT-RUN separately.** Never merge them into one number — a count that hides its own
skips is worse than no count.

## Part 6 — What I will verify

I rebuild the compiler, re-run every gate, and re-measure every number you claim, **before anything is
accepted**. So:

- **A verified partial beats a claim.** A plainly stated "I could not run this" costs nothing.
- **Do not state a hypothesis as a finding.** If you suspect something but have not confirmed it, say so in
  those words. Several real defects here were found that way — and several false ones avoided.

**One thing worth knowing:** independent checks on this project have caught real errors in my own work
**six times** — documents I wrote, a rename I applied, a changelog I clobbered. If you find something wrong
in the existing files, **say so.** That has been the single most valuable thing any collaborator has done
here.
