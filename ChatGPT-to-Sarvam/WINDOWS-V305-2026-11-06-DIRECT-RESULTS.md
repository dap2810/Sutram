# Windows v305 direct execution: OOM access violation; known IDE defect remains

**Not release-accepted. No v305 installer run.** The owner-supplied direct-test
handoff was executed on native Windows build 26100 after removing the old v1.4.0
installation. Fresh persisted PATH now resolves one installed v303 compiler;
tests used the repository's explicit **v305** executable instead.

Compiler SHA-256:
`db5eda53871aafa4749d593ddef2d29e2841e3eb4d3cb7cdf680223fb45a073c`.

**New observation requiring investigation:** the unchanged B3 executable crashes
with `0xC0000005`, without stdout/stderr, under 64/128/256 MiB per-process Windows
Job commit limits. It completes 100,000,000 inserts unrestricted and under a 2 GiB
limit; B2 passes under the same 128 MiB runner. The limits are local to the test
child. This disproves graceful OOM handling for the tested Windows memory-pressure
case. `rt_veh` falls through to `EXCEPTION_CONTINUE_SEARCH` when its lazy
`VirtualAlloc(MEM_COMMIT)` fails, consistent with the result; the exact fault
instruction was not captured. No compiler fix was attempted.

**Passes:** alias follows growth, 20,000 koshes, `parimana()` 0/4096/0, budget
refusal, parameter growth (`gan=2`), `anka_akshar` B/a, literal concatenation safely
refused, the S1 call rejected, and all three exact omitted-upper-bound S2
regressions (8/2/0). The handoff's `k[1 tak]` is malformed; its syntax rejection
was not counted as proof of slice correctness.

**Full native suite:** 321 PASS, 1 COMPILE_FAIL, 3 NO_EXPECTATION, 6 SKIP.
The lone failure, `79_ayojan_cwd`, lacks compiler-relative `lib/` beside direct
`win/sutram.exe`. The byte-identical compiler with unchanged libraries in a
portable folder passes that case from an unrelated CWD. The raw suite remains
321/1; a full 322/0 rerun is not claimed.

**IDE:** Hello World executes. The known 64 KiB refusal appends its message after
the previous program's output instead of clearing it; screenshots captured.

**Cleanup caveat:** the old uninstaller removed the shared HKCU Sutram uninstall
registration. The remaining v303 compiler file was unchanged, but its installer
state was already incomplete. Account for this in the later installer round.
An unrelated Codex PATH entry missing after cleanup was restored; final PATH
comparison confirms only the old Sutram entry is removed, with machine PATH unchanged.

[Full results, environment audit, commands, and screenshots](../Windows-to-Sarvam/win-v305-2026-11-06/RESULTS.md).
Every probe and automation script is retained under the same folder on review
branch `codex/windows-v305-2026-11-06`. Product sources, goldens, and workflows are
unchanged. No CI was triggered.
