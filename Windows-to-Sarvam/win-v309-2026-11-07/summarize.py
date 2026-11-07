"""Read saved evidence, verify the preserved edit, and write the v309 reports.

Does not run/install anything or alter the preserved installation trees.
"""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def read(name):
    return json.loads((HERE / name).read_text(encoding='utf-8-sig'))

def write(name, text):
    (HERE / name).write_text(text.rstrip() + '\n', encoding='utf8', newline='\n')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(name, value):
    write(name, json.dumps(value, indent=2))

payload = read('payload.json')
arithmetic = read('arithmetic/results.json')
oom = read('oom/results.json')
native = Counter(x['status'] for x in read('native-cases.json'))
phases = {n: read(n + '.json') for n in ['initial', 'd1-stop', 'd1-retry', 'd2-stop', 'd2-retry', 'd3-stop', 'd3-retry']}
restore = read('restore-d3-failed.json')
edited = HERE / 'd3-edited-BUILDING.md'
preserved = Path(restore['preserved']) / 'docs/BUILDING.md'
original = HERE / 'd3-original-BUILDING.md'
inventory_hash = next(x['sha256'].lower() for x in restore['files'] if x['relative'] == r'docs\BUILDING.md')
edit = dict(
    provenance='Reconstructed read-only from saved evidence after dialog acknowledgement raised an observer error; no retry repeated.',
    original_sha256=sha(original), edited_sha256=sha(edited),
    after_retry_inventory_sha256=inventory_hash, preserved_file=str(preserved),
    preserved_file_sha256=sha(preserved),
    edit_preserved=sha(edited) == inventory_hash == sha(preserved),
    exact_added_bytes=(edited.read_bytes() == original.read_bytes() + b'\nV309 OWNER-EDIT RECOVERY PROBE: preserve this line.\n'),
    engine_exit=phases['d3-retry']['child_exit'],
    observer_status=phases['d3-retry']['status'],
    observer_error=phases['d3-retry']['observer_error'],
    dialog=phases['d3-retry']['dialog_text'],
)
save('d3-edit-result.json', edit)
assert edit['edit_preserved'] and edit['exact_added_bytes'] and edit['engine_exit'] == 1

d2_log = (HERE / 'd2-retry-engine.log').read_text(encoding='utf-8-sig')
d2_journal = (HERE / 'd2-stop-journal.txt').read_text(encoding='utf-8-sig')
recovery = dict(
    d1_seconds=phases['d1-stop']['seconds'], d1_engine_age_seconds=phases['d1-stop']['engine_age_seconds'],
    d1_payload_files=phases['d1-stop']['payload_files_present'],
    d2_stop_journal_counts=dict(Counter(line.split('\t')[0] for line in d2_journal.splitlines())),
    d2_retry_staging_start=len(re.findall(r'\] START \d+/657:', d2_log)),
    d2_retry_staging_done=len(re.findall(r'\] DONE  \d+/657:', d2_log)),
    d2_retry_already_staged=d2_log.count('Already staged '),
    d2_retry_publish_replacement=len(re.findall(r'\] PUBLISH \d+/657:', d2_log)),
    d3_edit=edit,
)
save('recovery-summary.json', recovery)
assert recovery['d1_seconds'] < 1 and recovery['d1_payload_files'] == 0
assert recovery['d2_stop_journal_counts']['PUBLISHED'] == 657
assert recovery['d2_retry_staging_done'] == 657 and recovery['d2_retry_publish_replacement'] == 0
assert arithmetic['summary'] == {'total': 7, 'passed': 7}
assert oom['summary'] == {'total': 32, 'passed': 32}
for case in oom['cases']:
    folder = HERE / 'oom' / f"{case['name']}-{case['limit_mib']}-{case['repetition']}"
    assert (folder / 'stderr').read_bytes() == b'Sutram truti: smritih na labdha\n'
    assert not (folder / 'stdout').read_bytes()
    assert case['exit'] == 1 and not case['timed_out']
assert native['PASS'] == 322 and not any(native[s] for s in ['FAIL', 'COMPILE_FAIL', 'TIMEOUT'])
assert read('handoff-identity.json')['pass'] and read('final-processes.json')['all_owned_processes_closed']

