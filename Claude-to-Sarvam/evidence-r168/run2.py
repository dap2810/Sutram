import os, time, json, subprocess
def spawn(b):
    r, w = os.pipe()
    fa = [(os.POSIX_SPAWN_DUP2, w, 1), (os.POSIX_SPAWN_CLOSE, r)]
    t = time.perf_counter()
    pid = os.posix_spawn(b, [b], {}, file_actions=fa)
    os.close(w)
    out = b''
    while True:
        c = os.read(r, 65536)
        if not c: break
        out += c
    os.close(r)
    _, st, ru = os.wait4(pid, 0)
    return time.perf_counter() - t, ru.ru_maxrss, os.waitstatus_to_exitcode(st), out.decode().strip()
def gtime(b):
    o = subprocess.run(['env', '-i', '/usr/bin/time', '-f', '%M', b], capture_output=True, text=True)
    return int(o.stderr.strip().splitlines()[-1])
progs = ['Z'] + [f'{k}{n}' for k in 'ABCDGM' for n in (50000, 200000, 800000)]
res = {}
for rep in range(5):
    for p in progs:
        res.setdefault(p, []).append(spawn('./' + p + '.bin'))
tm = {p: [gtime('./' + p + '.bin') for _ in range(3)] for p in progs}
for p in progs:
    r = res[p]
    print(f"{p:9s} exit {sorted(set(x[2] for x in r))} out {r[0][3]!r:15s} rss(posix_spawn) {[x[1] for x in r]}  rss(/usr/bin/time) {tm[p]}  wall ms {[round(x[0]*1000,1) for x in r]} best {min(x[0] for x in r)*1000:.1f}")
json.dump({'spawn': {k: [list(x) for x in v] for k, v in res.items()}, 'time': tm}, open('runs2.json', 'w'))
