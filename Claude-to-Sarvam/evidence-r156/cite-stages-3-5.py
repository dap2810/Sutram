# R156: stages 3-5 of the Windows citation audit, as run after cite2.py (stages 1-2) wrote plan2.json.
# Each stage reads the previous stage's still-uncited list and keeps what it finds cited.
import json, re, os, collections, fnmatch, subprocess, sys
S = sys.argv[1]                      # the folder holding plan2.json
os.chdir(sys.argv[2])                # the repository
files = [f for f in subprocess.run(['git','ls-files','-z'],capture_output=True).stdout.decode().split('\0') if f]
# stage 3: the basename in any .md/.html anywhere in the tree
alltext = '\n'.join(open(f,encoding='utf-8',errors='replace').read() for f in files if f.lower().endswith(('.md','.html','.htm')))
p3 = [(f,s) for f,s in json.load(open(S+'/plan2.json')) if not re.search(r'(?<![\w.-])'+re.escape(os.path.basename(f))+r'(?![\w])', alltext)]
# stage 4: named by a script in its own folder
scripts = collections.defaultdict(str)
for f in files:
    if f.startswith('Windows-to-Sarvam/') and f.count('/')>=2 and f.lower().endswith(('.ps1','.py','.psm1','.sh','.cmd','.bat')):
        scripts[f.split('/')[1]] += open(f,encoding='utf-8',errors='replace').read()+'\n'
p4 = [(f,s) for f,s in p3 if os.path.basename(f) not in scripts[f.split('/')[1]]]
# stage 5: a wildcard pattern in its folder's reports, or its name's first two words close together in them
md = collections.defaultdict(str)
for f in files:
    if f.startswith('Windows-to-Sarvam/') and f.lower().endswith('.md'):
        p = f.split('/'); md[p[1] if len(p)>2 else '(top)'] += open(f,encoding='utf-8',errors='replace').read()+'\n'
p5 = []
for f,s in p4:
    folder = f.split('/')[1]; rel = f.split('/',2)[2]; t = md[folder]
    pats = set(re.findall(r'[A-Za-z0-9_./-]*\*[A-Za-z0-9_.*-]*', t))
    hit = any(fnmatch.fnmatch(rel,p) or fnmatch.fnmatch(os.path.basename(rel),p) for p in pats if p not in ('*','**'))
    w = os.path.splitext(os.path.basename(rel))[0].split('-')
    prose = len(w)>=2 and re.search(r'\b'+re.escape(w[0])+r'\b[^.\n]{0,40}\b'+re.escape(w[1][:6]), t, re.I)
    if not (hit or prose): p5.append((f,s))
for n,p in (('plan3.json',p3),('plan4.json',p4),('plan5.json',p5)): json.dump(p, open(os.path.join(S,n),'w'))
print(len(p3), len(p4), len(p5), sum(s for _,s in p5))
