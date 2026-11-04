import subprocess, time, os, signal, sys
def measure(binary, secs=2.0):
    p = subprocess.Popen([binary], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    peak_rss = 0; peak_vsz = 0
    t0 = time.time()
    while time.time() - t0 < secs:
        try:
            with open(f"/proc/{p.pid}/status") as f:
                d = {}
                for line in f:
                    if line.startswith("VmRSS:"): d["rss"] = int(line.split()[1])
                    if line.startswith("VmSize:"): d["vsz"] = int(line.split()[1])
                peak_rss = max(peak_rss, d.get("rss", 0))
                peak_vsz = max(peak_vsz, d.get("vsz", 0))
        except FileNotFoundError:
            break
        if p.poll() is not None:
            break
        time.sleep(0.01)
    if p.poll() is None:
        p.kill()
    p.wait()
    return peak_rss, peak_vsz
if __name__ == "__main__":
    for b in sys.argv[1:]:
        rss, vsz = measure(b)
        print(f"{b}: peak RSS {rss} KB ({rss/1024:.1f} MB), peak VSZ {vsz} KB ({vsz/1024:.1f} MB)")
