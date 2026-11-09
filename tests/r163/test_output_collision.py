#!/usr/bin/env python3
"""R163 (Sarvam ROUND-163 WS1; found R162): the output is never a file the compile or the link read.

Up to v315 `sutram hello.sm hello.sm` wrote the binary over the program (exit 0); `--object` and `sutram-link`
did the same. Each case below is run in a fresh folder; every input's bytes are compared before and after.

  a  the source as the output, by the same name, by ./name, by a hard link, by a symbolic link -> refused, exit 1,
     E_NIRGAM_NIVESH, the source byte for byte as it was
  b  --object with the source as the output -> refused, the source unchanged
  c  a yoj module as the output (lib/ganit.smlib, copied into the folder) -> refused, the module unchanged; and a
     --debug compile of that program (a module opened once per traced statement) is not refused
  d  the --lang pack file as the output -> refused, the pack unchanged
  e  the --ffi file as the output -> refused, unchanged
  f  sutram-link with an object as the output -> refused, E_NIRGAM_NIVESH, the object unchanged
  g  the ordinary cases still work: a new output; an existing output that is not an input is replaced, as before -
     and, because the output is now opened without truncation and cut only after the check, an existing LARGER
     file ends exactly as a fresh build's bytes (compiler, --object, linker); a .exe output (PE) naming its own
     source is refused too
  h  an output that cannot be opened is refused, E_NIRGAM_PATRA (v315 reported success and wrote nothing);
     /dev/null still works
  i  --separate's root file (named on the command line, its folder used for yoj, not read) as the output -> refused
  j  /dev/stdout as the output with stdout appended to the source (sutram a.sm /dev/stdout >> a.sm) -> refused,
     no binary written: the open file behind /dev/stdout is the source. The compiler prints its messages on
     standard output, so the refusal itself is what the shell appends after the program
  k  sutram-elf2smo and sutram-coff2smo with the input as the output (same name, hard link) -> refused, unchanged;
     an ordinary conversion still works and a larger existing output ends exactly as a fresh one (the objects are
     made with nasm; without nasm these lines are NOT RUN)
  l  tools/sutram_build.py with -o naming the program, one of its modules, or a --foreign object -> refused,
     unchanged (the linker cannot see these: its inputs are the objects); an ordinary build still works
  (f also covers a linker output naming its SECOND object.)
  Not tested here, and why: a path replaced between the check and the write - by construction there is no such
  window (the identity checked is the open handle's, and the same handle is cut and written); an identity that
  cannot be read - the compiler refuses (E_NIRGAM_NIVESH), but no ordinary file makes fstat fail
Usage: python3 tests/r163/test_output_collision.py [--compiler PATH] [--linker PATH] [--elf2smo PATH] [--coff2smo PATH]
       [--build tools/sutram_build.py]
"""
import hashlib, os, shutil, subprocess, sys, tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
PROG = 'mukhya() {\n    likha(1)\n}\n'
checks = fails = 0


def check(ok, what):
    global checks, fails
    checks += 1
    fails += not ok
    print(('PASS  ' if ok else 'FAIL  ') + what)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def run(argv, cwd):
    r = subprocess.run(argv, capture_output=True, text=True, cwd=cwd, timeout=120)
    return r.returncode, r.stdout + r.stderr


def refused(argv, cwd, keep, what):
    # a compiler without the check has written over the source in an earlier case: start each case from it again
    open(os.path.join(cwd, 'a.sm'), 'w').write(PROG)
    before = {p: sha(os.path.join(cwd, p)) for p in keep}
    rc, out = run(argv, cwd)
    after = {p: sha(os.path.join(cwd, p)) for p in keep}
    check(rc == 1 and 'E_NIRGAM_NIVESH' in out and before == after,
          f'{what}: refused, exit 1, E_NIRGAM_NIVESH, unchanged' + ('' if rc == 1 and before == after else f' -- rc {rc}: {out.strip()[:120]}'))


