# Scenario B: build a collection of 1,000,000 numbers, then sum it - a list, append, sum()
v = []
for i in range(1000000):
    v.append(i)
print(sum(v))
