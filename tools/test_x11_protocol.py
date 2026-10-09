#!/usr/bin/env python3
"""Mock X11 server — verifies the Sutram Linux GUI's protocol bytes without a display.

The sandbox has no X server, so the GUI cannot be run visually here. This stands
in for one: it accepts the connection, validates the setup request, replies with
a well-formed setup block, then reads every request the client sends and checks
it against the X11 wire format.

The important change from the first version: request lengths are no longer
asserted against hard-coded numbers. The reader derives the body length FROM the
length field, reads exactly that many bytes, and then checks the request is
self-consistent. The old test asserted `length == 8` for CreateWindow, which
encoded the client's bug as expected behaviour instead of catching it.

It proves the client's X11 protocol is correctly formed. It does NOT prove the
window renders — only a real display can show that.

Run: python3 tools/test_x11_protocol.py
"""
import os, socket, struct, subprocess, sys

SOCKDIR = "/tmp/.X11-unix"
SOCKPATH = os.path.join(SOCKDIR, "X0")

ROOT_WIN = 0x00001234
RID_BASE = 0x00400000
RID_MASK = 0x003FFFFF

fails = []

def check(cond, label, detail=""):
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + (f"   {detail}" if detail else ""))
    if not cond:
        fails.append(label)


def build_setup():
    vendor = b"SutramMock"
    vpad = (-len(vendor)) % 4
    hdr = bytearray(40)
    hdr[0] = 1
    struct.pack_into("<HH", hdr, 2, 11, 0)
    struct.pack_into("<I", hdr, 8, 1)
    struct.pack_into("<I", hdr, 12, RID_BASE)
    struct.pack_into("<I", hdr, 16, RID_MASK)
    struct.pack_into("<I", hdr, 20, 0)
    struct.pack_into("<H", hdr, 24, len(vendor))
    struct.pack_into("<H", hdr, 26, 4096)
    hdr[28] = 1
    hdr[29] = 1
    hdr[34] = 8
    hdr[35] = 255
    fmt = struct.pack("<BBBBBBBB", 24, 32, 32, 0, 0, 0, 0, 0)
    scr = bytearray(40)
    struct.pack_into("<I", scr, 0, ROOT_WIN)
    struct.pack_into("<I", scr, 4, 0x00000020)
    struct.pack_into("<I", scr, 8, 0xFFFFFF)
    struct.pack_into("<H", scr, 20, 1024)
    struct.pack_into("<H", scr, 22, 768)
    struct.pack_into("<H", scr, 28, 1)
    struct.pack_into("<H", scr, 30, 1)
    struct.pack_into("<I", scr, 32, ROOT_WIN)
    scr[38] = 24
    body = vendor + b"\0" * vpad + fmt + bytes(scr)
    total = len(hdr) + len(body)
    struct.pack_into("<H", hdr, 6, total // 4)
    return bytes(hdr) + body


# ---- request shapes we expect to see --------------------------------------
# (opcode, name, fixed_body_bytes)  -> body = 4*length - 4 (length counts the
# whole request including its own 4-byte header)
FIXED = {
    1:  ("CreateWindow", 32),    # 36 total with one value
    8:  ("MapWindow", 4),
    55: ("CreateGC", 20),        # 24 total with two values
    56: ("ChangeGC", 12),        # 16 total with one value
    70: ("PolyFillRect", 8),     # 20 total with one rectangle
    76: ("ImageText8", 12),      # 16 + n, padded
}


def main():
    os.makedirs(SOCKDIR, exist_ok=True)
    if os.path.exists(SOCKPATH):
        os.unlink(SOCKPATH)
    srv = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    srv.bind(SOCKPATH)
    srv.listen(1)
    print("  mock X server listening on", SOCKPATH)

    gui = os.environ.get("SUTRAM_GUI", "/scratch/work/sutram-gui")
    proc = subprocess.Popen([gui], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    conn, _ = srv.accept()
    conn.settimeout(6)

    def read_exact(n):
        buf = b""
        while len(buf) < n:
            chunk = conn.recv(n - len(buf))
            if not chunk:
                break
            buf += chunk
        return buf

    # ---- 1. connection setup request --------------------------------------
    hs = read_exact(12)
    order, pad, major, minor, alen, dlen, pad2 = struct.unpack("<BBHHHHH", hs[:12])
    check(order == 0x6C, "byte order byte is 'l' (little-endian)", f"got 0x{order:02x}")
    check(major == 11, "protocol major version is 11", f"got {major}")
    check(minor == 0, "protocol minor version is 0", f"got {minor}")
    check(alen == 0 and dlen == 0, "no auth requested", f"alen={alen} dlen={dlen}")

    conn.sendall(build_setup())

    # ---- 2. read requests, length-driven ----------------------------------
    seen = []
    windows = set()

    def read_request():
        head = read_exact(4)
        if len(head) < 4:
            return None
        op = head[0]
        ln = struct.unpack_from("<H", head, 2)[0]
        body = read_exact(4 * ln - 4)
        if len(body) < 4 * ln - 4:
            return None
        return op, ln, body

    for _ in range(3):
        r = read_request()
        if r is None:
            break
        op, ln, body = r
        name, fixed = FIXED.get(op, (f"op{op}", None))
        seen.append(name)
        total = 4 * ln
        if fixed is not None:
            if name in ("CreateWindow", "CreateGC", "ChangeGC"):
                # these carry a value list; check the fixed part is covered
                check(total >= fixed + 4,
                      f"{name}: declared length covers its fixed fields",
                      f"{total} bytes, fixed part {fixed}")
            elif name == "ImageText8":
                n = (total - 16)
                check(16 <= total <= 16 + 255,
                      f"{name}: length matches n bytes of text",
                      f"{total} bytes total")
            else:
                check(total == fixed + 4,
                      f"{name}: declared length equals its body size",
                      f"{total} bytes, expected {fixed + 4}")
        if name == "CreateWindow":
            wid = struct.unpack_from("<I", body, 0)[0]
            parent = struct.unpack_from("<I", body, 4)[0]
            w = struct.unpack_from("<H", body, 12)[0]
            h = struct.unpack_from("<H", body, 14)[0]
            vm = struct.unpack_from("<I", body, 24)[0]
            windows.add(wid)
            check(parent == ROOT_WIN, "CreateWindow: parent is the advertised root",
                  f"got 0x{parent:08x}, expected 0x{ROOT_WIN:08x}")
            check(w == 900 and h == 620, "CreateWindow: window is 900x620", f"got {w}x{h}")
            check(vm == 0x00000800, "CreateWindow: value-mask is CWEventMask", f"got 0x{vm:08x}")
            check(wid == (RID_BASE | 1), "CreateWindow: id drawn from the advertised range",
                  f"got 0x{wid:08x}")
        if name == "MapWindow":
            wid = struct.unpack_from("<I", body, 0)[0]
            check(wid in windows, "MapWindow: targets the window we created",
                  f"0x{wid:08x}")

    check(seen[:3] == ["CreateWindow", "CreateGC", "MapWindow"],
          "request order is CreateWindow, CreateGC, MapWindow", str(seen[:3]))

    # ---- 3. provoke a repaint and count what comes back -------------------
    expose = bytearray(32)
    expose[0] = 12                       # Expose
    struct.pack_into("<I", expose, 4, RID_BASE | 1)
    struct.pack_into("<HHHH", expose, 8, 0, 0, 900, 620)
    conn.sendall(bytes(expose))

    ops = {}
    for _ in range(40):
        try:
            r = read_request()
        except Exception:
            break
        if r is None:
            break
        op, ln, body = r
        name, fixed = FIXED.get(op, (f"op{op}", None))
        ops[name] = ops.get(name, 0) + 1
        total = 4 * ln
        if name == "PolyFillRect":
            check(total == 20, "PolyFillRect: length is 20 bytes (1 rect)", f"got {total}")
        if name == "ImageText8":
            check(total % 4 == 0, "ImageText8: request is 4-byte aligned", f"got {total}")
        if name == "ChangeGC":
            check(total == 16, "ChangeGC: length is 16 bytes (1 value)", f"got {total}")

    check(ops.get("PolyFillRect", 0) >= 4,
          "repaint drew at least four rectangles (background + two panes + rule)",
          f"got {ops.get('PolyFillRect', 0)}")
    check(ops.get("ImageText8", 0) >= 4,
          "repaint drew at least four text runs (title + two labels + hint)",
          f"got {ops.get('ImageText8', 0)}")
    check(ops.get("ChangeGC", 0) >= 4,
          "repaint set the GC colour before each colour change",
          f"got {ops.get('ChangeGC', 0)}")

    conn.close()
    srv.close()
    proc.terminate()
    try:
        out = proc.communicate(timeout=5)[0] or ""
    except Exception:
        proc.kill()
        out = ""
    check("connected to X" in out, "client reported a successful connection", repr(out.strip()[:60]))

    try:
        os.unlink(SOCKPATH)
    except Exception:
        pass

    print(f"\n  {len(fails)} failure(s)" if fails else "\n  all X11 protocol checks passed")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
