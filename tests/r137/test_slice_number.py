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

The gate fails if src/sutram_compiler.asm defines an OP_* this table does not spell, so a new operator cannot be
added without a case here. A refusal must be an unsuccessful compiler exit, no output file and the code.

  python3 tests/r137/test_slice_number.py [--compiler PATH]
Last line: "r137 slice is not a number: N checks, M failed".
"""
import os, re, subprocess, sys, tempfile

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


def run(exe):
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
    work = tempfile.mkdtemp(prefix='r137-')
    progs = [(n, HEAD + '    ' + b + '\n}\n', w) for n, b, w in cases()] + [('ChatGPT S4 laundering probe', CHATGPT, 'E_')]
    for i, (name, text, want) in enumerate(progs):
        sm, out = os.path.join(work, f'{i}.sm'), os.path.join(work, f'{i}')
        open(sm, 'w', encoding='utf-8').write(text)
        c = subprocess.run([comp, sm, out], cwd=ROOT, capture_output=True, text=True)
        said = c.stdout + c.stderr
        if want.startswith('E_'):
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
    print(f'r137 slice is not a number: {checks} checks, {fails} failed')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
