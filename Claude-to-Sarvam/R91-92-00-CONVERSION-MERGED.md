# R91 + R92 — The exact-only conversion is merged. 3.7 stops, 3.0 is 3. Seven programs relied on truncation; I rewrote each, keeping the same answers. `inf` from a division is closed; `inf` from overflow is not.

- **Commit on `main`:** this round's commit (parent `1e2961a`). It contains compiler v281, ChatGPT's R161 patch unchanged, the R160 fixture, the library and test rewrites, docs and evidence.
- **Compiler: `Sutram 1.0 (v281) - sampurna sutra`** (was v280). `sutram.exe` and `win/sutram.exe` (identical, cross-built here) have SHA-256 `51bbb8ed0e83853acca52c16c554bc054ae2742a45ed45d7ca80a83bb8ec1284`. Linux x86-64 cloud, 2 cores, 7 GB.
- **`crash corpus: 227 cases + manifest, 0 failed`.**
- **Suite: `NO-EXPECTATION=4 PASS=263`, FAIL=0** (new: 294, 295; 112 re-recorded). Library proofs **229/229**. Property proofs **86/86**.
- **Gates (`sh tools/gates.sh`, Xvfb display, Linux): 57 PASS / 0 FAIL / 1 NOT-RUN (Windows execution).** The intermittent guard-page failure did not appear in either full run this round.
- **The guard, origin/main (v280) → v281: 673 programs, 517 byte-identical, 128 refused identically, 26 DIFFER, 2 new (294, 295)**, on three paths: Linux ELF, Linux PE, and the Windows compiler under Wine. The Windows compiler's 1086 outputs are byte-identical to the Linux compiler's PE outputs.

## R91 — already landed in R90, and checked again

The NaN patch and the float-division patch went in at v280 (`c494804`). **ChatGPT's six-operator fixture (R160)
is now `examples/294` and prints `0 1 0 0 0 0`**, unchanged. I renumbered it only because R90 had taken 291.
v279 printed `1 0 1 1 0 0` (R90 evidence).

## R92 WS1 — the conversion patch, merged

`ROUND-161-EXACT-FLOAT-TO-INT.patch`, SHA-256 `0aed3178…8619224`, as you quoted it, applied unchanged.
**ChatGPT's `ROUND-162-EXACT-FLOAT-TO-INT-V280.patch` (`7f33ef19…`) arrived while I pushed. I diffed it against
R161: the compiler source change is identical.** Only its two NaN/infinity test fixtures differ: they make the
values by overflow, as my port of the test already does. **So main now carries exactly the R162 patch's source.
There is nothing further to apply**, and nothing must be applied twice.

```
dasham d = 3.7; vitti i = d; likha(i) -> 'Sutram Error [E_DASHAM_VITTI]: dashama-phalam purnanka-seemayam na bhavati', exit 1
dasham d = 3.0; vitti i = d; likha(i) -> '3', exit 0
```

