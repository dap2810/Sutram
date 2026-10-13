import os, socket, struct, subprocess, time, shutil

# Slice 18 proof: Ctrl-B lists the current directory; Enter opens a file or
# descends into a directory; Esc cancels. Buffer read back via Ctrl-S.
SOCKDIR="/tmp/.X11-unix"; SOCKPATH=os.path.join(SOCKDIR,"X0")
SAVED="/tmp/.sutram_gui_saved.sm"
ROOT_WIN=0x00000400; RID_BASE=0x00200000; RID_MASK=0x001FFFFF

def build_setup():
    v=b"Sutram-Mock"; vp=(-len(v))%4
    h=bytearray(40); h[0]=1
    struct.pack_into("<H",h,2,11); struct.pack_into("<H",h,4,0); struct.pack_into("<H",h,6,1)
    struct.pack_into("<I",h,12,RID_BASE); struct.pack_into("<I",h,16,RID_MASK)
    struct.pack_into("<H",h,20,len(v)); h[29]=1
    s=bytearray(40); struct.pack_into("<I",s,0,ROOT_WIN)
    struct.pack_into("<H",s,28,1); struct.pack_into("<H",s,30,1)
    struct.pack_into("<I",s,32,ROOT_WIN); s[38]=24
    b=v+b"\0"*vp+bytearray(8)+bytes(s); struct.pack_into("<H",h,6,(40+len(b))//4)
    return bytes(h)+b

def kc_reply(first,count):
    sy=bytearray(); t={}
    for i,ch in enumerate("1234567890"): t[10+i]=ch
    for i,ch in enumerate("qwertyuiop"): t[24+i]=ch
    for i,ch in enumerate("asdfghjkl"): t[38+i]=ch
    for i,ch in enumerate("zxcvbnm"): t[52+i]=ch
    for i in range(count):
        ch=t.get(first+i,0); sy+=struct.pack("<I",ord(ch) if isinstance(ch,str) else ch); sy+=struct.pack("<I",0)
    n=len(sy)//4; h=bytearray(32); h[0]=1; h[1]=2; struct.pack_into("<I",h,4,n); return bytes(h)+bytes(sy)

# ---- fixtures ----
shutil.rmtree("/tmp/brtest", ignore_errors=True)
shutil.rmtree("/tmp/brdeep", ignore_errors=True)
os.makedirs("/tmp/brtest"); open("/tmp/brtest/solo.sm","w").write("solo content\n")
os.makedirs("/tmp/brdeep/sub"); open("/tmp/brdeep/sub/deep.sm","w").write("deep\n")
if os.path.exists(SAVED): os.unlink(SAVED)
os.makedirs(SOCKDIR, exist_ok=True)

def run_case(cwd, script):
    """Spawn the GUI with a given cwd, run `script(conn, key, drain, texts)`, return it."""
    if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)
    srv=socket.socket(socket.AF_UNIX,socket.SOCK_STREAM); srv.bind(SOCKPATH); srv.listen(1)
    proc=subprocess.Popen([os.environ.get("SUTRAM_GUI","/scratch/work/Sutram/sutram-gui")],
                          stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,cwd=cwd)
    conn,_=srv.accept(); conn.settimeout(8)
    def rx(n):
        b=b""
        while len(b)<n:
            c=conn.recv(n-len(b))
            if not c: break
            b+=c
        return b
    rx(12); conn.sendall(build_setup())
    def rr():
        h=rx(4)
        if len(h)<4: return None
        l=struct.unpack_from("<H",h,2)[0]; return h,l,rx(4*l-4)
    for _ in range(3): rr()
    h,l,b=rr(); conn.sendall(kc_reply(b[0],b[1]))
    def key(kc,ctrl=False):
        ev=bytearray(32); ev[0]=2; ev[1]=kc
        struct.pack_into("<I",ev,4,RID_BASE|1); struct.pack_into("<H",ev,10,1)
        if ctrl: struct.pack_into("<H",ev,28,0x0004)
        conn.sendall(bytes(ev)); time.sleep(0.05)
    def drain(secs=0.5):
        reqs=[]; old=conn.gettimeout(); conn.settimeout(0.15); t=time.time()
        while time.time()-t<secs:
            try: r=rr()
            except socket.timeout: break
            if r is None: break
            reqs.append((r[0][0], r[0]+r[2]))
        conn.settimeout(old); return reqs
    def texts(reqs):
        out=[]
        for op,raw in reqs:
            if op==76:
                n=raw[1]; out.append(raw[16:16+n].decode("latin-1"))
        return out
    try: return script(conn,key,drain,texts)
    finally:
        conn.close(); srv.close(); proc.terminate()
        try: proc.communicate(timeout=5)
        except Exception: proc.kill()

def saved(key):
    key(39, ctrl=True); time.sleep(0.35)
    try: return open(SAVED,"rb").read().decode("latin-1")
    except FileNotFoundError: return "<none>"

CTRL_B=56; ESC=9; RETURN=36; BACKSPACE=22; DOWN=116; UP=111
results=[]

# ---- 1) list + open a file -------------------------------------------------
def case1(conn,key,drain,texts):
    key(CTRL_B, ctrl=True); time.sleep(0.15)
    listed = any("solo.sm" in t for t in texts(drain()))
    key(RETURN); time.sleep(0.2)          # selection 0 is the only entry
    g = saved(key)
    return listed, g

listed, g1 = run_case("/tmp/brtest", case1)
print("1 listed solo.sm:", listed)
print("1 opened content :", repr(g1))
ok1 = listed and g1 == "solo content\n"
results.append(ok1)

# ---- 2) descend into a directory ------------------------------------------
def case2(conn,key,drain,texts):
    key(CTRL_B, ctrl=True); time.sleep(0.15)
    top = texts(drain())
    key(RETURN); time.sleep(0.25)         # selection 0 is the only entry: the dir
    inner = texts(drain())
    return top, inner

top, inner = run_case("/tmp/brdeep", case2)
print("2 top level shows sub/:", any("sub" in t for t in top))
print("2 after Enter shows deep.sm:", any("deep.sm" in t for t in inner))
ok2 = any("sub" in t for t in top) and any("deep.sm" in t for t in inner)
results.append(ok2)

# ---- 3) Esc cancels without opening ---------------------------------------
def case3(conn,key,drain,texts):
    key(CTRL_B, ctrl=True); time.sleep(0.15)
    key(ESC); time.sleep(0.15)
    key(52)                                # 'z' -> goes into the editor buffer
    return saved(key)

g3 = run_case("/tmp/brtest", case3)
print("3 esc-cancels:", repr(g3))
ok3 = g3 == "z"
results.append(ok3)

print("RESULT:", all(results))
