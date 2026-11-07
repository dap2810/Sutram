# v306 native Windows verification — 2026-11-06

**Clean installation succeeded; OOM verification failed in two reproducible cases.**
The IDE safeguard and all 322 checked native-suite cases passed. This is measured
Windows evidence, not release acceptance. No compiler, library, original example,
golden, installer, workflow or product source was changed in this round.

Tested source: `d0907ccccc500c7c98f9eec28be6326669f0a8ff`.
Owner instructions: [REQUEST.md](REQUEST.md).

| Test | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| A1/A2 preserve existing installation | Preserve files and record PATH | Original v305 backup: 662 files verified; A3 partial tree separately preserved; one canonical user PATH entry removed before A4 | PASS |
| A3 installer refuses over existing install | Refuses and names it | Same-directory upgrade started instead; stalled during copy; owner ended wizard | Expectation not met; source explicitly permits this same-directory upgrade |
| A4 clean install | Finish, no console, child exits | Finish after 8.05 s; no visible child console observed; child exited; wizard closed | PASS |
| A5 new-shell identity | One canonical path, v306 | Exactly canonical `bin\sutram.exe`; `Sutram 1.0 (v306) - sampurna sutra`; 657/657 payload hashes match | PASS |
| B1 B3 at 64 MiB | Refusal, exit 1 | Exact message on stderr, exit 1 | PASS |
| B1 B3 at 128 MiB | Refusal, exit 1 | Exact message on stderr, exit 1 | PASS |
| B1 B3 at 256 MiB | Refusal, exit 1 | Exact message on stderr, exit 1 | PASS |
| B1 B3 at 512 MiB | Refusal, exit 1 | Exact message, then `0xC00000FD`; reproduced 6/6 including initial run | **FAIL** |
| B1 B3 at 640 MiB | Refusal, exit 1 | Exact message on stderr, exit 1; repeated control also passed | PASS |
| B2 B3 at 768/1024/2048 MiB | `100000000`, exit 0 | Exact stdout, exit 0, no stderr | PASS |
| B3 mandapa at 64 MiB | Refusal, exit 1 | Exact message, then `0xC00000FD`; reproduced 6/6 including initial run | **FAIL** |
| B4 page-touch at 64 MiB | Refusal, exit 1 | Exact message on stderr, exit 1; repeated control also passed | PASS |
| C1 refused load | Clear old output and explain retained editor | Old Hello output replaced by two refusal/retention notices; editor and title retain Hello | PASS |
| C2 Save safeguard | Save held `01_hello.sm` | Edited isolated Hello copy changed; refused oversized file and all originals unchanged | PASS |
| D full native suite | 322+ PASS, no COMPILE_FAIL | 322 PASS; 3 NO_EXPECTATION; 6 explicitly skipped; no FAIL/COMPILE_FAIL/TIMEOUT; 18.606 s | PASS for checked cases |
| E natural 15-minute timeout | Installer ends stalled child automatically | Owner ended stalled wizard before any automatic result was observed; child required cleanup | **NOT VERIFIED — manually interrupted** |

The remaining OOM failure is a crash **after** the expected message. The message
alone is insufficient to count a refusal as passing. `0xC00000FD` is
`STATUS_STACK_OVERFLOW`, confirmed against the local Windows SDK `ntstatus.h`.
The failing cases were rerun serially after the suite and IDE had finished;
neither failure depends on those concurrent checks.

- [Installation, preservation and timeout limitations](INSTALL.md)
- [Exact OOM cases, outputs and repetitions](OOM.md)
- [IDE native execution and Save evidence](IDE.md)
- [Commands and reproducibility](COMMANDS.md)
- [Suite totals](suite.json), [all native cases](native-cases.json)

Installed compiler SHA-256:
`d3f3dc157baddec973947a4d5f5b1760203542b6576b11c15aab6a757f48df77`.
Installer SHA-256:
`e6006caf2bacebf378b9d3b8cd4527d63c1de6ac2e96efa630e5c268ff852e5f`.
IDE SHA-256:
`635c276b354c672925d460eaf6717c69333ed347eaa6084eda08ae6b40a55ad0`.

Sarvam: please acknowledge these results, investigate the two crash-after-message
cases, and reconcile A3's written expectation with the implemented same-folder
upgrade policy. The two already acknowledged installer gaps remain known gaps;
this report does not reclassify them as newly discovered defects.
