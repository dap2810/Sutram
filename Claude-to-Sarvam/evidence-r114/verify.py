"""R114: every guard DIFFER must be the token and nothing else.
  verify.py NEW_ROOT GUARD_OUT_DIR GUARD_TXT [--run]
For each DIFFER line: old.replace(b'Sutram Error', b'Sutram truti') == new, byte for byte (same length, so no
offset moves). With --run (ELF only): both binaries are run; old output with the token replaced == new output,
same exit code. Prints a count and every failure."""
import glob, os, re, subprocess, sys
PATTERNS = ['examples/*.sm', 'examples/*/*.sm', 'tests/stdlib/*.sm', 'tests/r*/*.sm', 'tests/r*/*/*.sm']
root, gdir, gtxt = sys.argv[1:4]; run = '--run' in sys.argv
ext = '.exe' if os.path.exists(os.path.join(gdir, '0.new.exe')) or any(f.endswith('.exe') for f in os.listdir(gdir)) else ''
rels = sorted({os.path.relpath(p, root) for pat in PATTERNS for p in glob.glob(os.path.join(root, pat))})
differ = [m.group(1) for l in open(gtxt) for m in [re.match(r'DIFFER\s+(\S+)', l)] if m]
ok = bad = runs_ok = runs_bad = 0; n_tokens = 0
for rel in differ:
    i = rels.index(rel)
    o = open(f'{gdir}/{i}.old{ext}', 'rb').read(); n = open(f'{gdir}/{i}.new{ext}', 'rb').read()
    if len(o) == len(n) and o.replace(b'Sutram Error', b'Sutram truti') == n:
        ok += 1; n_tokens += o.count(b'Sutram Error')
    else:
        bad += 1; print('NOT TOKEN-ONLY', rel, len(o), len(n))
    if run and not ext:
        res = []
        for f in (f'{gdir}/{i}.old', f'{gdir}/{i}.new'):
            os.chmod(f, 0o755)
            try:
                r = subprocess.run([f], capture_output=True, timeout=20, cwd=root, input=b'')
                res.append((r.returncode, r.stdout + r.stderr))
            except subprocess.TimeoutExpired:
                res.append(('timeout', b''))
        if res[0][0] == res[1][0] and res[0][1].replace(b'Sutram Error', b'Sutram truti') == res[1][1]:
            runs_ok += 1
        else:
            runs_bad += 1; print('RUN DIFFERS', rel, res[0][0], res[1][0])
print(f'{len(differ)} DIFFER: {ok} differ only by the token ({n_tokens} occurrences), {bad} otherwise'
      + (f'; run: {runs_ok} same output and exit code after the token, {runs_bad} otherwise' if run and not ext else ''))