labels = ['keep(k[0:1] + zero)', 'keep(k[0:1] ^ zero)', 'likha(k[0:1] + 0)', 'yadi (k[0:1])', 'likha(k[0:1])', 'vitti i = k[0:1]', 'pankti_gan(k[0:2])']
text = ['# v309 arithmetic verification (Task A)', '', '**7/7 pass on native Windows.** The two original add/XOR reproductions are refused; no executable is emitted. The valid slice-length control prints `2`.', '', '[Exact argv, output streams, exit codes and timings](arithmetic/results.json); [commands and provenance](COMMANDS.md).', '', '| Program | Expected | Actual | Pass? |', '| --- | --- | --- | --- |']
for label, case in zip(labels, arithmetic['cases']):
    actual = 'exit 1, no executable, ' + re.search(r'\[(E_\w+)\]', case['compile']['stdout'])[1] if case['name'] != 'length' else 'compile 0; native exit 0; stdout `2\\n`; empty stderr'
    text.append(f"| `{label}` | {'2' if case['name'] == 'length' else 'refusal'} | {actual} | PASS |")
text += ['', 'The six refusals are written to **stdout**, with empty stderr. All six output paths were absent before compilation and remained absent. The prior add/XOR sources are copied without rewriting their reproductions.']
for label, case in zip(labels, arithmetic['cases']):
    text += ['', f"## `{label}`", '', f"Source: [{case['name']}.sm](arithmetic/{case['name']}.sm). Compiler exit `{case['compile']['exit']}`.", '', 'Exact compiler stdout:', '', '```text', case['compile']['stdout'].rstrip('\n'), '```']
    if case['name'] == 'length':
        text += ['', r'Native stdout is exactly `2\n` (LF), native exit 0, empty stderr.']
write('ARITHMETIC.md', '\n'.join(text))

text = ['# v309 native low-memory verification (Task B)', '', '**32/32 requested runs pass.** Every child exits `0x00000001`, produces empty stdout and exactly 32 stderr bytes ending in LF. No `0xC00000FD` or timeout occurred.', '', 'The existing Windows Job Object harness imposes a per-process commit limit before the first executable instruction. It does not lower the host memory limit. [Raw per-run results](oom/results.json) include peaks, remaining headroom, runtime, argv and working directory; adjacent directories contain the original stdout/stderr bytes.', '', '| B3 kosh limit | Run 1 | Run 2 | Run 3 | stderr 32 bytes + LF? |', '| ---: | --- | --- | --- | --- |']
for cap in [448, 480, 512, 544, 576, 608, 640]:
    text.append(f'| {cap} MiB | exit 1 | exit 1 | exit 1 | Yes, 3/3 |')
text += ['', '| 64 MiB control | Repetitions | Exit | stderr 32 bytes + LF? |', '| --- | ---: | --- | --- |', '| `A3-mandapa.sm` | 10 | 1 in all 10 | Yes, 10/10 |', '| `A3-nirmmita-touch-pages.sm` | 1 | 1 | Yes |', '', 'Exact stderr for every run:', '', '```text', 'Sutram truti: smritih na labdha', '```', '', '`53757472616d2074727574693a20736d7269746968206e61206c61626468610a` (hex, final byte `0a`).', '', 'Sources: [B3.sm](oom/B3.sm), [A3-mandapa.sm](oom/A3-mandapa.sm), [A3-nirmmita-touch-pages.sm](oom/A3-nirmmita-touch-pages.sm). [Runner and exact commands](COMMANDS.md).', '', 'This establishes the requested v309 boundary/control behavior on this machine. It does not establish that every possible allocation failure, reserve-allocation failure or teardown path is safe. No new Linux result or general memory-safety acceptance is claimed.']
write('OOM.md', '\n'.join(text))

text = ['# v309 payload comparison (Task C)', '', '**FAIL: two of the three checkout files differ from the package manifest solely because of CRLF.** The root `.gitattributes` at the tested commit still has no `*.md text eol=lf` rule. No attributes, source or package bytes were changed in this verification.', '', f"Tested commit: `{payload['commit']}`. Obtained the checked-in release package from this Windows checkout; this is **not a newly built Windows package**. All **657/657 embedded payload entries** match their manifest. Package integrity and deterministic bytes across checkouts are different checks.", '', '| File | Checkout SHA-256 | Manifest / embedded SHA-256 | Match? | Checkout CRLF? |', '| --- | --- | --- | --- | --- |']
for f in payload['files']:
    text.append(f"| `{f['file']}` | `{f['checkout_sha256']}` | `{f['manifest_sha256']}` | {'YES' if f['match'] else 'NO'} | {f['checkout_crlf']} |")
