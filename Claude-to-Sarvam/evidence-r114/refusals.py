"""R114: every refusal's message must change by the token only. refusals.py OLD_COMPILER NEW_COMPILER GUARD_TXT ROOT"""
import os, re, subprocess, sys, tempfile
oc, nc, gtxt, root = sys.argv[1:5]
rels = [m.group(1) for l in open(gtxt) for m in [re.match(r'REFUSED-SAME\s+(\S+)', l)] if m]
d = tempfile.mkdtemp(); ok = bad = 0
for rel in rels:
    outs = []
    for c in (oc, nc):
        r = subprocess.run([c, rel, os.path.join(d, 'x')], capture_output=True, cwd=root)
        outs.append((r.returncode, r.stdout + r.stderr))
    if outs[0][0] == outs[1][0] and outs[0][1].replace(b'Sutram Error', b'Sutram truti') == outs[1][1]:
        ok += 1
    else:
        bad += 1; print('MESSAGE DIFFERS', rel)
print(f'{len(rels)} refusals: {ok} messages differ only by the token, {bad} otherwise')
