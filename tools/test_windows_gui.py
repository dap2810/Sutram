"""Native GUI smoke test restricted to a freshly launched review executable."""
from pathlib import Path
import ctypes as C
from ctypes import wintypes as W
import subprocess,time,os,json,sys
sys.stdout.reconfigure(encoding="utf-8")
# Process-local error mode inherited only by our test children.
import ctypes
ctypes.windll.kernel32.SetErrorMode(0x8003)
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=Path(os.environ.get('SUTRAM_EVIDENCE',str(ROOT/'build/windows/evidence')))
EVIDENCE.mkdir(parents=True,exist_ok=True)
u=C.WinDLL('user32',use_last_error=True)
CB=C.WINFUNCTYPE(W.BOOL,W.HWND,W.LPARAM)
u.EnumWindows.argtypes=[CB,W.LPARAM];u.EnumChildWindows.argtypes=[W.HWND,CB,W.LPARAM]
u.GetWindowThreadProcessId.argtypes=[W.HWND,C.POINTER(W.DWORD)]
u.GetDlgCtrlID.argtypes=[W.HWND];u.GetDlgCtrlID.restype=C.c_int
u.GetClassNameW.argtypes=[W.HWND,W.LPWSTR,C.c_int]
u.SendMessageTimeoutW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM,W.UINT,W.UINT,C.POINTER(C.c_size_t)]
u.SendMessageTimeoutW.restype=W.LPARAM
u.PostMessageW.argtypes=[W.HWND,W.UINT,W.WPARAM,W.LPARAM]
def send(h,msg,w=0,l=0,timeout=25000):
    result=C.c_size_t()
    if not u.SendMessageTimeoutW(h,msg,w,l,2,timeout,C.byref(result)):
        raise RuntimeError(f'Window message timed out/error: {msg}, {C.get_last_error()}')
    return result.value
def text(h):
    b=C.create_unicode_buffer(65536)
    send(h,13,len(b),C.addressof(b))
    return b.value
env=os.environ.copy()
temp=ROOT/'build/windows/gui-temp';temp.mkdir(exist_ok=True)
env['TEMP']=env['TMP']=str(temp)
startup=ROOT/'build/windows/gui-startup.sm'
startup.write_text('mukhya() {\n    likha("ARGV_OPEN_OK\\n")\n}\n',encoding='utf8')
si=subprocess.STARTUPINFO();si.dwFlags=1;si.wShowWindow=0
cmd=[str(ROOT/'sutram-ide-gui.exe'),str(startup)]
proc=subprocess.Popen(cmd,cwd=ROOT,env=env,startupinfo=si)
log={'command':cmd,'pid':proc.pid,'checks':[]}
def check(name,condition,detail):
    log['checks'].append({'check':name,'pass':bool(condition),'detail':detail})
    print(name,condition,str(detail)[:250],flush=True)
    if not condition:raise AssertionError(name)