text += ['', 'Both Markdown files become byte-identical to the embedded copies when CRLF is replaced with LF. All three embedded copies have no CRLF; the language pack already matches.', '', 'The requested PowerShell CRLF check on `docs/LANGUAGE-REFERENCE.md` returns **True**. [Native certutil and PowerShell output](payload-native-commands.txt), [comparison and attributes snapshot](payload.json), [all embedded hash checks](payload-all.json), [manifest](payload.manifest.sha256).', '', 'Sarvam should complete/review the root Markdown LF rule and deterministic packaging, then verify a fresh Windows checkout and compare actual Windows/Linux package manifests. This round does not establish a causal relationship between byte differences and any security-product action.']
write('PAYLOAD.md', '\n'.join(text))

warning = '\n'.join(line for line in (HERE / 'd3-retry-engine.log').read_text(encoding='utf-8-sig').splitlines() if 'Not this installer' in line or 'ERROR:' in line)
text = f'''# v309 installation and interrupted recovery (Task D)

The native v309 installer completed the upgrade and both interruption retries. The edited file was preserved by an explicit refusal. **The late retry still copies all 657 payload files into staging**, so the requested shortcut for an already-published payload is not demonstrated.

| Attempt | Observation | Result |
| --- | --- | --- |
| Initial upgrade | Finish in {phases['initial']['finish_seconds']:.2f} s; engine 0; closes after Finish | PASS |
| D1 before first copy | Stopped {phases['d1-stop']['seconds']:.3f} s after Install; engine age {phases['d1-stop']['engine_age_seconds']:.3f} s; 0 payload files; no pending record or transaction | Boundary caught |
| D1 retry | Finish in {phases['d1-retry']['finish_seconds']:.2f} s; engine 0; no pending record/transaction | PASS |
| D2 after last file | Stopped at {phases['d2-stop']['seconds']:.2f} s; 657 files present and 657 `PUBLISHED` journal records; pending record still present | Boundary caught |
| D2 retry | Finish in {phases['d2-retry']['finish_seconds']:.2f} s; engine 0; 657 staging START/DONE pairs, 0 Already staged, 0 replacement PUBLISH log entries | Recovery PASS; repeats staging |
| D3 partway | Stopped at {phases['d3-stop']['seconds']:.2f} s; 57 payload files; appended one line to `docs/BUILDING.md` | Edit recorded |
| D3 retry | Engine 1; error dialog and explicit preserved-file log; edited bytes unchanged | Preservation PASS; observer acknowledgement error disclosed below |

These are observed timings, not performance guarantees. The native suite/OOM run overlapped early recovery work; timing differences cannot be assigned to installer changes.

## D1: previous-attempt handling

The first engine was stopped before it produced a pending record or transaction. The retry therefore has **no previous-attempt notice**; it starts normally and completes. See [stop](d1-stop.json), [retry](d1-retry.json), [retry log](d1-retry-engine.log) and [Finish screenshot](d1-retry-finish.png).

## D2: distinguishes installed files from staging copies

The stop was caught after the last payload publication, before the pending record was cleared. The saved journal ends with `PUBLISHED` for `win\\sutram.exe`; the log had just reached `Writing the payload manifest.` This proves the requested last-file/pending-record boundary, **not interruption inside a partially written journal record**.

The retry logs both prior journal and pending-record notices: `A previous installation stopped part-way ... this run finishes it.` It then recopies **657/657** files into the transaction staging folder. It does not reuse any already-staged entry. There are no per-file replacement `PUBLISH` entries on retry.

The no-replacement interpretation is supported by the pinned installer source: when the target hash matches the new payload hash, the publish loop discards the staged copy, journals `PUBLISHED`, and continues without replacing the target (`windows/native-installer/install-core.ps1`, lines 570-575). Thus it recognises matching installed content **after repeating extraction/staging**, not by immediately finalising the existing publication. No claim is made that all physical disk writes were independently traced.

Evidence: [stop](d2-stop.json), [stop log](d2-stop-engine.log), [stop journal](d2-stop-journal.txt), [retry](d2-retry.json), [retry log](d2-retry-engine.log), [D2 capture](d2-retry-finish.png), [derived counts](recovery-summary.json). The D2 capture contains only the title bar, so it does not prove the rendered Finish page. D2 completion is supported by the observed Finish control, successful Finish click/exit and engine completion log; the initial and D1 captures show the full Finish page.

## D3: the owner's edited bytes survive

Appended exactly `\\nV309 OWNER-EDIT RECOVERY PROBE: preserve this line.\\n` to `docs/BUILDING.md`. The retry refuses before replacing it; the GUI reports that setup did not complete and points to the log. The log gives the specific reason and recovery instructions:

```text
{warning}
```

| Evidence | SHA-256 |
| --- | --- |
| Original | `{edit['original_sha256']}` |
| Edited before retry | `{edit['edited_sha256']}` |
| Post-retry inventory before restore | `{edit['after_retry_inventory_sha256']}` |
| Preserved file, independently read after restore | `{edit['preserved_file_sha256']}` |

The complete edited folder and transaction remain at:

```text
{restore['preserved']}
{restore['preserved_transaction']}
```

Sources: [original](d3-original-BUILDING.md), [edited](d3-edited-BUILDING.md), [result](d3-edit-result.json), [retry log](d3-retry-engine.log), [error screenshot](d3-retry-error.png), [preservation/restore inventory](restore-d3-failed.json).

## Observer errors and final state

Two observer failures are retained rather than counted as product defects:

1. The first wizard observation tried Next before control 2002 existed. It closed the wizard before starting an engine. [Record](initial-observer-error.json). The helper was corrected to wait for the control; the actual upgrade then completed ([Finish](initial-finish.png)).
2. After capturing the D3 error dialog, synchronous `BM_CLICK` acknowledgement returned `SendMessageTimeout failed for message 0xF5`. The engine had exited 1 and the wizard also exited; the controller recorded `OBSERVER_ERROR`, preserved the interrupted folder, and restored the independently verified working v309 backup. This is why [d3-retry.json](d3-retry.json) is not labelled a clean observer pass. [Controller error](recovery-controller-error.txt). D3 preservation was then established read-only by comparing the original edit, post-retry inventory and preserved bytes; no install was repeated to hide this error.

The canonical installation is again **v309**, **657/657 hashes** match, one fresh-shell path resolves, and no pending file/transaction remains ([final identity](final-identity.json), [handoff-time identity](handoff-identity.json)). All 15 recorded wizard/engine processes are closed and no installer lock remains ([process check](final-processes.json)). No process was left waiting for the owner to close it.

Only handles belonging to the recorded test wizard/child were stopped. Logs/journals were copied after termination, with shared read access; live engine logs were not opened. No antivirus exclusion, service change or resumption of security-suspended processes was attempted. Successful finite runs do not establish that security-product suspensions can never recur. There was no v309 IDE acceptance test in this round.
'''
write('RECOVERY.md', text)

