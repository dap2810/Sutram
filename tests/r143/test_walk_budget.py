#!/usr/bin/env python3
"""R143-R152: the expression walk's budget - a release default of 200000, a per-compile flag, a tested refusal.

R152 (Sarvam R149-R150, ChatGPT R214-R217): the default is 200000 steps, and --analysis-steps=N sets it for one
compile (its contract: tests/r152/test_analysis_steps.py). The bound a statement the syntax tree holds cannot pass
is 8 x (AST_HEAP_CAP / AST_NODE_SIZE) + 1 = 349,521; the widest statement the tree holds (21,829 terms) takes
exactly 87,316 steps. Earlier: v311 200000 fixed, v312 65536, v313 349521.

  * the source: the default is 200000, the walk starts from r152_steps (the flag, or the default) at every walk,
    the bound is computed from AST_HEAP_CAP and AST_NODE_SIZE, the budget is spent before each entry is taken;
  * the release compiler: the widest statement compiles and prints 21829; with --analysis-steps=87315 it is
    refused (exit 1, no output, E_VAKYA_SEEMA naming 87315, saying it is the analysis limit and not the syntax
    tree's, and what to do), and with 87316 it compiles - the steps are exact;
  * a test build with -DR143_WALK_BUDGET=64 refuses 40 terms naming 64, compiles 10, and the flag overrides it;
  * the margin: with that build every example and library compiles exactly as with the release default. The
    largest statement in them takes 52 steps (lib/brihat.smlib:174, 11 terms).

  python3 tests/r143/test_walk_budget.py [--compiler PATH]
Last line: "r143 walk budget: N checks, M failed".
"""
import glob, os, re, shutil, subprocess, sys, tempfile

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

    def compile_(c, name, text, extra=()):
        sm, out = os.path.join(work, name + '.sm'), os.path.join(work, name)
        open(sm, 'w').write(text)
        r = subprocess.run([c] + list(extra) + [sm, out], capture_output=True, text=True, timeout=120)
        return r, out, r.stdout + r.stderr

    def refused(c, name, text, budget, extra=()):
        r, out, said = compile_(c, name, text, extra)
        ok = (r.returncode == 1 and not os.path.exists(out) and '[E_VAKYA_SEEMA]' in said
              and f'parikshanam {budget} padeshu' in said and 'parikshana-seema' in said and 'vibhaja' in said
              and '--analysis-steps=<adhika>' in said and "vakya-vriksha-seema" in said)
        return ok, ('refused, exit 1, no output, E_VAKYA_SEEMA naming ' + str(budget) + ', the analysis limit (not the tree\'s): split, or raise it') if ok else \
            f'exit {r.returncode}, output {"made" if os.path.exists(out) else "none"}: {said.strip()[:90]!r}'

    def prints(c, name, text, want, extra=()):
        r, out, said = compile_(c, name, text, extra)
        if not os.path.exists(out):
            return False, 'refused: ' + said.strip()[:90]
        p = subprocess.run([out], capture_output=True, text=True, timeout=20)
        return p.returncode == 0 and p.stdout == want, f'prints {p.stdout!r}'

    src = open(os.path.join(ROOT, 'src', 'sutram_compiler.asm'), encoding='utf-8').read()
    code = re.sub(r';[^\n]*', '', src)
    m = re.search(r'%ifndef R143_WALK_BUDGET\s+%define R143_WALK_BUDGET (\d+)\s+%endif', code)
    budget = int(m.group(1)) if m else None
    cap = int(re.search(r'(?m)^AST_HEAP_CAP equ (\d+)', code).group(1))
    size = int(re.search(r'(?m)^AST_NODE_SIZE equ (\d+)', code).group(1))
    bound = 8 * (cap // size) + 1
    walk = code[code.find('\nr137_check_stmt:'):]
    w = walk[walk.find('\n.walk:'):walk.find('mov rbx, [rax+r15*8]')]
    gen = walk[walk.find('\n.gen:'):]
    gen = gen[:gen.find('jmp .walk')]
    lo = re.search(r'mov r9d, (\d+)', gen)
    hi = re.search(r'cmp r9d, (\d+)', gen)
    fields = list(range(int(lo.group(1)), int(hi.group(1)), 8)) if lo and hi else []
    check(budget == 200000 and fields and len(fields) <= 8 and bound == 349521
          and 'mov rax, [rel r152_steps]' in walk and 'mov [rel r137_budget], rax' in walk
          and w.find('dec qword [rel r137_budget]') < w.find('js .exhausted') < w.find('dec r15'),
          f'the source: the default is {budget}; every walk starts from r152_steps (--analysis-steps=N or the default); '
          f'a statement the tree holds cannot pass 8 x (AST_HEAP_CAP {cap} / AST_NODE_SIZE {size}) + 1 = {bound} (the walk '
          f'pushes at most 8 fields, offsets {fields}); spent before each entry is taken')
    if budget is None:
        budget = bound
    ok, got = prints(comp, 'widest', wide(21829), '21829\n')
    check(ok, f'release compiler: the widest statement the syntax tree holds (21,829 terms) compiles - {got}')
    ok, got = refused(comp, 'exact_no', wide(21829), 87315, ['--analysis-steps=87315'])
    ok2, got2 = prints(comp, 'exact_yes', wide(21829), '21829\n', ['--analysis-steps=87316'])
    check(ok and ok2, f'release compiler: the widest statement with --analysis-steps=87315 - {got}; with 87316 - {got2}')
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
            ok, got = prints(exe, 'small_flag', wide(40), '40\n', ['--analysis-steps=200000'])
            check(ok, f'test build, budget 64: --analysis-steps=200000 overrides it, and 40 terms compile - {got}')
            # R144 (Sarvam R144 WS1-WS2, ChatGPT R212): the margin, on every run. Every example and every library
            # compiles with the budget at 64 exactly as with the release budget: no real statement needs 64 steps,
            # so the release budget is more than 1,024 times the largest statement anyone here has written.
            progs = sorted(glob.glob(os.path.join(ROOT, 'examples', '*.sm')) + glob.glob(os.path.join(ROOT, 'examples', '*', '*.sm')))
            for lib in sorted(glob.glob(os.path.join(ROOT, 'lib', '*.smlib'))):
                lp = os.path.join(work, 'lib_' + os.path.basename(lib)[:-6] + '.sm')
                open(lp, 'w').write(f'yoj {os.path.basename(lib)[:-6]}\nmukhya() {{\n    likha(1)\n}}\n')
                progs.append(lp)
            hit, differ = [], []
            for i, pr in enumerate(progs):
                o1, o2 = os.path.join(work, 'm_rel'), os.path.join(work, 'm_64')
                for o in (o1, o2):
                    if os.path.exists(o):
                        os.remove(o)
                r1 = subprocess.run([comp, pr, o1], cwd=ROOT, capture_output=True, text=True, errors='replace')
                r2 = subprocess.run([exe, pr, o2], cwd=ROOT, capture_output=True, text=True, errors='replace')
                if 'E_VAKYA_SEEMA' in r2.stdout + r2.stderr:
                    hit.append(os.path.relpath(pr, ROOT))
                elif r1.returncode != r2.returncode or os.path.exists(o1) != os.path.exists(o2) or \
                        (os.path.exists(o1) and open(o1, 'rb').read() != open(o2, 'rb').read()):
                    differ.append(os.path.relpath(pr, ROOT))
            nlib = len(glob.glob(os.path.join(ROOT, 'lib', '*.smlib')))
            check(not hit and not differ,
                  f'the margin: with the budget at 64, all {len(progs) - nlib} examples and all {nlib} libraries compile as with '
                  f'{budget} - the largest real statement takes fewer than 64 steps, a margin over {budget // 64:,}x'
                  + (f' (E_VAKYA_SEEMA: {hit[:3]})' if hit else '') + (f' (differ: {differ[:3]})' if differ else ''))
    print(f'r143 walk budget: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
