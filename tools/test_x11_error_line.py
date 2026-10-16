import os, socket, struct, subprocess, sys, tempfile, shutil, stat

# Slice 33 proof: after a failed compile, the gutter paints the compiler's error
# line number in RED and the other numbers stay dim.
#
# The GUI finds its compiler by reading /proc/self/exe and appending "/sutram_compiler",
# so we run the GUI from a temp dir with a MOCK compiler beside it that prints a
# diagnostic containing "<file>:2:" and exits 1.
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
ROOT_WIN = 0x00000400; RID_BASE = 0x00200000; RID_MASK = 0x001FFFFF
GUTTER_X = 18                      # PANE_X + 8
COL_GUTTER = 0x5A6A7A
COL_ERR = 0xE05C5C
ERR_LINE = 2
LINES = 4


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


gui_src = os.environ.get("SUTRAM_GUI", "/scratch/work/sutram-gui")
work = tempfile.mkdtemp(prefix="sutram-errline-")
shutil.copy(gui_src, os.path.join(work, "sutram-gui"))

# the mock compiler: prints a diagnostic naming line 2, exits 1
mock = os.path.join(work, "sutram_compiler")
with open(mock, "w") as f:
    f.write('#!/bin/sh\n'
            'echo "Sutram Error [E_TEST]: $1:%d: deliberate failure for the test"\n' % ERR_LINE
            + 'exit 1\n')
os.chmod(mock, 0o755)

src = os.path.join(work, "prog.sm")
with open(src, "w") as f:
    for i in range(LINES):
        f.write("likha(%d)\n" % i)

os.makedirs(SOCKDIR, exist_ok=True)
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)
srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); srv.bind(SOCKPATH); srv.listen(1)
proc = subprocess.Popen([os.path.join(work, "sutram-gui"), src],
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


def drain(t=1.2):
    conn.settimeout(t); buf = b""
    try:
        while True:
            c = conn.recv(65536)
            if not c: break
            buf += c
    except socket.timeout: pass
    return buf


def key(kc, state=0):
    ev = bytearray(32); ev[0] = 2; ev[1] = kc
    struct.pack_into("<I", ev, 4, RID_BASE | 1)
    struct.pack_into("<H", ev, 10, 1)
    struct.pack_into("<H", ev, 28, state)
    conn.sendall(bytes(ev))


# an Expose first so the editor paints
exp = bytearray(32); exp[0] = 12
struct.pack_into("<I", exp, 4, RID_BASE | 1)
struct.pack_into("<H", exp, 12, 900); struct.pack_into("<H", exp, 14, 700)
conn.sendall(bytes(exp)); drain(0.8)

# Ctrl-R = keycode 27 with the Control mask
key(27, 0x0004)
buf = drain(2.0)

# walk the stream: track the last SetForeground (56) and record each gutter draw
cur = None
gutter = {}
i = 0
while i + 4 <= len(buf):
    op = buf[i]; ln = struct.unpack_from("<H", buf, i + 2)[0]
    if ln == 0 or ln > 4096 or i + 4 * ln > len(buf): break
    if op == 56 and ln >= 4:
        # SetForeground: opcode 0, len 2, drawable 4, gc 8, foreground 12
        cur = struct.unpack_from("<I", buf, i + 12)[0]
    elif op == 76 and ln >= 4:
        n = buf[i + 1]
        x = struct.unpack_from("<h", buf, i + 12)[0]
        if x == GUTTER_X:
            gutter[buf[i + 16:i + 16 + n].decode("latin-1")] = cur
    i += 4 * ln

proc.terminate()
try: proc.wait(timeout=4)
except Exception: proc.kill()
conn.close(); srv.close()
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)
shutil.rmtree(work, ignore_errors=True)

print("  gutter numbers and their colours:")
for k in sorted(gutter, key=lambda s: (len(s), s)):
    c = gutter[k]
    tag = "ERR" if c == COL_ERR else ("dim" if c == COL_GUTTER else hex(c or 0))
    print(f"    {k!r:8s} -> {tag}")

want = str(ERR_LINE)
if want not in gutter:
    print(f"  FAIL  gutter number {want!r} was not painted at all")
    sys.exit(1)
if gutter[want] != COL_ERR:
    print(f"  FAIL  line {want} painted {hex(gutter[want] or 0)}, expected the error red {hex(COL_ERR)}")
    sys.exit(1)
others = [k for k in gutter if k != want and gutter[k] == COL_ERR]
if others:
    print(f"  FAIL  these lines are also red: {others}")
    sys.exit(1)
print(f"  PASS  line {ERR_LINE} is red ({hex(COL_ERR)}); the others are dim")
sys.exit(0)
