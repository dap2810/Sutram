import json
old = {(r['a'], r['b'], r['op']): r for r in json.load(open('<workspace>/r101/ws1/trap_matrix.json'))}
new = {(r['a'], r['b'], r['op']): r for r in json.load(open('<workspace>/r102/ws1/trap_matrix_v2.json'))}
A = {"int": 5, "dasham": 2.5, "string": "ab", "kosh": None}
B = {"int": 3, "dasham": 1.5, "string": "cd", "kosh": None}
def classify(r):
    a, b, op, res = r['a'], r['b'], r['op'], r['result']
    if res == "REFUSED":
        return "REFUSED"
    if res == "CRASH":
        return "CRASH"
    if a in ("int", "dasham") and b in ("int", "dasham"):
        x, y = A[a], B[b]
        if a == "int" and b == "int" and op == "/":
            return "CORRECT" if res == "1" else "SILENT-WRONG"
        if op == "%":
            if a == "int" and b == "int":
                return "CORRECT" if res == "2" else "SILENT-WRONG"
            return "SILENT-WRONG"
        exp = {"==": 1 if x == y else 0, "!=": 1 if x != y else 0, "<": 1 if x < y else 0,
               "<=": 1 if x <= y else 0, ">": 1 if x > y else 0, ">=": 1 if x >= y else 0,
               "+": x + y, "-": x - y, "*": x * y, "/": x / y}[op]
        got = float(res)
        if op in ("==", "!=", "<", "<=", ">", ">="):
            return "CORRECT" if got == exp else "SILENT-WRONG"
        return "CORRECT" if abs(got - exp) < 0.01 else "SILENT-WRONG"
    if (a, op, b) in (("string", "+", "int"), ("int", "+", "string"), ("string", "-", "int")):
        return "BY-DESIGN"
    if a == "string" and b == "string" and op in ("==", "!=", "<", "<=", ">", ">="):
        exp = {"==": 0, "!=": 1, "<": 1, "<=": 1, ">": 0, ">=": 0}[op]
        return "CORRECT" if res == str(exp) else "SILENT-WRONG"
    if a == "string" and b == "string" and op == "+":
        return "CONCAT"
    return "SILENT-WRONG"
V1OPS = ["==", "!=", "<", "+", "-", "*", "/"]
V1KINDS = ["int", "dasham", "string", "kosh"]
fixed, remaining, newtraps = [], [], []
for k, ro in old.items():
    if k[0] not in V1KINDS or k[1] not in V1KINDS or k[2] not in V1OPS:
        continue
    rn = new[k]
    co, cn = classify(ro), classify(rn)
    if co == "SILENT-WRONG" and cn in ("CORRECT", "REFUSED", "CONCAT"):
        fixed.append((k, cn, rn['result']))
    elif co == "SILENT-WRONG" and cn in ("SILENT-WRONG", "CRASH"):
        remaining.append((k, cn, rn['result']))
    elif co in ("CORRECT", "REFUSED") and cn in ("SILENT-WRONG", "CRASH"):
        newtraps.append((k, co, cn, rn['result']))
print(f"v1-subset comparison: FIXED={len(fixed)} REMAINING={len(remaining)} NEW={len(newtraps)}")
print("--- fixed:")
for k, cn, res in fixed:
    print(" ", k, "->", cn, res)
print("--- remaining:")
for k, cn, res in remaining:
    print(" ", k, "->", cn, res)
print("--- NEW:")
for k, co, cn, res in newtraps:
    print(" ", k, co, "->", cn, res)
nsw = 0
for k, r in new.items():
    if k[0] not in V1KINDS or k[1] not in V1KINDS or k[2] not in V1OPS:
        if classify(r) == "SILENT-WRONG":
            nsw += 1
print("new-coverage silent-wrong cells:", nsw)
for k in [("string", "string", "<="), ("string", "string", ">"), ("string", "string", ">="),
          ("string", "string", "+"), ("string", "string", "-"), ("string", "string", "*"),
          ("string", "string", "/"), ("string", "string", "%"),
          ("string", "int", "-"), ("string", "int", "*"), ("string", "int", "/"), ("string", "int", "%"),
          ("string", "dasham", "+"), ("string", "dasham", "-"), ("string", "dasham", "*"),
          ("string", "dasham", "/"), ("string", "dasham", "%"),
          ("string", "kosh", "=="), ("kosh", "string", "=="),
          ("mala", "mala", "=="), ("mala", "mala", "<"), ("mala", "mala", "+"),
          ("rachana", "rachana", "=="), ("rachana", "rachana", "<"), ("rachana", "rachana", "+")]:
    print("cell", k, "->", new[k]['result'])
