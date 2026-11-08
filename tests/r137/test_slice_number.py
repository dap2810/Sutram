#!/usr/bin/env python3
"""R137-R138: a slice is not a number, and neither is a kosh - in any expression, by any operator.

ChatGPT's R207 follow-up (S4) and Sarvam's own run on v308: `k[0:1] + zero` compiled and printed the slice
descriptor's address, and `keep(k[0:1] + zero)` with an untyped keep carried the slice past every door and read the
kosh's old elements (7 while k[0] was 99). The doors (R134) never saw a slice, because the operator had made it a
number first. v309 refuses the use (r137_check_stmt, run on every statement before it is generated):

  * every binary operator - each OP_* the compiler defines - with a slice on either side, a kosh slice or a mala's:
    E_VIBHAG_ANKA; unary minus and ! too (they are binary operators on 0);
  * a slice as a builtin's argument (only pankti_gan takes one), a condition (yadi, yavat, ?:), a for-loop bound, an
    index, a cell or raw store, a function value's or an untyped parameter's argument: E_VIBHAG_ANKA;
  * a kosh made a number by a call or ?: (`dek(k) + zero`, `(c ? k : k) + zero`): E_KOSH_GANIT, as a bare kosh is;
  * ChatGPT's laundering probe: refused;
  * controls compile and print the right values: a slice to a vibhag parameter, pankti_gan, a slice name passed on.

R141: and the same at a module-level vitti initializer, which is not a statement (ChatGPT R208 C1): a kosh from a
call in arithmetic there is E_KOSH_GANIT, a kosh bound to the module vitti E_KOSH_DVARA; a scalar call is fine.

R142 (Sarvam R142 WS1, ChatGPT R209): the walk is inside expression code generation. gen_expr generates without
a walk of its own only inside a statement or initializer the walk has checked (r142_checked); anything reaching it
otherwise is walked there, its own value counted as a number. The gate proves the shape two ways:
  * by reading the source: gen_expr's first instructions are that test and the walk; the generator's body is
    reached from gen_expr alone; r142_checked is raised only after a walk; the walk keeps its own stack;
  * by building the two entries' mutants (-DR142_MUTANT_NO_STMT_CHECK, -DR142_MUTANT_NO_GLOBAL_CHECK: the entry
    forgets the walk, as a new entry might) and running every case above with them: every negative is still
    refused, and a control may be refused (a forgotten check refuses more) but never compiles to a wrong value.
And the walk's stack (R142): r126_ret_kind, working out a prakriya's return kind for the first time in the middle
of the walk, used to overwrite the walk's pending nodes on the shared rfx2_stack: v310 printed an address, and
read 7 while k[0] was 99, for a statement in a prakriya defined before the prakriya it called.

R147: and the fourteen ways of keeping a slice past a growth (tests/r147/slices/, Sarvam R147 Task 4): each refused,
by the release compiler and by both mutants.

The gate fails if src/sutram_compiler.asm defines an OP_* this table does not spell, so a new operator cannot be
added without a case here. A refusal must be an unsuccessful compiler exit, no output file and the code.

  python3 tests/r137/test_slice_number.py [--compiler PATH]
Last line: "r137 slice is not a number: N checks, M failed".
"""
import os, re, shutil, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OPS = {'OP_ADD': '+', 'OP_SUB': '-', 'OP_MUL': '*', 'OP_DIV': '/', 'OP_EQ': '==', 'OP_LE': '<=', 'OP_LT': '<',
       'OP_GT': '>', 'OP_GE': '>=', 'OP_NE': '!=', 'OP_MOD': '%', 'OP_AND': '&', 'OP_OR': '|', 'OP_XOR': '^',
       'OP_LAND': '&&', 'OP_LOR': '||', 'OP_SHL': '<<', 'OP_SHR': '>>'}
HEAD = ('prakriya keep(x) {\n    nivartanam x\n}\nprakriya dek(kosh a) {\n    nivartanam a\n}\n'
        'prakriya vib(vibhag s) {\n    nivartanam s[0]\n}\n'
        'mukhya() {\n    kosh k[1]\n    kosh_kship(k, 7)\n    vitti zero = 0\n    vitti one = 1\n    vitti c = 1\n'
        '    mala m[4]\n    m[0] = 5\n    vitti p = nirmmita(64)\n')


