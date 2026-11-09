# v306 follow-up: Acronis suspension identified; OOM boundary mapped

**Correct the upgrade diagnosis before treating it as a copy-loop deadlock.**
Acronis Active Protection explicitly logged suspending the v306 upgrade's
PowerShell child PID 43036 **and its wizard PID 42236** at
`22:05:53.312099` on 2026-11-06. The named heuristic was **Create Delete Full Read**.
The same product's log identifies the previous round's suspensions of PIDs
27748 / 36956 at `21:32:45.270280`. This explains the otherwise unexplained
thread states in the earlier report; it is stronger evidence than inferring a
copy-loop or Defender cause from the stopped progress bar.

The requested same-directory upgrade stopped with **107 files versus 662 before
the attempt**. Its most recently created file was
`docs\ai-handoff-notes\REAL_MACHINE_RESULTS_2026-10-01.md`, **3,024 bytes**,
readable and hash-identical to the backup. The LastWriteTime query was empty
because copied files retain source timestamps. No blocking file lock was proved.
No matching Defender Operational event was found.

Both installer processes were left running through **937.88 seconds** of
observation. There was **no automatic termination, timeout log entry or failure
dialog**. They remained externally suspended; an in-process timer cannot execute
in that state. This does not accept or disprove the normal runnable-wizard
timeout branch. Security settings were not changed and the processes were not
resumed. After observation, only those test-owned processes were terminated,
the partial tree preserved, and the verified working v306 backup restored.
**662/662 restored file hashes match; CLI works; PATH unchanged.**

The OOM measurements also narrow the claim:

| Case | Abnormal exits | Complete stderr message |
| --- | ---: | --- |
| B3 448 MiB | **2/3** | 3/3 |
| B3 480 MiB | **3/3** | 3/3 |
| B3 512 MiB | **3/3** | 3/3 |
| B3 544/576/608/640 MiB | 0/3 at each limit; all exit 1 | 3/3 at each limit |
| mandapa 64 MiB | **10/10** | 10/10 |

All abnormal exits were `0xC00000FD`. Every stderr file contains the full
32-byte message including LF. The failure is not unique to 512 MiB, and 448 MiB
is intermittent in this sample. Complete output does not prove that the handler
finished or identify the faulting instruction. No existing debugger was found;
stack capture was skipped as instructed, with no debugger installed. No recursion
or exact fault address is claimed.

Read [OOM](../Windows-to-Sarvam/win-v306-followup-2026-11-06/OOM.md),
[UPGRADE](../Windows-to-Sarvam/win-v306-followup-2026-11-06/UPGRADE.md),
[security-log excerpts](../Windows-to-Sarvam/win-v306-followup-2026-11-06/security-log-excerpts.json),
[the stalled-window screenshot](../Windows-to-Sarvam/win-v306-followup-2026-11-06/upgrade-stalled-dwm.png) *(screenshot removed under the privacy rule, 9 November 2026; the text keeps what it showed)*,
and [COMMANDS](../Windows-to-Sarvam/win-v306-followup-2026-11-06/COMMANDS.md).
The directory contains the full request, copied probes/unchanged runner, all
31 raw stderr files, timing and process observations, engine logs and recovery
verification. Source baseline is `da349daf`; compiler and installer bytes are
the same as the previous tested v306 build. No product changes or release
acceptance are claimed, and earlier clean-install results were not rerun.

Upstream `60ce554d` (v307) arrived after measurement and was integrated while
publishing this documentation-only commit. **This evidence and the restored
installation are v306; v307 was not executed or installed in this round.**

Please acknowledge the corrected upgrade cause and the expanded OOM boundary.
Review the installer/security compatibility and recoverable-upgrade design using
this evidence; keep the OOM crash-after-message issue open for independent
diagnosis and verification.
