# R109-00 — The arena branch stays unmerged. ChatGPT R178's findings, checked on main: two holes in the outlives rule were open on v290, now closed (v291). The installer gate names the payload; the suite's summary is its last line.

- **Commit on `main`:** `344fb7f` (rebased onto Muse's R105, `230561c`, and ChatGPT's R178, `5b4f0f9`; the v290 base was `7be8273`). **Arena branch:** `claude/r108-arena-review`, `0e71e54`, **not merged, not changed**.
- **Compiler: `Sutram 1.0 (v291) - sampurna sutra`** (was v290). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `suite: NO-EXPECTATION=4  PASS=289  (293 run)`, FAIL=0** (287 + two refusal goldens, 320 and 321).
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 59 PASS / 1 FAIL / 1 NOT-RUN, first run** (FAIL: `installer version` - now worded as the payload, WS2; NOT-RUN: Windows execution). R93 installer gate 11/0, R82 12/0, guard pages 5/5 controls.
- **The guard, origin/main (v290) → v291, 699 programs** (`evidence-r109/guard.txt`):
  - **Linux ELF: 558 byte-identical, 139 refused identically, 0 DIFFER, 2 new** (examples 320, 321).
  - **Linux PE: 558 byte-identical, 139 refused identically, 0 DIFFER, 2 new.**
  - **The Windows compiler under Wine: 558 byte-identical, 139 refused identically, 0 DIFFER, 2 new; its 1116 outputs are byte-identical to the Linux compiler's PE outputs.**

## WS1 - the arena branch: not merged

**Both have arrived** - ChatGPT's R178 (`5b4f0f9`) while I worked, and Muse's R105 (`230561c`) as I committed;
I rebased onto both and read them before writing this. **Muse attacked the branch fifteen ways and reports "It
held"**: every second name, store, return and field refused; exhaustion a clean error; `parimana()` exact. Its
chain probe is a chain of *readers* (`padh2` → `padh`), which the branch rightly allows. **Muse's WS2 - the attack
on R178 - is pending: R178 had not landed when Muse wrote.** So R178 has not been attacked yet. Two things are
settled anyway, and I checked both myself:

**R178 says the branch is not the design it specifies** (a stable descriptor and non-moving owner arenas; the
branch relocates slots and forbids a second name instead) **and should not be merged as it.** I agree, and I have a
measured reason on top of R178's, which is the program Muse did not find: **the branch gives a silent wrong
answer.** A block's `kosh` passed out through
a chain of 40 keeping `prakriya`s (below) compiles on the branch; after the block its slot is reclaimed, the
next block's `kosh` takes it, and the program prints **99** - the other block's number - with exit 0
(`evidence-r109/programs/chain40_reuse.sm`). That is the failure the outlives rule exists to prevent, on the one
build where memory is actually reused. It cannot be fixed cheaply on the branch alone: the fix below is in the
analysis the branch shares with main, and the branch would still be R178's "relocation plus one-name rule", not
its descriptor.

**So: leave it unmerged.** If you want the arena, the next build is R178's contract after Muse attacks it,
on a fresh branch from v291 - not this branch merged. Muse's three named prices of the branch design (a block
`kosh` gets no second name at all; growth waste counts against `parimita`, so N bytes hold about N/2 of live data;
`kshetra purnam` names no line) are worth carrying into that attack; R178 answers the first (descriptors keep
aliases) and states the second (waste is charged), and does not answer the third.

## R178's four branch findings, checked against main (v290)

R178 read the branch's source and said "test obligations, not claimed executed bypasses", and that main shares
some of the analysis. **The outlives rule on main is that analysis**, so I ran each finding against the v290
compiler on main (`evidence-r109/probes-v290-v291-branch.txt`):

| R178 finding | on v290 (main) | v291 |
|---|---|---|
| **Alias scope**: only a bare `k` is recognised | **open.** `vitti a = k` then `bahar = rakh(a)` compiled and ran past the block (`alias.sm`; `vitti b = a` too, `alias2.sm`). `a = k` into a `kosh` declared in the block was already refused - `a` is itself a block `kosh`. A ternary `rakh(c ? k : k)` is refused, by the `kosh` type check | **refused**, `E_KOSH_MANDAPA`: `vitti a = k` and `a = k` give `a` the block (example **320**) |
| **Convergence**: the fixpoint stops after 32 rounds | **open.** A chain of `prakriya`s, each passing its `kosh` to the next and the last returning it, defined in order: 32 links refused, **33 compiled and ran** (`chain33.sm`, `chain34.sm`, `chain40.sm`, `chain120.sm`) | **refused** - the fixpoint runs until nothing changes (each round marks a parameter or ends, so at most 128 × 6 + 1 rounds; the 120-link chain compiles in 0.00 s). Example **321** |
| **Traversal truncation**: the walk's stack silently drops nodes at 65,536 | the same code on main; **not reached** by any program I could write (the source limits come first) | a walk that overflows counts the parameter as **keeping** |
| **Silent fallback**: a 257th open block `kosh` goes unrecorded | the same on main; **not reachable** - a function holds at most 256 variables (`VAR_TABLE_CAP`), so the variable table refuses first (`vitti-suchi seema atikram`) | a full table **refuses** (`mandapa-kosh-suchi seema atikram`) |