def cases():
    out = []
    for name, op in OPS.items():
        out.append((f'{name}: k[0:1] {op} zero', f'likha(k[0:1] {op} zero)', 'E_VIBHAG_ANKA'))
        out.append((f'{name}: one {op} m[0:2]', f'likha(one {op} m[0:2])', 'E_VIBHAG_ANKA'))
    out += [('unary -', 'likha(-k[0:1])', 'E_VIBHAG_ANKA'), ('unary !', 'likha(!m[0:2])', 'E_VIBHAG_ANKA'),
            ('likha(mala slice)', 'likha(m[0:2])', 'E_VIBHAG_ANKA'),
            ('yadi (slice)', 'yadi (m[0:2]) {\n        likha(1)\n    }', 'E_VIBHAG_ANKA'),
            ('yavat (slice)', 'yavat (m[0:2]) {\n        likha(1)\n    }', 'E_VIBHAG_ANKA'),
            ('?: condition', 'likha(m[0:2] ? 1 : 2)', 'E_VIBHAG_ANKA'),
            ('?: arm + zero', 'likha((c ? k[0:1] : k[0:1]) + zero)', 'E_VIBHAG_ANKA'),
            ('for bound', 'chakra i = 1 tak m[0:2] {\n        likha(i)\n    }', 'E_VIBHAG_ANKA'),
            ('index', 'likha(m[m[0:1]])', 'E_VIBHAG_ANKA'),
            ('cell store', 'm[1] = m[0:2] + zero\n    likha(m[1])', 'E_VIBHAG_ANKA'),
            ('raw store', 'p[0] = m[0:2]\n    likha(p[0])', 'E_VIBHAG_ANKA'),
            ('untyped parameter', 'likha(keep(m[0:2]))', 'E_VIBHAG_ANKA'),
            ('function value', 'vitti f = keep\n    likha(f(m[0:2]))', 'E_VIBHAG_ANKA'),
            ('declared from arithmetic', 'vitti v = k[0:1] + zero\n    likha(v)', 'E_VIBHAG_ANKA'),
            ('kosh result + zero', 'likha(dek(k) + zero)', 'E_KOSH_GANIT'),
            ('?: of kosh + zero', 'likha((c ? k : k) + zero)', 'E_KOSH_GANIT'),
            ('bare kosh + zero', 'likha(k + zero)', 'E_KOSH_GANIT'),
            ('control: vib(k[0:1])', 'likha(vib(k[0:1]))', '7\n'),
            ('control: pankti_gan(m[0:3])', 'likha(pankti_gan(m[0:3]))', '3\n'),
            ('control: a slice name passed on', 'vitti t = m[0:2]\n    likha(vib(t))', '5\n'),
            ('control: element arithmetic', 'likha(k[0] + m[0])', '12\n')]
    return out


CHATGPT = ('prakriya keep(x) {\n    nivartanam x\n}\nmukhya() {\n    kosh k[1]\n    kosh_kship(k, 7)\n'
           '    vitti obstacle = nirmmita(16)\n    vitti zero = 0\n    vitti t = keep(k[0:1] + zero)\n    kosh_kship(k, 8)\n'
           '    k[0] = 99\n    vitti addr = t[0]\n    likha(addr[0])\n    likha(k[0])\n}\n')


# R141 (ChatGPT R208 C1): a module-level initializer is checked as a statement is - it is not one.
MK = 'prakriya make_kosh() {\n    kosh k[1]\n    kosh_kship(k, 7)\n    nivartanam k\n}\n'
GLOBALS = [
    ('global initializer: make_kosh() + zero (C1)', 'vitti zero = 0\nvitti leaked = make_kosh() + zero\n' + MK + 'mukhya() {\n    likha(leaked)\n}\n', 'E_KOSH_GANIT'),
    ('global initializer: make_kosh() == 0', 'vitti leaked = make_kosh() == 0\n' + MK + 'mukhya() {\n    likha(leaked)\n}\n', 'E_KOSH_GANIT'),
    ('global initializer: (1 ? make_kosh() : make_kosh()) + 0', 'vitti leaked = (1 ? make_kosh() : make_kosh()) + 0\n' + MK + 'mukhya() {\n    likha(leaked)\n}\n', 'E_KOSH_GANIT'),
    ('global initializer: a kosh into a module vitti', 'vitti leaked = make_kosh()\n' + MK + 'mukhya() {\n    likha(leaked)\n}\n', 'E_KOSH_DVARA'),
    ('global initializer control: 3 + f()', 'vitti g = 3 + f()\nprakriya f() {\n    nivartanam 4\n}\nmukhya() {\n    likha(g)\n}\n', '7\n'),
]

