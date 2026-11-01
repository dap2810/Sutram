# R100-00 — Verdict: NO. v283 is not shippable as v1.0. Two things must change first, then a short list; ordered below.

- **Commit on `main`:** this round's commit (parent `fdaa5cd`). It contains this verdict and `evidence-r100/` only; no code.
- **Compiler: `Sutram 1.0 (v283) - sampurna sutra`**, unchanged. `sutram_compiler` SHA-256 `b7bf6d926ef8b028cf344aa57c6cc0fb902fbc0d4e17bf09f092378f887ec8de`. Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=270`, FAIL=0.** Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 58 PASS / 1 FAIL (`installer version`) / 1 NOT-RUN (Windows execution).**
  These are R95's run at `c8606ae`. Since then **no file under `src/`, `lib/`, `examples/`, `tests/`, `tools/` or `win/`
  has changed**, and neither has a binary (checked with `git diff --stat c8606ae HEAD`). So it is the same tree, not
  re-run.
- **The guard:** 680 programs, 0 DIFFER on three paths (R96). It was not re-run, for the same reason.

## WS1 — the verdict: NO, and what must change, in order

**The Linux compiler is in good shape. The release is not**, for two reasons that come before anything else:

1. **The Windows installer ships v243.** Windows is where the students are; it is the IDE and the installer.
   Every fix of the last two weeks would be missing from what they get:
   - the conversion refusal and the NaN comparisons;
   - float division by zero and the large-value printer;
   - `%` on a `dasham`;
   - the loop hang.

   A v1.0 whose installer runs a 40-version-old compiler isn't v1.0. **The gate says so, correctly.**
2. **Four silent wrong answers a first-term student will hit are still open.** I probed them on v283
   (`evidence-r100/first-term-traps-v283.txt`). Each prints something wrong, or nothing, with exit 0:

| # | program | v283 prints | why a student hits it |
|---|---|---|---|
| a | `likha(a, " ", b)` (a variable first) | **nothing at all**, exit 0 | the first way anyone prints two numbers. A non-literal first argument switches to raw write (fd, buffer, length). The reference documents it (§4, line 216), but a student won't read that |
| b | `vitti s = "ab"; likha(s == "ab")` | **0** | `yadi (naam == "Ram")` is the first string program anyone writes. `==` compares addresses |
| c | `vitti u = s + t` with two string variables, then `shabda(u)` | **8388923**, then **SIGSEGV** (exit 139) | "Namaste " + name. `+` adds the addresses. Not in the reference (R86 reported it) |
| d | `vitti x` with no value, in a function called twice, or in a loop | **`0 99 99`** / **`0 50 51`**: the previous call's value | forgetting to initialise a counter. R86 reported it. The reference says nothing |

**The order of the changes:**

1. **Rebuild the installer at v283 on Windows** (WS2 below), commit it with its `.sha256`, and pass the gate.
   Then run the standard-user acceptance: install, open the IDE, compile and run a lesson, upgrade, uninstall with
   the student's files kept. *The maintainer's step; nothing else ships without it.*
2. **Refuse (a): a `likha` of three values whose first is not a string literal.** Raw write gets its own spelling
   (`likha_fd(1, buf, n)` or the existing `likh8` family), and the library's raw writes move to it.
   *A compiler change, about a day with the guard.* The name is yours, under the vocabulary rule.
3. **Refuse (b) and (c): `==` and `+` where an operand is a string literal or a variable assigned one.** The error
   names `vartani_tul` / `vartani_cat`, the comparison and join that already exist. *About a day.*
4. **Refuse (d): `vitti x` with no value.** It is a one-line error: "give it a value". The guard will say how many
   tree programs declare without a value; I'd expect a handful. *Half a day.*
5. **A message for runaway recursion.** `f(n)` calling `f(n + 1)` with no base case dies with **SIGSEGV and no
   output**. A student who forgets the base case sees a crash, not a message. The minimum is a guard page plus a
   signal handler that prints `E_GAHANATA` (or your name for it). *It is in the runtime; two days, Linux and
   Windows separately.* This one I would accept shipping as a documented limitation, but not 2–4.

**If you ship anyway, the release notes must say these are NOT included or not fixed:**

- the four traps above (a–d);
- the recursion crash;
- `int` overflow wraps silently at run time: `4000000000 * 4000000000` is `-2446744073709551616`, and a
  factorial loop goes negative at 21!. Documented in §3a; the library's `kramgun` returns −1 instead;
- `vitti a = k` aliases a `kosh`, and after it grows the two diverge (§16);
- a `dasham` that overflows becomes `inf` and prints `inf` without a message;
- `0 of 306` library functions are `parikshita`;
- the 2⁶³ literal is read 2048 too high;
- `E_DASHAM_VITTI` and `E_CHAKRA_DASHAM` on a variable give no line;
- Windows execution is tested only under Wine here; the release is real-Windows-tested only when the maintainer does it.

## WS2 — the maintainer's commands, in order

On Windows 10 or 11, in a fresh clone at this commit, with NASM and binutils `ld` on `PATH`, Python 3, and
PowerShell 7:

```powershell
git clone https://github.com/dap2810/Sutram.git ; cd Sutram
git log -1 --format=%H                                 # note it: the release commit
Get-FileHash sutram_compiler -Algorithm SHA256         # expect b7bf6d926ef8b028cf344aa57c6cc0fb902fbc0d4e17bf09f092378f887ec8de
Get-FileHash win\sutram.exe -Algorithm SHA256          # the Linux cross-build in the tree: 6ca28a40a9334d90a6a18463bcef9e92e79f9be90b2e3a6e9b3a048f23c1419d
python tools\update_windows_manifest.py                # REVIEW `git diff windows\windows-build-integrity.sha256` first
pwsh -NoProfile -File windows\preflight-windows.ps1    # must end PREFLIGHT PASS
pwsh -NoProfile -File windows\build-windows-setup.ps1  # rebuilds win\sutram.exe, the IDE, Sutram-Setup.exe
win\sutram.exe --version                               # must print: Sutram 1.0 (v283) - sampurna sutra
python tools\check_installer_version.py                # must print: PASS installer v283 = compiler v283 (...)
Get-FileHash Sutram-Setup.exe -Algorithm SHA256        # REPORT THIS - and it must equal the line in Sutram-Setup.sha256
```

**Two hashes to know in advance:**

- **`sutram_compiler` is `b7bf6d92…ec8de`.** It is the Linux ELF in the repository, so it is byte-for-byte what he
  cloned. If his hash differs, he has a different commit.
- **His `win\sutram.exe` will not hash to `6ca28a40…`.** The build script recompiles it with his NASM and `ld`, and
  the Windows toolchain doesn't produce the Linux cross-build's bytes. ChatGPT's v279 rebuild showed that. **The
  version must match; the hash he reports is his own.**

He then commits `Sutram-Setup.exe`, `Sutram-Setup.sha256`, `win\sutram.exe`, `sutram.exe` and the regenerated
manifest together. `gates.sh` on Linux passes `installer version` on that commit, and the hash he reports is the
one the release notes print.

## WS3 — of this week's findings, how many would a first-term student have hit?

**My answer: 3 of the 5 you name. Of everything found, 6 of 11.**

This is a judgment from what a first term contains: printing, arithmetic, `yadi`, loops, functions, arrays,
strings. It is not a measurement; the project has no student programs to count. I've graded each by how
early the construct appears and how ordinary the input is:

| finding | status | first term? |
|---|---|---|
| **`dasham` stored in `vitti` truncated** (an average stored as a whole number: `vitti ausat = yog / n` with a `dasham`) | fixed v281 | **yes, very likely**: averages are week 3 |
| **`chakra` with a decimal end hangs** (`chakra i = 0 tak n / 2.0`, `tak 2.5`) | fixed v283 | **yes, likely**: "count to half of n" |
| **`vitti a = k` aliases a `kosh`** | documented, not fixed | **yes, when arrays come**: "copy the list" |
| `%` on a `dasham` gave garbage | fixed v282 | unlikely: parity checks use whole numbers |
| NaN comparing equal to everything | fixed v280 | **no**: a first-term program never makes a NaN, and division by zero now stops first |
| division of a `dasham` by zero printed `inf` | fixed v280 | yes, but it now stops |
| large `dasham` printed as a negative | fixed v279 | no: needs 10¹³ |
| `likha` split lines after a division | fixed v280 | yes, but mild |
| **`likha(a, " ", b)` prints nothing** | **open** | **yes, the most likely of all** |
| **string `==` / `+` on variables** | **open** | **yes**: names and greetings |
| **`vitti x` with no value reads a leftover** | **open** | **yes**: a forgotten initialiser |

**The three most likely, in order: (1) `likha(a, " ", b)` printing nothing; (2) string `==` and `+` on variables;
(3) a `dasham` average truncated into a `vitti`, now refused.** The first two are still open. **That is the real
release risk:** the open traps are more likely than anything fixed this week. They are why the verdict is
NO, even though the gates pass.

## Not done

- **I fixed none of (a)–(d) or the recursion crash.** You asked for a verdict and a list; the list needs your
  choice of names (for raw write, under the vocabulary rule) and your agreement to break the few tree programs
  that (a) and (d) will catch.
- **The installer:** it needs Windows.
- **Not run:** real Windows.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.