**Its 13-case oracle: v280 4/13, v281 13/13** (ChatGPT's Windows numbers exactly), and 13/13 in the
peephole + XMM-cache build.

The cases cover a fraction declared or assigned, an exact positive and an exact negative integer, `kosh_push`, an
integer-`kosh` store, an integer argument, `mukhya`'s return, `-0.0`, NaN, infinity, +2⁶³ and −2⁶³. I made the test
run on Linux, and its NaN and infinity now come from overflow, since dividing by zero is an error at v280.

Two more pieces of review:

- **`xmm1` is scratch at every conversion site.** A conversion happens where a value is stored, never inside a
  float expression, and the XMM cache keeps `xmm2`–`xmm5`.
- **Its error message does not reset the newline flag** that R90 fixed. `likha("a ", f(d), kosh_push(k, d), 5)`
  prints `a 415` on one line.

## R92 WS2 — the guard, and for every changed program, which answer was right

**Step 1 — the patch alone, with the library and programs as they were** (`evidence-r92/guard.txt`):
26 DIFFER. I ran every one with both compilers: **16 print the same output, 10 changed.** All 10 changed
because the program now stops with `E_DASHAM_VITTI`.

| program | old answer | new | which is right |
|---|---|---|---|
| `201_madhava_library`, `madhava_madhava_sin`, `madhava_madhava_cos`, `r18_madhava_reduction`, `r76_known_values` | correct (`sin .5 = 0.479426`) | **stops** | **OLD.** `madhava_sin`/`cos` truncated `x / 2PI` on purpose to reduce the argument. That truncation was correct, and the new rule broke it. |
| `fmt_fixed` | correct | **stops** | **OLD.** `roop_sthir` rounds by truncating `scaled`, also on purpose. |
| `93`, `94` (`vitti whole = blend(1.0, 4.0)` → 2) | 2 | stops | **NEW.** 2.5 truncated to 2 is the trap a student falls into. |
| `112` (integer `kosh` takes 2.9 → 2, 4.8 → 4) | 2, 4 | stops | **NEW**, by your rule. |
| `r71/conversion` (2.75 → 2) | 2 | stops | **NEW**, by your rule. |

**So your expectation was right for the programs and wrong for the library.** Muse's five sites are the
first two rows (3 library functions) plus 93 and 94. The guard found two more: 112 and `r71/conversion`.

**What I did with each:**

- **The library: rewritten so it gives the same answers.** `madhava_sin`, `madhava_cos` and `roop_sthir` now
  take the whole part as a `dasham`: `(m + 2^52) - 2^52` rounds a non-negative `m` below 2⁵², and they step
  down by 1 if it rounded up. From 2⁵² every `dasham` is already whole. That is exactly the old truncation, bit
  for bit. No new name was needed, so the vocabulary rule isn't touched.
  - **Checked: 6000 `madhava_sin`/`cos` inputs, from ±1.1×10⁴ to ±5×10⁹, scaled by 10⁹, and 3000 `roop_sthir`
    results give identical output with the old library on v280 and the new one on v281**
    (`evidence-r92/library-rewrite-same-answers.txt`).
- **93, 94 and `r71/conversion`:** each now converts a whole value (`blend(1.0, 3.0)` = 2.0, `x = 2.0`), and its
  comment says a fraction would stop. **Their goldens are unchanged.**
- **112:** it now shows the new rule. `2.0` is stored as 2, then storing `4.8` stops. **Its golden changed to
  `2` + the error, exit 1.** That is the rule working, not a lost test.

**Step 2 — this commit:** 26 DIFFER. I ran all 26 on ELF and PE: 25 print the same output. The other one is 112,
changed as above. The guard marks the four rewritten programs "source changed".

**Two tests the guard can't see relied on truncation too, and failed in the first gate run. Both are rewritten
to test the same thing:**

- **Property `edge30 float`:**
  - It checked `vitti s100 = madhava_sin(100.0) * 1000000.0` against −506365 (eight such values). These stay
    `dasham` now, and the check is the truncation as a range (−506366 < v ≤ −506365).
  - `vitti fbig = varna_tak_dashm("1.7e308")` is now a `dasham`.
- **Gate `R46 debug usable`:** its deliberately buggy sine had `vitti k = x / pi2`. It now calls a helper that
  takes the whole part. Nothing may follow `mukhya`, so the helper comes first, and the expected trace lines
  moved down by 11 (line 10 is now line 21). It's the same bug, found by the same trace.

## R91 WS3 — Muse's division sites, on v281

Muse's `dasham` division census found two sites (the five were the conversion sites above):

- **`examples/118`'s `madhya`** (`sarva_yog / kosh_len(a)`) can't reach the division with an empty `kosh`.
  `a[0]` stops first with `mala ank seema atikram`. The same division without the index stops with
  `E_SHUNYA_BHAJAN` on v280 and v281.
- **`289`** no longer divides by zero (since R90).

**So `inf` from a division is closed: no path prints it.**

**`inf` printed is still open, through overflow.** `dasham h = 1e20`, squared four times, prints `inf`, with no
message and exit 0 (`evidence-r92/oracles-and-cases.txt`). From v281, storing it in a `vitti` stops the
program, but printing it doesn't.

Closing it needs a check after every `dasham` `*`, `+`, `-` and `/` (overflow can come from any of them), or a
decision that printing `inf` is acceptable when the program really overflowed. **That's a policy decision, and
I'd want it before the release, as you said.** It is the remaining float item.

## R92 WS3 — the installer: I can't build it here, and here is what blocks it and what the maintainer runs

- **Blocked:** the build is PowerShell on Windows. `windows/build-windows-setup.ps1` runs four steps:
  `preflight-windows.ps1`, which checks the source manifest and runs a compiled `hello` natively;
  `build-windows-native.ps1`; `gui/build-gui.ps1`; and `native-installer/build-installer.ps1`, which uses
  `nasm.exe`, `ld.exe` and `Compress-Archive`. This session has no PowerShell and no Windows host. Rebuilding it
  with Linux tools would give a different zip and a different hash, which is not the build he reviews.
- **The manifest must be regenerated first,** after reviewing it. ChatGPT measured `windows-build-integrity.sha256`
  at 34 missing and 254 mismatched entries; the R88 move added to that. `tools/update_windows_manifest.py` is
  marked "review sources before".
- **What the maintainer runs, at this commit, on Windows with NASM and binutils `ld` on PATH:**

```powershell
git pull                                         # at this commit
python tools/update_windows_manifest.py          # after reviewing the input diff
pwsh -NoProfile -File windows/preflight-windows.ps1
pwsh -NoProfile -File windows/build-windows-setup.ps1
win\sutram.exe --version                         # must say v281
Get-FileHash Sutram-Setup.exe -Algorithm SHA256  # must match the line in Sutram-Setup.sha256
```

**The SHA-256 he must record is the one his build prints.** Expect his `win\sutram.exe` hash to differ from
`51bbb8ed…`. ChatGPT's Windows rebuild of v279 had a different hash from the cross-built one in the tree
(`eeffb701…` against `b47ea145…`), so the two toolchains don't produce identical bytes. Then comes his
standard-user install, IDE, compile and run, upgrade and uninstall. The checked-in `Sutram-Setup.exe`
(`285470a4…`) is still the old v243 package.

## Found, not fixed

- **The literal `9223372036854775808.0` (2⁶³) is parsed as the next double up, 2⁶³ + 2048.** 2⁶² parses
  exactly. This is the "long decimal literal" ChatGPT saw refused. The parser rounds wrong at the top of the
  range; it is a small fix for next round.
- **The `E_DASHAM_VITTI` message has no line number.** The emitter has no source position. The division check
  carries one, so this is doable.
- **`tests/r79_real/report_plain.sm` crashes with SIGSEGV (rc −11) when run with no input** (it reads N from
  stdin), on v280 and v281 alike. Its `mandapa` twin `report_blocks` exits 1 cleanly. It is the same before and
  after, and with its real input it passes (gate R79). I didn't investigate it this round.

## Not done

The overflow `inf` policy; the installer build, which needs Windows; real Windows; the Wine-compiler guard ran,
real Windows did not. **Not touched:** `backups/`, `Windows-to-Sarvam/`, the frozen packs, `MEMORY-DECISION.md`.