# R142: the walk's pending nodes, overwritten by a first r126_ret_kind of f (defined after g) on v310.
LATE_F = 'prakriya f() {\n    vitti a = 1\n    nivartanam a + 3 - 4\n}\nmukhya() {\n    g()\n}\n'
STACK = [
    ('R142 walk stack: slice arithmetic beside a first call of f', 'prakriya g() {\n    mala m[4]\n    m[0] = 5\n'
     '    vitti zero = 0\n    likha(((m[0:2] * 1) * 1) + (f() + zero))\n    nivartanam 0\n}\n' + LATE_F, 'E_VIBHAG_ANKA'),
    ('R142 walk stack: kosh arithmetic beside a first call of f', 'prakriya dek(kosh a) {\n    nivartanam a\n}\n'
     'prakriya g() {\n    kosh k[1]\n    kosh_kship(k, 7)\n    vitti zero = 0\n'
     '    likha(((dek(k) + zero) * 1) + (f() + zero))\n    nivartanam 0\n}\n' + LATE_F, 'E_KOSH_GANIT'),
    ('R142 walk stack: the S4 stale read beside a first call of f (v310: 7 and 99)',
     'prakriya keep(x) {\n    nivartanam x\n}\nprakriya g() {\n    kosh k[1]\n    kosh_kship(k, 7)\n'
     '    vitti obstacle = nirmmita(16)\n    vitti zero = 0\n    vitti t = keep((k[0:1] * 1) + (f() + zero))\n'
     '    kosh_kship(k, 8)\n    k[0] = 99\n    vitti addr = t[0]\n    likha(addr[0])\n    likha(k[0])\n'
     '    nivartanam 0\n}\n' + LATE_F, 'E_VIBHAG_ANKA'),
    ('R142 walk stack control: the same with no slice prints 4', 'prakriya g() {\n    vitti zero = 0\n'
     '    likha(((zero * 1) * 1) + (f() + 4))\n    nivartanam 0\n}\n' + LATE_F, '4\n'),
]

# R147 (Sarvam R147 Tasks 4-5): the fourteen ways of keeping a slice past a growth, one file each in
# tests/r147/slices/ - the ten found and closed (cell, untyped parameter and result, function value, module vitti,
# record field, raw memory, dasham parameter, arithmetic, module initializer) and four new (a comparison used as an
# index, two prakriyas in sequence, a kosh element, inline machine code). Every one is refused; with the mutants too.
SLICES = {'01_cell': 'E_KOSH_VIBHAG', '02_untyped_param': 'E_KOSH_VIBHAG', '03_untyped_return': 'E_KOSH_VIBHAG',
          '04_function_value': 'E_KOSH_VIBHAG', '05_module_vitti': 'E_KOSH_VIBHAG', '06_record_field': 'E_KOSH_VIBHAG',
          '07_raw_memory': 'E_KOSH_VIBHAG', '08_dasham_param': 'E_KOSH_VIBHAG', '09_arithmetic': 'E_VIBHAG_ANKA',
          '10_module_initializer': 'E_KOSH_DVARA', '11_comparison_as_index': 'E_VIBHAG_ANKA',
          '12_two_functions': 'E_KOSH_VIBHAG', '13_kosh_element': 'E_KOSH_VIBHAG',
          '14_inline_assembly': 'SYNTAX',   # yantra takes a string of machine bytes, not a value
          '15_ffi_argument': 'E_KOSH_VIBHAG'}   # R152: a declared foreign function's argument (--ffi ... --object)
FFI = ['--ffi', os.path.join(ROOT, 'tests', 'r33', 'kinds.sffi'), '--object']


