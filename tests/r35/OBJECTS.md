# The Windows FFI tests' C objects (COFF x64)

`tests/r35/test_ffi_windows.py`, `tests/r35/test_coff2smo.py` and `tools/fuzz_coff2smo.py` read these as
**committed inputs**, so the gates need no C compiler (`.gitignore` excepts `tests/r35/*.obj`).

Built on 2026-10-21, on the owner's Windows 11 PC, with **GCC 16.2.0 (Rev3, Built by MSYS2 project)** - the
UCRT64 toolchain, target `x86_64-w64-mingw32`, so the objects are COFF x64 with the Microsoft x64 ABI:

```
gcc -c -O2 -ffreestanding -fno-asynchronous-unwind-tables -fno-stack-protector X.c -o X.obj
gcc -c -O2 -ffreestanding -fno-stack-protector winffi.c -o winffi-unwind.obj   # unwind tables on purpose: refused
```

| Object | From | What it is for |
|---|---|---|
| `winffi.obj` | `winffi.c` | the 22 functions `winffi.sm` calls |
| `winffi-unwind.obj` | `winffi.c` | `.pdata`/`.xdata`: the reader refuses it |
| `callout.obj` | `callout.c` | calls an undefined function: refused |
| `writable.obj` | `writable.c` | writable data: refused |
| `dataptr.obj` | `dataptr.c` | a pointer table - `ADDR64` relocations in `.rdata`: refused |

```
26b72c469d3508cf3f590b323973561a20b483188ae4caec275ffbbd97cf1d91  winffi.obj
b74a089cbf761c10b19631cf2ca21b3ba9733bd232a3782b2e435562ea8c0fb6  winffi-unwind.obj
4ad0aaed52152cda15338983d2385ebed9285c0602097600acc734e4fecde8a3  callout.obj
63366924efd252253beeec0d387c937c3e569d12e843912de669755590d7f4e1  writable.obj
3b0918db6ca3baa194297d134061f4560fd5a19668f101c207d5aa5205de2d93  dataptr.obj
```

`winffi.obj`'s `.text` is 32-byte aligned and its `.rdata` 16; `w_neg` and `w_abs` read their 16-byte
constants with `xorpd`, which is why sutram-link aligns a PE's later objects (docs/OBJECT-FORMAT.md).
