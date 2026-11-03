# R114-00 — `Sutram Error` is `Sutram truti`, in the compiler and all eleven packs (v294). Each pack file differs from v293 by the token and nothing else; every program that changed, changed by the token and nothing else.

- **Commit on `main`:** `c97a862` (on top of R113, `1c2db09`).
- **Compiler: `Sutram 1.0 (v294) - sampurna sutra`** (was v293). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`** (its rule moved with the token: a crash is now "no `Sutram truti` diagnostic").
- **Suite: `suite: NO-EXPECTATION=4  PASS=297  (301 run)`, FAIL=0** - 82 goldens now say `truti`.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 60 PASS / 1 FAIL / 1 NOT-RUN** (FAIL: `installer version`, `payload v243`; NOT-RUN: Windows execution). **The first run was 59 / 2 / 1:** `R28 linker` failed - my replacement had also changed the tests' expectations of the **linker's** messages, which this round leaves alone. I put those 16 lines back (`tests/r28/test_link.py`, `tests/r34/test_link_windows.py`: the linker still says `Sutram Error`); re-run 60 / 1 / 1 (`evidence-r114/gates-first-run.txt`, `gates.txt`).** - **`pack messages` passes** (WS2).
- **The guard, origin/main (v293) → v294, 707 programs** (`evidence-r114/guard.txt`):
  - **Linux ELF: 119 byte-identical, 142 refused identically, 446 DIFFER, 0 new.**
  - **Linux PE: 250 byte-identical, 142 refused identically, 315 DIFFER, 0 new.**
  - **The Windows compiler under Wine: 250 byte-identical, 142 refused identically, 315 DIFFER (the same 315), 0 new; its 1130 outputs are byte-identical to the Linux compiler's PE outputs.**
  - **Every DIFFER is the token and nothing else** (WS4).

## WS1 - the change, and the before/after you asked for

**One token, `Sutram Error` → `Sutram truti`, everywhere the compiler prints or embeds it, and identically in the
eleven packs.** The two words are both five letters, so no message moved by a byte - which is also what makes the
guard check below exact.

**Before and after, one file (`lang/hindi.sandesh`, the full diff in `evidence-r114/hindi.sandesh.diff`):**

```
-r48_msg_near	": Sutram Error [E_PARSE]: शब्द '"
+r48_msg_near	": Sutram truti [E_PARSE]: शब्द '"
```

**And for every file** (`evidence-r114/token-only-per-file.txt`) - each compared with v293 after replacing the token
in the old text: **all eleven packs differ from v293 by the token alone** (137 replacements each: 68 message values,
the 68 default-text comments that mirror them, and the header line that names the token), and so do the five
compiler sources (121 in all). Key order, key set, every translation, every `{kw:...}` and `{ver}`: unchanged.

**What moved with it, so the rule is still enforced:**

| | |
|---|---|
| `tools/sandesh.py` | the invariant token is now `Sutram truti` (its `TAGS` and its list of permitted Latin words) - a pack still carrying `Sutram Error` is refused; **a new test** says so (`tests/sandesh/test_sandesh.py`, "retired token") |
| **the Linux IDE** | `ide/sutram_gui_linux.asm` decided a compile had failed by finding the five letters `Error` in the output - it would have run a failed build. It now looks for `truti`. (`docs/WHATS-LEFT.md` C1/D2 named exactly this blocker; both marked done.) |
| goldens and tests | 82 suite goldens, 108 pack-message goldens, the negative corpus, 14 test scripts and the pack test, 19 tools - token only |
| docs | the reference, `SANDESH.md`, the vocabulary page, the specification, and the six book editions where they quote compiler output |

**Not changed, on purpose:**

- **The linker.** `sutram-link`, `sutram-elf2smo` and `sutram-coff2smo` print their own `Sutram Error` (38 strings).
  The permission names the compiler and the packs; the linker is separate binaries, one of them in the installer
  payload. It is the one place a user can still see `Sutram Error` from a current build - your call.
- **History**: round reports, the changelog's past entries, `docs/rounds/`, `docs/reports/`, the frozen snapshots in
  `compiler/`, and `MEMORY-DECISION.md`.
- **`Sutram suchana:`** - unchanged.

## WS2 - the pack gate

**`pack messages`: PASS** (12 sets × 11 cases), and `sandesh.py --check`: *"119 compiler + 23 IDE messages x 11
packs: OK"*. Last time it failed because the default changed and the packs did not; now they changed together, and
the checker changed with them.

## WS3 - the decision record

**`docs/decisions/R114-SUTRAM-TRUTI.md`**: what was authorised (the one token, compiler and all eleven packs), by
whom (the owner, 3 November, relayed in your R114 and its commit `3d60756`), and **what the exception does not
permit** - no new translation, no body rewrite, no new key, no other word, not the linker, not history, and no
precedent: the next change to a frozen pack needs its own written permission. `LANGUAGE-PRIORITY.md` (the freeze
itself) has a one-line, dated pointer to it under "it must leave the other ten exactly as they are", so the next
reader of the rule meets the exception where the rule is.

## WS4 - the guard: every change is the token

**The count you asked for: 446 programs change on Linux, 315 as Windows `.exe`s** - the ones that carry a run-time
message in their own bytes (an `.exe` carries fewer: some messages are Linux-only). I did not take "only the token"
on trust; I checked each one (`evidence-r114/verify.py`, `token-check-*.txt`):

| | checked | result |
|---|---|---|
| **each DIFFER binary** - the v293 bytes with `Sutram Error` replaced by `Sutram truti`, against the v294 bytes | ELF 446, PE 315, Wine 315 | **all equal, byte for byte**, same length (10,174 replacements in the ELF set, 3,299 in the PE set) |
| **each ELF DIFFER, run** - v293's output with the token replaced, against v294's output, and the exit code | 446 | **all equal** |
| **each refusal's message** - the guard counts a refusal as "identical" by exit code alone, so I compared the text | 142 | **all differ by the token alone** |
| the 119 / 250 byte-identical programs | | carry no run-time message |

So: **no program changed what it does or what else it prints; 446 changed one word in their messages.**

## Not done

- **The linker** (above).
- **Native-speaker review** of `truti` as the failure word (ChatGPT R183's lexicon note stands): NOT RUN.
- **Windows:** the Windows compiler under Wine, above; not on real Windows. The installer payload is still v243.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`; the packs changed by the
  one token and nothing else.