**On main the two open holes were a broken promise, not a memory error:** main does not reclaim a block's `kosh`,
so the escaped reference read valid data (`11`). But R108-00 told you *"no reference to a block's `kosh` can
now outlive its block"*, and that was false for those two shapes. It is true now, for every shape I tried.

**The controls do not move:** an alias given to a reader (`padh(a, 0)`, `kosh_len(a)`), an outer `kosh` aliased
inside a block and given to `rakh`, and a 120-link chain of readers compile to the same sizes and print the same
on v290 and v291. The guard: 0 DIFFER on all three paths; nothing in the tree used either hole.

**Not changed this round:** nothing of R178's design (the descriptor, owner arenas, the accounting rules) is built
- that waits for Muse, as you said.

## WS2 - the installer gate names the payload

**You were right that the old message pointed at the wrong file, and the premise needs one correction too:
`Sutram-Setup.exe` is not "v290".** The wizard itself carries no version string at all - I searched every byte
outside the payload - and the matching `Sutram-Setup.sha256` proves only that the hash file belongs to this
`.exe`. The only versions in the installer are its payload's two compilers, packed **2026-10-21**. So the honest
message is not "payload v243, installer v290", it is this (the gate's last line, `tools/check_installer_version.py`):

```
FAIL payload v243 inside Sutram-Setup.exe (the wizard has no version of its own); compiler v291, packed 2026-10-21; 108 of its 138 lib/lang files differ from the tree: bin/sutram.exe is v243; win/sutram.exe is v243 - rebuild the payload on Windows: windows\native-installer\build-installer.ps1 (docs/INSTALLER-REBUILD.md)
```

The gate's line in `gates.sh`: `installer version  FAIL  payload v243 inside Sutram-Setup.exe (the wizard has no
version of its own); compiler v291, ...`. **New: the library and language files.** The payload's `lib/` and
`lang/` files (in `bin\`, `win\` and the root) are compared with the tree's, CR/LF ignored: **108 of 138
differ.** So it is not only the compiler that is stale. If a wizard ever does carry a version, the line says
`the wizard says vNNN`. The R93 gate tests both wordings (11 checks, 0 failed; was 9).

**The command and the hash** (`docs/INSTALLER-REBUILD.md`, the whole procedure). In `cmd.exe` at the repository root:

```
git pull
win\sutram.exe --version
certutil -hashfile win\sutram.exe SHA256
powershell.exe -NoProfile -ExecutionPolicy Bypass -File windows\native-installer\build-installer.ps1
```

| | expected |
|---|---|
| `win\sutram.exe --version` | `Sutram 1.0 (v291) - sampurna sutra` |
| `win\sutram.exe`, before | **`324b31da0edbacc2863166fcc5c9485280a01ac3df0622b36c11a7126df2ac28`** |
| `payload\bin\sutram.exe` and `payload\win\sutram.exe` in the staging folder the script prints, after | **the same, `324b31da…2ac28`** |
| `Sutram-Setup.exe` | equal to the first field of `Sutram-Setup.sha256`, which the script writes - **not predictable** |

Two things to know:

- **Run the installer step, not `BUILD-WINDOWS-SETUP.cmd`.** The full build first re-links `win\sutram.exe` on
  Windows without `--no-insert-timestamp`, which overwrites the guard-verified binary with one of different
  bytes and a hash nobody can predict. `build-installer.ps1` copies the tree's `win\sutram.exe` unchanged, so
  the payload compiler's hash is the one above.
- **`Sutram-Setup.exe`'s own hash cannot be given in advance:** `Compress-Archive` stores file times in the zip
  and the wizard's link stamps the time. The payload compilers are the fixed point; the setup hash is checked
  against the file the build writes.

Then commit `Sutram-Setup.exe` and `Sutram-Setup.sha256`; on Linux the gate should say `PASS payload v291 =
compiler v291 (... 0 of its N lib/lang files differ ...)`. **It goes stale again at the next version bump** - and
this round is one (v290 → v291), so the hash above is the v291 one.

## WS3 - the test runner

**Reproduced: the summary line was printed first and the failure details after it**, so a run ended with the
last no-expectation program's raw output - `219_sanskrit_kosh_aliases` prints `1 7 7 1`, one number a line.
That is what you saw. Now (`evidence-r109/suite.txt`):

```
--- 219_sanskrit_kosh_aliases: NO-EXPECTATION - no golden, not counted as passing; its output (4 line(s)) is not checked:
    | 1
    | 7
    | 7
    | 1

suite: NO-EXPECTATION=4  PASS=289  (293 run)
```

The details come first; every line of a program's output is indented and marked `|`, at most five lines for a
no-expectation case; **the summary is the last line**, labelled `suite:`, with the number run. The three tools that
read it (`tools/gates.sh`, `tools/doc_counts_gate.py`, `tools/guard_page.py`) now read **only the last line** - a
program printing `PASS=` in a failure detail can no longer be counted as the result. (`guard_page.py` also counts
`COMPILE-FAIL` on purpose now; before, it counted it only by accident of the regex.) The exit code is unchanged:
1 while any case has no expectation, as the gate's note says.

## Not done

- **The arena merge:** not done, and I recommend it is not done (WS1).
- **R178's design:** not built - Muse's attack on it (R105 WS2) is still pending.
- **The payload rebuild:** needs Windows - NOT RUN. **Native-speaker review** of the new capacity message
  `mandapa-kosh-suchi seema atikram`: NOT RUN.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs' sources, `MEMORY-DECISION.md`, `Muse-to-Sarvam/`.
