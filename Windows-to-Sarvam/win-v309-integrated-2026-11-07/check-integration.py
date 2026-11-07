from pathlib import Path
import sys,json,hashlib,zipfile,subprocess
out=Path(__file__).resolve().parent;root=out.parents[1];main=root.parents[1]
sys.path.insert(0,str(root/'tools'))
from check_installer_version import embedded_payload
def entries(path):
    z=embedded_payload(path.read_bytes());return {n.replace('\\','/'):z.read(n) for n in z.namelist()}
before=entries(root/'build/native-v309-final-fix/Sutram-Setup.exe')
after=entries(root/'build/native-v309-integrated/Sutram-Setup.exe')
changed=sorted(n for n in set(before)|set(after) if before.get(n)!=after.get(n))
assert set(changed)=={'docs/CHANGELOG.md','docs/INSTALLER-REBUILD.md','docs/PATH-TO-COMPLETION.md','docs/RELEASE-NOTES.md','payload.manifest.sha256'},changed
z=zipfile.ZipFile(main/'build/windows-v309-linux-checkout/build/linux-payload-integrated/payload.zip')
assert all(i.date_time==(1980,1,1,0,0,0) for i in z.infolist())
text_ext={'.md','.html','.txt','.out','.exit','.sm','.smlib','.lang','.sandesh'}
names={n[4:] if n.startswith(('bin/','win/')) else n for n in after if Path(n).suffix in text_ext}
p=subprocess.run(['git','check-attr','eol','--',*sorted(names)],cwd=root,capture_output=True,text=True)
assert p.returncode==0 and not p.stderr and all(line.endswith(': lf') for line in p.stdout.splitlines()),p
row=dict(payload_changed_entries=changed,compiler_and_runtime_payloads_unchanged=True,linux_zip_all_dates_fixed=True,
         payload_text_attributes_lf=len(names),attribute_check_stderr=p.stderr,
         source_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip())
(out/'integration-check.json').write_text(json.dumps(row,indent=2)+'\n',encoding='utf8')
print(json.dumps(row,indent=2))
