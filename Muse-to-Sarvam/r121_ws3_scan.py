# Round 121 WS3 method: does any lib function allocate inside a loop body?
# (1) Braced-loop scan: for every prakriya body, find yavat/chakra headers and
# their braced bodies; report any alloc call (nirmmita/kosh_kship/kosh_yuj/
# vartani_sandhi/vartani_cat) inside one. Result on v297: 0 hits.
# (2) Candidate check: the 20 functions whose body contains both a loop and an
# alloc call; print every alloc line (all are at function lines 1-16, i.e.
# allocate-once-before-the-loop, then fill in the loop).
import re, glob
def bodies(text):
    out = []
    for m in re.finditer(r'prakriya\s+(\w+)\s*\(', text):
        i = text.find('{', m.end())
        if i < 0: continue
        depth = 0; j = i
        while j < len(text):
            if text[j] == '{': depth += 1
            elif text[j] == '}':
                depth -= 1
                if depth == 0: break
            j += 1
        out.append((m.group(1), text[i:j+1]))
    return out
def loop_bodies(body):
    res = []
    for m in re.finditer(r'(?:yavat|chakra)\s*\(', body):
        i = body.find('{', m.end())
        if i < 0: continue
        depth = 0; j = i
        while j < len(body):
            if body[j] == '{': depth += 1
            elif body[j] == '}':
                depth -= 1
                if depth == 0: break
            j += 1
        res.append(body[i:j+1])
    return res
ALLOCS = ('nirmmita', 'kosh_kship', 'kosh_yuj', 'vartani_sandhi', 'vartani_cat')
for f in sorted(glob.glob('lib/*.smlib')):
    for name, body in bodies(open(f).read()):
        for lb in loop_bodies(body):
            hit = [a for a in ALLOCS if a in lb]
            if hit:
                print(f"{f}::{name}: alloc-in-loop {hit}")
print("braced-loop scan done (no output above = 0 alloc-in-loop)")
