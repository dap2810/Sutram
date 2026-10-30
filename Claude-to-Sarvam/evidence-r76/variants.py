# R76: per mutant VARIANT (ids can repeat on one line), kill with the proofs, then search a witness.
import sys, random, shutil, tempfile, re
from pathlib import Path
sys.path.insert(0, 'tools')
import lib_mutant_score as S, lib_mutant_witness as W, lib_proof_gaps as g
comp = str(Path('sutram_compiler').resolve())
funcs = {(f['module'], f['name']): f for p in sorted(g.LIB.glob('*.smlib')) for f in g.parse_module(p)}
deps = {p.stem: g.module_imports(p.read_text(encoding='utf-8')) for p in g.LIB.glob('*.smlib')}
golds = g.golden_proofs()
for p in golds: p['mods'] = g.closure(g.module_imports(p['src']), deps)
_, props = g.load_props()
work = Path(tempfile.mkdtemp())
for spec in sys.argv[1:]:
    mod, name = spec.split('.')
    f = funcs[(mod, name)]; path = g.LIB / (mod + '.smlib')
    rel = [p for p in golds if mod in p['mods']]
    relp = list(range(len(props)))
    muts = S.mutants(path, f, 200, random.Random('%s.%s' % (mod, name)))
    orig = Path(tempfile.mkdtemp(dir=work)); g.make_tree(orig)
    header, _ = g.probe_header(comp, orig, mod)
    arity = len([p for p in f['params'].split(',') if p.strip()])
    args = W.inputs(arity, random.Random(20261019))
    want = W.run(comp, orig, header, name, args); again = W.run(comp, orig, header, name, args)
    good = [(x, w) for x, w, v in zip(args, want, again) if w is not None and w == v]
    args, want = [x for x, _ in good], [w for _, w in good]
    lines = path.read_text(encoding='utf-8').split('\n')
    killed = surv = 0
    for tag, text in muts:
        if tag == 'S': continue
        t = Path(tempfile.mkdtemp(dir=work)); g.make_tree(t, {mod: text})
        if not g.mutant_compiles(comp, t, header): shutil.rmtree(t, ignore_errors=True); continue
        by = g.kill(comp, t, rel, [])
        if not by:
            for i in relp:
                ok, _ = g.run_prop(comp, t, i)
                if not ok: by = ['prop']; break
        if by: killed += 1
        else:
            surv += 1
            changed = [l for a, l in zip(lines, text.split('\n')) if a != l]
            wit = W.first_difference(comp, t, header, name, args, want)
            print(f'{mod}.{name} {tag}: {changed[0].strip() if changed else "(line deleted)"}  ->  ' + (f'WITNESS input {wit[0]} real {wit[1]} mutant {wit[2]}' if wit else f'no witness on {len(args)} inputs'), flush=True)
        shutil.rmtree(t, ignore_errors=True)
    print(f'== {mod}.{name}: {killed} killed, {surv} survive', flush=True)
shutil.rmtree(work, ignore_errors=True)
