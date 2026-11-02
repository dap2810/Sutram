# R104-00 — Muse's FIXALL patch is applied (v286), with one fix of my own to it: the recursion guard's slot is now an ordinary module global, so `--object` and `--separate` builds link byte-identical again. All 551 moved programs run the same old and new.

- **Commit on `main`:** `__SHA__` (the v285 base was `3a78e6e`).
- **Compiler: `Sutram 1.0 (v286) - sampurna sutra`** (was v285). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=273`, FAIL=0.** Library proofs 229/229, property proofs 86/86, r52 12/0, r81 24/0.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 59 PASS / 1 FAIL / 1 NOT-RUN.** The FAIL is `installer
  version` (v243 against v286); the NOT-RUN is Windows execution. **The first gate run, on Muse's patch applied
  verbatim, was 55 / 5 / 1** — four gates it broke are described below and fixed; `evidence-r104/gates-first-run-muse-patch-verbatim.txt`.
- **The guard, origin/main (v285) → v286, 683 programs** (`evidence-r104/guard.txt`):
  - **Linux ELF: 0 byte-identical, 132 refused identically, 551 DIFFER, 0 new** — every program that compiles
    differs, by design: the recursion guard is in every `mukhya` and every `prakriya`.
  - **All 551 DIFFER run old and new: 551 the same output and exit code, 0 changed** (`evidence-r104/diffrun-elf.txt`).
  - **Linux PE: 551 byte-identical, 132 refused identically, 0 DIFFER.** Windows programs are unchanged.
  - **The Windows compiler under Wine: 551 byte-identical, 132 refused identically, 0 DIFFER; its 1102 outputs are byte-identical to the Linux compiler's PE outputs.**

## WS1 - the count of each kind

You asked, for every DIFFER, whether the old behaviour was a bug or the new refusal breaks something legitimate.

| kind | count |
|---|---|
| programs whose bytes differ only by the recursion guard (same source, same output, same exit) | **537** |
| programs whose source Muse renamed (`likha(1, …)` → `dvaram_likha(1, …)`: `examples/215`, `217`, 12 `tests/stdlib`, 2 `tests/r79_real`; `lib/patra.smlib` behind them) and whose output and exit are the same | **14** |
| programs newly refused by v286 (a refusal change in the tree) | **0** |
| programs whose output or exit changed | **0** |
| old behaviour that was a bug, in the tree | **0** - none of the tree's programs hit a trap; the fixes show on the 16 probes below |
| legitimate program broken by a refusal | **0** |

The 132 refused identically are the tree's deliberate compile-fail fixtures (and `305`, R103's). One run in
`diffrun-elf.txt` ends `rc -11 -> -11`: `tests/r79_real/report_plain.sm` segfaults on both sides when given no
input, as the runner gives it; its own harness feeds it data and it passes (the `R79 real programs` gate).

**The five traps, each compiled and run on v285 and v286** (`evidence-r104/trap-probes-v285-vs-v286.txt`, 16 probes with
their sources in `evidence-r104/programs/`):

| probe | v285 | v286 |
|---|---|---|
| `likha(a, " ", b)` | ran, exit 0, printed nothing | **`E_LIKHA_TRAYA`** at compile time |
| `likha("a ", a, "\n")`, `likha(a, "\n")` | `a 7`, `7` | the same |
| `dvaram_likha(1, p, 2)` | `agyat prakriya` (no such builtin) | writes the 2 raw bytes, returns 2 |
| `likha(s == "ab")`; `yadi (s == "ab")` | `0`; the branch not taken | **`E_VARTANI_TUL`** |
| `vartani_tul(s, "ab")` | `0 1` | the same |
| `vitti u = s + t` (two strings) | `8388923` (an address sum) | **`E_VARTANI_CAT`** at 4:17 with a caret |
| `s + 1` (string plus integer: pointer arithmetic) | `ello` | the same |
| `s = "ab"; s = 5; s + 3` | `8` | the same (the mark follows the last assignment) |
| `vitti x` with no value, in a prakriya called twice | `99 99` | **`E_MULYA_VINA`** |
| `dasham d` with no value | `0.000000` | **`E_MULYA_VINA`** |
| `vitti m[4]` (a mala) | `3` | the same |
| recursion with no base case; mutual recursion | exit 139 (SIGSEGV), nothing printed | **`E_GAHANATA`**, exit 1 |
| `yog(500)`, `yog(3000)` | `125250 4501500` | the same |

**Are the five right?** The four compile-time refusals are: each replaces a silent wrong answer, each `Sanket`
names the builtin to use, and no tree program is caught. Two things to know, both stated in Reference §5a:
`vitti x` followed by assignment in both branches of a `yadi` is now refused too (Muse's blanket rule; write
`vitti x = 0`); and the string tracking is by variable, so two *parameters* compared with `==` still compare
addresses - a literal on either side is refused. The Sanskrit is Muse's and mine to the same degree:
best-effort, **native-speaker review NOT RUN.**

## What Muse's patch broke, and the fix

**Applied verbatim, the patch failed four gates: `pack messages`, `R28 linker`, `R29 separate compilation`,
`R30 module vitti`** (`gates-first-run-muse-patch-verbatim.txt`). Muse's report says "Object mode: compiles" -
it compiles, but the project's rule since R28 is that `--object` + `sutram-link` is **byte-identical** to the
direct compile, and Muse turned the guard off in object mode, so a linked program lacked it.

**The fix (`evidence-r104/claude-fix-to-muse-patch.diff`, +70 / −118 lines in `src/sutram_compiler.asm`):** the
entry-`rsp` slot is now an ordinary hidden module global, **`0gahanata`**, registered through `r56_register_global`
exactly as R65 registers the arena's `0kshetra_*` globals; `mukhya` stores `rsp` into it with an r56 relocation,
every prologue loads it with `r56_emit_global_load`, and a module object (no `mukhya`) marks it extern so
`sutram-link` resolves it to the root's. Muse's private patch list, its capacity message and its `rfx_slot_used`
flag are gone - the collision Muse hit and worked around was between their own list and the r56 globals; using
r56 itself removes the problem. **R28 237/0, R29 267 + 179 identical, R30 8/0** on the fixed build. The PE output
is still byte-identical (the guard is skipped on `target_pe`).

**`pack messages`:** 36 of the 132 pack-message goldens carry a "N bytes compiled" line, and every binary is 15
bytes longer (the `mukhya` store and the 8-byte slot): re-recorded, that line only, as in R101A
(`evidence-r104/pack-goldens-byte-count-lines.diff`). No pack changed.

**Muse's own two claims I re-measured:** the trip point - `yog(3900)` runs and `yog(4000)` refuses on v286 (Muse:
4007 / 4008 for their probe's frame); v285 ran `yog(4000)` and died at 4100. And the cost - **15 bytes in
`mukhya` and 115 per `prakriya`** (the check, the trap and its 57-byte message are emitted in every function;
one shared trap would cut it to about 20); 50,000,000 calls take the same 0.10 s. `evidence-r104/ws2-recursion-depth-size-speed.txt`.

## WS2 - the recursion limit against a legitimate deep recursion

**500 levels: fine; the limit is about 4,000 frames** (`sub rsp, 2048` per call plus the pushes, under the 8 MiB
default stack; the threshold is 8,339,456 bytes below `mukhya`'s entry). `yog(500) = 125250` and
`yog(3000) = 4501500` on both compilers; `yog(3900)` runs on v286; `yog(4000)` is `E_GAHANATA`. **The guard takes
nothing a program could have had:** v285 crashed at 4,100 without a word. The tree's deepest recursion is single
digits (Muse's census). The limit is Linux-only; on Windows the stack is 1 MB by default and the guard is not
emitted (PE unchanged) - a Windows program still segfaults where it did.

## WS3 - can a `kosh` made inside a `mandapa` die with the block, and what does the liveness table cost?

Yes, three ways; here is what each costs. None is built (you said: only after the patch lands, and answer).

1. **Unmap at block exit, the message weakens.** Each block with a `kosh` keeps a chain head (one stack slot);
   each `kosh` gets a 6th header word (the previous region) and a 7th (its mapping length); every exit site
   (`r82_emit_zero`'s: the end, `nivartanam`, `krama`/`agrim`, rewinds) walks the chain and `munmap`s. **The
   R82 check then reads unmapped memory: `E_KOSH_MANDAPA` becomes SIGSEGV** (or, if the address is reused, a
   silent read of another `kosh`). Memory for kb1: 400 MB → ~0. About 2 days. I would not build this one.
2. **Unmap all but the header page.** As 1, but `munmap(region + 4096, len - 4096)`: the header stays, the slot
   and generation are readable, **the message stays exact**. Cost: **4 KB per dead `kosh`** - which is what a
   small `kosh` costs today, so kb1 stays at 400 MB; a `kosh` of a million numbers gives back 8 MB of its 8 MB.
   About 2 days. Honest and cheap, but it does nothing for the shape the 400 MB comes from.
3. **The liveness table** (R101A's option 3): a table outside the regions, 16 bytes per `kosh` made in a block
   (its address, and its slot address or generation), looked up by address at the check. The region can then be
   unmapped whole and the message stays exact. **Costs:** the table itself (kb1: 100,000 × 16 B = 1.6 MB in place
   of 400 MB); the lookup - a hash of the address with linear probing, about 15 instructions against the check's 8
   today, on every call with a `kosh` parameter (R82 measured +11% on a call whose whole body is one read; this
   would roughly double that); a fixed capacity to choose, with a refusal when full; and the `munmap` per `kosh`
   per exit, about 10 µs each (`mmap` in kb1 measures 4.5 µs). About 4 days.

**A fourth, which I would build if the owner wants the memory back:** **reuse the region at the same
declaration.** A `kosh` declared in a block keeps its region in a hidden per-declaration global; the next entry
of the block reuses it (fresh generation, so a stale handle from the previous entry is still caught exactly:
same slot, different generation). A recursive re-entry while the region is in use takes a fresh `mmap` and
unmaps it at exit. **kb1: 400 MB → one page; the message stays exact; no table, no lookup cost; one `mmap` per
declaration site instead of per entry.** About 3 days. It does not help a program that makes many `kosh`s at
*different* sites, which no measured program does.

Today's answer, for the programmer, is unchanged: make the `kosh` once and `kosh_clear` it (0 MB), or budget the
block with `parimita`.

## Also in this commit

- Reference: §4 (`dvaram_likha` in the table), §4a (raw write rewritten), **§5a** (the three compile-time refusals,
  what still passes, what is not tracked), **§6d** (recursion depth), §20 (`dvaram_likha` is not `parikshita`).
  README: one paragraph. Changelog v286.
- Muse's 57-site rename of the raw write is in; `tests/r52` and `tests/r81_parikshita` carry Muse's new checks.

## Not done

- **Windows:** the guard is not emitted for PE; a Windows recursion still segfaults. The budget and the regions
  are Linux-only as before. Not run on real Windows.
- **The region return:** answered above, not built.
- **The installer:** v243, now against v286.
- **Native-speaker review** of the five new Sanskrit messages.
- **Open from R100:** the `2^63` literal; line positions for `E_DASHAM_VITTI`, `E_CHAKRA_DASHAM` on a variable,
  `E_DASHAM_KRIYA` on bit operators; `E_MULYA_VINA` and `E_LIKHA_TRAYA` have no line (DECL nodes carry no position).
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs' sources, `MEMORY-DECISION.md`,
  `Muse-to-Sarvam/` (the patch file stays as Muse wrote it; my change is a diff beside it).
