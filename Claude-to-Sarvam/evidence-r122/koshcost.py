#!/usr/bin/env python3
"""R122 WS2: what N kosh cost, measured. The program makes N kosh (each in a loop body: its region is kept for the
program's life, as every kosh region is), pushes E elements into each, prints 'ready', and waits on grahan; this
script then reads /proc/PID/status (VmPeak/VmSize = address space; VmHWM/VmRSS = resident) and /proc/PID/maps
(the mapping count), and lets it finish. A baseline with N = 0 is subtracted for the per-kosh cost."""
import os, subprocess, sys, tempfile
COMP = sys.argv[1] if len(sys.argv) > 1 else '<repo>/sutram_compiler'
d = tempfile.mkdtemp(dir=os.path.dirname(os.path.abspath(__file__)))
def measure(n, e):
    src = os.path.join(d, f'k{n}_{e}.sm'); exe = src[:-3] + '.bin'
    open(src, 'w').write(f'''mukhya() {{
    vitti t = 0
    chakra i = 1 tak {n} {{
        kosh k[1]
        chakra j = 1 tak {e} {{
            kosh_kship(k, j)
        }}
        t = t + kosh_gan(k)
    }}
    likha("ready ", t, "\\n")
    vitti x = grahan()
}}
''' if n else 'mukhya() {\n    likha("ready ", 0, "\\n")\n    vitti x = grahan()\n}\n')
    r = subprocess.run([COMP, src, exe], capture_output=True, text=True)
    if r.returncode: return None, r.stdout[-200:]
    p = subprocess.Popen([exe], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    line = p.stdout.readline()
    st = dict(l.split(':', 1) for l in open(f'/proc/{p.pid}/status').read().splitlines() if ':' in l)
    maps = sum(1 for _ in open(f'/proc/{p.pid}/maps'))
    p.stdin.write('1\n'); p.stdin.flush(); p.wait()
    kb = lambda k: int(st[k].split()[0])
    return dict(peak_vm=kb('VmPeak'), vm=kb('VmSize'), hwm=kb('VmHWM'), rss=kb('VmRSS'), maps=maps, out=line.strip()), None
base, _ = measure(0, 0)
print(f"# {subprocess.run([COMP,'--version'],capture_output=True,text=True).stdout.splitlines()[0]}, Linux ELF. KB from /proc/PID/status at the end of the program.")
print(f"baseline (no kosh): VmPeak {base['peak_vm']} KB, VmHWM {base['hwm']} KB, {base['maps']} mappings")
print(f"{'kosh':>6} {'elements each':>14} | {'address space (VmPeak)':>24} | {'resident peak (VmHWM)':>22} | {'per kosh: address':>18} {'resident':>9} | mappings")
for e in (1, 100, 10000):
    for n in (1, 10, 100, 1000):
        m, err = measure(n, e)
        if not m: print(f'{n:6d} {e:14d} | FAILED {err}'); continue
        dv = m['peak_vm'] - base['peak_vm']; dr = m['hwm'] - base['hwm']
        print(f"{n:6d} {e:14d} | {m['peak_vm']:>18,} KB ({m['peak_vm']/1048576:6.1f} GiB) | {m['hwm']:>19,} KB | {dv/n/1024:>14.1f} MiB {dr/n:>7.1f} KB | {m['maps']}")
