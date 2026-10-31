# R93-00 — The installer is now a gate, and it fails: the checked-in installer ships v243. `e+N` was documented; now it is explained.

- **Commit on `main`:** this round's commit (parent `7680d4c`). It adds one tool, one test, two gates, one golden, the docs changes and evidence.
- **Compiler: `Sutram 1.0 (v281)` — unchanged**, byte-identical to origin/main's (`sutram_compiler` and `sutram.exe`). Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=264`, FAIL=0** (one new golden, 296). Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 58 PASS / 1 FAIL / 1 NOT-RUN.**
  - **The FAIL is the new `installer version` gate, failing as designed:** `Sutram-Setup.exe` ships `bin/sutram.exe` and `win/sutram.exe` at **v243**, and the compiler is **v281**.
  - The NOT-RUN is Windows execution.
- **The guard, origin/main → this tree: Linux ELF and Linux PE — 674 programs, 545 byte-identical, 128 refused identically, 0 DIFFER, 1 new (296).** **NOT RUN: the Windows compiler under Wine** — its `.exe` is byte-identical to origin/main's.

## WS1 — the guard on the conversion: done in R92, the evidence is in `evidence-r92/guard.txt`

The conversion landed in R92 (`02e4c90`), and the guard you ask for was that round's work. Here it is again
in brief. With the patch alone, 26 programs compiled to different bytes. I ran every one with both compilers:
16 printed the same output and 10 changed. **Your expectation was right for 4 and wrong for 6:**

- **The refusal was right in 4:**
  - 93 and 94: `blend(1.0, 4.0)` is 2.5, which v280 truncated to 2.
  - 112: an integer `kosh` took 2.9 as 2 and 4.8 as 4.
  - `r71/conversion`: 2.75 became 2.
  - Muse counted 93 and 94; the guard found 112 and `r71/conversion` too.
- **The old answer was right in 6:** `madhava_sin` and `madhava_cos` (examples 201 and four library tests) and
  `roop_sthir` (`fmt_fixed`). These are Muse's three library sites. **The truncation there was the method, not a
  bug:** argument reduction needs `trunc(x / 2PI)`, and rounding needs the whole part.
- **What I did:**
  - I rewrote the three library functions to take the whole part as a `dasham`, then convert exactly. The
    answers are the same, bit for bit: 6000 sin/cos inputs and 3000 `roop_sthir` results compared identical
    (`evidence-r92/library-rewrite-same-answers.txt`).
  - 93, 94 and `r71/conversion` now convert a whole value, with the same goldens.
  - 112 now shows 4.8 stopping. Its golden changed; that is the rule.

On v281 itself, the guard against v280 shows 26 DIFFER. 25 print the same output, and the one that changed is
112. This round's guard is v281 → v281: 0 DIFFER.

## WS2 — `1.000000e+80`: in the reference since v279, pinned by golden 289, and now explained

**It was documented.**

- §15 has said since R87 (v279): "From 2⁶³ up it prints `d.dddddde+N` (`1.234568e+22`)".
- **Golden 289** pins `above 2^63 1.234568e+22`.
- The v279 changelog entry says it.

**But you are right that it was not explained.** A student who reads "`d.dddddde+N`" still doesn't know what
`1.000000e+80` means. §15 now has a paragraph, **"Reading `e+N`"**. It says that `1.000000e+80` is
1.000000 × 10⁸⁰ ("a 1 followed by 80 zeros"), and that the seven digits shown are the number's first seven,
rounded. It also gives a negative example and a table:

| value | prints |
|---|---|
| `3.5` | `3.500000` |
| `10000000000000.0` (10¹³) | `10000000000000.000000` |
| `9000000000000000000.0` (just below 2⁶³) | `9000000000000000000.000000` |
| 10²⁰ squared twice (10⁸⁰) | `1.000000e+80` |
| `0.0 - 15000000000000000000.0` | `-1.500000e+19` |
| `0.0000001` | `0.000000` |
| overflow past the largest `dasham` | `inf` |

**Golden 296 (`r93_float_e_notation`)** pins your exact program: 10²⁰ squared twice. It prints
`1.000000e+20`, `1.000000e+40` and `1.000000e+80`, and covers the 2⁶³ boundary, a negative and a tiny value. All
of it matches Python's `{:.6e}` / `{:.6f}`, and PE output is identical.

## WS3 — the installer as a release gate

**`tools/check_installer_version.py`**, gate **`installer version`**:

1. It opens `Sutram-Setup.exe` and finds the payload zip the wizard embeds, from its end-of-central-directory
   record.
2. It reads the `Sutram 1.0 (vNNN)` string of `bin\sutram.exe` and `win\sutram.exe` inside it.
3. It **FAILS unless both equal the compiler version** in `src/sutram_compiler.asm`.
4. It also FAILS if `Sutram-Setup.sha256` is not the file's SHA-256. That is the hash the maintainer checks
   after he downloads it.

It compares versions, not bytes. A Windows build of the compiler is not byte-identical to the Linux cross-build
in the tree (ChatGPT's v279 rebuild showed that), so a bytes check would fail every correct installer.

**Today, on the checked-in installer** (`evidence-r93/installer-version-gate.txt`):

```
FAIL installer (bin/sutram.exe v243, win/sutram.exe v243), compiler v281: bin/sutram.exe is v243; win/sutram.exe is v243 - rebuild it on Windows: windows/build-windows-setup.ps1
```

**The check is proven on eight cases.** Gate **`R93 installer gate`** (`tests/r93/test_installer_version.py`) builds
stand-in installers from this tree's `win/sutram.exe`. The checker must pass two current ones (with and without
a `.sha256`) and fail six stale ones:

- `bin` compiler one version behind;
- `win` compiler one version behind;
- a compiler missing;
- a compiler with no version string;
- a `.sha256` of another file;
- no installer at all.

8 checks, 0 failed.

**What this means:** **`gates.sh` now exits 1 until the installer is rebuilt at the current version**, and
`.github/workflows/gates.yml` (manual) will show red. That is the step you asked for. The next compiler bump
makes it fail again until the installer follows.

### The rebuild at v281 — not done here, and the hash I report is the old one

I can't build the installer in this session, for the reasons in R92: it is a PowerShell build on Windows, and a
Linux imitation would produce a different file from the one he reviews.

- **The SHA-256 of the installer in the tree is `285470a4a51c14eed7c23bd3342e068b4610f91301da1877f98fa0cfbe8c0c5b`.**
  That is the v243 package. It matches `Sutram-Setup.sha256`, so the hash half of the gate passes and only the
  version half fails.
- **To clear the gate, the maintainer runs, at this commit on Windows** (NASM and binutils `ld` on PATH):

```powershell
python tools/update_windows_manifest.py          # after reviewing the input diff (34 missing, 254 changed, per ChatGPT)
pwsh -NoProfile -File windows/preflight-windows.ps1
pwsh -NoProfile -File windows/build-windows-setup.ps1
python tools/check_installer_version.py          # must print: PASS installer v281 = compiler v281 (...)
Get-FileHash Sutram-Setup.exe -Algorithm SHA256  # record this hash; Sutram-Setup.sha256 must hold it
```

Then he commits `Sutram-Setup.exe` and `Sutram-Setup.sha256` together, and the gate passes on Linux too. The
install, IDE, upgrade and uninstall acceptance on a standard-user machine is still his step.

## Not done

- **The installer rebuild:** it needs Windows, as above.
- **The overflow `inf` policy** (R92): still open.
- **The 2⁶³ literal parse, and the line in `E_DASHAM_VITTI`** (R92): next round.
- **Not run:** real Windows.
- **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.
