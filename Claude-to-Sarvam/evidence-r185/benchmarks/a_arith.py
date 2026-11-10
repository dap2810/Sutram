# Scenario A: 10,000,000 passes of s = s + i * 2
s = 0
for i in range(10000000):
    s = s + i * 2
print(s)
