# The FFI tests' C objects

`tests/r32/test_ffi.py`, `tests/r33/test_ffi_kinds.py`, `tools/fuzz_ffi.py` and `tools/fuzz_elf2smo.py` read
these ELF objects as **committed inputs**, so the gates need no C compiler. Until R34 they were never
committed - `.gitignore` has `*.o` - and on a fresh clone all four gates failed with *patram na udghatitam*.
`.gitignore` now excepts `tests/r32/*.o` and `tests/r33/*.o`.

Built on 2026-10-21 with **gcc 13.3.0** (Ubuntu 13.3.0-6ubuntu2~24.04.1), from the `.c` file of the same name,
with the flags `docs/OBJECT-FORMAT.md` documents for foreign code:

```
gcc -c -O2 -ffreestanding -fno-asynchronous-unwind-tables -fno-pic -fno-stack-protector X.c -o X.o
gcc -c -O2 -ffreestanding -fno-pic -fno-stack-protector tests/r32/foreign.c -o tests/r32/foreign-unwind.o   # unwind tables on purpose: the reader must refuse it
```

```
c5d788f4c7b2b92321d50b207690835838fd796e285abcf50c62b9b1a889266c  tests/r32/foreign.o
69ea73173869b8cf06fadb3c09dd006bd5dbba8fb25d39743fd981608b1c766b  tests/r32/foreign-unwind.o
8eb0ad3e1f8a5552e701e589ce634dee0a13fdeff5b85cb8acd7842406c68974  tests/r32/negative.o
af7371a095a10081a63fd55dfe2e9d40ea834ed4ec1ae75d8dd0a2eb226caceb  tests/r33/kinds.o
135dc73c77863595036563d8d42f2d4e0c04c0ae7d4da6a4824b9384ccdf9715  tests/r33/align16.o
f617ba56dddf2992fb69f4b09eba228d891acf3c1283091104cd4139c3ada726  tests/r33/mid.o
21f78aa1e0193f55ab00cbc866d4edcc9e55e6e40692914d6cf983f057ab947d  tests/r33/mid-other.o
```

With exactly these files, on main's v242 and on R34's v243 alike: R32 FFI 44 checks, R33 FFI kinds 29 checks,
the FFI fuzzer and the ELF-reader fuzzer all PASS (`Claude-to-Sarvam/evidence-r34/gates-linux.txt`). The
objects R32 and R33 were first proved with (possibly built by zig cc) were not kept, so these are not
claimed to be byte-identical to those - only to pass the same gates.