write('RESULTS.md', f'''# Windows v309 verification — 7 November 2026

**v309 is installed and working at the canonical path.** Arithmetic, the requested OOM cases and the native suite pass. Payload determinism remains unresolved; late recovery completes but repeats all staging copies. Independent Sarvam acceptance is pending.

| Task | Result | Evidence |
| --- | --- | --- |
| A arithmetic | 7/7; six refusals, valid length prints 2 | [ARITHMETIC.md](ARITHMETIC.md) |
| B OOM | 32/32; exit 1, exact 32-byte diagnostic, no FD | [OOM.md](OOM.md) |
| C checkout/package hashes | FAIL: 2/3 differ by CRLF; embedded integrity 657/657 | [PAYLOAD.md](PAYLOAD.md) |
| D recovery | Early/late retries finish; edit preserved; late retry restages 657 files | [RECOVERY.md](RECOVERY.md) |
| E fresh-shell identity | Only canonical v309, registry 1.0.309, 657/657 installed hashes | [handoff-identity.json](handoff-identity.json) |
| E native suite | 322 PASS; 3 NO_EXPECTATION; 6 deliberate skips; 0 FAIL / COMPILE_FAIL / TIMEOUT | [native-cases.json](native-cases.json) |

Tested repository commit: `{payload['commit']}`.
Compiler SHA-256: `{payload['compiler_sha256']}`.
Setup SHA-256: `{payload['setup_sha256']}`.

The original fresh-shell check found an older installed candidate and stopped, as requested. The owner's subsequent `start working on it` authorised the v309 installation. The original installation was preserved before upgrade; v309 was backed up before interruption tests. [Original inventory](backup-before-v309.json), [working v309 inventory](backup-working-v309.json).

No compiler, library, example, golden, installer, release binary or workflow was modified. This publication contains only reports, test probes/helpers and recorded evidence. No full CI was launched. No release, IDE or general memory-safety acceptance is claimed. The two helper errors are disclosed in RECOVERY.md.

[Exact commands and evidence interpretation](COMMANDS.md). [Owner's brief](OWNER-INSTRUCTIONS.md). [Sarvam handoff](../../ChatGPT-to-Sarvam/WINDOWS-V309-2026-11-07.md).
''')
print(json.dumps(dict(arithmetic=arithmetic['summary'], oom=oom['summary'], native=dict(native), d3_edit_preserved=edit['edit_preserved'], d2_staging_copies=recovery['d2_retry_staging_done']), indent=2))
