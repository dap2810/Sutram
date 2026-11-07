"""Derive reports from the saved native observations, without rerunning tests."""
from pathlib import Path
import hashlib,json,collections,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def read(name):return json.loads((HERE/name).read_text(encoding='utf-8-sig'))
def write(name,text):(HERE/name).write_text(text,encoding='utf8',newline='\n')
candidate=read('candidate.json');initial=read('initial.json');identity=read('handoff-identity.json')
expr={r['name']:r for r in read('expressions/results.json')['cases']};supp=read('supplemental/results.json')
nest=read('nesting/results.json');suite=read('native-cases.json');counts=collections.Counter(r['status'] for r in suite)
c1=read('ownership/c1-suffix-result.json');c2=read('ownership/c2-result.json');c3=read('ownership/c3-result.json');c4=read('ownership/c4-unequal-existing-result.json');ordinary=read('ownership/ordinary-result.json');processes=read('final-processes.json')
assert identity['pass'] and processes['all_owned_processes_closed'] and not processes['installer_lock_exists']
assert counts['PASS']==322 and not any(counts[k] for k in ['FAIL','COMPILE_FAIL','TIMEOUT'])
assert c1['owned_copies_after'] and c2['pass_'] and c3['edit_survived'] and not c4['owned_copies_after'] and ordinary['exit']==0
assert all(r['compile']['exit']==1 and not r['output_exists'] and r['pass_'] for r in supp[:2])
# Initial optional scoring was overly narrow. Preserve it and classify explicitly,
# rather than silently changing raw evidence or treating valid local binding as a bug.
classified={}
for name,r in expr.items():
    if name=='local-direct':
        run=supp[-1]['run'];ok=r['compile']['exit']==0 and run['exit']==0 and run['stdout']=='7\n';note='Valid local kosh binding, positive control; initial optional refusal expectation was wrong.'
    elif name in ['add','xor']:
        ok=r['compile']['exit']==1 and not r['output_file_exists'] and '[E_VIBHAG_ANKA]' in r['compile']['stdout'];note='Exact slice-specific refusal is valid; initial generic kosh-only scorer was too narrow.'
    else:ok=r['pass'];note='Original observation/expectation retained.'
    classified[name]=dict(pass_=ok,note=note)
write('expressions/classified-verdicts.json',json.dumps(classified,indent=2)+'\n')
assert all(r['pass_'] for r in classified.values())
# Journal is append-only. Recover exact historical prefixes from the retained final
# transaction, accepting a prefix only when its hash equals the earlier snapshot.
saved=read('restore-after-c4.json');finaljournal=(Path(saved['preserved_transaction'])/'journal.txt').read_bytes()
for name in ['c1-unmodified-interruption','c1-suffix-before','c1-suffix-after','c4-unequal-existing-before','c4-unequal-existing-after']:
    wanted=read('ownership/'+name+'.json')['transaction']['journal.txt']['sha256'];h=hashlib.sha256();prefix=b''
    for line in finaljournal.splitlines(keepends=True):
        h.update(line);prefix+=line
        if h.hexdigest()==wanted:
            (HERE/'ownership'/(name+'-journal.txt')).write_bytes(prefix);break
    else:raise RuntimeError('Cannot recover exact journal '+name)

text='# v310 global initializers and syntax probes\n\n'
text+='Exact compiler/version/hash: [candidate.json](candidate.json). Sources, argv, exit codes, timings, stdout/stderr and output existence: [raw results](expressions/results.json).\n\n'
for name in ['global-direct','global-add','valid-global','two-globals-no-main','record-literal','default-argument']:
    r=expr[name];text+=f"## {name}\n\nCompile exit `{r['compile']['exit']}`; executable produced: `{r['output_file_exists']}`. Exact compiler output:\n\n```text\n{r['compile']['stdout']}{r['compile']['stderr']}```\n\n"
    if 'run' in r:text+=f"Native output: `{r['run'].get('stdout','').strip()}`, exit `{r['run'].get('exit')}`.\n\n"
