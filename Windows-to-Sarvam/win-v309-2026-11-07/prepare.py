"""Pin the unmodified v309 package and compare its exact manifest bytes."""
from pathlib import Path
import hashlib,json,subprocess,sys,shutil
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
WORK=ROOT/'build/windows-v309-2026-11-07';WORK.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(ROOT/'tools'))
from check_installer_version import embedded_payload
sha=lambda b:hashlib.sha256(b).hexdigest()
setup=ROOT/'Sutram-Setup.exe';data=setup.read_bytes()
assert sha(data)=='9d046b4e1b3d95222523e78304e48cb5bc10a69f951b33822a2673f0dc3bb533'
shutil.copy2(setup,WORK/'Sutram-Setup.exe')
z=embedded_payload(data);names={n.replace('\\','/'):n for n in z.namelist()}
manifest=z.read(names['payload.manifest.sha256'])
(HERE/'payload.manifest.sha256').write_bytes(manifest)
entries={line.split(' *',1)[1].replace('\\','/'):line.split(' *',1)[0].lower() for line in manifest.decode('utf-8-sig').splitlines()}
rows=[]
for name in ['docs/LANGUAGE-REFERENCE.md','lang/sanskrit.lang','README.md']:
    raw=(ROOT/name).read_bytes();packed=z.read(names[name]);want=entries[name]
    rows.append(dict(file=name,checkout_sha256=sha(raw),manifest_sha256=want,payload_sha256=sha(packed),match=sha(raw)==want,payload_matches_manifest=sha(packed)==want,checkout_crlf=b'\r\n' in raw,payload_crlf=b'\r\n' in packed,crlf_only=raw!=packed and raw.replace(b'\r\n',b'\n')==packed))
all_payload=[dict(file=n,pass_=sha(z.read(names[n]))==want) for n,want in entries.items()]
for name in ['bin/sutram.exe','win/sutram.exe']:
    b=z.read(names[name]);assert sha(b)==sha((ROOT/'win/sutram.exe').read_bytes()),'Payload/compiler identity differs'
record=dict(commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),setup_sha256=sha(data),compiler_sha256=sha((ROOT/'win/sutram.exe').read_bytes()),manifest_entries=len(entries),manifest_passed=sum(x['pass_'] for x in all_payload),files=rows,attributes=(ROOT/'.gitattributes').read_text(encoding='utf8'),source='Checked-in release package obtained from this Windows checkout; not a new Windows build')
(HERE/'payload.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf8')
(HERE/'payload-all.json').write_text(json.dumps(all_payload,indent=2)+'\n',encoding='utf8')
shutil.copy2(ROOT/'Windows-to-Sarvam/win-v307-fixes-2026-11-06/ui-helper.ps1',HERE/'ui-helper.ps1')
shutil.copy2(Path(r'%USERPROFILE%\Downloads\SUTRAM-WINDOWS-V309.md'),HERE/'OWNER-INSTRUCTIONS.md')
print(json.dumps(record,indent=2))
