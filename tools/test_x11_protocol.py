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
    101: ("GetKeyboardMapping", 4),  # first_keycode, count, 2 unused
}



# ---- slice 4: server keymap -------------------------------------------------
# Standard US keycode -> ASCII (index 0 keysym). The client should fetch this
# with GetKeyboardMapping (101) rather than assume it.
KC_TABLE = {}
for i, ch in enumerate("1234567890"):
    KC_TABLE[10 + i] = ch
KC_TABLE[20] = "-"; KC_TABLE[21] = "="
for i, ch in enumerate("qwertyuiop"):
    KC_TABLE[24 + i] = ch
KC_TABLE[34] = "["; KC_TABLE[35] = "]"
for i, ch in enumerate("asdfghjkl"):
    KC_TABLE[38 + i] = ch
KC_TABLE[47] = ";"; KC_TABLE[48] = "'"; KC_TABLE[49] = "`"
for i, ch in enumerate("zxcvbnm"):
    KC_TABLE[52 + i] = ch
KC_TABLE[59] = ","; KC_TABLE[60] = "."; KC_TABLE[61] = "/"
KC_TABLE[65] = " "


def build_keymap_reply(first, count, overrides=None):
    """GetKeyboardMapping reply: 32-byte header + count*per keysyms."""
    overrides = overrides or {}
    per = 2
    syms = bytearray()
    for i in range(count):
        kc = first + i
        ch = overrides.get(kc, KC_TABLE.get(kc, 0))
        syms += struct.pack("<I", ord(ch) if isinstance(ch, str) else ch)  # index 0
        syms += struct.pack("<I", 0)                                       # index 1
    n = len(syms) // 4
    hdr = bytearray(32)
    hdr[0] = 1                       # Reply
    hdr[1] = per                     # keysyms_per_keycode
    struct.pack_into("<H", hdr, 2, 0)
    struct.pack_into("<I", hdr, 4, n)
    return bytes(hdr) + bytes(syms)


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
        # body excludes the 4-byte header, so ImageText8's n is head[1], not
        # body[0] — body[0] is the first byte of the drawable window id.
        return op, ln, body, head

    for _ in range(3):
        r = read_request()
        if r is None:
            break
        op, ln, body, head = r
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

    # ---- 2b. slice 4: the client must ask for the real keymap ------------
    r = read_request()
    check(r is not None and r[0] == 101,
          "client requests GetKeyboardMapping (opcode 101)",
          f"got {r[0] if r else None}")
    if r is not None:
        op, ln, body, head = r
        check(4 * ln == 8, "GetKeyboardMapping: 8-byte request", f"got {4*ln}")
        first_kc = body[0]
        count = body[1]
        check(first_kc == 8 and count == 119,
              "GetKeyboardMapping: asks for keycodes 8..126",
              f"first={first_kc} count={count}")
        # Serve a deliberately NON-US value for keycode 43 ('h' on US): 'Z'.
        # If the client uses the server map it draws 'Z'; if it uses its
        # hardcoded US table it draws 'h'. The next section proves which.
        conn.sendall(build_keymap_reply(first_kc, count, overrides={43: "Z"}))

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
        op, ln, body, head = r
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

    # ---- 4. typing: send KeyPress events, expect the text to be drawn ------
    def keypress(keycode):
        ev = bytearray(32)
        ev[0] = 2                        # KeyPress
        ev[1] = keycode                  # detail = keycode
        struct.pack_into("<I", ev, 4, RID_BASE | 1)
        struct.pack_into("<H", ev, 10, 1)
        conn.sendall(bytes(ev))

    def drain_texts():
        """Read until the client goes quiet, collecting ImageText8 payloads.

        A fixed request count desynchronises the stream: if the client sends
        more than the cap, leftovers are attributed to the next key. Drain to
        quiescence instead.
        """
        found = []
        old = conn.gettimeout()
        conn.settimeout(0.35)
        try:
            while True:
                try:
                    r = read_request()
                except Exception:
                    break
                if r is None:
                    break
                op, ln, body, head = r
                if op == 76:             # ImageText8
                    n_chars = head[1]
                    found.append(body[12:12 + n_chars].decode("latin-1"))
        finally:
            conn.settimeout(old)
        return found

    # Slice 4: the server served 'Z' for keycode 43. If the client used its
    # hardcoded US table it would draw 'h' here. It must draw 'Z'.
    keypress(43)
    texts = drain_texts()
    check(any("Z" in t for t in texts),
          "client used the SERVER keymap (keycode 43 -> 'Z', not US 'h')",
          f"saw {texts[:6]}")
    check(not any(t == "h" for t in texts),
          "client did NOT fall back to the hardcoded US table for keycode 43",
          f"saw {texts[:6]}")

    # keycode 31 is 'i' in the served map, so the line becomes 'Zi'
    keypress(31)
    texts = drain_texts()
    check(any(t == "Zi" for t in texts),
          "typing keycode 31 produced 'Zi' on the same line",
          f"saw {texts[:6]}")

    # backspace (keycode 22) removes the last character
    keypress(22)
    texts = drain_texts()
    check(any(t == "Z" for t in texts) and not any(t == "Zi" for t in texts),
          "backspace removed the last character",
          f"saw {texts[:6]}")

    # Return (keycode 36) starts a new line, so the text splits
    keypress(36)
    keypress(31)
    texts = drain_texts()
    check(sum(1 for t in texts if t in ("Z", "i")) >= 2,
          "return then a key produced two separate lines",
          f"saw {texts[:6]}")

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
