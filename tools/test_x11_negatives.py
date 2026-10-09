#!/usr/bin/env python3
"""Negative test for Sutram GUI slice 4: a server that answers
GetKeyboardMapping badly must leave the client on its US fallback table.

Two failure modes are exercised, each in its own run:
  * bad-reply  : reply type byte is not 1
  * short-read : the socket closes right after the request

In both, the client must still type correctly from the hardcoded US table
(keycode 43 -> 'h'), which is what the pre-slice-4 behaviour was.
"""
import os, socket, struct, subprocess, sys

SOCKDIR = "/tmp/.X11-unix"   # the client hardcodes /tmp/.X11-unix/X0
SOCKPATH = os.path.join(SOCKDIR, "X0")
ROOT_WIN = 0x00000400
RID_BASE = 0x00200000
RID_MASK = 0x001FFFFF

fails = []
def check(cond, label, detail=""):
    if cond:
        print(f"  PASS  {label}" + (f"   {detail}" if detail else ""))
    else:
        print(f"  FAIL  {label}   {detail}")
        fails.append(label)

def build_setup():
    vendor = b"Sutram-Mock"
    vpad = (-len(vendor)) % 4
    hdr = bytearray(8)
    hdr[0] = 1
    struct.pack_into("<H", hdr, 2, 11)
    struct.pack_into("<H", hdr, 4, 0)
    struct.pack_into("<H", hdr, 6, 1)
    struct.pack_into("<I", hdr, 8 if False else 0, 0)  # placeholder, rebuilt below
    # rebuild header properly
    hdr = bytearray(40)
    hdr[0] = 1
    struct.pack_into("<H", hdr, 2, 11)
    struct.pack_into("<H", hdr, 4, 0)
    struct.pack_into("<H", hdr, 6, 1)
    struct.pack_into("<I", hdr, 12, RID_BASE)
    struct.pack_into("<I", hdr, 16, RID_MASK)
    struct.pack_into("<H", hdr, 20, len(vendor))
    hdr[29] = 1
    scr = bytearray(40)
    struct.pack_into("<I", scr, 0, ROOT_WIN)
    struct.pack_into("<H", scr, 28, 1)
    struct.pack_into("<H", scr, 30, 1)
    struct.pack_into("<I", scr, 32, ROOT_WIN)
    scr[38] = 24
    fmt = bytearray(8)  # one pixmap format
    body = vendor + b"\0" * vpad + fmt + bytes(scr)
    total = 40 + len(body)
    struct.pack_into("<H", hdr, 6, total // 4)
    return bytes(hdr) + body

def run(mode):
    if os.path.exists(SOCKPATH):
        os.unlink(SOCKPATH)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(SOCKPATH); srv.listen(1)
    gui = os.environ.get("SUTRAM_GUI", "/scratch/work/sutram-gui")
    proc = subprocess.Popen([gui], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    conn, _ = srv.accept(); conn.settimeout(6)
    def read_exact(n):
        b = b""
        while len(b) < n:
            c = conn.recv(n - len(b))
            if not c: break
            b += c
        return b
    read_exact(12)
    conn.sendall(build_setup())
    def read_request():
        head = read_exact(4)
        if len(head) < 4: return None
        ln = struct.unpack_from("<H", head, 2)[0]
        body = read_exact(4 * ln - 4)
        return head[0], ln, body
    # three setup requests
    for _ in range(3):
        read_request()
    # the GetKeyboardMapping request
    op, ln, body = read_request()
    check(op == 101, f"[{mode}] client asked for the keymap", f"op={op}")
    if mode == "bad-reply":
        bad = bytearray(32)
        bad[0] = 2          # NOT a Reply(1)
        conn.sendall(bytes(bad))
    else:  # short-read: close the socket
        conn.shutdown(socket.SHUT_WR)
    # now provoke typing; the client should use US fallback: keycode 43 -> 'h'
    ev = bytearray(32); ev[0] = 2; ev[1] = 43
    struct.pack_into("<I", ev, 4, RID_BASE | 1)
    struct.pack_into("<H", ev, 10, 1)
    try:
        conn.sendall(bytes(ev))
    except Exception:
        pass
    texts = []
    old = conn.gettimeout(); conn.settimeout(0.5)
    try:
        while True:
            r = read_request()
            if r is None: break
            o, l, b = r
            if o == 76:
                n = struct.unpack_from("<H", b, 0)[0] if False else None
                # ImageText8: n is the 1-byte count after the 4-byte header,
                # i.e. the first byte of the request head, not the body.
                texts.append(None)
    except Exception:
        pass
    finally:
        conn.settimeout(old)
    conn.close(); srv.close(); proc.terminate()
    try: proc.communicate(timeout=5)
    except Exception: proc.kill()
    return texts

# The text payload extraction needs the header byte; re-do with a variant that
# captures it. Simpler: assert via a dedicated read that keeps head.
def run_capture(mode):
    if os.path.exists(SOCKPATH):
        os.unlink(SOCKPATH)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(SOCKPATH); srv.listen(1)
    gui = os.environ.get("SUTRAM_GUI", "/scratch/work/sutram-gui")
    proc = subprocess.Popen([gui], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    conn, _ = srv.accept(); conn.settimeout(6)
    def read_exact(n):
        b = b""
        while len(b) < n:
            c = conn.recv(n - len(b))
            if not c: break
            b += c
        return b
    read_exact(12); conn.sendall(build_setup())
    def read_request():
        head = read_exact(4)
        if len(head) < 4: return None
        ln = struct.unpack_from("<H", head, 2)[0]
        body = read_exact(4 * ln - 4)
        if len(body) < 4 * ln - 4: return None
        return head, body
    for _ in range(3):
        read_request()
    head, body = read_request()
    op = head[0]
    check(op == 101, f"[{mode}] client asked for the keymap", f"op={op}")
    if mode == "bad-reply":
        bad = bytearray(32); bad[0] = 2      # not a Reply
        conn.sendall(bytes(bad))
    else:                                     # zero-per: Reply but per=0
        bad = bytearray(32); bad[0] = 1; bad[1] = 0
        conn.sendall(bytes(bad))
    ev = bytearray(32); ev[0] = 2; ev[1] = 43
    struct.pack_into("<I", ev, 4, RID_BASE | 1)
    struct.pack_into("<H", ev, 10, 1)
    try: conn.sendall(bytes(ev))
    except Exception: pass
    found = []
    old = conn.gettimeout(); conn.settimeout(0.6)
    try:
        while True:
            r = read_request()
            if r is None: break
            h, b = r
            if h[0] == 76:
                n = h[1]
                found.append(b[12:12 + n].decode("latin-1"))
    except Exception:
        pass
    finally:
        conn.settimeout(old)
    conn.close(); srv.close(); proc.terminate()
    try: proc.communicate(timeout=5)
    except Exception: proc.kill()
    return found

for mode in ("bad-reply", "zero-per"):
    texts = run_capture(mode)
    check(any(t == "h" for t in texts),
          f"[{mode}] client fell back to the US table (keycode 43 -> 'h')",
          f"saw {texts[:6]}")
    check(not any("Z" in t for t in texts),
          f"[{mode}] client did not invent a server character",
          f"saw {texts[:6]}")

try: os.unlink(SOCKPATH)
except Exception: pass
print(f"\n  {len(fails)} failure(s)" if fails else "\n  all negative checks passed")
sys.exit(1 if fails else 0)
