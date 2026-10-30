# R76: for every surviving mutant of the listed functions (lib_mutant_score's own mutant set, same seed and
# cap), look for a number input on which the mutant and the real function differ (lib_mutant_witness's
# inputs and runner). Prints WITNESS / NO-WITNESS / NOT-TRIED per survivor.
import sys, json, random, shutil, tempfile
from pathlib import Path
sys.path.insert(0, 'tools')
import lib_mutant_score as S, lib_mutant_witness as W, lib_proof_gaps as g
rows = json.load(open(sys.argv[1])); compiler = str(Path('sutram_compiler').resolve())
funcs = {(f['module'], f['name']): f for p in sorted(g.LIB.glob('*.smlib')) for f in g.parse_module(p)}
ptrs = W.pointer_params(funcs); work = Path(tempfile.mkdtemp()); out = []
for r in rows:
    if not r['survivors']: continue
    f = funcs[(r['module'], r['name'])]; path = g.LIB / (f['module'] + '.smlib')
    if ptrs[(f['module'], f['name'])]:
        for m in r['survivors']: out.append((f['name'], m, 'NOT-TRIED', 'a parameter is a list, string or record'))
        continue
    muts = dict(S.mutants(path, f, 200, random.Random('%s.%s' % (f['module'], f['name']))))
    orig = Path(tempfile.mkdtemp(dir=work)); g.make_tree(orig)
    header, _ = g.probe_header(compiler, orig, f['module'])
    arity = len([p for p in f['params'].split(',') if p.strip()])
    args = W.inputs(arity, random.Random(20261019))
    if 'dasham' in f['params']:
        rnd = random.Random(7); args = [tuple(round(rnd.uniform(-60, 60), 3) for _ in range(arity)) for _ in range(300)] + [tuple([v] * arity) for v in (0.0, 1.0, -1.0, 3.141592653589793, -3.141592653589793, 6.283185307179586, 2.5, -2.5)]
    want = W.run(compiler, orig, header, f['name'], args); again = W.run(compiler, orig, header, f['name'], args)
    good = [(x, w) for x, w, v in zip(args, want or [], again or []) if w is not None and w == v]
    args, want = [x for x, _ in good], [w for _, w in good]
    for m in r['survivors']:
        if m not in muts: out.append((f['name'], m, 'NOT-TRIED', 'id not reproduced')); continue
        mt = Path(tempfile.mkdtemp(dir=work)); g.make_tree(mt, {f['module']: muts[m]})
        wit = W.first_difference(compiler, mt, header, f['name'], args, want) if args else None
        out.append((f['name'], m, 'WITNESS', f'input {wit[0]} real {wit[1]} mutant {wit[2]}') if wit else (f['name'], m, 'NO-WITNESS', f'{len(args)} inputs'))
        shutil.rmtree(mt, ignore_errors=True)
        print(*out[-1], sep='  ', flush=True)
shutil.rmtree(work, ignore_errors=True)
