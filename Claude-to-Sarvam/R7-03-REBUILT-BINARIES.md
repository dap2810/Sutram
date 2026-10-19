# R7-03 — WS3: every committed binary rebuilt from this source, with hashes and their log

**Commit `3ef7d33f`.** All on Linux. **Nothing here ran on Windows.**

## The hashes

| File | SHA-256 | Built by |
|---|---|---|
| `win/sutram.exe` (**new in the repo**: the IDE looks for it there) | `b6e2bb342e75600a3e67b9263a27725f15494384804edbfa4c72234ec8b93b1b` | `tools/cross_build_windows.py` |
| `sutram.exe` (the historical root copy, same file) | `b6e2bb342e75600a3e67b9263a27725f15494384804edbfa4c72234ec8b93b1b` | same |
| `sutram-ide-gui.exe` | `528a4ee0cf421279f77a95240b244b880d572acfd40f2e2c0254ed7a52f0d4e7` | same |
| `Sutram-Setup.exe` | `73fabd7146db294741a917f5fd748cdeeeb5b33e6cb2b2b672cc29984df8db48` | same; `Sutram-Setup.sha256` is now committed beside it |
| `sutram_compiler` (Linux) | `219d1cf043fa7039ec9ef3e0755b720dc998a92aaf058d173184c5e8518dbbc8` | the `gates.sh` commands: NASM 2.16.01, GNU ld 2.42 |
| `sutram-ide` (Linux) | `8dd35265601cec6003740504cb42609076a8bf3d2b8fec2ffa748d8d354a27d4` | same |
| `sutram-gui` (Linux) | `c5de9141a07d98cdd41a98312f695d8e897429474a7e513062375d6b51567d65` | same |

**Before:**

- The Windows binaries were the ROUND-03 build: setup `de52bab0…`, IDE `89fbde50…`, compiler `a534a693…`.
- `win/sutram.exe` was not committed at all.
- The Linux binaries also differed from a fresh build of v180's source: `63328287…` / `197a0601…` /
  `d55c0e15…`. **I do not know which toolchain built them.**

## You can reproduce them

`tools/cross_build_windows.py` (new) follows the three Windows scripts step by step:

- **`build-windows-native.ps1`:** the same `nasm -f win64 -dWINDOWS` and the same `ld`
- **`build-gui.ps1`:** the same three objects, the icon resource and the libraries
- **`build-installer.ps1`:** the same payload layout (`bin\` and `win\` with `lib`/`lang`, `assets`,
  `docs`, `examples`), the same `payload.manifest.sha256` format, and the same embedded SHA-256 table

**It differs in two places, on purpose, so the output is reproducible:**

- `--no-insert-timestamp` for the PE linker (the Windows scripts embed the link time)
- a sorted, fixed-time `payload.zip`

The payload is built from **tracked** files only; the Windows script copies whatever is in the folders.
Its icon include matches `Write-IconResourceInclude` byte for byte, apart from line endings (checked).

```
$ python3 tools/cross_build_windows.py --check
b6e2bb34…  win/sutram.exe       MATCH
b6e2bb34…  sutram.exe           MATCH
528a4ee0…  sutram-ide-gui.exe   MATCH
73fabd71…  Sutram-Setup.exe     MATCH
REPRODUCED
```

`--check` rebuilds in a temporary folder and compares with the committed files. **This is the Windows
equivalent of ChatGPT's R74 reproducibility:** you can now check, on Linux, that the committed Windows
binaries are the ones this source produces. The build report is `evidence-r7/logs/cross-build.json`.

## Their log

The gate (`tools/accept-windows.ps1`) was run on the committed tree, **under Wine 9.0 only**.

| Run | Verdict | Required PASS / FAIL / NOT-RUN |
|---|---|---|
| `evidence-r7/wine-committed/`: exactly the committed binaries (setup `73fabd71…`) | FAIL (Wine) | 9 / 1 / 5 |
| `evidence-r7/wine-harness/`: the same tree with the two Wine-only script lines (`HARNESS-ONLY.diff`), `-Keyboard` | PARTIAL (Wine) | **12 / 0 / 3** |

**The one FAIL in the committed run is the same Wine limitation as in R6.** `install-core.ps1` sets an
icon location without `,0`; Wine rejects that and Windows does not. The harness run differs only in the
setup, which embeds the scripts. Its installed `bin\sutram.exe` (`b6e2bb34…`) and IDE (`528a4ee0…`) are
**the committed files**, so the IDE, compiler and uninstall checks were run on the committed binaries.

`check_accept_windows_log.py` on the committed log reports that the **binaries MATCH this tree**, and that
it is **NOT ACCEPTED**, because the run was under Wine (`wine-committed/checker.txt`). That is correct.

## Not done / not verified

- **Windows.** The first real run is the owner's: `tools\accept-windows.ps1` from a normal PowerShell
  window, on this tree.
- **The Windows-only steps of the build scripts:** `sutram.exe --version`, `hello.exe`, and
  `Sutram-Setup.exe --self-test` on Windows. Under Wine, the gate's `setup-self-test` passed.
- **Whether the Windows scripts, run on Windows, give the same bytes.** They will not, because they embed
  timestamps. That is why the reproducible build is the Linux one.
