# Sutram — standing context for Muse

**Read this before any round.** It is kept current so you never work from a stale picture.
**You are paused at present.** This document exists so that when you resume, you start up to date.

Last updated: 2026-10-19 · **v176** · repo `dap2810/Sutram`

---

## 1. What Sutram is

A **native-compiling programming language with Sanskrit keywords**, written as **one hand-written NASM
file** (`src/sutram_compiler.asm`) that emits **native x86-64 machine code** with **no runtime**. End users
need no toolchain.

**The aim, and it is the whole point:** a person who reads and writes an Indian language but **knows no
English at all** must be able to learn and use this language. Sanskrit is the canonical keyword set; **11
language packs** render every keyword into Hindi, Marathi, Gujarati, Bengali, Punjabi, Odia, Tamil, Telugu,
Kannada and Malayalam.

**Build:** `nasm -f elf64 -I. src/r68_compiler_entry.asm -o s.o && ld -o sutram_compiler s.o`
**Gates:** `sh tools/gates.sh` — its output is the truth about the tree.

---

## 2. What changed while you were paused — read this carefully

**The whole language was renamed to Sanskrit between v157 and v176.** If you hold notes, patches or test
fixtures from before that, **they will not apply.** This is the single most important thing on this page.

| Was | Is now |
|---|---|
| `sort` `list` `map` `set` `array` | `shreni` `suchi` `nighantu` `sangrah` `mala` |
| `string` `file` `hash` `result` `fmt` | `varna` `patra` `gudh` `phal` `roop` |
| `util` `serial` `bigint` `num` `strconv` `baseconv` `strb` `math` | `sadhan` `anukram` `brihat` `ank` `vakyank` `aadhar` `khand` `ganit` |
| `pankti` `punaravartana` `pratiyati` `ayojan` | `mala` `chakra` `prati` `yoj` |
| **`to`** | **`tak`** |

**Three changes that affect your work directly:**

1. **An undefined name is now a compile error** (v173, extended v175). `Sutram Error [E_UNDEFINED_NAME]:
   agyat naam 'x'`. Before, an undefined name **silently read as 0** — so a mistyped keyword gave a **wrong
   answer with no diagnostic**. Also now errors: an undeclared struct field, a field name over 8 bytes, and
   an undeclared array index. **Any proof or fixture that relied on the old behaviour will now fail.**
2. **The compiler's diagnostics are Sanskrit** (v169) — `Sutram Error: vyakaran dosh, pankti 5:1`.
3. **The Windows interface is English** (v175) — menus, buttons and installer.

**The rename's tail surfaced in seven different places** — code, comments, HTML, prose, keyword tables, the
teaching books, and the GUI's own keyword table — **and not one was found by a gate.** Expect more; the
sweeps have never come back empty.

---

## 3. Where the project stands (measured, v176)

| Gate | Result |
|---|---|
| Regression suite | **191 PASS / 4 NO-EXPECTATION** |
| Code generation | 12 / 12 |
| Language packs | 33 / 33 over 11 packs |
| Library proofs | **191 / 191** |
| Property proofs | 86 / 86 |
| Layers | 14 core / 9 alloc / 1 std |
| Module graph | 18 / 18 |
| X11 GUI protocol | 18 / 18 |
| **Windows execution** | **PARTIAL** — installed, run and uninstalled once on real Windows 11 as a standard user; **not a release** |
| Standard library | **24 modules / 303 functions** |

---

## 4. The road to v1.0 — where your work sits

**`ROADMAP-TO-V1.0.md` in the repo is the single source of truth.** Ten numbered steps, each with an owner
and a "done when". **If a task is not on that list, it is not on the critical path.**

**v1.0 is:** the procedural core correct and complete, the library usable, Windows installing and running,
and the diagnostics in the user's language. **It is not** generics, concurrency, events, the kernel
demonstration or separate compilation — those are v2.

| # | Step | Owner |
|---|---|---|
| 1 | Close the silent-wrong-answer class in the compiler | Claude |
| 2 | Decide and apply the diagnostics language | Owner decides, Claude applies |
| 3 | Make Windows a repeatable gate, then pass it | Claude builds, **owner runs** |
| 4 | Fix the `kosh` leak | ChatGPT |
| **5** | **Prove the standard library is complete** | **Muse — this is yours** |
| 6 | Compile every code sample in every document | Sarvam |
| 7 | Measure performance | Sarvam |
| 8 | Security and least-privilege audit | Sarvam + Claude |
| 9 | Install / upgrade / uninstall on clean Windows | **Owner** |
| 10 | Freeze and release v1.0 | Sarvam |

### Your step, in detail

**Step 5 — prove the standard library is complete. Done when every one of the 24 modules has a documented
contract, a passing proof, and at least one example that compiles and runs.**

**The honest state of it:** the library is **24 modules and 303 functions**, with **191 library proofs and 86
property proofs** passing. **191 is not 303 — and nobody currently knows which functions have no proof.**
Producing that list is the first thing to do, and it is the number that has to exist before release.

**Two things that will bite you, both learned the hard way on this project:**

- **A stale name can hide after a `\n` escape.** The character before it is the letter `n`, so a naive
  word-boundary check misses it. This cost a whole round.
- **`pankti` means "line" as well as being the old array keyword.** It appears legitimately inside the
  Sanskrit diagnostic `vyakaran dosh, pankti 5:1`. **Do not "fix" it.** Same for `to` — an ordinary English
  word that was also a keyword, which has been broken and repaired four times.

---

## 5. The rules this project runs on

- **A verified partial beats a claim.** A plainly stated "I could not run this" costs nothing. A guess costs
  a whole round, because **every delivery is rebuilt from source and every number re-measured before it is
  merged.**
- **Report PASS, FAIL and NOT-RUN separately**, with the environment named per check. A count that hides its
  own skips is worse than no count.
- **Do not state a hypothesis as a finding.** Several real defects were found by collaborators saying "I
  suspect this but have not confirmed it" — and several false ones avoided.
- **Read the current file from main before changing it.** A stale working copy once silently reverted 27
  compiler strings and dropped the suite from 187 to 181 **while the changelog claimed 187.** That is the
  most serious error made on this project, and it is why the rule exists.
- **Independent checks have caught ten errors of mine.** If you find something wrong in an existing file,
  **say so.** It is the most valuable thing any collaborator has done here.
- **The language directive:** every new identifier Sanskrit, easy to remember and easy to type. **Never
  rename inside string literals or prose — only code.**
