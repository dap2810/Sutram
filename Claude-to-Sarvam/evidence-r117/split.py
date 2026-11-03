# For each guard DIFFER: (a) v296 compiler + v295 lib/source  vs  v295 compiler + v295 lib/source  -> isolates the compiler change
#                        (b) v295 compiler + v296 lib/source vs v295 compiler + v295 lib/source     -> isolates the library change
import subprocess, sys, os, filecmp, shutil
G, NEW, OLD = sys.argv[1], '/home/claude/sutram', sys.argv[1] + '/r116/guard/old'
NC, OC = NEW + '/sutram_compiler', OLD + '/sutram_compiler'
T = G + '/r117/split'; os.makedirs(T, exist_ok=True)
differ = [l.split()[1] for l in open(G + '/r116/guard/guard-elf.txt') if l.startswith('DIFFER')]
def comp(c, root, rel, out):
    if os.path.exists(out): os.remove(out)
    r = subprocess.run([c, os.path.join(root, rel), out], cwd=root, capture_output=True, timeout=60)
    return r.returncode == 0 and os.path.exists(out)
# a mixed root: v296 lib + sources, run by the v295 compiler
# the compiler finds lib/ next to its own binary, so each mix is a copied tree with its own compiler binary
MIX = T + '/mix_b'   # v295 tree, v296 lib, v295 compiler binary
MIXA = T + '/mix_a'  # v295 tree, v295 lib, v296 compiler binary
for d in (MIX, MIXA):
    if os.path.isdir(d): shutil.rmtree(d)
    shutil.copytree(OLD, d, symlinks=True, ignore=shutil.ignore_patterns('.git'))
shutil.rmtree(MIX + '/lib'); shutil.copytree(NEW + '/lib', MIX + '/lib')
shutil.copy(NC, MIXA + '/sutram_compiler')
OCB, NCA = MIX + '/sutram_compiler', MIXA + '/sutram_compiler'
a_same = b_same = 0; a_diff = []; b_diff = []
for rel in differ:
    if not os.path.exists(os.path.join(OLD, rel)): continue
    base = T + '/base.bin'; comp(OC, OLD, rel, base)
    x = T + '/a.bin'; comp(NCA, MIXA, rel, x)
    if filecmp.cmp(base, x, shallow=False): a_same += 1
    else: a_diff.append(rel)
    y = T + '/b.bin'
    shutil.copy(os.path.join(OLD, rel), os.path.join(MIX, rel))  # v295 program text, v296 lib
    if not comp(OCB, MIX, rel, y): b_diff.append(rel)
    elif filecmp.cmp(base, y, shallow=False): b_same += 1
    else: b_diff.append(rel)
print(f'(a) v296 COMPILER on v295 lib + v295 program text: {a_same} byte-identical to v295, {len(a_diff)} differ {a_diff}')
open(T+"/b_diff.txt","w").write(chr(10).join(b_diff))
print(f'(b) v295 compiler on v296 LIB + v295 program text: {b_same} byte-identical, {len(b_diff)} differ or do not compile (v296 lib uses abhava(cond, msg), which v295 cannot parse)')
