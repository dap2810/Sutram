from pathlib import Path
import json,hashlib,shutil
here=Path(__file__).resolve().parent
r=json.loads((here/'preflight.json').read_text(encoding='utf8'))
assert r['embedded_version_number']==312 and not r['may_proceed']
assert not r['installation_attempted'] and not r['tasks_A_to_D_run']
def write(name,text):(here/name).write_text(text,encoding='utf8',newline='\n')
shutil.copy2('C:/Users/dmech/Downloads/SUTRAM-WINDOWS-V313-PREFLIGHT (1).md',here/'REQUEST.md')
write('.gitattributes','* -text\n')
write('PREFLIGHT.md',f'''# v313-or-later preflight — STOP: package is v312

Checked at `{r['checked_at']}` against repository commit `{r['source_commit']}`. The setup was read directly from Git, its embedded `bin/sutram.exe` extracted to a workspace artifact directory, and that compiler executed natively without installation.

Exact stdout, exit {r['exit']} (stderr empty):

```text
{r['stdout'].rstrip()}
```

| Artifact | SHA-256 |
| --- | --- |
| Sutram-Setup.exe | `{r['setup_sha256']}` |
| Embedded bin/sutram.exe | `{r['embedded_compiler_sha256']}` |
| Repository win/sutram.exe | `{r['repository_compiler_sha256']}` |

The setup matches its declared checksum. The embedded and repository compilers are byte-identical. These are three explicitly identified artifact hashes; equality of the two compiler hashes is expected.

**P2 decision: STOP. The package is v312; this v313-or-later round cannot proceed.** No installation, licence-window launch, budget probe, flag probe, uninstall or suite run was performed. Existing installed state and prior evidence were left unchanged. No release acceptance is claimed.

Reproduce the preflight only:

```powershell
python Windows-to-Sarvam/win-v313-preflight-2026-11-08/preflight.py --ref {r['source_commit']}
```

[Raw record](preflight.json), [raw stdout](version-stdout.txt), [raw stderr](version-stderr.txt), [brief](REQUEST.md). The current brief's explicit stop rule supersedes the broader baseline work permitted by the previous brief.
''')
write('RESULTS.md',f'''# Windows round — stopped at version preflight

The current package at `{r['source_commit']}` contains **v312**. The brief requires **v313 or later** and explicitly says to stop if v312 is found. [Exact version output and all three artifact hashes](PREFLIGHT.md).

| Test | Expected | Actual | Pass? |
| --- | --- | --- | --- |
| P1 — embedded version | v313 or later | Sutram 1.0 (v312) - sampurna sutra | **FAIL — STOP** |
| A1 — walk-budget message | recorded | Stopped at P2 | NOT RUN |
| A2 — AST-capacity message | recorded | Stopped at P2 | NOT RUN |
| A3 — messages distinguishable? | yes | Stopped at P2 | NOT ASSESSED |
| A3 — remedy named? | yes | Stopped at P2 | NOT ASSESSED |
| A4 — --analysis-steps=64 | accepted | Stopped at P2; flag availability not probed | NOT RUN |
| A4 — zero, negative, non-number | refused | Stopped at P2 | NOT RUN |
| B1 — whole instruction visible | full text | Stopped at P2 | NOT RUN |
| C1 — no new temp directory | none | Stopped at P2 | NOT RUN |
| C2 — two uninstall runs | consistent | Stopped at P2 | NOT RUN |
| C3 — nothing survives | nothing | Stopped at P2 | NOT RUN |
| D — fresh-shell identity | one path, expected version | No installation performed | NOT RUN |
| D — native suite | 322 PASS, no FAIL | Stopped at P2 | NOT RUN |
| D — elapsed time | compare to 18.6 s | No suite run | NOT RUN |

Only extraction, hashing and the native `--version` invocation were performed. No results from the previous v312 runs are promoted to this round. The report, exact supplied brief, raw output and reproduction script are retained with EVIDENCE.sha256. No product code, workflow, installation, registry or earlier evidence was changed.
''')
for name,title in [('BUDGET.md','Tasks A1–A4'),('LICENCE.md','Tasks B1–B2'),('UNINSTALL.md','Tasks C1–C3')]:
    write(name,f'# {title} — NOT RUN\n\nStopped at P2 because the extracted package compiler is v312. The supplied brief requires v313 or later before these checks. See [PREFLIGHT.md](PREFLIGHT.md). No prior-version results are substituted.\n')
write('EVIDENCE.sha256',''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()} *{p.name}\n' for p in sorted(here.iterdir()) if p.is_file() and p.name!='EVIDENCE.sha256'))
print('Preflight STOP report written; no Tasks A-D executed.')
