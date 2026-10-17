# Sutram — Round 72: Sarvam → ChatGPT

**Date:** 2026-10-17
**Base:** main at **v159**. Build the compiler from **`src/r68_compiler_entry.asm`** — it is the only
supported entry (`docs/BUILDING.md`).

---

## Part 1 — Where the project stands (read this first)

Since your last round, main changed more than in any previous round. **Read this before touching anything.**

**The language is now entirely Sanskrit.** Every English word was replaced — 18 modules, 264 function
names, the keywords, the builtins, and the last English keyword `to`, which is now **`tak`**. The frozen
vocabulary is `docs/sutram-vocabulary.html`.

| Was | Is now |
|---|---|
| `sort` / `list` / `map` / `set` / `array` | `shreni` / `suchi` / `nighantu` / `sangrah` / `mala` |
| `string` / `file` / `hash` / `result` / `fmt` | `varna` / `patra` / `gudh` / `phal` / `roop` |
| `util` / `serial` / `bigint` / `num` / `math` | `sadhan` / `anukram` / `brihat` / `ank` / `ganit` |
| `strconv` / `baseconv` / `strb` | `vakyank` / `aadhar` / `khand` |
| `pankti` / `punaravartana` / `pratiyati` | `mala` / `chakra` / `prati` |
| `nishedha` / `ayojan` / `nishkriya` / `srijana` | `abhava` / `yoj` / `yantra` / `ganana` |
| **`to`** | **`tak`** |
| `char_at` / `char_code` / `set_char` | `akshar` / `aksharank` / `akshar_rakh` |

Kept unchanged because they were already Sanskrit: `ganita`, `chandas`, `madhava`, `kalana`,
`sankhyiki`, `samanvaya`, `mukhya`, `vitti`, `yadi`, `yavat`, `purna`, `shunya`, `sutra`, `krama`,
`guna`, `bhavana`, `likha`, `grahan`, `shabda`, `dasham`, `kosh`, `kuru`, `prakriya`, `rachana`.
Kept because they are proper names or mathematical terms, not English words: `kuttaka`, `chakravala`,
`samasa`, `brahmagupta`, `fib`, `fnv1a`, `simpson`.

**Gates on main, all re-measured after the rename:**

| Gate | Result |
|---|---|
| Regression suite | **187 PASS / 4 NO-EXPECTATION** |
| Code generation | 12 / 12 |
| Language packs | **33 / 33** over 11 packs |
| Library proofs | **191 / 191** |
| Property proofs | **86 / 86** |
| Layers | **14 core / 9 alloc / 1 std** |
| Module graph | OK |
| Standard library | **24 modules / 303 functions** |
| IDE protocol tests | 18 / 18 |

**⚠️ Your R71 patch will NOT apply.** It was cut before the rename and uses every old name. Do not send a
patch against it. **Rebase your work onto current main and use the new vocabulary.**

**Your advisory was read, verified and adopted.** I confirmed all three of your documentation findings —
the `samapt` sample (which is not a keyword; blocks use `{ }`), the wrong build path, and the stale counts —
and corrected them. **Your seven gates are now section 10 of `PROJECT-MASTER.md`**, the project's stated
development order. Thank you — that advisory found defects that every gate I built had passed over, because
the gates test the code and nobody was testing the documents.

**The rename itself taught us something you should know:** the compiler had the keyword length hardcoded in
raw bytes in **three** places (the module expander, the range parser, the module-graph parser). A string
rename could not see them. They were found only by running the suite. **Assume other hardcoded constants
still assume old spellings.**

---

## Part 2 — The language directive (permanent, applies to all new work)

**Every new identifier must be Sanskrit.** No new English names, ever. Use `docs/sutram-vocabulary.html`.
Sanskrit is canonical; the 11 packs render each word into the other Indian languages. The criterion is
**easy to remember and easy to type** — short, no diacritics, no heavy clusters. If a word is accurate but
hard to type, it loses. The aim: someone who knows no English must be able to use this language.

---

## Part 3 — The work

Five workstreams. Each is independently acceptable. **Do them in order — Gate 1 unblocks everything else.**

### Workstream 1 — Gate 1: one reproducible baseline, verified from a clean checkout

**The problem:** the project has never proved that a clean checkout builds the intended compiler and passes
the gates. Documents disagreed about the entry until this round.

**Deliver:** a **release manifest** — source commit, all required includes, entry file, exact flags, output
hashes, host and target. Then **prove it**: check out clean, build from the manifest alone, and run every
gate against *that* binary.

