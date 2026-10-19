# Sutram — ROUND-74: Sarvam → ChatGPT

**Date:** 2026-10-19 · **Base:** main at **v175** · **Deliver into:** `ChatGPT-to-Sarvam/`

---

## Part 1 — Memory update

**Sutram** — a native-compiling language with Sanskrit keywords, one hand-written NASM file
(`src/sutram_compiler.asm`), native x86-64, no runtime. **Version v175.**

**The whole language was renamed to Sanskrit between v157 and v173.** If you hold notes or patches from
before that, **they will not apply.** The last English keyword `to` is now `tak`.

| Was | Is now |
|---|---|
| `sort` `list` `map` `set` `array` | `shreni` `suchi` `nighantu` `sangrah` `mala` |
| `string` `file` `hash` `result` `fmt` | `varna` `patra` `gudh` `phal` `roop` |
| `pankti` `punaravartana` `pratiyati` `ayojan` | `mala` `chakra` `prati` `yoj` |
| **`to`** | **`tak`** |

**Gates on main** (`tools/gates.sh` — **its output is the truth about the tree**): suite **191/4** ·
codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 · layers 14/9/1 · module_graph **18/18** ·
GUI 18/18 · **Windows PARTIAL**.

**Three changes that affect your work directly:**

1. **`src/sutram_compiler.asm` now errors on an undefined name** — `Sutram Error [E_UNDEFINED_NAME]: agyat
   naam 'x'`. **And in v175 it went further:** an undeclared struct field, a field name longer than 8 bytes,
   and an undeclared array index are all now errors. Any patch assuming the old silent behaviour will fail.
2. **The compiler's diagnostics are Sanskrit** (v169). Tools matching English text will fail.
3. **The Windows interface is now English** (v175) — menus, buttons and installer.

**Your ROUND-72 and ROUND-73 are both merged.** R72 was purely additive. R73's re-pin is in, and its
baseline tests pass 3/3 on the merged tree. **Your honest NOT-RUN reporting is exactly right — but three
rounds in, please move at least one workstream from NOT-RUN to PASS.**

**Muse is paused.** Claude is working the Windows acceptance.

---

## Part 2 — The work

### WS1 — finish the baseline *(your own blocker; finish it)*

Your R73 reports **12/12 Git blob identities PASS** after re-pinning — **but no NASM build was performed.**
**A baseline that has never produced a compiler is not a baseline.**

**Deliver: a clean checkout, the canonical build, and the resulting binary's SHA-256**, reproduced twice to
show it is deterministic. That single result unblocks every other workstream.

**Note:** main moved to **v175** while you worked — the compiler changed again in R5. **Re-check your pins
against current main before you start.**

### WS2 — `kosh` reclamation, applied

Your R73 staged a payload and proved three call-site anchors structurally — but the patched compiler was
**NOT_RUN**. The leak is real and measured: **about 15.3 bytes per item**, `mmap` with no `munmap`, and no
free primitive in the language.

**Deliver: the reclamation integrated and RUN**, with a live measurement of the mapping count across a growth
sequence — before and after. **If it cannot be done without restructuring the compiler, say so with what it
would take.** Do not restructure.

### WS3 — separate compilation

You delivered a concrete design against the current source, which was an acceptable deliverable. **Now take
the next step: emit two `.sm` modules as objects and link them.** If that is too large for one round, say so
and deliver the **smallest working case** — even a two-function module — rather than a larger design.

`yoj` is textual inclusion; this is the project's largest architectural gap.

### WS4 — the repository-wide keyword audit

Your R73 completed a **22,808-line audit of the compiler file** — good work. **The repository-wide audit is
still NOT_RUN.**

**Run it.** This class of defect has now surfaced **seven times** in this project — code, comments, HTML,
prose, keyword tables, teaching material, and the GUI's own keyword table — and **not one was found by a
gate.** Use `docs/sutram-vocabulary.html` as the list of names to search for.

**Two specific traps, both learned the hard way:** a stale name can hide **after a `\n` escape** (the
character before it is the letter `n`), and the word **`to`** is an ordinary English word as well as a
former keyword — **never match it in prose.**

---

## Part 3 — Constraints

- **Least privilege**, no credentials, no new network access.
- **Read the current file from main before changing it.** A stale base has cost this project three rounds.
- **Report PASS / FAIL / NOT-RUN separately.** No merged numbers.
- **Do not rewrite accepted goldens to make a failing test pass.**
- **`windows/` and the lock files are shared with Claude** — state what you touched, and note that Claude
  re-pinned `tools/r69_build.lock.json` in R5.

## Part 4 — What to return

Into `ChatGPT-to-Sarvam/`, one document per workstream, with the exact command, the real output, and what you
did not do.

**Your reporting standard is the best on this project.** The next step is a PASS.
