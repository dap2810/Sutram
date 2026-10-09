import os, socket, struct, subprocess, sys, time, shutil

# Slice 11 proof: the output pane scrolls. A mock compiler beside the GUI emits
# 10 lines; the pane shows the last 7 (auto-scrolled to newest), PgUp shows the
# first 7, PgDn returns to the last 7. No display needed.
SOCKDIR = "/tmp/.X11-unix"; SOCKPATH = os.path.join(SOCKDIR, "X0")
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

# ---- stage GUI + a mock compiler beside it (find_compiler uses /proc/self/exe) --
STAGE = "/tmp/sc11"
shutil.rmtree(STAGE, ignore_errors=True); os.makedirs(STAGE)
shutil.copy(os.environ.get("SUTRAM_GUI", "/scratch/work/sutram-gui"), STAGE + "/sutram-gui")
mock = STAGE + "/sutram_compiler"
with open(mock, "w") as f:
    f.write("#!/usr/bin/env python3\n"
            "import sys\n"
            "for i in range(1, 11):\n"
            "    print('Error: line %d problem' % i)\n"
            "sys.exit(1)\n")
os.chmod(mock, 0o755)

os.makedirs(SOCKDIR, exist_ok=True)
if os.path.exists(SOCKPATH): os.unlink(SOCKPATH)
srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); srv.bind(SOCKPATH); srv.listen(1)
proc = subprocess.Popen([STAGE + "/sutram-gui"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
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
    conn.sendall(bytes(ev)); time.sleep(0.05)

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

# type "likha", then Ctrl-R
for kc in (46, 31, 45, 43, 38): key(kc)
key(27, ctrl=True)          # Ctrl-R -> mock compiler emits 10 lines
time.sleep(1.2)
first = texts()
err = [t for t in first if t.startswith("Error:")]
print("after run, error lines drawn:", err)

ok_bottom = err == ["Error: line %d problem" % i for i in range(5, 11)]
print("AUTO-SCROLL TO BOTTOM (newest, lines 5-10 + trailing blank):", ok_bottom)

key(104)                    # PgUp
time.sleep(0.3)
mid = [t for t in texts() if t.startswith("Error:")]
ok_up = mid == ["Error: line %d problem" % i for i in range(1, 8)]
print("PgUp (first 7):", ok_up, mid[:1], mid[-1:] if mid else [])

key(109)                    # PgDn
time.sleep(0.3)
down = [t for t in texts() if t.startswith("Error:")]
ok_down = down == ["Error: line %d problem" % i for i in range(5, 11)]
print("PgDn (back to newest):", ok_down)

key(104); key(104)          # PgUp twice -> clamp at top
time.sleep(0.3)
clamped = [t for t in texts() if t.startswith("Error:")]
one_page = ["Error: line %d problem" % i for i in range(1, 8)]
ok_clamp = len(clamped) in (7, 14) and clamped == one_page * (len(clamped) // 7)
print("PgUp x2 clamps at top:", ok_clamp, "->", clamped)

print("RESULT:", all([ok_bottom, ok_up, ok_down, ok_clamp]))
conn.close(); srv.close(); proc.terminate()
try: proc.communicate(timeout=5)
except Exception: proc.kill()
