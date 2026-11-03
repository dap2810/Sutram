import subprocess, sys
C,D=sys.argv[1],sys.argv[2]
cases=[('0.0000000000000000000001',22),('0.0000000000000000000000000000001234',31),('12345e-310',306),('3e-324',324),('1e-323',323),('0.'+'0'*300+'1',301),('1'+'0'*25+'e-330',305),('0.123456789012345678',0)]
for c,k in cases:
    cells=''.join(f'    b[{i}] = {ord(ch)}\n' for i,ch in enumerate(c))
    if len(c)>150: cells=f'    b[0] = 48\n    b[1] = 46\n    vitti i = 2\n    yavat (i < {len(c)-1}) {{\n        b[i] = 48\n        i = i + 1\n    }}\n    b[{len(c)-1}] = 49\n'
    src=f'yoj vakyank\n\nmukhya() {{\n    vitti b = nirmmita({len(c)*8})\n{cells}    vitti ok = nirmmita(8)\n    dasham v = varna_tak_dashm(b, {len(c)}, ok)\n    vitti j = 0\n    yavat (j < {k}) {{\n        v = v * 10.0\n        j = j + 1\n    }}\n    likha(v)\n    likha(ok[0])\n}}\n'
    open(D+'/vd.sm','w').write(src)
    r=subprocess.run([C,D+"/vd.sm",D+"/vd.bin"],capture_output=True,text=True,cwd=sys.argv[3])
    if r.returncode: print('COMPILE',c,r.stdout[:200]); continue
    o=subprocess.run([D+'/vd.bin'],capture_output=True,text=True).stdout.split()
    print(f'{c[:40]!r:44} x10^{k} -> {o}   python {__import__("decimal").Decimal(c).scaleb(k)}')
