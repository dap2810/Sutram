"""Actual unchanged embedded installer engine on the canonical native installation.

C1/C4 seed explicitly documented owned transaction fixtures after a real interruption.
Only test-owned content is seeded. A read-only handle deliberately prevents the final
staged compiler rename, leaving the transaction inspectable before commit cleanup.
"""
from pathlib import Path
import argparse,ctypes,hashlib,json,os,shutil,subprocess,sys,time
from ctypes import wintypes
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];WORK=ROOT/'build/native-v310'
INSTALL=Path(os.environ['LOCALAPPDATA'])/'Programs/Sutram';TXN=INSTALL.with_name('Sutram.sutram-transaction')
PS=Path(os.environ['SystemRoot'])/'System32/WindowsPowerShell/v1.0/powershell.exe'
candidate=json.loads((HERE/'candidate.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
SETUP=WORK/'Sutram-Setup.exe';CORE=WORK/'install-core.ps1';ZIP=WORK/'payload.zip'
assert sha(SETUP)==candidate['setup_sha256']
sys.path.insert(0,str(ROOT/'tools'));from check_installer_version import payload_bounds
data=SETUP.read_bytes();bounds=payload_bounds(data);ZIP.write_bytes(data[bounds[0]:bounds[1]])
core=(ROOT/'windows/native-installer/install-core.ps1').read_bytes();assert core in data
CORE.write_bytes(core);assert sha(CORE)==candidate['engine_sha256']
ap=argparse.ArgumentParser();ap.add_argument('phase',choices=['concurrency','edit','fixtures','ordinary']);a=ap.parse_args()
out=HERE/'ownership';out.mkdir(exist_ok=True)
active=[];records=[]
def save(name,obj):(out/(name+'.json')).write_text(json.dumps(obj,indent=2)+'\n',encoding='utf8')
def inventory(root):
    return {str(p.relative_to(root)).replace('\\','/'):dict(sha256=sha(p),bytes=p.stat().st_size) for p in sorted(root.rglob('*')) if p.is_file()} if root.exists() else {}
def snapshot(name):
    obj=dict(target=inventory(INSTALL),transaction=inventory(TXN),time=time.time());save(name,obj)
    if (TXN/'journal.txt').exists():shutil.copy2(TXN/'journal.txt',out/(name+'-journal.txt'))
    return obj
def preserve(action,name,backup=None):
    cmd=[str(PS),'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(HERE/'preserve.ps1'),'-Action',action,'-Name',name]
    if backup:cmd+=['-BackupName',backup]
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    save('preserve-'+name,dict(command=cmd,exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace')))
    if p.returncode:raise RuntimeError('Preservation failed: '+p.stderr.decode('utf8','replace'))
def start(name):
    log=out/(name+'-engine.log');stdout=open(out/(name+'-stdout.txt'),'wb');stderr=open(out/(name+'-stderr.txt'),'wb')
    cmd=[str(PS),'-NoLogo','-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(CORE),'-PayloadZip',str(ZIP),'-InstallDir',str(INSTALL),'-SetupExePath',str(SETUP),'-LogPath',str(log),'-AddPath','-DesktopShortcut']
    t=time.perf_counter();p=subprocess.Popen(cmd,cwd=ROOT,stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
    row=dict(name=name,pid=p.pid,command=cmd,launched=time.time(),start_perf=t,engine_sha256=sha(CORE),setup_sha256=sha(SETUP));active.append((p,row,stdout,stderr));return p,row
def finish(p,row):
    try:p.wait(timeout=max(1,180-(time.perf_counter()-row['start_perf'])))
    except subprocess.TimeoutExpired:p.kill();p.wait(10);row['timeout']=True
    row.update(exit=p.returncode,seconds=time.perf_counter()-row['start_perf'],process_exited=p.poll() is not None)
    save(row['name'],row);records.append(row);print(row['name'],row['exit'],round(row['seconds'],3),flush=True)
def compare(before,after,name):
    locations={}
    for place,items in [('target',after['target']),('transaction',after['transaction'])]:
        for rel,v in items.items():locations.setdefault(v['sha256'],[]).append(place+'/'+rel)
    disappeared=[];changed=[]
    for rel,v in before['target'].items():
        if rel not in after['target']:disappeared.append(dict(file=rel,**v,copies_after=locations.get(v['sha256'],[])))
        elif v['sha256']!=after['target'][rel]['sha256']:changed.append(dict(file=rel,**v,new_sha256=after['target'][rel]['sha256'],copies_after=locations.get(v['sha256'],[])))
    row=dict(disappeared=disappeared,changed=changed);save(name,row);return row
class Hold:
    def __init__(self,path):
        k=ctypes.WinDLL('kernel32',use_last_error=True);self.k=k
        k.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE];k.CreateFileW.restype=wintypes.HANDLE
        k.CloseHandle.argtypes=[wintypes.HANDLE]
        self.handle=k.CreateFileW(str(path),0x80000000,1,None,3,0,None)
        if self.handle==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
    def close(self):self.k.CloseHandle(self.handle)
try:
    if a.phase=='concurrency':
        before=snapshot('c2-before');p1,r1=start('c2-first');p2,r2=start('c2-second')
        finish(p1,r1);finish(p2,r2);after=snapshot('c2-after')
        logs=[(out/(r['name']+'-engine.log')).read_text(encoding='utf8') for r in [r1,r2]]
        result=dict(launch_gap_seconds=r2['start_perf']-r1['start_perf'],exit_codes=[r1['exit'],r2['exit']],lock_message=[line for log in logs for line in log.splitlines() if 'Another Sutram installer' in line],completion=[line for log in logs for line in log.splitlines() if 'Installation complete:' in line],pass_=sorted([r1['exit'],r2['exit']])==[0,1] and any('Another Sutram installer' in log for log in logs))
        result['diff']=compare(before,after,'c2-diff');save('c2-result',result);print(json.dumps(result,indent=2),flush=True)
    elif a.phase=='edit':
        preserve('backup','working-v310');preserve('vacate','before-c3')
        try:
            p,row=start('c3-edit');target=INSTALL/'docs/BUILDING.md';last=INSTALL/'win/sutram.exe';edit=None
            deadline=time.perf_counter()+150
            while p.poll() is None and time.perf_counter()<deadline:
                if target.is_file() and not last.exists() and (TXN/'stage/win/sutram.exe').is_file():
                    original=target.read_bytes();mark=b'\nV310 C3 OWNER EDIT DURING PUBLICATION: preserve this line.\n'
                    (out/'c3-original-BUILDING.md').write_bytes(original)
                    with target.open('ab') as f:f.write(mark)
                    edited=target.read_bytes();(out/'c3-edited-BUILDING.md').write_bytes(edited)
                    edit=dict(target=str(target),time=time.time(),engine_still_running=p.poll() is None,last_target_absent=not last.exists(),later_file_staged=(TXN/'stage/win/sutram.exe').exists(),original_sha256=hashlib.sha256(original).hexdigest(),edited_sha256=hashlib.sha256(edited).hexdigest());break
                time.sleep(.002)
            finish(p,row)
            result=dict(edit=edit,exit=row['exit'],after_sha256=sha(target) if target.exists() else None)
            result['edit_survived']=bool(edit and result['after_sha256']==edit['edited_sha256']);save('c3-result',result);snapshot('c3-after');print(json.dumps(result,indent=2),flush=True)
        finally:preserve('restore','after-c3','working-v310')
    elif a.phase=='ordinary':
        preserve('vacate','before-ordinary')
        try:
            cmd=[str(PS),'-NoProfile','-NonInteractive','-ExecutionPolicy','Bypass','-File',str(HERE/'run-install.ps1'),'-Name','ordinary-stop','-Moment','middle']
            p=subprocess.run(cmd,cwd=ROOT,capture_output=True,timeout=280,creationflags=subprocess.CREATE_NO_WINDOW)
            save('ordinary-stop-command',dict(command=cmd,exit=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace')))
            assert p.returncode==0
            stop=json.loads((HERE/'ordinary-stop.json').read_text());assert stop['status']=='INTERRUPTED' and 0<stop['payload_files_present']<657
            before=snapshot('ordinary-before');p,row=start('ordinary-retry');finish(p,row);after=snapshot('ordinary-after')
            diff=compare(before,after,'ordinary-diff');save('ordinary-result',dict(exit=row['exit'],diff=diff))
            assert row['exit']==0
        except BaseException:
            preserve('restore','ordinary-error','working-v310');raise
    else:
        # The actual GUI interruption must already have captured a partial clean install.
        stop=json.loads((HERE/'c1-stop.json').read_text());assert stop['status']=='INTERRUPTED' and stop['payload_files_present']<657 and stop['payload_files_present']>0
        assert TXN.is_dir() and (INSTALL/'payload.pending.sha256').is_file()
        snapshot('c1-unmodified-interruption')
        rel='docs/BUILDING.md';target=INSTALL/rel;backup=TXN/'backup'/rel;supdir=TXN/'backup/_superseded/docs';backup.parent.mkdir(parents=True,exist_ok=True);supdir.mkdir(parents=True,exist_ok=True)
        blocked=TXN/'stage/win/sutram.exe';assert blocked.is_file() and not (INSTALL/'win/sutram.exe').exists()
        for name,wrong_existing in [('c1-suffix',False),('c4-unequal-existing',True)]:
            # These unique bytes are declared owned by the interrupted journal, not a user file.
            content=(name+' TEST-OWNED intermediate payload bytes\n').encode();target.write_bytes(content)
            backup.write_bytes(b'FIXTURE original older payload bytes, retained separately\n')
            have=sha(target).upper();sup=supdir/('BUILDING.md.'+have[:12]);assert not sup.exists()
            if wrong_existing:sup.write_bytes(b'FIXTURE wrong bytes at the expected hash-prefix filename\n')
            with (TXN/'journal.txt').open('a',encoding='utf8',newline='') as f:f.write('STAGED\tdocs\\BUILDING.md\t'+have+'\r\n')
            (out/(name+'-owned-before.txt')).write_bytes(content)
            fixture=dict(target=str(target),owned_sha256=have.lower(),journal_declaration='STAGED',backup_sha256=sha(backup),superseded=str(sup),superseded_before_sha256=sha(sup) if sup.exists() else None,blocked_staged_path=str(blocked),method='Unchanged full embedded engine; synthetic journal-owned intermediate plus backup; later staged compiler held without delete-sharing to retain transaction before commit.')
            save(name+'-fixture',fixture);before=snapshot(name+'-before')
            hold=Hold(blocked)
            try:p,row=start(name);finish(p,row)
            finally:hold.close()
            after=snapshot(name+'-after');diff=compare(before,after,name+'-diff')
            locations=[place+'/'+path for place in ['target','transaction'] for path,v in after[place].items() if v['sha256']==have.lower()]
            result=dict(engine_exit=row['exit'],owned_sha256=have.lower(),owned_copies_after=locations,superseded_after_sha256=sha(sup) if sup.exists() else None,target_after_sha256=sha(target),expected_controlled_stop='later win/sutram.exe rename fails because test holds a non-delete-sharing read handle',diff=diff)
            save(name+'-result',result);print(name,'owned copies after',locations,flush=True)
        preserve('restore','after-c4','working-v310')
finally:
    for p,row,stdout,stderr in active:
        if p.poll() is None:p.kill();p.wait(10);row['stopped_by_observer_cleanup']=True;save(row['name'],row)
        stdout.close();stderr.close()
    save(a.phase+'-processes',records)
