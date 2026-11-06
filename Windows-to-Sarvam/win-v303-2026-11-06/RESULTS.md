# v303 Windows verification: STOPPED at installed command identity

**Verdict: not accepted.** The installed canonical binary is v303, but a new
`cmd.exe` resolves bare `sutram` to a different, older installation and prints
`Sutram 1.4.0`. The supplied handoff requires stopping when this version check is
not v303. Memory probes, native suite, and IDE checks were therefore NOT RUN.

The installer completion check also failed. Its engine log ends at `Copying
Sutram files.` The owner reported that PowerShell remained open and had to be
closed manually. Do not mark installation successful just because the compiler
file was copied.

## Identity and scope

- Date: 2026-11-06, native Windows build 26100, non-elevated user.
- Request: [REQUEST.md](REQUEST.md), supplied as `C:\Users\dmech\Downloads\SUTRAM-WINDOWS-V303.md`.
- Tested snapshot: `27f4fa74d22d6b246d955941b6e375a7a073c782`, the last main-history
  snapshot before v304. Its installer was introduced at `47c37912`.
- Main was already v305 at fetched commit `f1f0b2a5`. A version choice was offered;
  with no reply, the supplied v303 request was followed using an isolated worktree.
  **These observations do not constitute testing of v305.**
- Installer SHA-256: `0a278682f8333419fcdb874674910c5201e85df741b7835f77fe061845b669e0`.
- Installed compiler: `C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe`.
- Installed compiler SHA-256: `4c05d5cbad99b32be1a38459f1b4b794e00f8b34f89a662ef1ca363c92ec1603`.
  This is byte-identical to the pinned `win/sutram.exe` and agrees with R204's
  earlier static payload audit.

Direct execution of the installed compiler returned exit 0 and exactly:

```text
Sutram 1.0 (v303) - sampurna sutra
Samskrita-mukhya bhasha -> x86-64 yantra-bhasha
```

A new `cmd.exe /d /c "where sutram && sutram --version"` returned exit 0 and:

```text
C:\Users\dmech\AppData\Local\Sutram\bin\sutram.exe
C:\Users\dmech\AppData\Local\Programs\Sutram\bin\sutram.exe
Sutram 1.4.0
```

The older executable's SHA-256 is
`441db69c3bcc04576bebfc4d87b1d43a53d3b1e7497ccaeb7a00bfac6e78c2a8`.
The new command process used PATH reconstructed from the machine and user
registry values, so it did not merely inherit Codex's stale PATH. Output was
captured through pipes; no interactive terminal rendering is claimed. The
working directory contained neither installation and did not supply `sutram`.

## Requested checks

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| Installer runs | no error | Wizard automation timed out; engine log stops during copying; owner closed remaining PowerShell | FAIL / incomplete |
| `sutram --version` | v303 | Bare command prints `Sutram 1.4.0`; explicit canonical path prints v303 | FAIL |
| M1 alias across growth | `a0=99 k0=99` | Stopped at version gate | NOT RUN |
| M2 20,000 koshes | `sum=20000` | Stopped at version gate | NOT RUN |
| M3 out of memory | Sanskrit message, exit 1 | Stopped at version gate | NOT RUN |
| M4 `parimana()` | non-zero inside block | Stopped at version gate | NOT RUN |
| M5 budget | `E_PARIMITA` | Stopped at version gate | NOT RUN |
| D1 `anka_akshar(66)` and `(97)` | `B` and `a` | Stopped at version gate | NOT RUN |
| D2 `vartani_sandhi` | `abcd` or refusal | Stopped at version gate | NOT RUN |
| Native suite | same or better than 312/0 | No suite executed; no pass/fail count claimed | NOT RUN |
| IDE runs a program | output appears | Stopped at version gate | NOT RUN |
| IDE 64 KiB file | refuses AND clears output | Stopped at version gate | NOT RUN |

## Installer evidence and limits

The harness launched the real installer, accepted the license, selected the
default per-user destination, selected Add PATH, deselected the optional Desktop
shortcut, and clicked Install. It then used a bounded window-text query to wait
for Finish. The query raised `WM_GETTEXT timed out`; the harness killed its wizard
process. A subsequent process inspection found the installer PowerShell engine
still running (PID 19036, child of wizard PID 35668). The owner then reported:

> it installed but it did not do and left poweshell open in last process, i had to close it manually

The engine log records successful pre-install `--version` and `--help` checks,
removal of previous manifest-owned payload files, and `Copying Sutram files.`
It records no post-install version check or completion. The installed
`install.log` was still the old 2026-11-03 log when inspected. A complete payload,
shortcuts, associations, and installer state are **not verified**.

The automation used a hidden launch. Its two attempted installer captures were
black and are not accepted visual evidence. No IDE screenshot exists for this
run. The timeout does not by itself establish an intrinsic installer defect:
the automation and its termination contributed to the incomplete run. The
engine's underlying stall has not been diagnosed. This distinction must be
preserved when deciding what needs fixing.

## Handoff

1. Resolve the duplicate installation/PATH ordering deliberately so that a new
   terminal selects the intended compiler. No existing installation was deleted
   and no corrective PATH change was made during this report-only task.
2. Complete and observe a clean installer run, including its post-install check.
   Do not infer success from the copied compiler alone.
3. Repeat the version gate before any remaining probes. Agree on v305 or a newer
   pinned candidate for the next run; v303 has since been superseded.

Logs: [identity.json](identity.json), [installer.json](installer.json),
[install-at-stop.log](install-at-stop.log), and [COMMANDS.md](COMMANDS.md).
The review branch `codex/windows-v303-2026-11-06` retains the automation scripts
and failed captures; main receives documentation and observations only. No
compiler, library, examples, goldens, or workflows were edited. No CI run was
triggered. No `.sm` probes were generated or executed before the stop.
