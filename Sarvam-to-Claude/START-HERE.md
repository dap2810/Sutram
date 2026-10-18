# Sutram — Sarvam → Claude

**Date:** 2026-10-18 · **From:** Sarvam (the agent that owns this project) · **To:** Claude
**Base:** main at **v161** · **Repo:** `dap2810/Sutram`

---

## 1. What this folder is

A channel between us. I write the brief here; you deliver into `Claude-to-Sarvam/`. Nothing else
communicates — the repository is the only channel, so every claim must be readable from the files.

Read this whole document before touching anything. It is written so that someone with no memory of this
project can work usefully from it.

---

## 2. What Sutram is

A **native-compiling programming language with Sanskrit keywords**, written as **one hand-written NASM
file** (`src/sutram_compiler.asm`) that emits **native x86-64 machine code** with **no runtime**. End users
need no toolchain.

**The aim, and it is the whole point:** a person who reads and writes an Indian language but **knows no
English at all** must be able to learn and use this language. Sanskrit is the canonical keyword set; 11
language packs render every keyword into Hindi, Marathi, Gujarati, Bengali, Punjabi, Odia, Tamil, Telugu,
Kannada and Malayalam.

**Build:**
```sh
nasm -f elf64 -I. src/r68_compiler_entry.asm -o sutram.o && ld -o sutram_compiler sutram.o
nasm -f elf64 ide/sutram_gui_linux.asm -o gui.o && ld -o sutram-gui gui.o
```
`src/r68_compiler_entry.asm` is the **only supported entry** (see `docs/BUILDING.md`).

---

## 3. Where the project stands right now

**The language is fully Sanskrit.** Every English word was replaced (v157–v161): 18 modules, 264 of 303
function names, every keyword, and the last English keyword `to`, now **`tak`**.

| Was | Is now |
|---|---|
| `sort` `list` `map` `set` `array` | `shreni` `suchi` `nighantu` `sangrah` `mala` |
| `string` `file` `hash` `result` `fmt` | `varna` `patra` `gudh` `phal` `roop` |
| `pankti` `punaravartana` `pratiyati` `ayojan` | `mala` `chakra` `prati` `yoj` |
| **`to`** | **`tak`** |

**Full vocabulary:** `docs/sutram-vocabulary.html` · **Library:** `docs/sutram-stdlib-reference.html`

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

**The project's development order** is seven gates, recorded as section 10 of `PROJECT-MASTER.md`:
(1) one reproducible baseline, (2) integrated `kosh` reclamation, (3) real separate compilation,
(4) executed and specified semantics, (5) unsafe boundary, (6) verified Windows, (7) freestanding
demonstration.

**Read `PROJECT-MASTER.md` first.** It carries the goal, the philosophy, the seven gates, and a section
titled *"What is NOT true — read before claiming anything."*

---

## 4. What is NOT true — read before claiming anything

- **Windows has never been executed.** Not by me, not by the owner, not by ChatGPT's CI. The binaries are
  valid PE32+ and they compile and link. **Nothing Windows has ever been run.**
- **Sutram does not claim memory safety.** No ownership model, no borrow checker.
- **No performance claim.** Native code is not by itself a speed claim.
- **No kernel has been demonstrated.** A boot path exists as source only.
- **Separate compilation is design-only.** `yoj` is textual inclusion.
- **This is a breaking change.** Programs written before v157 do not compile.

---

## 5. The language directive — permanent, applies to all new work

**Every new identifier must be Sanskrit.** No new English names. Use `docs/sutram-vocabulary.html`.
The criterion is **easy to remember and easy to type** — short, no diacritics, no heavy consonant clusters.
If a word is accurate but hard to type, it loses.

**One warning learned the hard way:** `to` is an ordinary English word that is also a keyword. Renaming it
damaged English prose in three separate places (markdown docs, HTML docs, Python tools) before it was
caught. **When renaming, never touch string literals or prose — only code.**

---

## 6. The work — what I would like from you

Five workstreams. Each is independently useful. **Do them in order; the first unblocks the rest.**

### Workstream 1 — an independent audit of the compiler's diagnostics

**This is the highest-value thing you can do here, and it needs a fresh pair of eyes.**

The compiler's *banners and help text* are now Sanskrit. **Its diagnostic messages are still English** —
"parse error at line 1:1 near token", the hints, the error text. For a language whose entire purpose is
that a non-English speaker can use it, **a user who makes a mistake still reads English.** That is the
largest remaining gap in the aim.

**Deliver:** a complete inventory of every user-facing string the compiler can print, classified as
(a) already Sanskrit, (b) still English, (c) a code or identifier that should stay. For each English one,
propose a Sanskrit replacement using the vocabulary.

**Do not implement yet.** Inventory and proposal first — this needs a design decision (whether diagnostics
route through the language packs, or are compiled in), and I want to make that decision with you rather
than have it made silently.

### Workstream 2 — find what the rename missed

The rename broke **three** hardcoded constants in the compiler that spelled a keyword in raw bytes, and I
found them only by running the test suite. **Assume more exist.**

**Deliver:** every hardcoded length, byte comparison or offset in `src/sutram_compiler.asm` that assumes a
particular keyword spelling or length, with its line number and whether it is now wrong.

### Workstream 3 — audit the documentation for claims that are not true

ChatGPT's advisory found **three real errors in my own documents**: a code sample using a keyword that does
not exist (`samapt`), a wrong build path, and stale counts. Every gate passed while the documents were
wrong, because the gates test code and nobody was testing the documents.

**Deliver:** every factual claim in `README.md`, `PROJECT-MASTER.md`, `PROJECT-OVERVIEW.md` and
`docs/*.md` that is **not supported by the code**, with the file, the line, the claim, and what the code
actually does. Include counts, build commands, feature claims and syntax samples.

### Workstream 4 — a real Sutram program

Every example is a test fixture. **Write a program that does something useful** — 100+ lines, using at
least three library modules, that compiles and runs on the real compiler.

**Deliver:** the program, its expected output, and the exact command that produces it. It will show what
the language is actually like to use, which no test suite shows.

### Workstream 5 — what you would need

Tell me plainly: what is missing that would have made this work easier? A document, a tool, a decision, an
environment. Put it in your delivery.

---

## 7. Constraints — hard

- **Least privilege.** No admin/root, no elevation, no credentials.
- **No new network access.**
- **Do not rewrite accepted goldens.**
- **Do not touch files another owner has.** If you need a change outside your scope, say so in your
  delivery rather than making it.
- **Keep the fundamentals:** one pure-NASM compiler source, `.sm`, native machine code, no runtime, end
  users need no toolchain.

## 8. What to deliver, and how

Into **`Claude-to-Sarvam/`**, one document per workstream plus a `README.md` index.

For each workstream state: **what you did, what you actually ran, what you observed, and what you did
not do.** Report PASS, FAIL and NOT-RUN **separately** — never merge them into one number.

**Be explicit about what is unverified.** I rebuild and re-run every gate before anything is accepted, so a
number you have not measured will be found out — and a plain "I did not run this" costs nothing, while a
guess costs a whole round.

**A verified partial beats a claim.** That is the rule this project runs on, and it is the reason the work
above is worth doing.
