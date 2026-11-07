"""Read-only Acronis correlation for PIDs actually launched by the v307 tests."""
from pathlib import Path
import datetime,gzip,hashlib,json,re
HERE=Path(__file__).resolve().parent
phases=[]
for phase in ('clean','upgrade-observer-failed','upgrade','reader-interference/interrupt','reader-interference/recovery','interrupt','recovery'):
    path=HERE/(phase+'.json')
    if path.exists():
        row=json.loads(path.read_text(encoding='utf-8-sig'))
        phases.append(dict(phase=phase,started=row['started'],pids=[row['pid']]+([row['child']['pid']] if row.get('child') else [])))
pids={pid for p in phases for pid in p['pids']}
pattern=re.compile(r'\b(?:'+'|'.join(map(str,pids))+r')\b')
folder=Path(r'C:\ProgramData\Acronis\ActiveProtection\Logs')
files=sorted(folder.glob('active_protection*'),key=lambda p:p.stat().st_mtime,reverse=True)[:6]
r=dict(read_at=datetime.datetime.now().astimezone().isoformat(),phases=phases,files=[])
for p in files:
    row=dict(path=str(p),size=p.stat().st_size)
    try:
        original=p.read_bytes();row['read_bytes_sha256']=hashlib.sha256(original).hexdigest()
        lines=(gzip.decompress(original) if p.suffix=='.gz' else original).decode('utf8','replace').splitlines()
        hits=[n for n,s in enumerate(lines) if pattern.search(s) and any(t in s.lower() for t in ('suspend','suspected malware','terminated','watching of the process'))]
        indices=sorted({i for n in hits for i in range(max(0,n-12),min(len(lines),n+12))})
        row['matching_lines']=[n+1 for n in hits]
        row['relevant_lines']=[dict(line=n+1,text=lines[n]) for n in indices]
    except Exception as exc:row['error']=str(exc)
    r['files'].append(row)
(HERE/'security-log-excerpts.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(phases=phases,files=[{k:v for k,v in x.items() if k!='relevant_lines'} for x in r['files']]),indent=2))
