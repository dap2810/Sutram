import os, socket, struct, subprocess, sys, time

# Slice 26 proof: all seven menus open, each with its own items.
# Click each label in the strip and require a PolyFillRect dropdown of
#   x = that menu's x-offset, y = MENU_H, w = 120, h = 8 + 22*item_count
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
ROOT_WIN = 0x00000400; RID_BASE = 0x00200000; RID_MASK = 0x001FFFFF
MENU_H = 28; DROP_W = 120; ROW_H = 22
MENU_X = [300, 370, 450, 510, 570, 650, 740]
MENU_N = [3, 5, 1, 1, 1, 1, 1]          # File..Help item counts
NAMES = ["patra", "sampad", "khol", "dosh", "vikalp", "gavaksh", "sahay"]


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


def drain(t=0.5):
    conn.settimeout(t); buf = b""
    try:
        while True:
            c = conn.recv(65536)
            if not c: break
            buf += c
    except socket.timeout: pass
    return buf


def click(x, y):
    ev = bytearray(32); ev[0] = 4                      # ButtonPress
    struct.pack_into("<I", ev, 4, RID_BASE | 1)
    struct.pack_into("<H", ev, 24, x); struct.pack_into("<H", ev, 26, y)
    conn.sendall(bytes(ev))
    rel = bytearray(32); rel[0] = 5                    # ButtonRelease
    struct.pack_into("<I", rel, 4, RID_BASE | 1)
    struct.pack_into("<H", rel, 24, x); struct.pack_into("<H", rel, 26, y)
    conn.sendall(bytes(rel))
    time.sleep(0.25)


def rects(buf):
    """every PolyFillRect (opcode 70): (x,y,w,h)"""
    out = []; i = 0
    while i + 4 <= len(buf):
        op = buf[i]; ln = struct.unpack_from("<H", buf, i + 2)[0]
        if ln == 0 or ln > 4096 or i + 4 * ln > len(buf): break
        if op == 70 and ln >= 5:
            x, y, w, hgt = struct.unpack_from("<hhHH", buf, i + 12)
            out.append((x, y, w, hgt))
        i += 4 * ln
    return out


drain()
fails = []
for idx, name in enumerate(NAMES):
    click(MENU_X[idx], 5)
    buf = drain(0.6)
    want = (MENU_X[idx], MENU_H, DROP_W, 8 + ROW_H * MENU_N[idx])
    got = [r for r in rects(buf) if r == want]
    if got:
        print(f"  {name:8s} opens  ->  dropdown {want[2]}x{want[3]} at x={want[0]}  OK")
    else:
        near = [r for r in rects(buf) if r[2] == DROP_W]
        print(f"  {name:8s} FAIL   ->  wanted {want}, saw {near}")
        fails.append(name)

proc.terminate()
try: proc.wait(timeout=4)
except Exception: proc.kill()
conn.close(); srv.close()
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)

if fails:
    print("FAIL: menus that did not open correctly:", ", ".join(fails)); sys.exit(1)
print("PASS: all 7 menus open with their own items"); sys.exit(0)
