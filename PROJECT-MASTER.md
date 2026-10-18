# Sutram — Project Master Record

**One patra to read before touching anything.**
Last updated: 2026-10-16 · CHANGELOG v152 · 129 recorded versions
Repo: `https://github.com/dap2810/Sutram` (public, owner `dap2810`, branch `main`)

If you are an AI or a person about to work on this project, **read this patra first, then
`docs/sutram-design-parameters.html`.** Between them you will know what the project is, what it is
trying to be, what has been done, and the rules it holds itself to.

---

## 1. What Sutram is

**A programming language whose keywords are Sanskrit, compiled by one hand-written NASM patra to native
machine code.** No runtime, no C compiler, no interpreter, no virtual machine. The end user needs no
toolchain at all.

Its name, सूत्रम्, means *sūtra* — the terse rule-form of Pāṇini's *Aṣṭādhyāyī*, the world's first formal
grammar. The language's identity and its grammar are the same decision: Sanskrit is the keyword core, and
the standard library is built on the Indian mathematical tradition (Piṅgala's binary, the Meru-prastāra,
Āryabhaṭa's kuṭṭaka, Bhāskara's chakravāla).

A program looks like this:

```sutram
mukhya() {
    vitti n = 5
    yavat (n > 0) {
        likha(n)
        n = n - 1
    }
}
```

This exact program compiles and prints `5 4 3 2 1`. Blocks use `{ }` — there is no `samapt` keyword.

`mukhya` = main · `vitti` = variable · `likha` = print · `yavat` = while · `{ }` = block.

**Multilingual by design.** The same program can be written in Devanagari, Gujarati, Tamil, Telugu,
Bengali, Kannada, Malayalam, Marathi, Odia or Punjabi — the canonical meaning is fixed and only the
keyword spellings change. **11 language packs** exist today.

## 2. The main goal

> **A multi-paradigm, native-compiled language with an easy procedural core, strong type checking,
> memory safety by default, and explicit low-level control for operating systems.**

The target is **Python-like ease for everyday programming, Rust-inspired safety, C-level hardware
control, and reusable abstractions** — without copying every feature or every complexity of those
languages.

Concretely, in the owner's words: *make this programming language powerful*, with the advanced complexity
**optional for the programmer — not undefined in the implementation**.

## 3. The philosophy

1. **Simple programs must be simple.** A beginner writes a useful program without learning classes,
   traits, concurrency or memory annotations first. Advanced features build on that foundation.
2. **The language's identity is the point.** Sanskrit keywords are not decoration. This is the one thing
   Sutram does that no other language does, and it is a design commitment, not a theme.
3. **No runtime, no toolchain.** One hand-written NASM patra produces native machine code. The end user
   downloads a binary and runs it.
4. **Do not claim what you have not measured.** Safety, portability, performance superiority and OS
   readiness are **not** claimed without evidence. This is the project's governing rule.
5. **A verified partial beats a claim.** Every number in the docs is meant to come from running something,
   and anything untested is labelled untested.
6. **Check the check.** More than once, the thing that was wrong was the tool doing the checking — a test
   reading the wrong byte offset, a listing sorted by an identical timestamp, a number typed by hand
   instead of read. Before reporting a defect, confirm the check itself is right.

## 4. The paradigms — nine of them

The project supports (or is building toward) nine paradigms. Status is measured against the compiler as
tested.

| # | Paradigm | Status |
|---|---|---|
| 1 | **Imperative / procedural** — the foundation | **Implemented** — the language's strongest part |
| 2 | **Practical functional** — first-class functions, closures, iterators, pattern matching | Partial — functions exist, but not first-class |
| 3 | **Generic programming** — generics with clear constraints | Not started |
| 4 | **Object orientation through composition** — structures, methods, traits | Partial — `rachana` gives structs; no methods or traits |
| 5 | **Data-oriented** — contiguous arrays, slices, layout, SIMD | Partial — `mala`/`kosh` are contiguous; no slices or SIMD |
| 6 | **Structured concurrency** — threads, tasks, channels, cancellation | Not started |
| 7 | **Event-driven / asynchronous** — callbacks, timers, async I/O | Not started |
| 8 | **Controlled compile-time metaprogramming** — bounded, deterministic | Partial — `sutra` consts; `yoj` is textual include |
| 9 | **Multilingual and native-script programming** | **Implemented** — 11 packs over one canonical meaning |

