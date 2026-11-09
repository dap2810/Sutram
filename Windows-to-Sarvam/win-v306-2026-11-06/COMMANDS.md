# Commands and reproduction

Working directory: `<repo>`; Windows PowerShell, normal user.
Fetched origin and fast-forwarded main to the tested source
`d0907ccccc500c7c98f9eec28be6326669f0a8ff` before verification:

```powershell
git fetch origin
git merge --ff-only origin/main
git rev-parse HEAD
& .\Windows-to-Sarvam\win-v306-2026-11-06\preserve.ps1
& .\Windows-to-Sarvam\win-v306-2026-11-06\install.ps1 -Phase a3
```

The exact initially loaded A3 observer/helper versions are archived as
`install-a3-loaded.ps1` and `ui-helper-a3-loaded.ps1`. While A3 was running, the
working observer gained additional error-dialog/timing capture for A4; the
archived A3 versions preserve what was actually loaded. These are observation
scripts, not replacements for installer source.

The owner's Task Manager intervention is recorded separately. After observation
ended, the following script closed only the verified orphan child, moved the
partial folder aside, removed the canonical user PATH entry and ran clean A4:

```powershell
& .\Windows-to-Sarvam\win-v306-2026-11-06\clean-install.ps1
python Windows-to-Sarvam/win-v306-2026-11-06/identity.py
```

Filesystem/GUI operations outside the workspace used approved tool escalation;
the installer script explicitly rejects an Administrator token. The fresh-shell
test passed before B/C/D were started.

```powershell
python Windows-to-Sarvam/win-v306-2026-11-06/probes.py
python Windows-to-Sarvam/win-v306-2026-11-06/suite.py
& .\Windows-to-Sarvam\win-v306-2026-11-06\ide.ps1
python Windows-to-Sarvam/win-v306-2026-11-06/repeat_oom.py
```

The first two Python commands were launched concurrently. `probes.py` returned
exit 1 for the two observed OOM failures. `suite.py` returned exit 0 after 18.606 s.
The IDE returned success. The repeat command ran after all three had completed
and returned exit 1, reproducing the two abnormal exits five times each.

`suite.py` executes the original `tools/test_windows_native.py` without changing
its inputs or overriding its compiler-selection behavior. The root and `win/`
compilers have the same SHA-256 as the installed compiler. `79_ayojan_cwd` uses
the root compiler with adjacent `lib/`, as the v306 harness specifies; it passed
with stdout `81\n` from the unrelated build working directory.

All generated executables and temporary Save-test files remain under `build/`
and are not uploaded. All three `.sm` probes, the unchanged Job runner, diagnostic
scripts, JSON results, original request, engine logs and screenshots are included
in this evidence directory. Do not blindly rerun preservation/installation
scripts over the completed installation: they deliberately reject existing backup
destinations. The OOM and suite commands are sufficient to reproduce their results
against the pinned compiler bytes.

No GitHub Actions run was launched and no workflow file was edited.