try:
    windows=[]
    @CB
    def collect(h,l):
        pid=W.DWORD();u.GetWindowThreadProcessId(h,C.byref(pid))
        if pid.value==proc.pid:
            b=C.create_unicode_buffer(256);u.GetClassNameW(h,b,256)
            if b.value=='SutramNativeGUIWindow':windows.append(h)
        return True
    for _ in range(50):
        u.EnumWindows(collect,0)
        if windows:break
        if proc.poll() is not None:raise RuntimeError(f'GUI exited {proc.returncode}')
        time.sleep(.1)
    check('window',len(windows)==1,windows)
    main=windows[0];controls={}
    @CB
    def children(h,l):
        ident=u.GetDlgCtrlID(h)
        if ident:controls[ident]=h
        return True
    u.EnumChildWindows(main,children,0)
    check('editor/output/run',all(i in controls for i in [201,203,101]),sorted(controls))
    check('argv-open','ARGV_OPEN_OK' in text(controls[201]),text(controls[201]))
    send(main,0x111,101)
    output=text(controls[203])
    check('run-button','ARGV_OPEN_OK' in output,output)
    source='mukhya() {\r\n    likha("GUI_UTF8_\\u0928\\u092e\\u0938\\u094d\\u0924\\u0947\\n")\r\n    likha(42)\r\n}\r\n'
    source=source.replace(r'\u0928',chr(0x928)).replace(r'\u092e',chr(0x92e)).replace(r'\u0938',chr(0x938)).replace(r'\u094d',chr(0x94d)).replace(r'\u0924',chr(0x924)).replace(r'\u0947',chr(0x947))
    b=C.create_unicode_buffer(source)
    send(controls[201],12,0,C.addressof(b))
    check('unicode-editor',text(controls[201]).replace('\r\n','\n')==source.replace('\r\n','\n'),text(controls[201]))
    send(main,0x111,2010)
    output=text(controls[203])
    check('menu-run','GUI_UTF8_' in output and '42' in output and '\u0928\u092e\u0938\u094d\u0924\u0947' in output,output)
    rect=W.RECT()
    u.GetClientRect.argtypes=[W.HWND,C.POINTER(W.RECT)]
    u.GetClientRect(controls[201],C.byref(rect))
    check('editor-layout',rect.right>300 and rect.bottom>100,[rect.right,rect.bottom])
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
        check('window-render',u.PrintWindow(main,dc,2)!=0,[width,height])
        Image.frombuffer('RGB',(width,height),C.string_at(bits,width*height*4),'raw','BGRX',0,1).save(EVIDENCE/'ide-native.png')
    finally:
        g.SelectObject(dc,old);g.DeleteObject(bmp);g.DeleteDC(dc)
    # Check actual RichEdit formatting, including offsets after line breaks.
    palette='mukhya() {\r\n    likha(42)\r\n    custom() \"green\" # comment\r\n    '+chr(0x964)+'\r\n}\r\n'
    b=C.create_unicode_buffer(palette)
    send(controls[201],12,0,C.addressof(b))
    positions=palette.replace('\r\n','\r')
    # WM_USER messages do not marshal pointers across processes. Allocate
    # only a CHARFORMAT data buffer in our own freshly spawned child.
    k=C.WinDLL('kernel32',use_last_error=True)
    k.OpenProcess.argtypes=[W.DWORD,W.BOOL,W.DWORD];k.OpenProcess.restype=W.HANDLE
    k.VirtualAllocEx.argtypes=[W.HANDLE,C.c_void_p,C.c_size_t,W.DWORD,W.DWORD];k.VirtualAllocEx.restype=C.c_void_p
    k.WriteProcessMemory.argtypes=[W.HANDLE,C.c_void_p,C.c_void_p,C.c_size_t,C.c_void_p]
    k.ReadProcessMemory.argtypes=k.WriteProcessMemory.argtypes
    k.VirtualFreeEx.argtypes=[W.HANDLE,C.c_void_p,C.c_size_t,W.DWORD]
    k.CloseHandle.argtypes=[W.HANDLE]
    handle=k.OpenProcess(0x38,False,proc.pid)
    assert handle
    remote=k.VirtualAllocEx(handle,None,60,0x3000,4)
    assert remote
    try:
        for token,color in [('mukhya',0x00116DE8),('likha',0x00B0C94E),('42',0x00E886B5),('custom',0x0027A2C9),('green',0x0055996A),('# comment',0x006A6A6A),(chr(0x964),0x00E6D45C)]:
            start=positions.index(token)
            send(controls[201],0xB1,start,start+1)
            fmt=C.create_string_buffer(60)
            struct.pack_into('<I',fmt,0,60)
            assert k.WriteProcessMemory(handle,remote,fmt,60,None)
            send(controls[201],0x43A,1,remote)
            assert k.ReadProcessMemory(handle,remote,fmt,60,None)
            observed=struct.unpack_from('<I',fmt,20)[0]
            check('color-'+token,observed==color,{'expected':hex(color),'actual':hex(observed)})
    finally:
        k.VirtualFreeEx(handle,remote,0,0x8000);k.CloseHandle(handle)
    b=C.create_unicode_buffer('mukhya() { vitti x = }\r\n')
    send(controls[201],12,0,C.addressof(b))
    send(main,0x111,101)
    output=text(controls[203])
    check('compiler-error','Error' in output or 'failed' in output,output)
    # ---- R73: Sanskrit interface, editor keys, status line, bhasha pack, icon ----
    labels={i:text(controls[i]) for i in (101,102,103,104,105,106)}
    check('button-labels',labels=={101:'chal',102:'khol',103:'sanchay',104:'udaharan khol',105:'presh',106:'phal_rikta'},labels)
    check('status-line',206 in controls and 'pankti' in text(controls[206]) and 'bhasha' in text(controls[206]),text(controls[206]) if 206 in controls else None)
    check('title-sanskrit','Sutram sampadak' in text(main) and ' *' in text(main),text(main))
    def set_editor(s):
        b=C.create_unicode_buffer(s);send(controls[201],12,0,C.addressof(b))
    def caret_end():
        send(controls[201],0xB1,10**6,10**6)
    def editor():
        return text(controls[201]).replace('\r\n','\n')
    set_editor('mukhya() {\r\n');caret_end()
    send(controls[201],0x100,9,0);send(controls[201],0x102,9,0)      # Tab key: WM_KEYDOWN + WM_CHAR
    check('tab-indent',editor()=='mukhya() {\n    ',repr(editor()))
    set_editor('mukhya() {');caret_end()
    send(controls[201],0x100,13,0);send(controls[201],0x102,13,0)    # Enter after '{'
    check('enter-autoindent',editor()=='mukhya() {\n    ',repr(editor()))
    send(controls[201],0x102,0x7D,0)                                  # '}' on the blank indented line
    check('brace-dedent',editor()=='mukhya() {\n}',repr(editor()))
    set_editor('    likha(1)');caret_end()
    send(main,0x111,2039)                                             # sampad > antar hatao
    check('menu-unindent',editor()=='likha(1)',repr(editor()))
    set_editor('mukhya() {\r\n    likha(1)\r\n    likha(2)\r\n}\r\n')
    send(controls[201],0xB1,11,30)
    send(main,0x111,2038)                                             # sampad > antar on a block
    check('block-indent',editor()=='mukhya() {\n        likha(1)\n        likha(2)\n}\n',repr(editor()))
    deva=(ROOT/'examples/218_sanskrit_devanagari.sm').read_text(encoding='utf8').replace('\n','\r\n')
    set_editor(deva);send(main,0x111,2010)                            # bhasha: swayam detects Devanagari
    output=text(controls[203])
    check('devanagari-swayam','योगः = 15' in output,output)
    check('status-pack','swayam (sanskrit)' in text(controls[206]),text(controls[206]))
    send(main,0x111,2041);send(main,0x111,2010)                       # bhasha: mool -> no pack -> must fail
    output=text(controls[203])
    check('devanagari-mool-fails','योगः = 15' not in output and ('Error' in output or 'asaphal' in output),output)
    send(main,0x111,2042);send(main,0x111,2010)                       # bhasha: sanskrit explicit
    output=text(controls[203])
    check('devanagari-sanskrit','योगः = 15' in output,output)
    send(main,0x111,2040)
    set_editor('mukhya() {\r\n    likha(7)\r\n}\r\n')
    b=C.create_unicode_buffer('likha');send(controls[207],12,0,C.addressof(b))
    send(controls[201],0xB1,0,0);send(main,0x111,2037)                # sampad > agrim anwesh
    check('find-moves-caret','pankti 2' in text(controls[206]),text(controls[206]))
    sh=C.WinDLL('shell32',use_last_error=True)
    sh.ExtractIconExW.argtypes=[W.LPCWSTR,C.c_int,C.c_void_p,C.c_void_p,W.UINT]
    check('icon-resource',sh.ExtractIconExW(str(ROOT/'sutram-ide-gui.exe'),-1,None,None,0)>=1,'ExtractIconExW count')
    set_editor(deva);send(main,0x111,2010)
    dc=g.CreateCompatibleDC(None);bits=C.c_void_p()
    bmp=g.CreateDIBSection(dc,bmi,0,C.byref(bits),None,0)
    old=g.SelectObject(dc,bmp)
    try:
        if u.PrintWindow(main,dc,2):
            Image.frombuffer('RGB',(width,height),C.string_at(bits,width*height*4),'raw','BGRX',0,1).save(EVIDENCE/'ide-sanskrit.png')
    finally:
        g.SelectObject(dc,old);g.DeleteObject(bmp);g.DeleteDC(dc)
finally:
    if proc.poll() is None:
        if 'main' in locals():u.PostMessageW(main,16,0,0)
        try:proc.wait(timeout=4)
        except subprocess.TimeoutExpired:proc.terminate();proc.wait(timeout=4)
    log['exit']=proc.returncode
    (EVIDENCE/'gui-smoke.json').write_text(json.dumps(log,indent=2,ensure_ascii=True))

