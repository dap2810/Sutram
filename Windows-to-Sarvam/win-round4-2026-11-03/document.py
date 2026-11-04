import json
from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[1]
p=root/'docs/LANGUAGE-REFERENCE.md';s=p.read_text(encoding='utf8')
s=s.replace('### Two names for one `kosh`: `vitti a = k` is not a copy (v278; on Linux the names stay one from v284)','### Two names for one `kosh`: region-backed alias stability (Linux v284; Windows Round 4 candidate)')
start=s.index('**On Linux (from v284) a `kosh` never moves**');end=s.index('\n```',start)
s=s[:start]+'''**On ELF and PE a `kosh` grows in its own 64 MiB region.** Aliases stay together while the new capacity fits `R101A_MAXCAP = 8,388,603`. Capacity doubles: for a power-of-two capacity, growth beyond 4,194,304 elements already asks for 8,388,608 and relocates. Larger initial declarations and diagnostic allocation modes also retain relocation paths. This is bounded alias stability, not a general alias-safety guarantee.

Linux uses lazy `MAP_NORESERVE`; Windows currently reserves **and commits** the entire region. The Windows candidate therefore costs 64 MiB of commit per kosh, even when almost empty. See the Round 4 MEMORY report for measured cost and the reserve/commit follow-up required before release.
'''+s[end:]
s=s.replace('prints on Linux (`examples/288`, which pins it):','prints on Linux and Windows (`examples/288`, which pins it):')
start=s.index('**On Windows the old behaviour remains');end=s.index('**What a region costs',start)
s=s[:start]+s[end:]
s=s.replace('**What a region costs (R101A, measured', '**What a region costs on Linux (R101A, measured')
s=s.replace('(Outside a block, and in\n  a Windows program, a computed negative size still gives 0.)','(Outside a block, a computed negative size still gives 0.)')
s=s.replace('- **Linux only.** In a Windows (PE) program, and in the `GUARD_PAGES` diagnostic build, a `mandapa` is an\n  ordinary block: everything works, nothing is reclaimed.', '- **ELF and PE:** scratch cursor rewind reuses storage. In the `GUARD_PAGES` diagnostic build, a `mandapa` remains an ordinary block. Windows currently commits the whole 1 GiB arena on first use; cursor rewind does not decommit it.')
s=s.replace('adds one counter update. **Linux ELF only; Windows (PE) compilation refuses `parimana()` with\n  `E_WINDOWS_SMRITI`, rather than silently returning zero.**','adds one counter update. **ELF and PE share this logical-byte accounting.** It excludes reserved address space, Windows commit charge and fallback allocations outside the arena.')
s=s.replace('- **Linux ELF only, as the block.** Windows (PE) compilation refuses `mandapa parimita N` with\n  `E_WINDOWS_SMRITI`, including blocks whose allocations would fit. An ordinary Windows `mandapa`\n  still releases nothing. Windows `kosh` growth/alias limitations in section 16 remain unchanged.', '- **ELF and PE:** the same scratch budget and nested-budget checks apply. Exceeding the limit stops before the allocation with `E_PARIMITA`, exit 1. This bounds logical scratch bytes, not OS commit or kosh storage.')
p.write_text(s,encoding='utf8')
rows=json.loads((h/'baseline-windows/native-cases.json').read_text())
failed=[r for r in rows if r['status']=='FAIL']
lines=['# Round 4 verified candidate','', 'Based on Round 3 `a01bd5bf`. Code and evidence stay on `codex/windows-round4-2026-11-03`; no main push, merge, installation or installer rebuild.','',
'| Item | Round 3 | Round 4 | Linux unchanged? |','|---|---|---|---|',
'| parimana() | compile refusal | live logical bytes; rounding/rewind probes pass | Yes |',
'| mandapa parimita | compile refusal | nested and boundary checks pass; overflow E_PARIMITA exit 1 | Yes |',
'| kosh alias | a[0]=41 k[0]=99 | a[0]=99 k[0]=99 | Yes |',
'| E_WINDOWS_SMRITI | emitted | removed after shared arena and regions passed native verification | No ELF output change observed |',
'| 220_hindi_parse_error | FAIL, missing --lang hindi | PASS with correct flag | PASS |',
'| 29_nishkriya | FAIL, raw Linux exit syscall | SKIP_LINUX_RAW_SYSCALL with explicit reason | PASS |',
'| 288_r86_kosh_alias_moves | FAIL, stale alias | PASS | PASS |',
'| Native suite | 306 PASS / 3 FAIL / 4 COMPILE_FAIL | 312 PASS / 0 FAIL / 0 COMPILE_FAIL; 3 no-expectation, 4 skips | 315 PASS / 4 no-expectation |','',
'## Sequential evidence','',
'| Stage | Windows | Linux |','|---|---|---|',
'| baseline | 306 pass, 3 fail, 4 compile failures | 315 pass |',
'| arena (experimental, kosh regions disabled on PE) | 309 pass, 4 fail | 315 pass |',
'| regions (experimental) | 311 pass, 2 fail | 315 pass |',
'| final (promoted, harness classified) | 312 pass, no failures | 315 pass |','',
'Every stage retains build commands, compiler SHA-256, timings, probe output and suite output in its platform directory. Linux returns 1 solely for four NO_EXPECTATION cases. No golden was rewritten. `arena.patch` and `regions.patch` preserve the experiments relative to a01bd5bf (PowerShell UTF-16 patch output); `finalize.py` records promotion, run with `python -X utf8`.',
'','## Exact original failures','']
for r in failed:
 lines += ['### '+r['case'],'','```json',json.dumps(r,indent=2),'```','']