**Why multilingual is a paradigm and not a feature:** every other language on the suchi can be described
without naming a natural language. Sutram cannot.

## 5. The parameters — twenty requirements

The full statement is `docs/sutram-design-parameters.html`. Summary, with honest status:

**A · Paradigms** — 1–9 above.

**B · Capabilities beyond paradigms**

| # | Requirement | Status | The gap |
|---|---|---|---|
| 10 | Strong static typing with inference | Partial | Types checked; inference limited; no formal contracts |
| 11 | Coherent memory and resource model | **Not started** | No ownership, no borrow checking, no `unsafe` boundary |
| 12 | Explicit error handling | Partial | `ok` out-param convention; no phal type or propagation |
| 13 | Genuine freestanding capability | Partial | Native ELF/PE, no libc; **no boot path or kernel demonstrated** |
| 14 | One language, layered libraries | Partial | 24 modules; layers now marked and machine-checked |
| 15 | Portability in the compiler | Partial | Linux x86-64 tested; **Windows never executed** |
| 16 | Real modules, packages, separate compilation | Partial | `yoj` is textual inclusion; no package manager |
| 17 | Excellent developer tools | Partial | IDE + installer + diagnostics; no formatter, LSP or debugger |
| 18 | Interoperability and ecosystem | Not started | No C FFI |
| 19 | Precise specification and evidence gates | Partial | Real gates and `SPECIFICATION.md`; no fuzzing, no cross-platform run |

**C · Implementation order** — the charter's own sequence, which the project follows:
1. Stabilise the foundation · 2. Make substantial programs manageable · 3. Prove systems capability ·
4. Add reusable abstractions · 5. Expand carefully.

**The project is at stage 1–2. Do not jump to stage 4.**

**Tally: 3 implemented · 12 partial · 5 not started.**

## 6. The history

**Era 1 — the Sanskrit compiler (v1–v28, late September 2026).**
The project began as a Sanskrit-keyword compiler in NASM, iterated rapidly. Artefacts from this era are
named `sanskrit-*.zip` and `sutram-v2.zip` … `sutram-v28.zip`. By the end of it there was a working
compiler, a book, an icon sangrah, and a Windows port plan.

**Era 2 — the round system (ROUND-01 onward).**
Work moved to a numbered-round model with independent AI partners, each taking a *heavy* assignment and
delivering verifiable artefacts. `docs/CHANGELOG.md` records every version from v21 to v152.

**Era 3 — the design charter (v151–v152).**
The owner wrote down what the language is *for*. This became `docs/sutram-design-parameters.html`
(20 requirements, each with honest status) and `docs/sutram-project-status.html` (measured state).

**Where the numbers stand now** (measured 2026-10-16):

| Metric | Value |
|---|---|
| Regression suite | **187 pass, 4 no-expectation** |
| Code-generation shape gates | **12 / 12** |
| Language packs | **33 / 33** checks over **11** packs |
| Library proofs | **191 / 191** |
| Property proofs | **86 / 86** |
| Module graph | OK |
| Layer check | **14 core, 9 alloc, 1 std** |
| Standard library | **24 modules, 303 functions** |
| Example programs | **207** |
| GUI tests | **18 / 18** |
| Negative corpus (R70) | **6 / 6, native_status PASS** |
| Compiler source | 545,722 B → **190,144 B** binary |
| Repository | ~1,800 files |

## 7. How the project is built

Three parties work on it. **The repository is the only channel between them.**

| Party | Role | Delivers |
|---|---|---|
| **Sarvam** (this agent) | Owns the project; verifies everything; builds and runs every gate; syncs to `main`; works its own stream | Compiler work, the Linux IDE, docs, verification |
| **ChatGPT** | Compiler, systems, specification, Windows | Branch sources + a preparation tool that pins input blobs; reports as `ROUND-NN-*.md` |
| **Muse** | Standard library, proofs, contracts | Patches with a SHA-256 block; reports as `date-roundNN-*.md` |

**Folders on the repo:**

