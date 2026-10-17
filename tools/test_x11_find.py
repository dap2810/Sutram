import os, socket, struct, subprocess, time

# Slice 15 proof: Ctrl-F opens a find prompt, Enter searches (wrapping) and moves
# the caret tak the hit, Esc cancels without moving it. Buffer read back via Ctrl-S.
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
    try:
        conn.sendall(bytes(ev))
    except BrokenPipeError:
        print("GUI DIED before keycode %d ctrl=%d; poll=%s" % (kc, ctrl, proc.poll()))
        raise SystemExit(1)
    time.sleep(0.04)
    if proc.poll() is not None:
        print("GUI EXITED after keycode %d ctrl=%d rc=%s" % (kc, ctrl, proc.poll()))
        raise SystemExit(1)

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

def saved():
    key(39, ctrl=True); time.sleep(0.35)     # Ctrl-S
    try: return open(SAVED, "rb").read().decode("latin-1")
    except FileNotFoundError: return "<none>"

A, B, C, Z = 38, 56, 54, 52       # a, b, c, z
RETURN, ESC, BACKSPACE = 36, 9, 22
CTRL_F = 41

# "abcabc", caret at end
for kc in (A, B, C, A, B, C): key(kc)
print("buffer:", repr(saved()))

# Ctrl-F, type "bc", Enter -> wraps and finds "bc" at index 1
key(CTRL_F, ctrl=True); time.sleep(0.1)
key(B); key(C)
found = [t for t in texts() if "Find" in t or t == "Find: "]
print("prompt drawn:", any("Find" in t for t in found) or any(t.startswith("Find") for t in found))
key(RETURN)
key(Z)                            # insert at the hit
got = saved()
print("after Ctrl-F 'bc' Enter z:", repr(got))
ok_find = got == "azbcabc"
print("FIND + WRAP MOVED CARET TO HIT:", ok_find)

# Esc must cancel without moving the caret: caret is now at 2 (after z).
# Ctrl-F, type "abc", Esc, then insert 'q' -> must land at 2, not at a hit.
key(CTRL_F, ctrl=True); time.sleep(0.1)
key(A); key(B); key(C)
key(ESC)
key(24)                           # 'q' on the mock keymap
got2 = saved()
print("after Ctrl-F 'abc' Esc q:", repr(got2))
ok_esc = got2 == "azqbcabc"
print("ESC CANCELS WITHOUT MOVING CARET:", ok_esc)

print("RESULT:", all([ok_find, ok_esc]))

conn.close(); srv.close(); proc.terminate()
try: proc.communicate(timeout=5)
except Exception: proc.kill()
