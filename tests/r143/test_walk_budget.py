#!/usr/bin/env python3
"""R143: the expression walk's budget refuses, and the refusal is reachable with the release compiler.

ChatGPT R211: the 0-1023 parentheses probe measured parser nesting, not the walk's budget. And R141 compared the
wrong units: its "200000 can never be reached, the heap holds 43,690 nodes" counted nodes, but r137_check_stmt
spends a step on every entry it pops, a node or a field that is not one. Measured on v311: the widest statement
the AST heap holds (21,829 terms) takes 87,316 steps; the largest walk in the 768 programs takes 52. So v311's
refusal was code no program could reach. v312's budget is 65536 (R143_WALK_BUDGET):

  * a wide statement - 20,000 terms, siblings, not nesting - is refused by the release compiler: exit 1, no
    output file, E_VAKYA_SEEMA naming 65536; the same as a module-level initializer (the walk at r56);
  * 10,000 terms compile and print 10000;
  * a test build of this source with -DR143_WALK_BUDGET=64 refuses 40 terms naming 64, and compiles 10;
  * the source: the budget is that define, and it is spent before each entry is taken.

  python3 tests/r143/test_walk_budget.py [--compiler PATH]
Last line: "r143 walk budget: N checks, M failed".
"""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def wide(n, glob=False):
    e = '+'.join(['z'] * n)
    if glob:
        return f'vitti z = 1\nvitti g = {e}\nmukhya() {{\n    likha(g)\n}}\n'
    return f'mukhya() {{\n    vitti z = 1\n    likha({e})\n}}\n'


def main():
    comp = os.path.join(ROOT, 'sutram_compiler')
    own = '--compiler' not in sys.argv
    if not own:
        comp = os.path.abspath(sys.argv[sys.argv.index('--compiler') + 1])
    checks = fails = 0

    def check(ok, what):
        nonlocal checks, fails
        checks += 1
        fails += not ok
        print(('PASS  ' if ok else 'FAIL  ') + what)

    work = tempfile.mkdtemp(prefix='r143-')

    def compile_(c, name, text):
        sm, out = os.path.join(work, name + '.sm'), os.path.join(work, name)
        open(sm, 'w').write(text)
        r = subprocess.run([c, sm, out], capture_output=True, text=True, timeout=120)
        return r, out, r.stdout + r.stderr

    def refused(c, name, text, budget):
        r, out, said = compile_(c, name, text)
        ok = (r.returncode == 1 and not os.path.exists(out) and '[E_VAKYA_SEEMA]' in said
              and f' {budget} padeshu' in said)
        return ok, ('refused, exit 1, no output, E_VAKYA_SEEMA naming ' + str(budget)) if ok else \
            f'exit {r.returncode}, output {"made" if os.path.exists(out) else "none"}: {said.strip()[:90]!r}'

    def prints(c, name, text, want):
        r, out, said = compile_(c, name, text)
        if not os.path.exists(out):
            return False, 'refused: ' + said.strip()[:90]
        p = subprocess.run([out], capture_output=True, text=True, timeout=20)
        return p.returncode == 0 and p.stdout == want, f'prints {p.stdout!r}'

    src = open(os.path.join(ROOT, 'src', 'sutram_compiler.asm'), encoding='utf-8').read()
    code = re.sub(r';[^\n]*', '', src)
    m = re.search(r'%ifndef R143_WALK_BUDGET\s+%define R143_WALK_BUDGET (\d+)\s+%endif', code)
    budget = int(m.group(1)) if m else None
    walk = code[code.find('\nr137_check_stmt:'):]
    w = walk[walk.find('\n.walk:'):walk.find('mov rbx, [rax+r15*8]')]
    check(budget == 65536 and 'mov qword [rel r137_budget], R143_WALK_BUDGET' in walk
          and w.find('dec qword [rel r137_budget]') < w.find('js .exhausted') < w.find('dec r15'),
          f'the source: the budget is R143_WALK_BUDGET ({budget}), spent before each entry is taken, refusing when spent')
    if budget is None:
        budget = 65536
    for name, text, what in (('wide', wide(20000), 'a 20,000-term statement'),
                             ('wide_global', wide(20000, True), 'a 20,000-term module-level initializer')):
        ok, got = refused(comp, name, text, budget)
        check(ok, f'release compiler: {what} (wide, not deep) - {got}')
    ok, got = prints(comp, 'control', wide(10000), '10000\n')
    check(ok, f'release compiler: a 10,000-term statement compiles - {got}')
    if not own:
        print('NOT RUN  the lowered-budget build (it builds this tree\'s source; --compiler names another)')
    elif not (shutil.which('nasm') and shutil.which('ld')):
        print('NOT RUN  the lowered-budget build: nasm or ld is not installed')
    else:
        exe = os.path.join(work, 'budget64')
        b = subprocess.run(f'nasm -f elf64 -I. -DR143_WALK_BUDGET=64 src/r68_compiler_entry.asm -o {exe}.o && ld -o {exe} {exe}.o',
                           shell=True, cwd=ROOT, capture_output=True, text=True)
        if b.returncode:
            check(False, 'the -DR143_WALK_BUDGET=64 build: ' + b.stderr.strip()[:90])
        else:
            ok, got = refused(exe, 'small', wide(40), 64)
            check(ok, f'test build, budget 64: a 40-term statement - {got}')
            ok, got = prints(exe, 'small_ok', wide(10), '10\n')
            check(ok, f'test build, budget 64: a 10-term statement compiles - {got}')
    print(f'r143 walk budget: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