def main():
    a = sys.argv[1:]
    compiler = os.path.abspath(a[a.index('--compiler') + 1]) if '--compiler' in a else os.path.join(ROOT, 'sutram_compiler')
    linker = os.path.abspath(a[a.index('--linker') + 1]) if '--linker' in a else os.path.join(ROOT, 'sutram-link')
    elf2smo = os.path.abspath(a[a.index('--elf2smo') + 1]) if '--elf2smo' in a else os.path.join(ROOT, 'sutram-elf2smo')
    coff2smo = os.path.abspath(a[a.index('--coff2smo') + 1]) if '--coff2smo' in a else os.path.join(ROOT, 'sutram-coff2smo')
    builder = os.path.abspath(a[a.index('--build') + 1]) if '--build' in a else os.path.join(ROOT, 'tools', 'sutram_build.py')
    d = tempfile.mkdtemp()
    try:
        open(os.path.join(d, 'a.sm'), 'w').write(PROG)
        refused([compiler, 'a.sm', 'a.sm'], d, ['a.sm'], 'a: the source as its own output')
        refused([compiler, 'a.sm', './a.sm'], d, ['a.sm'], 'a: the source as ./name')
        os.link(os.path.join(d, 'a.sm'), os.path.join(d, 'hard.sm'))
        refused([compiler, 'a.sm', 'hard.sm'], d, ['a.sm'], 'a: a hard link to the source')
        os.symlink('a.sm', os.path.join(d, 'sym.sm'))
        refused([compiler, 'a.sm', 'sym.sm'], d, ['a.sm'], 'a: a symbolic link to the source')
        refused([compiler, '--object', 'a.sm', 'a.sm'], d, ['a.sm'], 'b: --object with the source as the output')
        # every file a case may write over is a copy in the temporary folder - never the tree's own (a compiler
        # without the check would write over it; this test once did, to a copy of lang/gujarati.lang)
        os.makedirs(os.path.join(d, 'lib'))
        shutil.copy(os.path.join(ROOT, 'lib', 'ganit.smlib'), os.path.join(d, 'lib', 'ganit.smlib'))
        open(os.path.join(d, 'm.sm'), 'w').write('yoj ganit\nmukhya() {\n    likha(varg(3))\n}\n')
        rc, out = run([compiler, 'm.sm', 'm.bin'], d)
        check(rc == 0 and run([os.path.join(d, 'm.bin')], d)[1].strip() == '9', 'c: the module program compiles and prints 9')
        # --debug opens a module once for each statement it traces (hundreds of opens of a few files): each file is
        # noted once, so the inputs never run past the limit (the first staged build refused every --debug yoj compile)
        rc, out = run([compiler, '--debug', 'm.sm', 'md.bin'], d)
        check(rc == 0 and os.path.exists(os.path.join(d, 'md.bin')), 'c: a --debug compile of the module program is not refused')
        refused([compiler, 'm.sm', 'lib/ganit.smlib'], d, ['m.sm', 'lib/ganit.smlib'], 'c: a yoj module (the source folder\'s lib/ganit.smlib, which the compile read) as the output')
        os.makedirs(os.path.join(d, 'lang'))
        shutil.copy(os.path.join(ROOT, 'lang', 'gujarati.lang'), os.path.join(d, 'lang', 'gujarati.lang'))
        refused([compiler, '--lang', 'gujarati', 'a.sm', 'lang/gujarati.lang'], d,
                ['a.sm', 'lang/gujarati.lang'], 'd: the --lang pack (lang/gujarati.lang, read from the working folder) as the output')
        shutil.copy(os.path.join(ROOT, 'tests', 'r33', 'kinds.sffi'), os.path.join(d, 'k.sffi'))
        refused([compiler, '--ffi', 'k.sffi', '--object', 'a.sm', 'k.sffi'], d, ['a.sm', 'k.sffi'], 'e: the --ffi file as the output')
        open(os.path.join(d, 'a.sm'), 'w').write(PROG)
        rc, out = run([compiler, '--object', 'a.sm', 'a.smo'], d)
        check(rc == 0 and os.path.exists(os.path.join(d, 'a.smo')), 'f: the object is made')
        refused([linker, 'a.smo', 'a.smo'], d, ['a.smo'], 'f: sutram-link with its object as the output')
        open(os.path.join(d, 'b.sm'), 'w').write('prakriya do() {\n    nivartanam 2\n}\n')
        rc, out = run([compiler, '--object', 'b.sm', 'b.smo'], d)
        refused([linker, 'b.smo', 'a.smo', 'b.smo'], d, ['a.smo', 'b.smo'], 'f: sutram-link with its second object as the output')
        open(os.path.join(d, 'a.sm'), 'w').write(PROG)
        run([compiler, '--object', 'a.sm', 'a.smo'], d)   # again: a linker without the check wrote over a.smo above
        rc, out = run([linker, 'l.bin', 'a.smo'], d)
        check(rc == 0 and run([os.path.join(d, 'l.bin')], d)[1].strip() == '1', 'f: an ordinary link still works')
        rc, out = run([compiler, 'a.sm', 'new.bin'], d)
        check(rc == 0 and run([os.path.join(d, 'new.bin')], d)[1].strip() == '1', 'g: a new output is made')
        open(os.path.join(d, 'old.bin'), 'w').write('an earlier build\n')
        rc, out = run([compiler, 'a.sm', 'old.bin'], d)
        check(rc == 0 and run([os.path.join(d, 'old.bin')], d)[1].strip() == '1',
              'g: an existing output that is not an input is replaced, as before')
        # the output is opened without truncation and cut only after the check: an existing LARGER file must end
        # exactly as a fresh compile's bytes, not with the old file's tail
        run([compiler, 'a.sm', 'fresh.bin'], d)
        open(os.path.join(d, 'big.bin'), 'wb').write(b'x' * 200000)
        rc, out = run([compiler, 'a.sm', 'big.bin'], d)
        check(rc == 0 and sha(os.path.join(d, 'big.bin')) == sha(os.path.join(d, 'fresh.bin')),
              'g: an existing larger output is cut first - its bytes are exactly a fresh compile\'s')
        open(os.path.join(d, 'big.smo'), 'wb').write(b'y' * 200000)
        run([compiler, '--object', 'a.sm', 'fresh.smo'], d)
        rc, out = run([compiler, '--object', 'a.sm', 'big.smo'], d)
        check(rc == 0 and sha(os.path.join(d, 'big.smo')) == sha(os.path.join(d, 'fresh.smo')),
              'g: the same for --object')
        open(os.path.join(d, 'big2.bin'), 'wb').write(b'z' * 200000)
        rc, out = run([linker, 'big2.bin', 'a.smo'], d)
        check(rc == 0 and sha(os.path.join(d, 'big2.bin')) == sha(os.path.join(d, 'l.bin')), 'g: the same for sutram-link')
        # an output that cannot be opened: up to v315 the compiler said "Siddh", exit 0, and wrote nothing
        rc, out = run([compiler, 'a.sm', os.path.join(d, 'no-such-folder', 'x.bin')], d)
        check(rc == 1 and 'E_NIRGAM_PATRA' in out and not os.path.exists(os.path.join(d, 'no-such-folder')),
              'h: an output in a folder that does not exist: refused, exit 1, E_NIRGAM_PATRA (v315 said Siddh, exit 0)')
        rc, out = run([compiler, '--object', 'a.sm', os.path.join(d, 'no-such-folder', 'x.smo')], d)
        check(rc == 1 and 'E_NIRGAM_PATRA' in out, 'h: the same with --object')
        rc, out = run([compiler, 'a.sm', '/dev/null'], d)
        check(rc == 0, 'h: /dev/null is still an output (a device is not cut, and is no input)')
        shutil.copy(os.path.join(d, 'a.sm'), os.path.join(d, 'p.exe'))
        refused([compiler, 'p.exe', 'p.exe'], d, ['p.exe'], 'g: a .exe (PE) output naming its own source')
        open(os.path.join(d, 'root.sm'), 'w').write(PROG)
        refused([compiler, '--separate', 'b.sm', 'root.sm', 'root.sm'], d, ['b.sm', 'root.sm'],
                'i: --separate with its root file as the output')
        open(os.path.join(d, 'a.sm'), 'w').write(PROG)
        rc, out = run(['sh', '-c', f'"{compiler}" a.sm /dev/stdout >> a.sm'], d)
        got = open(os.path.join(d, 'a.sm'), 'rb').read()
        # the compiler's messages go to standard output, which the shell was told to append to a.sm: the refusal
        # is appended after the program - that is the redirection's doing. The program itself, and no binary.
        check(rc == 1 and got.startswith(PROG.encode()) and b'E_NIRGAM_NIVESH' in got[len(PROG):] and b'\x7fELF' not in got,
              'j: /dev/stdout appended to the source (sutram a.sm /dev/stdout >> a.sm): refused, exit 1, the program intact '
              '(the refusal, printed on standard output, is what the shell appended)')
        nasm = shutil.which('nasm')
        for tool, fmt, ext, glob in ((elf2smo, 'elf64', 'o', 'ek:function'), (coff2smo, 'win64', 'obj', 'ek')):
            name = os.path.basename(tool)
            if not nasm:
                print(f'NOT RUN  k: {name} - no nasm to make an object')
                continue
            open(os.path.join(d, 'f.asm'), 'w').write(f'section .text\nglobal {glob}\nek:\n    mov eax, 1\n    ret\n')
            obj = 'f.' + ext
            subprocess.run([nasm, '-f', fmt, 'f.asm', '-o', obj], cwd=d, check=True)
            refused([tool, obj, obj], d, [obj], f'k: {name} with its input as the output')
            os.link(os.path.join(d, obj), os.path.join(d, 'h' + obj))
            refused([tool, obj, 'h' + obj], d, [obj], f'k: {name} with a hard link to its input as the output')
            rc1, _ = run([tool, obj, 'k1.smo'], d)
            open(os.path.join(d, 'k2.smo'), 'wb').write(b'w' * 100000)
            rc2, _ = run([tool, obj, 'k2.smo'], d)
            check(rc1 == 0 and rc2 == 0 and sha(os.path.join(d, 'k1.smo')) == sha(os.path.join(d, 'k2.smo')),
                  f'k: {name}: an ordinary conversion works; a larger existing output ends exactly as a fresh one')
            os.remove(os.path.join(d, 'h' + obj))
        build = [sys.executable, builder, '--compiler', compiler, '--linker', linker,
                 '--elf2smo', elf2smo, '--coff2smo', coff2smo]
        refused(build + ['a.sm', '-o', 'a.sm'], d, ['a.sm'], 'l: sutram_build.py -o the program itself')
        refused(build + ['m.sm', '-o', 'lib/ganit.smlib'], d, ['m.sm', 'lib/ganit.smlib'], 'l: sutram_build.py -o one of its modules')
        if nasm:
            open(os.path.join(d, 'f.asm'), 'w').write('section .text\nglobal ek:function\nek:\n    mov eax, 1\n    ret\n')
            subprocess.run([nasm, '-f', 'elf64', 'f.asm', '-o', 'f.o'], cwd=d, check=True)
            refused(build + ['--foreign', 'f.o', 'a.sm', '-o', 'f.o'], d, ['a.sm', 'f.o'], 'l: sutram_build.py -o its --foreign object')
        else:
            print('NOT RUN  l: --foreign - no nasm to make an object')
        rc, out = run(build + ['m.sm', '-o', 'mb.bin'], d)
        check(rc == 0 and run([os.path.join(d, 'mb.bin')], d)[1].strip() == '9', 'l: an ordinary sutram_build.py build still works')
    finally:
        shutil.rmtree(d, ignore_errors=True)
    print(f'r163 output collision: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
