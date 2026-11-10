import subprocess,sys,os
C='./sc'
def run(name,src,stdin=''):
    open(name+'.sm','w',encoding='utf-8').write(src)
    if os.path.exists(name+'.bin'): os.remove(name+'.bin')
    c=subprocess.run([C,name+'.sm',name+'.bin'],capture_output=True,text=True,errors='replace')
    if not os.path.exists(name+'.bin'):
        return 'REFUSED: '+(c.stdout+c.stderr).strip().split('\n')[0][:110]
    try:
        r=subprocess.run(['./'+name+'.bin'],capture_output=True,text=True,errors='replace',input=stdin,timeout=10)
        return ('exit %d: '%r.returncode if r.returncode else '')+(r.stdout+r.stderr).strip().replace('\n',' | ')[:160]
    except subprocess.TimeoutExpired: return 'TIMEOUT'
def M(body): return 'mukhya() {\n'+''.join('    '+l+'\n' for l in body.split(';') if l.strip())+'}\n'
P=[l for l in open(sys.argv[1],encoding='utf-8').read().split('\n===\n')]
for blk in P:
    if not blk.strip(): continue
    head,_,src=blk.partition('\n')
    name,_,expect=head.partition(' :: ')
    if src.startswith('M:'): src=M(src[2:])
    got=run(name.strip(),src,stdin='hello\n' if 'grahan' in name else '')
    print(f'{name.strip():18} expect [{expect.strip()}]  got [{got}]')
