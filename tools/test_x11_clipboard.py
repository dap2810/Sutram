import os, socket, struct, subprocess, time

# Slice 16 proof: selection + internal clipboard.
# The editor buffer is read back through the real Ctrl-S save path, so these
# checks prove the whole copy/cut/paste pipeline, not just the protocol bytes.
# A second set of checks looks for the selection-highlight colour in the
# requests the client sends (ChangeGC with foreground 0x2B4A6B).
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
SAVED = "/tmp/.sutram_gui_saved.sm"
ROOT_WIN = 0x00000400; RID_BASE = 0x00200000; RID_MASK = 0x001FFFFF
COL_SEL = 0x2B4A6B

def build_setup():
    vendor = b"Sutram-Mock"; vpad = (-len(vendor)) % 4
    hdr = bytearray(40); hdr[0] = 1
    struct.pack_into("<H", hdr, 2, 11); struct.pack_into("<H", hdr, 4, 0); struct.pack_into("<H", hdr, 6, 1)
    struct.pack_into("<I", hdr, 12, RID_BASE); struct.pack_into("<I", hdr, 16, RID_MASK)
    struct.pack_into("<H", hdr, 20, len(vendor)); hdr[29] = 1
    scr = bytearray(40); struct.pack_into("<I", scr, 0, ROOT_WIN)
    struct.pack_into("<H", scr, 28, 1); struct.pack_into("<H", scr, 30, 1)
    struct.pack_into("<I", scr, 32, ROOT_WIN); scr[38] = 24
    body = vendor + b"\0" * vpad + bytearray(8) + bytes(scr)
    total = 40 + len(body); struct.pack_into("<H", hdr, 6, total // 4)
    return bytes(hdr) + body

def kc_reply(first, count):
    per = 2; syms = bytearray(); tbl = {}
    for i, ch in enumerate("1234567890"): tbl[10 + i] = ch
    for i, ch in enumerate("qwertyuiop"): tbl[24 + i] = ch
    for i, ch in enumerate("asdfghjkl"): tbl[38 + i] = ch
    for i, ch in enumerate("zxcvbnm"): tbl[52 + i] = ch
    tbl.update({20: "-", 21: "=", 34: "[", 35: "]", 47: ";", 48: "'", 49: "`", 59: ",", 60: ".", 61: "/", 65: " "})
    for i in range(count):
        ch = tbl.get(first + i, 0)
        syms += struct.pack("<I", ord(ch) if isinstance(ch, str) else ch); syms += struct.pack("<I", 0)
    n = len(syms) // 4; hdr = bytearray(32); hdr[0] = 1; hdr[1] = per
    struct.pack_into("<I", hdr, 4, n); return bytes(hdr) + bytes(syms)

if os.path.exists(SAVED): os.unlink(SAVED)
os.makedirs(SOCKDIR, exist_ok=True)
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)
srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); srv.bind(SOCKPATH); srv.listen(1)
proc = subprocess.Popen([os.environ.get("SUTRAM_GUI", "/scratch/work/sutram-gui")],
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
conn, _ = srv.accept(); conn.settimeout(8)

def rx(n):
    b = b""
    while len(b) < n:
        c = conn.recv(n - len(b))
        if not c: break
        b += c
    return b

rx(12); conn.sendall(build_setup())
def rr():
    h = rx(4)
    if len(h) < 4: return None
    ln = struct.unpack_from("<H", h, 2)[0]
    return h, ln, rx(4 * ln - 4)
for _ in range(3): rr()
h, ln, body = rr(); conn.sendall(kc_reply(body[0], body[1]))

def drain(secs=0.4):
    conn.settimeout(0.15); buf = b""; t = time.time()
    while time.time() - t < secs:
        try:
            c = conn.recv(65536)
            if not c: break
            buf += c
        except socket.timeout:
            break
    conn.settimeout(8)
    return buf

KM = {'a':38,'b':56,'c':54,'d':40,'e':26,'f':41,'g':42,'h':43,'i':31,'j':44,'k':45,
      'l':46,'m':58,'n':57,'o':32,'p':33,'q':24,'r':27,'s':39,'t':28,'u':30,'v':55,
      'w':25,'x':53,'y':29,'z':52,' ':65}
RETURN, BACKSPACE, ESC, HOME, END = 36, 22, 9, 102, 107
CTRL_A, CTRL_C, CTRL_X, CTRL_V, CTRL_S = 38, 54, 53, 55, 39

def key(kc, ctrl=False, shift=False):
    ev = bytearray(32); ev[0] = 2; ev[1] = kc
    struct.pack_into("<I", ev, 4, RID_BASE | 1); struct.pack_into("<H", ev, 10, 1)
    st = 0
    if ctrl: st |= 0x0004
    if shift: st |= 0x0001
    struct.pack_into("<H", ev, 28, st)
    conn.sendall(bytes(ev)); time.sleep(0.05)

def typ(s):
    for ch in s: key(KM[ch])

def saved():
    key(CTRL_S, ctrl=True); time.sleep(0.35)
    try: return open(SAVED, "rb").read().decode("latin-1")
    except FileNotFoundError: return "<none>"

def reset():
    key(CTRL_A, ctrl=True); key(BACKSPACE); time.sleep(0.1)

results = []

# ---- 0) highlight colour present only when a selection exists -------------
key(KM['a']); key(KM['b'])                      # type "ab", no selection
no_sel_reqs = drain()
hl_absent = struct.pack("<I", COL_SEL) not in no_sel_reqs
print("highlight colour absent with no selection:", hl_absent)
results.append(hl_absent)

key(CTRL_A, ctrl=True)                          # select all
sel_reqs = drain()
hl_present = struct.pack("<I", COL_SEL) in sel_reqs
print("highlight colour present with a selection:", hl_present)
results.append(hl_present)

# ---- 1) copy all, paste below ---------------------------------------------
reset(); typ("hello world")
key(CTRL_A, ctrl=True); key(CTRL_C, ctrl=True)  # copy the whole buffer
key(END, ctrl=True); key(RETURN); key(CTRL_V, ctrl=True)
g1 = saved()
ok1 = g1 == "hello world\nhello world"
print("1 copy-all+paste:", repr(g1), ok1); results.append(ok1)

# ---- 2) cut a whole line with no selection, paste at the end --------------
reset(); typ("abc"); key(RETURN); typ("def")
key(HOME, ctrl=True); key(CTRL_X, ctrl=True)    # cut line 0 incl. newline
key(END, ctrl=True); key(CTRL_V, ctrl=True)
g2 = saved()
ok2 = g2 == "defabc\n"
print("2 cut-line+paste:", repr(g2), ok2); results.append(ok2)

# ---- 3) shift-selection, copy the selected run ----------------------------
reset(); typ("abcdef")
key(HOME, ctrl=True)
key(114, shift=True)                            # 114 = Right
key(114, shift=True); key(114, shift=True)      # select "abc"
key(CTRL_C, ctrl=True)
key(END, ctrl=True); key(RETURN); key(CTRL_V, ctrl=True)
g3 = saved()
ok3 = g3 == "abcdef\nabc"
print("3 shift-select copy:", repr(g3), ok3); results.append(ok3)

# ---- 4) Escape clears a selection instead of quitting ---------------------
reset(); typ("xy")
key(CTRL_A, ctrl=True); key(ESC); time.sleep(0.1)
alive = proc.poll() is None
key(KM['z'])                                    # selection gone -> 'z' appends
g4 = saved()
ok4 = alive and g4 == "xyz"
print("4 escape-clears-selection:", repr(g4), "alive=", alive, ok4); results.append(ok4)

# ---- 5) backspace deletes the selection -----------------------------------
reset(); typ("hello")
key(CTRL_A, ctrl=True); key(BACKSPACE)
g5 = saved()
ok5 = g5 == ""
print("5 backspace-deletes-selection:", repr(g5), ok5); results.append(ok5)

# ---- 6) typing over a selection replaces it -------------------------------
reset(); typ("oldtext")
key(CTRL_A, ctrl=True); typ("new")
g6 = saved()
ok6 = g6 == "new"
print("6 type-replaces-selection:", repr(g6), ok6); results.append(ok6)

print("RESULT:", all(results))

conn.close(); srv.close(); proc.terminate()
try: proc.communicate(timeout=5)
except Exception: proc.kill()
