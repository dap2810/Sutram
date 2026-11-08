from pathlib import Path
import os,json,hashlib,datetime,subprocess
HERE=Path(__file__).resolve().parent
roots=[Path(os.environ['TEMP']),Path(os.environ['LOCALAPPDATA'])/'Temp']
rows=[]
for root in roots:
    newest=sorted(root.iterdir(),key=lambda p:p.stat().st_mtime,reverse=True)[:15]
    own=[]
    for p in sorted(root.glob('STM*')):
        if not p.is_dir():continue
        files=[]
        for f in sorted(p.rglob('*')):
            if f.is_file():files.append({'path':str(f),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
        own.append({'directory':str(p),'files':files})
    rows.append({'root':str(root),'newest_entries':[{'name':p.name,'directory':p.is_dir(),'modified':datetime.datetime.fromtimestamp(p.stat().st_mtime).astimezone().isoformat()} for p in newest],'stm_directories':own})
r={'time':datetime.datetime.now().astimezone().isoformat(),'scope':'Read-only preflight snapshot; no new uninstall performed','locations_resolve_to_same_directory':roots[0].resolve()==roots[1].resolve(),'locations':rows}
(HERE/'temp-inspection.json').write_text(json.dumps(r,indent=2)+'\n',encoding='utf8',newline='\n')
print(json.dumps({'same_directory':r['locations_resolve_to_same_directory'],'stm_directories':rows[0]['stm_directories']},indent=2))
