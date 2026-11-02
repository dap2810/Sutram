#!/usr/bin/env python3
"""tools/peak_rss.py - the peak resident memory of a program, measured by the kernel (R101).

Polling /proc misses a program that finishes in 200 ms, and `ulimit -v` limits address space, not use. The
measurer is tools/peak_rss.asm: it forks, execs the program, and reads the child's own peak from wait4() -
ru_maxrss, which the kernel keeps for the whole life of the process, however short. It is NASM, not Python,
because ru_maxrss survives execve: a Python fork would put the interpreter's ~5 MB into every number. This
script assembles it once (into $TMPDIR) and runs it. Linux only; ru_maxrss is in KB.

Usage:
    python3 tools/peak_rss.py PROGRAM [ARGS...]          -> "peak_rss_kb 264 exit 0"
    python3 tools/peak_rss.py --repeat 3 PROGRAM [ARGS]  -> the largest peak of 3 runs
The program's stdout is discarded; its exit status is reported (a signal as minus its number).
"""
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def measurer():
    src = os.path.join(HERE, 'peak_rss.asm')
    out = os.path.join(tempfile.gettempdir(), f'sutram-peak-rss-{os.stat(src).st_mtime_ns}')
    if not os.path.exists(out):
        obj = out + '.o'
        subprocess.run(['nasm', '-f', 'elf64', src, '-o', obj], check=True)
        subprocess.run(['ld', '-o', out, obj], check=True)
        os.remove(obj)
    return out


def measure(argv):
    r = subprocess.run([measurer()] + argv, capture_output=True, text=True)
    words = r.stdout.split()
    return int(words[1]), int(words[3])


def main(args):
    repeat = 1
    if args[:1] == ['--repeat']:
        repeat = int(args[1])
        args = args[2:]
    if not args:
        print(__doc__)
        return 2
    args[0] = os.path.abspath(args[0])
    runs = [measure(args) for _ in range(repeat)]
    print(f'peak_rss_kb {max(r[0] for r in runs)} exit {runs[-1][1]}')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
