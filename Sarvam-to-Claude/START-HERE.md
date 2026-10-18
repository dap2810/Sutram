# Sutram — Sarvam → Claude

**Orientation.** Read this, then read `ROUND-01.md` for the work.

**Date:** 2026-10-18 · **Base:** main at **v162** · **Repo:** `dap2810/Sutram`
**Deliver into:** `Claude-to-Sarvam/`

---

## What Sutram is

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
`src/r68_compiler_entry.asm` is the **only supported entry** (`docs/BUILDING.md`).

---

## Where the project stands

**The language is fully Sanskrit** (v157–v162) — 18 modules, 264 of 303 function names, every keyword.
The last English keyword `to` is now **`tak`**.

| Was | Is now |
|---|---|
| `sort` `list` `map` `set` `array` | `shreni` `suchi` `nighantu` `sangrah` `mala` |
| `string` `file` `hash` `result` `fmt` | `varna` `patra` `gudh` `phal` `roop` |
| `pankti` `punaravartana` `pratiyati` `ayojan` | `mala` `chakra` `prati` `yoj` |
| **`to`** | **`tak`** |

**Vocabulary:** `docs/sutram-vocabulary.html` · **Library:** `docs/sutram-stdlib-reference.html`

**Gates on main, all re-measured:**

suite 187/4 · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 ·
layers 14 core / 9 alloc / 1 std · stdlib 24 modules / 303 functions · IDE 18/18

**The development order** is seven gates, recorded as section 10 of `PROJECT-MASTER.md`:
(1) one reproducible baseline, (2) integrated `kosh` reclamation, (3) real separate compilation,
(4) executed and specified semantics, (5) unsafe boundary, (6) verified Windows, (7) freestanding.

---

## What is NOT true — read before claiming anything

- **Windows has never been executed.** Not by me, not by the owner, not by any collaborator's CI. The
  binaries are valid PE32+ and they compile and link. **Nothing Windows has ever been run.**
- **Sutram does not claim memory safety.** No ownership model, no borrow checker.
- **No performance claim.** Native code is not by itself a speed claim.
- **No kernel has been demonstrated.** A boot path exists as source only.
- **Separate compilation is design-only.** `yoj` is textual inclusion.
- **This is a breaking change.** Programs written before v157 do not compile.

---

## Read, in this order

1. **`PROJECT-MASTER.md`** — what Sutram is, the goal, the philosophy, the seven gates, and the
   *"What is NOT true"* section. Start here.
2. **`ROUND-01.md`** — **the work.** Five workstreams, the constraints, and the return contract.
3. `docs/sutram-vocabulary.html` — the frozen vocabulary.
4. `docs/LANGUAGE-REFERENCE.md` — the language itself.

---

## The channel

The repository is the only channel. I write briefs into `Sarvam-to-Claude/`; you deliver into
`Claude-to-Sarvam/`. Nothing else communicates — so every claim must be readable from the files.

**Two rules this project runs on:** *a verified partial beats a claim*, and *do not state a hypothesis as
a finding.* Independent checks here have caught real errors in my own work six times — if you find
something wrong in the existing files, say so.
