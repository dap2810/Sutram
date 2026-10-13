import os, socket, struct, subprocess, time

# Slice 17 proof: Ctrl-O opens a file by path, Ctrl-N starts a new buffer, and
# the prompt is actually visible (not overpainted by the editor repaint).
# The buffer is read back through the real Ctrl-S save path.
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
SAVED = "/tmp/.sutram_gui_saved.sm"
SRC = "/tmp/sutramopen.sm"
ROOT_WIN = 0x00000400; RID_BASE = 0x00200000; RID_MASK = 0x001FFFFF
PROMPT_Y = 44 + 400 - 12          # ED_Y + ED_H - 12

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

CONTENT = "alpha\nbeta\ngamma\n"
open(SRC, "w").write(CONTENT)
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

def drain(secs=0.5):
    """Return the ordered list of (opcode, full_request_bytes)."""
    reqs = []; old = conn.gettimeout(); conn.settimeout(0.15); t = time.time()
    while time.time() - t < secs:
        try:
            r = rr()
        except socket.timeout:
            break
        if r is None: break
        hh, ll, bb = r
        reqs.append((hh[0], hh + bb))
    conn.settimeout(old)
    return reqs

def texts(reqs):
    out = []
    for op, raw in reqs:
        if op == 76:                       # ImageText8
            n = raw[1]; out.append(raw[16:16 + n].decode("latin-1"))
    return out

KM = {'a':38,'b':56,'c':54,'d':40,'e':26,'f':41,'g':42,'h':43,'i':31,'j':44,'k':45,
      'l':46,'m':58,'n':57,'o':32,'p':33,'q':24,'r':27,'s':39,'t':28,'u':30,'v':55,
      'w':25,'x':53,'y':29,'z':52,' ':65,'.':60,'/':61}
RETURN, ESC, BACKSPACE = 36, 9, 22
CTRL_O, CTRL_N, CTRL_S = 32, 57, 39

def key(kc, ctrl=False):
    ev = bytearray(32); ev[0] = 2; ev[1] = kc
    struct.pack_into("<I", ev, 4, RID_BASE | 1); struct.pack_into("<H", ev, 10, 1)
    if ctrl: struct.pack_into("<H", ev, 28, 0x0004)
    conn.sendall(bytes(ev)); time.sleep(0.05)

def typ(s):
    for ch in s: key(KM[ch])

def saved():
    key(CTRL_S, ctrl=True); time.sleep(0.35)
    try: return open(SAVED, "rb").read().decode("latin-1")
    except FileNotFoundError: return "<none>"

results = []

# ---- 1) Ctrl-O <path> Enter loads the file -------------------------------
key(CTRL_O, ctrl=True); time.sleep(0.1)
typ(SRC)
key(RETURN); time.sleep(0.2)
g1 = saved()
ok1 = g1 == CONTENT
print("1 open-by-path:", repr(g1), ok1); results.append(ok1)

# ---- 2) the prompt is drawn AND not overpainted --------------------------
key(CTRL_O, ctrl=True); time.sleep(0.1)
typ("/tmp")
reqs = drain()
tl = texts(reqs)
prompt_seen = any(t.startswith("Open:") for t in tl)
# find the index of the Open: text in request order
idx = None
for i, (op, raw) in enumerate(reqs):
    if op == 76 and raw[16:16 + 5] == b"Open:":
        idx = i
overpaint = False
if idx is not None:
    for op, raw in reqs[idx + 1:]:
        if op == 70:                       # PolyFillRect
            y = struct.unpack_from("<h", raw, 14)[0]
            hgt = struct.unpack_from("<H", raw, 18)[0]
            if y <= PROMPT_Y <= y + hgt:
                overpaint = True
ok2 = prompt_seen and (idx is not None) and (not overpaint)
print("2 prompt drawn=%s idx=%s overpainted=%s" % (prompt_seen, idx, overpaint), ok2); results.append(ok2)
key(ESC); time.sleep(0.1)

# ---- 3) Ctrl-N clears the buffer ----------------------------------------
key(CTRL_N, ctrl=True); time.sleep(0.1)
g3 = saved()
ok3 = g3 == ""
print("3 ctrl-N new buffer:", repr(g3), ok3); results.append(ok3)

# ---- 4) a bad path leaves the buffer untouched and reports it ------------
typ("keep me")
key(CTRL_O, ctrl=True); time.sleep(0.1)
typ("/tmp/nosuchfile.sm")
key(RETURN); time.sleep(0.2)
errs = texts(drain())
g4 = saved()
ok4 = g4 == "keep me" and any("cannot open" in t for t in errs)
print("4 bad path:", repr(g4), "error-shown=", any("cannot open" in t for t in errs), ok4); results.append(ok4)

# ---- 5) Esc cancels the open prompt without loading ----------------------
key(CTRL_O, ctrl=True); time.sleep(0.1)
typ("/tmp/nosuchfile.sm")
key(ESC); time.sleep(0.1)
key(KM['z'])
g5 = saved()
ok5 = g5 == "keep mez"
print("5 esc-cancels-open:", repr(g5), ok5); results.append(ok5)

print("RESULT:", all(results))

conn.close(); srv.close(); proc.terminate()
try: proc.communicate(timeout=5)
except Exception: proc.kill()