- `Sarvam-to-ChatGPT/` — rounds issued to ChatGPT
- `ChatGPT-to-Sarvam/` — its replies (ROUND-42 … ROUND-70)
- `Sarvam-to-Muse/` — rounds issued to Muse
- `Muse-to-Sarvam/` — its replies (round1 … round28)
- `Sarvam-to-ChatGPT-Windows/` — the Windows installer + IDE brief
- `Sarvam-to-ChatGPT-Clean-Project/` — the whole-project audit brief
- `ChatGPT-to-Sarvam-Clean/` — its audit reply

**The working rules that emerged, learned the hard way:**

- **Never merge unverified work.** Build it, run it, then sync.
- **Verify every GitHub write against the API**, not the download. The tarball and the raw CDN have both
  served stale content repeatedly.
- **Diff before syncing.** Partners cut branches from older `main`; a blind copy has silently reverted
  newer work twice.
- **Two AIs given the same task will collide.** Keep workstreams provably disjoint.
- **A report is not verifiable — the files are.** Fetch the artefacts and check the hashes.
- **Never ship a `--record` sweep.** It rewrites every golden and strips newlines from `.exit` files.

## 8. The hard constraints — these do not bend

- **Sanskrit keyword core** · **`.sm`** extension · **one pure-NASM compiler source** · **native machine
  code** · **no runtime dependency** · **the end user needs no toolchain.**
- **Least privilege.** No admin, no root, no UAC, no elevation, no HKLM, no registry beyond HKCU.
- **No credentials** anywhere — placeholders only, including tests and commit messages.
- **No new network access.** No push-triggered workflows — `workflow_dispatch` only.
- **No antivirus or execution-policy bypass** advice, and no code requiring either.
- **Fail closed** on unexpected input.

## 9. What is NOT true — read before claiming anything

- **Sutram does not claim memory safety.** There is no ownership model. The charter says specify the rules
  *before* claiming the guarantee, and `docs/MEMORY-MODEL.md` is that specification — not an
  implementation.
- **Windows is not supported.** The sources exist and are complete-looking. **Nothing Windows has ever
  been executed by this project.** The one gate nothing has passed.
- **No performance claim.** The compiler emits native code; that is not by itself a speed claim.
- **No OS capability.** No boot path, no kernel, no freestanding run. `docs/FREESTANDING.md` is a gap suchi.
- **A known defect, open:** the Windows console renders `Sutram 1.0 (v29) – the complete thread` as
  `... ĞÖ the complete thread` — a mangled en-dash. The compiler writes UTF-8; the console reads a legacy
  code page. Any non-ASCII output is corrupted on Windows.

## 10. The development order — seven gates

Proposed by ChatGPT's advisory of 2026-10-17 and adopted here as the project's stated order. Each gate
has a **deliverable** and an **acceptance condition**; nothing is claimed as done until its condition is
met on the real binary. Gates can run in parallel where patra ownership is disjoint.

| # | Gate | Deliverable | Accept when |
|---|---|---|---|
| 1 | **One reproducible baseline** | A release manifest: source commit, inputs, entry, flags, output hashes, host and target. Feature labels: default-integrated, experimental, source-only, planned | A clean checkout builds the intended compiler, and every accepted gate runs against *that* executable. Never rewrite goldens to make a new binary pass |
| 2 | **`kosh` reclamation, integrated** | The staged Linux growth fix merged, with capacity arithmetic, allocation-failure handling and an **explicit alias-invalidation contract** | Growth programs keep their output; old mappings are gone after growth; the live buffer is correct. **Windows is tested separately or excluded** — Linux syscall emission is not a Windows deallocation |
| 3 | **Real separate compilation** | An object/interface representation, public/private symbols, relocations, a native link driver | **Two actual `.sm` units compile separately, link once and run.** Private, missing, duplicate and incompatible symbols fail deliberately |
| 4 | **Executed and specified semantics** | Precise rules for scoping, evaluation order, integers, conversions, strings and pack selection | Discriminating positive *and* negative programs run on the real compiler, with recorded inputs, exits and diagnostics |
| 5 | **Unsafe boundary and resource model** | End-to-end acceptance of the optional boundary, then an ownership design | Valid use works; forbidden use-after-move, conflicting mutation and dangling-reference cases are prevented **within the declared scope** |
| 6 | **Verified Windows release** | One accepted native package chain and a consistent pack experience | The exact compiler and PE execute on Windows; **non-ASCII console output is verified**; GUI open/edit/run/close and per-user install paths are exercised |
| 7 | **Freestanding demonstration** | A documented loader interface, entry ABI, stack, memory layout and OS-free core | A Sutram-generated body boots in the declared image and produces an expected captured marker. **An unbooted sector or an ordinary native app does not satisfy this** |

