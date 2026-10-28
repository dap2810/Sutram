"""R51: what each of the six problems looks like on today's compiler."""
import os, subprocess, sys
comp, work = sys.argv[1], sys.argv[2]
CASES = {
    'p1_two_arg':   'mukhya() {\n    vitti x = 42\n    likha("x = ", x)\n    likha("y")\n}\n',
    'p1_three_arg': 'mukhya() {\n    vitti x = 42\n    likha("x = ", x, 9)\n}\n',
    'p1_today':     'mukhya() {\n    vitti x = 42\n    likha("x = ")\n    likha(x)\n    likha("\\n")\n}\n',
    'p2_tak':       'mukhya() {\n    chakra i = 0 tak 3 {\n        likha(i)\n    }\n}\n',
    'p2_c_shape':   'mukhya() {\n    chakra (vitti i = 0; i < 3; i = i + 1) {\n        likha(i)\n    }\n}\n',
    'p3_no_vitti':  'mukhya() {\n    x = 5\n    likha(x)\n}\n',
    'p4_no_prati':  'mukhya() {\n    likha(1)\n}\n',
    'p4_prati_3':   'mukhya() {\n    likha(1)\n    prati 3\n}\n',
    'p5_no_yoj':    'mukhya() {\n    likha(brihat_yuj(1, 2, 3, 4))\n}\n',
    'p5_typo':      'mukhya() {\n    likh(1)\n}\n',
    'brace':        'mukhya() {\n    likha("a{b}c {x}\\n")\n}\n',
    'p6_devanagari': 'मुख्य() {\n    वित्ति फलम् = 2 + 3।\n    लिख(फलम्)।\n}\n',
    'arity_likha0': 'mukhya() {\n    likha()\n}\n',
    'arity_kosh_push1': 'mukhya() {\n    kosh k[2]\n    kosh_push(5)\n}\n',
    'lkhb_dasham':  'mukhya() {\n    dasham d = 2.5\n    lkhb(d)\n    likha("\\n")\n}\n',
    'brace_var':    'mukhya() {\n    vitti x = 7\n    likha("{x}\\n")\n}\n',
}
for name, src in CASES.items():
    p = os.path.join(work, name + '.sm'); exe = os.path.join(work, name)
    open(p, 'w').write(src)
    if os.path.exists(exe): os.remove(exe)
    r = subprocess.run([comp, p, exe], capture_output=True, text=True)
    print(f'== {name}\n{src}--- compile (exit {r.returncode}): {r.stdout.strip()[:200]}')
    if os.path.exists(exe):
        q = subprocess.run([exe], capture_output=True)
        print(f'--- run (exit {q.returncode}): {q.stdout!r}')
