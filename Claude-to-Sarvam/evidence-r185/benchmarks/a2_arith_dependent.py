# Scenario A2: 10,000,000 passes of s = (s + i * 2) ^ (s >> 3), kept to 64 bits as the others are
M = (1 << 64) - 1
s = 0
for i in range(10000000):
    s = (s + i * 2) ^ (s >> 3)
    s &= M
    if s >> 63:
        s -= 1 << 64
print(s)
