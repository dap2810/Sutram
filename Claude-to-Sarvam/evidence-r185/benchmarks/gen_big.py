#!/usr/bin/env python3
"""Write the same program - N small functions and a main that calls each once - in Sutram, C, Rust, Go
and Java, for the compile-time comparison. Usage: python3 gen_big.py N OUTDIR"""
import os, sys

n = int(sys.argv[1])
out = sys.argv[2]
os.makedirs(os.path.join(out, 'go_big'), exist_ok=True)
os.makedirs(os.path.join(out, 'java_big'), exist_ok=True)
R = range(n)

with open(os.path.join(out, 'big.sm'), 'w') as f:
    for i in R:
        f.write('prakriya f%d(a, b) {\n    vitti c = a * 3 + b\n    yadi (c > 1000) {\n        c = c - 1000\n    }\n    nivartanam c + %d\n}\n\n' % (i, i))
    f.write('mukhya() {\n    vitti s = 0\n')
    for i in R:
        f.write('    s = f%d(s, %d)\n' % (i, i))
    f.write('    likha(s)\n}\n')

with open(os.path.join(out, 'big.c'), 'w') as f:
    f.write('#include <stdint.h>\n#include <stdio.h>\n\n')
    for i in R:
        f.write('static int64_t f%d(int64_t a, int64_t b) {\n    int64_t c = a * 3 + b;\n    if (c > 1000) {\n        c = c - 1000;\n    }\n    return c + %d;\n}\n\n' % (i, i))
    f.write('int main(void) {\n    int64_t s = 0;\n')
    for i in R:
        f.write('    s = f%d(s, %d);\n' % (i, i))
    f.write('    printf("%lld\\n", (long long)s);\n    return 0;\n}\n')

with open(os.path.join(out, 'big.rs'), 'w') as f:
    for i in R:
        f.write('fn f%d(a: i64, b: i64) -> i64 {\n    let mut c = a * 3 + b;\n    if c > 1000 {\n        c = c - 1000;\n    }\n    c + %d\n}\n\n' % (i, i))
    f.write('fn main() {\n    let mut s: i64 = 0;\n')
    for i in R:
        f.write('    s = f%d(s, %d);\n' % (i, i))
    f.write('    println!("{}", s);\n}\n')

with open(os.path.join(out, 'go_big', 'main.go'), 'w') as f:
    f.write('package main\n\nimport "fmt"\n\n')
    for i in R:
        f.write('func f%d(a, b int64) int64 {\n\tc := a*3 + b\n\tif c > 1000 {\n\t\tc = c - 1000\n\t}\n\treturn c + %d\n}\n\n' % (i, i))
    f.write('func main() {\n\tvar s int64\n')
    for i in R:
        f.write('\ts = f%d(s, %d)\n' % (i, i))
    f.write('\tfmt.Println(s)\n}\n')
with open(os.path.join(out, 'go_big', 'go.mod'), 'w') as f:
    f.write('module bench/big\n\ngo 1.24\n')

with open(os.path.join(out, 'java_big', 'Big.java'), 'w') as f:
    f.write('public class Big {\n')
    for i in R:
        f.write('    static long f%d(long a, long b) {\n        long c = a * 3 + b;\n        if (c > 1000) {\n            c = c - 1000;\n        }\n        return c + %d;\n    }\n\n' % (i, i))
    # javac refuses a method over 64 KB of bytecode, so main is cut into parts of 500 calls
    parts = [list(R)[k:k + 500] for k in range(0, n, 500)]
    for k, part in enumerate(parts):
        f.write('    static long part%d(long s) {\n' % k)
        for i in part:
            f.write('        s = f%d(s, %d);\n' % (i, i))
        f.write('        return s;\n    }\n\n')
    f.write('    public static void main(String[] args) {\n        long s = 0;\n')
    for k in range(len(parts)):
        f.write('        s = part%d(s);\n' % k)
    f.write('        System.out.println(s);\n    }\n}\n')