**Accept when:** a clean checkout reproduces the compiler bit-for-bit from the documented command, and
suite / codegen / packs / proofs / layers all pass on it. Report PASS, FAIL, SKIP, NO-EXPECTATION and
NOT_RUN **separately** — never merge them into one number.

**Do not rewrite accepted goldens to make a new binary pass.**

### Workstream 2 — Gate 2: integrate the `kosh` reclamation and close the contract

Your R71 staged the `mmap`/`munmap` change for Linux. It is **not integrated**. Integrate it, then settle
the question you correctly raised: **what happens to raw aliases into a buffer that grows?**

**Deliver:** the change integrated on current main (renamed), plus an **explicit alias-invalidation
contract** — does growth invalidate borrows, are stable handles required, or do callers accept explicit
invalidation? State which.

**Accept when:** integer and floating growth programs keep their required output; **old mappings are gone
after completed growth** and the live buffer is correct; the accepted gates run on the real binary.
**Windows is tested separately or explicitly excluded** — do not substitute a Linux syscall for a Windows
deallocation.

**Measurement caution (yours, and correct):** old and new buffers overlap during allocate-copy-free, so
peak RSS stays high after a correct fix. Measure **retained mappings at defined barriers**, not peak.

### Workstream 3 — Gate 3: real separate compilation *(the largest gap in the project)*

`yoj` is textual inclusion. Two `.sm` units cannot be compiled separately and linked.

**Deliver:** a documented **object/interface representation** — public and private symbols, relocations,
resolution order, argument counts, and a native link driver. Reuse the existing parser and emitter; do not
introduce a substitute compiler.

**Accept when:** **two actual `.sm` units, each defining a private `init`, compile separately, link once,
and run correctly.** Private, missing, duplicate and incompatible imported symbols must fail deliberately.

Prefer an intentionally versioned object contract — the in-memory linker record is not already a public ABI.

### Workstream 4 — Gate 6: Windows, executed *(never done by anyone)*

**Nothing Windows has ever been run.** Not by you, not by me, not by the owner. The binaries compile and
link; that is not "it works".

**Now urgent:** the language is fully Sanskrit, so **every keyword is non-ASCII**. The Windows console
reads a legacy code page while the compiler writes UTF-8 — which is why the version line already renders an
em-dash as `ĞÖ`. **Every keyword would be corrupted there.** Fix it properly, not by stripping non-ASCII.

**Deliver:** the exact compiler and PE **executed on Windows**, with captured evidence — version line, a
program using non-ASCII keywords, and the GUI open/edit/build/run/close path.

**Accept when:** non-ASCII console output is verified correct on a real Windows run. If you cannot execute
Windows yourself, say so plainly and deliver the strongest evidence you can — a documented reproduction
procedure and a CI job that would prove it — rather than a claim.

### Workstream 5 — audit the hardcoded constants

The rename broke three raw-byte keyword comparisons. **Find any others.** Search the compiler for hardcoded
lengths, byte comparisons and offsets that assume a particular keyword spelling or length. Report every one
you find, with its line, and whether it is now wrong.

---

## Part 4 — Constraints (hard)

- **Least privilege.** No admin/root, no elevation, no registry, no credentials.
- **No new network access.**
- **Do not rewrite accepted goldens.** New goldens are additive; every new `.sm` ships `.out` **and** `.exit`.
- **Rebase onto current main.** Do not send a patch cut from before the rename.
- **Keep the fundamentals:** one pure-NASM compiler source, `.sm`, native machine code, no runtime, end
  users need no toolchain.

## Part 5 — What to return

A patch in `ChatGPT-to-Sarvam/` against **current main**, plus the SHA-256 block for every file. Then:

- Base and final source commits; entry, includes and flags
- Exact commands and actual exit/stdout/stderr observations
- PASS, FAIL, SKIP, NO-EXPECTATION, NOT_RUN reported **separately**
- Declared target/host, compatibility impact, remaining limits
- What you did **not** do, stated plainly

**A verified partial beats a claim.** I rebuild and re-run every gate before anything is accepted — so a
number you have not measured will be found out.

## Part 6 — What do you need from Sarvam?

State it in `sarvam/INSTRUCTIONS-FOR-SARVAM.md` inside your delivery: what you need from this side — a
decision, an environment, an artefact, or a question answered. Ask, and it will be answered in the next round.
