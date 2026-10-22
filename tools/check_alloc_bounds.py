#!/usr/bin/env python3
"""R37: enforce "validity before the address is formed" for every computed allocation in lib/.

Every `nirmmita(...)` in lib/*.smlib whose size is computed with a multiplication (directly,
or through a variable assigned from one) must, in the same prakriya and on an earlier line,
be preceded by a constant bound on a count: `yadi (<count> > <constant>) { prati ... }`.
That is the R35/R36 form: the count is checked BEFORE it is multiplied, so a wrapped size
never exists. A site that does not need one must be listed in EXEMPT below, with the reason
(the R36 audit's verdicts). A new computed allocation with neither fails this check.

Constant sizes (`nirmmita(32)`, `nirmmita(3 * 8)`) need nothing.

usage: python3 -B tools/check_alloc_bounds.py      (exit 0 when every site is bounded or explained)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (module, prakriya) -> why its computed allocations need no bound before the multiply
EXEMPT = {
    ('nighantu', 'nighantu_vardh'): 'oldcap = m[0] <= the nighantu_srij bound, so oldcap * 33 + 1 <= 5.44e18',
    ('nighantu', 'nighantu_mil'): 'scap is the source map capacity, <= the nighantu_srij bound',
    ('sangrah', 'rakh_samroop_diff'): 'a set is a map: cap <= the nighantu_srij bound',
    ('sangrah', 'rakh_sangam'): 'a set is a map: cap <= the nighantu_srij bound',
    ('sangrah', 'rakh_sampat'): 'a set is a map: cap <= the nighantu_srij bound',
    ('sangrah', 'rakh_bhed'): 'a set is a map: cap <= the nighantu_srij bound',
    ('sangrah', 'rakh_asti_upasamuh'): 'a set is a map: cap <= the nighantu_srij bound',
    ('sangrah', 'rakh_tak_mala'): 'a set is a map: cap <= the nighantu_srij bound',
    ('aadhar', 'brihat_ank_tak'): "the caller's own digit count: a wrap needs more than 2^58 digits",
    ('brihat', 'brihat_shesh'): "the caller's own digit count",
    ('brihat', 'brihat_ghatmod'): "the caller's own digit count",
    ('shreni', 'mil_shreni'): "the caller's own array length",
}

BOUND = re.compile(r'yadi \(\s*([\w\[\]]+)\s*>\s*\d+\s*\)\s*\{\s*prati')
TERM = re.compile(r'[A-Za-z_]\w*(?:\[\d+\])?')
CONST_SIZE = re.compile(r'^[\d\s*+]+$')


def main():
    sites = bounded = exempt = 0
    bad = []
    used = set()
    for lib in sorted((ROOT / 'lib').glob('*.smlib')):
        func, mult_vars, bounds = None, {}, set()
        for no, line in enumerate(lib.read_text(encoding='utf-8').split('\n'), 1):
            code = line.split('#', 1)[0]
            m = re.match(r'\s*prakriya\s+(\w+)\s*\(', code)
            if m:
                func, mult_vars, bounds = m.group(1), {}, set()
                continue
            b = BOUND.search(code)
            if b:
                bounds.add(b.group(1))
            a = re.match(r'\s*(?:vitti\s+)?(\w+)\s*=\s*(.+)$', code)
            if a and '*' in a.group(2) and 'nirmmita' not in a.group(2):
                mult_vars[a.group(1)] = set(TERM.findall(a.group(2)))
            for arg in re.findall(r'nirmmita\(([^()]*(?:\([^()]*\)[^()]*)*)\)', code):
                arg = arg.strip()
                if CONST_SIZE.match(arg):
                    continue
                computed = '*' in arg or arg in mult_vars
                if not computed:
                    continue
                sites += 1
                key = (lib.stem, func)
                # the counts this size is computed from, through any variable assigned from a product
                counts, todo = set(), list(TERM.findall(arg))
                while todo:
                    t = todo.pop()
                    if t in counts:
                        continue
                    counts.add(t)
                    todo.extend(mult_vars.get(t, ()))
                if counts & bounds:
                    bounded += 1
                elif key in EXEMPT:
                    exempt += 1
                    used.add(key)
                else:
                    bad.append(f'{lib.name}:{no}: {func}: nirmmita({arg}) with no bound on the count before it')
    for b in bad:
        print('FAIL', b)
    stale = sorted(set(EXEMPT) - used)
    for s in stale:
        print('FAIL stale exemption (no computed allocation there any more):', s)
    print(f'alloc bounds: {sites} computed allocations in lib/: {bounded} bounded before the multiply, '
          f'{exempt} exempt with a reason, {len(bad) + len(stale)} failed')
    return 1 if bad or stale else 0


if __name__ == '__main__':
    sys.exit(main())
