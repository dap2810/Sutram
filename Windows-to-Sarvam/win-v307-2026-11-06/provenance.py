"""Read-only comparisons for the source and raw evidence being handed off."""
from pathlib import Path
import hashlib,json,subprocess
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=dict(test_commit='75586a754371dc27f9ed850f592df6194b8e11a6',checks=[])
def check(label,ok,**data):r['checks'].append(dict(check=label,passed=bool(ok),**data))
for name,want in [('Sutram-Setup.exe','cbbfd0a66c0a9728c3fd88096631462430c0185cd8c6738964d5b885253e7481'),('win/sutram.exe','0444b43552f6140147ee4701aeac857d585086681bbe4e5bd71d8f90bedd3f7b'),('sutram.exe','0444b43552f6140147ee4701aeac857d585086681bbe4e5bd71d8f90bedd3f7b')]:
    actual=sha(ROOT/name);check(name,actual==want,sha256=actual)
engine=Path(r'%USERPROFILE%\AppData\Local\Temp\STM43D7.tmp\install-core.ps1')
source=ROOT/'windows/native-installer/install-core.ps1'
if engine.exists():
    check('Embedded engine equals repository text after newline/BOM normalization',engine.read_text(encoding='utf-8-sig')==source.read_text(encoding='utf-8-sig'),embedded_sha256=sha(engine),source_sha256=sha(source))
for probe in HERE.glob('r136_ws1_*.sm'):
    original=ROOT/'Muse-to-Sarvam'/probe.name
    check(probe.name,probe.read_bytes()==original.read_bytes(),original=str(original.relative_to(ROOT)),sha256=sha(probe))
runner=HERE/'job_runner.py';original=ROOT/'Windows-to-Sarvam/win-v306-followup-2026-11-06/job_runner.py'
check('Unchanged Job Object runner',runner.read_bytes()==original.read_bytes(),sha256=sha(runner))
oom=json.loads((HERE/'oom.json').read_text(encoding='utf8'))
for row in oom['runs']:
    raw=(HERE/row['stderr_file']).read_bytes()
    check(row['stderr_file'],raw.hex()==row['stderr_hex'] and len(raw)==row['stderr_bytes'],bytes=len(raw),ends_lf=raw.endswith(b'\n'))
suite=json.loads((HERE/'suite.json').read_text(encoding='utf8'))
check('Native harness unchanged since run',sha(ROOT/'tools/test_windows_native.py')==suite['harness_sha256'])
r['pass']=all(x['passed'] for x in r['checks'])
(HERE/'provenance.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(passed=r['pass'],checks=len(r['checks']),failures=[x for x in r['checks'] if not x['passed']]),indent=2))
raise SystemExit(not r['pass'])
