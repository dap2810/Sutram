import subprocess, os, collections, re, json, sys
os.chdir('/home/claude/sutram')
files = [f for f in subprocess.run(['git','ls-files','-z'],capture_output=True).stdout.decode().split('\0') if f]
W = 'Windows-to-Sarvam/'
KEEP_EXT = ('.md', '.ps1', '.py', '.sha256', '.psm1', '.sh', '.bat', '.cmd', '.html', '.htm')
def rd(f):
    try: return open(f, encoding='utf-8', errors='replace').read()
    except Exception: return ''
mds = {f: rd(f) for f in files if f.lower().endswith(('.md', '.html', '.htm'))}
win = [f for f in files if f.startswith(W) and f.count('/') >= 2]
folders = collections.defaultdict(list)
for f in win: folders[f.split('/')[1]].append(f)
cited = set()
def scan(text, folder, fs, same):
    for f in fs:
        rel = f[len(W) + len(folder) + 1:]; base = os.path.basename(f)
        if (folder + '/' + rel) in text: cited.add(f); continue
        if same and (rel in text or re.search(r'(?<![\w.-])' + re.escape(base) + r'(?![\w])', text)): cited.add(f); continue
        # a directory named as a whole: 'screenshots/' or `screenshots`
        d = os.path.dirname(rel)
        while d:
            if same and (d + '/') in text or (folder + '/' + d + '/') in text or (folder + '/' + d + '`') in text: cited.add(f); break
            d = os.path.dirname(d)
for folder, fs in folders.items():
    for m, t in mds.items():
        same = m.startswith(W + folder + '/') or (m.startswith(W) and m.count('/') == 1 and folder in t)
        if same or folder in t:
            scan(t, folder, fs, same or (folder in t and False))
    # one level of chain: a cited text/json index in the folder naming a file by basename
    idx = [f for f in fs if f in cited and f.lower().endswith(('.json', '.txt', '.csv', '.tsv', '.log'))]
    for i in idx:
        t = rd(i)
        for f in fs:
            if f not in cited and re.search(r'(?<![\w.-])' + re.escape(os.path.basename(f)) + r'(?![\w])', t): cited.add(f)
plan = [(f, os.lstat(f).st_size) for f in win if f not in cited and not os.path.basename(f).lower().endswith(KEEP_EXT)]
tot = sum(s for _, s in plan)
print('Windows files', len(win), 'cited data', sum(1 for f in win if f in cited), 'uncited data', len(plan), f'{tot/1e6:.2f} MB')
c = collections.Counter(); n = collections.Counter()
for f, s in plan: k = f.split('/')[1]; c[k] += s; n[k] += 1
for k, v in c.most_common(40): print(f'{v/1e6:7.2f} MB {n[k]:5d}  {k}')
e = collections.Counter()
for f, s in plan: e[os.path.splitext(f)[1].lower()] += s
print(e.most_common(12))
json.dump(plan, open('/tmp/claude-0/-home-claude/e35834e8-b611-5238-b1df-59668dfdca3d/scratchpad/r155/plan2.json','w'))
