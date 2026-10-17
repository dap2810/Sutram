import os, socket, struct, subprocess, sys, time, tempfile

# Slice 32 proof: the editor draws line numbers in a gutter.
#  1. open a file with several lines
#  2. send an Expose so draw_all repaints
#  3. require the painted ImageText8 stream tak contain the gutter numbers
#     "1","2","3",... at the gutter x, and the text tak have shifted right
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
ROOT_WIN = 0x00000400; RID_BASE = 0x00200000; RID_MASK = 0x001FFFFF
PANE_X = 10; ED_GUTTER = 34
GUTTER_X = PANE_X + 8              # where the numbers are drawn
LINES = 5


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


src = tempfile.NamedTemporaryFile("w", suffix=".sm", delete=False)
for i in range(LINES):
    src.write(f"likha({i})\n")
src.close()

os.makedirs(SOCKDIR, exist_ok=True)
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)
srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); srv.bind(SOCKPATH); srv.listen(1)
proc = subprocess.Popen([os.environ.get("SUTRAM_GUI", "/scratch/work/sutram-gui"), src.name],
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


def drain(t=1.5):
    conn.settimeout(t); buf = b""
    try:
        while True:
            c = conn.recv(65536)
            if not c: break
            buf += c
    except socket.timeout: pass
    return buf


exp = bytearray(32); exp[0] = 12
struct.pack_into("<I", exp, 4, RID_BASE | 1)
struct.pack_into("<H", exp, 12, 900); struct.pack_into("<H", exp, 14, 700)
conn.sendall(bytes(exp))
buf = drain(1.5)

# ImageText8: opcode 76, n at +1, x at +12, string at +16
draws = []
i = 0
while i + 4 <= len(buf):
    op = buf[i]; ln = struct.unpack_from("<H", buf, i + 2)[0]
    if ln == 0 or ln > 4096 or i + 4 * ln > len(buf): break
    if op == 76 and ln >= 4:
        n = buf[i + 1]
        x = struct.unpack_from("<h", buf, i + 12)[0]
        draws.append((x, buf[i + 16:i + 16 + n].decode("latin-1")))
    i += 4 * ln

proc.terminate()
try: proc.wait(timeout=4)
except Exception: proc.kill()
conn.close(); srv.close()
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)
os.unlink(src.name)

gutter = [t for x, t in draws if x == GUTTER_X]
want = [str(i) for i in range(1, LINES + 1)]
missing = [w for w in want if w not in gutter]

if not missing:
    print(f"  PASS  gutter numbers painted: {gutter}")
    print(f"        all of {want} present at x={GUTTER_X}")
    sys.exit(0)
print(f"  FAIL  missing {missing} from the gutter")
print(f"        gutter draws: {gutter}")
print(f"        all draws   : {[t for _, t in draws][:14]}")
sys.exit(1)
