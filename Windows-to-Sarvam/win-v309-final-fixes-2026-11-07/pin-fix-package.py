from pathlib import Path
import sys,hashlib,shutil,json,subprocess
root=Path(__file__).resolve().parents[2]
out=root/'Windows-to-Sarvam/win-v309-final-fixes-2026-11-07'
sys.path.insert(0,str(root/'tools'))
from check_installer_version import embedded_payload
sha=lambda b:hashlib.sha256(b).hexdigest()
setup=root/'Sutram-Setup.exe';data=setup.read_bytes()
assert (root/'windows/native-installer/install-core.ps1').read_bytes() in data
z=embedded_payload(data);names={n.replace('\\','/'):n for n in z.namelist()}
manifest=z.read(names['payload.manifest.sha256'])
(out/'payload.manifest.sha256').write_bytes(manifest)
entries={line.split(' *',1)[1].replace('\\','/'):line.split(' *',1)[0].lower() for line in manifest.decode('utf-8-sig').splitlines()}
rows=[dict(file=n,expected=h,actual=sha(z.read(names[n]))) for n,h in entries.items()]
assert len(rows)==657 and all(r['expected']==r['actual'] for r in rows)
assert sha(z.read(names['bin/sutram.exe']))==sha((root/'win/sutram.exe').read_bytes())
shutil.copy2(setup,root/'build/native-v309-final-fix/Sutram-Setup.exe')
record=dict(source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),setup_sha256=sha(data),compiler_sha256=sha((root/'win/sutram.exe').read_bytes()),engine_sha256=sha((root/'windows/native-installer/install-core.ps1').read_bytes()),payload_entries=len(rows),manifest_sha256=sha(manifest),checks=rows)
(out/'candidate.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in record.items() if k!='checks'},indent=2))
