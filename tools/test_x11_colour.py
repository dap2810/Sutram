import os, socket, struct, subprocess, sys, time

# Slice 19 proof: the editor emits PER-TOKEN foreground colours.
# Type `likha 'a' 12` (keyword, string, number) and read the protocol back.
# The draw stream must contain several distinct GCForeground values.
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
ROOT_WIN = 0x00000400; RID_BASE = 0x00200000; RID_MASK = 0x001FFFFF

COL_KW, COL_BI, COL_STR, COL_NUM, COL_CMT = 0xE86D11, 0x4EC9B0, 0x6A9955, 0xB586E8, 0x6A6A6A

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
    tbl.update({20: "-", 21: "=", 34: "[", 35: "]", 47: ";", 48: "'", 49: "`",
                59: ",", 60: ".", 61: "/", 65: " "})
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

def drain():
    """read everything currently pending"""
    conn.settimeout(0.4); buf = b""
    try:
        while True:
            c = conn.recv(65536)
            if not c: break
            buf += c
    except socket.timeout:
        pass
    return buf

def parse_colours(buf):
    """walk the request stream, collect GCForeground values from ChangeGC (56)"""
    cols = []; i = 0
    while i + 4 <= len(buf):
        op = buf[i]
        if op not in (0, 1, 8, 55, 56, 60, 61, 62, 63, 64, 65, 70, 72, 74, 76, 77, 78, 88):
            break
        ln = struct.unpack_from("<H", buf, i + 2)[0]
        if ln == 0 or ln > 4096: break
        end = i + 4 * ln
        if end > len(buf): break
        if op == 56 and ln >= 4:
            mask = struct.unpack_from("<I", buf, i + 8)[0]
            if mask & 0x0004 and ln >= 4:
                cols.append(struct.unpack_from("<I", buf, i + 12)[0])
        i = end
    return cols

# keycodes: l=46 i=31 k=45 h=43 a=38  1=10 2=11  ' =48
def tap(kc, ctrl=False):
    ev = bytearray(32); ev[0] = 2; ev[1] = kc
    struct.pack_into("<I", ev, 4, RID_BASE | 1); struct.pack_into("<H", ev, 10, 1)
    if ctrl: struct.pack_into("<H", ev, 28, 0x0004)
    conn.sendall(bytes(ev)); time.sleep(0.06)

drain()
for kc in [46, 31, 45, 43, 38]:            # l i k h a  -> keyword
    tap(kc)
tap(65)                                     # space
tap(48); tap(38); tap(48)                   # 'a'  -> string
tap(65)                                     # space
tap(10); tap(11)                            # 12   -> number

buf = drain()
cols = parse_colours(buf)
uniq = sorted(set(cols))
print("distinct foreground colours seen:", [hex(c) for c in uniq])

proc.terminate()
try: proc.wait(timeout=5)
except Exception: proc.kill()
conn.close(); srv.close()
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)

want = {("keyword", COL_KW), ("string", COL_STR), ("number", COL_NUM), ("default", 0xDFE7EE)}
missing = [n for n, c in want if c not in uniq]
if missing:
    print("FAIL: missing colours for:", missing); sys.exit(1)
print("PASS: keyword/string/number/default colours all present")
sys.exit(0)
