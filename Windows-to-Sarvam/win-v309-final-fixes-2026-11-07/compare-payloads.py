"""Compare native-Windows and native-Linux staged payloads and fresh checkouts."""
from pathlib import Path
import hashlib,json,sys,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];MAIN=ROOT.parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from check_installer_version import embedded_payload
sha=lambda b:hashlib.sha256(b).hexdigest()
windows=embedded_payload((ROOT/'build/native-v309-final-fix/Sutram-Setup.exe').read_bytes())
linux=zipfile.ZipFile(MAIN/'build/windows-v309-linux-checkout/build/linux-payload-final/payload.zip')
def entries(z):return {n.replace('\\','/'):z.read(n) for n in z.namelist()}
w=entries(windows);l=entries(linux)
names=sorted(set(w)|set(l))
rows=[dict(file=n,windows=sha(w[n]) if n in w else None,linux=sha(l[n]) if n in l else None,match=n in w and n in l and w[n]==l[n]) for n in names]
samples=[]
for n in ['README.md','docs/LANGUAGE-REFERENCE.md','lang/sanskrit.lang']:
    fresh=(MAIN/'build/windows-v309-fixes-fresh'/n).read_bytes()
    lf=(MAIN/'build/windows-v309-linux-checkout'/n).read_bytes()
    stale=(ROOT/n).read_bytes()
    samples.append(dict(file=n,windows_fresh_sha256=sha(fresh),linux_fresh_sha256=sha(lf),payload_sha256=sha(w[n]),fresh_windows_crlf=b'\r\n' in fresh,stale_windows_crlf=b'\r\n' in stale,match=fresh==lf==w[n]))
binary=['bin/sutram.exe','win/sutram.exe','bin/sutram-link.exe','sutram-ide-gui.exe','assets/sutram.ico']
sources=['win/sutram.exe','win/sutram.exe','sutram-link.exe','sutram-ide-gui.exe','icons/sutram.ico']
raw=[dict(file=n,unchanged=w[n]==(ROOT/src).read_bytes()) for n,src in zip(binary,sources)]
result=dict(windows_source_commit=json.loads((HERE/'candidate.json').read_text())['source_commit'],linux_source_commit=(MAIN/'build/windows-v309-linux-checkout/.git/HEAD').read_text().strip(),payload_files=len(names)-1,manifest_sha256=sha(w['payload.manifest.sha256']),all_entries_equal=all(x['match'] for x in rows),samples=samples,binaries=raw,entries=rows,zip_bytes_equal='not claimed; ZIP metadata/compression differ')
(HERE/'payload-comparison.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
assert len(names)==658 and result['all_entries_equal'] and all(x['match'] and not x['fresh_windows_crlf'] for x in samples) and all(x['unchanged'] for x in raw)
print(json.dumps({k:v for k,v in result.items() if k!='entries'},indent=2))
