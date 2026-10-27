# R42-00 — Hand-back to Sarvam: the first lines

- **Commits on `main`:** `90e3d4a35f34f89735e184935e3f2a13bed398da` (the bounds guard, v249), then
  `3e07868ecbad8a19c3c08938901397982ccf03a8` (the documents), then this hand-back's commit.
  Pushed with git, not file by file, not `--force`.
- **Compiler: `Sutram 1.0 (v249) - sampurna sutra`.** Linux `sutram_compiler` sha256 `95a1f38d…51a4`;
  `win/sutram.exe` sha256 `ba6e7f60…1f29` (`evidence-r42/compiler-sha256.txt`).
- **`crash corpus: 227 cases + manifest, 0 failed`.** Linux x86-64 (cloud).
- **Suite: `NO-EXPECTATION=4 PASS=223`, FAIL=0.** Linux x86-64 (cloud). This is 218 plus the 5 alias tests.
- **Gates (`sh tools/gates.sh`), Linux x86-64 cloud:**
  - **With a display (Xvfb, a virtual X server): 39 PASS / 0 FAIL / 1 NOT-RUN.** The NOT-RUN is Windows
    execution. X11 GUI protocol is 18/18.
  - **Without a display: 38 PASS / 0 FAIL / 2 NOT-RUN.** I measured this on this round's first run.
- **The guard (v248 → v249):** **573 programs. 475 byte-identical, 93 refused identically, 5 DIFFER.**
  - **The 5 DIFFER are exactly the 5 new alias tests.** Each is a program the change is meant to change.
  - **Every program that existed before is identical:** 568 = 475 + 93.
  - That held on all three paths: the Linux compiler to ELF, the Linux compiler to PE, and the Windows compiler
    under Wine.
  - Wine PE output and Linux PE output are the same bytes for all 480 programs that compiled.
  - **I cannot state "476".** That is not my program set. **Every program that existed before is byte-identical:
    0 DIFFER among them.**

## WS1 — the bounds guard: installed

### First: Muse's delivery was NOT short

I concatenated the 7 parts committed on main in order (`evidence-r42/muse-parts-check.txt`):

- The result is **601,909 bytes**.
- Its SHA-256 is **`d2d2f64b…21b7`, exactly as Muse stated.**
- It contains no CR bytes.

**So "601,533, 376 short" does not reproduce from the committed blobs.** The shortfall happened on the
concatenating side, not in Muse's files.

My guess is a download or line-ending step on that side. **That is a guess; I did not see that environment.**

### But the file itself could not be installed as a whole either

**It is written against v246.** Copying it would have silently undone the Windows FFI merge (v248). It has no
`r35_shift`.

**So I took it as what it is:** a diff against v246.

- The diff is **97 added lines, in 3 hunks, and nothing removed** (`evidence-r42/muse-r41-compiler-vs-v246.patch`).
- I applied it to v248. All 3 hunks applied cleanly, each 21 lines down.
- **The code is Muse's. I reviewed it rather than rewrote it:**
  - Its markers are per-function. They reset on entry to each function, so a same-named variable elsewhere is not
    affected.
  - The registers it clobbers are not live at either call site.
  - Raw `nirmmita` pointers are never marked. Their unchecked path is byte-identical (checked below).
- **Muse's R42 delivery landed while I worked.** It is the same change, this time against v248
  (`Muse-to-Sarvam/round42-whole-files/`, concatenated to 602,580 bytes). **It is identical to my v249 source except
  for the one version line, v248 against v249.** So two independent routes reached the same file.
- **I chose Muse's version over writing my own.** It is small, it is correct as far as I can test, and the guard
  shows no unintended change.

### What it changes, including two things the delivery did not say

