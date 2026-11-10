#!/usr/bin/env python3
"""R179 WS1: what madvise(MADV_DONTNEED) buys and costs on the mapping Sutram's field is.
The field: mmap(1 GiB, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS|MAP_NORESERVE) - the flags of r65_t5 / r101a_a1.
For each span (at the top of the mapping, where a block's memory is): write every byte (memset, as a block's
nirmmita does), read VmRSS; write it all again (a later block reusing resident pages: the "keep" cost);
madvise(DONTNEED) the span, timed; read VmRSS; check it reads 0; write it all again (the "after a discard" cost).
Times are the best of 5. This is a C-level measurement driven from Python (libc memset / madvise through ctypes);
it is not a Sutram program and no compiler was changed."""
import ctypes, mmap, time, sys
libc = ctypes.CDLL(None, use_errno=True)
libc.mmap.restype = ctypes.c_void_p
libc.mmap.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_long]
libc.madvise.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_int]
libc.memset.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t]
GIB = 1 << 30
base = libc.mmap(None, GIB, 3, 0x4022, -1, 0)
assert base and base != ctypes.c_void_p(-1).value
def rss():
    for l in open('/proc/self/status'):
        if l.startswith('VmRSS'): return int(l.split()[1])
def t(f):
    a = time.perf_counter(); f(); return (time.perf_counter() - a) * 1000
print(f'page size {mmap.PAGESIZE}; baseline VmRSS {rss():,} KB')
print('span      | VmRSS written | write again, kept | madvise | VmRSS after | reads 0 | write again, discarded | extra per page')
for mib in (1, 4, 16, 64, 256, 512):
    n = mib << 20; a = base + GIB - n; pages = n // 4096
    best = {'keep': 1e9, 'madv': 1e9, 'cold': 1e9}
    for _ in range(5):
        libc.memset(a, 0x4d, n); r1 = rss()
        best['keep'] = min(best['keep'], t(lambda: libc.memset(a, 0, n)))
        libc.memset(a, 0x4d, n)
        best['madv'] = min(best['madv'], t(lambda: libc.madvise(a, n, 4)))
        r2 = rss()
        zero = ctypes.string_at(a, 4096) == b'\0' * 4096 and ctypes.string_at(a + n - 4096, 4096) == b'\0' * 4096
        best['cold'] = min(best['cold'], t(lambda: libc.memset(a, 0, n)))
        libc.madvise(a, n, 4)
    extra = (best['cold'] + best['madv'] - best['keep']) * 1e6 / pages
    print(f'{mib:4d} MiB | {r1:>10,} KB | {best["keep"]:9.3f} ms | {best["madv"]:7.3f} ms | {r2:>8,} KB | {str(zero):5} | {best["cold"]:9.3f} ms | {extra:6.0f} ns')