def run(exe):
    if not os.access(exe, os.X_OK):
        return None, 'writes an object (--object)'
    try:
        r = subprocess.run([exe], capture_output=True, text=True, timeout=10)
        return r.returncode, f'prints {r.stdout!r}'
    except subprocess.TimeoutExpired:
        return None, 'runs for ever (stopped after 10 s)'


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

    src = open(os.path.join(ROOT, 'src', 'sutram_compiler.asm'), encoding='utf-8').read()
    defined = set(re.findall(r'(?m)^(OP_[A-Z_]+)\s+equ\b', src))
    check(defined == set(OPS), f'every operator the compiler defines has a case here ({sorted(defined ^ set(OPS)) or "all"})')
    code = re.sub(r';[^\n]*', '', src)

    def body_of(label):
        i = code.find('\n' + label + ':')
        m = re.search(r'\n[a-z_][a-z0-9_]*:', code[i + 1:]) if i >= 0 else None
        return code[i:i + 1 + (m.start() if m else 0)] if i >= 0 else ''
    ge = [l.strip() for l in body_of('gen_expr').splitlines() if l.strip() and not l.strip().startswith('%')][1:]
    check(ge[:2] == ['cmp qword [rel r142_checked], 0', 'jne r142_gen_expr_body']
          and 0 < ''.join(ge).find('call r137_check_stmt') < ''.join(ge).find('call r142_gen_expr_body'),
          'R142: gen_expr itself goes to the generator only inside a checked statement or initializer, and walks '
          'anything else first')
    refs = {b: [l for l in re.findall(r'(?m)^[a-z_][a-z0-9_.]*:|\b(?:call|jmp|j[a-z]+)\s+' + b + r'\b', code)
                if not l.endswith(':')] for b in ('r142_gen_expr_body', 'r142_gen_stmt_body')}
    outside = [b for b, w in (('r142_gen_expr_body', 'gen_expr'), ('r142_gen_stmt_body', 'gen_stmt'))
               if code.count(b) != body_of(w).count(b) + 1]
    check(not outside and refs['r142_gen_expr_body'] and refs['r142_gen_stmt_body'],
          f'R142: the generators\' bodies are reached only through gen_expr and gen_stmt ({outside or "no other reference"})')
    raised = []
    for m in re.finditer(r'inc qword \[rel r142_checked\]', code):
        fn = re.findall(r'(?m)^([a-z_][a-z0-9_]*):', code[:m.start()])[-1]
        before = code[code.rfind('\n' + fn + ':', 0, m.start()):m.start()]
        raised.append((fn, 'call r137_check_stmt' in before))
    check(raised and all(ok for _, ok in raised),
          f'R142: r142_checked is raised only after the walk, in the same function ({raised})')
    walk = body_of('r137_check_stmt')
    check('rfx2_stack' not in walk and 'rfx2_push' not in walk and 'r142_wstack' in walk,
          'R142: the walk keeps its own stack (r126_ret_kind uses rfx2_stack in the middle of it)')
    work = tempfile.mkdtemp(prefix='r137-')
    progs = [(n, HEAD + '    ' + b + '\n}\n', w) for n, b, w in cases()] + [('ChatGPT S4 laundering probe', CHATGPT, 'E_')]
    progs += [(n, t, w) for n, t, w in GLOBALS + STACK]
    sdir = os.path.join(ROOT, 'tests', 'r147', 'slices')
    found = sorted(f[:-3] for f in os.listdir(sdir) if f.endswith('.sm')) if os.path.isdir(sdir) else []
    check(found == sorted(SLICES), f'R147/R152: tests/r147/slices holds the fifteen shapes, each with a case here ({len(found)} files)')
    progs += [(f'R147 shape {n}', open(os.path.join(sdir, n + '.sm'), encoding='utf-8').read(), w)
              for n, w in sorted(SLICES.items()) if n in found]

    def compile_(comp, i, text, tag='', name=''):
        sm, out = os.path.join(work, f'{tag}{i}.sm'), os.path.join(work, f'{tag}{i}')
        open(sm, 'w', encoding='utf-8').write(text)
        c = subprocess.run([comp] + (FFI if name.startswith('R147 shape 15') else []) + [sm, out], cwd=ROOT,
                           capture_output=True, text=True)
        return c, out, c.stdout + c.stderr
    for i, (name, text, want) in enumerate(progs):
        c, out, said = compile_(comp, i, text, name=name)
        if want == 'SYNTAX':
            ok = c.returncode != 0 and not os.path.exists(out) and 'vyakaran dosh' in said
            got = 'refused (syntax)' if ok else ('compiles, ' + run(out)[1] if os.path.exists(out) else 'refused ' + said.strip()[:60])
        elif want.startswith('E_'):
            ok = c.returncode != 0 and not os.path.exists(out) and (want == 'E_' and '[E_' in said or f'[{want}]' in said)
            got = 'refused ' + (m.group(0) if (m := re.search(r'E_[A-Z_]+', said)) else repr(said.strip()[:60]))
            if os.path.exists(out):
                got = 'compiles, ' + run(out)[1]
        else:
            ok, got = False, 'refused ' + said.strip()[:60]
            if os.path.exists(out):
                rc, got = run(out)
                ok = rc == 0 and got == f'prints {want!r}'
        check(ok, f'{name}: want {want!r}; {got}')
    # R152 (Sarvam R151 WS3 item 5): the release binaries are the plain builds - no mutant, no lowered budget.
    if own and shutil.which('nasm') and shutil.which('ld'):
        plain = os.path.join(work, 'plain')
        b = subprocess.run(f'nasm -f elf64 -I. src/r68_compiler_entry.asm -o {plain}.o && ld -o {plain} {plain}.o',
                           shell=True, cwd=ROOT, capture_output=True, text=True)
        same = b.returncode == 0 and open(plain, 'rb').read() == open(comp, 'rb').read()
        msg = 'the committed sutram_compiler is the plain build of src/ byte for byte (no -D: no mutant, no lowered budget)'
        if shutil.which('x86_64-w64-mingw32-ld'):
            bw = subprocess.run(f'nasm -f win64 -dWINDOWS -I./ src/r68_compiler_entry.asm -o {plain}w.obj && '
                                f'x86_64-w64-mingw32-ld -mi386pep --no-insert-timestamp --entry=_start -o {plain}w.exe {plain}w.obj',
                                shell=True, cwd=ROOT, capture_output=True, text=True)
            same = same and bw.returncode == 0 and all(open(f'{plain}w.exe', 'rb').read() == open(os.path.join(ROOT, x), 'rb').read()
                                                       for x in ('sutram.exe', os.path.join('win', 'sutram.exe')))
            msg += '; so are sutram.exe and win/sutram.exe (-dWINDOWS only)'
        check(same, msg)
    if not own:
        print('NOT RUN  the mutant check (it builds this tree\'s compiler; --compiler names another)')
    elif not (shutil.which('nasm') and shutil.which('ld')):
        print('NOT RUN  the mutant check: nasm or ld is not installed')
    else:
        for define in ('R142_MUTANT_NO_STMT_CHECK', 'R142_MUTANT_NO_GLOBAL_CHECK'):
            exe = os.path.join(work, define)
            b = subprocess.run(f'nasm -f elf64 -I. -D{define} src/r68_compiler_entry.asm -o {exe}.o && ld -o {exe} {exe}.o',
                               shell=True, cwd=ROOT, capture_output=True, text=True)
            if b.returncode:
                check(False, f'{define}: the mutant builds ({b.stderr.strip()[:80]})')
                continue
            leaked, over = [], []
            for i, (name, text, want) in enumerate(progs):
                c, out, said = compile_(exe, i, text, define, name=name)
                made = os.path.exists(out)
                if want == 'SYNTAX':
                    if c.returncode == 0 or made:
                        leaked.append(name)
                elif want.startswith('E_'):
                    if c.returncode == 0 or made or '[E_' not in said:
                        leaked.append(name)
                elif made:
                    rc, got = run(out)
                    if not (rc == 0 and got == f'prints {want!r}'):
                        leaked.append(name + ' (' + got + ')')
                else:
                    over.append(name)
            check(not leaked, f'R142 mutant {define} (the entry forgets the walk): every negative still refused, no control '
                  f'wrong ({len(progs) - len(over) - len(leaked)} as before, {len(over)} control(s) refused instead'
                  + (f': {", ".join(over)}' if over else '') + (f'; LEAKED: {leaked}' if leaked else '') + ')')
    print(f'r137 slice is not a number: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