**The discipline these enforce.** No gate is satisfied by a document, a patch, or a claim. Each one names
the observation that makes it true. Two of them — Windows execution and the freestanding boot — have
**never been performed by anyone**, and that is stated plainly in section 9.

## 11. How to work on this project

1. **Read this patra, then `docs/sutram-design-parameters.html`.**
2. **Build it first.** NASM and a linker are all you need:
   ```sh
   nasm -f elf64 -I. src/r68_compiler_entry.asm -o /tmp/c.o && ld -o sutram_compiler /tmp/c.o
   nasm -f elf64 ide/sutram_gui_linux.asm -o /tmp/g.o && ld -o sutram-gui /tmp/g.o
   ```
3. **Run the gates** before and after your change:
   ```sh
   python3 tests/run_tests.py                        # expect PASS=187 NO-EXPECTATION=4
   python3 tools/codegen_gate.py ./sutram_compiler   # expect 12 PASS
   python3 tools/test_lang_packs.py ./sutram_compiler # expect 33/33
   python3 tools/proof_lib.py --compiler ./sutram_compiler     # expect 183
   python3 tools/proof_props.py --compiler ./sutram_compiler   # expect 76
   python3 tools/check_layers.py                     # expect 12 core, 9 alloc
   ```
4. **Work in a stage that matches the charter's order.** We are at stage 1–2.
5. **Report honestly.** Say what you ran, what you observed, and what you could not verify. Keep failures
   and skips separate from passes.
6. **If you change behaviour, update the docs that describe it** — and leave `CHANGELOG.md`'s historical
   numbers alone.

## 12. What is open right now

| Item | State |
|---|---|
| **Windows installer + IDE** → ChatGPT (`Sarvam-to-ChatGPT-Windows/`) | Issued, awaiting |
| **Charter numbering in the round briefs** | **My error to fix** — briefs cite items 13/11/9 where the charter has 14/12/10. Both partners caught it independently. |
| **`0 std` in the layer check** | Worth confirming it is intentional |
| **`kosh` growth leak** | Recorded in `docs/MEMORY-MODEL.md` — copies to a new buffer without reclaiming the old |
| **The Windows encoding defect** | Named, in the Windows brief |
| **R66/R67 pack-count mismatch** | **Fixed** by the clean-project audit (45 → 44, with a regression) |

## 13. The nighantu of the documents

| If you want… | Read |
|---|---|
| What the language is being built to be | `docs/sutram-design-parameters.html` |
| How the project is actually doing | `docs/sutram-project-status.html` |
| The language reference | `docs/LANGUAGE-REFERENCE.md` |
| The standard library | `docs/sutram-stdlib.html`, `docs/LIBRARY-LAYERS.md`, `docs/LIBRARY-BOUNDARY.md` |
| What is specified and what is not | `docs/SPECIFICATION.md` |
| The memory model (proposed) | `docs/MEMORY-MODEL.md` |
| What must be rejected | `docs/NEGATIVE-CORPUS.md` |
| The freestanding gap suchi | `docs/FREESTANDING.md` |
| Numeric behaviour | `docs/NUMERIC-CONTRACT.md`, `docs/OVERFLOW-SAFETY.md` |
| The error convention | `docs/ERROR-CONVENTION.md` |
| Property proofs, and what would break them | `docs/PROPERTY-NET.md` |
| Every version | `docs/CHANGELOG.md` |
| The books (6 editions) | `docs/sutram-book-*.html` |
| Installing on Windows | `docs/INSTALLATION-ROUTES.md`, `docs/WINDOWS-SETUP.md` |

---

**The standard, one last time.** Do not claim safety, portability, performance superiority or OS
readiness without corresponding evidence. A verified partial beats a claim. And check the check — the
tool doing the checking has been the wrong thing more often than the thing being checked.
