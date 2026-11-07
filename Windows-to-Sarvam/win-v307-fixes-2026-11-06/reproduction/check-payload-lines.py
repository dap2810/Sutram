from pathlib import Path
import hashlib,json,os,subprocess
root=Path(__file__).resolve().parents[2]
stage=root/'build/windows/setup-56ef087c8dec4c729c6df84a7cd97c20/payload'
old=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram-before-review-fixes-20261106'
rows=[]
for p in stage.rglob('*'):
    if not p.is_file() or p.name=='payload.manifest.sha256':continue
    rel=p.relative_to(stage);q=old/rel
    if q.is_file() and p.read_bytes()!=q.read_bytes():
        a,b=p.read_bytes(),q.read_bytes()
        rows.append(dict(path=str(rel),crlf_only=a.replace(b'\r\n',b'\n')==b,bytes_before=len(a),bytes_installed=len(b)))
(root/'build/fixes/payload-differences.json').write_text(json.dumps(rows,indent=2)+'\n')
print('different',len(rows),'CRLF-only',sum(r['crlf_only'] for r in rows))
print('other',[r['path'] for r in rows if not r['crlf_only']])
fixture=root/'tests/fixtures/file_hello.txt'
before=fixture.read_bytes();canonical=subprocess.check_output(['git','show','HEAD:tests/fixtures/file_hello.txt'],cwd=root)
(root/'build/fixes/fixture-repair.json').write_text(json.dumps(dict(path=str(fixture),before_hex=before.hex(),git_blob_hex=canonical.hex()))+'\n')
fixture.write_bytes(canonical)
