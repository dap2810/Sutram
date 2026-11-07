"""Read/inject keys only in the specified installer's child console."""
import ctypes as C
from ctypes import wintypes as W
import json, sys
from pathlib import Path

k=C.WinDLL('kernel32',use_last_error=True)
def api(n,r,a):
    f=getattr(k,n); f.restype=r; f.argtypes=a; return f
class Coord(C.Structure): _fields_=[('x',W.SHORT),('y',W.SHORT)]
class Rect(C.Structure): _fields_=[('left',W.SHORT),('top',W.SHORT),('right',W.SHORT),('bottom',W.SHORT)]
class Info(C.Structure): _fields_=[('size',Coord),('cursor',Coord),('attr',W.WORD),('window',Rect),('max',Coord)]
class Key(C.Structure):
    _fields_=[('down',W.BOOL),('repeat',W.WORD),('vk',W.WORD),('scan',W.WORD),('char',W.WCHAR),('ctrl',W.DWORD)]
class Event(C.Union): _fields_=[('key',Key),('padding',C.c_byte*16)]
class Input(C.Structure): _fields_=[('type',W.WORD),('event',Event)]
attach=api('AttachConsole',W.BOOL,[W.DWORD]); free=api('FreeConsole',W.BOOL,[])
openfile=api('CreateFileW',W.HANDLE,[W.LPCWSTR,W.DWORD,W.DWORD,C.c_void_p,W.DWORD,W.DWORD,W.HANDLE])
close=api('CloseHandle',W.BOOL,[W.HANDLE]); win=api('GetConsoleWindow',W.HWND,[])
getinfo=api('GetConsoleScreenBufferInfo',W.BOOL,[W.HANDLE,C.POINTER(Info)])
read=api('ReadConsoleOutputCharacterW',W.BOOL,[W.HANDLE,W.LPWSTR,W.DWORD,Coord,C.POINTER(W.DWORD)])
write=api('WriteConsoleInputW',W.BOOL,[W.HANDLE,C.POINTER(Input),W.DWORD,C.POINTER(W.DWORD)])
pid,mode,target=int(sys.argv[1]),sys.argv[2],Path(sys.argv[3])
row=dict(pid=pid,mode=mode)
try:
    free()
    if not attach(pid): raise C.WinError(C.get_last_error())
    row['console_hwnd']=win()
    handle=openfile('CONOUT$',0x80000000,3,None,3,0,None)
    if handle==C.c_void_p(-1).value: raise C.WinError(C.get_last_error())
    try:
        info=Info()
        if not getinfo(handle,C.byref(info)): raise C.WinError(C.get_last_error())
        lines=min(info.cursor.y+1,400)
        origin=Coord(0,max(0,info.cursor.y+1-lines)); size=info.size.x*lines
        buffer=C.create_unicode_buffer(size+1); count=W.DWORD()
        if not read(handle,buffer,size,origin,C.byref(count)): raise C.WinError(C.get_last_error())
        text=buffer[:count.value]
        row['text']='\n'.join(text[i:i+info.size.x].rstrip() for i in range(0,len(text),info.size.x)).rstrip()
    finally: close(handle)
    if mode!='read':
        chars={'enter':'\r','yes':'Y\r'}[mode]
        handle=openfile('CONIN$',0xC0000000,3,None,3,0,None)
        if handle==C.c_void_p(-1).value: raise C.WinError(C.get_last_error())
        try:
            events=(Input*(len(chars)*2))()
            for i,ch in enumerate(chars):
                for j,down in enumerate((True,False)):
                    e=events[2*i+j]; e.type=1; e.event.key=Key(down,1,13 if ch=='\r' else 89,0,ch,0)
            count=W.DWORD()
            if not write(handle,events,len(events),C.byref(count)): raise C.WinError(C.get_last_error())
            row['input_events_written']=count.value
        finally: close(handle)
except Exception as exc: row['error']=str(exc)
finally:
    free()
    target.write_text(json.dumps(row,indent=2)+'\n',encoding='utf8')
print(json.dumps({k:v for k,v in row.items() if k!='text'}))
