"""Measure Windows private commit and working set while a native probe waits on stdin."""
import ctypes as C,json,subprocess
from ctypes import wintypes as W
from pathlib import Path
h=Path(__file__).resolve().parent;root=h.parents[1];c=root/'build/round3/final-windows/compiler.exe'
class Counters(C.Structure):
 _fields_=[('cb',W.DWORD),('PageFaultCount',W.DWORD)]+[(n,C.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
api=C.WinDLL('psapi');api.GetProcessMemoryInfo.argtypes=[W.HANDLE,C.POINTER(Counters),W.DWORD];api.GetProcessMemoryInfo.restype=W.BOOL
rows=[]
for name,body in [('empty',''),('arena','vitti p=nirmmita(64)'),('one_kosh','kosh k[1] kosh_push(k,41)'),('arena_two_kosh','vitti p=nirmmita(64) kosh k[1] kosh m[1]')]:
 src=h/'programs'/('cost_'+name+'.sm');src.write_text('mukhya() { '+body+' likha("ready\\n") vitti n=grahan() }\n',encoding='utf8')
 target=c.parent/('cost_'+name+'.exe');cmd=[str(c),str(src),str(target)];subprocess.run(cmd,check=True,capture_output=True)
 with subprocess.Popen([str(target)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as p:
  assert p.stdout.readline().strip()==b'ready'
  mem=Counters();mem.cb=C.sizeof(mem)
  if not api.GetProcessMemoryInfo(W.HANDLE(int(p._handle)),C.byref(mem),mem.cb):raise C.WinError()
  out,err=p.communicate(b'0\n',timeout=10)
  rows.append(dict(name=name,command=cmd,run_command=[str(target)],exit=p.returncode,counters={n:getattr(mem,n) for n,_ in mem._fields_}))
(h/'cost-windows.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print(json.dumps(rows,indent=2))
