# Native Windows repair evidence

Source review: [PR #67](https://github.com/dap2810/Sutram/pull/67),
`edac959a9b38238973a1921e5a93adb7794951a1`, base `e282e237`.
The owner's latest instruction authorized fixes, superseding the earlier v307
diagnostic-only instruction. Product changes remain on the review branch.
Main contains this record and logs. The main checkout subsequently advanced to
`38751cee` (v308); it is not the source of the installed repair candidate.

## Installer evidence

| Attempt | Evidence | Result |
| --- | --- | --- |
| First upgrade, CRLF payload | [record](attempt1/upgrade.json), [Acronis](attempt1/security-log-excerpts.json), [log after stop](attempt1/upgrade-after-stop.log), [DWM screenshot](attempt1/upgrade-stalled-dwm.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*, [restoration](attempt1/restore-upgrade.json) | Suspended by Acronis; recorded processes 32756 and 37664 stopped after evidence capture. 662 original files restored and verified. |
| Normalized upgrade | [record](upgrade.json), [engine log](upgrade-engine.log), [Finish screenshot](upgrade-finish.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)* | Finish 21.20 s; engine 0; 654 payload files unchanged; wizard closed after Finish. |
| Clean install | [record](clean.json), [log](clean-engine.log), [Finish screenshot](clean-finish.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)* | Finish 9.47 s; engine 0; wizard closed after Finish. |
| Interrupted install | [record](interrupt.json), [log](interrupt-engine.log) | Observer killed only its own recorded handles after 17 complete filenames at 5.70 s; pending manifest retained. |
| Recovery | [record](recovery.json), [log](recovery-engine.log), [partial screenshot](recovery-finish.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)* | Finish 8.65 s; engine 0; pending record absent; wizard closed after Finish. |

Timing is measured from clicking Install until Finish is observed; it includes
polling and UI latency and is not a benchmark guarantee. The clean and upgrade
Finish screenshots are complete. The recovery screenshot captured only a small
title-bar fragment, so it is not visual proof of that page; recovery completion
uses the recorded Finish control, engine exit/log and final manifest checks.
No live installer log
was opened by the final observer; progress for interruption came from filenames.
The independent [I/O fixture](installer-io.json) proves 100 writes while a shared
reader remains open, unchanged timestamps, successful new/replaced files,
manifest exclusion, no success leftovers, locked-target refusal with original
bytes retained, and successful retry: 9/9. A sandbox-denied replacement was
rerun outside the sandbox; no security protection was disabled.

[Payload differences](payload-differences.json) identify all 153 CRLF-only files:
1 `.txt`, 95 `.md`, 25 `.html`, 14 `.exit`, 18 `.out`. Both compilers were the
only other original differences. Normalizing those known UTF-8 text extensions
and changing MEMORY-MODEL.md leaves three differing payload files in the final
package. The fix is reproducible packaging plus unchanged-file retention, not
security software configuration. File.Replace alone did not resolve the first
attempt: Acronis also observed its internal rename/delete sequence.

[Final identity](identity.json) verifies 657/657 manifest entries, the installed
compiler hash, CLI exit 0 and a single canonical path through a fresh shell.
[Final process checks](final-processes.json) find no surviving recorded test
process. The [final security excerpt scan](security-log-excerpts.json) found no
suspension events for the four final phase process pairs in the six newest
relevant Acronis logs. This limited negative search does not establish universal
absence of protection activity. The first attempt's positive suspension record
is retained separately.

The backup and preservation paths are in [before.json](before.json),
[upgrade preservation](restore-upgrade.json) and [clean preservation](restore-clean.json).
No existing backup was deleted. Registry DisplayVersion was observed as 1.0.307.
No new IDE behavior or uninstaller acceptance was tested.

## Compiler evidence

- [OOM boundary results](oom/results.json): B3 at 448/480/512/544/576/608/640 MiB,
  three runs each; mandapa at 64 MiB ten runs; page-touch at 64 MiB; B3 at
  64/128/256 MiB and success at 768 MiB. **36/36**. Refusals have exit 1, empty
  stdout and exactly 32 stderr bytes. Success prints `100000000` and exits 0.
- [Existing OOM controls](oom-controls/results.json): **8/8**, including invalid
  stderr, successful small koshes, success at 2048 MiB, and null access retaining
  `0xC0000005` rather than being mislabeled OOM.
- [Slice checks](slices/results.json): **20/20**, including all 13 Muse r136
  programs, four typed-view escapes, recursive slice/comparator controls and
  R133 safe1 printing 0/99. Existing safe function-value behavior is retained;
  unknown function values still have no general borrow contract.
- [Native suite](native-cases.json): **322 PASS**, three NO_EXPECTATION, one
  raw-Linux-syscall skip and five side-effect/inline-assembly skips; no failure.
- [Linux first comparison](linux-first/results.json) and
  [targeted final checks](linux-final/results.json): both suite summaries 327 PASS
  / four NO_EXPECTATION, codegen 12, packs 33, library 229, properties 86, layers
  14/9/1, R23 23/0, R126 42/0, R127 26/0, R133 10/0. This is the required core
  set plus relevant slice gates, not a claim that all tools/gates.sh gates ran.

The first Linux library run had the same file_read failure in both binaries:
the fixture had CRLF. [Exact bytes before and in Git](fixture-repair.json) show
the extra CR; restoring the exact Git blob gives 229/229 in both. The initial
candidate R23 failure was a changed return diagnostic; the final code preserves
the prior diagnostic and the unchanged gate passes. The native-only invocation
of the Linux R133 harness mis-detects its extensionless output; its safe1 case is
actually executed by the native runner and the original harness passes in WSL.
No expected output or frozen baseline was rewritten.

An intermediate new OOM test incorrectly expected ten million rather than the
source's hundred million; correcting that test expectation produced the final
36/36 record above. The final candidate itself already printed the source's
correct value. [Runtime consistency](runtime-consistency.log) confirms the
generated include. Registration fault injection was NOT RUN here (the existing
v307 harness requires Wine); this is not native registration-failure evidence.

The mitigation is supported by native exit measurements, not a captured fault
stack. Microsoft's [TerminateProcess contract](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-terminateprocess)
supports self-termination without normal process teardown. Ordinary exits are
unchanged. The [ReplaceFile contract](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-replacefilew)
also has failure cases; do not generalize the locked-file fixture into a proof
of atomic crash recovery under every storage failure.

## Upstream v308 comparison

Fetched `38751cee9681a2077dd258939a3fe14b8ba8b40b` after the repair tests.
Committed `win/sutram.exe` SHA-256
`9a15a7f25b6f4825c9bca40debb53899c9f8a772b780286bed0efb5d086f81f1`:

- [Same OOM matrix](upstream-v308-oom/results.json): **36/36 pass** using upstream's
  reserve-based implementation. These are direct native generated-program runs;
  the v308 setup was not installed.
- [Variable-zero arithmetic probes](wrapper-comparison/results.json),
  [addition source](wrapper-comparison/add.sm), [XOR source](wrapper-comparison/xor.sm):
  baseline v307 and upstream v308 both compile, exit 0 and print **7/99**. The
  repair candidate refuses both with `E_KOSH_VIBHAG`. This turns the pinned static
  review's S4 prediction into an observed native failure. The repair's binary
  expression recursion is available in PR #67 for independent port/review.

The draft has intentional implementation overlap/conflicts with v308. Do not
overwrite its new journal engine or treat these v307 installation results as
v308 acceptance. Its published ownership/race findings remain outstanding.

## Build and reproduction record

[Build identity](build-identity.json) pins raw source inputs, binary hashes and
Python/Windows versions. NASM source remains authoritative. In the isolated
`build/windows-v307-fixes` worktree, the native compiler commands were:

```powershell
python tools/build_windows_runtime.py
nasm -f win64 -dWINDOWS -I./ src/r68_compiler_entry.asm -o build/fixes/candidate.obj
ld -mi386pep --no-insert-timestamp --entry=_start -o build/fixes/candidate.exe build/fixes/candidate.obj
python tools/test_v307_fix_regressions.py --compiler build/fixes/candidate.exe --phase oom --evidence build/fixes/release-oom
python tools/test_v307_fix_regressions.py --compiler build/fixes/candidate.exe --phase slice --evidence build/fixes/verified-slices
python tests/windows/test_commit_oom.py --compiler build/fixes/candidate.exe --out build/fixes/release-commit-oom
```

The native compiler used NASM from `C:\Program Files\mingw64\bin` and LD from
`C:\tdm-gcc-64\bin`. Its baseline build hash differs from the committed release
compiler; do not call them byte-identical. The candidate was copied to the
review worktree's root/win compiler paths for the unchanged native suite and
package staging only. Tracked release binaries were subsequently restored to
their exact base Git bytes and are not part of the PR.

`windows/native-installer/build-installer.ps1` staged and assembled the setup.
Both local LD choices lacked an automatic system-import-library search path,
so its first link failed. The final link used the staged object explicitly:

```powershell
& 'C:\Program Files\mingw64\bin\ld.exe' -mi386pep --no-insert-timestamp --subsystem windows --entry=_start -o Sutram-Setup.exe build/windows/setup-b065f2d784f94c21adb7a03dd51645d6/wizard.obj '-LC:/Program Files/mingw64/x86_64-w64-mingw32/lib' -lkernel32 -lbcrypt
```

The package self-test, embedded-script gates and package-version gate passed;
see [recovery source gate](test_installer_recovery.log),
[engine source gate](test_installer_engine.log), and
[version gate](check_installer_version.log). Those static checks alone were not
used as acceptance: the real wizard tests above followed them.

The recorded [helper scripts](reproduction/) were run from the review worktree's
`build/fixes/`, not from their archived evidence location. They contain absolute
paths and machine-specific preservation preconditions. They are an execution
record, not instructions to run cleanup blindly on another checkout. The UI
observer uses recorded handles/PIDs, screenshots and post-exit log preservation.
Linux commands, exact outputs and timings are in the two Linux result folders.

Final local setup: `build/windows-v307-fixes/build/fixes/review-Sutram-Setup.exe`,
SHA-256 `7ba5fdda8e373492ae272d2b0ef3cc2965287715a4503d9c11b3c02fcaf398bd`.
Installed candidate compiler:
`a95ceaf1fca6310cd8b2df0892632a38642595cdfaa53bdef7ec0736b138aa70`.
All version banners remain v307. The upstream checkout and installed candidate
are deliberately identified separately. Sarvam acknowledgement is pending.
