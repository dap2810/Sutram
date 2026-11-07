"""Keep the accidental provider-metadata expansion locally; publish measured fields."""
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
source=HERE/'clean.json'
raw=source.read_bytes()
r=json.loads(raw)
archive=HERE.parents[1]/'build/windows-v307-2026-11-06/clean-observer-provider-metadata.json'
assert not archive.exists()
archive.write_bytes(raw)
count=0
for row in r.get('observations',[]):
    v=row.get('last_line')
    if isinstance(v,dict):
        row['last_line']=v.get('value',v.get('Value','[See engine log; provider metadata excluded]'))
        count+=1
r['observer_issue']=dict(description='Get-Content returned an extended string; ConvertTo-Json expanded provider metadata, delaying observation. Observer stopped; Finish verified in clean-finish.json. Fixed by creating a plain .NET string.',raw_bytes=len(raw),raw_sha256=hashlib.sha256(raw).hexdigest(),local_archive=str(archive),normalized_last_lines=count)
source.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print('Normalized clean observation',len(raw),'bytes ->',source.stat().st_size,'bytes;',count,'extended strings removed')
