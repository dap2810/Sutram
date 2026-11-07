# Fix verification commands and retained evidence

Owner instruction: implement fixes, verify them, then hand off. Product code lives on `codex/windows-v309-fixes` / [draft PR #68](https://github.com/dap2810/Sutram/pull/68). The native worktree was `E:\Github_Projects\Sutram\build\windows-v309-fixes`; the ordinary main checkout remains separate. No workflow changed or full CI ran.

## Build and payload comparison

Implementation commits: `8321f843` (normalization/reuse), `ddaa7ec0` (relocated linker libraries), `4536cc36` (ordinal manifest order), `5da6318f` (expanded regression fixture only). The package was built from `4536cc36` and its unchanged engine is what the later test commit checks.

From the native worktree:

```powershell
$env:PATH='C:\Program Files\mingw64\bin;'+$env:PATH
& windows/native-installer/build-installer.ps1
```

The successful build log is [build-windows.log](build-windows.log), including the exact NASM/linker argv, detected icon resource and native `--self-test`. The builder copies the unchanged compiler/GUI/linker rather than rebuilding them. Its generated files remain local and are not added to the release branch.

Two initial builds failed at linking, first with `c:\tdm-gcc-64\bin\ld.exe`, then with the installed MinGW `ld.exe`: `cannot find -lkernel32` / `cannot find -lbcrypt`. The libraries were present beside the toolchains; the builder now adds that directory explicitly. No toolchain/dependency was installed and no global PATH was changed.

A fresh Windows worktree at `8321f843` supplies the attribute-check samples. A separate **local** Ubuntu clone supplies a real Linux payload build:

```powershell
git worktree add --detach build/windows-v309-fixes-fresh 8321f843
wsl -d Ubuntu -- git clone --no-checkout --no-hardlinks /mnt/e/Github_Projects/Sutram /mnt/e/Github_Projects/Sutram/build/windows-v309-linux-checkout
wsl -d Ubuntu -- git -C /mnt/e/Github_Projects/Sutram/build/windows-v309-linux-checkout -c core.autocrlf=false checkout --detach 8321f843
wsl -d Ubuntu -- python3 /mnt/e/Github_Projects/Sutram/build/windows-v309-linux-checkout/tools/build_installer_linux.py --work /mnt/e/Github_Projects/Sutram/build/windows-v309-linux-checkout/build/linux-payload --payload-only
```

That first comparison had all 657 file contents equal but unequal manifest ordering; the JSON is retained. After the order correction, the local Linux clone was updated and rebuilt:

```sh
cd /mnt/e/Github_Projects/Sutram/build/windows-v309-linux-checkout
git fetch origin codex/windows-v309-fixes
git -c core.autocrlf=false checkout --detach 4536cc36
python3 tools/build_installer_linux.py --work build/linux-payload-fixed --payload-only
```

The final Linux builder printed `PAYLOAD PASS: 657 files; manifest 0523ff8050787c529777727998aaffd3d1c144e2fd8ed31100c0e220b559d096`. This ran under Ubuntu/WSL, not a Windows emulation of Linux. WSL initially returned access/RPC startup errors, then started normally on retry; no service or security configuration was changed. Linux linking/Wine was not required or claimed for `--payload-only`.

The native builder was run again after the ordering fix. Then:

```powershell
python build/pin-fix-package.py
python Windows-to-Sarvam/win-v309-fixes-2026-11-07/compare-payloads.py
python tests/r130/test_installer_engine.py
python tests/r134/test_install_transaction.py
& tests/windows/test_installer_reuse.ps1
```

The package-pinning script is preserved here as [pin-fix-package.py](pin-fix-package.py), with its location-relative root adjusted for this evidence folder. It verifies all embedded files and exact engine bytes, then copies the fixed setup to `build/native-v309-fix/Sutram-Setup.exe`. `compare-payloads.py` records every compared entry, all three fresh-checkout samples and unchanged binaries. The helpers reflect the recorded local worktree/clone layout.

The 14-check fixture executes the **actual AST-extracted engine functions and publish loop** against isolated files under `build/`. It checks matching/missing/changed targets, staged reuse, edits/removal after reuse, absence of premature publication and a successful restaging retry. It does not install or change HKCU. The first expanded-fixture attempt stopped at its own path guard because the tested publish loop reused a variable named `target`; that fixture variable error was fixed and the final 14 checks passed. [Initial error](reuse-fixture-observer-error.txt), [final output](reuse-fixture-final.txt). The earlier nine-check fixture output/log are retained separately.

## Native GUI upgrade and interruptions

The preserved preparation script is historical bootstrap material, not a command to overwrite an existing evidence directory. The final committed helper files include the subsequent capture correction. All installation commands ran from the native worktree:

```powershell
& Windows-to-Sarvam/win-v309-fixes-2026-11-07/initial-install.ps1
& Windows-to-Sarvam/win-v309-fixes-2026-11-07/recovery-tests.ps1
```

`initial-install.ps1` makes a verified backup, launches the real wizard and requires Finish/engine 0. `recovery-tests.ps1` saves a working-candidate backup, vacates the canonical target by moving it aside, and runs `run-install.ps1` with the following exact name/moment pairs:

| Name | Moment |
| --- | --- |
| d1-stop | before |
| d1-retry | complete |
| d2-stop | after |
| d2-retry | complete |
| d3-stop | middle |
| d3-retry | complete |

The controller requires the D1 stop before one second/first payload file, D2's full payload plus pending record, zero D2 retry staging copies, and an exact preserved D3 edit with engine 1. After D3, it preserves that tree/transaction and restores the hash-verified candidate backup. It returned exit 0. Every phase JSON stores exact setup/child argv, PIDs/start times, observations, exit codes and closure state. Only owned handles are stopped; no name-wide kill, antivirus exclusion, service change or live-log handle is used.

After discovering another partial PrintWindow capture, an additional same-folder confirmation finished while still using the old capture helper. The edit preparation had stopped on an optional `PIL` import before changing the helper; no PIL dependency was installed. The correction uses only Windows/.NET APIs and was then exercised with another distinct phase:

```powershell
& Windows-to-Sarvam/win-v309-fixes-2026-11-07/run-install.ps1 -Name final-upgrade
& Windows-to-Sarvam/win-v309-fixes-2026-11-07/run-install.ps1 -Name capture-confirmation
```

Both completed with 657 reused files and no staging copies. Only `capture-confirmation` used the final foreground-window capture implementation. The old helper and partial image are retained; see [RECOVERY.md](RECOVERY.md). The screenshot is taken before unchecking Launch IDE and clicking Finish; the test does not launch the IDE.

## Final verification and reporting

```powershell
python Windows-to-Sarvam/win-v309-fixes-2026-11-07/installed-smoke.py
& Windows-to-Sarvam/win-v309-fixes-2026-11-07/verify-saved.ps1
python Windows-to-Sarvam/win-v309-fixes-2026-11-07/report.py
```

The smoke script records complete compile/run argv from both installed layouts. Identity rebuilds fresh PATH from the registry and compares the installed manifest and uninstaller to the pinned candidate, as well as all 657 payload hashes. The process check compares all 18 recorded PIDs and start times. Report generation reads only saved/native evidence and the preserved edit; it does not install or delete anything.

JSON/log/screenshot bytes are preserved by the local evidence attributes. A CR-aware whitespace check is appropriate for the raw Windows records. Source changes and their regression test are confined to the review branch; the main handoff is documentation/evidence only. The previous compiler tests are linked as dated evidence rather than repeated or relabelled as new runs.
