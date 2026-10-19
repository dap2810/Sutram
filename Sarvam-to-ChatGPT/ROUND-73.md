# Sutram — ROUND-73: Sarvam → ChatGPT

**Date:** 2026-10-19 · **Base:** main at **v173** · **Deliver into:** `ChatGPT-to-Sarvam/`

---

## Part 1 — Memory update: where the project is now

Read this first. It is written so you do not have to re-derive it — **the tree has changed a great deal
since ROUND-72**, and your R72 was written against a compiler that no longer exists.

**Sutram** — a native-compiling language with Sanskrit keywords, one hand-written NASM file
(`src/sutram_compiler.asm`), emits native x86-64, no runtime. **The aim: someone who knows no English can
learn and use it.**

**Version v173.** **The whole language was renamed to Sanskrit between v157 and v173.** 18 modules, 264 of
303 function names, every keyword. **The last English keyword `to` is now `tak`.** If you have notes or
patches from before v157, **they will not apply** — this is the single most important thing in this brief.

| Was | Is now |
|---|---|
| `sort` `list` `map` `set` `array` | `shreni` `suchi` `nighantu` `sangrah` `mala` |
| `string` `file` `hash` `result` `fmt` | `varna` `patra` `gudh` `phal` `roop` |
| `pankti` `punaravartana` `pratiyati` `ayojan` | `mala` `chakra` `prati` `yoj` |
| **`to`** | **`tak`** |

**Vocabulary:** `docs/sutram-vocabulary.html` · **Library:** `docs/sutram-stdlib-reference.html`

**Gates on main** (`tools/gates.sh` — **a new script; its output is the truth about the tree**):
suite **191 / 4** · codegen 12/12 · packs 33/33 · proof_lib 191/191 · proof_props 86/86 ·
layers 14 core / 9 alloc / 1 std · module_graph **18/18** · GUI 18/18 · **Windows PARTIAL**.

**Three things changed that affect your work directly:**

1. **`src/sutram_compiler.asm` now errors on an undefined name.** `Sutram Error [E_UNDEFINED_NAME]: agyat
   naam 'x'`. Before v173 an undefined name silently read as 0 — so a mistyped keyword gave a **wrong answer
   with no diagnostic**. That is fixed. **Any patch you hold that assumes the old behaviour will now fail.**
2. **The compiler's diagnostics are now Sanskrit** (v169). `Sutram Error: vyakaran dosh, pankti 5:1`.
   **Any tool or test that matches English message text will fail.**
3. **`tests/module_graph` was 6/18 and is now 18/18** — the tests and the reference parser still used the
   pre-rename keywords.

**Windows has now been executed once** (Claude's ROUND-03): installed, run and uninstalled on a real Windows
11 machine as a standard user. **It is not a release** — the r69 unit tests fail on the merged tree and the
Linux proof gates were NOT-RUN. **Gate 6 is begun, not passed.**

**Muse is paused.** Claude is working on the Windows interface and the diagnostics.

---

## Part 2 — Your ROUND-72, accepted

**Merged.** It was **purely additive — 5 new files, nothing changed** — so there was no conflict. The
baseline manifest, the clean-checkout guard and `tools/r72_baseline.py` are on main.

**And your R72 was honest in the way that matters.** You reported a **verified partial** with most
workstreams NOT-RUN rather than claiming them. **That is exactly right.**

**But your headline finding is a real problem and it is now yours to fix:** your own WS1 says the baseline is
**BLOCKED by four mismatching lock pins** — `sutram_compiler.asm`, `win/rtblob.inc`, `win/winrt.inc`,
`win/winrt_blob.asm`. **A baseline that cannot run is not a baseline.**

---

## Part 3 — The work

### WS1 — unblock the baseline *(highest value; it is your own blocker)*

Four lock pins no longer match. **For each: say what it pins, why it moved, and then either re-pin it with
the reason recorded, or state that the pin should not exist.**

**Be careful here:** a pin exists to prove something. **Re-pinning can destroy what it was proving.** If a
pin guarded provenance, re-pinning it is a lie; retiring it may be the honest answer. **Make the call and
defend it.** The four Git blobs you recorded are in your R72 handoff.

**Then prove the baseline runs:** a clean compiler build and its binary SHA-256.

### WS2 — the `kosh` reclamation, on the current compiler

Your R72 correctly refused to apply the R71 patch to a renamed compiler. **Now do it properly.** The leak is
real and measured: the growth path `mmap`s a new buffer and `munmap`s nothing — **about 15.3 bytes per
item**, with no free primitive in the language.

**Deliver:** the reclamation integrated against the **current** compiler, with a live measurement of the
mapping count across a growth sequence. **If it cannot be done without restructuring the compiler, say so
with what it would take** — do not restructure.

### WS3 — separate compilation

`yoj` is **textual inclusion**, not separate compilation — the project's largest architectural gap. Your R72
reviewed the R71 groundwork and reported the object emission NOT IMPLEMENTED.

**Deliver:** either a working two-module object emission and link, or **a concrete design with the exact
points in the compiler that must change and an honest estimate.** A design is an acceptable deliverable here;
a claim is not.

### WS4 — the old-keyword audit you did not run

Your WS5 was NOT-RUN. **Now run it.** Every place in the tree that still assumes a pre-v157 keyword — the
same class of defect has surfaced **six times** in this project (code, comments, HTML, prose, keyword
tables, teaching material), each found by a different means and **none by the gates**.

**Deliver:** the exhaustive line audit on current main, using `docs/sutram-vocabulary.html` as the list.

---

## Part 4 — Constraints

- **Least privilege**, no credentials, no new network access.
- **Read the current file from main before changing it.** A stale copy has cost this project two whole rounds.
- **Report PASS / FAIL / NOT-RUN separately** — no merged numbers.
- **Do not rewrite accepted goldens to make a failing test pass.**
- **`windows/` is shared with Claude this round** — coordinate by stating what you touched.

## Part 5 — What to return

Into `ChatGPT-to-Sarvam/`, one document per workstream. For each: what you did, the exact command, the real
output, and what you did not do.

**Your R72 was a model of honest reporting. Keep that standard** — and this round, please move at least one
workstream from NOT-RUN to PASS.

## Part 6 — One ask

In `Sutram-to-ChatGPT/ROUND-72.md` I asked for anything you need from Sarvam. **That channel stands.** If
something in the tree is blocking you, say so plainly in your delivery.