text+='''## Meaning and controls

Both requested unsafe globals refuse with exit 1 and no executable; the valid global prints 7.
All three literal A2 snippets give syntax errors. However, the two-global snippet fails at end-of-file because it lacks `mukhya`, **not because two globals are forbidden**. Adding `mukhya() { likha(a + b) }` compiles and prints 3. It does not establish a new unchecked path: globals are the path this release now validates. These snippets do not prove class-wide closure.

The supplied default-argument example fails at `vitti`, before the default value. The additional `f(n = 5)` control fails at `=` (exact output in [supplemental results](supplemental/results.json)), directly exercising that syntax.

Local addition of a returned kosh refuses with `E_KOSH_GANIT`. Direct local kosh binding is supported and prints 7; the initial optional probe wrongly expected refusal. Likewise, the initial arithmetic scorer accepted only generic kosh diagnostics and incorrectly marked the valid `E_VIBHAG_ANKA` refusals false. Raw records are unchanged. [Classified verdicts](expressions/classified-verdicts.json) explain these three harness expectation corrections; none is concealed as a product failure or rerun success.
'''
write('INITIALIZER.md',text)
write('BUDGET.md',f'''# v310 native nesting boundary

Balanced program: `mukhya() {{ likha(` + `(` repeated N + `1` + `)` repeated N + `) }}`.
N counts **additional pairs inside `likha(...)`**, excluding the call's parentheses.

Tested every integer N from 0 through 1023, increasing exactly one level per compile: **1024 probes**.
N=0..1022 compile with exit 0. N=1023 refuses with exit 1, no executable, empty stderr, no timeout or crash:

```text
{nest['boundary']['compile']['stdout']}```

The N=1022 executable runs with exit 0 and prints `1`. Each compiler process had a 15-second deadline.
This exercises the parser nesting guard; it does **not** trigger or prove the expression walk's 200,000-visit budget. No budget-exhaustion experiment was run, as requested.

[Every source and raw command/output](nesting/results.json), [last compiling source](nesting/depth-1022.sm), [first refusal](nesting/depth-1023.sm), [generator](compiler-probes.py).
''')
write('ARITHMETIC.md','''# v310 arithmetic refusals

Both the brief's add/XOR wrappers and the original preserved v307 reproductions refuse with exit 1 and produce no executable. Exact diagnostic for all four:

```text
'''+supp[0]['compile']['stdout']+'''```

The valid `pankti_gan(k[0:2])` control compiles, exits 0 and prints `2`.

[Brief cases and control](expressions/results.json); [original add/XOR sources and commands](supplemental/results.json). These are new v310 executions, not recycled v309 counts. See INITIALIZER.md for the disclosed initial scorer correction.
''')
manifest={r['file'].replace('\\','/'):r['expected'].lower() for r in candidate['checks']}
c2after=read('ownership/c2-after.json')['target'];c2matches=sum(c2after[n]['sha256']==h for n,h in manifest.items());assert c2matches==657
ordinary_diff=ordinary['diff'];disappeared='\n'.join(f"- `{r['file']}`: SHA-256 `{r['sha256']}`; same bytes after retry: {', '.join('`'+p+'`' for p in r['copies_after']) or 'NONE'}." for r in ordinary_diff['disappeared']) or '- None.'
write('OWNERSHIP.md',f'''# v310 native installer ownership

**C4 FAIL: unequal existing superseded content causes loss of the target's prior bytes in a controlled recovery fixture.** Ordinary interrupted recovery succeeds. No user file was used as the loss probe; its sentinel bytes are retained in this evidence folder, and whole installations/transactions were moved aside before restoring the baseline.

All engine tests execute the **complete, unchanged `install-core.ps1` embedded in the pinned setup**, with its exact embedded ZIP, at the real canonical per-user destination. C2 uses two engine processes rather than two wizard windows. Initial installation and both controlled interruptions use the actual setup GUI. No mocked filesystem/registry, edited engine, security changes, or forced resume of suspended processes.

## C1 — suffix preservation

The real clean install was interrupted after `{read('c1-stop.json')['payload_files_present']}/657` target files appeared, while a later compiler was still staged. The untouched clean interruption had no superseded directory: there was no old target to supersede. Absence alone is not a passing test.

To exercise replacement, the test seeded a known intermediate payload at `docs/BUILDING.md`, recorded its complete hash in a `STAGED` journal entry, and supplied an older backup. These are explicit synthetic owned transaction inputs. The actual engine moved those intermediate bytes to:

`{c1['owned_copies_after'][0]}`

Full preserved hash: `{c1['owned_sha256']}`. The filename's suffix is the first 12 uppercase hex characters. C1 passes for this fixture.

A read-only, non-delete-sharing handle on the later staged `win/sutram.exe` deliberately stops its final rename. Exit 1 is expected fixture control, preserving transaction evidence before commit cleanup. It is not an unexplained installer failure.

## C2 — concurrency and fresh state

Two actual embedded-engine processes launched `{c2['launch_gap_seconds']:.6f}` seconds apart. One completed with exit 0; the other refused with exit 1:

```text
{c2['lock_message'][0]}
{c2['completion'][0]}
```

After both exited: **657/657 payload hashes match**, no target pathname disappeared, and no pending transaction remained. Only installation log/journal/state metadata changed. [Raw process results and comparison](ownership/c2-result.json), [first log](ownership/c2-first-engine.log), [second log](ownership/c2-second-engine.log). The recorded process seconds are observation upper bounds because the controller collected the first process before the second; they are not individual exit timestamps. This proves the concurrent-start case, not every possible arbitrary-writer race or delayed state-read interleaving.

## C3 — edit during publication

During a clean run, after `docs/BUILDING.md` appeared but before the final compiler was published, the observer appended a unique line. It recorded the engine still running, the later target absent, and its staged copy present. The engine completed with exit 0; the edit survived exactly:

`{c3['after_sha256']}`

[Edit bytes and observation](ownership/c3-result.json), [engine log](ownership/c3-edit-engine.log). This is the requested already-published-file case. It does not prove protection against an edit between a target's hash check and its rename/delete. The edited installation was preserved as a whole and a verified baseline restored before further testing.

## C4 — unequal superseded copy

Using the same interrupted transaction, the test installed a different journal-owned sentinel as the target and precreated its expected 12-hex-prefix backup name with **different bytes**. No hash collision is required: a filename can contain any prefix.

- Target before retry: `{c4['owned_sha256']}`.
- Existing superseded file before/after: `{c4['superseded_after_sha256']}`.
- Target after retry: `{c4['target_after_sha256']}` (new payload).
- Copies of the original target hash anywhere in the installed tree or transaction afterward: **0**.

The unchanged engine journals `SUPERSEDED`, deletes the target because the named backup exists, and publishes the new file. It subsequently stops at the deliberately locked later compiler. Thus the loss is observable **before commit cleanup**. No equality-mismatch warning occurs; the only error is the intentionally blocked later rename.

The vulnerable statement is `windows/native-installer/install-core.ps1:604` at source `{candidate['source_commit']}`. [Fixture inputs](ownership/c4-unequal-existing-fixture.json), [before/after hash inventory and result](ownership/c4-unequal-existing-result.json), [actual log](ownership/c4-unequal-existing-engine.log), [journal](ownership/c4-unequal-existing-after-journal.txt), [sentinel bytes preserved outside the installation](ownership/c4-unequal-existing-owned-before.txt).

**Pathname-only comparison would miss this defect:** no target pathname disappears in either seeded fixture, because the deleted path is replaced. Content-hash comparison finds the lost bytes. C1 preserves its old hash; C4 does not. The fixtures demonstrate a reachable engine branch under seeded recovery state, not spontaneous loss during the unmodified ordinary retry.

## Every disappearance in ordinary recovery

A separate unmodified clean install was interrupted after `{read('ordinary-stop.json')['payload_files_present']}/657` files, then retried successfully (engine exit 0, observed `{read('ownership/ordinary-retry.json')['seconds']:.3f}` seconds). Target inventory before/after reports:

{disappeared}

No other target pathname disappeared; `{len(ordinary_diff['changed'])}` preexisting target files changed bytes. Final installed payload verification is **657/657**. [Ordinary complete inventory diff](ownership/ordinary-diff.json). The pending record's removal is expected completion, and its bytes are the installed manifest.

## Reproduction and recovery

`ownership.py` plus `ownership-controller.ps1` record all argv, process exits, fixture data, complete target/transaction inventories and hashes. The five earlier fixture journals were recovered as exact prefixes of the retained append-only journal; each prefix's full SHA-256 was verified against its contemporaneous inventory. They are not reconstructed from guessed events.

Use a dedicated test installation or preserved backup when reproducing. Keep the fixture's non-delete-sharing handle until the engine exits; otherwise normal commit cleanup removes its backups. The final working installation is v310 with matching package/manifest/uninstaller hashes, one fresh-shell PATH entry, no pending transaction and all 12 recorded installer/wizard processes closed.

Requested next change for Sarvam: eliminate deletion based on an existing prefix-name. Prefer moving to a fresh unique backup and preserving both copies; a full-hash-then-delete check alone still has a writer race. Independently reproduce and fix in a review branch, then rerun these native cases on the exact rebuilt artifact. This round's brief explicitly prohibited product changes, so **no repair or release acceptance is claimed** here.
''')
write('RESULTS.md',f'''# v310 native Windows verification — 7 November 2026

**Completed the requested verification. Release acceptance is not granted: C4 reproduces a recovery data-loss defect with controlled test bytes.** Compiler/library/examples/goldens/installer sources and shipped binaries were not changed. The specific [v310 brief](REQUEST.md) overrides the standing repair workflow for this verification-only round.

Tested source: `{candidate['source_commit']}`. Native version:

```text
{identity['version']['stdout']}```

| Artifact | SHA-256 |
|---|---|
| Setup | `{candidate['setup_sha256']}` |
| Compiler | `{candidate['compiler_sha256']}` |
| Embedded engine | `{candidate['engine_sha256']}` |
| Embedded manifest | `{candidate['manifest_sha256']}` |

The embedded ZIP contains 657 manifest-listed payload files, all verified; its compiler equals the repository compiler byte-for-byte. The exact engine source bytes occur inside the setup. See [candidate.json](candidate.json).

| Test | Expected | Actual | Pass? |
|---|---|---|---|
| A — direct global kosh | Refusal | Exit 1, E_KOSH_DVARA, no executable | Yes |
| A — global kosh + zero | Refusal | Exit 1, E_KOSH_GANIT, no executable | Yes |
| A1 — scalar global | 7 | Native output 7, exit 0 | Yes |
| A2 — two globals without main | Syntax error | End-of-file syntax error; adding main prints 3 | Literal input yes; class inference unsupported |
| A2 — record literal | Syntax error | At colon, exit 1 | Yes |
| A2 — default argument | Syntax error | At vitti; additional untyped case fails at = | Yes |
| B — nesting | Compile or clean refusal | 0–1022 compile, 1023 refuses; no crashes/timeouts | Yes |
| C1 — suffix preservation | Preserved exact bytes | Exact full hash in suffixed backup in seeded recovery fixture | Yes, scoped |
| C2 — concurrent processes | One refuses, no corruption | Engines exit 0/1; lock message; 657 matching hashes | Yes, scoped |
| C3 — edit during copying | Survives or reported | Edit survives; engine exit 0 | Yes |
| C4 — preservation of overwritten content | No lost bytes | Unequal prefix-name backup causes old target bytes to vanish from tree/transaction | **FAIL** |
| C4 — ordinary interrupted retry | No unexplained disappearance | Completes; only pending manifest pathname removed, same bytes in final manifest | Yes |
| D — identity | One path, expected version | Canonical v310, registry 1.0.310, 657/657 hashes | Yes |
| D — native suite | 322+ PASS, no failures | 322 PASS, 0 FAIL/COMPILE_FAIL/TIMEOUT | Yes |
| E — add/XOR | Refusal | Both brief and original cases exit 1, E_VIBHAG_ANKA, no executable | Yes |
| E — length | 2 | Native output 2, exit 0 | Yes |

Suite exclusions: 3 NO_EXPECTATION, 1 SKIP_LINUX_RAW_SYSCALL, 5 SKIP_SIDE_EFFECT_OR_INLINE_ASM. [All cases](native-cases.json). OOM, IDE workflows, uninstall, cross-platform payload determinism and gate-mutation checks were not rerun or newly accepted. Prior reports retain their own artifact identities and counts.

Native setup reached Finish in **{initial['finish_seconds']:.3f} seconds**, engine exit 0, and closed after Finish. [Viewed completion screenshot](initial-finish.png) shows the success page; the helper unchecked Launch IDE after capture. Both interruption tests intentionally stopped only their own wizard/engine. C1/C4 controlled rename failures are explained in OWNERSHIP.md, not mislabeled as ordinary installation failures.

The final ordinary retry leaves a working canonical v310 installation; all 657 payload hashes, manifest and uninstaller match, fresh shell resolves exactly one compiler, and all **12 recorded installer/wizard processes** are closed with no lock or pending transaction. [Final identity](handoff-identity.json), [process closure](final-processes.json). Original v309 and each test installation/transaction remain preserved; see `backup-*.json`, `vacate-*.json`, `restore-*.json`.

Detailed reports: [INITIALIZER](INITIALIZER.md), [BUDGET](BUDGET.md), [OWNERSHIP](OWNERSHIP.md), [ARITHMETIC](ARITHMETIC.md), [commands](COMMANDS.md). Raw observations are retained, including the three corrected harness expectations explained in INITIALIZER.md. Per-file evidence hashes are in `EVIDENCE.sha256` (excluding the manifest itself).

Sarvam action: acknowledge the exact candidate and native results; reproduce/fix C4; retain the class-inference correction and the existing gate/atomicity review limitations; verify the final rebuilt candidate independently. Source fixes belong in a review branch. No CI workflow or automatic run was changed/launched.
''')
write('COMMANDS.md','''# Commands and scope

Test checkout: `E:\\Github_Projects\\Sutram\\build\\windows-v310-acceptance`, pinned to candidate.json's source commit. It was created after `git fetch origin`, `git merge --ff-only origin/main`, and `git worktree add -b codex/windows-v310-2026-11-07 build/windows-v310-acceptance origin/main`.

Preparation: `python build/prepare-v310.py` from the original repository; a copy of that script is included here. It adapts prior observation/preservation helpers into this evidence folder without touching product source.

From the pinned checkout (PowerShell, ordinary user):

```powershell
python Windows-to-Sarvam/win-v310-2026-11-07/pin-fix-package.py
python Windows-to-Sarvam/win-v310-2026-11-07/compiler-probes.py expressions
python Windows-to-Sarvam/win-v310-2026-11-07/compiler-probes.py nesting
$env:SUTRAM_EVIDENCE=Join-Path (Get-Location) 'Windows-to-Sarvam/win-v310-2026-11-07'
python tools/test_windows_native.py
& Windows-to-Sarvam/win-v310-2026-11-07/initial-install.ps1
python Windows-to-Sarvam/win-v310-2026-11-07/ownership.py concurrency
& Windows-to-Sarvam/win-v310-2026-11-07/ownership-controller.ps1
python Windows-to-Sarvam/win-v310-2026-11-07/supplemental.py
python Windows-to-Sarvam/win-v310-2026-11-07/ownership.py ordinary
& Windows-to-Sarvam/win-v310-2026-11-07/verify-saved.ps1
python Windows-to-Sarvam/win-v310-2026-11-07/report.py
```

Compiler and suite work ran concurrently with the independent initial install; all ownership tests ran sequentially. Engine launches, complete arguments, fixtures, process IDs/exits and hash inventories are in ownership/*.json. GUI argv/child identities/screenshots/logs are in initial.json, c1-stop.json, ordinary-stop.json and accompanying files. Every compiler probe, including every nesting depth, is retained with argv/output in the corresponding results.json.

Safety guards: original installation copied and hash-verified; later trees/transactions moved to verified direct-child destinations under per-user Programs; no security configuration changes or arbitrary process kills; only owned process handles stopped; background PowerShell engines launched without visible windows. The GUI observer bounds runs to 240 seconds; native engines have a 180-second observation deadline; compiler/run probes have 15-second deadlines. The suite uses its existing 15/5-second compile/run deadlines. No timeout fired.

Fresh identity reconstructs Machine + User registry PATH and starts a new cmd process outside the compiler directory, then runs `where sutram` and `sutram --version`. It also checks all installed hashes and registration. Process closure is checked using recorded GUI PID/start pairs and terminal status of owned engine process handles.

The fixture test deliberately supplies known-owned journal entries and synthetic backup bytes, and holds one later staged compiler open without delete sharing. Those inputs are essential to reproduce C1/C4; they are documented fixture state, not evidence of a naturally corrupted installation. The engine/ZIP/setup bytes are unchanged and hash-pinned.

Reproduction needs a fresh evidence/output directory and controlled installation state: stale-output and duplicate-backup guards deliberately refuse accidental reruns. The final report generator never reruns product tests. Native raw logs and the complete Git publication diff are the reviewable record. No product source diff exists in this round.
''')
print('Reports generated; C4 remains FAIL; final installed identity verified.')