lines += ['## Focused checks and limits','',
'Nine memory probes pass on both hosts; source and literal expectations are in contracts.py and programs/. Existing string/allocation contract tests: Windows 8 pass, 1 Linux-only skip; Linux 9 pass. Focused Linux gates: codegen 12, packs 33, library 229, properties 86, crash corpus 227 (see checks-linux.json). This is not a run of all 62 gates.',
'', 'The Windows harness now supplies the same Hindi flag required by the test. Test 29 contains literal Linux exit syscall bytes (`yantra`); it is explicitly skipped, not counted as passing. No compiler reinterpretation of raw assembly.',
'', '**Release limitation:** this cheapest port is functional but expensive: first arena use commits 1 GiB; each kosh commits 64 MiB. `cost-windows.json` measures private commit versus working set. Recommend reserve-only regions with incremental page commitment before shipping this as a general Windows memory implementation. No claim of complete memory safety, low-memory resilience or unbounded alias stability.',
'', 'Infrastructure retries: the first finalize.py attempt used Windows cp1252 and failed reading UTF-8 source; rerun with -X utf8 succeeded. Sandbox temporary-directory denial in Windows unittest was rerun with host permission (initial JSON preserved). WSL git could not resolve Windows worktree metadata; fixture.py restored the exact committed file bytes using Windows git before Linux library checks. No fixture or golden changes are included.',
'', 'Commands: from this worktree run `python Windows-to-Sarvam/win-round4-2026-11-03/verify.py final`, `python .../contracts.py`, `python .../cost.py` (Windows only), `python .../fixture.py` (Windows git), and `python .../checks.py`. Linux equivalents use `wsl -d Ubuntu -- python3 /mnt/e/Github_Projects/Sutram/build/round4-review/Windows-to-Sarvam/win-round4-2026-11-03/<script> [stage]`. Full expanded compiler/test argv appear in JSON evidence.']
(h/'FIXES.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
with (h/'MEMORY.md').open('a',encoding='utf8') as f:
 f.write('''
## Result and cost

The guard-only experiment worked. PE now uses the same persistent/scratch pointers and separate kosh logical-byte counter as ELF. No duplicate Windows counter was needed. Nested budgets compare prospective scratch consumption to each active lexical budget before changing the cursor. Scratch exits rewind; reused bytes are zeroed. The shared code is still pure NASM; the embedded native WinAPI adapter is unchanged.

The first investigation incorrectly described example 29 as getpid/ENOSYS. Reading the actual source corrected that: it emits raw Linux exit syscall 60 with exit code 42. FIXES.md contains the exact observed native result.

Measured on this Windows machine (single sample per process, not a benchmark): empty probe private commit 475,136 bytes; arena probe 1,076,314,112; one kosh 67,715,072; arena plus two kosh 1,210,793,984. Working sets were only about 3.7 MB. Private commit is the issue, not physical pages touched. The adapter uses VirtualAlloc RESERVE|COMMIT; these are not reserve-only regions. This cost makes the candidate unsuitable for unbounded kosh-creation workloads, even though all requested functional cases pass. Recommend a follow-up separating MEM_RESERVE from page-granular MEM_COMMIT for the arena and each kosh. A smaller arena/region is another option but lowers capacity and must change the corresponding accounting constants and documented bounds together. Neither optimization is claimed implemented here.

parimana reports logical bytes, not Windows commit, working set, reserved address space, code, stack or allocations falling back outside the 1 GiB arena. Budgets cover lexical scratch allocations, not kosh storage or allocation inside called procedures. Regions are never released to the OS. A block kosh still has program lifetime. Failed-region allocation accounting and exhaustion fallback inherit Linux limitations; real OS exhaustion has not been forced on the user's machine.

Alias stability is bounded by requested capacity, not merely current length: new capacity must be <= 8,388,603. Standard doubling from capacity 4,194,304 would exceed that bound, so that growth relocates. Oversized initial declarations and diagnostic modes retain relocation behavior. The nine focused tests establish the reported normal-path parity, not universal memory safety. A stable descriptor design or an explicit maximum-capacity refusal would be needed to eliminate that remaining shared limit.
''')
