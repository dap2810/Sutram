# Final Windows v309 fixes, native results and acknowledgement request

**Publication update:** main advanced again to v310 (`1cfab051`, reviewed at `8f3f97af`) during upload. Its independent C1/I2/budget fixes are preserved. This handoff and the installed candidate remain pinned to the actually tested v309 repair below; **v310 native verification is not claimed**. PR #68 is now comparison material against v310: review remaining differences (including publication safeguards, traversal-stack isolation and manifest ordering) before selectively integrating; do not merge the superseded v309 fixes blindly. The repository checkout is current through that v310 work.

**Implemented the identified fixes, rebuilt and installed the final candidate, then verified it.** [Draft PR #68](https://github.com/dap2810/Sutram/pull/68) now ends at **`7ab8c439075b91278dd0e96bf000140a0ed26cf5`**, integrating concurrent main through `3adae819` with conflicts resolved. It includes the packaging/recovery fixes and the R208 compiler-entry/ownership-read repairs. Main receives documentation/evidence only; independent Sarvam acknowledgement and acceptance are pending.

The full native validation ran at `664ff188`; the integrated head preserves identical compiler, engine, uninstaller, wizard and IDE Git bytes. Only four documentation payload files and their manifest changed. After integration, the package was rebuilt, the 14/7 native fixtures and 16/29 installer gates passed again, Windows/Linux payload equality was rechecked, and the exact integrated setup installed successfully in **22.67 s**. Read [integration proof and current machine identity](../Windows-to-Sarvam/win-v309-integrated-2026-11-07/RESULTS.md) first. The original complete recovery/IDE/compiler results remain unchanged and separately pinned below.

The owner's standing instruction is **fix issues, verify, then hand off**. Keep that workflow for subsequent Windows work. Source stays on a review branch until accepted; do not replace an authorised repair with a diagnostic-only handoff.

| Issue | Implemented and verified result |
| --- | --- |
| Windows/Linux payload mismatch | LF attributes, staging normalization and identical ordinal order; all 657 payload files and the manifest match |
| Windows linker imports | Adjacent toolchain libraries discovered; native setup build/self-test pass |
| Retry copies published files again | Late recovery reuses all 657 files with zero staging copies |
| Reused target changes/disappears | Publication refuses before moving the only copy; restaging retry tested |
| Global initializer bypass (C1) | Original compiler failed 21/42 expanded cases; repaired Windows and Linux hosts pass 42/42 |
| Validator completeness | Separate traversal stack; exhausted budget refuses; forced local/global exhaustion tested |
| Ownership snapshot before lock (I2) | Registry/discovery/state/pending reads now follow lock; 7/7 real two-process fixture checks |
| Native installer recovery | Early/late retries finish; edited-file retry refuses and preserves exact bytes; working installation restored and final upgrade finishes |
| IDE behaviour | Native Run, refused-load Save safeguard and new global compiler refusal pass; originals unchanged |
| Final machine state | Canonical v309 PATH, 657/657 installed hashes, prior 21 plus integration's 2 processes closed, no pending transaction/installer lock |

Fresh verification on this final compiler: **322 native example passes**, **7/7 arithmetic**, **32/32 native Job Object memory limits**, **59/59 slice checks** and **21/21 ownership-predicate checks**. The 42/59/21 compiler gates also pass under native Linux/WSL. Installer gates are **16/16 R130**, **28/28 R134**, plus **14/14 native reuse/publication checks**. Both installed compiler layouts compile an imported library from an unrelated directory and print 81.

Exact currently installed integration identities:

- Setup SHA-256: `ffed7a486b0b3eab86c5a76afea32bc606e6b8b24feca4d8bc546cac99c9f0d7`
- Compiler SHA-256: `bcb33e6dbb58c1e8556d29057c2f20128cc00f54e48cf860c7ea5496c0972532`
- Engine SHA-256: `b78783ddbc62a1e9676f2b34c4b40236c8046362eb2153b33e832831d12bf08b`
- Manifest SHA-256: `a534c832d00c1052e95d1d3577e2bcdb2c548bc6a3ee041d3facb5a90163943f`

Runnable setup remains at `E:\Github_Projects\Sutram\build\windows-v309-fixes\build\native-v309-integrated\Sutram-Setup.exe`; that exact candidate is installed. Earlier working, interrupted and deliberately edited trees are preserved. Generated binaries and frozen source-integrity release pins have **not** been promoted to main by this repair. Rebuild/re-pin the canonical release after independent source review, including the global-expression validation change.

Read [complete final results](../Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/RESULTS.md), [commands and provenance](../Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/COMMANDS.md), [expression entry-point audit](../Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/ENTRY-PATHS.md), [successful setup screenshot](../Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/initial-finish.png), [native IDE refusal](../Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/C3-global-refusal.png), and [process cleanup](../Windows-to-Sarvam/win-v309-final-fixes-2026-11-07/final-processes.json). The final evidence folder contains every phase record, exact commands, compiler before/after programs, raw logs, package hashes, memory-limit outputs and backup identities.

The first final-candidate recovery observer failed at screenshot capture **after the engine had completed successfully**; its records remain archived. A corrected observer completed the full recovery rerun. The process-check observer also needed a JSON-array/PID-0 fix; its initial errors remain. These are disclosed separately from product results. D2 stops after final publication, not inside a torn journal write. Timing is not a speedup claim. Complete ZIP/setup byte reproducibility, arbitrary concurrent-write safety, full IDE/uninstall acceptance, the 15-minute timeout under suspension and general security-product compatibility remain outside the verified claims. No security settings, frozen expectations or workflow triggers were changed; no full CI was launched.

Please acknowledge **PR #68 at 7ab8c439 and this final handoff**. The [consolidated index](WINDOWS-HANDOFF-INDEX-2026-11-06.md) retains all earlier handoffs, including the [earlier same-day packaging candidate](WINDOWS-V309-FIXES-2026-11-07.md). This final evidence resolves the reproduced C1/I2 findings in [the concurrent R208 review](ROUND-208-V309-ENTRY-PATH-AND-LOCK-REVIEW.md); it does not turn that review's unexecuted release gates into passes.
