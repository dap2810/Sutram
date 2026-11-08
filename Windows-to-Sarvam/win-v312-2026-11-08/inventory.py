from pathlib import Path
import os,sys,json,hashlib,winreg,datetime
HERE=Path(__file__).resolve().parent
name=sys.argv[1]
def walk(root):
    rows=[]
    if root.exists():
        for p in [root,*sorted(root.rglob('*'))]:
            row={'path':str(p),'directory':p.is_dir()}
            if p.is_file():
                try:row.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                except OSError as e:row['error']=str(e)
            rows.append(row)
    return rows
programs=Path(os.environ['LOCALAPPDATA'])/'Programs'
temp=Path(os.environ['TEMP'])
roots=[programs/'Sutram',programs/'Sutram.sutram-transaction',programs/'Sutram.sutram-lock']
roots.extend(p for p in temp.iterdir() if 'sutram' in p.name.lower() or p.name.upper().startswith('STM'))
r={'time':datetime.datetime.now().astimezone().isoformat(),'roots':{str(p):walk(p) for p in roots},'preserved_old_roots':[str(p) for p in programs.iterdir() if p.name.lower().startswith('sutram') and p not in roots],'registry':{}}
def regtree(path):
    try:k=winreg.OpenKey(winreg.HKEY_CURRENT_USER,path)
    except FileNotFoundError:return None
    with k:
        subcnt,valcnt,_=winreg.QueryInfoKey(k);values=[]
        for i in range(valcnt):
            n,v,t=winreg.EnumValue(k,i);values.append({'name':n,'type':t,'value':v.hex() if isinstance(v,bytes) else v})
        return {'path':'HKCU\\'+path,'values':values,'subkeys':[regtree(path+'\\'+winreg.EnumKey(k,i)) for i in range(subcnt)]}
for path in [r'Software\Classes\.sm',r'Software\Classes\Sutram.Source',r'Software\Microsoft\Windows\CurrentVersion\Uninstall\Sutram',r'Software\SutramAcceptanceArchives',r'Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.sm']:
    r['registry'][path]=regtree(path)
(HERE/(name+'-inventory.json')).write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
print(json.dumps({'name':name,'roots':{p:len(rows) for p,rows in r['roots'].items()},'old_backup_roots':len(r['preserved_old_roots'])},indent=2))
