import subprocess, os, time
C = "/home/hatch/workspace/r103/tree/sutram_compiler"
D = "/home/hatch/workspace/r103/ws2/probes"

def gen(n, touched, name):
    lines = ["mukhya() {"]
    for i in range(n):
        lines.append(f"    kosh k{i}[4]")
        if touched:
            lines.append(f"    kosh_push(k{i}, 1)")
    lines.append("    vitti x = grahan()")
    lines.append("    likha(x)")
    lines.append("}")
    p = f"{D}/{name}.sm"
    open(p, "w").write("\n".join(lines) + "\n")
    b = f"{D}/{name}.bin"
    r = subprocess.run([C, p, b], capture_output=True, text=True, timeout=120)
    if not os.path.exists(b):
        print(f"{name}: COMPILE FAILED: {(r.stderr or r.stdout)[:300]}")
        return None
    return b

def measure(b, name):
    pr = subprocess.Popen([b], stdin=subprocess.PIPE,
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    st = open(f"/proc/{pr.pid}/status").read()
    vals = {}
    for key in ["VmPeak", "VmSize", "VmHWM", "VmRSS"]:
        for ln in st.splitlines():
            if ln.startswith(key):
                vals[key] = int(ln.split()[1])
    pr.kill()
    pr.wait()
    print(f"{name}: VmPeak={vals.get('VmPeak')} kB VmSize={vals.get('VmSize')} kB "
          f"VmHWM={vals.get('VmHWM')} kB VmRSS={vals.get('VmRSS')} kB")
    return vals

measure(gen(0, False, "base"), "baseline N=0")
for n in [1, 10, 100, 1000]:
    b = gen(n, False, f"decl{n}")
    if b:
        measure(b, f"declared-only N={n}")
for n in [1, 10, 100, 1000]:
    b = gen(n, True, f"touch{n}")
    if b:
        measure(b, f"touched N={n}")
