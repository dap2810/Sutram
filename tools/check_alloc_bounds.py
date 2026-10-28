#!/usr/bin/env python3
"""R37: enforce "validity before the address is formed" for every computed allocation in lib/.

Every `nirmmita(...)` in lib/*.smlib whose size is not a constant (R37: computed with a
multiplication, directly or through a variable assigned from one; R39: any size) must, in the same prakriya and on an earlier line,
be preceded by a constant bound on a count: `yadi (<count> > <constant>) { nivartanam ... }` (or `prati`, its alias).
That is the R35/R36 form: the count is checked BEFORE it is multiplied, so a wrapped size
never exists. A site that does not need one must be listed in EXEMPT below, with the reason
(the R36 audit's verdicts). A new computed allocation with neither fails this check.

Constant sizes (`nirmmita(32)`, `nirmmita(3 * 8)`) need nothing. A `nirmmita(` this line-based
reader cannot read whole on its line (split over lines, nested parentheses two deep) fails (R38),
so it is never skipped unchecked.

R39 (Sarvam's WS3: does this check follow where a size comes from, or only how it is spelled?):
  * an exemption names the expression, not only the prakriya, so a new allocation in an exempt
    prakriya is not exempt;
  * the bound must be small enough: the size, with every bounded count at its bound, must fit
    in 2^63 - 1 (a bound like `c > 10^18` before `c * 33` fails);
  * a bounded count assigned again after its bound is no longer bounded.
  * a bounded plain count needs a check below as well (`c < 0` or `c < 1`): a negative count
    wraps to a positive size too (mala_nava, R37). A container's field (X[1]) is its constructor's;
  * every size that is not a constant is checked - a parameter (the multiply is in the caller)
    or a function's result as well as a product - so no channel skips the check.
  * a bound counts only while the block it is in is still open: one inside a branch does not
    cover an allocation after the branch.
What it still cannot see: the value of a count a CALLER passes (its exemption reason must say
why the caller is trusted), a '#' inside a string literal, and anything a regular expression
over one line misreads; it is a structured approximation, not a proof.

usage: python3 -B tools/check_alloc_bounds.py      (exit 0 when every site is bounded or explained)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (module, prakriya, size expression) -> why that allocation needs no bound before the multiply.
# R39: keyed by the expression too, so a NEW allocation in an exempt prakriya is not exempt.
# R39: every remaining exemption sizes from a container's own capacity (X[0]), which its
# constructor bounds (nighantu_srij: c <= 164703072086692424, so X[0] * 33 + 1 <= 5.44e18).
# Before R39 the sets sized from the caller's cap argument, which nothing bounds or checks.
CAP = "a container's own capacity X[0], bounded by nighantu_srij: X[0] * 33 + 1 <= 5.44e18"
EXEMPT = {
    ('nighantu', 'nighantu_vardh', 'oldcap * 33 + 1'): 'oldcap = m[0]: ' + CAP,
    ('nighantu', 'nighantu_mil', 'src[0] * 33 + 1'): CAP,
    ('sangrah', 'rakh_samroop_diff', 'a[0] * 33 + 1'): CAP,
    ('sangrah', 'rakh_samroop_diff', 'b[0] * 33 + 1'): CAP,
    ('sangrah', 'rakh_sangam', 'a[0] * 33 + 1'): CAP,
    ('sangrah', 'rakh_sangam', 'b[0] * 33 + 1'): CAP,
    ('sangrah', 'rakh_sampat', 'a[0] * 33 + 1'): CAP,
    ('sangrah', 'rakh_bhed', 'a[0] * 33 + 1'): CAP,
    ('sangrah', 'rakh_asti_upasamuh', 'a[0] * 33 + 1'): CAP,
    ('sangrah', 'rakh_tak_mala', 's[0] * 33 + 1'): CAP,
    ('sangrah', 'rakh_tak_mala', 's[0] * 32 + 1'): CAP,
    ('sangrah', 'rakh_tak_mala', 's[0] * 8'): CAP,
}
INT64_MAX = 2 ** 63 - 1

LOWER = re.compile(r'yadi \(\s*(\w+)\s*<\s*\d+\s*\)')   # R39: c < 0, c < 1, c < 2 ...: a clamp or a return
BOUND = re.compile(r'yadi \(\s*([\w\[\]]+)\s*>\s*(\d+)\s*\)\s*\{\s*(?:nivartanam|prati)\b')   # R54: lib/ says nivartanam; prati is its alias
TERM = re.compile(r'[A-Za-z_]\w*(?:\[\d+\])?')
CONST_SIZE = re.compile(r'^[\d\s*+]+$')


def assigned(code):
    """The names a line assigns to (`x = ...`, `vitti x = ...`); `==`, `<=`, `>=`, `!=` are not assignments."""
    return [m.group(1) for m in re.finditer(r'([A-Za-z_]\w*(?:\[\d+\])?)\s*=(?!=)', code)]


def size_at_bound(arg, exprs, bounds):
    """The size with every bounded count at its bound, or None if it cannot be computed."""
    text, seen = arg, set()
    for _ in range(8):
        names = [t for t in TERM.findall(text) if t not in bounds and t in exprs and t not in seen]
        if not names:
            break
        for t in names:
            seen.add(t)
            text = re.sub(r'(?<![\w\[])' + re.escape(t) + r'(?![\w\[])', '(' + exprs[t] + ')', text)
    for t, (k, _no, _d) in bounds.items():
        text = re.sub(r'(?<![\w\[])' + re.escape(t) + r'(?![\w\[])', str(k), text)
    if not re.fullmatch(r'[\d\s*+()-]+', text):
        return None
    return eval(text, {'__builtins__': {}})


def main():
    sites = bounded = exempt = 0
    bad = []
    used = set()
    for lib in sorted((ROOT / 'lib').glob('*.smlib')):
        func, exprs, bounds, lowers, depth = None, {}, {}, {}, 0
        for no, line in enumerate(lib.read_text(encoding='utf-8').split('\n'), 1):
            code = line.split('#', 1)[0]
            # R39: a bound counts only while the block it is in is open, so a bound inside a
            # branch does not cover an allocation after that branch
            for table in (bounds, lowers):
                for name in [n for n, v in table.items() if (v[2] if table is bounds else v[1]) > depth]:
                    del table[name]
            here = depth
            depth += code.count('{') - code.count('}')
            m = re.match(r'\s*prakriya\s+(\w+)\s*\(', code)
            if m:
                func, exprs, bounds, lowers = m.group(1), {}, {}, {}
                continue
            b = BOUND.search(code)
            if b:
                bounds[b.group(1)] = (int(b.group(2)), no, here)
            lo = LOWER.search(code)
            if lo:
                lowers[lo.group(1)] = (no, here)
            # R39: a bounded count assigned again after its bound is no longer bounded
            for name in assigned(code):
                if name in bounds and bounds[name][1] != no:
                    del bounds[name]
                if name in lowers and lowers[name][0] != no:
                    del lowers[name]
            a = re.match(r'\s*(?:vitti\s+)?(\w+)\s*=\s*(.+)$', code)
            if a and '*' in a.group(2) and 'nirmmita' not in a.group(2):
                exprs[a.group(1)] = a.group(2).strip()
            args = re.findall(r'nirmmita\(([^()]*(?:\([^()]*\)[^()]*)*)\)', code)
            if len(args) != len(re.findall(r'\bnirmmita\s*\(', code)):
                # R38: a call this line-based reader cannot read (split over lines, or nested
                # deeper than one level) would otherwise be skipped, not checked
                bad.append(f'{lib.name}:{no}: {func}: a nirmmita( call this check cannot read on one line')
            for arg in args:
                arg = arg.strip()
                if CONST_SIZE.match(arg):
                    continue
                # R39: every size that is not a constant counts - a product here, a variable assigned
                # from one, a parameter (the multiply is in the caller) or a function's result
                sites += 1
                key = (lib.stem, func, arg)
                # the counts this size is computed from, through any variable assigned from a product
                counts, todo = set(), list(TERM.findall(arg))
                while todo:
                    t = todo.pop()
                    if t in counts:
                        continue
                    counts.add(t)
                    todo.extend(TERM.findall(exprs.get(t, '')))
                if counts & set(bounds):
                    # R39: the bound must be small enough: the size at the bound must fit
                    v = size_at_bound(arg, exprs, bounds)
                    # R39: a negative count wraps too (mala_nava, R37: -2^61 + 1 cells of 8 bytes is 8).
                    # A plain count needs a lower check; a container's field (X[1]) is set by its constructor.
                    unsigned = sorted(t for t in counts & set(bounds) if '[' not in t and t not in lowers)
                    if unsigned:
                        bad.append(f'{lib.name}:{no}: {func}: nirmmita({arg}): {", ".join(unsigned)} has an upper '
                                   f'bound but no check below (c < 0, c < 1 ...) before it')
                    elif v is None:
                        bad.append(f'{lib.name}:{no}: {func}: nirmmita({arg}): bounded, but the size at the bound '
                                   f'cannot be computed here, so the bound cannot be checked')
                    elif v > INT64_MAX:
                        bad.append(f'{lib.name}:{no}: {func}: nirmmita({arg}): the bound is too large - the size '
                                   f'at the bound is {v}, past 2^63 - 1')
                    else:
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
