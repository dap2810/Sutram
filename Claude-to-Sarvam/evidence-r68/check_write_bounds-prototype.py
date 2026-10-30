#!/usr/bin/env python3
"""R68 prototype (WS3 pricing): does the body of a lib prakriya stay within the capacity its
contract states for a caller-supplied buffer?

Contract: a comment line above the prakriya with `>= <expr> cells|bytes|elements` (vakyank, roop)
or `out must hold <expr> elements` (samanvaya). The buffer is the parameter the body writes through
(directly or through a `vitti dst = out` alias). Body: every `buf[idx] =` / `akshar_rakh(buf, idx, ..)`
is bounded by evaluating idx on a grid of small parameter values (0..GRID), with each loop variable
at both ends of its range (`yavat (v < B)` with v = init, v = v + 1 -> [init, B-1]; `yavat (v >= B)`
with v = v - 1 -> [B, init]), under the path conditions that enclose the write (the `yadi` headers
around it, and the complement of every top-level `yadi (c) { nivartanam }` before it).
Reports OVER with the grid point that does it. Affine code only: a write whose index or loop bound
this cannot read is reported UNREAD, never skipped.
"""
import re, sys, glob, os, itertools

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/sutram"
GRID = 6
CONTRACT = re.compile(r'(?:>=\s*(?P<e1>[\w\s+*/()-]+?)\s*(?:cells|bytes|elements))|(?:must hold\s+(?P<e2>[\w\s+*/()-]+?)\s*elements)')
PRAK = re.compile(r'^prakriya\s+(\w+)\s*\(([^)]*)\)')
W_CELL = re.compile(r'^\s*(\w+)\[([^\]]+)\]\s*=(?!=)')
W_BYTE = re.compile(r'^\s*akshar_rakh\(\s*(\w+)\s*,\s*([^,]+),')
ASSIGN = re.compile(r'^\s*(?:vitti\s+)?(\w+)\s*=(?!=)\s*(.+?)\s*$')
YAVAT = re.compile(r'^\s*yavat\s*\((.*)\)\s*\{')
YADI = re.compile(r'^\s*yadi\s*\((.*)\)\s*\{\s*(nivartanam\b.*)?')

def py(expr):
    e = expr.replace('/', '//')
    return e

def ev(expr, env):
    try:
        return eval(py(expr), {'__builtins__': {}}, dict(env))
    except Exception:
        return None

def strip(line):
    out, q = [], False
    for ch in line:
        if ch == '"': q = not q
        if ch == '#' and not q: break
        out.append(ch)
    return ''.join(out)

def audit(path):
    lines = open(path).read().split('\n')
    mod = os.path.basename(path)[:-6]
    i, n, rows = 0, len(lines), []
    while i < n:
        m = PRAK.match(lines[i])
        if not m:
            i += 1; continue
        name, params = m.group(1), [p.split()[-1] for p in m.group(2).split(',') if p.strip()]
        j = i - 1; comment = []
        while j >= 0 and lines[j].startswith('#'):
            comment.append(lines[j]); j -= 1
        cm = CONTRACT.search(' '.join(reversed(comment)))
        k = i + 1; body = []
        while k < n and not lines[k].startswith('}'):
            body.append((k + 1, strip(lines[k]))); k += 1
        if cm:
            cap = (cm.group('e1') or cm.group('e2')).strip()
            rows.append(check(mod, name, params, cap, body))
        i = k + 1
    return rows

