"""Run the unchanged B3 executable with a per-process Windows Job commit limit."""
import ctypes as C
from ctypes import wintypes as W
import json, msvcrt, os, subprocess, sys, time
from verify import HERE, WORK, check_identity, digest, save

check_identity()
k = C.WinDLL('kernel32', use_last_error=True)
SIZE = C.c_size_t
class BASIC(C.Structure):
    _fields_ = [('ProcessTime', C.c_int64), ('JobTime', C.c_int64), ('Flags', W.DWORD),
                ('MinWS', SIZE), ('MaxWS', SIZE), ('Active', W.DWORD), ('Affinity', SIZE),
                ('Priority', W.DWORD), ('Scheduling', W.DWORD)]
class IOC(C.Structure):
    _fields_ = [(n, C.c_uint64) for n in ('readOps','writeOps','otherOps','readBytes','writeBytes','otherBytes')]
class LIMITS(C.Structure):
    _fields_ = [('Basic', BASIC), ('IO', IOC), ('ProcessMemory', SIZE), ('JobMemory', SIZE),
                ('PeakProcess', SIZE), ('PeakJob', SIZE)]
class STARTUP(C.Structure):
    _fields_ = [('cb', W.DWORD), ('reserved', W.LPWSTR), ('desktop', W.LPWSTR), ('title', W.LPWSTR),
                ('x', W.DWORD), ('y', W.DWORD), ('xSize', W.DWORD), ('ySize', W.DWORD),
                ('xChars', W.DWORD), ('yChars', W.DWORD), ('fill', W.DWORD), ('flags', W.DWORD),
                ('show', W.WORD), ('reserved2Size', W.WORD), ('reserved2', C.c_void_p),
                ('stdin', W.HANDLE), ('stdout', W.HANDLE), ('stderr', W.HANDLE)]
class PROCESS(C.Structure):
    _fields_ = [('process', W.HANDLE), ('thread', W.HANDLE), ('pid', W.DWORD), ('tid', W.DWORD)]

def api(name, result, args):
    fn = getattr(k, name); fn.restype = result; fn.argtypes = args; return fn
create_job = api('CreateJobObjectW', W.HANDLE, [C.c_void_p, W.LPCWSTR])
set_job = api('SetInformationJobObject', W.BOOL, [W.HANDLE, C.c_int, C.c_void_p, W.DWORD])
assign = api('AssignProcessToJobObject', W.BOOL, [W.HANDLE, W.HANDLE])
create = api('CreateProcessW', W.BOOL, [W.LPCWSTR,W.LPWSTR,C.c_void_p,C.c_void_p,W.BOOL,W.DWORD,C.c_void_p,W.LPCWSTR,C.POINTER(STARTUP),C.POINTER(PROCESS)])
resume = api('ResumeThread', W.DWORD, [W.HANDLE])
wait = api('WaitForSingleObject', W.DWORD, [W.HANDLE, W.DWORD])
exitcode = api('GetExitCodeProcess', W.BOOL, [W.HANDLE, C.POINTER(W.DWORD)])
terminate = api('TerminateProcess', W.BOOL, [W.HANDLE,W.UINT])
close = api('CloseHandle', W.BOOL, [W.HANDLE])

def checked(value):
    if not value: raise C.WinError(C.get_last_error())
    return value

job = checked(create_job(None, None))
info = PROCESS()
test = sys.argv[1] if len(sys.argv) > 1 else 'B3'
limit_mib = int(sys.argv[2]) if len(sys.argv) > 2 else 128
assert test in ('B1','B2','B3') and limit_mib in (64,128,256,2048)
target = WORK / (test + '.exe')
record = {'test':f'{test}-under-{limit_mib}MiB-commit-limit','executable':str(target),
          'executable_sha256':digest(target),'process_commit_limit_bytes':limit_mib*1024*1024,
          'timeout_seconds':60,'command':[str(target)],'mechanism':'Windows Job Object, process memory limit; child assigned while suspended'}
start = time.perf_counter()
try:
    limits = LIMITS(); limits.Basic.Flags = 0x100 | 0x2000
    limits.ProcessMemory = record['process_commit_limit_bytes']
    checked(set_job(job, 9, C.byref(limits), C.sizeof(limits)))
    with open(WORK/'oom.stdout', 'wb') as out, open(WORK/'oom.stderr', 'wb') as err, open(os.devnull, 'rb') as inp:
        si = STARTUP(); si.cb = C.sizeof(si); si.flags = 0x100
        handles = [msvcrt.get_osfhandle(f.fileno()) for f in (inp,out,err)]
        for h in handles: os.set_handle_inheritable(h, True)
        si.stdin,si.stdout,si.stderr = handles
        try:
            checked(create(str(target),C.create_unicode_buffer(subprocess.list2cmdline([str(target)])),None,None,True,
                           0x4 | 0x08000000,None,str(WORK),C.byref(si),C.byref(info)))
        finally:
            for h in handles: os.set_handle_inheritable(h, False)
        checked(assign(job, info.process))
        if resume(info.thread) == 0xFFFFFFFF: raise C.WinError(C.get_last_error())
        result = wait(info.process, 60000)
        record['timed_out'] = result == 258
        if result == 258: checked(terminate(info.process, 124)); wait(info.process, 3000)
        elif result != 0: raise C.WinError(C.get_last_error())
        code = W.DWORD(); checked(exitcode(info.process,C.byref(code)))
        record['exit'] = code.value
    record['stdout'] = (WORK/'oom.stdout').read_text(encoding='utf8',errors='replace')
    record['stderr'] = (WORK/'oom.stderr').read_text(encoding='utf8',errors='replace')
    record['graceful_oom'] = record['exit'] == 1 and (record['stdout']+record['stderr']).startswith('Sutram truti: kosh vardhayitum smritih na labdha') and not record['timed_out']
except Exception as e:
    record['error'] = str(e)
    if info.process: terminate(info.process, 125); wait(info.process, 3000)
    raise
finally:
    if info.thread: close(info.thread)
    if info.process: close(info.process)
    close(job)
    record['elapsed_seconds'] = round(time.perf_counter()-start,4)
    save(f'oom-{test}-{limit_mib}MiB.json', record)
print(json.dumps(record,indent=2))
