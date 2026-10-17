import os, socket, struct, subprocess, time

# Slice 14 proof: Tab inserts a 4-space indent; Ctrl-Home / Ctrl-End jump the
# caret tak the start / end of the whole file. Buffer read back via Ctrl-S.
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
SAVED = "/tmp/.sutram_gui_saved.sm"
ROOT_WIN = 0x00000400; RID_BASE = 0x00200000; RID_MASK = 0x001FFFFF

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

def key(kc, ctrl=False):
    ev = bytearray(32); ev[0] = 2; ev[1] = kc
    struct.pack_into("<I", ev, 4, RID_BASE | 1); struct.pack_into("<H", ev, 10, 1)
    if ctrl: struct.pack_into("<H", ev, 28, 0x0004)
    conn.sendall(bytes(ev)); time.sleep(0.04)

A, B = 38, 56          # 'a','b' on the mock keymap
RETURN, TAB = 36, 23
HOME, END = 102, 107
SAVE = 39

def saved():
    key(SAVE, ctrl=True); time.sleep(0.35)
    try: return open(SAVED, "rb").read().decode("latin-1")
    except FileNotFoundError: return "<none>"

# 1) Tab inserts four spaces
key(A); key(TAB); key(B)
got1 = saved()
print("after a,Tab,b:", repr(got1))
ok_tab = got1 == "a    b"
print("TAB INSERTS 4 SPACES:", ok_tab)

# 2) Ctrl-Home -> start of file, then insert 'z'
key(HOME, ctrl=True); key(52)          # 'z'
got2 = saved()
print("after Ctrl-Home,z:", repr(got2))
ok_home = got2 == "za    b"
print("CTRL-HOME -> FILE START:", ok_home)

# 3) Ctrl-End -> end of file, then insert 'y'
key(END, ctrl=True); key(29)           # 'y'
got3 = saved()
print("after Ctrl-End,y:", repr(got3))
ok_end = got3 == "za    by"
print("CTRL-END -> FILE END:", ok_end)

print("RESULT:", all([ok_tab, ok_home, ok_end]))

conn.close(); srv.close(); proc.terminate()
try: proc.communicate(timeout=5)
except Exception: proc.kill()