def check(mod, name, params, cap, body):
    alias, defs, stack, guards, writes = {}, {}, [], [], []
    # stack entries: (indent, kind, data) kind in {'yavat','yadi','other'}
    for ln, code in body:
        if not code.strip(): continue
        ind = len(code) - len(code.lstrip())
        while stack and stack[-1][0] >= ind:
            stack.pop()
        y = YAVAT.match(code)
        d = YADI.match(code)
        if y:
            stack.append((ind, 'yavat', y.group(1))); continue
        if d:
            if d.group(2) and not stack:          # top-level early return: its complement holds after
                guards.append('not (%s)' % d.group(1))
            else:
                stack.append((ind, 'yadi', d.group(1)))
            continue
        w = W_CELL.match(code) or W_BYTE.match(code)
        if w:
            writes.append((ln, w.group(1), w.group(2).strip(), [s for s in stack], list(guards)))
        a = ASSIGN.match(code)
        if a:
            lhs, rhs = a.group(1), a.group(2)
            if '[' in lhs: continue
            if re.fullmatch(r'\w+', rhs) and rhs in params or rhs in alias:
                alias[lhs] = alias.get(rhs, rhs)
            else:
                defs.setdefault(lhs, []).append((ln, rhs))
    buf = None
    for ln, b, idx, st, g in writes:
        root = alias.get(b, b)
        if root in params:
            buf = root; break
    if buf is None:
        return (mod, name, cap, 'NO-WRITE', 'no write into a parameter buffer')
    verdict, detail = 'WITHIN', ''
    unread = []
    for ln, b, idx, st, g in writes:
        if alias.get(b, b) != buf: continue
        # loop variable ranges from the enclosing yavat headers
        ranges, conds = {}, list(g)
        for _, kind, data in st:
            if kind == 'yadi':
                conds.append(data); continue
            lm = re.match(r'\s*(\w+)\s*(<=|<|>=|>)\s*(.+?)\s*$', data)
            if not lm:
                unread.append('%d: loop %s' % (ln, data)); continue
            v, op, bound = lm.groups()
            inits = [r for l, r in defs.get(v, []) if l < ln]
            init = inits[-1] if inits else None
            if init is None:
                unread.append('%d: loop var %s has no init' % (ln, v)); continue
            ranges[v] = (op, init, bound)
        def names(e): return set(re.findall(r'[A-Za-z_]\w*', e))
        free = set()
        for e in [idx] + [r[1] for r in ranges.values()] + [r[2] for r in ranges.values()] + conds + [cap]:
            free |= names(e)
        free -= set(ranges) | {'not', 'and', 'or'}
        # locals defined once from an affine expression are substituted; others are grid variables
        subst = {a: r for a, r in alias.items() if r != buf and a != r}
        for v in list(free):
            if v in params: continue
            ds = [r for l, r in defs.get(v, []) if l < ln]
            if len(ds) == 1 and v not in ranges:
                subst[v] = ds[0]
        # one round of substitution (vitti shift = w - cnt; vitti w = width)
        def expand(e):
            for _ in range(4):
                for v, r in subst.items():
                    e = re.sub(r'(?<![\w.])%s(?![\w(])' % re.escape(v), '(%s)' % r, e)
            return e
        idx_e, cap_e = expand(idx), expand(cap)
        conds_e = [expand(c) for c in conds]
        rng_e = {v: (op, expand(a), expand(b)) for v, (op, a, b) in ranges.items()}
        vars_ = set()
        for e in [idx_e, cap_e] + conds_e + [x for r in rng_e.values() for x in r[1:]]:
            vars_ |= names(e)
        vars_ -= set(rng_e) | {'not', 'and', 'or'}
        vars_ = sorted(vars_)
        worst = None
        for pt in itertools.product(range(GRID + 1), repeat=len(vars_)):
            env = dict(zip(vars_, pt))
            if any(ev(c, env) is not True for c in conds_e):
                continue
            capv = ev(cap_e, env)
            if capv is None: unread.append('%d: capacity %s' % (ln, cap)); break
            # loop vars at both ends of their ranges (affine index -> extremes)
            ends = []
            ok = True
            for v, (op, a, bnd) in rng_e.items():
                av, bv = ev(a, env), ev(bnd, env)
                if av is None or bv is None: ok = False; break
                if op == '<': lo, hi = av, bv - 1
                elif op == '<=': lo, hi = av, bv
                elif op == '>=': lo, hi = bv, av
                else: lo, hi = bv + 1, av
                if hi < lo: ok = False; break      # loop does not run
                ends.append((v, lo, hi))
            if not ok: continue
            for choice in itertools.product(*[(lo, hi) for _, lo, hi in ends]):
                e2 = dict(env); e2.update({v: c for (v, _, _), c in zip(ends, choice)})
                iv = ev(idx_e, e2)
                if iv is None: unread.append('%d: index %s' % (ln, idx)); ok = False; break
                if iv >= capv or iv < 0:
                    if worst is None or iv - capv > worst[0]:
                        worst = (iv - capv, ln, idx, dict(e2), capv)
            if not ok: break
        if worst:
            verdict = 'OVER'
            detail += ' :%d %s[%s] = index %d, capacity %d at %s;' % (
                worst[1], buf, worst[2], worst[0] + worst[4], worst[4],
                ','.join('%s=%s' % kv for kv in sorted(worst[3].items()) if kv[0] in vars_ or kv[0] in rng_e))
    if unread:
        verdict = verdict if verdict == 'OVER' else 'UNREAD'
        detail += ' unread: ' + '; '.join(unread[:3])
    return (mod, name, cap, verdict, detail.strip())

if __name__ == '__main__':
    files = sorted(glob.glob(os.path.join(ROOT, 'lib', '*.smlib')))
    total = 0
    for f in files:
        for r in audit(f):
            total += 1
            print('%-10s %-22s cap=%-22s %-8s %s' % r)
    print('%d contracts read' % total)
