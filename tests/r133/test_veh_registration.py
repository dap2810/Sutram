#!/usr/bin/env python3
"""R133 (ChatGPT R205-206 W1): if the Windows runtime cannot install its memory handler, the program stops with a
message and exit 1 - it does not run on and die at the first touch of reserved memory with no output.

rt_init (win/winrt_blob.asm) registers rt_veh with AddVectoredExceptionHandler; v300-v306 did not test the result.
Without the handler, the first touch of a reserved page (the arena, every kosh region) is an access violation that
nothing commits. Windows does not let a test make that API fail, so this builds a TEST runtime in a scratch copy of
src/ and win/ with -DR133_FAIL_VEH_REGISTRATION (the call's result forced to NULL), a compiler around it, and runs
one PE program under Wine:

  1. the shipped runtime: the program prints 100000 and exits 0;
  2. the test runtime (registration fails): no output, `Sutram truti: smriti-prabandhah na arabdhah` on stderr,
     exit 1;
  3. (R135) a test runtime whose every lazy commit fails (-DR135_FAIL_COMMIT): no output, `Sutram truti: smritih na
     labdha`, exit 1 - the out-of-memory exit, through the release of its 64 KiB reserve;
  4. (R137) the same with the start-up reserve also refused (-DR137_FAIL_RESERVE): the same message and exit - the
     fallback is the v307 exit, without the 64 KiB in hand;
  5. the tree's win/rtblob.inc is exactly what win/winrt_blob.asm builds (the test runtime is never committed).
Needs nasm, ld and /usr/lib/wine/wine64; without Wine the last line says NOT RUN.
Last line: "r133 handler registration: N checks, M failed".
"""
import os, shutil, struct, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WINE = '/usr/lib/wine/wine64'
PROG = 'mukhya() {\n    kosh k[1]\n    chakra i = 1 tak 100000 {\n        kosh_kship(k, i)\n    }\n    likha(kosh_gan(k))\n}\n'
MSG = 'Sutram truti: smriti-prabandhah na arabdhah'


def blob_inc(asm_dir, defines):
    out = os.path.join(asm_dir, 'rt.bin')
    subprocess.run(['nasm', '-f', 'bin', '-I.'] + defines + ['win/winrt_blob.asm', '-o', out], cwd=asm_dir, check=True)
    data = open(out, 'rb').read()
    off, size = struct.unpack('<II', data[-8:])
    lines = ['; Generated from win/winrt_blob.asm. Build metadata trailer is excluded.', f'RT_BLOB_LEN equ {size}',
             'RT_INIT_OFF equ 0', f'RT_SYSCALL_OFF equ {off}', 'rt_blob:']
    lines += ['db ' + ','.join(f'0x{x:02x}' for x in data[i:min(i + 16, size)]) for i in range(0, size, 16)]
    return '\n'.join(lines) + '\n'


def main():
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    work = tempfile.mkdtemp(prefix='r133-veh-')
    try:
        for d in ('src', 'win'):
            shutil.copytree(os.path.join(ROOT, d), os.path.join(work, d))
        check(blob_inc(work, []) == open(os.path.join(ROOT, 'win', 'rtblob.inc'), encoding='utf-8').read(),
              'win/rtblob.inc is what win/winrt_blob.asm builds')
        if not os.path.exists(WINE):
            print('r133 handler registration: NOT RUN (no Wine) - ' + f'{checks} checks, {fails} failed')
            return 0
        def test_compiler(define, name):
            return test_compiler2([define], name)

        def test_compiler2(defines, name):
            open(os.path.join(work, 'win', 'rtblob.inc'), 'w', encoding='utf-8').write(blob_inc(work, defines))
            obj, out = os.path.join(work, name + '.o'), os.path.join(work, name)
            subprocess.run(['nasm', '-f', 'elf64', '-I.', 'src/r68_compiler_entry.asm', '-o', obj], cwd=work, check=True)
            subprocess.run(['ld', '-o', out, obj], check=True)
            return out
        test_c = test_compiler('-DR133_FAIL_VEH_REGISTRATION', 'test_noveh')
        commit_c = test_compiler('-DR135_FAIL_COMMIT', 'test_nocommit')
        noreserve_c = test_compiler2(['-DR135_FAIL_COMMIT', '-DR137_FAIL_RESERVE'], 'test_noreserve')
        src = os.path.join(work, 'p.sm')
        open(src, 'w', encoding='utf-8').write(PROG)
        env = dict(os.environ, WINEDEBUG='-all')
        for label, comp, want_out, want_err, want_rc in (
                ('the shipped runtime', os.path.join(ROOT, 'sutram_compiler'), '100000\n', '', 0),
                ('a runtime whose handler registration fails', test_c, '', MSG + '\n', 1),
                ('a runtime whose every lazy commit fails (R135: the reserve is given back, then the message)',
                 commit_c, '', 'Sutram truti: smritih na labdha\n', 1),
                ('(R137) the same with no reserve to give back (it could not be had at start): the same exit',
                 noreserve_c, '', 'Sutram truti: smritih na labdha\n', 1)):
            exe = os.path.join(work, 'p.exe')
            if os.path.exists(exe):
                os.remove(exe)
            subprocess.run([comp, src, exe], cwd=ROOT, capture_output=True)
            if not os.path.exists(exe):
                check(False, f'{label}: the program compiles')
                continue
            r = subprocess.run([WINE, exe], capture_output=True, timeout=120, env=env)
            out = r.stdout.decode('utf-8', 'replace').replace('\r', '')
            err = r.stderr.decode('utf-8', 'replace').replace('\r', '')
            check(out == want_out and err == want_err and r.returncode == want_rc,
                  f'{label}: exit {r.returncode}, stdout {out!r}, stderr {err!r} (want {want_rc}, {want_out!r}, {want_err!r})')
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f'r133 handler registration: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
