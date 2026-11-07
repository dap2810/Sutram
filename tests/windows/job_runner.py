"""Bound one native Windows child by commit charge, without changing host limits."""
import ctypes as C
from ctypes import wintypes as W
from pathlib import Path
import msvcrt
import os
import subprocess
import time

SIZE = C.c_size_t

class BasicLimits(C.Structure):
    _fields_ = [('ProcessTime', C.c_int64), ('JobTime', C.c_int64), ('Flags', W.DWORD),
                ('MinWS', SIZE), ('MaxWS', SIZE), ('Active', W.DWORD), ('Affinity', SIZE),
                ('Priority', W.DWORD), ('Scheduling', W.DWORD)]

class IOCounters(C.Structure):
    _fields_ = [(n, C.c_uint64) for n in ('readOps', 'writeOps', 'otherOps', 'readBytes', 'writeBytes', 'otherBytes')]

class ExtendedLimits(C.Structure):
    _fields_ = [('Basic', BasicLimits), ('IO', IOCounters), ('ProcessMemory', SIZE),
                ('JobMemory', SIZE), ('PeakProcess', SIZE), ('PeakJob', SIZE)]

class Startup(C.Structure):
    _fields_ = [('cb', W.DWORD), ('reserved', W.LPWSTR), ('desktop', W.LPWSTR), ('title', W.LPWSTR),
                ('x', W.DWORD), ('y', W.DWORD), ('xSize', W.DWORD), ('ySize', W.DWORD),
                ('xChars', W.DWORD), ('yChars', W.DWORD), ('fill', W.DWORD), ('flags', W.DWORD),
                ('show', W.WORD), ('reserved2Size', W.WORD), ('reserved2', C.c_void_p),
                ('stdin', W.HANDLE), ('stdout', W.HANDLE), ('stderr', W.HANDLE)]

class ProcessInfo(C.Structure):
    _fields_ = [('process', W.HANDLE), ('thread', W.HANDLE), ('pid', W.DWORD), ('tid', W.DWORD)]

kernel = C.WinDLL('kernel32', use_last_error=True)

def api(name, result, args):
    fn = getattr(kernel, name)
    fn.restype, fn.argtypes = result, args
    return fn

create_job = api('CreateJobObjectW', W.HANDLE, [C.c_void_p, W.LPCWSTR])
set_job = api('SetInformationJobObject', W.BOOL, [W.HANDLE, C.c_int, C.c_void_p, W.DWORD])
query_job = api('QueryInformationJobObject', W.BOOL, [W.HANDLE, C.c_int, C.c_void_p, W.DWORD, C.c_void_p])
assign = api('AssignProcessToJobObject', W.BOOL, [W.HANDLE, W.HANDLE])
create = api('CreateProcessW', W.BOOL, [W.LPCWSTR, W.LPWSTR, C.c_void_p, C.c_void_p, W.BOOL,
                                     W.DWORD, C.c_void_p, W.LPCWSTR, C.POINTER(Startup), C.POINTER(ProcessInfo)])
resume = api('ResumeThread', W.DWORD, [W.HANDLE])
wait = api('WaitForSingleObject', W.DWORD, [W.HANDLE, W.DWORD])
get_exit = api('GetExitCodeProcess', W.BOOL, [W.HANDLE, C.POINTER(W.DWORD)])
terminate = api('TerminateProcess', W.BOOL, [W.HANDLE, W.UINT])
close = api('CloseHandle', W.BOOL, [W.HANDLE])

def checked(value):
    if not value:
        raise C.WinError(C.get_last_error())
    return value

def run_limited(executable, directory, limit_mib, timeout=60, invalid_stderr=False):
    """Capture one process; assign its Job before any executable instruction runs."""
    executable, directory = Path(executable).resolve(), Path(directory).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    job = checked(create_job(None, None))
    info = ProcessInfo()
    result = {'command': [str(executable)], 'cwd': str(directory),
              'limit_bytes': limit_mib * 1024 * 1024, 'timeout_seconds': timeout,
              'invalid_stderr': invalid_stderr}
    start = time.perf_counter()
    try:
        limits = ExtendedLimits()
        limits.Basic.Flags = 0x100 | 0x2000  # PROCESS_MEMORY | KILL_ON_JOB_CLOSE
        limits.ProcessMemory = result['limit_bytes']
        checked(set_job(job, 9, C.byref(limits), C.sizeof(limits)))
        actual = ExtendedLimits()
        checked(query_job(job, 9, C.byref(actual), C.sizeof(actual), None))
        if actual.ProcessMemory != limits.ProcessMemory or actual.Basic.Flags != limits.Basic.Flags:
            raise RuntimeError('Windows Job did not retain the requested limit')
        with open(directory/'stdout', 'wb') as out, open(directory/'stderr', 'wb') as err, open(os.devnull, 'rb') as inp:
            startup = Startup()
            startup.cb, startup.flags = C.sizeof(startup), 0x100  # USESTDHANDLES
            handles = [msvcrt.get_osfhandle(f.fileno()) for f in (inp, out, err)]
            for handle in handles:
                os.set_handle_inheritable(handle, True)
            startup.stdin, startup.stdout, startup.stderr = handles
            if invalid_stderr:
                startup.stderr = W.HANDLE(-1)
            try:
                command = C.create_unicode_buffer(subprocess.list2cmdline([str(executable)]))
                checked(create(str(executable), command, None, None, True,
                               0x4 | 0x08000000, None, str(directory), C.byref(startup), C.byref(info)))
            finally:
                for handle in handles:
                    os.set_handle_inheritable(handle, False)
            checked(assign(job, info.process))
            if resume(info.thread) == 0xFFFFFFFF:
                raise C.WinError(C.get_last_error())
            status = wait(info.process, timeout * 1000)
            result['timed_out'] = status == 258
            if status == 258:
                checked(terminate(info.process, 124))
                wait(info.process, 3000)
            elif status != 0:
                raise C.WinError(C.get_last_error())
            code = W.DWORD()
            checked(get_exit(info.process, C.byref(code)))
            result['exit'] = code.value
            # R136: the commit the process reached, and what the limit left at that peak - the number a
            # teardown's stack page is measured against (Muse R137), not the limit itself.
            peak = ExtendedLimits()
            if query_job(job, 9, C.byref(peak), C.sizeof(peak), None):
                result['peak_process_bytes'] = peak.PeakProcess
                result['peak_job_bytes'] = peak.PeakJob
                result['headroom_bytes'] = result['limit_bytes'] - peak.PeakProcess
        result['stdout'] = (directory/'stdout').read_text(encoding='utf8', errors='replace')
        result['stderr'] = (directory/'stderr').read_text(encoding='utf8', errors='replace')
        return result
    except BaseException:
        if info.process:
            terminate(info.process, 125)
            wait(info.process, 3000)
        raise
    finally:
        if info.thread:
            close(info.thread)
        if info.process:
            close(info.process)
        close(job)
        result['elapsed_seconds'] = round(time.perf_counter() - start, 4)
