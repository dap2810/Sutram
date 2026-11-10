"""Static byte-routing audit of v315 lexer; no compiler or project test execution.
Run from a git checkout: python3 scan.py REF OUTPUT_JSON
Reports raw-source candidates, not preprocessing or parsing results.
"""
import ast, collections, json, re, subprocess, sys
REF, OUT = sys.argv[1:]
def alpha(c): return 65 <= c <= 90 or 97 <= c <= 122 or c in (95, 224)
def digit(b, i):
    if i >= len(b): return 0
    if 48 <= b[i] <= 57: return 1
    if i + 2 < len(b) and b[i] == 224 and b[i+1] in (165,171,167,169,173,175,177,179) and 166 <= b[i+2] <= 175: return 3
    return 0
def danda(b,i): return b[i:i+3] in (b'\xe0\xa5\xa4', b'\xe0\xa5\xa5')
def scan(b):
    i, hits, invalid = 0, [], []
    while i < len(b):
        c=b[i]
        if c in (9,10,13,32): i+=1; continue
        if b[i:i+2] == b'//' or c == 35:
            j=b.find(b'\n',i); i=len(b) if j<0 else j; continue
        if b[i:i+2] == b'/*':
            j=b.find(b'*/',i+2); i=len(b) if j<0 else j+2; continue
        if danda(b,i): i+=3; continue
        w=digit(b,i)
        if not w and alpha(c):
            while i<len(b) and not danda(b,i) and (alpha(b[i]) or 48<=b[i]<=57):
                if b[i]==224:
                    if i+2>=len(b) or not 160<=b[i+1]<=191 or not 128<=b[i+2]<=191:
                        invalid.append(i); return hits,invalid
                    i+=3
                else: i+=1
            continue
        if w:
            if b[i:i+2] in (b'0x',b'0X'):
                i+=2
                while i<len(b) and b[i] in b'0123456789abcdefABCDEF': i+=1
            else:
                while digit(b,i): i+=digit(b,i)
                if b[i:i+1]==b'.' and digit(b,i+1):
                    i+=1
                    while digit(b,i): i+=digit(b,i)
            continue
        if c==34:
            i+=1
            while i<len(b) and b[i]!=34:
                i+=2 if b[i]==92 else 1
            i+=1; continue
        if c in b'(){};,[],:?.=!:<>+-*/%&|^':
            if b[i:i+2] in (b'==',b'!=',b'<=',b'>=',b'<<',b'>>',b'++',b'--',b'+=',b'-=',b'*=',b'/=',b'%=',b'&&',b'||'): i+=2
            else: i+=1
            continue
        hits.append(i); i+=1
    return hits,invalid
raw=subprocess.check_output(['git','ls-tree','-r','-z',REF])
files=[]
for ent in raw.split(b'\0'):
    if not ent: continue
    meta,path=ent.split(b'\t',1); mode,typ,sha=meta.split()
    p=path.decode()
    if p.endswith(('.sm','.smlib')) or p.startswith('tests/') and p.endswith(('.py','.sh')): files.append((p,sha.decode()))
p=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
allrows=[]; literals=[]; counts=collections.Counter(); errors=[]; blobs={}
for path,sha in files:
    p.stdin.write((sha+'\n').encode());p.stdin.flush()
    hdr=p.stdout.readline().split(); n=int(hdr[2]);b=p.stdout.read(n);p.stdout.read(1);blobs[path]=b
    if path.endswith(('.sm','.smlib')):
        hits,invalid=scan(b); counts['sutram_files']+=1
        counts[path.split('/')[0]]+=1
        if invalid: errors.append({'path':path,'offsets':invalid})
        if hits:
            rows=[]
            for i in hits:
                line=b.count(b'\n',0,i)+1;start=b.rfind(b'\n',0,i)+1
                end=b.find(b'\n',i); end=len(b) if end<0 else end
                import_line=bool(re.match(rb'\s*(?:yoj|ayojan)\s',b[start:end]))
                rows.append({'offset':i,'line':line,'byte_column':i-start+1,'byte':f'{b[i]:02X}','import_line':import_line})
            allrows.append({'path':path,'hits':rows})
    elif path.endswith('.py'):
        counts['python_files']+=1
        try: tree=ast.parse(b)
        except (SyntaxError,UnicodeError): errors.append({'path':path,'python_parse':'failed'});continue
        for node in ast.walk(tree):
            if isinstance(node,ast.Constant) and isinstance(node.value,(str,bytes)):
                v=node.value.encode() if isinstance(node.value,str) else node.value
                if not re.search(rb'\b(?:mukhya|prakriya|mandapa|vitti|kosh)\b',v): continue
                hits,invalid=scan(v)
                if hits: literals.append({'path':path,'host_line':node.lineno,'literal_length':len(v),'bytes':dict(collections.Counter(f'{v[i]:02X}' for i in hits))})
    else: counts['shell_files']+=1
p.stdin.close();p.wait()
report={'base':REF,'method':'static lexer byte routing; no preprocessing or compiler execution','counts':dict(counts),'raw_source_candidates':allrows,'invalid':errors,'python_literal_candidates':literals}
json.dump(report,open(OUT,'w'),indent=2,ensure_ascii=False)
print(json.dumps({'counts':dict(counts),'raw_hit_files':len(allrows),'raw_hit_bytes':sum(len(r['hits']) for r in allrows),'invalid_files':len(errors),'python_candidates':len(literals)},indent=2))
for r in allrows:
    print(r['path'],dict(collections.Counter(h['byte'] for h in r['hits'])),'lines',sorted(set(h['line'] for h in r['hits'])),'imports',sum(h['import_line'] for h in r['hits']))
