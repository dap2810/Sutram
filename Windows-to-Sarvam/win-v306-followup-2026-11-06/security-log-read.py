"""Read-only correlation after Windows reported suspended installer threads."""
from pathlib import Path
import gzip,json,re,hashlib
HERE=Path(__file__).resolve().parent
folder=Path(r'C:\ProgramData\Acronis\ActiveProtection\Logs')
files=sorted(folder.glob('active_protection*'),key=lambda p:p.stat().st_mtime,reverse=True)[:6]
rows=[]
for p in files:
    row=dict(path=str(p),size=p.stat().st_size)
    try:
        original=p.read_bytes()
        row['read_bytes_sha256']=hashlib.sha256(original).hexdigest()
        data=gzip.decompress(original) if p.suffix=='.gz' else original
        lines=data.decode('utf-8','replace').splitlines()
        hits=[n for n,s in enumerate(lines) if 'suspended successfully' in s and re.search(r'\b(?:42236|43036|27748|36956)\b',s)]
        indices=sorted({i for n in hits for i in range(max(0,n-12),min(len(lines),n+12))})
        row['suspension_lines']=[n+1 for n in hits]
        row['relevant_lines']=[dict(line=n+1,text=lines[n]) for n in indices]
    except Exception as exc:row['error']=str(exc)
    rows.append(row)
(HERE/'security-log-excerpts.json').write_text(json.dumps(rows,indent=2)+'\n',encoding='utf8')
for row in rows:
    print(row['path'],len(row.get('relevant_lines',[])),row.get('error',''))
    for line in row.get('relevant_lines',[]):print(line['text'])
