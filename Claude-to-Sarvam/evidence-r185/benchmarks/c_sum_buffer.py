# Scenarios C and D: fill a buffer of n numbers, then sum all of it r times (arguments: r n) - a list and sum()
import sys

r = int(sys.argv[1]) if len(sys.argv) > 1 else 1
n = int(sys.argv[2]) if len(sys.argv) > 2 else 10000000
p = [i & 1023 for i in range(n)]
t = 0
for q in range(r):
    p[q] += 1
    t += sum(p)
print(t)
