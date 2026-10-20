#!/usr/bin/env python3
"""R15-03: for each mutant that survived tools/lib_mutant_score.py, look for an
input that tells it apart from the real function (a WITNESS).

It reuses tools/lib_mutant_witness.py (R8): the same input sets, the same rule
that only functions whose parameters are all plain numbers can be tried. The
mutants are rebuilt with lib_mutant_score.mutants() in the same order, so the
k-th mutant here is the k-th one the scorer ran.

  WITNESS     an input gives a different result: the proofs miss a real defect
  NO-WITNESS  no input in the set told it apart: likely equivalent
  NOT-TRIED   a parameter is a list, string or record (or no number input runs cleanly)

usage (repository root):
  python3 -B Claude-to-Sarvam/evidence-r15/proofs/witness_r15.py SCORE.json OUT.json [--compiler C]
"""
import json
import random
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools'))
import lib_proof_gaps as G  # noqa: E402
import lib_mutant_witness as W  # noqa: E402
import lib_mutant_score as S  # noqa: E402


def main(argv):
    score, outp = argv[0], argv[1]
    compiler = str(Path(argv[argv.index('--compiler') + 1] if '--compiler' in argv else ROOT / 'sutram_compiler').resolve())
    rows = json.load(open(score, encoding='utf-8'))
    funcs = {(f['module'], f['name']): f for p in sorted(G.LIB.glob('*.smlib')) for f in G.parse_module(p)}
    ptrs = W.pointer_params(funcs)
    work = Path(tempfile.mkdtemp())
    report = []
    try:
        for r in rows:
            surv = [i for i, m in enumerate(r['mutants']) if m[1] == 'SURVIVED']
            if not surv:
                continue
            f = funcs[(r['module'], r['name'])]
            base = {'module': f['module'], 'name': f['name']}
            if ptrs[(f['module'], f['name'])]:
                report += [dict(base, mutant=r['mutants'][i][0], result='NOT-TRIED',
                                why='a parameter is a list, string or record') for i in surv]
                continue
            path = G.LIB / (f['module'] + '.smlib')
            ms = S.mutants(path, f, 40, random.Random('%s.%s' % (f['module'], f['name'])))
            assert [m[0] for m in ms] == [m[0] for m in r['mutants']], (f['name'], 'mutant order differs')
            orig = Path(tempfile.mkdtemp(dir=work))
            G.make_tree(orig)
            header, _ = G.probe_header(compiler, orig, f['module'])
            arity = len([p for p in f['params'].split(',') if p.strip()])
            args = W.inputs(arity, random.Random(20261019))
            want = W.run(compiler, orig, header, f['name'], args)
            again = W.run(compiler, orig, header, f['name'], args)
            good = [(x, w) for x, w, v in zip(args, want, again) if w is not None and w == v]
            args, want = [x for x, _ in good], [w for _, w in good]
            print('%s.%s: %d inputs, %d survivors' % (f['module'], f['name'], len(args), len(surv)), flush=True)
            for i in surv:
                tag = ms[i][0]
                if not args:
                    report.append(dict(base, mutant=tag, result='NOT-TRIED', why='no number input runs cleanly'))
                    continue
                mt = Path(tempfile.mkdtemp(dir=work))
                G.make_tree(mt, {f['module']: ms[i][1]})
                wit = W.first_difference(compiler, mt, header, f['name'], args, want)
                if wit:
                    report.append(dict(base, mutant=tag, result='WITNESS', input=list(wit[0]),
                                       real=wit[1], mutant_gives=wit[2]))
                else:
                    report.append(dict(base, mutant=tag, result='NO-WITNESS', inputs_tried=len(args)))
                shutil.rmtree(mt, ignore_errors=True)
            shutil.rmtree(orig, ignore_errors=True)
    finally:
        shutil.rmtree(work, ignore_errors=True)
    Path(outp).write_text(json.dumps(report, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    from collections import Counter
    print(dict(Counter(x['result'] for x in report)))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
