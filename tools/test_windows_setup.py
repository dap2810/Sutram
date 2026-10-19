"""Installer integrity and welcome-only smoke. Never clicks Install/Next."""
from pathlib import Path
import ctypes as C
from ctypes import wintypes as W
import subprocess,os,time,json
C.windll.kernel32.SetErrorMode(0x8003)
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=Path(os.environ.get('SUTRAM_EVIDENCE',str(ROOT/'build/windows/evidence')))
EVIDENCE.mkdir(parents=True,exist_ok=True)
log={'checks':[]}
def check(name,ok,detail):
    log['checks'].append({'check':name,'pass':bool(ok),'detail':detail})
    print(name,ok,detail,flush=True)
    if not ok:raise AssertionError(name)
exe=ROOT/'Sutram-Setup.exe'
x=subprocess.run([str(exe),'--self-test'],capture_output=True,timeout=15)
check('embedded-self-test',x.returncode==0,{'command':[str(exe),'--self-test'],'exit':x.returncode})
parts=sorted((ROOT/'build/windows').glob('setup-*/payload.zip'),key=lambda p:p.stat().st_mtime)
payload=parts[-1].read_bytes();data=bytearray(exe.read_bytes());offset=data.find(payload)
assert offset>=0
data[offset+65]^=1
bad=ROOT/'build/windows/setup-tampered.exe';bad.write_bytes(data)
x=subprocess.run([str(bad),'--self-test'],capture_output=True,timeout=15)
check('tampered-embedded-payload',x.returncode==1,{'command':[str(bad),'--self-test'],'exit':x.returncode})
u=C.WinDLL('user32',use_last_error=True)
CB=C.WINFUNCTYPE(W.BOOL,W.HWND,W.LPARAM)
u.EnumWindows.argtypes=[CB,W.LPARAM]
u.GetClassNameW.argtypes=[W.HWND,W.LPWSTR,C.c_int]
u.GetWindowThreadProcessId.argtypes=[W.HWND,C.POINTER(W.DWORD)]
u.PostMessageW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM]
si=subprocess.STARTUPINFO();si.dwFlags=1;si.wShowWindow=0
env=os.environ.copy();temp=ROOT/'build/windows/wizard-temp';temp.mkdir(exist_ok=True)
env['TEMP']=env['TMP']=str(temp)
proc=subprocess.Popen([str(exe)],cwd=ROOT,env=env,startupinfo=si)
log['command']=[str(exe)];log['pid']=proc.pid
try:
    windows=[]
    @CB
    def collect(h,l):
        pid=W.DWORD();u.GetWindowThreadProcessId(h,C.byref(pid))
        if pid.value==proc.pid:
            name=C.create_unicode_buffer(256);u.GetClassNameW(h,name,256)
            if name.value=='SutramWizardWindow':windows.append(h)
            elif len(log.get('other_windows',[]))<5:
                log.setdefault('other_windows',[]).append(name.value)
                print('Other own window class:',repr(name.value),flush=True)
        return True
    for _ in range(50):
        u.EnumWindows(collect,0)
        if windows:break
        if proc.poll() is not None:raise RuntimeError(f'Wizard exited {proc.returncode}')
        time.sleep(.1)
    u.WaitForInputIdle.argtypes=[W.HANDLE,W.DWORD]
    check('wizard-idle',u.WaitForInputIdle(proc._handle,5000)==0,'waited for GUI construction')
    check('welcome-window',len(windows)==1,windows)
    main=windows[0];rect=W.RECT()
    # Render our own window offscreen without taking focus from the user.
    u.SetWindowPos.argtypes=[W.HWND,W.HWND,C.c_int,C.c_int,C.c_int,C.c_int,W.UINT]
    assert u.SetWindowPos(main,None,-30000,-30000,800,600,0x54)
    u.UpdateWindow.argtypes=[W.HWND]
    u.UpdateWindow(main)
    # Capture only the test application's window, never the user's desktop.
    from PIL import Image
    g=C.WinDLL('gdi32',use_last_error=True)
    u.GetWindowRect.argtypes=[W.HWND,C.POINTER(W.RECT)]
    u.PrintWindow.argtypes=[W.HWND,W.HDC,W.UINT]
    g.CreateCompatibleDC.argtypes=[W.HDC];g.CreateCompatibleDC.restype=W.HDC
    g.CreateDIBSection.argtypes=[W.HDC,C.c_void_p,W.UINT,C.POINTER(C.c_void_p),W.HANDLE,W.DWORD]
    g.CreateDIBSection.restype=W.HANDLE
    g.SelectObject.argtypes=[W.HDC,W.HANDLE];g.SelectObject.restype=W.HANDLE
    g.DeleteObject.argtypes=[W.HANDLE];g.DeleteDC.argtypes=[W.HDC]
    u.GetWindowRect(main,C.byref(rect))
    width,height=rect.right-rect.left,rect.bottom-rect.top
    import struct
    bmi=C.create_string_buffer(struct.pack('<IiiHHIIiiII',40,width,-height,1,32,0,width*height*4,0,0,0,0))
    dc=g.CreateCompatibleDC(None);bits=C.c_void_p()
    bmp=g.CreateDIBSection(dc,bmi,0,C.byref(bits),None,0)
    old=g.SelectObject(dc,bmp)
    try:
        check('window-render',u.PrintWindow(main,dc,0)!=0,[width,height])
        picture=Image.frombuffer('RGB',(width,height),C.string_at(bits,width*height*4),'raw','BGRX',0,1)
        picture.save(EVIDENCE/'installer-welcome.png')
        check('nonblank-render',any(high-low>80 for low,high in picture.getextrema()),picture.getextrema())
    finally:
        g.SelectObject(dc,old);g.DeleteObject(bmp);g.DeleteDC(dc)
    check('welcome-does-not-extract',not list(temp.iterdir()),str(temp))
finally:
    if proc.poll() is None:
        if 'main' in locals():u.PostMessageW(main,16,0,0)
        try:proc.wait(timeout=4)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=4)
    log['exit']=proc.returncode
    (EVIDENCE/'installer-smoke.json').write_text(json.dumps(log,indent=2))
check('close-welcome',proc.returncode==0,proc.returncode)
