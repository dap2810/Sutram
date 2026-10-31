import os, re, subprocess, sys
from urllib.parse import unquote
ROOT='/home/claude/sutram'; os.chdir(ROOT)
STAY='AI-WORK-DIVISION BUILDING CHANGELOG CI-NOTIFICATION-POLICY ERROR-CONVENTION FREESTANDING INSTALLATION-ROUTES LANGUAGE-REFERENCE LIBRARY-BOUNDARY MEMORY-MODEL NUMERIC-CONTRACT OBJECT-FORMAT OPEN-ISSUES OVERFLOW-SAFETY PATH-TO-COMPLETION SANDESH SPECIFICATION WHATS-LEFT WINDOWS-PORT-PLAN WINDOWS-SETUP'.split()
VOCAB='VOCABULARY-TABLE VOCABULARY-SHORT VOCABULARY-COMPLETE VOCABULARY-RULE VOCABULARY-DERIVATION'.split()
DEC='MEMORY-DECISION MEMORY-UNIQUE-HYBRID ALIAS-DESIGN MEMORY-DESIGN MEMORY-IMPROVEMENTS MEMORY-MY-IDEA'.split()
mds=sorted(f[:-3] for f in os.listdir('docs') if f.endswith('.md'))
assert len(mds)==75, len(mds)
M={}
for n in mds:
    if n in STAY: continue
    if n in VOCAB: d='vocabulary'
    elif n in DEC: d='decisions'
    elif re.match(r'R\d+-',n): d='rounds'
    else: d='reports'
    M[f'docs/{n}.md']=f'docs/{d}/{n}.md'
assert all(f'docs/{s}.md' not in M for s in STAY) and len(M)==55
# --- WS2: split the changelog (fence-aware), 20 newest entries stay
lines=open('docs/CHANGELOG.md',encoding='utf-8').read().split('\n')
fence=False; starts=[]
for i,l in enumerate(lines):
    if l.lstrip().startswith('```'): fence=not fence
    elif not fence and l.startswith('## '): starts.append(i)
assert starts[0]==0, starts[:2]
cut=starts[20]
keep=lines[:cut]; old=lines[cut:]
first_old=old[0][3:].split(' - ')[0]; last_keep=lines[starts[19]][3:].split(' - ')[0]
keep=['> **The 20 newest entries.** Older ones, from %s back to the first, are in [rounds/CHANGELOG-ARCHIVE.md](rounds/CHANGELOG-ARCHIVE.md) (split in R88).'%first_old,'']+keep
old=['> **Older changelog entries**, %s and earlier. The 20 newest are in [../CHANGELOG.md](../CHANGELOG.md) (split in R88). Entries are kept as written; only links were updated for the R88 move.'%first_old,'']+old
open('docs/CHANGELOG.md','w',encoding='utf-8').write('\n'.join(keep).rstrip('\n')+'\n')
open('docs/CHANGELOG-ARCHIVE.md','w',encoding='utf-8').write('\n'.join(old))
M['docs/CHANGELOG-ARCHIVE.md']='docs/rounds/CHANGELOG-ARCHIVE.md'
print(f'changelog: {len(starts)} entries; kept 20 (down to {last_keep}); archived {len(starts)-20} (from {first_old})')
# --- files whose text may be rewritten
tracked=[f for f in subprocess.run(['git','ls-files'],capture_output=True,text=True).stdout.split('\n') if f]+['docs/CHANGELOG-ARCHIVE.md']
EXT=('.md','.html','.py','.sh','.yml','.yaml','.ps1','.psm1','.bat','.cmd','.nsi')
cand=[f for f in tracked if not f.startswith('backups/') and f.endswith(EXT) and os.path.isfile(f)]
newloc=lambda p: M.get(p,p)
LINK=re.compile(r'(\]\(\s*<?)([^)\s>]+)(>?(?:\s+"[^"]*")?\s*\))|(href=")([^"]+)(")')
changed={}; nlinks=0; nment=0
for f in cand:
    text=open(f,encoding='utf-8',errors='surrogateescape').read(); orig=text
    fnew=newloc(f)
    if f.endswith(('.md','.html')):
        def fix(m):
            global nlinks
            pre,t,post=(m.group(1),m.group(2),m.group(3)) if m.group(2) is not None else (m.group(4),m.group(5),m.group(6))
            if re.match(r'^[a-z][a-z0-9+.-]*:',t,re.I) or t.startswith(('#','//','/')): return m.group(0)
            path,sep,frag=t.partition('#')
            if not path: return m.group(0)
            tgt=os.path.normpath(os.path.join(os.path.dirname(f),unquote(path)))
            if tgt.startswith('..'): return m.group(0)
            ntgt=newloc(tgt)
            if ntgt==tgt and fnew==f: return m.group(0)
            if not os.path.exists(tgt) and tgt not in M: return m.group(0)   # already broken: leave it
            rel=os.path.relpath(ntgt,os.path.dirname(fnew) or '.')
            if rel==path: return m.group(0)
            nlinks+=1
            return pre+rel+sep+frag+post
        text=LINK.sub(fix,text)
    def ment(m):
        global nment
        p='docs/'+m.group(1)+'.md'
        if p in M: nment+=1; return M[p]
        return m.group(0)
    text=re.sub(r'(?<![\w-])docs/([\w.-]+)\.md\b',ment,text)
    if text!=orig:
        open(f,'w',encoding='utf-8',errors='surrogateescape').write(text); changed[f]=1
print(f'links rewritten: {nlinks}; docs/X.md path mentions rewritten: {nment}; files edited: {len(changed)}')
open(sys.argv[1],'w').write('\n'.join(sorted(changed))+'\n')
# --- the move
for d in ('vocabulary','decisions','rounds','reports'): os.makedirs('docs/'+d,exist_ok=True)
for a,b in sorted(M.items()):
    if a=='docs/CHANGELOG-ARCHIVE.md': os.rename(a,b); continue
    subprocess.run(['git','mv',a,b],check=True)
subprocess.run(['git','add','docs/rounds/CHANGELOG-ARCHIVE.md'],check=True)
open(sys.argv[2],'w').write(''.join(f'{a}\t{b}\n' for a,b in sorted(M.items())))
from collections import Counter; print(Counter(b.split('/')[1] for b in M.values()))
