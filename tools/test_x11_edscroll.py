import os, socket, struct, subprocess, time

# Slice 13 proof: the editor pane scrolls to follow the caret. Type 30 lines;
# the pane must show the LAST 23 (caret at the bottom). Then walk the caret up
# and the pane must show the first lines. No display needed.
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
SAVED = "/tmp/.sutram_gui_saved.sm"
ROOT_WIN = 0x00000400; RID_BASE = 0x00200000; RID_MASK = 0x001FFFFF
ED_VISIBLE = 23

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

# keycodes on the mock keymap
L = 46                       # 'l'
RETURN = 36; UP = 111
DIG = {str(d): (19 if d == 0 else 9 + d) for d in range(10)}   # 0->19, 1->10 ... 9->18

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

def key(kc, ctrl=False):
    ev = bytearray(32); ev[0] = 2; ev[1] = kc
    struct.pack_into("<I", ev, 4, RID_BASE | 1); struct.pack_into("<H", ev, 10, 1)
    if ctrl: struct.pack_into("<H", ev, 28, 0x0004)
    conn.sendall(bytes(ev)); time.sleep(0.03)

def texts():
    out = []; old = conn.gettimeout(); conn.settimeout(0.6)
    try:
        while True:
            r = rr()
            if r is None: break
            hh, ll, bb = r
            if hh[0] == 76:
                n = hh[1]; out.append(bb[12:12 + n].decode("latin-1"))
    except Exception: pass
    finally: conn.settimeout(old)
    return out

# type 30 lines: l01 .. l30
for i in range(1, 31):
    key(L)
    for ch in "%02d" % i: key(DIG[ch])
    if i < 30: key(RETURN)

time.sleep(1.0)
# caret is at line 30; the pane should show the last 23 lines: l08 .. l30
allt = [t for t in texts() if len(t) == 3 and t.startswith("l") and t[1:].isdigit()]
first = allt[-ED_VISIBLE:]          # last repaint = the current frame
print("after typing 30 lines, final frame:", first[:1], "...", first[-1:], "(%d lines)" % len(first))
ok_bottom = first == ["l%02d" % i for i in range(8, 31)]
print("AUTO-FOLLOW TO BOTTOM (l08..l30):", ok_bottom)

# walk the caret to the top
for _ in range(29): key(UP)
time.sleep(0.8)
allt2 = [t for t in texts() if len(t) == 3 and t.startswith("l") and t[1:].isdigit()]
top = allt2[-ED_VISIBLE:]
print("after 29 Ups, final frame:", top[:1], "...", top[-1:], "(%d lines)" % len(top))
ok_top = top == ["l%02d" % i for i in range(1, 24)]
print("SCROLLED BACK TO TOP (l01..l23):", ok_top)

# buffer intact via Ctrl-S
key(39, ctrl=True); time.sleep(0.4)
try: buf = open(SAVED, "rb").read().decode("latin-1")
except FileNotFoundError: buf = "<none>"
lines = buf.split("\n")
ok_buf = len([x for x in lines if x]) == 30 and lines[0] == "l01" and lines[29] == "l30"
print("BUFFER INTACT (30 lines, l01..l30):", ok_buf)
print("RESULT:", all([ok_bottom, ok_top, ok_buf]))

conn.close(); srv.close(); proc.terminate()
try: proc.communicate(timeout=5)
except Exception: proc.kill()
