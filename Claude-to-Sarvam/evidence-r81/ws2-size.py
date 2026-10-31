# R81 WS2: which library functions could be 'parikshita' today, unchanged? Mark every prakriya in a
# copy of lib/, compile a program that loads each module; on a refusal, unmark the function named and
# record why; repeat to a fixpoint. What is left marked passes the checker with every callee marked.
import os, re, shutil, subprocess, sys, json
G = sys.argv[1]; TREE = '/home/claude/sutram'
D = f'{G}/r81/m'; shutil.rmtree(D, ignore_errors=True); os.makedirs(D)
shutil.copy(f'{G}/r81/c/sutram_compiler', D)
for l in ('lang', 'win'): os.symlink(f'{TREE}/{l}', f'{D}/{l}')
shutil.copytree(f'{TREE}/lib', f'{D}/lib')
mods = sorted(f[:-6] for f in os.listdir(f'{D}/lib') if f.endswith('.smlib'))
funcs = {}   # name -> module
for m in mods:
    p = f'{D}/lib/{m}.smlib'; t = open(p).read()
    for n in re.findall(r'^prakriya\s+([A-Za-z_0-9]+)\s*\(', t, re.M):
        funcs.setdefault(n, m)
    t = re.sub(r'^prakriya(\s)', r'parikshita prakriya\1', t, flags=re.M)
    open(p, 'w').write(t)
why = {}
def unmark(name):
    m = funcs[name]; p = f'{D}/lib/{m}.smlib'; t = open(p).read()
    t2 = re.sub(r'^parikshita prakriya(\s+' + re.escape(name) + r'\s*\()', r'prakriya\1', t, flags=re.M)
    assert t2 != t, name; open(p, 'w').write(t2)
for m in mods:
    src = f'{D}/p_{m}.sm'; open(src, 'w').write(f'yoj {m}\nmukhya() {{\n    likha(1)\n}}\n')
    for _ in range(2000):
        r = subprocess.run([f'{D}/sutram_compiler', src, f'{D}/x'], capture_output=True, text=True, cwd=D)
        out = r.stdout + r.stderr
        mm = re.search(r"Sutram Error \[(E_APARIKSHITA_[A-Z]+)\]: parikshita prakriya '([^']+)'(.*)", out)
        if not mm:
            if r.returncode != 0: why.setdefault('__compile_error__', []).append((m, out.strip()[:300]))
            break
        code, f, rest = mm.groups()
        if code == 'E_APARIKSHITA_AHVAN':
            g = re.search(r"prakriyam '([^']+)'", rest).group(1); reason = ('calls', g)
        elif code == 'E_APARIKSHITA_SMRITI':
            reason = ('index', re.search(r"- '([^']+)\[", rest).group(1))
        else:
            reason = ('uses', re.search(r"- '(.+)' parikshitum", rest).group(1))
        why[f] = reason; unmark(f)
total = len(funcs); refused = len(why) - (1 if '__compile_error__' in why else 0)
ok = sorted(n for n in funcs if n not in why)
res = {'total': total, 'markable': ok, 'why': {k: v for k, v in why.items() if k != '__compile_error__'},
       'compile_errors': why.get('__compile_error__', []), 'funcs': funcs}
json.dump(res, open(f'{G}/r81/size.json', 'w'), indent=1)
print(total, 'functions;', len(ok), 'pass unchanged;', refused, 'refused')
