import subprocess,os,sys
G=sys.argv[1]; NEW=os.path.abspath('.')
n=d=0
for f in open(G+'/refused.lst').read().split():
    r=[]
    for c,root in ((G+'/old/sutram_compiler',G+'/old'),(G+'/old/sc_new',NEW)):
        src=os.path.join(root,f)
        p=subprocess.run([c,src,G+'/rx'],capture_output=True,cwd=os.path.dirname(src))
        r.append((p.stdout+p.stderr).replace(root.encode(),b'<root>'))
    n+=1
    if r[0]!=r[1]:
        d+=1; print('MSG-DIFF',f); print('  old',r[0][:300]); print('  new',r[1][:300])
print(n,'refused programs,',d,'with a different message')
