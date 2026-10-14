import os, socket, struct, subprocess, sys, time

# Slice 20 proof: the menu bar is clickable.
#  1. click the "File" label  -> a dropdown background must be drawn
#  2. click the "Exit" item   -> the process must quit
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
ROOT_WIN = 0x00000400; RID_BASE = 0x00200000; RID_MASK = 0x001FFFFF
COL_DROPBG = 0x1B2733; COL_MENUSEL = 0x1A4A5C

def build_setup():
    vendor = b"Sutram-Mock"; vpad = (-len(vendor)) % 4
    hdr = bytearray(40); hdr[0] = 1
    struct.pack_into("<H", hdr, 2, 11); struct.pack_into("<H", hdr, 4, 0)
    struct.pack_into("<I", hdr, 12, RID_BASE); struct.pack_into("<I", hdr, 16, RID_MASK)
    struct.pack_into("<H", hdr, 20, len(vendor)); hdr[29] = 1
    scr = bytearray(40); struct.pack_into("<I", scr, 0, ROOT_WIN)
    struct.pack_into("<H", scr, 28, 1); struct.pack_into("<H", scr, 30, 1)
    struct.pack_into("<I", scr, 32, ROOT_WIN); scr[38] = 24
    body = vendor + b"\0" * vpad + bytearray(8) + bytes(scr)
    total = 40 + len(body); struct.pack_into("<H", hdr, 6, total // 4)
    return bytes(hdr) + body

def kc_reply(first, count):
    syms = bytearray(); tbl = {}
    for i, ch in enumerate("1234567890"): tbl[10 + i] = ch
    for i, ch in enumerate("qwertyuiop"): tbl[24 + i] = ch
    for i, ch in enumerate("asdfghjkl"): tbl[38 + i] = ch
    for i, ch in enumerate("zxcvbnm"): tbl[52 + i] = ch
    for i in range(count):
        ch = tbl.get(first + i, 0)
        syms += struct.pack("<I", ord(ch) if isinstance(ch, str) else ch); syms += struct.pack("<I", 0)
    n = len(syms) // 4; hdr = bytearray(32); hdr[0] = 1; hdr[1] = 2
    struct.pack_into("<I", hdr, 4, n); return bytes(hdr) + bytes(syms)

os.makedirs(SOCKDIR, exist_ok=True)
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)
srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); srv.bind(SOCKPATH); srv.listen(1)
proc = subprocess.Popen([os.environ.get("SUTRAM_GUI", "/scratch/work/sutram-gui-menu")],
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

def drain(t=0.5):
    conn.settimeout(t); buf = b""
    try:
        while True:
            c = conn.recv(65536)
            if not c: break
            buf += c
    except socket.timeout: pass
    return buf

def colours(buf):
    cols = []; i = 0
    while i + 4 <= len(buf):
        op = buf[i]; ln = struct.unpack_from("<H", buf, i + 2)[0]
        if ln == 0 or ln > 4096 or i + 4 * ln > len(buf): break
        if op == 56 and ln >= 4 and (struct.unpack_from("<I", buf, i + 8)[0] & 4):
            cols.append(struct.unpack_from("<I", buf, i + 12)[0])
        i += 4 * ln
    return cols

def click(x, y):
    ev = bytearray(32); ev[0] = 4; ev[1] = 1
    struct.pack_into("<I", ev, 4, RID_BASE | 1)
    struct.pack_into("<I", ev, 12, RID_BASE | 1)
    struct.pack_into("<h", ev, 24, x); struct.pack_into("<h", ev, 26, y)
    conn.sendall(bytes(ev)); time.sleep(0.25)

drain()
# "File" label sits at x offset 300..374, y within the 28px strip
click(320, 12)
buf = drain(0.6)
cols = colours(buf)
print("after clicking File -> colours:", [hex(c) for c in sorted(set(cols))])
ok_open = (COL_MENUSEL in cols) or (COL_DROPBG in cols)
print("  dropdown/highlight drawn:", ok_open)

# click the "Exit" item (3rd row): x inside the box, y = MENU_H + 6 + 2*22 + ~8
click(330, 28 + 6 + 2 * 22 + 8)
time.sleep(0.6)
alive = proc.poll() is None
print("  process quit after Exit:", not alive)

conn.close(); srv.close()
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)
if alive: proc.terminate()
try: proc.wait(timeout=4)
except Exception: proc.kill()

if ok_open and not alive:
    print("PASS: menu bar opens a dropdown and Exit quits"); sys.exit(0)
print("FAIL: menu bar interaction incomplete"); sys.exit(1)
