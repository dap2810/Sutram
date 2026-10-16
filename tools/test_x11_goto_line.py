import os, socket, struct, subprocess, sys, tempfile, shutil

# Slice 34 proof: after a failed compile the editor JUMPS to the error line.
#
# The buffer is 60 lines but only 23 fit. The mock compiler names line 45. Before the
# run the gutter shows the top of the file (1..); after Ctrl-R it must show a window
# that CONTAINS 45. That proves the scroll happened, not just the colour.
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
ROOT_WIN = 0x00000400; RID_BASE = 0x00200000; RID_MASK = 0x001FFFFF
GUTTER_X = 18
ERR_LINE = 45
LINES = 60


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
work = tempfile.mkdtemp(prefix="sutram-goto-")
shutil.copy(gui_src, os.path.join(work, "sutram-gui"))
mock = os.path.join(work, "sutram_compiler")
with open(mock, "w") as f:
    f.write('#!/bin/sh\necho "Sutram Error [E_TEST]: $1:%d: deliberate"\nexit 1\n' % ERR_LINE)
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


def gutter_numbers(buf):
    """every ImageText8 drawn at the gutter x, in order"""
    out = []
    i = 0
    while i + 4 <= len(buf):
        op = buf[i]; ln = struct.unpack_from("<H", buf, i + 2)[0]
        if ln == 0 or ln > 4096 or i + 4 * ln > len(buf): break
        if op == 76 and ln >= 4:
            n = buf[i + 1]
            x = struct.unpack_from("<h", buf, i + 12)[0]
            if x == GUTTER_X:
                out.append(buf[i + 16:i + 16 + n].decode("latin-1"))
        i += 4 * ln
    return out


# expose so the editor paints the top of the file
exp = bytearray(32); exp[0] = 12
struct.pack_into("<I", exp, 4, RID_BASE | 1)
struct.pack_into("<H", exp, 12, 900); struct.pack_into("<H", exp, 14, 700)
conn.sendall(bytes(exp))
before = gutter_numbers(drain(1.0))

# Ctrl-R = keycode 27 with the Control mask
ev = bytearray(32); ev[0] = 2; ev[1] = 27
struct.pack_into("<I", ev, 4, RID_BASE | 1)
struct.pack_into("<H", ev, 10, 1); struct.pack_into("<H", ev, 28, 0x0004)
conn.sendall(bytes(ev))
after = gutter_numbers(drain(2.5))

proc.terminate()
try: proc.wait(timeout=4)
except Exception: proc.kill()
conn.close(); srv.close()
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)
shutil.rmtree(work, ignore_errors=True)

print("  gutter before Ctrl-R:", before[:8], "...")
print("  gutter after  Ctrl-R:", after[:8], "...")

want = str(ERR_LINE)
if want not in before and want not in after:
    print(f"  FAIL  line {want} never appeared in the gutter")
    sys.exit(1)
if want in before:
    print(f"  FAIL  line {want} was already visible before the run -- test cannot prove a jump")
    sys.exit(1)
print(f"  PASS  the editor jumped: line {ERR_LINE} visible only after the failed compile")
sys.exit(0)
