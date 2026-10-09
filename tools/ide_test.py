#!/usr/bin/env python3
"""Drive the Sutram IDE through a PTY and report what it actually renders.

Usage: python3 tools/ide_test.py
This is the IDE's regression harness: it launches the real binary in a pseudo
terminal, sends keystrokes, and reconstructs the visible screen.
"""
import os, pty, time, fcntl, termios, struct, select

# Derive the IDE path from the repository root so the harness is portable
# (ChatGPT flagged the old hardcoded /scratch/work path — correct catch).
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDE = os.environ.get("SUTRAM_IDE") or os.path.join(_ROOT, "sutram-ide")


def run(keys, arg, cols=80, rows=24, wait=0.7):
    pid, fd = pty.fork()
    if pid == 0:
        os.execv(IDE, ["sutram-ide", arg])
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))
    time.sleep(wait)
    out = b""
    for k in keys:
        os.write(fd, k)
        time.sleep(0.4)
        while True:
            r, _, _ = select.select([fd], [], [], 0.15)
            if not r:
                break
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                chunk = b""
            if not chunk:
                break
            out += chunk
    time.sleep(0.3)
    while True:
        r, _, _ = select.select([fd], [], [], 0.2)
        if not r:
            break
        try:
            chunk = os.read(fd, 65536)
        except OSError:
            break
        if not chunk:
            break
        out += chunk
    try:
        os.kill(pid, 9)
    except Exception:
        pass
    os.waitpid(pid, 0)
    return out


def screen(data, cols=80, rows=24):
    grid = [[" "] * cols for _ in range(rows)]
    r = c = 0
    i = 0
    while i < len(data):
        ch = data[i]
        if ch == 27 and i + 1 < len(data) and data[i + 1] == ord("["):
            j = i + 2
            while j < len(data) and not (64 <= data[j] <= 126):
                j += 1
            params = data[i + 2:j].decode("latin1")
            final = chr(data[j]) if j < len(data) else ""
            if final == "H":
                parts = params.split(";")
                r = (int(parts[0]) - 1) if parts and parts[0] else 0
                c = (int(parts[1]) - 1) if len(parts) > 1 and parts[1] else 0
            elif final == "J":
                grid = [[" "] * cols for _ in range(rows)]
            i = j + 1
            continue
        if ch == 10:
            r += 1
            c = 0
        elif ch == 13:
            c = 0
        elif 32 <= ch < 127:
            if 0 <= r < rows and 0 <= c < cols:
                grid[r][c] = chr(ch)
            c += 1
        i += 1
    return ["".join(row).rstrip() for row in grid]


def show(name, keys, arg, cols=80, rows=24):
    print(f"=== {name} ===")
    data = run(keys, arg, cols=cols, rows=rows)
    for i, l in enumerate(screen(data, cols, rows)):
        if l.strip():
            print(f"{i+1:2d}| {l}")
    for code, nm in [(b"\x1b[95m", "keyword"), (b"\x1b[92m", "string"), (b"\x1b[96m", "number"), (b"\x1b[90m", "comment/lineno")]:
        print(f"   {nm:16s} colour: {'emitted' if code in data else 'ABSENT'}")
    print()


if __name__ == "__main__":
    hello = os.path.join(_ROOT, "examples", "01_hello.sm")
    show("render: line numbers + highlighting", [b"\x11"], hello)
    show("run a program (Ctrl-R)", [b"\x12", b"\x11"], hello)
    show("shell pane (Ctrl-T, two statements, Enter runs the session)",
         [b"\x14", b"vitti x = 6", b"\r", b"likha(x * 7)", b"\r", b"\x14"], hello)
    show("examples browser (Ctrl-E x3 then Run)", [b"\x05", b"\x05", b"\x05", b"\x12", b"\x11"], hello)
    show("edit: type text then run", [b"   ", b"likha(42)", b"\x12", b"\x11"], hello)