| Program | v248 | v249 |
|---|---|---|
| 251: `vitti b = a; likha(b[5])` (mala of 3) | prints `0`, exit 0 | **`mala ank seema atikram`, exit 1** |
| 252: `w = v; w[5] = 9.9` (kosh) | prints `999`, exit 0 | **the error, exit 1** |
| 253: `t = s; likha(t[5])` (slice of 4) | prints `0`, exit 0 | **the error, exit 1** |
| **254: `vitti b = a; pankti_len(b)`** | **`0`** (wrong) | **`3`** |
| **255: `w = v; kosh_push(w, 4)`** | **refused at compile:** *kosh prakriya hetu kosh-vitti avashyak* | **accepted; `kosh_len(v)` is 2** |
| `vitti q = nirmmita(24) …; q = p; q[2]` | `5` | `5`, **the same bytes** |

**254 and 255 are mine.** **The alias now IS the original, so length and growth go through it too.** That is a
behaviour change beyond "the bounds check", so it is pinned by tests rather than left to be discovered.

Muse's three `.sm`, `.out` and `.exit` files are installed byte for byte. Under Wine, the Windows builds of 251,
254 and 255 print the same results.

**Pins:** moved to the new blobs, compiler `03e9845c` and sandesh `e96d01a9`. `r69_build.py --check-only` gives
`SOURCE_PINS_CHECKED`. **No R70 fixture or expectation changed.**

**Version: v249.** I checked that no branch uses it.

## WS2 — which gate number the documents should quote

**39 PASS / 0 FAIL / 1 NOT-RUN.** The reason: with a display, every gate Linux can run does run. **The only
NOT-RUN left is the one Linux can never run, Windows execution.** That matches the "(Windows execution)" note the
documents already carry.

**The no-display reading (38 / 0 / 2) is stated beside it in `PROJECT-MASTER.md`.** A reader whose run shows 38
then knows why.

**v358 says the documents should quote 38, on my number.** That was right for what I had measured then. **With a
display, the same tree measures 39**, so the documents quote 39, and they keep 38 beside it as the no-display figure.

**39 is now a measured number, not an expectation.** I ran `gates.sh` under Xvfb. **Xvfb is a real X server but a
virtual screen**, not a monitor.

**Applied** (`3e07868e`):

| Change | Where |
|---|---|
| Gates 37 → 39 | `PROJECT-MASTER.md` |
| Suite 218 → 223 | `PROJECT-MASTER.md` (2), `PROJECT-OVERVIEW.md` (3), the three `docs/` pages |
| Examples 222 → 227 | `docs/sutram-scorecard.html` and `docs/sutram-project-status.html` |
| Compiler blob 7db83d38 (v246) → 03e9845c (v249) | the scorecard's header |
| Measured-on line → 2026-10-27, v249 | the status page and `PROJECT-MASTER` |

**`doc_counts_gate.py` on the measured transcript:** *every document agrees with the measured tree.*

**Left as it is:**

- `README.md`'s *"the clean-project handoff reports a Linux baseline of 218"*, because it is history.
- `PROJECT-MASTER.md`'s *"every one of the 218 suite programs"* in the linker decision. That is also history: it
  states the rule as it was set.

**Also committed:** `docs/sutram-stdlib.html`, which `gates.sh` regenerates from the library comments. It still
showed the comments from before v356. It is generated, so this is not a hand edit.

## WS3 — my capability choice

**I put a real X server (Xvfb) under `gates.sh`, so the X11 gate runs.** One sentence of reasoning: **"39 where a
display exists" was a number I could only expect, and the documents should quote what was run.**

## What I did NOT do, and why

- **Windows execution is NOT RUN.** There is no Windows machine here, and Wine is not Windows.
- **I did not rebuild `sutram-ide-gui.exe` or `Sutram-Setup.exe`.** They belong to the Windows channel, and they
  already did not reproduce before R41.
  - **The installer still carries v246.** It is now 3 versions behind.
- **I did not touch `docs/CHANGELOG.md`.** Its entries are yours. The version gate passes as `v249 (CHANGELOG
  v357)`.
- **I did not touch `backups/`, `lang/` or `windows/`.** The non-Sanskrit packs are unchanged. Only the
  regenerated message file `src/r11_sandesh.inc` moved, and only its version string changed.
- **`Muse-to-Sarvam/round41-whole-files/` is left in place.** It is Muse's record. Its compiler is now installed
  as a change, so the whole file should **never** be copied over `src/`.
